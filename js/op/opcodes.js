
var __all__ = ['DISABLED', 'OPCODE_NAMES', 'OP_0', 'OP_0NOTEQUAL', 'OP_1', 'OP_10',
    'OP_11', 'OP_12', 'OP_13', 'OP_14', 'OP_15', 'OP_16', 'OP_1ADD',
    'OP_1NEGATE', 'OP_1SUB', 'OP_2', 'OP_2DIV', 'OP_2DROP', 'OP_2DUP',
    'OP_2MUL', 'OP_2OVER', 'OP_2ROT', 'OP_2SWAP', 'OP_3', 'OP_3DUP',
    'OP_4', 'OP_5', 'OP_6', 'OP_7', 'OP_8', 'OP_9', 'OP_ABS', 'OP_ADD',
    'OP_AND', 'OP_BOOLAND', 'OP_BOOLOR', 'OP_CAT', 'OP_CHECKMULTISIG',
    'OP_CHECKMULTISIGVERIFY', 'OP_CHECKSIG', 'OP_CHECKSIGVERIFY',
    'OP_CODESEPARATOR', 'OP_DEPTH', 'OP_DIV', 'OP_DROP', 'OP_DUP',
    'OP_ELSE', 'OP_ENDIF', 'OP_EQUAL', 'OP_EQUALVERIFY', 'OP_FALSE',
    'OP_FROMALTSTACK', 'OP_GREATERTHAN', 'OP_GREATERTHANOREQUAL',
    'OP_HASH160', 'OP_HASH256', 'OP_IF', 'OP_IFDUP', 'OP_INVALIDOPCODE',
    'OP_INVERT', 'OP_LEFT', 'OP_LESSTHAN', 'OP_LESSTHANOREQUAL',
    'OP_LSHIFT', 'OP_MAX', 'OP_MIN', 'OP_MOD', 'OP_MUL', 'OP_NEGATE',
    'OP_NIP', 'OP_NOP', 'OP_NOP1', 'OP_NOP10', 'OP_NOP2', 'OP_NOP3',
    'OP_NOP4', 'OP_NOP5', 'OP_NOP6', 'OP_NOP7', 'OP_NOP8', 'OP_NOP9',
    'OP_NOT', 'OP_NOTIF', 'OP_NUMEQUAL', 'OP_NUMEQUALVERIFY',
    'OP_NUMNOTEQUAL', 'OP_OR', 'OP_OVER', 'OP_PICK', 'OP_PUBKEY',
    'OP_PUBKEYHASH', 'OP_PUSHDATA1', 'OP_PUSHDATA2', 'OP_PUSHDATA4',
    'OP_RESERVED', 'OP_RESERVED1', 'OP_RESERVED2', 'OP_RETURN',
    'OP_RIGHT', 'OP_RIPEMD160', 'OP_ROLL', 'OP_ROT', 'OP_RSHIFT',
    'OP_SHA1', 'OP_SHA256', 'OP_SIZE', 'OP_SUB', 'OP_SUBSTR', 'OP_SWAP',
    'OP_TOALTSTACK', 'OP_TRUE', 'OP_TUCK', 'OP_VER', 'OP_VERIF',
    'OP_VERIFY', 'OP_VERNOTIF', 'OP_WITHIN', 'OP_XOR', 'RESERVED',
    'get_opcode_name', 'is_disabled', 'is_reserved',
    'OP_HASHVERIFY', 'OP_HASH512', 'OP_MINERHASH']

//////////////////////////////////////
// Constants
// An empty array of bytes is pushed onto the stack. (This is not a no-op: an
// item is added to the stack.)
var OP_0 = 0x00;
var OP_FALSE = 0x00;

// The next opcode bytes is data to be pushed onto the stack
//N/A            = 0x01-0x4b

// The next byte contains the number of bytes to be pushed onto the stack.
var OP_PUSHDATA1 = 0x4c

// The next two bytes contain the number of bytes to be pushed onto the stack.
var OP_PUSHDATA2 = 0x4d

// The next four bytes contain the number of bytes to be pushed onto the stack.
var OP_PUSHDATA4 = 0x4e

// The number -1 is pushed onto the stack.
var OP_1NEGATE = 0x4f

// The number 1 is pushed onto the stack.
var OP_1 = 0x51
var OP_TRUE = 0x51

