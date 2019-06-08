import random
import re
from flask import Flask, request
import json
from nbc import script
from nbc import protocol
from nbc import wallet
import requests
import hashlib
import getpass
from mine_client import PoetClient
from nbc import coins
from nbc import util
import sys
import os
import time
import struct
import traceback
from threading import Timer
from binascii import hexlify, unhexlify

from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver

from smartcard.sw.ErrorChecker import ErrorChecker
from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
from smartcard.sw.SWExceptions import SWException, WarningProcessingException

from smartcard.util import toHexString, toBytes

VERBOSE = '--verbose' in sys.argv
sys.ps1 = '\n>>>'

SELECT = toBytes('00A40400 0E D196300077130010000000020101')
GET_RESPONSE = [0x00, 0xc0, 0, 0]

gCard = None
gExpectedAtr = toBytes("3B9F 00 801F038031E073FE211367 00 434F537EC101 00")
gExpectedMask = toBytes("FFFF 00 FFFFFFFFFFFFFFFFFFFFFF 00 FFFFFFFFFFFF 00")

gLastErrCode = '9000'


def ORD(ch):   # compatible to python3
    return ch if type(ch) == int else ord(ch)


def CHR(i):    # compatible to python3
    return bytes(bytearray((i,)))


def checkAtrMatch(atr):
    if len(atr) != len(gExpectedAtr):
        return False

    for (targ, curr, mask) in zip(gExpectedAtr, atr, gExpectedMask):
        if targ != (curr & mask):
            return False
    return True


class MyErrorChecker(ErrorChecker):
    def __call__(self, data, sw1, sw2):
        global gLastErrCode
        gLastErrCode = '%02x%02x' % (sw1, sw2)


gErrorchain = []
gErrorchain = [ErrorCheckingChain(gErrorchain, MyErrorChecker()),
               ErrorCheckingChain(gErrorchain, ISO7816_8ErrorChecker()),
               ErrorCheckingChain(gErrorchain, ISO7816_4ErrorChecker())]


class DFTELECOMObserver(CardObserver):
    def __init__(self):
        self.observer = ConsoleCardConnectionObserver()

    def update(self, observable, actions):
        global gCard

        (addedcards, removedcards) = actions
        for card in addedcards:
            if checkAtrMatch(card.atr):
                card.connection = card.createConnection()
                card.connection.connect()
                if VERBOSE:
                    card.connection.addObserver(self.observer)

                response, sw1, sw2 = card.connection.transmit(SELECT)
                if sw1 == 0x61:
                    second, sw1, sw2 = card.connection.transmit(
                        GET_RESPONSE + [sw2])
                    response += second

                if sw1 == 0x90 and sw2 == 0x00:
                    card.connection.setErrorCheckingChain(gErrorchain)
                    gCard = card

                    print('card added :', toHexString(card.atr).lower())
                    print('card reader:', card.connection.getReader())

                    # autoStartCard() will be called after 4 seconds
                    Timer(4, lambda: autoStartCard()).start()
                    break  # just select first expected card

        for card in removedcards:
            if checkAtrMatch(card.atr):
                if gCard:
                    print('card removed:', toHexString(card.atr).lower())
                gCard = None


def transmit(s, conn=None):
    global gLastErrCode

    if not conn:
        conn = gCard.connection
    if type(s) == str:
        s = toBytes(s)

    res, sw1, sw2 = conn.transmit(s)
    iLoop = 0
    while sw1 == 0x61 and iLoop < 32:   # max hold 8,192 bytes (32*256)
        # if sw2 == 0 means auto length
        second, sw1, sw2 = conn.transmit(GET_RESPONSE + [sw2])
        res += second
        iLoop += 1

    return (res, '%02x%02x' % (sw1, sw2))


def getPubAddr(conn=None):
    try:
        res, status = transmit('80220200 02 0000', conn)
        if status == '9000':
            return ''.join(chr(c) for c in res)
    except:
        if gLastErrCode == '6984':  # no account exists yet
            return None
        else:
            raise    # re-raise
    return None


