import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GdkPixbuf
from pathlib import Path
from database.Film import Film
from FilmCrawler import FilmCrawler
from database.Persistable import Persistable
from database.DbUtils import DbUtils


##############################################################################################################
##################################################  Handler  #################################################
##############################################################################################################
#Alle Handler für das Hauptfenster
class MainWindowHandler:
    
    #Beenden des Programmes
    def on_QuitMenu_activate(self, *args):
        Gtk.main_quit(*args)
        
    #Beenden des Dialogs
    def on_dlg_destroy(self, widget, data=None):
        pass
    def play_movie_handler(self, menuItem):
        if get_selected_movie(main.TreeView) is None:
            #todo: errodialog anzeigen
            print('error')
        else:
            print('play movie clicked')
    
    def on_ImportMenu_activate(self, menuItem):
        main.ImportMovieWindow = ImportMovieWindow()
           
    #Wird "Film bearbeiten" gewählt"
    def edit_movie_handler(self, menuItem):
        if get_selected_movie(main.TreeView) is None:
            #todo: errodialog anzeigen
            print('error')
        else:
            selectedMovie = get_selected_movie(main.TreeView)
            movie = Movie()
            movie.assign(selectedMovie)  
            main.EditMovieWindow = EditMovieWindow(movie) 
            main.EditMovieWindow.image.set_from_pixbuf(update_image(selectedMovie.imageFilePath))  
        
    def on_EditFileExtensionsMenu_activate(self, menuItemm):
        print('open fileext admin')     

        
    #Bei Auswahl eines Filmes, werden die Attribute der Filme geladen das passendne Bild geladen
    def on_treeviewMovieSelection_changed(self,tree_selection) :
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            main.selectedMovie = model.get_value(tree_iter,0)              
            main.image.set_from_pixbuf(update_image(main.selectedMovie.imageFilePath))
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
            #todo: hier film loeschen einfuegen
            print("The OK button was clicked")
            
class ImportMovieWindowHandler:
    def on_GenreButton_clicked(self, button):        
        selectedMovie = get_selected_movie(main.ImportMovieWindow.TreeView)
        if selectedMovie is None:
            #todo: errodialog anzeigen
            print('error')
        else:
            main.EditGenreWindow = EditGenreWindow(selectedMovie.genreList, main.ImportMovieWindow) 
    
    #Handler, wenn der Editierte Film gespeichert werden soll
    def on_SaveButton_clicked(self, button):    
        #todo savefunktion der Filmliste aufrufen und anschließend den Treeview vom Hauptfenster aktualisierenhier gespeichert werden        
        main.ImportMovieWindow.window.destroy()
    
    #Handler zum schließen ohne speichern
    def on_AbortButton_clicked(self, button):
        main.ImportMovieWindow.window.destroy()
    
    def on_FanartFileChooser_file_set(self, widget):
        selectedMovie = get_selected_movie(main.ImportMovieWindow.TreeView)
        if selectedMovie is None:
            #todo: errodialog anzeigen
            print('error')
        else:
            selectedMovie.imageFilePath = widget.get_filename()
            main.ImportMovieWindow.image.set_from_pixbuf(update_image(widget.get_filename(),480, 272))          
        
    def on_MovieFileChooser_file_set(self, widget):
        selectedMovie = get_selected_movie(main.ImportMovieWindow.TreeView)
        if selectedMovie is None:
            #todo: errodialog anzeigen
            print('error')
        else:
            selectedMovie.filePath = widget.get_filename()        
        
    def on_treeviewMovieSelection_changed(self,tree_selection) :
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            main.ImportMovieWindow.movie = model.get_value(tree_iter,0)              
            main.ImportMovieWindow.image.set_from_pixbuf(update_image(main.ImportMovieWindow.movie.imageFilePath,480, 272))            
            main.ImportMovieWindow.genreText.set_text(get_genre_string(main.ImportMovieWindow.movie.genreList))
            main.ImportMovieWindow.fanartFileChooser.set_filename(main.ImportMovieWindow.movie.imageFilePath)
            main.ImportMovieWindow.movieFileChooser.set_filename(main.ImportMovieWindow.movie.filePath)
            main.ImportMovieWindow.movieName.set_text(main.ImportMovieWindow.movie.name)

    
    def on_MovieText_focus_out_event(self, widget, event):
        selectedMovie = get_selected_movie(main.ImportMovieWindow.TreeView)
        if selectedMovie is not None:
            #keine Fehlermeldung, wenn nur der Text geändert wird
            main.ImportMovieWindow.movie.name = widget.get_text()
    
    def on_ImportFolderFileChooser_file_set(self, widget):
        filme = FilmCrawler.crawl_folder('K:/downloads/The.Boss.Baby.German.DL.AC3.1080p.WebHD.h264-PsO - filecrypt.cc/The.Boss.Baby.German.DL.AC3.1080p.WebHD.h264-PsO/', True)
        if filme:
            for film in filme:
                Film.persist(film)

        film_liste = []
        if (Persistable.get_db() != None):
            film_liste = Film.get_all()

        for film in film_liste:
            main.ImportMovieWindow.movieListStore.append((film, ))
      

