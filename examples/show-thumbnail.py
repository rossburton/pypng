#! /usr/bin/python

if __name__ == '__main__':
    import sys
    from PNG import Png
    
    png = Png.open(file(sys.argv[1], "rb"))
    
    for c in [c for c in png.chunks if c.type == 'thMB']:
        print(c.data)
        sys.exit(0)