// The number in the word name (2-16) is pushed onto the stack.
var OP_2 = 0x52
var OP_3 = 0x53
var OP_4 = 0x54
var OP_5 = 0x55
var OP_6 = 0x56
var OP_7 = 0x57
var OP_8 = 0x58
var OP_9 = 0x59
var OP_10 = 0x5a
var OP_11 = 0x5b
var OP_12 = 0x5c
var OP_13 = 0x5d
var OP_14 = 0x5e
var OP_15 = 0x5f
var OP_16 = 0x60


//////////////////////////////////////
// Flow Control

// Does nothing.
var OP_NOP = 0x61

// If the top stack value is not 0, the statements are executed. The top
// stack value is removed.
var OP_IF = 0x63

// If the top stack value is 0, the statements are executed. The top stack
// value is removed.
var OP_NOTIF = 0x64

// If the preceding var OP_IF or var OP_NOTIF or var OP_ELSE was not executed then these
// statements are and if the preceding var OP_IF or var OP_NOTIF or var OP_ELSE was
// executed then these statements are not.
var OP_ELSE = 0x67

// Ends an if/else block.
var OP_ENDIF = 0x68

// Marks transaction as invalid if top stack value is not true. True is
// removed, but false is not.
var OP_VERIFY = 0x69

// Marks transaction as invalid.
var OP_RETURN = 0x6a


//////////////////////////////////////
// Stack

// Puts the input onto the top of the alt stack. Removes it from the main stack.
var OP_TOALTSTACK = 0x6b

// Puts the input onto the top of the main stack. Removes it from the alt stack.
var OP_FROMALTSTACK = 0x6c

// If the top stack value is not 0, duplicate it.
var OP_IFDUP = 0x73

// Puts the number of stack items onto the stack.
var OP_DEPTH = 0x74

// Removes the top stack item.
var OP_DROP = 0x75

// Duplicates the top stack item.
var OP_DUP = 0x76

// Removes the second-to-top stack item.
var OP_NIP = 0x77

// Copies the second-to-top stack item to the top.
var OP_OVER = 0x78

// The item ''n'' back in the stack is copied to the top.
var OP_PICK = 0x79

// The item ''n'' back in the stack is moved to the top.
var OP_ROLL = 0x7a

// The top three items on the stack are rotated to the left.
var OP_ROT = 0x7b

// The top two items on the stack are swapped.
var OP_SWAP = 0x7c

// The item at the top of the stack is copied and inserted before the
// second-to-top item.
var OP_TUCK = 0x7d

// Removes the top two stack items.
var OP_2DROP = 0x6d

// Duplicates the top two stack items.
var OP_2DUP = 0x6e

// Duplicates the top three stack items.
var OP_3DUP = 0x6f

// Copies the pair of items two spaces back in the stack to the front.
var OP_2OVER = 0x70

// The fifth and sixth items back are moved to the top of the stack.
var OP_2ROT = 0x71

// Swaps the top two pairs of items.
var OP_2SWAP = 0x72


//////////////////////////////////////
// Splice

// Concatenates two strings.
var OP_CAT = 0x7e

// Returns a section of a string.
var OP_SUBSTR = 0x7f

// Keeps only characters left of the specified point in a string.
var OP_LEFT = 0x80

// Keeps only characters right of the specified point in a string.
var OP_RIGHT = 0x81

// Pushes the string length of the top element of the stack (without popping it).
var OP_SIZE = 0x82


//////////////////////////////////////
// Bitwise Logic

// Flips all of the bits in the input.
var OP_INVERT = 0x83

// Boolean ''and'' between each bit in the inputs.
var OP_AND = 0x84

// Boolean ''or'' between each bit in the inputs.
var OP_OR = 0x85

// Boolean ''exclusive or'' between each bit in the inputs.
var OP_XOR = 0x86

// Returns 1 if the inputs are exactly equal, 0 otherwise.
var OP_EQUAL = 0x87

// Same as var OP_EQUAL, but runs var OP_VERIFY afterward.
var OP_EQUALVERIFY = 0x88

//////////////////////////////////////
// Arithmetic

// 1 is added to the input.
var OP_1ADD = 0x8b

// 1 is subtracted from the input.
var OP_1SUB = 0x8c

