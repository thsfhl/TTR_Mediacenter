# -*- coding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GdkPixbuf
from random import randint

from develop.source.python.database.Movie import Movie
from develop.source.python.database.Genre import Genre
from develop.source.python.FilmCrawler import FilmCrawler
from develop.source.python.database.DbUtils import DbUtils

#Handler Klasse
class Handler:
    
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
        
    #Destroy the dialog
    def on_dlg_destroy(self, widget, data=None):
        pass
    
    #Bei Auswahl eines Filmes, werden die Attribute der Filme und das passende Bilde geladen
    def onSelectionChanged(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist:
            tree_iter = model.get_iter(path)
            selected_film = model.get_value(tree_iter,0)
            if selected_film.get_image():
                main.update_image(selected_film.get_image())
            main.update_genre(main.get_genre_string(selected_film.get_genre_list()))
            
    #handler fuer doppelclick und Enter
    def onFilmdblClk(self, treeview, path, column):
        print('dblClk')
        
    #handler fuer Popupmenue    
    def on_button_press(self, widget, event):
        if event.button == 3:        
            main.moviePopup.popup(None, None, None, None, event.button, event.time)
    
    #handler fuer Film loeschen auswaehlen
    def del_film_handler(self, menuItem):    
        response = main.delDlg.run()
        main.delDlg.hide()
        if response == 1:
            #hier film loeschen einfuegen
            print("The OK button was clicked")
        elif response == 2:
            print("The Cancel button was clicked")

# Gtk.TreeCellDataFunc
def titel_cell_data_func(tree_column, cell, tree_model, iter, data):
    #model fuer aktuelle Zeile holen
    obj = tree_model[iter][0]    # tree_model[iter] <-- TreeModelRow

    #text fuer aktuelle Zeile setzen
    cell.set_property('text', obj.get_titel())
    

class RtestWindow:
    
    #angezeigtes Bild laden, skalieren und anzeigen
    def update_image(self,filePath):
        bgImage =  GdkPixbuf.Pixbuf().new_from_file(filePath)
        bgImage = bgImage.scale_simple(1280,720, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(bgImage)
    
    #aus den Genres einen anzeigbaren String generieren    
    def get_genre_string(self, genre_list):
        tmpString = ""
        for genre in genre_list:
            if tmpString == "":
                tmpString = genre.get_name()
            else:
                tmpString = tmpString + ", " + genre.get_name()
        return (tmpString)
    
    def update_genre(self, genreString):
        self.genreBuffer.set_text(genreString)
        
    def __init__(self):
        #Gladedatei Laden
        self.gladefile = "test.glade"
        #Gtk.Builder Instanz 
        self.builder = Gtk.Builder() 

        #Glade File dem Builder zuweisen
        self.builder.add_from_file(self.gladefile) 
        #Eventhandler zuweisen
        self.builder.connect_signals(Handler())
        
        #Das Fenster zuweisen (Hier hat man Zugriff auf alle Funktionen des Hauptfensters)
        self.window = self.builder.get_object("MainWindow") 
        
        #Das Image zuweisen (Noetig, damit man das den Bildbereich bearbeiten kann)
        self.image = self.builder.get_object("FanArtImage")
        #Treeview zuweisen (Noetig, damit man im Treeview rumarbeiten kann
        self.TreeView = self.builder.get_object("MovieTreeView")
        
        self.textviewGenre = self.builder.get_object("genreTextView")
        self.textviewDesc = self.builder.get_object("descTextView")
        self.moviePopup = self.builder.get_object("moviePopUp")
        self.delDlg = self.builder.get_object("delDlg")
        #Loeschdialog ans Fenster anhaengen
        self.delDlg.set_transient_for(self.window)
        self.genreBuffer = self.textviewGenre.get_buffer()
        self.descBuffer = self.textviewDesc.get_buffer()

        #Einen Liststore erstellen. Hier kommt die Filmliste rein. Die Filme werden als Objekte angehaengt.
        listStore = Gtk.ListStore(Movie)
        
        #Spalte fuer die Filme erzeugen       
        cellrenderer = Gtk.CellRendererText()
        treeviewcolumn = Gtk.TreeViewColumn('FilmTitel')
        
        #Setzen des anzeigetextes und Objektes
        treeviewcolumn.set_cell_data_func(cellrenderer, titel_cell_data_func)
        
        #CellRenderer zur Spalte, und Spalte zum TreeView hinzufgen
        treeviewcolumn.pack_start(cellrenderer, True)
        self.TreeView.append_column(treeviewcolumn)
        
        
        #self.update_image()
        #testweise werden Filmobjekte der Liste hinzugefuegt

        # "Echte" Filmobjekte erzeugen:
        db = DbUtils()
        db.create_database()
        filme = FilmCrawler.crawl_folder('D:\Breaking Bad\Breakin_Bad_S01', True)

        if filme:
            for film in filme:
                # 1-3 Genres hinzuf�gen
                for i in range(randint(1, 3)):
                    # Zuf�lliges Genre hinzuf�gen
                    film.add_genre(Genre.get_by_id(randint(1, 5)))
                Movie.persist(film)

        film_liste = Movie.get_all()

        for film in film_liste:
            listStore.append((film, ))

        self.TreeView.set_model(listStore)

        self.window.show()  # this shows the 'window1' object
        
    

if __name__ == "__main__":
    main = RtestWindow() # create an instance of our class
    Gtk.main() # run the darn thing