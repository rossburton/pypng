#! /usr/bin/python

if __name__ == "__main__":
    import sys
    from PNG import Png, tEXt
    
    if len(sys.argv) != 4:
        print "Syntax: png-set-text filename.png key content"
        sys.exit(1)
        
    (filename, key, content) = sys.argv[1:]

    f = file(filename, 'rb')
    png = Png.open(f)
    f.close()
    
    # Kill existing Metadata chunks
    def chunk_killer(chunk):
        if chunk.keyword == key:
            png.chunks.remove(chunk)
    [chunk_killer(c) for c in png.chunks if isinstance(c, tEXt)]

    # Add a new one
    c = tEXt(key, content)
    # Insert this chunk right at the beginning, after the IHDR
    png.chunks.insert(1, c)
    
    # TODO: backup existing
    f = file(filename, 'wb')
    png.write(f)
    f.close()
