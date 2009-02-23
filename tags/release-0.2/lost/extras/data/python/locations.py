import appuifw 
import time
import datetime

class SaveLocationDlg(object):
    
    def __init__(self, locationStore):
        self._locationStore = locationStore
        fields = [(u'Name', 'text'), (u'Date', 'date', time.time())]
        self._form = self._createForm(fields)
        self._form.save_hook = self._saveHook

    def execute(self, position):
        self._saved = False
        self._form.execute()
        if self._saved:
            name, date = self._form[0][2], self._form[1][2]
            self._locationStore.save(LocationInfo(name,str(datetime.date.fromtimestamp(date)),position))

    def _saveHook(self, arg):
        self._saved = True  

    def _createForm(self, fields):
        return appuifw.Form(fields)

class LocationsView(object):
    
    def __init__(self, locationStore, viewManager, engine):
        self._viewManager = viewManager
        self._store = locationStore
        self._locations = None
        self._engine = engine

    def activate(self):
        self._locations = self._store.read()
        if self._locations:
            nameAndDates = [(unicode(info.name),unicode(info.date)) for info in self._locations]
            appuifw.app.body = appuifw.Listbox(nameAndDates,self._selectionCallback)
            appuifw.app.menu = [(u'View', self._view),
                                (u'Navigate', self._navigate),
                                (u'Edit', self._edit),
                                (u'Delete', self._delete),
                                (u'Back to map', self._toMapView)]
            
        else:
            appuifw.note(u'No saved locations', 'info')
            self._toMapView()

    def _selectionCallback(self):
        pass

    def _toMapView(self):
        self._viewManager.changeView('MapView')
    
    def _view(self):
        info = self._locations[appuifw.app.body.current()]
        self._engine.currentPosition = info.position
        self._toMapView()

    def _navigate(self):
        pass
        
    def _edit(self):
        pass
        
    def _delete(self):
        pass

class LocationInfo(object):
    
    def __init__(self, *args):
        if len(args) == 3:
            self.name, self.date, self.position = args
        elif len(args) == 1:
            self._fromString(args[0])    

    def _fromString(self, string):
        self.name, self.date, lat,lon = string.split(',')
        self.position = (float(lat),float(lon))
    
    def __str__(self):
        lat,lon = self.position
        return '%s,%s,%f,%f' % (self.name, self.date,lat,lon)

    def __eq__(self, other):
        if type(other) == LocationInfo:
            return other.name == self.name and other.date == self.date and \
                   other.position == self.position
        return False 

class LocationStore(object):
    """Place to store user locations"""

    def __init__(self):
        """Creates location store.
        param:
            file - opened file object"""
        f = self._openFile('a')
        f.close()

    def read(self):
        """Reads all location infos.
        return: [(location name, time, position)]"""
        f = self._openFile('rt')
        lines = f.readlines()
        f.close()
        infos = []
        for info in lines:
            infos.append(LocationInfo(info))
        return infos

    def save(self, locationInfo):

        f = self._openFile('a')
        f.write(str(locationInfo)+'\n')
        f.close()

    def _openFile(self, mode):
        return open('locations.txt', mode)