// The input is multiplied by 2.
var OP_2MUL = 0x8d

// The input is divided by 2.
var OP_2DIV = 0x8e

// The sign of the input is flipped.
var OP_NEGATE = 0x8f

// The input is made positive.
var OP_ABS = 0x90

// If the input is 0 or 1, it is flipped. Otherwise the output will be 0.
var OP_NOT = 0x91

// Returns 0 if the input is 0. 1 otherwise.
var OP_0NOTEQUAL = 0x92

// a is added to b.
var OP_ADD = 0x93

// b is subtracted from a.
var OP_SUB = 0x94

// a is multiplied by b.
var OP_MUL = 0x95

// a is divided by b.
var OP_DIV = 0x96

// Returns the remainder after dividing a by b.
var OP_MOD = 0x97

// Shifts a left b bits, preserving sign.
var OP_LSHIFT = 0x98

// Shifts a right b bits, preserving sign.
var OP_RSHIFT = 0x99

// If both a and b are not 0, the output is 1. Otherwise 0.
var OP_BOOLAND = 0x9a

// If a or b is not 0, the output is 1. Otherwise 0.
var OP_BOOLOR = 0x9b

// Returns 1 if the numbers are equal, 0 otherwise.
var OP_NUMEQUAL = 0x9c

// Same as var OP_NUMEQUAL, but runs var OP_VERIFY afterward.
var OP_NUMEQUALVERIFY = 0x9d

// Returns 1 if the numbers are not equal, 0 otherwise.
var OP_NUMNOTEQUAL = 0x9e

// Returns 1 if a is less than b, 0 otherwise.
var OP_LESSTHAN = 0x9f

// Returns 1 if a is greater than b, 0 otherwise.
var OP_GREATERTHAN = 0xa0

// Returns 1 if a is less than or equal to b, 0 otherwise.
var OP_LESSTHANOREQUAL = 0xa1

// Returns 1 if a is greater than or equal to b, 0 otherwise.
var OP_GREATERTHANOREQUAL = 0xa2

// Returns the smaller of a and b.
var OP_MIN = 0xa3

// Returns the larger of a and b.
var OP_MAX = 0xa4

// Returns 1 if x is within the specified range (left-inclusive), 0 otherwise.
var OP_WITHIN = 0xa5


//////////////////////////////////////
// Crypto

// The input is hashed using RIPEMD-160.
var OP_RIPEMD160 = 0xa6

// The input is hashed using SHA-1.
var OP_SHA1 = 0xa7

// The input is hashed using SHA-256.
var OP_SHA256 = 0xa8

// The input is hashed twice: first with SHA-256 and then with RIPEMD-160.
var OP_HASH160 = 0xa9

// The input is hashed two times with SHA-256.
var OP_HASH256 = 0xaa

// All of the signature checking words will only match signatures to the data
// after the most recently-executed var OP_CODESEPARATOR.
var OP_CODESEPARATOR = 0xab

// The entire transaction's outputs, inputs, and script (from the most
// recently-executed var OP_CODESEPARATOR to the end) are hashed. The signature
// used by var OP_CHECKSIG must be a valid signature for this hash and public
// key. If it is, 1 is returned, 0 otherwise.
var OP_CHECKSIG = 0xac

// Same as var OP_CHECKSIG, but var OP_VERIFY is executed afterward.
var OP_CHECKSIGVERIFY = 0xad

// For each signature and public key pair, var OP_CHECKSIG is executed. If more
// public keys than signatures are listed, some key/sig pairs can fail. All
// signatures need to match a public key. If all signatures are valid, 1 is
// returned, 0 otherwise. Due to a bug, one extra unused value is removed
// from the stack.
var OP_CHECKMULTISIG = 0xae

// Same as var OP_CHECKMULTISIG, but var OP_VERIFY is executed afterward.
var OP_CHECKMULTISIGVERIFY = 0xaf


//////////////////////////////////////
// Pseudo-words

// Represents a public key hashed with var OP_HASH160.
var OP_PUBKEYHASH = 0xfd

// Represents a public key compatible with var OP_CHECKSIG.
var OP_PUBKEY = 0xfe

// Matches any opcode that is not yet assigned.
var OP_INVALIDOPCODE = 0xff


//////////////////////////////////////
// Reserved words

