import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class TTRFileChooser(Gtk.Window):
    def __init__(self, filetypes = []):
        Gtk.Window.__init__(self, title="Verzeichnisauswahl")

        box = Gtk.Box(spacing=6)
        self.add(box)

        button1 = Gtk.Button("Datei auswaehlen")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

        button2 = Gtk.Button("Verzeichnis auswaehlen")
        button2.connect("clicked", self.on_folder_clicked)
        box.add(button2)

        self._fileName = ""
        self._folderName = ""

        self.filetypes = filetypes

    def getFileName(self):
        return self._fileName

    def getFolderName(self):
        return self._folderName

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Bitte waehle eine Datei aus", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Datei auswaehlen wurde geklickt")
            self._fileName = dialog.get_filename()
            print("Selektierte Datei: " + self._fileName)
        elif response == Gtk.ResponseType.CANCEL:
            print("Vorgang wurde durch den Benutzer abgebrochen")

        dialog.destroy()

    def add_filters(self, dialog):
        filter = Gtk.FileFilter()
        filter.set_name("Mediendateien")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        for i in self.filetypes:
           filter.add_pattern("*" + i)
        dialog.add_filter(filter)


    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Bitte waehle ein Verzeichnis aus", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Verzeichnis auswaehlen wurde geklickt")
            self._folderName = dialog.get_filename()
            print("Folder selected: " + self._folderName)
        elif response == Gtk.ResponseType.CANCEL:
            print("Vorgang wurde durch den Benutzer abgebrochen")

        dialog.destroy()
