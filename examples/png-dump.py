#! /usr/bin/python

import sys
from PNG import Png, tEXt

if __name__ == '__main__':
    p = Png.open(open(sys.argv[1], "rb"))
    for c in p.chunks:
        print("Type: %s (%d bytes)" % (c.type, len(c.data)))
        if isinstance(c, tEXt):
            print("%s: %s" % (c.keyword, c.content))
