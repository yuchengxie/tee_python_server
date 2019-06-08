const bh = require('../bufferhelp');
const opcodes = require('./opcodes');

var opcode;
var value;
var verify;
var bytes_;
var OP_LITERAL = 0x1ff;
var _expand_verify;

function Tokenizer(pk_script, expand_verify = false) {
    _expand_verify = expand_verify;
    this._script = '';
    this._tokens = [];
    // this._process = _process;
    this.get_script_address = get_script_address;
    this.match_template = match_template;
    // this._process(pk_script);
}

function _process(str_script) {
    var _tokens = [];
    var script = bh.hexStrToBuffer(str_script);
    while (script.length > 0) {
        // console.log('script:', script, script.slice(0, 1)); s
        opcode = ORD(script.slice(0, 1))
        bytes_ = script.slice(0, 1);
        script = script.slice(1);
        value = null;
        verify = false;

        if (opcode == opcodes.OP_0) {
            value = 0;
            opcode = OP_LITERAL;
        } else if (opcode >= 1 && opcode <= 78) {
            var length = opcode;
            if (opcode >= opcodes.OP_PUSHDATA1 && opcode <= opcodes.OP_PUSHDATA4) {
                var iTmp = opcode - opcodes.OP_PUSHDATA1;
                var op_length = [1, 2, 4][iTmp];
                //todo
            }
            var sTmp = script.slice(0, length);
            value = bh.bufToStr(sTmp);
            bytes_ = Buffer.concat([bytes_, sTmp]);
            script = script.slice(length)
            // if (value.length != length) {
            //     throw 'not enought script for literal';
            // }
            opcode = OP_LITERAL;
        } else if (opcode == OP_LITERAL) {
            opcode = OP_LITERAL;
            value = -1;
        } else if (opcode == opcodes.OP_TRUE) {
            opcode = OP_LITERAL;
            value = 1;
        } else if (opcode >= opcodes.OP_1 && opcode <= opcodes.OP_16) {
            opcode = OP_LITERAL;
            // value = 0;
        } else if (_expand_verify && opcode in _Verify) {
            opcode = _Verify[opcode];
            verify = true;
        }
        _tokens.push([opcode, bytes_, value]);
        if (verify) {
            _tokens.push(opcodes.OP_VERIFY, Buffer(0), null);
        }

    }
    this._tokens = _tokens;
    var output = [];
    for (var k1 in _tokens) {
        var t = _tokens[k1];
        if (t[0] == OP_LITERAL) {
            output.push(t[2]);
        } else {
            if (t[1]) {
                var s = opcodes.get_opcode_name(t[0]);
                output.push(s);
            }
        }
    }
    var s = '';
    for (var i = 0; i < output.length; i++) {
        if (i < output.length - 1) {
            s += output[i] + ' ';
        } else {
            s += output[i];
        }
    }
    return s;
    // this._script = s;
}

var _Verify = {
    0x88: opcodes.OP_EQUAL,
    0x9d: opcodes.OP_NUMEQUAL,
    0xad: opcodes.OP_CHECKSIG,
    0xaf: opcodes.OP_CHECKMULTISIG
}

function ORD(ch) {
    return bh.bufToNumer(ch);
}

function get_script_address(pk_script, node, block = null) {
    if (match_template(this._tokens, TEMPLATE_PAY_TO_PUBKEY_HASH)) {
        return this._tokens[2][2];
    } else if (block && this._tokens.match_template(TEMPLATE_PAY_TO_MINERHASH)) {
        var hi = node._bind_vcn / 256;
        var lo = node._bind_vcn % 256;
        return CHR(lo) + CHR(hi) + block.miner + node.coin.mining_coin_type;
    }
    return null
}

function CHR(i) {
    return null;
}

var _lambda = (t) => {
    return t.length == 5;
}

var TEMPLATE_PAY_TO_PUBKEY_HASH = [_lambda, opcodes.OP_DUP,
    opcodes.OP_HASH512, _is_coin_hash, opcodes.OP_HASHVERIFY,
    opcodes.OP_CHECKSIG];
var TEMPLATE_PAY_TO_MINERHASH = [_lambda, opcodes.OP_DUP,
    opcodes.OP_HASH512, opcodes.OP_MINERHASH, opcodes.OP_EQUALVERIFY,
    opcodes.OP_CHECKSIG]

function match_template(tokens, template) { //given a template, True if this script matches
    if (!template[0](tokens)) {
        return false;
    }
    var z = zip(tokens, template.slice(1, template.length));
    for (var i = 0; i < z.length; i++) {
        var m = z[i];
        if (typeof m[1] == 'function') {
            if (!m[1](m[0][0], m[0][1], m[0][2])) {
                return false;
            }
        } else if (m[1] != m[0][0]) {
            return false;
        }
    }
    return true;
}

function zip(tokens, templates) {
    var b = [];
    var len = tokens.length < templates.length ? tokens.length : templates.length;
    for (var i = 0; i < len; i++) {
        b.push([tokens[i], templates[i]]);
    }
    return b;
}

function _is_coin_hash(opcode, bytes_, data) {
    if (opcode != OP_LITERAL) {
        return false;
    }
    if (data.length <= 34) {
        return false;
    }
    return true;
}

module.exports = {
    Tokenizer,_process
}