#! /usr/bin/python

# Very dumb example to dump the raw IDAT.  After decompression but is not
# a pixel dump as it doesn't decode the filtering.

import sys
from PNG import Png
import zlib

if __name__ == '__main__':
    p = Png.open(open(sys.argv[1], "rb"))
    for c in p.chunks:
        if c.type == b"IDAT":
            data = zlib.decompress(c.data)
            for b in data:
                print("0x%X" % b)
