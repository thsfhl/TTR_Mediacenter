import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GdkPixbuf

#Handler Klasse
class MainWindowHandler:
    
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)
        
    #Destroy the dialog
    def on_dlg_destroy(self, widget, data=None):
        pass

    def onEditMovieActivate(self, menuItem):
        selectedMovie = get_selected_movie()
        movie = Movie()
        movie.assign(selectedMovie)  
        main.EditMovieWindow = EditMovieWindow(movie)        

        
    #Bei Auswahl eines Filmes, werden die Attribute der Filme geladen das passendne Bilde geladen
    def on_treeviewMovieSelection_changed(self,tree_selection) :
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            main.selectedMovie = model.get_value(tree_iter,0)  
            image = main.builder.get_object("FanArtImage")
            image.set_from_pixbuf(update_image(main.selectedMovie.imageFilePath))
            genreBuffer = main.genreBuffer
            genreBuffer.set_text(get_genre_string(main.selectedMovie.genreList))
            
    #handler fuer doppelclick und Enter
    def on_MovieTreeView_row_activated(self, treeview, path, column):
        print('dblClk')
        
    #handler fuer Popupmenue    
    def on_MovieTreeView_Right_Click(self, widget, event):
        if event.button == 3:        
            main.moviePopup.popup(None, None, None, None, event.button , event.time)
    
    #handler fuer Film loeschen auswaehlen
    def del_film_handler(self, menuItem):    
        response = main.delDlg.run()
        main.delDlg.hide()
        if response == 1:
            #hier film loeschen einfuegen
            print("The OK button was clicked")
        elif response == 2:
            print("The Cancel button was clicked")
            

class EditMovieWindowHandler:
    def on_GenreButton_clicked(self, button):
        main.EditGenreWindow = EditGenreWindow(main.EditMovieWindow.movie.genreList) 
    
    def on_SaveButton_clicked(self, button):        
        main.selectedMovie = main.EditMovieWindow.movie
        main.EditMovieWindow.window.destroy()
        
        
        
class EditGenreWindowHandler:
    def on_SaveButton_clicked(self, widget):
        del main.EditMovieWindow.movie.genreList[:]
        for genre in main.EditGenreWindow.liststore:            
            if genre[0] == True:
                main.EditMovieWindow.movie.genreList.append(Genre(genre[1].name))                         
        main.EditMovieWindow.genreText.set_text(get_genre_string(main.EditMovieWindow.movie.genreList))   
        main.EditGenreWindow.window.destroy() 
        
            
class Movie (GObject.GObject):
    name = ""
    filePath = ""
    imageFilePath = ""    
    genreList =[]
    def __init__(self, name='', filePath='', ImageFilePath=''):
            GObject.GObject.__init__(self)
            self.name = name
            self.filePath = filePath
            self.imageFilePath = ImageFilePath
            self.genreList =[]
            
    def assign(self, movie):
        self.name = movie.name
        self.filePath = movie.filePath
        self.imageFilePath = movie.imageFilePath
        for genre in movie.genreList:
            self.genreList.append(genre)

class Genre(GObject.GObject):
    name = ""
    def __init__(self,name):
        GObject.GObject.__init__(self)
        self.name = name
            

            
def set_treeview_cell_txt_colone(tree_column, cell, tree_model, iter, data):
    #model fuer aktuelle Zeile holen
    obj = tree_model[iter][0]    #
    #text fuer aktuelle Zeile setzen
    cell.set_property('text', obj.name)
    
def set_treeview_cell_txt_coltwo(tree_column, cell, tree_model, iter, data):
    #model fuer aktuelle Zeile holen
    obj = tree_model[iter][1]    #
    #text fuer aktuelle Zeile setzen
    cell.set_property('text', obj.name)
    
def update_image(filePath):
    #angezeigtes Bild laden, skalieren und anzeigen
    bgImage =  GdkPixbuf.Pixbuf().new_from_file(filePath)
    bgImage = bgImage.scale_simple(1280,720, GdkPixbuf.InterpType.BILINEAR)
    return bgImage

def show_window(aClass):
    aClass.window.show_now()
    
def get_selected_movie():
    main.TreeView.get_selection() 
    (model, pathlist) = main.TreeView.get_selection().get_selected_rows()
    for path in pathlist :
        tree_iter = model.get_iter(path)
        return model.get_value(tree_iter,0) 
        
#def hide_window(aClass):
#    aClass.window.hide()
    

#aus den Genres einen anzeigbaren String generieren    
def get_genre_string(genreList):
    tmpString = ""
    for genre in genreList:
        if tmpString == "":
            tmpString = genre.name
        else:
            tmpString = tmpString + ", " +  genre.name            
    return (tmpString)


