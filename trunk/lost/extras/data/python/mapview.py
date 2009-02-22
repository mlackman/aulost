import appuifw
import key_codes
import graphics
import time
import locations

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
            # Clear the area of map piece, which does not have image
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

class MapView(object):
    
    def __init__(self, mapEngine, viewManager, exitCallback):
        self._viewManager = viewManager
        self._engine = mapEngine
        self._layers = [MapLayer(self._engine), CursorLayer(self._engine.gps)]
        appuifw.app.body = appuifw.Canvas(self._redraw,self._keypressed, self._resize)
        appuifw.app.menu = [(u'Size',\
                            ((u'Normal', self._normalSize),
                             (u'Large',  self._largeSize),
                             (u'Full',   self._fullSize))),
                        (u'Zoom in', self._engine.zoomIn),
                        (u'Zoom out', self._engine.zoomOut),
                        (u'Locate', self._engine.gps.start),
                        (u'Goto', self._goto),
                        (u'Store location', self._storeLocation),
                        (u'View locations', self._viewLocations),
                        (u'Exit', exitCallback)]
        appuifw.app.screen = 'normal'
        appuifw.app.body.clear()

    def update(self):
        self._redraw((0,0,0,0))

    def _keypressed(self, keyEvent):
        keycode = keyEvent['keycode']
        if keycode == key_codes.EKeyUpArrow:
            self._engine.moveMap(0, -10)
        elif keycode == key_codes.EKeyDownArrow:
            self._engine.moveMap(0, 10)
        elif keycode == key_codes.EKeyLeftArrow:
            self._engine.moveMap(-10, 0)
        elif keycode == key_codes.EKeyRightArrow:
            self._engine.moveMap(10, 0)

    def _resize(self, event):
        self._engine.update()

    def _redraw(self, area):
        if not hasattr(appuifw.app.body,'size'):
            return
        map(lambda layer: layer.update(), self._layers)

    def _normalSize(self):
        appuifw.app.screen='normal'
        
    def _largeSize(self):
        appuifw.app.screen='large'
        
    def _fullSize(self):
        appuifw.app.screen='full'

    def _storeLocation(self):
        dlg = locations.SaveLocationDlg(locations.LocationStore())
        values = dlg.execute(self._engine.currentPosition)           

    def _viewLocations(self):
        self._engine.gps.stop()
        self._viewManager.changeView('LocationsView')

    def _goto(self):
        self._engine.gotoLocation((65.794404,24.88808)) 