def getPubKey(conn=None):
    try:
        res, status = transmit('80220000 00', conn)
        if status == '9000':
            return ''.join(('%02x' % c) for c in res)
    except:
        if gLastErrCode == '6984':  # no account exists yet
            return None
        else:
            raise    # re-raise
    return None


def getPubKeyHash(conn=None):
    try:
        res, status = transmit('80220100 00', conn)
        if status == '9000':
            return ''.join(('%02x' % c) for c in res)
    except:
        if gLastErrCode == '6984':  # no account exists yet
            return None
        else:
            raise    # re-raise
    return None


def getSerialNo(conn=None):
    res, status = transmit('80010500 00', conn)
    if status == '9000':
        return ''.join(('%02x' % c) for c in res)
    else:
        return '00' * 8


monitor = CardMonitor()
observer = DFTELECOMObserver()
monitor.addObserver(observer)  # monitor.obs should be [observer]


curr_coin = coins.Newborntoken
curr_coin.WEB_SERVER_ADDR = 'http://user1-node.nb-chain.net'

MINING_NODE_ADDR = ('user1-node.nb-chain.net', 30302)

if '--pool' in sys.argv and sys.argv[-1] != '--pool':
    _pool_addr = sys.argv[sys.argv.index('--pool')+1].split(':')
    if len(_pool_addr) >= 2:
        _pool_addr[1] = int(_pool_addr[1])
    else:
        _pool_addr.append(30302)
    MINING_NODE_ADDR = tuple(_pool_addr[:2])


gStartTime = time.time()
gBehavior = 0

gPoetClient = None
gPseudoWallet = None


def inputPin():
    psw = ''
    while True:
        psw = getpass.getpass('input PIN: ').strip()
        if not psw:
            print('no password, operation will be cancel.')
            break
        if re.match(r'^\d+$', psw) and len(psw) >= 3 and len(psw) <= 10:
            break
        print("invalid PIN code, it should be 3-10 character of '0'-'9'")

    if psw and (len(psw) & 0x01) == 1:
        psw += 'f'
    return psw


class TeeMiner(object):
    SUCC_BLOCKS_MAX = 256

    def __init__(self, pubHash):
        self.pub_keyhash = pubHash
        self.succ_blocks = []

    def check_elapsed(self, block_hash, bits, txn_num, curr_tm=None, sig_flag=b'\x00', hi=0):
        if not gCard:
            return None  # failed

        if not curr_tm:
            curr_tm = int(time.time())

        try:
            sCmd = b'\x80\x23' + sig_flag + b'\x00'
            sBlockInfo = block_hash + struct.pack('<II', bits, txn_num)
            sData = struct.pack('<IB', curr_tm, len(sBlockInfo)) + sBlockInfo
            sCmd = sCmd + struct.pack('<B', len(sData)) + sData

            res, status = transmit(hexlify(sCmd).decode('latin-1'))
            if status == '9000':
                if len(res) > 64:  # ecc signature must large than 64 bytes
                    self.succ_blocks.append([curr_tm, hi])
                    if len(self.succ_blocks) > self.SUCC_BLOCKS_MAX:
                        del self.succ_blocks[: -self.SUCC_BLOCKS_MAX]

                    return bytes(bytearray(res)) + sig_flag
        except:
            traceback.print_exc()

        return None  # failed


