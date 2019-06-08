import sys
import os
import time
import struct
import json
import traceback
import hashlib
from threading import Timer
from binascii import hexlify, unhexlify
import util
import protocol

from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver

from smartcard.sw.ErrorChecker import ErrorChecker
from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
from smartcard.sw.SWExceptions import SWException, WarningProcessingException

from smartcard.util import toHexString, toBytes

from flask import Flask
from flask import request
from entity import Pin
from nbc import coins

app = Flask(__name__)

VERBOSE = '--verbose' in sys.argv
sys.ps1 = '\n>>>'

SELECT = toBytes('00A40400 0E D196300077130010000000020101')
GET_RESPONSE = [0x00, 0xc0, 0, 0]
WEB_SERVER_ADDR = 'http://raw0.nb-chain.net'
curr_coin = coins.Newborntoken

gCard = None
gExpectedAtr = toBytes("3B9F 00 801F038031E073FE211367 00 434F537EC101 00")
gExpectedMask = toBytes("FFFF 00 FFFFFFFFFFFFFFFFFFFFFF 00 FFFFFFFFFFFF 00")

gLastErrCode = '9000'

SUCCESS = 1
FAILED = 0


class WalletApp(object):
    SHEET_CACHE_SIZE = 16

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

    def account_state(uock_from=0, uock_before=0):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = request.get(WEB_SERVER_ADDR+'/txn/state/account', params={
                        'addr': '', 'uock': uock_from, 'uock2': uock_before}, headers=headers, tiemout=30)
        if r.status_code == 200:
            msg = protocol.Message.parse(r.content, magic)
            if msg.command == protocol.UdpReject.command:
                print('Error:'+get_reject_msg_(msg))
            elif msg.command == protocol.AccState.command:
                if msg.account == account:

                    # class PseudoWallet(object):
                    # def __init__(self, pubKey, pubHash):
                    #     pass
                    # self.pub_key = util.key.compress_public_key(unhexlify(pubKey))
                    # self.pub_hash = unhexlify(pubHash)
                    # self._vcn = (ORD(self.pub_hash[30]) << 8) + ORD(self.pub_hash[31])
                    # self.coin_type = b'\x00'
                    # self.pub_addr = util.key.publickey_to_address(
                    #     self.pub_key, self._vcn, self.coin_type, version=b'\x00')
                    # self.pin_code = '000000'

                    # def address(self):
                    #     return self.pub_addr

                    # def publicHash(self):
                    #     return self.pub_hash

                    # def publicKey(self):
                    #     return self.pub_key

                    # def sign(self, payload):
                    #     pass
                    # h = hashlib.sha256(payload).digest()
                    # h = hashlib(h).decode('latin-1')

                    # pinLen = len(self.pin_code)
                    # sCmd = ('802100%02x%02x' %
                    #         (pinLen << 5, pinLen + 32)) + self.pin_code + h

                    # res, status = transmit(sCmd)
                    # if(status == '9000'):
                    #     return ''.join(chr(ch) for ch in res).encode('latin-1')
                    # else:
                    #     raise RuntimeError('TEE sign transaction failed')


# def ORD(ch):  # compatible to python3
#     return ch if type(ch) == int else ord(ch)


# def CHR(i):    # compatible to python3
#     return bytes(bytearray((i,)))


# def checkAtrMatch(atr):
#     if len(atr) != len(gExpectedAtr):
#         return False

#     for (targ, curr, mask) in zip(gExpectedAtr, atr, gExpectedMask):
#         if targ != (curr & mask):
#             return False
#     return True


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


def autoStartCard():
    # print('autoStartCard...')
    pass


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


def verify_pin(psw):
    result = {}
    if psw == None:
        result = {'msg': 'no pass args', 'status': FAILED}
        return result
    if psw == '':
        result = {'msg': 'can not be empty', 'status': FAILED}
        return result

    try:
        res, status = transmit(('00200000%02x' % (len(psw)//2,)) + psw)
        result = {'msg': 'verify PIN code successful.', 'status': SUCCESS}
        return result
    except:
        if gLastErrCode[:3] == '63c':
            result = {'msg': 'incorrect PIN code, left try count: ' +
                      gLastErrCode[-1:], 'status': FAILED}
            return result
        else:
            result = {'msg': 'verify PIN code failed.', 'status': FAILED}
            return result


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


@app.route('/', methods=['get'])
def hello():
    # return json.dumps('are you sb?')
    return 'welcome use api'


@app.route('/getpass', methods=['POST'])
def getpass():
    pincode = request.values.get('pass')
    print('服务收到参数psw:', pincode)
    result = verify_pin(pincode)
    return json.dumps(result)


@app.route('/sign', methods=['POST'])
def sign():
    payload = request.values.get('payload')
    pin_code = request.values.get('pincode')
    sign_params = {'payload': payload, 'pincode': pin_code}
    print('sign_params:', sign_params)
    # 1.验证传过来的密码是否合法
    result = verify_pin(pin_code)
    if(result['status'] == FAILED):
        return json.dumps(result)
    else:
        # 2.获取签名
        t = {}
        h = hashlib.sha256(payload.encode()).digest()
        print('h:', h)
        h = hexlify(h).decode('latin-1')
        print('h:', h)

        pinLen = len(pin_code)//2
        sCmd = ('802100%02x%02x' % (pinLen << 5, pinLen + 32)) + pin_code + h

        res, status = transmit(sCmd)
        print('status:', status)
        if(status == '9000'):
            t = ''.join(chr(ch) for ch in res).encode('latin-1')
            t = hexlify(t).decode()
            t = {'msg': '', 'sign': t, 'status': SUCCESS}
            print('t:', t, len(t))
        else:
            t = {'msg': 'TEE sign transaction failed',
                 'sign': '', 'status': FAILED}

        return json.dumps(t)


@app.route('/info', methods=['GET'])
def info():
    if not checkPseudoWallet():
        print('TEE wallet not ready yet!')
    uockBefore = 0
    uockAfter = 0


if __name__ == "__main__":
    app.after_request(after_request)
    app.run(host='127.0.0.1', port=3000, debug=True)
    monitor.deleteObserver(observer)
