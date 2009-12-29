import socket
import map as maps
import e32
import appuifw
import mapview
import locations
import track
import gps
import view

class MainLoop(object):
    
    def __init__(self):
        self._lock = e32.Ao_lock()
        
    def start(self):
        self._lock.wait()
            
    def stop(self):
        self._lock.signal()

class LostApp:
    def __init__(self):
        appuifw.app.title = u'Lost'
        appuifw.app.directional_pad = False
        self._selectAccessPoint()
        self.engine = maps.MapEngine(gps.GPS(), self._downloadException)
        vm = view.ViewManager()
        mapView = mapview.MapView(self.engine, maps.MapProviders(), vm, self._exitApp)
        locationView = locations.LocationsView(locations.LocationStore(), vm, self.engine)
        trackView = track.TrackView(track.TrackStore(), vm, self.engine)

        self.engine.setCallback(mapView.update)
        vm.change_view('MapView')

        mapView.selectMapProvider()
        
        self.__mainloop = mainloop = MainLoop()
        appuifw.app.exit_key_handler = self._exitApp           

    def start(self):
        self.engine.start()
        self.__mainloop.start()

    def _exitApp(self):
        self.engine.close()
        self.__mainloop.stop()

    def _downloadException(self):
        result = appuifw.query(u'Current access point could not be used! Select new one?',\
                              'query')
        if result:
            self._selectAccessPoint()
            self.engine.update()

    def _selectAccessPoint(self):
        apid = socket.select_access_point()  #Prompts you to select the access point
        if apid:
            apo = socket.access_point(apid)      #apo is the access point you selected     
            maps.apo = apo
        else:
            maps.apo = None
        
        