class PseudoWallet(object):
    def __init__(self, pubKey, pubHash):
        self.pub_key = util.key.compress_public_key(unhexlify(pubKey))
        self.pub_hash = unhexlify(pubHash)
        self._vcn = (ORD(self.pub_hash[30]) << 8) + ORD(self.pub_hash[31])
        self.coin_type = b'\x00'   # fixed to '00'

        self.pub_addr = util.key.publickey_to_address(
            self.pub_key, self._vcn, self.coin_type, version=b'\x00')
        self.pin_code = '000000'   # always reset to '000000'

    def address(self):
        return self.pub_addr

    def publicHash(self):
        return self.pub_hash

    def publicKey(self):
        return self.pub_key

    def sign(self, payload):
        h = hashlib.sha256(payload).digest()  # h must be 32 bytes
        h = hexlify(h).decode('latin-1')      # convert to utf-8

        pinLen = len(self.pin_code) // 2
        sCmd = ('802100%02x%02x' %
                (pinLen << 5, pinLen + 32)) + self.pin_code + h

        res, status = transmit(sCmd)  # maybe raise error here
        if status == '9000':
            return ''.join(chr(ch) for ch in res).encode('latin-1')
        else:
            raise RuntimeError('TEE sign transaction failed')


def _startMining():
    global gPseudoWallet, gPoetClient

    try:
        pubKey = getPubKey()
        pubHash = getPubKeyHash()
    except:
        print('warning: start mining failed (invalid account)')
        return

    gPseudoWallet = PseudoWallet(pubKey, pubHash)

    gPoetClient = PoetClient([TeeMiner(unhexlify(pubHash))],
                             link_no=0, coin=coins.Newborntoken, name='client1')
    gPoetClient.start()
    gPoetClient.set_peer(MINING_NODE_ADDR)
    print('mining task starting ...')


def autoStartCard():
    global gBehavior

    if sys.flags.interactive:
        return   # interactive mode for debugging, ignore mining

    if time.time() - gStartTime < 10:  # only auto start when inserting card within 10 seconds
        res, status = transmit('80010400 00')  # get user behavior
        if status == '9000':
            gBehavior = (res[0] << 8) | res[1]
            if (gBehavior & 0x04) == 0x04:  # auto mining
                _startMining()


# =====================


def hash_str(s):  # s is bytes, return str type
    return hexlify(s).decode('latin-1')


def fine_print(value):
    s = '%.8f' % (value/100000000,)
    if s.find('.') >= 0:
        s = s.rstrip('0')
        if s[-1] == '.':
            s = s[:-1]
    return s


def special_int(s):
    if not s:
        return 0
    if s[-1] == '-':
        return int('-' + s[:-1])
    else:
        return int(s)


def safe_hex(s):
    s = s[:16]             # max take 16 char
    if len(s) & 0x01:      # odd length
        s += '0' + s

    try:
        unhexlify(s)         # check hex format
        return s
    except:
        raise Exception('invalid HEX format')


ttt = None


_BASE58_CHAR = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
_TX_TRANSFER_MAX = 1000000000000     # 10000 NBC

_BREAK_LOOP = '\npress Ctrl+C to break query loop, transaction starting ...\n'


def checkPseudoWallet():
    global gPseudoWallet
    if gPseudoWallet:
        return gPseudoWallet

    pubKey = getPubKey()
    pubHash = getPubKeyHash()
    if pubKey and pubHash:
        gPseudoWallet = PseudoWallet(pubKey, pubHash)
        return gPseudoWallet
    else:
        return None


def randomData(size):
    b = [random.randint(0, 255) for i in range(size)]
    return ''.join('%02x' % ch for ch in b)