#Alle Handler für das Film bearbeiten Fenster
class EditMovieWindowHandler:
    #Handler wenn der Button zum öffnen des GenreFensters genutzt wird
    def on_GenreButton_clicked(self, button):               
        main.EditGenreWindow = EditGenreWindow(main.EditMovieWindow.movie.genreList, main.EditMovieWindow) 
    
    #Handler, wenn der Editierte Film gespeichert werden soll
    def on_SaveButton_clicked(self, button):        
        main.EditMovieWindow.movie.name = main.EditMovieWindow.movieName.get_text()
        main.selectedMovie.assign(main.EditMovieWindow.movie)
        main.image.set_from_pixbuf(update_image(main.selectedMovie.imageFilePath))
        genreBuffer = main.genreBuffer
        genreBuffer.set_text(get_genre_string(main.selectedMovie.genreList))
        #todo: main.selectedMovie muss hier gespeichert werden        
        main.EditMovieWindow.window.destroy()
    
    #Handler zum schließen ohne speichern
    def on_AbortButton_clicked(self, button):
        main.EditMovieWindow.window.destroy()
    
    def on_FanartFileChooser_file_set(self, widget):
        main.EditMovieWindow.movie.imageFilePath = widget.get_filename()
        main.EditMovieWindow.image.set_from_pixbuf(update_image(widget.get_filename()))          
        
    def on_MovieFileChooser_file_set(self, widget):
        main.EditMovieWindow.movie.filePath = widget.get_filename()
                       
         
#Alle Handler für das Genre bearbeiten Fenster      
class EditGenreWindowHandler:
    #Hander zum Speicern der ausgewählten Genres (Kein speichern in der Datenbank, dazu muss noch der Speichern Button beim Film editieren genutzt werden
    def on_SaveButton_clicked(self, widget):
        del main.EditGenreWindow.callWindow.movie.genreList[:]
        for genre in main.EditGenreWindow.liststore:            
            if genre[0] == True:
                main.EditGenreWindow.callWindow.movie.genreList.append(Genre(genre[1].name))                         
        main.EditGenreWindow.callWindow.genreText.set_text(get_genre_string(main.EditGenreWindow.callWindow.movie.genreList))   
        main.EditGenreWindow.window.destroy() 
        
##############################################################################################################
##################################################  Klassen  #################################################
##############################################################################################################  
#Filmklasse
#todo: Dies hier dient nur als Beispiel, wie ein Filmobjekt aufgebaut sein kann. Es muss vom Typ GObject sein (für den Treeview)            
class Movie (GObject.GObject):
    name = ""
    filePath = ""
    imageFilePath = ""    
    genreList =[]
    #Initialisieren der Klasse
    def __init__(self, name='', filePath='', ImageFilePath=''):
            GObject.GObject.__init__(self)
            self.name = name
            self.filePath = filePath
            self.imageFilePath = ImageFilePath
            self.genreList =[]
    #Kopie der Klasse erstellen        
    def assign(self, movie):
        self.name = movie.name
        self.filePath = movie.filePath
        self.imageFilePath = movie.imageFilePath
        self.genreList = []
        for genre in movie.genreList:
            self.genreList.append(genre)
#Genreklasse
#todo: Auch hier dient es nur als Beispiel, muss aber auch vom Typ GObject sein
class Genre(GObject.GObject):
    name = ""
    def __init__(self,name):
        GObject.GObject.__init__(self)
        self.name = name
            
##############################################################################################################
########################################  Allgemeine Funktionen  #############################################
##############################################################################################################  

