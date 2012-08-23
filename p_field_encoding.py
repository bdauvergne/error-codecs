import itertools
import struct
import random
import array
import sys

'''
   Idea: encode an array of value in Z_2^32 into Z_p for p prime. Here we use 
   p = 2^23-5.

   Copied from http://www.lshift.net/blog/2006/11/29/gf232-5
'''

__all__ = ('encode', 'decode')

P = 2**32-5
DECODED_BLOCK_SIZE = 2<<19-1
ENCODED_BLOCK_SIZE = 2<<19

def encode(buf):
    assert len(buf) % 4 == 0
    i = 0
    l = []
    while i < len(buf):
        l.append(encode_block(buf[i:i+DECODED_BLOCK_SIZE*4]))
        i += DECODED_BLOCK_SIZE*4
    return ''.join(l)

def decode(buf):
    i = 0
    l = []
    while i < len(buf):
        l.append(decode_block(buf[i:i+ENCODED_BLOCK_SIZE*4]))
        i += ENCODED_BLOCK_SIZE+1
    return ''.join(l)

def encode_block(block):
    assert len(block) <= DECODED_BLOCK_SIZE*4
    assert len(block) % 4 == 0
    bitmap = 0
    words = array.array('I')
    words.fromstring(block)
    if sys.byteorder == 'little':
        words.byteswap()
    bitmap = array.array('B', itertools.repeat(0, 1<<16))
    for c in words:
        v = c >> 13 & 7
        i = c >> 16
        bitmap[i] = v
    for i, c in enumerate(bitmap):
        if c != 255:
            for j in xrange(0, 8):
                if c & (1 << j) == 0:
                    mask = i << 3 + j
                    mask = (1 << 12)*(mask ^ 0x7FFFF)
                    break
            break
    for i, c in enumerate(words):
        words[i] = c ^ (mask << 1)
    words.insert(0, mask)
    if sys.byteorder == 'little':
        words.byteswap()
    return words.tostring()

def decode_block(block):
    assert len(block) <= ENCODED_BLOCK_SIZE*4
    assert len(block) % 4 == 0
    words = array.array('I')
    words.fromstring(block)
    if sys.byteorder == 'little':
        words.byteswap()
    mask = words.pop(0)
    for i, c in enumerate(words):
        words[i] = c ^ (mask<<1)
    if sys.byteorder == 'little':
        words.byteswap()
    return words.tostring()

if __name__ == '__main__':
    size = 1000*1000
    for i in xrange(100):
        s = hex(random.getrandbits(size*8))[2:-1]
        if len(s) != size:
            s = '0'*(2*size-len(s)) + s
        s = s.decode('hex')
        assert s == decode(encode(s))