// Transaction is invalid unless occuring in an unexecuted var OP_IF branch
var OP_RESERVED = 0x50

// Transaction is invalid unless occuring in an unexecuted var OP_IF branch
var OP_VER = 0x62

// Transaction is invalid even when occuring in an unexecuted var OP_IF branch
var OP_VERIF = 0x65

// Transaction is invalid even when occuring in an unexecuted var OP_IF branch
var OP_VERNOTIF = 0x66

// Transaction is invalid unless occuring in an unexecuted var OP_IF branch
var OP_RESERVED1 = 0x89

// Transaction is invalid unless occuring in an unexecuted var OP_IF branch
var OP_RESERVED2 = 0x8a

// The word is ignored.
var OP_NOP1 = 0xb0
var OP_NOP2 = 0xb1
var OP_NOP3 = 0xb2
var OP_NOP4 = 0xb3
var OP_NOP5 = 0xb4
var OP_NOP6 = 0xb5
var OP_NOP7 = 0xb6
var OP_NOP8 = 0xb7
var OP_NOP9 = 0xb8
var OP_NOP10 = 0xb9

var OP_HASHVERIFY = 0xb7 // NOP8
var OP_HASH512 = 0xb8 // NOP9   // The input is hash512 and hash160 and then hash256
var OP_MINERHASH = 0xb9 // NOP10

// DISABLED = frozenset([var OP_CAT, var OP_SUBSTR, var OP_LEFT, var OP_RIGHT, var OP_INVERT, var OP_AND,
//   var OP_OR, var OP_XOR, var OP_2MUL, var OP_2DIV, var OP_MUL, var OP_DIV, var OP_MOD,
//   var OP_LSHIFT, var OP_RSHIFT])

// RESERVED = frozenset([var OP_RESERVED, var OP_VER, var OP_VERIF, var OP_VERNOTIF, var OP_RESERVED1,
//   var OP_RESERVED2, var OP_NOP1, var OP_NOP2, var OP_NOP3, var OP_NOP4,
//   var OP_NOP5, var OP_NOP6, var OP_NOP7, var OP_NOP8, var OP_NOP9, OP_NOP10])

var OPCODE_NAMES = ['OP_FALSE', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
    'N/A', 'N/A', 'N/A', 'N/A', 'OP_PUSHDATA1', 'OP_PUSHDATA2',
    'OP_PUSHDATA4', 'OP_1NEGATE', 'OP_RESERVED', 'OP_TRUE',
    'OP_2', 'OP_3', 'OP_4', 'OP_5', 'OP_6', 'OP_7', 'OP_8',
    'OP_9', 'OP_10', 'OP_11', 'OP_12', 'OP_13', 'OP_14', 'OP_15',
    'OP_16', 'OP_NOP', 'OP_VER', 'OP_IF', 'OP_NOTIF', 'OP_VERIF',
    'OP_VERNOTIF', 'OP_ELSE', 'OP_ENDIF', 'OP_VERIFY',
    'OP_RETURN', 'OP_TOALTSTACK', 'OP_FROMALTSTACK', 'OP_2DROP',
    'OP_2DUP', 'OP_3DUP', 'OP_2OVER', 'OP_2ROT', 'OP_2SWAP',
    'OP_IFDUP', 'OP_DEPTH', 'OP_DROP', 'OP_DUP', 'OP_NIP',
    'OP_OVER', 'OP_PICK', 'OP_ROLL', 'OP_ROT', 'OP_SWAP',
    'OP_TUCK', 'OP_CAT', 'OP_SUBSTR', 'OP_LEFT', 'OP_RIGHT',
    'OP_SIZE', 'OP_INVERT', 'OP_AND', 'OP_OR', 'OP_XOR',
    'OP_EQUAL', 'OP_EQUALVERIFY', 'OP_RESERVED1', 'OP_RESERVED2',
    'OP_1ADD', 'OP_1SUB', 'OP_2MUL', 'OP_2DIV', 'OP_NEGATE',
    'OP_ABS', 'OP_NOT', 'OP_0NOTEQUAL', 'OP_ADD', 'OP_SUB',
    'OP_MUL', 'OP_DIV', 'OP_MOD', 'OP_LSHIFT', 'OP_RSHIFT',
    'OP_BOOLAND', 'OP_BOOLOR', 'OP_NUMEQUAL', 'OP_NUMEQUALVERIFY',
    'OP_NUMNOTEQUAL', 'OP_LESSTHAN', 'OP_GREATERTHAN',
    'OP_LESSTHANOREQUAL', 'OP_GREATERTHANOREQUAL', 'OP_MIN',
    'OP_MAX', 'OP_WITHIN', 'OP_RIPEMD160', 'OP_SHA1', 'OP_SHA256',
    'OP_HASH160', 'OP_HASH256', 'OP_CODESEPARATOR', 'OP_CHECKSIG',
    'OP_CHECKSIGVERIFY', 'OP_CHECKMULTISIG',
    'OP_CHECKMULTISIGVERIFY', 'OP_NOP1', 'OP_NOP2', 'OP_NOP3',
    'OP_NOP4', 'OP_NOP5', 'OP_NOP6', 'OP_NOP7', 'OP_HASHVERIFY',
    'OP_HASH512', 'OP_MINERHASH', null, null, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null,
    null, null, null, null, null, null, null, null, null, null,
    null, 'OP_PUBKEYHASH', 'OP_PUBKEY', 'OP_INVALIDOPCODE']