#Funktion um allen Zellen in Spalte 1 des Treeviews zu einer Textzelle zu machen            
def set_treeview_cell_txt_colone(tree_column, cell, tree_model, iter, data):
    #model fuer aktuelle Zeile holen
    obj = tree_model[iter][0]    
    #text fuer aktuelle Zeile setzen
    cell.set_property('text', obj.get_titel())
    
    
#Funktion um allen Zellen in Spalte 2 des Treeviews zu einer Textzelle zu machen    
def set_treeview_cell_txt_coltwo(tree_column, cell, tree_model, iter, data):
    #model fuer aktuelle Zeile holen
    obj = tree_model[iter][1]    #
    #text fuer aktuelle Zeile setzen
    cell.set_property('text', obj.get_titel())
#Funktion um ein Bild zu laden und anschließend zu skalieren    
def update_image(filePath, x=1280, y=720):
    myfile = Path(filePath)
    if myfile.is_file():
        bgImage =  GdkPixbuf.Pixbuf().new_from_file(filePath)      
    else:
        bgImage =  GdkPixbuf.Pixbuf().new_from_file('default movie.jpg')  
    bgImage = bgImage.scale_simple(x, y, GdkPixbuf.InterpType.BILINEAR)   
    return bgImage

#Funktion zum sichtbar machen von Fenstern
def show_window(aClass):
    aClass.window.show()
#Funktion um sich den aktuell selektierten Film im Haupttreeview zu holen    
def get_selected_movie(treeView):
    treeView.get_selection() 
    (model, pathlist) = treeView.get_selection().get_selected_rows()
    for path in pathlist :
        tree_iter = model.get_iter(path)
        return model.get_value(tree_iter,0) 
     

#Funktion um aus den Genres einen anzeigbaren String generieren    
def get_genre_string(genreList):
    tmpString = ""
    for genre in genreList:
        if tmpString == "":
            tmpString = genre.name
        else:
            tmpString = tmpString + ", " +  genre.name            
    return (tmpString)

##############################################################################################################
##################################################  Fenster  #################################################
##############################################################################################################  

#Hauptfenster
class MainWindow:    
    def __init__(self):        
        #Gtk.Builder zuweisen 
        self.builder = Gtk.Builder()
        #Glade File dem Builder zuweisen
        #todo: umbenennen der Gladefile
        self.builder.add_from_file("MainWindow.glade")         
        #Eventhandler zuweisen
        self.builder.connect_signals(MainWindowHandler())
        #Das Fenster zuweisen (Hier hat man Zugriff auf alle Funktionen des Hauptfensters)
        self.window = self.builder.get_object("MainWindow")         
        #Das Image zuweisen (Noetig, damit man das den Bildbereich bearbeiten kann)
        self.image = self.builder.get_object("FanArtImage")
        #Treeview zuweisen (Noetig, damit man im Treeview rumarbeiten kann
        self.TreeView = self.builder.get_object("MovieTreeView")        
        self.textviewGenre = self.builder.get_object("genreTextView")        
        self.moviePopup = self.builder.get_object("moviePopUp")
        self.delDlg = self.builder.get_object("delDlg")
        #Loeschdialog ans Fenster anhaengen
        self.delDlg.set_transient_for(self.window)
        self.genreBuffer = self.textviewGenre.get_buffer()
        
        
        
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
        #todo movieListStore benötigt Filmobjekte. Diese sollen normal aus der Datenbank geladen werden. Entweder man 
        #nimmt eine Objektliste, lädt dort alle Filme hinein und nutzt dann eine schleife mit movieListStore.append
        #oder man lädt die Filme direkt in einen Liststore (der Liststore ist nötig, weil er das Model des Treeviews wird
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

        #setzen des Models
        self.TreeView.set_model(movieListStore)   

        #Hauptfenster anzeigen
        show_window(self) # this shows the 'window1' object
        
