#! /usr/bin/python

import RDF

# Some namespace helpers
DC = RDF.NS("http://purl.org/dc/elements/1.1/")
RDFS = RDF.NS("rdfs:")

import pygtk; pygtk.require("2.0")
import gtk, gobject

# TODO: subclass gtk.Window?
class RDFEditor (gtk.Window):
    # TODO: in future take a pre-parsed model and provide a convenience function
    # to parse a filename and URI
    def __init__(self, uri):
        gtk.Window.__init__(self)
        
        self.load_namespaces()

        # Probably madness to use a model, should just use the rdf/xml parser
        # directly. Or write a RDF.Model backed GtkTreeModel
        self.rdf = RDF.Model()
        parser = RDF.Parser()
        self.context = RDF.Uri(uri)
        parser.parse_into_model(self.rdf, self.context)

        qs = RDF.Statement(subject = self.context, object = None, predicate = None)
        self.liststore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        for s in self.rdf:
            iter = self.liststore.append()
            self.liststore.set(iter, 0, s)

        self.set_title("RDF Editor")
        vbox = gtk.VBox()
        
        self.treeview = gtk.TreeView(self.liststore)
        def predicate_datafunc(column, renderer, model, iter):
            statement = model.get_value(iter, 0)
            renderer.set_property("text", self.namespaces.get_target(statement.predicate, RDFS.label) or statement.predicate)

        def object_datafunc(column, renderer, model, iter):
            statement = model.get_value(iter, 0)
            renderer.set_property("text", statement.object)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Property", renderer)
        column.set_cell_data_func(renderer, predicate_datafunc)
        self.treeview.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Value", renderer)
        column.set_cell_data_func(renderer, object_datafunc)
        self.treeview.append_column(column)

        # TODO: scrolled window
        vbox.add(self.treeview)

        bbox = gtk.HButtonBox()
        bbox.set_border_width(6)
        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.connect("clicked", self.add_cb)
        bbox.add(add_button)
        
        del_button = gtk.Button(stock=gtk.STOCK_REMOVE)
        del_button.connect("clicked", self.del_cb)
        bbox.add(del_button)

        save_button = gtk.Button(stock=gtk.STOCK_SAVE)
        save_button.connect("clicked", self.save_cb)
        bbox.add(save_button)

        vbox.pack_start(bbox, gtk.FALSE, gtk.FALSE)
        
        self.add(vbox)
        self.show_all()

    '''
    Create self.namespaces which is a model of statements from namespaces to
    human-readable names via the rdfs:label predicate
    '''
    def load_namespaces(self):
        self.namespaces = RDF.Model()
        # TODO: replace with configuration files
        m = {
            DC.title: "Title",
            DC.creator: "Creator",
            DC.description: "Description",
            DC.date: "Date"
            }
        for node,name in m.items():
            self.namespaces.append(RDF.Statement(node, RDFS.label, name))

    '''
    Add button callback
    '''
    def add_cb(self, button):
        dialog = gtk.Dialog("New Node", self.window,
                            gtk.DIALOG_NO_SEPARATOR |
                            gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.add_buttons(
            gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE,
            gtk.STOCK_ADD, gtk.RESPONSE_OK)
        dialog.set_default_response (gtk.RESPONSE_OK)
        dialog.vbox.add(gtk.Label("Enter the new type and value."))

        # TODO: drop-down of known URIs
        type = gtk.Entry()
        type.set_activates_default(gtk.TRUE)
        dialog.vbox.add(type)
        
        value = gtk.Entry()
        value.set_activates_default(gtk.TRUE)
        dialog.vbox.add(value)
        
        dialog.show_all()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            statement = RDF.Statement(subject = self.context,
                                      predicate = RDF.Uri(type.get_text()),
                                      object = value.get_text())
            self.rdf.append(statement)
            iter = self.liststore.append()
            self.liststore.set(iter, 0, statement)
        dialog.destroy()

    '''
    Delete button callback
    '''
    def del_cb(self, button):
        def killer(model, path, iter, rdf):
            del rdf[model.get_value(iter, 0)]
            model.remove(iter)
        self.treeview.get_selection().selected_foreach(killer, self.rdf)
    
    '''
    Save button callback
    '''
    def save_cb(self, button):
        serializer = RDF.Serializer()
        # TODO: this vapes namespace aliases, which sucks. librdf bug.
        serializer.serialize_model_to_file("output.rdf", self.rdf)
    
if __name__ == '__main__':
    import sys
    import os.path

    filename = sys.argv[1]
    # Handle relative paths
    if filename[:1] != '/':
        filename = os.path.abspath(filename)
    # For now, assume a local file was passed
    window = RDFEditor("file://%s" % filename)
    window.show()
    gtk.main()
