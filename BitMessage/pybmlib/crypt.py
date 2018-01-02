import hashlib, ctypes, pyelliptic
import protocol
from pyelliptic import arithmetic
from pyelliptic.openssl import OpenSSL

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def encodeBase(num, alphabet):
    if num == 0:
        return alphabet[0]

    a = []
    base = len(alphabet)
    while num:
        i = num % base
        num = num // base
        a.append(alphabet[i])
    a.reverse()
    return ''.join(a)
def encodeBase58(num):
    return encodeBase(num, BASE58_ALPHABET)

def decodeBase(s, alphabet):
    base = len(alphabet)
    length = len(s)
    num = 0

    try:
        p = length - 1
        for c in s:
            num += alphabet.index(c) * (base ** p)
            p -= 1
    except:
        return 0
    return num
def decodeBase58(s):
    return decodeBase(s, BASE58_ALPHABET)

def shash(algorithm, data):
    m = hashlib.new(algorithm)
    m.update(data)
    return m.digest()

def checksum(data):
    return shash('sha512', data)[0:4]

def pow(data):
    data = shash('sha512', data)
    return shash('sha512', data)

def addr(data):
    data = shash('sha512', data)
    return shash('ripemd160', data)

def encodeAddress(ripe, stream = 1, version = 2):
    if version >= 2:
        if len(ripe) != 20:
            raise Exception('Ripe length not equels to 20')
        if ripe[:2] == '\x00\x00':
            ripe = ripe[2:]
        elif ripe[:1] == '\x00':
            ripe = ripe[1:]
    a = ''

    a += protocol.encodeVarInt(version)
    a += protocol.encodeVarInt(stream)
    a += ripe

    h = pow(a)[0:4]

    a += h

    v = int(a.encode('hex'), 16)
    return 'BM-%s' % (encodeBase58(v))
def decodeAddress(address):
    address = str(address).strip()

    if address[:3] == 'BM-':
        i = decodeBase58(address[3:])
    else:
        i = decodeBase58(address)
    if i == 0:
        return ('invalidcharacters', 0, 0, 0)

    hexdata = hex(i)[2:-1]

    if len(hexdata) % 2 != 0:
        hexdata = '0' + hexdata

    data = hexdata.decode('hex')
    checksum = data[-4:]

    a = data[:-4]
    h = pow(a)[0:4]

    if checksum != h:
        return ('checksumfailed', 0, 0, 0)

    (version, size) = protocol.decodeVarInt(data[:9])

    if version == 0 or version > 3:
        return ('versiontoohigh', 0, 0, 0)

    (stream, isize) = protocol.decodeVarInt(data[size:])

    ripe = data[size + isize:-4]

    if 2 <= version <= 3:
        if len(ripe) == 19:
            ripe = '\x00' + ripe
        elif len(ripe) == 18:
            ripe = '\x00\x00' + ripe
        elif len(ripe) != 20:
            return ('badripe', 0, 0, 0)

    return ('success', version, stream, ripe)

def pointMul(privKey):
    ecKey = OpenSSL.EC_KEY_new_by_curve_name(OpenSSL.get_curve('secp256k1'))
    priv_key = OpenSSL.BN_bin2bn(privKey, 32, 0)
    group = OpenSSL.EC_KEY_get0_group(ecKey)
    pub_key = OpenSSL.EC_POINT_new(group)

    OpenSSL.EC_POINT_mul(group, pub_key, priv_key, None, None, None)
    OpenSSL.EC_KEY_set_private_key(ecKey, priv_key)
    OpenSSL.EC_KEY_set_public_key(ecKey, pub_key)

    size = OpenSSL.i2o_ECPublicKey(ecKey, 0)
    mb = ctypes.create_string_buffer(size)
    OpenSSL.i2o_ECPublicKey(ecKey, ctypes.byref(ctypes.pointer(mb)))

    OpenSSL.EC_POINT_free(pub_key)
    OpenSSL.BN_free(priv_key)
    OpenSSL.EC_KEY_free(ecKey)
    return mb.raw

class KeyPair:
    def __init__(self, size = 32):
        self.privKey = OpenSSL.rand(size)
        self.pubKey = pointMul(self.privKey)