#Genre Editieren Fenster
class EditGenreWindow:
    #Funktion damit um die erste Spalte zu Umschaltbaren Elemnte zu machen    
    def on_cell_toggled(self, widget, path):
        self.liststore[path][0] = not self.liststore[path][0]   
        
    #Initialisieren    
    def __init__(self, genreList, callWindow):
        #Gtk.Builder zuweisen
        self.builder = Gtk.Builder()        
        #Glade File dem Builder zuweisen
        self.builder.add_from_file('EditGenreWindow.glade')
        #Eventhandler zuweisen
        self.builder.connect_signals(EditGenreWindowHandler())
        #von welchem Fenster wurde EditGenreWindow aufgerufen?
        self.callWindow = callWindow
        #Liststore mit allen Möglichen Genres befüllen, hier mit Beispielen
        #todo: hier muss die Genreliste geladen werden. Anschließend wird der Liststore mit [false,genre] befüllt
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
                    
        #Das Fenster zuweisen 
        self.window = self.builder.get_object("GenreWindow") 
        #Fenster Modal setzen
        self.window.set_modal(True)
        #Das Image zuweisen (Noetig, damit man das den Bildbereich bearbeiten kann)
        self.image = self.builder.get_object("FanArtImage")
        #Treeview zuweisen (Noetig, damit man im Treeview rumarbeiten kann
        self.TreeView = self.builder.get_object("GenreTree")
    
        
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
        show_window(self)
        
class EditMovieWindow:        
    #Film bearbeiten Fenster initialisieren
    def __init__(self, movie=Movie()):
        #
        self.builder = Gtk.Builder()
        self.builder.add_from_file('EditMovieWindow.glade')
        #Das Fenster zuweisen (Hier hat man Zugriff auf alle Funktionen des Hauptfensters)
        self.window = self.builder.get_object("EditMovieWindow") 
        self.window.set_modal(True)
        show_window(self)
        self.builder.connect_signals(EditMovieWindowHandler())
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
        
        
        
class ImportMovieWindow:        
    #Film bearbeiten Fenster initialisieren
    def __init__(self):
        #
        self.builder = Gtk.Builder()
        self.builder.add_from_file('ImportMovieWindow.glade')
        self.builder.connect_signals(ImportMovieWindowHandler())
        
        #Das Fenster zuweisen (Hier hat man Zugriff auf alle Funktionen des Hauptfensters)
        self.window = self.builder.get_object("ImportMovieWindow") 
        self.window.set_modal(True)
        self.movie = Movie()
        
        #Das Image zuweisen (Noetig, damit man das den Bildbereich bearbeiten kann)
        self.image = self.builder.get_object("FanArtImage")
        self.movieFileChooser = self.builder.get_object("MovieFileChooser") 
        self.fanartFileChooser = self.builder.get_object("FanartFileChooser")
        self.movieName = self.builder.get_object("MovieText")        
        self.genreText = self.builder.get_object("GenreText")
        
        
        self.movieListStore = Gtk.ListStore(Film)
        self.TreeView = self.builder.get_object("MovieTreeView")  
        #Spalte fuer die Filme erzeugen    
        cellrenderer = Gtk.CellRendererText()
        treeviewcolumn = Gtk.TreeViewColumn('Zu importierende Filme')        
        #Setzen des anzeigetextes und Objektes
        treeviewcolumn.set_cell_data_func(cellrenderer, set_treeview_cell_txt_colone)
        
        #CellRenderer zur Spalte, und Spalte zum TreeView hinzufgen
        treeviewcolumn.pack_start(cellrenderer, True)
        self.TreeView.append_column(treeviewcolumn)
        
        Film1 = Movie('Logan','K:/downloads/Filme/Logan/Logan.mkv','K:/downloads/Filme/Logan/Logan-fanart.jpg')
        Film1.genreList.append(Genre('Action'))
        Film1.genreList.append(Genre('Drama'))
        Film1.genreList.append(Genre('Sci-Fi'))

        Film2 = Movie('xXx','K:/downloads/Filme/xXx III/xXx III.mkv','K:/downloads/Filme/xXx III/xXx III-fanart.jpg')
        Film2.genreList.append(Genre('Action'))
        Film2.genreList.append(Genre('Adventure'))
        Film2.genreList.append(Genre('Thriller'))
        
        Film3 = Movie('','','')
        Film3.genreList.append(Genre('Action'))
        Film3.genreList.append(Genre('Adventure'))
        Film3.genreList.append(Genre('Sci-Fi'))
        
        #todo frische änderung
        db = DbUtils()
        db.create_database()

        #movieListStore.append((Film1,))
        #movieListStore.append((Film2,))
        #movieListStore.append((Film3,))        
        
        #setzen des Models
        self.TreeView.set_model(self.movieListStore)   
        
        show_window(self)

        
        
        
        


       
        
if __name__ == "__main__":
    main = MainWindow() # create an instance of our class
    Gtk.main() # run the darn thing
