
### 1. 关于本项目

本项目（tee-wallet）是与 Newborn Bitcoin（简称 NBC）产品配套的，由官方提供的钱包客户端 APP。
NBC 是一个类似于比特币的产品，在 NBC 区块链上发行的币种称为 NBC 币，请访问 http://nb-coin.com
了解更多关于 NBC 的信息。

tee-wallet 是开源产品，任何人可从 github.com/nb-coin/tee-wallet 下载源码。

&nbsp;

### 2. 安装

tee-wallet 用 python 开发，支持 Python3.4+ 版本，Windows 或 MAC 各版本的桌面操作系统平台均支持。

如果您当前所用的 Python 是 2.7 以下的版本，请先升级到 3.4 以上的版本。另外，tee-wallet
使用如下依赖库，也请自行安装：

``` bash
pip install six
pip install click
pip install requests
pip install pyscard
```

本产品用到的读卡器驱动库是 pyscard，参见这个网址：

> `https://github.com/LudovicRousseau/pyscard`

当 Python 运行环境准备就绪后，请用如下脚本获取 tee-wallet 项目：

``` bash
git clone http://github.com/nb-coin/tee-wallet.git
```

然后运行本软件：

``` bash
cd tee-wallet
python wallet.py
```

当界面出现 "cmd>" 等待命令输入的提示符时，用户可键入操作指令，以便完成特定任务，
键入 "help" 可获得命令格式的使用帮助。

如果本客户端用于 NBC 挖矿，用户还可用 "--pool" 参数指示矿池所在的域名与端口号，比如：

``` bash
python wallet.py --pool user1-node.nb-chain.net:30302
```

&nbsp;

### 3. 命令行帮助

本软件提供如下子命令：

``` bash
  help      : print help
  break     : break command loop

  info [before=uock] [after=uock]
            : account information
  block [hash=block_id] [height]+
            : query block, "1-" for last one 
  utxo [num=5] [uock=id]
            : max list "num" of utxo or only list "uock" item
  transfer [after=uock] [hash=tx_id] [addr=nbc]+
            : transfer NBC to other account
  record [proof=1] [where=location] [after=uock] [hash=tx_id] ["desc"]+
            : record message or finger print of proof

  start     : start mining
  stop      : stop mining

  account   : show current NBC account
  create    : generate NBC account in TEE, only one time
  import    : import NBC account to TEE, only one time

  getpass   : verify PIN
  setpass   : change PIN
  bind      : bind phone number to TEE
  config [level=1|2|3] [automining=0|1]
            : change security level or auto mining
  export    : export NBC account to private_sn.bak file
  restore   : restore NBC account from private_sn.bak
```

各条指令含义如下：

1. help: 打印命令行的帮助信息
2. break: 退出命令行循环
3. info: 显示当前账号信息，包括地址、UTXO 余额等
4. block: 打印指定区块的详细信息
5. utxo: 显示当前账号的 utxo，或只显示指定 uock 那项 utxo 信息
6. transfer: 从当前账号转账若干 NBC 币给指定账号
7. record: 创建存证记录
8. start: 开始挖矿
9. stop: 停止挖矿
10. account: 显示当前 TEE 所绑定账号的信息
11. create: 指示 TEE 中的程序自动创建账号
12. import: 通过导入私钥让 TEE 创建账号
13. getpass: 验证 PIN 码
14. setpass: 修改 PIN 码
15. bind: 绑定手机号到 TEE 设备
16. config: 配置 TEE 设备的安全级别，或是否自动启动挖矿
17. export: 将 TEE 中账号的私钥以密文方式导出
18. restore: 根据密文私钥文件恢复 TEE 中的账号

&nbsp;

### 4. 使用指南：设置 PIN 码

在电脑的 USB 口先插入本 TEE 设备，然后运行本软件 `python wallet.py` 将进入命令行界面。

运行如下脚本可验证本设备的 PIN（Personal Identification Number）码，当前缺省值为 "000000"。

``` bash
getpass
```

修改 PIN 码要求输对原 PIN 码并给出新 PIN 码，合法的 PIN 码要求用 0~9 之间的数字，可取 3~10 个数字。

``` bash
setpass
```

为安全考虑，拿到设备后您应先改 PIN 码，您需妥善保管 PIN 码，拥有 PIN 码意味着拥有对该 TEE
设备的操作权。

&nbsp;

### 5. 使用指南：创建账号

本 TEE 设备出厂时不带 NBC 账号，您需往 TEE 导入一个账号，或让 TEE 中的程序帮你自动生成一个。
如果本 TEE 用于挖矿，须由 TEE 中程序生成账号，从外部导入的账号不能用于挖矿，只用作常规的数字货币钱包。

运行如下脚本查看 TEE 中的账号，当然，首次使用系统会报告账号为空：

``` bash
account
```

在导入账号前，您需准备一个 32 字节长的账号私钥，描述成类似如下 16 进制格式:

``` bash
0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20
```

这里只是举例，私钥取值越随机越好，而且，用户需自行保障其安全，不泄露给他人。拷贝上述私钥字串，
然后运行下面脚本向 TEE 导入私钥：

``` bash
import
```

在界面提示输入私钥时，粘贴上述已拷贝的字串，本 TEE 设备随后将它导入并创建账号。

如果想让本设备自行生成一个账号，可用如下脚本：

``` bash
create
```

请注意，在一个 TEE 设备导入 NBC 账号或自动生成账号，只能做一次，TEE 中一旦驻留了账号，
此账号便永远不可更换或删除。所以，准备往 TEE 安装账号前，您需认真想清楚该如何配置与管理 NBC 账号。

&nbsp;

