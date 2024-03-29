import appuifw
import key_codes
import graphics
import time
import locations
import math
import track
import view

KeyboardAmountOfMapMovement = 10

def rotatePoint(point, rad):
    x,y = point
    newX = x * math.cos(rad) - y * math.sin(rad)
    newY = y * math.cos(rad) + x * math.sin(rad)
    return newX,newY

def translatePoint(point, pos):
    x,y = point
    centerX,centerY = pos
    return centerX+x, centerY - y
    
class MapMover(object):
    """Moves map from different inputs"""
    
    def __init__(self, mapEngine):
        self._mapEngine = mapEngine
        self._lastPointerPos = None
        
    def canvasEventCallback(self, event):
        """Calback from appuifw.Canvas event. Moves the map according to the event"""
        if event.has_key('keycode'):
            self._keyboardEvent(event)
        else:
            self._pointerEvent(event)
            
    def _keyboardEvent(self, event):
        keyCode = event['keycode']
        if keyCode == key_codes.EKeyUpArrow:
            self._mapEngine.moveMap(0,-KeyboardAmountOfMapMovement)
        elif keyCode == key_codes.EKeyDownArrow:
            self._mapEngine.moveMap(0,KeyboardAmountOfMapMovement)
        elif keyCode == key_codes.EKeyLeftArrow:
            self._mapEngine.moveMap(-KeyboardAmountOfMapMovement,0)
        elif keyCode == key_codes.EKeyRightArrow:
            self._mapEngine.moveMap(KeyboardAmountOfMapMovement,0)
            
    def _pointerEvent(self, event):
        pointerEvent = event['type']
        if pointerEvent == key_codes.EButton1Down:
            self._lastPointerPos = event['pos']
        elif pointerEvent == key_codes.EDrag:
            lastPointerX,lastPointerY = self._lastPointerPos
            x,y = event['pos']
            self._mapEngine.moveMap(lastPointerX - x, lastPointerY - y)
            self._lastPointerPos = (x,y)
        elif pointerEvent == key_codes.EButton1Up:
            self._lastPoitnerPos = None
                
        
        
    

class Layer(object):
    """Layer, which are drawn top of each other"""
    
    def __init__(self):   
        self.canvas = None

class MapLayer(Layer):
    """Shows the map"""
        
    def __init__(self, engine):
        Layer.__init__(self)
        self._engine = engine

    def update(self):
        if self._engine.map:
            map(self._drawMapPiece, self._engine.map.mapPieces)

    def _drawMapPiece(self, mapPiece):
        image = mapPiece.image
        if image:        
            self.canvas.blit(image, (-mapPiece.x,-mapPiece.y))
        else:   
            # Clear the area of map piece, which does not have image
            width,height = mapPiece.size
            area = (mapPiece.x, mapPiece.y, mapPiece.x+width, mapPiece.y+height)
            white = (255,255,255)
            self.canvas.rectangle(area, white,fill=white)

class HeadingArrow(object):
    """Shows heading arrow in cursor"""
    
    def __init__(self):
        self._points = [(5.0,0.0),(-5.0,5.0),(-5,-5.0)]
        self.pos = (0.0,0.0)
        self.angle = 0
        

    def draw(self, canvas):
        rad = math.radians(self.angle)
        newPoints = map(lambda point: rotatePoint(point,rad), self._points)
        newPoints = map(lambda point: translatePoint(point, self.pos), newPoints)
        canvas.polygon(newPoints, (0,0,0),fill=(255,0,0),width=2)      

class CursorLayer(Layer):
    """Shows the crosshair"""
    
    def __init__(self, gps):
        Layer.__init__(self)
        self._gps = gps

    def update(self):
        canvas = self.canvas
        width,height = canvas.size
        centerX = width / 2
        centerY = height / 2
        lineWidth = 2
        canvas.ellipse((centerX-15,centerY-15,centerX+15,centerY+15),(0,0,0), width=lineWidth)
        canvas.line((centerX - 50, centerY, centerX + 50, centerY),(0,0,0),width=lineWidth)
        canvas.line((centerX, centerY-50, centerX, centerY+50),(0,0,0),width=lineWidth)

        if self._gps.active and self._gps.heading:
            x,y = 20.0, 0.0
            angle = 90 - self._gps.heading
            rad = math.radians(angle)
            newX, newY = rotatePoint((x,y), rad)
            arrow = HeadingArrow()
            arrow.angle = angle
            arrow.pos = centerX+newX,centerY-newY
            arrow.draw(canvas)

