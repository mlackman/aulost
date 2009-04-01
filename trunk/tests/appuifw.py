
class Application(object):
    
    def __init__(self):
        body = None

app = Application()

def note(*args,**kwargs):
    pass

class Canvas(object):

    def __init__(self, a,b,c): 
        self.size = (0,0)

    def clear(self): pass

class Listbox(object):

    def __init__(self, list, callback):
        self.list = list

class Form(object):

    def __init__(self, *args, **kwargs):
        self.save_hook = None

    def __getitem__(self, i):
        d = [(0,0,'name'),(0,0,1235286913.4549029)]
        return d[i]

    def execute(self):
        self.save_hook(0)
