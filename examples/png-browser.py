#! /usr/bin/python

import gtk, gtk.glade, gobject
import sys
from PNG import Png

# Show the ancillery/private/reserved/safe-to-copy bits somewhere
# Have human readable names for the chunks

class ChunkView(gtk.Widget):
    # Show the specified chunk
    def load_chunk(self, chunk):
        pass

    # Return a new chunk for the current data
    def save_chunk(self):
        # TODO: or take a chunk to write to?
        return None

class NoneChunkView(ChunkView, gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self)
        self.set_text("Select a chunk")
        self.show()
    
    def load_chunk(self, chunk):
        assert chunk is None

class UnknownChunkView(ChunkView, gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self)
        self.show()
    
    def load_chunk(self, chunk):
        self.set_text("Chunk type: %s" % chunk.type)

class IHDRChunkView(ChunkView, gtk.VBox):
    colour_map = {
        0: "Greyscale",
        2: "RGB",
        3: "Indexed",
        4: "Grayscale with alpha",
        6: "RGB with alpha"
        }
    compression_map = {
        0: "Deflate/Inflate"
        }

    filter_map = {
        0: "Adaptive"
        }

    interlacing_map = {
        0: "None",
        1: "Adam7"
        }

    def __init__(self):
        gtk.VBox.__init__(self, False, 0)
        table = gtk.Table(6, 2, False)
        table.set_border_width(8)
        table.set_row_spacings(8)
        table.set_col_spacings(8)
        self.pack_start(table, expand=False, fill=False)
        
        table.attach(gtk.Label("Size:"), 0, 1, 0, 1)
        self.size = gtk.Label()
        table.attach(self.size, 1, 2, 0, 1)
        
        table.attach(gtk.Label("Bit depth:"), 0, 1, 1, 2)
        self.depth = gtk.Label()
        table.attach(self.depth, 1, 2, 1, 2)

        table.attach(gtk.Label("Colour space:"), 0, 1, 2, 3)
        self.colour = gtk.Label()
        table.attach(self.colour, 1, 2, 2, 3)

        table.attach(gtk.Label("Compression:"), 0, 1, 3, 4)
        self.compression = gtk.Label()
        table.attach(self.compression, 1, 2, 3, 4)

        table.attach(gtk.Label("Filter:"), 0, 1, 4, 5)
        self.filter = gtk.Label()
        table.attach(self.filter, 1, 2, 4, 5)

        table.attach(gtk.Label("Interlacing:"), 0, 1, 5, 6)
        self.interlacing = gtk.Label()
        table.attach(self.interlacing, 1, 2, 5, 6)

        self.show_all()

    def load_chunk(self, chunk):
        self.size.set_text("%dpx x %dpx" % (chunk.width, chunk.height))
        self.depth.set_text("%d bits" % chunk.depth)
        self.colour.set_text(self.colour_map.get(chunk.colourtype, "Unknown"))
        self.compression.set_text(self.compression_map.get(chunk.compression, "Unknown"))
        self.filter.set_text(self.filter_map.get(chunk.filter, "Unknown"))
        self.interlacing.set_text(self.interlacing_map.get(chunk.interlacing, "Unknown"))

class tEXtChunkView(ChunkView, gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 0)
        self.set_border_width(8)
        self.keyword = gtk.Entry()
        self.pack_start(self.keyword, expand=False, fill=True, padding=8)
        scroller = gtk.ScrolledWindow(None, None)
        scroller.set_shadow_type(gtk.SHADOW_IN)
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.content = gtk.TextView()
        scroller.add(self.content)
        self.pack_start(scroller, expand=True, fill=True, padding=8)
        self.show_all()
        
    def load_chunk(self, chunk):
        self.keyword.set_text(chunk.keyword)
        self.content.get_buffer().set_text(chunk.content)

    def save_chunk(self):
        from PNG import tEXt
        buffer = self.content.get_buffer()
        c = tEXt(self.keyword.get_text(), buffer.get_text(*buffer.get_bounds()))
        return c

