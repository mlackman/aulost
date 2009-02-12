from math import pi, sin, log
import google

class MapPiece(object):
    
    def __init__(self, col, row, zoom):
        self.url = 'http://mt.google.com/mt?x=%d&y=%d&zoom=%d' % (col, row, 17-zoom)
        self.image = None
        self.size = (256,256)
        self.x = (col - long(col)) * google.TILE_SIZE
        self.y = (row - long(row)) * google.TILE_SIZE

class Map(object):

    def __init__(self, centerLocation, size, zoomLevel):
        self.mapPieces = []
        latitude,longitude = centerLocation
        col,row,zoom,tiles = google.locationCoord(latitude,longitude, zoomLevel)
        width, height = size
        x = width/2 - ((col - long(col)) * google.TILE_SIZE)
        y = height/2 - ((row - long(row)) * google.TILE_SIZE)
        nmbrOfColumns = width / google.TILE_SIZE + 1
        nmbrOfRows = height / google.TILE_SIZE + 1

        startCol = col - nmbrOfColumns/2
        startRow = row - nmbrOfRows/2
        startY = y - (col-startCol)*google.TILE_SIZE
        startX = x - (row-startRow)*google.TILE_SIZE
        currentY = startY
        for row in range(int(startRow), int(row+nmbrOfRows)):
            currentX = startX
            for column in range(int(startCol), int(col+nmbrOfColumns)):
                mp = MapPiece(column, row, zoom)
                mp.x = -currentX
                mp.y = -currentY
                currentX += google.TILE_SIZE
                self.mapPieces.append(mp)
            currentY += google.TILE_SIZE


class Google(object):
        
    def __init__(self):
        self.zoomLevel = 14

    def getMap(self, centerLocation, size):
        return Map(centerLocation, size, self.zoomLevel)
