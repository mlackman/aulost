import positioning 

class GPS(object):

    def __init__(self):
        self.seekingSatellites = False
        self.active = False
        self.heading = None
        self.position = None
        self._observers = []

    def addObserver(self, observer):
        self._observers.append(observer)

    def start(self):
        self.seekingSatellites = True
        positioning.select_module(positioning.default_module())
        positioning.set_requestors([{"type":"service", "format":"application", "data":"test_app"}])
        positioning.position(course=1,satellites=1, callback=self._dataReceived, interval=1000000, partial=0)

    def stop(self):
        self.active = False
        self.seekingSatellites = False
        positioning.stop_position()
    
    def _dataReceived(self, event):
        self.seekingSatellites = False
        self.active = True
        pos = event['position']
        lat = pos['latitude']
        lon = pos['longitude']
        if str(lat) != 'nan' and str(lon) != 'nan':
            self.position = (lat,lon)

        heading = event['course']['heading']
        if str(heading) != 'nan':
            self.heading = heading
        self._callObservers()
    
    def _callObservers(self):
        for obs in self._observers:
            obs()
