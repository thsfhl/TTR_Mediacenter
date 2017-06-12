import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class TTRFileChooser(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Verzeichnisauswahl")

        box = Gtk.Box(spacing=6)
        self.add(box)

        button1 = Gtk.Button("Datei auswaehlen")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

        button2 = Gtk.Button("Verzeichnis auswaehlen")
        button2.connect("clicked", self.on_folder_clicked)
        box.add(button2)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Bitte waehle eine Datei aus", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        self.add_filters(dialog)

        response = dialog.run()
        file = ""
        if response == Gtk.ResponseType.OK:
            print("Datei auswaehlen wurde geklickt")
            file = dialog.get_filename()
            print("Selektierte Datei: " + file)
        elif response == Gtk.ResponseType.CANCEL:
            print("Vorgang wurde durch den Benutzer abgebrochen")

        dialog.destroy()
        return file

    def add_filters(self, dialog):
        filter = Gtk.FileFilter()
        filter.set_name("Mediendateien")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        filter.add_pattern("*.tif")
        filter.add_pattern("*.xpm")
        dialog.add_filter(filter)


    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Bitte waehle ein Verzeichnis aus", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        folder = ""
        if response == Gtk.ResponseType.OK:
            print("Verzeichnis auswaehlen wurde geklickt")
            folder = dialog.get_filename()
            print("Folder selected: " + folder)
        elif response == Gtk.ResponseType.CANCEL:
            print("Vorgang wurde durch den Benutzer abgebrochen")

        dialog.destroy()
        return folder