import sys
import os
sys.path.append(
    os.path.pardir+os.path.sep+'lost'+os.path.sep+'extras'+os.path.sep+'data'+
    os.path.sep+'python')

import unittest
import view
import yamf

class TestEmptyViewManager(unittest.TestCase):
    
    def setUp(self):
        self.vm = view.ViewManager()
        
    def test_has_view(self):
        self.assertFalse(self.vm.has_view('view'))
        
    def test_changing_non_existing(self):
        self.assertRaises(AssertionError, self.vm.change_view, 'view')
        
    def test_current_view(self):
        self.assertEquals(None, self.vm.current_view)

class TestViewManagerWithView(unittest.TestCase):

    def setUp(self):
        self.vm = view.ViewManager()
        self.viewMock = yamf.Mock()
        self.vm.add('view', self.viewMock)
        
    def test_adding_same_view_twice(self):
        self.assertRaises(AssertionError, self.vm.add, 'view', yamf.Mock())
        
    def test_changing_view(self):
        self.viewMock.activate.mustBeCalled.once
        self.vm.change_view('view')
        
        self.viewMock.verify()
        
    def test_current_view(self):
        self.vm.change_view('view')
        self.assertEquals(self.viewMock, self.vm.current_view)
        
    def test_deactivate(self):
        anotherMockView = yamf.Mock()
        anotherMockView.deactivate.mustBeCalled.once

        self.vm.add('view2', anotherMockView)
        self.vm.change_view('view2')
        self.vm.change_view('view')
        
        anotherMockView.verify()    
    
if __name__ == '__main__':
    unittest.main()
    
