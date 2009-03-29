import sys
import os
sys.path.append(
    os.path.pardir+os.path.sep+'lost'+os.path.sep+'extras'+os.path.sep+'data'+
    os.path.sep+'python')

import unittest
import lostapp
import yamf

class TestMapProviderSelection(unittest.TestCase):

    def setUp(self):
        import appuifw
        self.givenSelections = None
        def stub_selection_list(selections):
            self.givenSelections = selections
        appuifw.selection_list = stub_selection_list

        import map as maps
        def stub_providers(self): return ['karttapaikka']
        maps.MapProviders.providers = stub_providers
        maps.MapProviders.setProvider = yamf.Mock().stubmethod
    
    def testMapProviderSelectionAtAppStartup(self):
        """Map provider must be selected when application launches"""
        app = lostapp.LostApp()
        self.assertEquals(self.givenSelections, [u'karttapaikka'])

    def testUserSelectMapProvider(self):
        import appuifw
        appuifw.selection_list = yamf.Mock().stubmethod
        appuifw.selection_list.returns(0)

        import map as maps
        mock = yamf.Mock()
        mock.mockMethod.mustBeCalld
        maps.MapEngine.setMapProvider = mock.mockMethod

        app = lostapp.LostApp()

        mock.verify()


if __name__ == '__main__':
    unittest.main()
