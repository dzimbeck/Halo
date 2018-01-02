#!/usr/bin/env python2
import random, string, unittest, struct
from pybmlib import protocol, crypt

class TestProtocol(unittest.TestCase):
    HEADER_DATA_HEX =   'd9b4bee97465737400000000000000002000000076f8186f536f6d65'
    HEADER_DATA_HEX +=  '20646174612049206b6e6f772049747320776f726b732e206c6f6c2e'
    HEADER_PAYLOAD  =   'Some data I know Its works. lol.'

    POW_DATA        =   'hello'
    POW_HASH        =   '0592a10584ffabf96539f3d780d776828c67da1ab5b169e9e8aed838aaecc9ed'
    POW_HASH        +=  '36d49ff1423c55f019e050c66c6324f53588be88894fef4dcffdb74b98e2b200'

    ADDR_DATA       =   'hello'
    ADDR_HASH       =   '79a324faeebcbf9849f310545ed531556882487e'

    ADDRESS_RIPE    =   '0JZM0ZU9BZWJRW1U3NED'
    ADDRESS_STREAM  =   1
    ADDRESS_VERSION =   2
    ADDRESS_STR     =   'BM-4ZVnmd2sEhmMhcpop8ELeuwwzoP3VUp1SJ6'

    MESSAGE_DATA    =   struct.pack('>III32s', 10, 25, 135, "Hello world!")

    def test_header_encode(self):
        header = protocol.Header('test')
        header.update(self.HEADER_PAYLOAD)

        self.assertEqual(header.serialize().encode('hex'), self.HEADER_DATA_HEX)

    def test_header_decode(self):
        header = protocol.Header.unserialize(self.HEADER_DATA_HEX.decode('hex'))

        self.assertEqual(header.payload, self.HEADER_PAYLOAD)

    def test_pow(self):
        self.assertEqual(crypt.pow(self.POW_DATA).encode('hex'), self.POW_HASH)

    def test_addr(self):
        self.assertEqual(crypt.addr(self.ADDR_DATA).encode('hex'), self.ADDR_HASH)

    def test_varint(self):
        def unit(i):
            h = protocol.encodeVarInt(i)
            (ii, s) = protocol.decodeVarInt(h)

            self.assertEqual(ii, i)

        unit(0)
        unit(13)
        unit(313134841)

        with self.assertRaises(Exception):
            unit(-5)

    def test_varstr(self):
        def unit(s):
            h = protocol.encodeVarStr(s)
            (ss, size) = protocol.decodeVarStr(h)

            self.assertEqual(ss, s)

        unit('toto')
        unit('Hello world!')

    def test_varlist(self):
        def unit(*items):
            h = protocol.encodeVarList(*items)
            (ii, size) = protocol.decodeVarList(h)

            self.assertEqual(list(items), ii)

        unit()
        unit(1, 2, 3, 4, 5, 6)
        unit(31341, 315654, 0, 644, 1234)

    def test_address(self):
        def unit(ripe, stream = 1, version = 2):
            a = crypt.encodeAddress(ripe, stream = stream, version = version)
            (status, iversion, istream, iripe) = crypt.decodeAddress(a)

            self.assertEqual(status, 'success')
            self.assertEqual((version, stream, ripe), (iversion, istream, iripe))

        unit(self.ADDRESS_RIPE)
        unit('00000000000000000000')

        self.assertEqual(crypt.encodeAddress(self.ADDRESS_RIPE, self.ADDRESS_STREAM, self.ADDRESS_VERSION)
                         , self.ADDRESS_STR)

    def test_message(self):
        class TestMessage:
            command = 'test'
            def __init__(self, data):
                self.data = data
            def serialize(self):
                return self.data
            @staticmethod
            def unserialize(data):
                return TestMessage(data)

        test_types = {
            'test': TestMessage
        }

        msg = TestMessage(self.MESSAGE_DATA)
        packet = protocol.encode(msg)

        dmsg = protocol.decode(packet, msg_types = test_types)

        self.assertEqual(dmsg.data, self.MESSAGE_DATA)

if __name__ == '__main__':
    unittest.main()
