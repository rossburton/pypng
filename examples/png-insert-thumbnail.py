#! /usr/bin/python

# Generate a 128x128 thumbnail and put it in a thMB chunk as a PNG image.

if __name__ == "__main__":
    import sys
    import pygtk ; pygtk.require("2.0")
    import gtk.gdk as gdk
    
    THUMBNAIL_CHUNK = 'thMB'
    
    pixbuf = gdk.pixbuf_new_from_file(sys.argv[1])
    
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    
    # Target height is 128x128
    target_width = target_height = 128
    
    # Scale the target width and heights. Yucky +0.0 to get floats
    if width > height:
        target_height = int(target_height * ((height + 0.0) / (width + 0.0)))
    elif width < height:
        target_width = int(target_width * ((width + 0.0) / (height + 0.0)))
        
    # Do the scale
    thumb = pixbuf.scale_simple(target_width, target_height, gdk.INTERP_HYPER)
    
    # Now transform thumb into a valid PNG file
    
    # A little hacky, but it works. :(
    THUMB_FILENAME = "/tmp/temp-thumb.png"
    thumb.save(THUMB_FILENAME, "png")
    thumb = ""
    for line in file(THUMB_FILENAME, 'rb'):
        thumb = thumb + line
    # End of nasty evil foul hack
    
    # Insert the PNG as a sub-image into the original
    from PNG import Png, Chunk
    f = open(sys.argv[1], 'rb')
    png = Png.open(f)
    f.close()
    
    # Kill existing thumbnail
    [png.chunks.remove(c) for c in png.chunks if c.type == THUMBNAIL_CHUNK]
    
    # Add a new one
    c = Chunk(THUMBNAIL_CHUNK, thumb)
    # Insert this chunk at the beginning, after the IHDR and probably after the RDF.
    png.chunks.insert(1, c)
    
    f = file(sys.argv[1], 'wb')
    png.write(f)
    f.close()
