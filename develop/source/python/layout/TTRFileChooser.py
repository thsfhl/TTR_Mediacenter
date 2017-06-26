import gi
from database.FileType import FileType

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class TTRFileChooser(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Verzeichnisauswahl")
        self.set_position(Gtk.WindowPosition.CENTER)

        self._box = Gtk.Box(spacing=6)
        self.add(self._box)

        self._button1 = Gtk.Button("Datei auswaehlen")
        self._button1.connect("clicked", self.on_file_clicked)
        self._box.add(self._button1)

        self._button2 = Gtk.Button("Verzeichnis auswaehlen")
        self._button2.connect("clicked", self.on_folder_clicked)
        self._box.add(self._button2)

        self._button3 = Gtk.Button(label="Cancel")
        self._button3.connect("clicked", self.on_cancel_clicked)
        self._box.add(self._button3)

        self._folder = None
        self._file = None
        self._canceled = True

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Bitte waehle eine Datei aus", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        self.add_filters(dialog)

        response = dialog.run()
        self._file = ""
        if response == Gtk.ResponseType.OK:
            print("Datei auswaehlen wurde geklickt")
            self._file = dialog.get_filename()
            self._canceled = False
            print("Selektierte Datei: " + self._file)
        elif response == Gtk.ResponseType.CANCEL:
            print("Vorgang wurde durch den Benutzer abgebrochen")

        dialog.destroy()
        if (not self._canceled):
            self._button3.set_label("Fertig")
            self.destroy()

    def add_filters(self, dialog):
        filter = Gtk.FileFilter()
        filter.set_name("Mediendateien")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")

        for f in FileType.get_all():
            filter.add_pattern("*%s" % f.get_extension())
        dialog.add_filter(filter)


    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Bitte waehle ein Verzeichnis aus", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        self._folder = ""
        if response == Gtk.ResponseType.OK:
            print("Verzeichnis auswaehlen wurde geklickt")
            self._folder = dialog.get_filename()
            self._canceled = False
            print("Folder selected: " + self._folder)
        elif response == Gtk.ResponseType.CANCEL:
            print("Vorgang wurde durch den Benutzer abgebrochen")

        dialog.destroy()
        if (not self._canceled):
            self._button3.set_label("Fertig")
            self.destroy()

    def on_cancel_clicked(self, widget):
        self.destroy()

    def getFileOrFolder(self):
        if (None != self._folder) and ( '' != self._folder):
            return self._folder
        else:
            return self._file

    def isCanceled(self):
        return self._canceled