import sys
import os
sys.path.append(
    os.path.pardir+os.path.sep+'lost'+os.path.sep+'extras'+os.path.sep+'data'+
    os.path.sep+'python')

import unittest
import yamf
from locations import LocationsView, SaveLocationDlg, LocationInfo
import appuifw

class TestLocationView(unittest.TestCase):

    def setUp(self):
        self.locationStoreStub = yamf.Mock()
        self.locationStoreStub.read.returns(
            [LocationInfo('name','15.4.2009',(65.0,25.0)),LocationInfo('name2','16.5.2010',(66.0,26.0))])
        self.v = LocationsView(self.locationStoreStub)
    
    def testViewComponentIsListBox(self):
        self.assertEquals(type(appuifw.app.body), appuifw.Listbox)

    def testViewShowsLocationInfos(self):
        self.assertEquals(appuifw.app.body.list, 
            [(u'name',u'15.4.2009'),(u'name2',u'16.5.2010')])

class TestLocationDlg(unittest.TestCase):

    class Tester(SaveLocationDlg):
        def __init__(self, locationStore, formMock):
            self.formMock = formMock
            SaveLocationDlg.__init__(self, locationStore)

        def _createForm(self, fields):
            return self.formMock
    
    def testUserDoesNotSave(self):
        locationStoreMock = yamf.Mock()
        locationStoreMock.save.mustNotBeCalled
        formMock = yamf.Mock()

        dlg = TestLocationDlg.Tester(locationStoreMock, formMock)
        dlg.execute((65,25))

        locationStoreMock.verify()

    def testUserSaves(self):
        locationStoreMock = yamf.Mock()
        locationStoreMock.save.mustBeCalled.withArgs(LocationInfo('name','2009-02-22',(65,25)))

        dlg = SaveLocationDlg(locationStoreMock)
        dlg.execute((65,25))

        locationStoreMock.verify()

if __name__ == '__main__':
    unittest.main()
