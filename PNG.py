class Chunk:
    def __init__(self, type, data):
        self.type = type
        self.data = data

    '''Write this chunk to the file-like object. Assumes that self.data is set
    and up to date.'''
    def write(self, f):
        import binascii
        import struct
        crcdata = self.type + self.data
        crc = binascii.crc32(crcdata)
        l = len(self.data)
        f.write(struct.pack(">i4s%ssi" % l, l, self.type, self.data, crc))

    def create(data):
        # Can't do this, what type is it? Use constructor.
        # TODO: exception?
        assert 1 == 0
    
    '''Read a chunk from the file-like object f, and return an object representing it.'''
    def read(f):
        import binascii
        import struct
        # Get the length
        length = struct.unpack(">I", f.read(4))[0]
        # Now get the type + data
        rawdata = f.read(4 + length)
        # Split and store them
        (chunktype, data) = struct.unpack(">4s%ss" % length, rawdata)
        # Finally get the CRC
        pngCRC = struct.unpack(">i", f.read(4))[0]
        # Check them
        myCRC = binascii.crc32(rawdata)
        if pngCRC != myCRC:
            print("ERROR: got CRC %d, calculated CRC %d" % (pngCRC, myCRC))
        # TODO: Somehow using getattr() would be better I think...
        if chunktype in globals():
            c = globals()[chunktype].create(data)
        else:
            c = Chunk(chunktype, data)
        return c
    read = staticmethod(read)

"""
A Chunk subclass which represents a tEXt chunk. tEXt is an ISO-8859-1 arbitary
text comment block.
"""
class tEXt(Chunk):
    def __init__(self, keyword, content):
        Chunk.__init__(self, b"tEXt", '')
        self.keyword = keyword
        self.content = content

    def create(data):
        import codecs
        (keyword, content) = data.split("\0")
        # TODO: handle keyword
        (utf8_content, length) = codecs.getdecoder("iso-8859-1")(content)
        # TODO: error check and throw exceptions
        c = tEXt(keyword, utf8_content)
        c.data = data
        return c
    create = staticmethod(create)
    
    def write(self, f):
        import codecs
        # TODO: handle keyword
        (encoded_content, length) = codecs.getencoder("iso-8859-1")(self.content)
        # TODO: error check and throw exceptions
        self.data = '\0'.join((self.keyword, encoded_content))
        Chunk.write(self, f)

    def __str__(self):
        return "%s: %s" % (self.keyword, self.content)


class pHYs(Chunk):
    def __init__(self, pixels_x, pixels_y, units):
        Chunk.__init__(self, b'pHYs', '')
        self.pixels_x = pixels_x
        self.pixels_y = pixels_y
        self.units = units

    def create(data):
        import struct
        c = pHYs(*struct.unpack("!IIb", data))
        c.data = data
        return c
    create = staticmethod(create)

    def write(self, f):
        import struct
        self.data = struct.pack("!IIb", self.pixels_x, self.pixels_y, self.units)
        Chunk.write(self, f)

class tIME(Chunk):
    def __init__(self, year, month, day, hour, minute, second):
        Chunk.__init__(self, b'tIME', '')
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def create(data):
        import struct
        c = tIME(*struct.unpack("!Hbbbbb", data))
        c.data = data
        return c
    create = staticmethod(create)

    def write(self, f):
        import struct
        self.data = struct.pack("!Hbbbbb", self.year, self.month, self.day, self.hour, self.minute, self.second)
        Chunk.write(self, f)

"""
A Chunk subclass which represents the image header chunk, IHDR.
"""
class IHDR(Chunk):
    def __init__(self, width, height, depth, colourtype, compression, filtering, interlacing):
        Chunk.__init__(self, b"IHDR", '')
        self.width = width
        self.height = height
        self.depth = depth
        self.colourtype = colourtype
        self.compression = compression
        self.filter = filtering
        self.interlacing = interlacing

    def create(data):
        import struct
        c = IHDR(*struct.unpack("!iibbbbb", data))
        c.data = data
        return c
    create = staticmethod(create)

    def write(self, f):
        import struct
        self.data = struct.pack("!iibbbbb", self.width, self.height, self.depth, self.colourtype, self.compression, self.filter, self.interlacing)
        Chunk.write(self, f)

# TODO: an incremental reader which allows for very fast reading

'''The PNG header bytes.'''
HEADER = b"\x89PNG\r\n\x1A\n"


class Png:
    def __init__(self, chunks = []):
        self.chunks = chunks
    
    '''Get all chunks of a specified type'''
    def get_chunks(self, t):
        if type(t) is str:
            return [c for c in self.chunks if c.type == t]
        else:
            return [c for c in self.chunks if isinstance(c, t)]
        
    '''Write the specified PNG to the file-like object f.'''
    def write(self, f):
        f.write(HEADER)
        [c.write(f) for c in self.chunks]

    '''Parse a PNG from the file-like object f'''
    def open(f):
        # Check PNG header
        if f.read(8) != HEADER:
            raise PngFormatException
        # Okay, create a chunks list
        chunks = []
        # And read them in
        while 1:
            c = Chunk.read(f)
            chunks.append(c)
            if (c.type == b"IEND"):
                # TODO: fix while loop
                return Png(chunks)
    open = staticmethod(open)
        
'''Exception raised when an invalid PNG file is parsed'''
class PngFormatException (Exception):
    pass