class WalletApp(object):
    SHEET_CACHE_SIZE = 16

    WEB_SERVER_ADDR = ''

    def __init__(self, wallet, vcn=0, coin=curr_coin):
        self._wallet = wallet
        self._vcn = vcn
        self._coin = coin

        self._sequence = 0
        self._wait_submit = []

    def failed_desc(self, r):
        return 'Error: request failed, code=' + str(r.status_code)

    def get_reject_msg_(self, msg):
        sErr = msg.message
        if type(sErr) != str:
            sErr = sErr.decode('latin-1')
        return sErr or 'Meet unknown error'

    def account_state(self, uock_from=0, uock_before=0, another=None):  # try query all UTXO
        account = another if another else self._wallet.address()
        if type(account) == bytes:
            account2 = account.decode('latin-1')
        else:  # account should be str type
            account2 = account
            account = account.encode('latin-1')

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.get(self.WEB_SERVER_ADDR + '/txn/state/account', params={
            'addr': account2, 'uock': uock_from, 'uock2': uock_before}, headers=headers, timeout=30)
        if r.status_code == 200:
            msg = protocol.Message.parse(r.content, self._coin.magic)
            if msg.command == protocol.UdpReject.command:
                print('Error: ' + self.get_reject_msg_(msg))

            elif msg.command == protocol.AccState.command:
                if msg.account == account:  # msg.link_no is peer's node._link_no
                    total = sum(u.value for u in msg.found)
                    sDesc = 'Total unspent: %s' % (fine_print(total),)
                    if len(msg.found) == msg.search:    # meet limit, should have more UTXO
                        sDesc += ' (not search all yet)'

                    print('Public address: %s' % (account2,))
                    print(sDesc)
                    print('List of (uock,height,value):' +
                          ('' if msg.found else ' none'))
                    for u in msg.found:
                        print('  %016x, %10s, %14s' %
                              (u.uock, u.height, fine_print(u.value)))
                    print('')
        else:
            print(self.failed_desc(r))

    def block_state(self, block_hash, heights=None):  # block_hash should be str or None
        if block_hash:
            if type(block_hash) != bytes:
                block_hash = block_hash.encode('latin-1')
            hash2 = hexlify(block_hash).decode('latin-1')
        else:
            hash2 = '00' * 32

        if heights:
            heights = [special_int(hi) for hi in heights]
        else:
            heights = []

        if not block_hash and not heights:
            print('warning: nothing to query.')
            return

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        account = self._wallet.address()
        if type(account) == bytes:
            account2 = account.decode('latin-1')
        else:
            account2 = account  # account2 should be str type

        r = requests.get(self.WEB_SERVER_ADDR + '/txn/state/block',
                         params={'hash': hash2, 'hi': heights}, headers=headers, timeout=30)
        if r.status_code == 200:
            msg = protocol.Message.parse(r.content, self._coin.magic)
            if msg.command == protocol.UdpReject.command:
                print('Error: ' + self.get_reject_msg_(msg))

            elif msg.command == protocol.ReplyHeaders.command:
                if not msg.headers:
                    print('no block is found!')
                else:
                    for (idx, block) in enumerate(msg.headers):
                        hi = msg.heights[idx]
                        txck = msg.txcks[idx]

                        print('Block(height=%i,txck=%i):' % (hi, txck))
                        print('  hash: %s' % (hash_str(block.hash),))
                        print('  version: %i' % (block.version,))
                        print('  link_no: 0x%x' % (block.link_no,))
                        print('  prev_block:  %s' %
                              (hash_str(block.prev_block),))
                        print('  merkle_root: %s' %
                              (hash_str(block.merkle_root),))
                        print('  timestamp: %i' % (block.timestamp,))
                        print('  bits:  %i' % (block.bits,))
                        print('  nonce: %i' % (block.nonce,))
                        print('  miner: %s' % (hash_str(block.miner),))
                        print('  txn_count: %i' % (block.txn_count,))
                        print('')
        else:
            print(self.failed_desc(r))

# =========================== web service ===============================


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return 'hello TEE'


@app.route('/info', methods=['GET'])
def info():
    if not checkPseudoWallet():
        print('TEE wallet not ready yet!')
    uockBefore = 0
    uockAfter = 0
    sAddr = gPseudoWallet.address()
    if type(sAddr) == bytes:
        sAddr = sAddr.decode('latin-1')

    app = WalletApp(gPseudoWallet, gPseudoWallet._vcn)
    app.WEB_SERVER_ADDR = curr_coin.WEB_SERVER_ADDR
    app.account_state(uockAfter, uockBefore)
    return 'info'


if __name__ == "__main__":
    app.after_request(after_request)
    app.run(host='127.0.0.1', port=3000, debug=True)
    monitor.deleteObserver(observer)
