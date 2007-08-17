#! /usr/bin/python

if __name__ == "__main__":
    import sys
    from PNG import Png
    
    png = Png.open(file(sys.argv[1], "rb"))
    png.write(file(sys.argv[2], "wb"))
