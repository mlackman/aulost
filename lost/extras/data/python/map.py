import positioning 
import threading
import google_provider
import e32
import appuifw
import urllib
import graphics
import socket

apo = 0 # access point

class Images(object):
    
    def __init__(self):
        self.s = threading.Semaphore()
        self.images = {}
        
    def add(self, url, image):
        self.s.acquire()
        self.images[url] = image
        self.s.release()

    def remove(self, url):
        self.s.acquire()
        if url in self.images:  
            self.images[url] = None
        self.s.release()

    def get(self, url):
        self.s.acquire()
        image = None
        if url in self.images:
            image = self.images[url]
        self.s.release()
        return image

class Worker(object):
        
    def __init__(self, callback):
        self.event = threading.Event()
        self.job = None
        self.thread = threading.Thread(target=self.run)
        self.running = True
        self.thread.start()
        self.callback = callback

    def setJob(self, job):
        if not self.job:
            self.job = job
            self.event.set()

    def stop(self):
        self.running = False
        self.event.set()
        self.thread.join()

    def run(self):
        socket.set_default_access_point(apo)
        while self.running:
            if self.job:
                self.job()
                self.job = None
                self.callback()
            else:
                self.event.wait()
                self.event.clear()

class MapDownloader(object):

    def __init__(self, images, mapLoadedCallback):
        self.mapLoadedCallback = mapLoadedCallback
        self.worker = Worker(self.mapPieceLoaded)
        self.urls = []
        self.images = images

    def add(self, url):
        """Starts loading map pieces which image is none. 
           MapLoadedCallback is called, when one of the map pieces has been loaded."""
        if self.urls.count(url) == 0:
            self.urls.append(url)
            self.worker.setJob(self.loadMapPiece)       

    def cancelLoading(self):
        self.worker.stop()         
            
    def loadMapPiece(self):
        """Loads map piece in different thread"""
        url = self.urls[0]
        filename = url[len(r'http://'):].replace('/','(').replace('.','!').replace('?','#').replace(':','_')
        try:    
            image = graphics.Image.open(filename)
        except:
            f = urllib.urlopen(url)
            data = f.read()
            f.close()
            f = open(filename, 'wb')
            f.write(data)
            f.close()
            image = graphics.Image.open(filename)
        self.images.add(url, image)
        self.urls.pop(0)
        
            
    def mapPieceLoaded(self):
        """Callback from worker. 
           Loads next map piece if there are still something to load"""
        if self.urls:
            self.worker.setJob(self.loadMapPiece)  
        self.mapLoadedCallback()

class GPS(object):

    def __init__(self, callback):
        self._callback = callback
        self.seekingSatellites = False
        self.active = False

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
        self._callback(event)

class MapEngine(object):
        
    def __init__(self, mapInformationChagedCallback):
        self.currentPosition = (65.681264, 24.755917)
        self._provider = google_provider.Google()
        self.map = None
        self._mapCache = Images()
        self._mapInformationChagedCallback = mapInformationChagedCallback
        self._loader = MapDownloader(self._mapCache, e32.ao_callgate(self._imageLoaded))
        self.gps = GPS(self._positionChanged)

    def update(self):
        self._updateMap()

    def start(self):
        self._updateMap()

    def close(self):
        self.gps.stop()
        self._loader.cancelLoading()

    def gotoLocation(self, position):
        self.gps.stop()
        self.currentPosition = position
        self._updateMap()

    def _imageLoaded(self):
        self._updateImages()
        self._mapInformationChagedCallback()

    def _updateImages(self):
        for m in self.map.mapPieces:
            if not m.image:
                m.image = self._mapCache.get(m.url)

    def _positionChanged(self, event):
        """Callback from gps"""
        pos = event['position']
        lat = pos['latitude']
        lon = pos['longitude']
        self.currentPosition = (lat,lon)
        self._updateMap()

    def _updateMap(self):
        newMap = self._provider.getMap(self.currentPosition, appuifw.app.body.size)
        if self.map:
            for oldMapPiece in self.map.mapPieces:
                for newMapPiece in newMap.mapPieces:
                    if oldMapPiece.url == newMapPiece.url:
                        newMapPiece.image = oldMapPiece.image
                        break
        self.map = newMap
        for map in self.map.mapPieces:
            if not map.image:
                cachedImage = self._mapCache.get(map.url)
                if cachedImage:
                    map.image = cachedImage
                else:
                    self._loader.add(map.url)
        self._mapInformationChagedCallback()
