import socket
import map as maps
import e32
import appuifw
import graphics
import key_codes

class MainLoop(object):
    
    def __init__(self):
        self._lock = e32.Ao_lock()
        
    def start(self):
        self._lock.wait()
            
    def stop(self):
        self._lock.signal()

class MapLayer(object):
        
    def __init__(self, engine):
        self._engine = engine

    def update(self):
        if self._engine.map:
            map(self._drawMapPiece, self._engine.map.mapPieces)

    def _drawMapPiece(self, mapPiece):
        image = mapPiece.image
        if image:        
            appuifw.app.body.blit(image, (-mapPiece.x,-mapPiece.y))
        else:
            width,height = mapPiece.size
            area = (mapPiece.x, mapPiece.y, mapPiece.x+width, mapPiece.y+height)
            white = (255,255,255)
            appuifw.app.body.rectangle(area, white,fill=white)

class CursorLayer(object):
    
    def __init__(self, gps):
        self._gps = gps

    def update(self):
        width,height = appuifw.app.body.size
        centerX = width / 2
        centerY = height / 2
        lineWidth = 1
        if self._gps.active:
            lineWidth = 2
        appuifw.app.body.rectangle((centerX-15,centerY-15,centerX+15,centerY+15),(0,0,0), width=lineWidth)
        appuifw.app.body.line((centerX - 50, centerY, centerX + 50, centerY),(0,0,0),width=lineWidth)
        appuifw.app.body.line((centerX, centerY-50, centerX, centerY+50),(0,0,0),width=lineWidth)

class LostApp:
    def __init__(self):
        apid = socket.select_access_point()  #Prompts you to select the access point
        if apid:
            apo = socket.access_point(apid)      #apo is the access point you selected     
            maps.apo = apo
        else:
            maps.apo = None
        self.engine = maps.MapEngine(self.__update)
        providers = map(lambda name: unicode(name), self.engine.providers())
        selection = appuifw.selection_list(providers)
        if selection is not None:
            self.engine.setProvider(providers[selection])
        
        self._layers = [MapLayer(self.engine), CursorLayer(self.engine.gps)]
        
        appuifw.app.title = u'Lost'
        appuifw.app.body = appuifw.Canvas(self.__redraw,self._keypressed, self.resize)
        appuifw.app.menu = [(u'Size',\
                            ((u'Normal', self._normalSize),
                             (u'Large',  self._largeSize),
                             (u'Full',   self._fullSize))),
                        (u'Zoom in', self.engine.zoomIn),
                        (u'Zoom out', self.engine.zoomOut),
                        (u'Locate', self.engine.gps.start),
                        (u'Goto', self._goto),
                        (u'Exit', self.exitApp)]
        appuifw.app.screen = 'normal'
        appuifw.app.body.clear()

        self.__mainloop = mainloop = MainLoop()
        appuifw.app.exit_key_handler = self.exitApp
        

    def _goto(self):
        self.engine.gotoLocation((65.794404,24.88808))      

    def start(self):
        self.engine.start()
        self.__mainloop.start()

    def exitApp(self):
        self.engine.close()
        self.__mainloop.stop()

    def _keypressed(self, keyEvent):
        keycode = keyEvent['keycode']
        if keycode == key_codes.EKeyUpArrow:
            self.engine.moveMap(0, -10)
        elif keycode == key_codes.EKeyDownArrow:
            self.engine.moveMap(0, 10)
        elif keycode == key_codes.EKeyLeftArrow:
            self.engine.moveMap(-10, 0)
        elif keycode == key_codes.EKeyRightArrow:
            self.engine.moveMap(10, 0)

    def resize(self, event):
        self.engine.update()
        
    def __redraw(self, area):
        if not hasattr(appuifw.app.body,'size'):
            return
        map(lambda layer: layer.update(), self._layers)
        """if self.engine.map:
            for m in self.engine.map.mapPieces:
                if m.image:        
                    appuifw.app.body.blit(m.image, (-m.x,-m.y))
                else:
                    width,height = m.size
                    appuifw.app.body.rectangle((m.x, m.y, m.x+width, m.y+height), (255,255,255),fill=(255,255,255))"""

        """width,height = appuifw.app.body.size
        centerX = width / 2
        centerY = height / 2
        lineWidth = 1
        if self.engine.gps.active:
            lineWidth = 2
        appuifw.app.body.rectangle((centerX-15,centerY-15,centerX+15,centerY+15),(0,0,0), width=lineWidth)
        appuifw.app.body.line((centerX - 50, centerY, centerX + 50, centerY),(0,0,0),width=lineWidth)
        appuifw.app.body.line((centerX, centerY-50, centerX, centerY+50),(0,0,0),width=lineWidth)"""
        
    def __update(self):
        self.__redraw((0,0,0,0))
        
    def _normalSize(self):
        appuifw.app.screen='normal'
        
    def _largeSize(self):
        appuifw.app.screen='large'
        
    def _fullSize(self):
        appuifw.app.screen='full'

