import struct
import crypt

HEADER_FORMAT = '<I12sI4s'

# Protocol units
def decodeVarInt(data):
    if len(data) == 0:
        return (0, 0)

    (b,) = struct.unpack('>B', data[0:1])
    if b < 0xfd:
        return (b, 1)
    if b == 0xfd:
        (v,) = struct.unpack('>H', data[1:3])
        return (v, 3)
    elif b == 0xfe:
        (v,) = struct.unpack('>I', data[1:5])
        return (v, 5)
    elif b == 0xff:
        (v,) = struct.unpack('>Q', data[1:9])
        return (v, 9)
    return (0, 0)
def encodeVarInt(i):
    if i < 0:
        raise Exception('varint cannot be < 0')
    if i < 0xfd:
        return struct.pack('>B', i)
    elif i >= 0xfd and i < 0x10000:
        return struct.pack('>BH', 0xfd, i)
    elif i >= 0x10000 and i < 0x100000000:
        return struct.pack('>BI', 0xfe, i)
    elif i >= 0x100000000 and i < 0x10000000000000000L:
        return struct.pack('>BQ', 0xff, i)
    raise Exception('varint cannot be >= 0x10000000000000000L')

def decodeVarStr(data):
    if len(data) == 0:
        return ('', 0)

    (length, size) = decodeVarInt(data)
    if length == 0:
        return ('', size)

    return (data[size:size + length], size + length)
def encodeVarStr(s):
    return encodeVarInt(len(s)) + s

def decodeVarList(data):
    if len(data) == 0:
        return ([], 0)

    (length, size) = decodeVarInt(data)
    if length == 0:
        return ([], size)

    l = []

    for i in range(length):
        (item, isize) = decodeVarInt(data[size:])
        l.append(item)
        size += isize

    return (l, size)
def encodeVarList(*items):
    s = ''

    s += encodeVarInt(len(items))
    for item in items:
        s += encodeVarInt(item)

    return s

# Exceptions
class HeaderException(Exception):
    pass
class ChecksumException(Exception):
    pass

# Messages
class Header:
    def __init__(self, command, magic = 0xE9BEB4D9):
        self.command = command
        self.magic = magic
        self.update('')
    def update(self, payload):
        self.length = len(payload)
        self.csum = crypt.checksum(payload)
        self.payload = payload
    def serialize(self):
        content = ''
        content += struct.pack(HEADER_FORMAT, self.magic, self.command, self.length, self.csum)
        content += self.payload

        return content
    @staticmethod
    def unserialize(data):
        header_size = struct.calcsize(HEADER_FORMAT)
        if len(data) < header_size:
            raise HeaderException('Data size < Header size')
        header_data = data[:header_size]
        (magic, command, length, csum) = struct.unpack(HEADER_FORMAT, header_data)

        header = Header(command.rstrip('\0'), magic)

        if len(data) < header_size + length:
            raise HeaderException('Data size < Header size + Payload length')
        payload = data[header_size:header_size + length]

        if crypt.checksum(payload) != csum:
            raise ChecksumException('Checksums didn\'t correspond.')

        header.update(payload)

        return header
    def __str__(self):
        s = ''

        s += 'Command          : %s\n' % (self.command)
        s += 'Magic            : 0x%08x\n' % (self.magic)
        s += 'Payload length   : %d\n' % (self.length)
        s += 'Payload checksum : %s\n' % (self.csum.encode('hex'))
        s += 'Payload data     : %s\n' % (self.payload.encode('hex'))
        s += '\n'
        s += 'Serialized data  : %s\n' % (self.serialize().encode('hex'))

        return s

MSG_TYPES = {

}

def encode(msg):
    header = Header(msg.command)
    header.update(msg.serialize())

    return header.serialize()

def decode(data, msg_types = MSG_TYPES):
    header = Header.unserialize(data)
    msg = None
    if header.command in msg_types.keys():
        msg_type = msg_types[header.command]
        msg = msg_type.unserialize(header.payload)
    return msg
