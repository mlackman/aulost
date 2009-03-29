import socket
import map as maps
import e32
import appuifw
import mapview
import locations
import track
import gps

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
        self._selectAccessPoint()
        self.engine = maps.MapEngine(gps.GPS(), self._downloadException)

        mapView = mapview.MapView(self.engine, maps.MapProviders(), self, self._exitApp)
        locationView = locations.LocationsView(locations.LocationStore(), self, self.engine)
        trackView = track.TrackView(track.TrackStore(), self, self.engine)
        self._views = {'MapView':mapView, 'LocationsView':locationView, \
                       'TrackView':trackView}
        self.engine.setCallback(mapView.update)
        self.changeView('MapView')

        mapView.selectMapProvider()
        
        self.__mainloop = mainloop = MainLoop()
        appuifw.app.exit_key_handler = self._exitApp           

    def start(self):
        self.engine.start()
        self.__mainloop.start()

    def changeView(self, viewName):
        self._views[viewName].activate()

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
        
        

