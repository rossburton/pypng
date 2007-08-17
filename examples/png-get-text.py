#! /usr/bin/python

if __name__ == "__main__":
    import sys
    from PNG import Png, tEXt
    
    if len(sys.argv) != 3:
        print "Syntax: png-get-text filename.png key"
        sys.exit(1)
        
    (filename, key) = sys.argv[1:]

    f = file(filename, 'rb')
    png = Png.open(f)
    f.close()
    
    print "\n".join([c.content for c in png.get_chunks(tEXt) if c.keyword == key])
