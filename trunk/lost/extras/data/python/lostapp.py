import socket
import map as maps
import e32
import appuifw
import mapview


class MainLoop(object):
    
    def __init__(self):
        self._lock = e32.Ao_lock()
        
    def start(self):
        self._lock.wait()
            
    def stop(self):
        self._lock.signal()

class LostApp:
    def __init__(self):
        apid = socket.select_access_point()  #Prompts you to select the access point
        if apid:
            apo = socket.access_point(apid)      #apo is the access point you selected     
            maps.apo = apo
        else:
            maps.apo = None
        self.engine = maps.MapEngine()
        mapView = mapview.MapView(self.engine, self._exitApp)
        self.engine.setCallback(mapView.update)
        providers = map(lambda name: unicode(name), self.engine.providers())
        selection = appuifw.selection_list(providers)
        if selection is not None:
            self.engine.setProvider(providers[selection])
        
        appuifw.app.title = u'Lost'

        self.__mainloop = mainloop = MainLoop()
        appuifw.app.exit_key_handler = self._exitApp           

    def start(self):
        self.engine.start()
        self.__mainloop.start()

    def _exitApp(self):
        self.engine.close()
        self.__mainloop.stop()
        
        

