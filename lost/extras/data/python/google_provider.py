from math import pi, sin, log, atan, exp
import google

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php
offset = 268435456
r = offset / pi

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php
def lonToX(lon):
    return offset + r * lon * pi / 180

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php
def latToY(lat):
    return offset - r * log((1 + sin(lat * pi / 180)) / (1 - sin(lat * pi / 180))) / 2

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php
def xToLon(x): 
    return ((x - offset) / r) * 180/ pi

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php    
def yToLat(y):
    return (pi / 2 - 2 * atan(exp((y - offset) / r))) * 180 / pi

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php    
def adjustLonByPixels(lon, delta, zoom):
    return xToLon(lonToX(lon) + (delta << (21 - zoom)))

#Code has been converted from http://svn.appelsiini.net/svn/javascript/trunk/google_maps_nojs/Google/Maps.php
def adjustLatByPixels(lat, delta, zoom):
    return yToLat(latToY(lat) + (delta << (21 - zoom)))


def provider():
    return Google()

class MapPiece(object):
    
    def __init__(self, col, row, zoom):
        self.url = 'http://mt.google.com/vt/v=w2.97&hl=en&x=%d&y=%d&z=%d' % (col, row, zoom)
        self.image = None
        self.size = (256,256)


class Map(object):

    def __init__(self, centerLocation, size, zoomLevel):
        self.mapPieces = []
        self.center = centerLocation
        self.zoom = zoomLevel
        self.size = size
        latitude,longitude = centerLocation
        col,row,zoom,tiles = google.locationCoord(latitude,longitude, zoomLevel)
        width, height = size
        x = width/2 - ((col - long(col)) * google.TILE_SIZE)
        y = height/2 - ((row - long(row)) * google.TILE_SIZE)
        
        # This is a hack to fill the hole screen. The formula should be something
        # which checks if the map tile which contains the centerLocation is not 
        # filling the whole screen ie its drawn to side of the screen.
        nmbrOfColumns = width / google.TILE_SIZE + 2
        nmbrOfRows = height / google.TILE_SIZE + 2

        startCol = col - nmbrOfColumns/2
        lastCol = col+nmbrOfColumns
        if lastCol > tiles:
            lastCol = tiles
        
        startRow = row - nmbrOfRows/2
        lastRow = row + nmbrOfRows
        if lastRow > tiles:
            lastRow = tiles 
        if tiles == 2: 
            lastRow = 1       

        startY = y - (col-startCol)*google.TILE_SIZE
        startX = x - (row-startRow)*google.TILE_SIZE
        currentY = startY
        for row in range(int(startRow), int(lastRow)):
            currentX = startX
            for column in range(int(startCol), int(lastCol)):
                mp = MapPiece(column, row, zoom)
                mp.x = currentX
                mp.y = currentY
                currentX += google.TILE_SIZE    
                self.mapPieces.append(mp)
            currentY += google.TILE_SIZE

    def toScreenCoordinates(self, position):
        scrCenterLat, scrCenterLon = self.center
        scrCenterY = int(latToY(scrCenterLat))
        scrCenterX = int(lonToX(scrCenterLon))
        wantedLat, wantedLon = position
        wantedY = int(latToY(wantedLat))
        wantedX = int(lonToX(wantedLon))
        dx = (wantedX - scrCenterX) >> (21-self.zoom)
        dy = (wantedY - scrCenterY) >> (21-self.zoom)
        width,height = self.size
        return dx+width/2, height/2+dy
        

    def move(self, dx, dy):
        for map in self.mapPieces:
            map.x += dx
            map.y += dy
        lat, lon = self.center
        newLat = adjustLatByPixels(lat, dy, self.zoom)
        newLon = adjustLonByPixels(lon, dx, self.zoom)
        self.center = (newLat,newLon)

class Google(object):
        
    def __init__(self):
        self.zoomLevel = 14
        self.name = 'Google maps'

    def zoomIn(self):
        if self.zoomLevel != 17:
            self.zoomLevel += 1

    def zoomOut(self):
        if self.zoomLevel != 1:
            self.zoomLevel -= 1

    def getMap(self, centerLocation, size):
        return Map(centerLocation, size, self.zoomLevel)

if __name__ == '__main__':
    g = Google()
    m = g.getMap((65.681264, 24.755917), (200,200))
    for map in m.mapPieces:
        print map.url
    print m.toScreenCoordinates((65.681422,24.76917))