class pHYsChunkView(ChunkView, gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self, '')
        self.show()
        
    def load_chunk(self, chunk):
        if chunk.units == 0:
            # This is an aspect ratio
            self.set_text("%d:%d" % (chunk.pixels_x, chunk.pixels_y))
        elif chunk.units == 1:
            # This is pixels-per-meter
            self.set_text("%ddpm x %ddpm\n%ddpi x %ddpi" % (chunk.pixels_x, chunk.pixels_y, round(chunk.pixels_x*0.0254), round(chunk.pixels_y*0.0254)))
        else:
            # Unknown units
            self.set_text("%d x %d (unknown units %d)" % (chunk.pixels_x, chunk.pixels_y, chunk.units))

class tIMEChunkView(ChunkView, gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self, '')
        self.show()
        
    def load_chunk(self, chunk):
        import time
        self.set_text(time.strftime("%c", (chunk.year, chunk.month, chunk.day, chunk.hour, chunk.minute, chunk.second, -1, -1, 0)))

class thMBChunkView(ChunkView, gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self, None, None)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.image = gtk.Image()
        self.add_with_viewport(self.image)
        self.show_all()

    def load_chunk(self, chunk):
        from gtk import gdk
        loader = gdk.PixbufLoader()
        loader.write(chunk.data, len(chunk.data))
        # TODO: handle area-prepared etc
        self.image.set_from_pixbuf(loader.get_pixbuf())
        loader.close()

class PngBrowser:
    def __init__(self):
        glade = gtk.glade.XML("png-browser.glade")
        glade.signal_autoconnect(self)
        self.window = glade.get_widget("window")
        self.pane = glade.get_widget("pane")
        self.statusbar = glade.get_widget("statusbar")
        self.status_context_chunk = self.statusbar.get_context_id("Chunk Details")
        self.chunkview = glade.get_widget("chunkview")
        self.chunkview.append_column(gtk.TreeViewColumn("Chunk", gtk.CellRendererText(), text=0))
        self.store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.chunkview.set_model(self.store)
        self.chunkview.get_selection().connect('changed', self.chunkview_selection_cb)
        self.current_iter = None
        self.current_view = None
        
        png = Png.open(file(sys.argv[1], "rb"))
        for c in png.chunks:
            i = self.store.append()
            self.store.set(i, 0, c.type, 1, c)
        self.show_chunk_page(None)
        self.window.show_all()

    def on_file_quit_activate(self, menuitem):
        if self.current_iter is not None:
            chunk = self.current_view.save_chunk()
            if chunk: self.store.set_value(self.current_iter, 1, chunk)

        chunks = []
        self.store.foreach(lambda model, path, iter: chunks.append(model.get_value(iter, 1)))
        Png(chunks).write(file("test.png", "wb"))
        gtk.main_quit()

    def on_chunk_add_activate(self, menuitem):
        print "ADD"
        
    def on_chunk_remove_activate(self, menuitem):
        (store, iter) = self.chunkview.get_selection().get_selected()
        if iter is None: return
        store.remove(iter)

    def get_widget_for_chunk(self, chunk):
        # Another need for a registry or dynamic class lookup
        if chunk is None:
            w = NoneChunkView()
        elif chunk.type == 'IHDR':
            w = IHDRChunkView()
        elif chunk.type == 'tEXt':
            w = tEXtChunkView()
        elif chunk.type == 'pHYs':
            w = pHYsChunkView()
        elif chunk.type == 'tIME':
            w = tIMEChunkView()
        elif chunk.type == 'thMB':
            w = thMBChunkView()
        else:
            w = UnknownChunkView()
        w.load_chunk(chunk)
        w.show()
        return w
    
    def show_chunk_page(self, chunk):
        w = self.get_widget_for_chunk(chunk)
        self.current_view = w
        existing_w = self.pane.get_child2()
        if existing_w: self.pane.remove(existing_w)
        self.pane.add(w)
        # Fiddle status bar
        self.statusbar.pop(self.status_context_chunk)
        if chunk: self.statusbar.push(self.status_context_chunk, "Chunk type: %s, chunk size: %d bytes" % (chunk.type, len(chunk.data)))
            
    def chunkview_selection_cb(self, selection):
        (model, iter) = selection.get_selected()
        if self.current_iter is not None:
            chunk = self.current_view.save_chunk()
            if chunk: model.set_value(self.current_iter, 1, chunk)
        self.current_iter = iter
        if iter is None:
            self.show_chunk_page(None)
        else:
            chunk = model.get_value(iter, 1);
            self.show_chunk_page(chunk)


if __name__ == '__main__':
    browser = PngBrowser()
    gtk.main()