class MainWindow:    
    def __init__(self):        
        #Gtk.Builder zuweisen 
        self.builder = Gtk.Builder()
        #Glade File dem Builder zuweisen
        self.builder.add_from_file("test.glade") 
        #Eventhandler zuweisen
        self.builder.connect_signals(MainWindowHandler())
        
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
        movieListStore = Gtk.ListStore(Movie)
    
        #Spalte fuer die Filme erzeugen    
        cellrenderer = Gtk.CellRendererText()
        treeviewcolumn = Gtk.TreeViewColumn('FilmTitel')
        
        #Setzen des anzeigetextes und Objektes
        treeviewcolumn.set_cell_data_func(cellrenderer, set_treeview_cell_txt_colone)
        
        
        
        #CellRenderer zur Spalte, und Spalte zum TreeView hinzufgen
        treeviewcolumn.pack_start(cellrenderer, True)
        self.TreeView.append_column(treeviewcolumn)
        
        
        #self.update_image()
        #testweise werden Filmobjekte der Liste hinzugefuegt
        Film1 = Movie('Logan','K:/downloads/Filme/Logan/Logan.mkv','K:/downloads/Filme/Logan/Logan-fanart.jpg')
        Film1.genreList.append(Genre('Action'))
        Film1.genreList.append(Genre('Drama'))
        Film1.genreList.append(Genre('Sci-Fi'))

        Film2 = Movie('xXx','K:/downloads/Filme/xXx III/xXx III.mkv','K:/downloads/Filme/xXx III/xXx III-fanart.jpg')
        Film2.genreList.append(Genre('Action'))
        Film2.genreList.append(Genre('Adventure'))
        Film2.genreList.append(Genre('Thriller'))
        
        Film3 = Movie('Rogue One','c:\Filme\Film3.mkv','Rogue One-fanart.jpg')
        Film3.genreList.append(Genre('Action'))
        Film3.genreList.append(Genre('Adventure'))
        Film3.genreList.append(Genre('Sci-Fi'))
        
        movieListStore.append((Film1,))
        movieListStore.append((Film2,))
        movieListStore.append((Film3,))
        self.TreeView.set_model(movieListStore)   

        
        self.window.show() # this shows the 'window1' object
        
    
class EditGenreWindow:
    
    def on_cell_toggled(self, widget, path):
        self.liststore[path][0] = not self.liststore[path][0]   
        
        
    def __init__(self, genreList):
        #Gtk.Builder zuweisen
        self.builder = Gtk.Builder()        
        #Glade File dem Builder zuweisen
        self.builder.add_from_file('EditGenreWindow.glade')
        #Eventhandler zuweisen
        self.builder.connect_signals(EditGenreWindowHandler())
        self.liststore = Gtk.ListStore(bool, Genre)
        genre1 = Genre('Action')
        genre2 = Genre('Drama')
        genre3 = Genre('Fantasy')
        genre4 = Genre('Sci-Fi')
        genre5 = Genre('Thriller')
        genre6 = Genre('Adventure')
        self.liststore.append([False, genre1])
        self.liststore.append([False, genre2])
        self.liststore.append([False, genre3])
        self.liststore.append([False, genre4])
        self.liststore.append([False, genre5])
        self.liststore.append([False, genre6])  
        
        #Übergebene Genres mit der Genreliste vergleichen und die bisher gewählten Genres als aktiv setzen
        for movieGenre in genreList:   
            for genre in self.liststore:
                if movieGenre.name == genre[-1].name:  
                    genre[0] = True
                    break
                    

        self.window = self.builder.get_object("GenreWindow") 
        self.window.set_modal(True)
        #Das Image zuweisen (Noetig, damit man das den Bildbereich bearbeiten kann)
        self.image = self.builder.get_object("FanArtImage")
        #Treeview zuweisen (Noetig, damit man im Treeview rumarbeiten kann
        self.TreeView = self.builder.get_object("GenreTree")
        
        #Einen Liststore erstellen. Hier kommt die Filmliste rein. Die Filme werden als Objekte angehaengt.
        #listStore = Gtk.ListStore(Film)
        
        self.TreeView.set_model(self.liststore)
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)

        genreToggleColumn = Gtk.TreeViewColumn("Toggle", renderer_toggle, active=0)
        self.TreeView.append_column(genreToggleColumn)        
        
        cellrenderer = Gtk.CellRendererText()
        genreColumn = Gtk.TreeViewColumn('Genre')        
        #Setzen des anzeigetextes und Objektes
        genreColumn.set_cell_data_func(cellrenderer, set_treeview_cell_txt_coltwo)
        
        #CellRenderer zur Spalte, und Spalte zum TreeView hinzufgen
        genreColumn.pack_start(cellrenderer, True)
        self.TreeView.append_column(genreColumn)
        self.SaveButton = self.builder.get_object("SaveButton")
        #self.SaveButton.connect("clicked", self.on_SaveButton_clicked)
        show_window(self)
        
class EditMovieWindow:        
    #Film bearbeiten Fenster initialisieren
    def __init__(self, movie=Movie()):
        #
        self.builder = Gtk.Builder()
        self.builder.add_from_file('EditMovie.glade')
        self.builder.connect_signals(EditMovieWindowHandler())
        
        #Das Fenster zuweisen (Hier hat man Zugriff auf alle Funktionen des Hauptfensters)
        self.window = self.builder.get_object("EditMovieWindow") 
        self.window.set_modal(True)
        self.movie = movie
        #Das Image zuweisen (Noetig, damit man das den Bildbereich bearbeiten kann)
        self.image = self.builder.get_object("FanArtImage")
        self.movieFileChooser = self.builder.get_object("MovieFileChooser") 
        self.movieFileChooser.set_filename(self.movie.filePath)
        
        self.fanartFileChooser = self.builder.get_object("FanartFileChooser")
        self.fanartFileChooser.set_filename(self.movie.imageFilePath)
        
        self.movieName = self.builder.get_object("MovieText")
        self.movieName.set_text(self.movie.name)
        self.genreText = self.builder.get_object("GenreText")
        self.genreText.set_text(get_genre_string(self.movie.genreList))
        
        show_window(self)
        #Treeview zuweisen (Noetig, damit man im Treeview rumarbeiten kann
        #self.TreeView = self.builder.get_object("GenreTree")
        
        #Einen Liststore erstellen. Hier kommt die Filmliste rein. Die Filme werden als Objekte angehaengt.
        #listStore = Gtk.ListStore(Film)
        
        #self.TreeView.set_model(self.liststore)
        
        
        
        


       
        
if __name__ == "__main__":
    main = MainWindow() # create an instance of our class
    #main = REditWindow() # create an instance of our class
    Gtk.main() # run the darn thing