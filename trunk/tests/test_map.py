import sys
import os
sys.path.append(
    os.path.pardir+os.path.sep+'lost'+os.path.sep+'extras'+os.path.sep+'data'+
    os.path.sep+'python')

import unittest
import map as maps
import yamf

class TestMapEngine(unittest.TestCase):

    def setUp(self):
        self.mapDownloaderMock = yamf.Mock()
        maps.MapDownloader = self.mapDownloaderMock
        self.engine = maps.MapEngine(yamf.Mock(), yamf.Mock().callback)

    def testMapProviderSet(self):
        self.mapDownloaderMock.resetLoadQueue.mustBeCalled

        self.engine.setMapProvider(yamf.Mock())

        self.mapDownloaderMock.verify()

    def testSettingSameMapProvider(self):
        self.mapDownloaderMock.resetLoadQueue.mustBeCalled.once

        providerMock = yamf.Mock()

        self.engine.setMapProvider(providerMock)
        self.engine.setMapProvider(providerMock)

        self.mapDownloaderMock.verify()

class TestMapDowloader(unittest.TestCase):

    def setUp(self):
        self.workerMock = yamf.Mock()
        maps.Worker = self.workerMock
        self.loader = maps.MapDownloader(yamf.Mock(), yamf.Mock(), yamf.Mock())

    def testResettingUrlsWhenNoUrlsOnQueue(self):
        self.loader.resetLoadQueue()

    def testWorkerUsedForThreading(self):
        self.workerMock.setJob.mustBeCalled

        self.loader.add('url')
        self.workerMock.verify()

class TestDownloading(unittest.TestCase):
        
    def setUp(self):
        self.imageMock = yamf.Mock()
        import graphics
        graphics.Image.open = self.imageMock.open
        self.workerMock = yamf.Mock()
        maps.Worker = self.workerMock
        self.loader = maps.MapDownloader(yamf.Mock(), yamf.Mock(), yamf.Mock())

    def testDownloading(self):
        self.imageMock.open.mustBeCalled
        
        self.loader.add('testurl')
        self.loader.loadMapPiece()
        self.imageMock.verify()

    def testResettingLoadQueueWithOneItem(self):
        self.workerMock.setJob.mustBeCalled

        self.loader.add('testurl')
        self.loader.resetLoadQueue()
        self.loader.loadMapPiece()
        self.loader.mapPieceLoaded()

    def testResettingLoadQueueWithManyItems(self):
        self.workerMock.setJob.mustBeCalled.times(2)

        self.loader.add('testurl')
        self.loader.add('testurl2')
        self.loader.resetLoadQueue()
        self.loader.loadMapPiece()
        self.loader.mapPieceLoaded()
        self.workerMock.verify()


       
            
    

if __name__ == '__main__':
    unittest.main()
