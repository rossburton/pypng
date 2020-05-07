#! /usr/bin/python

if __name__ == "__main__":
    import sys
    from PNG import Png, tEXt
    
    def text_cb(chunk):
        if c.keyword == "Metadata":
            print(c.content)

    png = Png.open(open(sys.argv[1], "rb"))
    [text_cb(c) for c in png.chunks if isinstance(c, tEXt)]
