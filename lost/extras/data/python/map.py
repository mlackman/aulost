import threading
import e32
import appuifw
import urllib
import graphics
import socket
import utils
import gps

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
        while self.running:
            if self.job:
                self.job()
                self.job = None
                self.callback()
            else:
                self.event.wait()
                self.event.clear()

class MapDownloader(object):

    def __init__(self, images, mapLoadedCallback, downloadExceptionCallback):
        self._downloadExceptionCallback = downloadExceptionCallback
        self.mapLoadedCallback = mapLoadedCallback
        self.worker = Worker(self.mapPieceLoaded)
        self.urls = []
        self.images = images
        self._accessPointChanged = True

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
        image = None
        try:    
            image = graphics.Image.open(filename)
        except:
            global apo
            if apo:
                if self._accessPointChanged:
                    socket.set_default_access_point(apo)
                    self._accessPointChanged = False
                try:
                    f = urllib.urlretrieve(url,filename)
                    image = graphics.Image.open(filename)
                except:
                    self._downloadExceptionCallback()
                    apo = None       
                    self._accessPointChanged = True

        if image:
            self.images.add(url, image)
        self.urls.pop(0)
        
            
    def mapPieceLoaded(self):
        """Callback from worker. 
           Loads next map piece if there are still something to load"""
        if self.urls:
            self.worker.setJob(self.loadMapPiece)  
        self.mapLoadedCallback()   

class MapProviders(object):
    
    def __init__(self):
        self.provider = None
        self._providers = {}
        files = utils.findFilesEndsWith('_provider.py', 'c:\\data\\python')
        for file in files:
            providerModule = __import__(file[:-3])
            provider = providerModule.provider()
            self._providers[provider.name] = provider

    def providers(self):
        return self._providers.keys()

    def setProvider(self, providerName):
        self.provider = self._providers[providerName]

class MapEngine(object):
        
    def __init__(self, gps, downloadExceptionCallback):
        self.gps = gps
        self._provider = None
        gps.addObserver(self._positionChanged)
        self.currentPosition = (65.681264, 24.755917)
        self.track = []
        self.map = None
        self._mapCache = Images()
        self._loader = MapDownloader(\
            self._mapCache, e32.ao_callgate(self._imageLoaded), \
            e32.ao_callgate(downloadExceptionCallback))

    def setMapProvider(self, provider):
        self._provider = provider

    def setCallback(self, callback):
        self._mapInformationChagedCallback = callback

    def update(self):
        self._updateMap()

    def start(self):
        self._updateMap()

    def close(self):
        self.gps.stop()
        self._loader.cancelLoading()

    def moveMap(self, dx, dy):
        self.gps.stop()
        if self.map:
            # TODO: This move should be getPosition...
            self.map.move(dx,dy) 
            self.currentPosition = self.map.center
            self._updateMap()

    def zoomIn(self):
        if self._provider:
            self._provider.zoomIn()
            self._updateMap()

    def zoomOut(self):
        if self._provider:
            self._provider.zoomOut()
            self._updateMap()

    def gotoLocation(self, position):
        self.gps.stop()
        self.currentPosition = position
        self._updateMap()

    def toScreenCoordinates(self, position):
        if self.map:
            return self.map.toScreenCoordinates(position)
        else:
            return (0,0)

    def _imageLoaded(self):
        self._updateImages()
        self._mapInformationChagedCallback()

    def _updateImages(self):
        for m in self.map.mapPieces:
            if not m.image:
                m.image = self._mapCache.get(m.url)

    def _positionChanged(self):
        """Callback from gps"""
        e32.reset_inactivity()
        if self.gps.position:
            self.currentPosition = self.gps.position
            self.track.append(self.currentPosition)
            self._updateMap()

    def _updateMap(self):
        if not self._provider or not hasattr(appuifw.app.body,'size'):
            return
        self.map = self._provider.getMap(self.currentPosition, appuifw.app.body.size)
        for map in self.map.mapPieces:
            if not map.image:
                cachedImage = self._mapCache.get(map.url)
                if cachedImage:
                    map.image = cachedImage
                else:
                    self._loader.add(map.url)
        self._mapInformationChagedCallback()
