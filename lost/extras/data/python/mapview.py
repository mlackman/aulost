import appuifw
import key_codes
import graphics
import time

class LocationDlg(object):
    
    def __init__(self):
        fields = [(u'Name', 'text'), (u'Date', 'date', time.time())]
        self._form = appuifw.Form(fields)
        self._form.save_hook = self._saveHook

    def execute(self):
        self._saved = False
        self._form.execute()
        if self._saved:
            return self._form[0][2], self._form[1][2]

    def _saveHook(self, arg):
        self._saved = True    

class LocationStore(object):
    
    def __init__(self):
        self._store = 'locations.txt'
        f = open(self._store,'a') # create the file
        f.close()
        
    def add(self, locationInfo):
        f = open(self._store, 'a')
        txt, date, position = locationInfo
        lat,lon = position
        s = '%s,%f,%f,%f\n' % (txt, date, lat,lon)
        f.write(s)
        f.close()
        
    def items(self):
        f = open(self._store, 'rt')
        lines = f.readlines()
        f.close()

        infos = []
        for line in lines:
            txt,date,lat,lon = line.split(',')
            infos.append((txt,float(date),(float(lat),float(lon))))
        return infos

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
    
    def __init__(self, mapEngine, exitCallback):
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
        dlg = LocationDlg()
        values = dlg.execute()
        if values:
            text, date = values
            store = LocationStore()
            lat,lon = self._engine.currentPosition
            store.add((text,date,self._engine.currentPosition))

    def _viewLocations(self):
        store = LocationStore()
        infos = store.items()
        infoTxts = map(lambda info: unicode(info[0]), infos)
        appuifw.selection_list(infoTxts)

    def _goto(self):
        self._engine.gotoLocation((65.794404,24.88808)) 