class InfoLayer(Layer):
    """Shows information"""
    
    def __init__(self, gps):
        Layer.__init__(self)
        self._gps = gps

    def update(self):
        if self._gps.seekingSatellites or self._gps.active:
            self._drawGPS() 

    def _drawGPS(self):
        canvas = self.canvas
        boundingBox, movement, nmbrOfChars =\
            canvas.measure_text(u'GPS',font='normal')
        x,y,x1,y1 = boundingBox
        width,height = canvas.size
        pos = (width-x1-5, -y+5)
        canvas.text(pos, u'GPS', font='normal')
        if self._gps.active:
            x,y = pos
            canvas.rectangle((x-2,2,width-2,y+2),(0,0,0),width=2)

class TrackLayer(Layer):
    """Shows track"""
    
    def __init__(self, engine):
        Layer.__init__(self)
        self._engine = engine
    
    def update(self):
        if self._engine.map:
            self._drawTrack()

    def _drawTrack(self):
        track = self._engine.track
        mapPiece = self._engine.map
        coordinates = map(lambda location: mapPiece.toScreenCoordinates(location), track)
        if len(coordinates) > 1:
            self.canvas.line(coordinates,(255,0,0),width=2)

class MapView(view.View):
    """View to show map and related information"""
    
    def __init__(self, mapEngine, mapProviders, viewManager, exitCallback):
        view.View.__init__(self, 'MapView', viewManager)
        self._mapProviders = mapProviders
        self._engine = mapEngine
        self._layers = [MapLayer(self._engine), CursorLayer(self._engine.gps),\
                        InfoLayer(self._engine.gps), TrackLayer(self._engine)]
        self._exitCallback = exitCallback
        self._offscreen = None
        self._mapMover = MapMover(mapEngine)
        self.lastPoint = None
        

    def activate(self):
        appuifw.app.body = appuifw.Canvas(self._redraw,self._mapMover.canvasEventCallback, self._resize)
        if not self._offscreen:
            self._offscreen = graphics.Image.new(appuifw.app.body.size)
        for layer in self._layers:
            layer.canvas = self._offscreen
        appuifw.app.menu = [(u'Size',
                                 ((u'Normal', self._normalSize),
                                 (u'Large',  self._largeSize),
                                 (u'Full',   self._fullSize))),
                            (u'Map',
                                 ((u'Zoom in', self._engine.zoomIn),
                                 (u'Zoom out', self._engine.zoomOut),
                                 (u'Change provider...', self.selectMapProvider))),
                            (u'GPS',
                                 ((u'Start', self._startGPS),
                                 (u'Stop', self._stopGPS))),
                            (u'Locations',
                                 ((u'Store location', self._storeLocation),
                                 (u'View locations', self._viewLocations))),
                            (u'Tracks',
                                 ((u'Store track', self._storeTrack),
                                 (u'View tracks', self._viewTracks))),
                            (u'Goto', self._goto),
                            (u'Exit', self._exitCallback)]
        appuifw.app.screen = 'normal'
        appuifw.app.body.clear()
        self.update()

    def update(self):
        self._redraw((0,0,0,0))

    def selectMapProvider(self):
        providerNames = map(lambda name: unicode(name), self._mapProviders.providers())
        selection = appuifw.selection_list(providerNames)
        if selection is not None:
            self._mapProviders.setProvider(providerNames[selection])
            self._engine.setMapProvider(self._mapProviders.provider)
            self._engine.update()
            self.update()

    def _resize(self, event):
        if type(appuifw.app.body) is appuifw.Canvas:
            self._offscreen = graphics.Image.new(appuifw.app.body.size)
            for layer in self._layers:
                layer.canvas = self._offscreen
            self._engine.update()

    def _redraw(self, area):
        if not hasattr(appuifw.app.body,'blit'):
            return
        map(lambda layer: layer.update(), self._layers)
        appuifw.app.body.blit(self._offscreen)
        
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
        self.view_manager.change_view('LocationsView')

    def _storeTrack(self):
        if self._engine.track:
            dlg = track.SaveTrackDlg(track.TrackStore())
            # Take the copy of the array because GPS is adding new location
            # points when dialog is executing. Otherwise the saving the locations
            # fails.
            trackPoints = []
            trackPoints.extend(self._engine.track)
            dlg.execute(trackPoints)
        else:
            appuifw.note(u'No track', 'info')

    def _viewTracks(self):
        self._engine.gps.stop()
        self.view_manager.change_view('TrackView')

    def _goto(self):
        self._engine.gotoLocation((65.794404,24.88808)) 

    def _startGPS(self):
        if self._engine.gps.seekingSatellites or self._engine.gps.active:
            return
        self._engine.track = []
        self._engine.gps.start()
        self.update()

    def _stopGPS(self):
        self._engine.gps.stop()
        self.update()

