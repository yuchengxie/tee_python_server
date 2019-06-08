
import socket, time, random, re, traceback
from threading import Thread
from binascii import hexlify

from nbc import util
from nbc import coins
from nbc import wallet
from nbc import protocol

_RE_IPV4 = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

class PoetClient(Thread):
  POET_POOL_HEARTBEAT = 5    # heartbeat every 5 seconds, can be 5 sec ~ 50 min (3000 sec)
  PEER_ADDR_ = None          # ('192.168.1.103',30303)
  
  def __init__(self, miners, link_no, coin, name=''):
    Thread.__init__(self)
    self.daemon = True
    self._active = False
    
    self.miners = miners
    self._name = name + '>'
    
    self._link_no = link_no
    self._coin = coin
    
    self._last_peer_addr = None
    
    self._recv_buffer = b''
    self._last_rx_time = 0
    self._last_pong_time = 0
    
    self._reject_count = 0
    self._last_taskid = 0
    self._time_taskid = 0
    self._compete_src = None
    
    self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    self.socket.bind(('',0))  # avoid 10022 error in windows system when call recvfrom() 
    self.socket.settimeout(self.POET_POOL_HEARTBEAT)
  
  def set_peer(self, peer_addr): # peer_addr: ('192.168.1.103',30303) or ('user1-node0.pinp.io',30302)
    ip, port = peer_addr
    sre = _RE_IPV4.match(ip)
    if sre:
      self.PEER_ADDR_ = (sre.string,int(port))
    else:  # ip should be domain name
      seedInfo = socket.getaddrinfo(ip,int(port),socket.AF_UNSPEC,socket.SOCK_STREAM)
      if seedInfo: # af, socktype, proto, canonname, addr = seedInfo[0]
        self.PEER_ADDR_ = seedInfo[0][4]
        self._last_peer_addr = (ip,port)
      else: raise Exception('invalid IP (' + ip + ')')
  
  def exit(self):
    self._active = False
    self.join()
  
  def run(self):
    self._active = True
    
    chunk = None
    while self.is_alive() and self._active:
      try:
        self.heartbeat()
      except:
        traceback.print_exc()
      
      try:
        chunk, addr = self.socket.recvfrom(1472)  # 1472 = 1500 - 8 - 20
        self._recv_buffer = chunk
        self._last_rx_time = int(time.time())
      except socket.timeout:
        chunk = None      # has delay
      except:
        chunk = None
        time.sleep(self.POET_POOL_HEARTBEAT)  # avoid unexpected error
      if not chunk: continue
      
      length = protocol.Message.first_msg_len(self._recv_buffer) # length maybe None
      while length and length <= len(self._recv_buffer):
        data = self._recv_buffer[:length]
        try:
          msg = protocol.Message.parse(data,self._coin.magic)    # will check magic-code and sum-code
          self._recv_buffer = self._recv_buffer[length:]
          length = protocol.Message.first_msg_len(self._recv_buffer)
          self._msg_ = msg    # for debuging
          try:
            self.handle_message(data,msg,addr)
          except:
            traceback.print_exc()
        except protocol.UnknownMsgError as e:
          self._recv_buffer = b''   # avoid chaos
          self.invalid_command(data,e)
        except protocol.MsgFormatError as e:
          self._recv_buffer = b''
          self.invalid_command(data,e)
        except Exception as e:     # just print error, avoid stopping
          self._recv_buffer = b''
          print('%s receive meet error: %s' % (self._name,e))
    
    try:
      self.socket.close()
    except: pass
    self._active = False
    print('%s PoET client exited.' % (self._name,))
  
  def handle_message(self, data, msg, peer_addr):
    sCmd = msg.command
    
    # print(self._name,'receive:',msg._debug())
    if sCmd == protocol.PoetInfo.command:
      if msg.curr_id > self._last_taskid:
        self._compete_src = (msg.curr_id,msg.block_hash,msg.bits,msg.txn_num,msg.link_no,msg.height)
        self._last_taskid = msg.curr_id
        self._time_taskid = self._last_rx_time
        self._reject_count = 0
        
        tm = time.localtime()
        print('%s receive a task (%02i:%02i): link=%i, height=%i, sn=%i' % (self._name,tm.tm_hour,tm.tm_min,msg.link_no,msg.height,msg.curr_id))
    elif sCmd == protocol.PoetReject.command:
      if msg.timestamp == self._time_taskid:      # avoid pseudo-message-attack
        if msg.reason == 'missed' and self._last_taskid == msg.sequence:
          pass   # still in same mining task
        else:
          self._compete_src = None                # temporary stop mining
          self._reject_count += 1
      self._last_pong_time = self._last_rx_time   # for checking alive
    elif sCmd == protocol.Pong.command:
      self._last_pong_time = self._last_rx_time   # for checking alive
  
  def invalid_command(self, data, e):
    print('%s API client meet error: %s' % (self._name,e))
  
  def send_message(self, msg, peer_addr):
    self.socket.sendto(msg.binary(self._coin.magic),peer_addr)
  
  def heartbeat(self):
    if not self.PEER_ADDR_: return
    
    now = int(time.time())
    if now - self._time_taskid > 1800:  # reset taskid when hang off more than half of an hour
      self._last_taskid = 0
    if self._reject_count > 120:  # too many reject, maybe peer restart (peer address maybe not change), task id maybe reset
      self._reject_count = 0
      self._last_taskid = 0
    
    # try reset socket and peer address when no receiving message since 30 minutes ago
    if now - self._last_rx_time > 1800 and self._last_peer_addr:
      try:  # maybe socket go bad, or peer address changed (peer restarted)
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind(('',0))
        sock.settimeout(self.POET_POOL_HEARTBEAT)
        
        self.socket.close()
        self.socket = sock
        self.set_peer(self._last_peer_addr)
      except:
        traceback.print_exc()
    
    compete_src = self._compete_src
    if compete_src:
      sn, block_hash, bits, txn_num, link_no, hi = compete_src
      succ_miner = None; succ_sig = None
      
      miners = self.miners[:]
      random.shuffle(miners)
      
      for miner in miners:
        sig = miner.check_elapsed(block_hash,bits,txn_num,now,b'\x00',hi)
        if sig:
          succ_miner = miner
          succ_sig = sig
          break
      
      if succ_miner:
        self._compete_src = None   # wait next mining loop
        
        msg = protocol.PoetResult(link_no,sn,succ_miner.pub_keyhash,succ_sig)
        self.send_message(msg,self.PEER_ADDR_)
        
        tm = time.localtime(now)
        print('%s success mining (%02i:%02i): link=%i, height=%i, sn=%i, miner=%s' % (self._name,tm.tm_hour,tm.tm_min,link_no,hi,sn,hexlify(succ_miner.pub_keyhash)))
        time.sleep(self.POET_POOL_HEARTBEAT)  # just success mining, no hurry try next
    
    if now >= self._last_rx_time + self.POET_POOL_HEARTBEAT:
      msg = protocol.GetPoetTask(self._link_no,self._last_taskid,self._time_taskid)
      self.send_message(msg,self.PEER_ADDR_)
