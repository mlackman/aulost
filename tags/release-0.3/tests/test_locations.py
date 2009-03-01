import sys
import os
sys.path.append(
    os.path.pardir+os.path.sep+'lost'+os.path.sep+'extras'+os.path.sep+'data'+
    os.path.sep+'python')

import unittest
import yamf
from locations import LocationStore, LocationInfo

class Tester(LocationStore):

    def __init__(self, filemock):
        self.fileMock = filemock
        LocationStore.__init__(self)
        
    
    def _openFile(self, mode):
        return self.fileMock
    
class TestLocationStore(unittest.TestCase):

    def setUp(self):
        self.fileMock = yamf.Mock()
        self.store = Tester(self.fileMock)

    def testSavingLocationInfo(self):
        self.fileMock.write.mustBeCalled.withArgs('name,25.4.2006,65.500000,25.000000\n')

        self.store.save(LocationInfo('name', '25.4.2006', (65.5, 25.0)))

        self.fileMock.verify()

    def testStoreHasOneLocationInfo(self):
        self.fileMock.readlines.returns(['name,25.4.2006,65.0,25.0'])

        locationInfos = self.store.read()
        
        self.assertEquals(locationInfos, [LocationInfo('name','25.4.2006',(65.0,25.0))] )
        
    def testStoreHasManyLocationInfo(self):
        self.fileMock.readlines.returns(['name,25.4.2006,65.0,25.0','name2,25.4.2006,66.0,26.0'])

        locationInfos = self.store.read()
        
        self.assertEquals(locationInfos, [LocationInfo('name','25.4.2006',(65.0,25.0)),\
                                          LocationInfo('name2','25.4.2006',(66.0,26.0))])
        


if __name__ == '__main__':
    unittest.main()