function get_opcode_name(opcode) {
    if (opcode < 0 || opcode > 255) {
        throw 'opcode must be 1 byte'
    }
    var name = OPCODE_NAMES[opcode]
    if (name == null) return OPCODE_NAMES[0xff];
    return name
}

function get_opcode(opcode_name) {
    // return OPCODE_NAMES.index(opcode_name)
}

function is_disabled(opcode) {
    // return opcode in DISABLES
}

function is_reserved(opcode) {
    // return opcode in RESERVED
}

module.exports = {
    __all__, OP_0, OP_1, OP_2, OP_3, OP_4, OP_5, OP_6, OP_7, OP_8, OP_9, OP_10, OP_11, OP_12, OP_13, OP_14, OP_15, OP_16, OP_FALSE, OP_PUSHDATA1, OP_PUSHDATA2, OP_PUSHDATA4, OP_1NEGATE, OP_TRUE, OP_NOP, OP_IF, OP_NOTIF, OP_ELSE, OP_ENDIF, OP_VERIFY, OP_RETURN, OP_TOALTSTACK, OP_FROMALTSTACK, OP_IFDUP, OP_DEPTH, OP_DROP, OP_DUP, OP_NIP, OP_OVER, OP_PICK, OP_ROLL, OP_ROT, OP_SWAP, OP_TUCK, OP_2DROP, OP_2DUP,
    OP_3DUP, OP_2OVER, OP_2ROT, OP_2SWAP, OP_CAT, OP_SUBSTR, OP_LEFT, OP_RIGHT, OP_SIZE, OP_INVERT, OP_AND, OP_OR, OP_XOR, OP_EQUAL, OP_EQUALVERIFY, OP_1ADD, OP_1SUB, OP_2MUL, OP_2DIV, OP_NEGATE, OP_ABS, OP_NOT, OP_0NOTEQUAL, OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD,
    OP_LSHIFT, OP_RSHIFT, OP_BOOLAND, OP_BOOLOR, OP_NUMEQUAL, OP_NUMEQUALVERIFY, OP_NUMNOTEQUAL, OP_LESSTHAN, OP_GREATERTHAN, OP_LESSTHANOREQUAL, OP_GREATERTHANOREQUAL, OP_MIN, OP_MAX, OP_WITHIN, OP_RIPEMD160, OP_SHA1, OP_SHA256, OP_HASH160, OP_HASH256, OP_CODESEPARATOR, OP_CHECKSIG, OP_CHECKSIGVERIFY, OP_CHECKMULTISIG, OP_CHECKMULTISIGVERIFY, OP_PUBKEYHASH, OP_PUBKEY, OP_INVALIDOPCODE, OP_RESERVED, OP_VER, OP_VERIF, OP_VERNOTIF, OP_RESERVED1, OP_RESERVED2, OP_NOP1, OP_NOP2, OP_NOP3, OP_NOP4, OP_NOP5, OP_NOP6, OP_NOP7, OP_NOP8, OP_NOP9, OP_NOP10,
    OP_HASHVERIFY, OP_HASH512, OP_MINERHASH, OPCODE_NAMES,
    get_opcode_name,
}