### 6. 使用指南：查看账户信息

执行如下脚本可查看当前账号信息，包括 Base58 地址与在线查得的 NBC 余额。

``` bash
info
```

NBC 采用类似比特币的 UTXO 账户模型，一个账号的总余额为它所拥有的所有未花费用（即 UTXO）项的总和。
UTXO 记录项由 UOCK（UTXO Compose Key）索引，特定 UOCK 唯一对应一项 UTXO，UOCK 是一个整数值，
其值大小与创建它所指示的 UTXO 的时间正相关。

查询账户余额时，还可由 `after=uock` 及（或） `before=uock` 参数来限定查询范围。比如：

``` bash
info after=442003675414528
```

如果 `after=uock1` 与 `before=uock2` 两个参数并用，表示限制范围为 `uock1 < uock <= uock2` 。

&nbsp;

### 7. 使用指南：查询 UTXO

显示当前账号拥有的 UTXO 详情信息，缺省显示最近 5 条 UTXO 记录。

``` bash
utxo
```

我们还可以用 `num=n` 参数指定只显示最近 n 条记录，n 在 1 ~ 100 之间取值，也可用 `uock=id`
指定只显示一条对应的记录。

&nbsp;

### 8. 使用指南：浏览指定高度的区块信息

``` bash
block 0 1-
```

一次可查阅一个或多个区块，比如上面脚本，查阅高度为 0 的区块（即创始区块）以及最后一个区块的信息，块高若带 `-` 后缀表示从当前区块链的最后一个区块向前倒数，`1-` 表示倒数第一个区块，`2-` 倒数第二个区块，其它类推。

我们还可以用 `hash=id` 查询指定区块头哈希值的区块，比如：

``` bash
block hash=9488469356089fea9638efa2bb61ab0740b2037178292bdd665933b0d3020000
```

&nbsp;

### 9. 使用指南：转账

从当前账号向指定账号转账，比如：

``` bash
transfer 1112pzQBWmUCsLtFZ1oNV769viSdDnAPX45N7Xp3zKvDPJwAL8BJFS=5.5
```

上面脚本含义为：从当前账号向 `1112pzQBWmUCsLtFZ1oNV769viSdDnAPX45N7Xp3zKvDPJwAL8BJFS` 转账
5.5 NBC 币，如果要向多个账号转账，罗列多个由 `=` 串接的目标账号及转账额的项目即可。
转账请求发起后，本程序将持续发起进度查询，每隔数十秒查询一次转账进度，进度信息将打印到界面。
若想停止查询，可按 `Ctrl + C` 链中断。

每次转账系统将计算该交易单的哈希值，此哈希值将唯一代表本交易，即用作交易 ID，在交易刚发起时，
界面会打印输出本次交易的哈希值。此后，我们可用类似如下脚本再次查询该交易的进度：

``` bash
transfer hash=e11e110060d16c77579d00cb105298c52b228f01664dcd9361ffae82b31cdffa
```

成功提交一项交易后，界面将打印动用当前账号中的最后一个 utxo 的位置标识（即 uock 值），
在紧接着的同一账号向外转帐时，可用 `after=uock` 指示从指定位置之后取 UXTO 来转账，
这有助于避免同一 UTXO 在两次转账中均被使用。

&nbsp;

### 10. 使用指南：存证

tee-wallet 支持短消息存证与哈希值存证。前者用于在区块链账本数据中保存简短信息，
后者只保存一段哈希字串，哈希字串则来源于对一篇文章或一长字串进行散列运算。

短消息存证可支持存入 72 个字符的内容，使用举例如下：

``` bash
record "Hello world!" "This is second line"
```

多行存证内容可用多个字串以传入参数形式来表达，如上有两行消息被存证。

哈希值存证用 `proof=1` 参数指示，再传入某个哈希值即可，举例如下：

``` bash
record proof=1 "ba125434cf56d1b265b4f05e788b838a0bbbd89d0dfd3b3ec1452488552d80b1"
```

本软件也将存证（包括短消息存证与哈希值存证）视作一项交易，与 `transfer` 子命令类似，
也支持用 `hash=id` 指定交易 ID 来查询交易进度，比如：

``` bash
record hash=a99718b42488efad73424511ac7e6cb4e9a7c9b200dca7182fb9eb67f023f267
```

&nbsp;

### 11. 软件集成与交互式调试

tee-wallet 作为 NBC 区块链的客户端钱包 APP，其主体功能，包括交易与信息查询，
要通过调用在 `https://api.nb-coin.com` 提供的 RESTful API 服务来实现。因为本软件已开源，
全部代码可从 github 下载过来研读，所以，本项目也是 NBC 区块链 RESTful API 一种实现样例，
大家可以仿照着将源码移植到 java、javascript 等运行环境下使用。

如果想用交互式命令行调试本软件，不妨以 `-i` 参数启动 python，比如：

``` bash
python -i wallet.py
```

另外，命令行参数还可带 `--verbose` 参数，用来打印从读卡器下发与回传的命令与响应。比如：

``` bash
python -i wallet.py --verbose --pool user1-node.nb-chain.net:30302
```

&nbsp;

### 12. 关于版权

tee-wallet 重用了 [ricmoo/pycoind](https://github.com/ricmoo/pycoind) 项目中的 util 模块代码，
对该模块我们维持原有的 MIT 授权证书。

本项目其它源码我们采用 MPL V2 开源协议，详见：[MPL 2.0](http://mozilla.org/MPL/2.0/)

任何问题请在 [github nb-coin/tee-wallet 项目](https://github.com/nb-coin/tee-wallet) 的
Issues 页中提交，谢谢关注本项目！

&nbsp;
