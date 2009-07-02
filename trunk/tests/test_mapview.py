import sys,os,unittest
sys.path.append(os.path.join(os.path.pardir,'lost','extras','data','python'))

from mapview import MapMover,KeyboardAmountOfMapMovement
import yamf
import key_codes

class MapMoverKeyboardEventTests(unittest.TestCase):

    def setUp(self):
        self.mapEngineMock = yamf.Mock()
        self.m = MapMover(self.mapEngineMock)
        
    def testUpKey(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(0,-KeyboardAmountOfMapMovement)
        self.m.canvasEventCallback({'keycode':key_codes.EKeyUpArrow})
        self.mapEngineMock.verify()        
        
    def testDownKey(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(0,KeyboardAmountOfMapMovement)
        self.m.canvasEventCallback({'keycode':key_codes.EKeyDownArrow})
        self.mapEngineMock.verify()
        
    def testLeftKey(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(-KeyboardAmountOfMapMovement,0)       
        self.m.canvasEventCallback({'keycode':key_codes.EKeyLeftArrow})
        self.mapEngineMock.verify()
        
    def testRightKey(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(KeyboardAmountOfMapMovement,0)       
        self.m.canvasEventCallback({'keycode':key_codes.EKeyRightArrow})
        self.mapEngineMock.verify()
        
class MapMoverPointerEventTests(unittest.TestCase):

    def setUp(self):
        self.mapEngineMock = yamf.Mock()
        self.m = MapMover(self.mapEngineMock)

    def testMovingUp(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(0,-1)
        self.m.canvasEventCallback({'type':key_codes.EButton1Down, 'pos':(50,50)})
        self.m.canvasEventCallback({'type':key_codes.EDrag, 'pos':(50,51)})
        self.m.canvasEventCallback({'type':key_codes.EButton1Up, 'pos':(50,51)})
        self.mapEngineMock.verify() 
        
    def testMovingDown(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(0,1)
        self.m.canvasEventCallback({'type':key_codes.EButton1Down, 'pos':(50,50)})
        self.m.canvasEventCallback({'type':key_codes.EDrag, 'pos':(50,49)})
        self.m.canvasEventCallback({'type':key_codes.EButton1Up, 'pos':(50,51)})
        self.mapEngineMock.verify() 
        
    def testMovingLeft(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(-1,0)
        self.m.canvasEventCallback({'type':key_codes.EButton1Down, 'pos':(50,50)})
        self.m.canvasEventCallback({'type':key_codes.EDrag, 'pos':(51,50)})
        self.m.canvasEventCallback({'type':key_codes.EButton1Up, 'pos':(53,50)})
        self.mapEngineMock.verify()
        
    def testMovingRight(self):
        self.mapEngineMock.moveMap.mustBeCalled.withArgs(1,0)
        self.m.canvasEventCallback({'type':key_codes.EButton1Down, 'pos':(50,50)})
        self.m.canvasEventCallback({'type':key_codes.EDrag, 'pos':(49,50)})
        self.m.canvasEventCallback({'type':key_codes.EButton1Up, 'pos':(53,50)})
        self.mapEngineMock.verify()              
    
    def testManyDragEvents(self):
        self.mapEngineMock.moveMap.mustBeCalled.times(2)
        self.m.canvasEventCallback({'type':key_codes.EButton1Down, 'pos':(50,50)})
        self.m.canvasEventCallback({'type':key_codes.EDrag, 'pos':(49,50)})
        self.m.canvasEventCallback({'type':key_codes.EDrag, 'pos':(48,50)})
        self.m.canvasEventCallback({'type':key_codes.EButton1Up, 'pos':(53,50)})
        self.mapEngineMock.verify()

if __name__ == '__main__':
    unittest.main()
