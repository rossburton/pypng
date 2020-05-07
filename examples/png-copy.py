#! /usr/bin/python

if __name__ == "__main__":
    import sys
    from PNG import Png
    
    png = Png.open(open(sys.argv[1], "rb"))
    png.write(open(sys.argv[2], "wb"))
