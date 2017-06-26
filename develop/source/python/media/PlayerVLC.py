import sys
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('GdkX11', '3.0')
from gi.repository import GdkX11

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from gettext import gettext as _

import ctypes

import vlc

class PlayerVLC(Gtk.Window):
    def __init__(self, myMedia = None):
        Gtk.Window.__init__(self, title="Vlc Media Player with Python")
        self._player_paused = False
        self._is_player_active = False
        self.connect("destroy", self.on_video_close)
        self._media = myMedia
        self._stopped = False

    def on_video_close(self, widget):
            self.stop_player(widget)
            widget.destroy()

    def show(self):
        self.show_all()

    def setup_objects_and_events(self):
        self.playback_button = Gtk.Button(label='Play')
        self.stop_button = Gtk.Button(label='Cancel')

        self.playback_button.connect("clicked", self.toggle_player_playback)
        self.stop_button.connect("clicked", self.stop_player)

        self.draw_area = Gtk.DrawingArea()
        self.draw_area.set_size_request(300, 300)

        self.draw_area.connect("realize", self._realized)

        self.hbox = Gtk.Box(spacing=6)
        self.hbox.pack_start(self.playback_button, True, True, 0)
        self.hbox.pack_start(self.stop_button, True, True, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)
        self.vbox.pack_start(self.draw_area, True, True, 0)
        self.vbox.pack_start(self.hbox, False, False, 0)

    def stop_player(self, widget, data=None):
        self.player.stop()
        self._stopped = True
        self._is_player_active = False
        self.playback_button.set_label('Replay')
        self.stop_button.connect("clicked", Gtk.main_quit)


    def toggle_player_playback(self, widget, data=None):

        """
        Handler für Schnittstelle zum Player VLC
        Buttons anzeigen als aktiv oder deaktiviert
        """

        if self._is_player_active == False and self._player_paused == False:
            self.player.play()
            self.playback_button.set_label('Play')
            self._is_player_active = True
            self.stop_button.connect("clicked", self.stop_player)

        elif self._is_player_active == True and self._player_paused == True:
            self.player.play()
            self.playback_button.set_label('Stop')
            self._player_paused = False
            self.stop_button.connect("clicked", self.stop_player)

        elif self._is_player_active == True and self._player_paused == False:
            self.player.pause()
            self.playback_button.set_label('Cont')
            self._player_paused = True
            self.stop_button.connect("clicked", self.stop_player)

        elif self._stopped == True:
            self.player.replay()
            self.playback_button.set_label('Stop')
            self._stopped = False
            self._player_paused = False
            self.stop_button.connect("clicked", self.stop_player)

        else:
            pass

    def _realized(self, widget, data=None):
        if 'linux' in sys.platform:
            # Inform libvlc that Xlib is not initialized for threads
            self.instance = vlc.Instance("--no-xlib")
        else:
            self.instance = vlc.Instance()

        self.player = self.instance.media_player_new()

        if 'linux' in sys.platform:
            win_id = widget.get_window().get_xid()
            self.player.set_xwindow(win_id)
        else:
            video_window = self.draw_area.get_property('window')
            ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
            ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object]
            drawingarea_gpointer = ctypes.pythonapi.PyCapsule_GetPointer(video_window.__gpointer__, None)
            # get the win32 handle
            gdkdll = ctypes.CDLL("libgdk-3-0.dll")
            window_handle = gdkdll.gdk_win32_window_get_handle(drawingarea_gpointer)
            self.player.set_hwnd(window_handle)

        self.player.set_mrl(self._media)
        self.player.play()
        self._is_player_active = True

