import appuifw 
import time
import datetime
import os
import view

class SaveLocationDlg(object):
    
    def __init__(self, locationStore, initialName=None, initialDateStr=None):
        self._locationStore = locationStore
        if initialName:
            nameField = (u'Name','text',unicode(initialName))
        else:
            nameField = (u'Name', 'text')
        if initialDateStr:
            year,month,day = initialDateStr.split('-')
            initialDate = datetime.date(int(year), int(month), int(day))
            timeField = (u'date','date', time.mktime(initialDate.timetuple()))
        else:
            timeField = (u'Date', 'date', time.time())
        fields = [nameField, timeField]
        self._form = self._createForm(fields)
        self._form.save_hook = self._saveHook

    def execute(self, position):
        self._saved = False
        self._form.execute()
        if self._saved:
            name, date = self._form[0][2], self._form[1][2]
            self._locationStore.save(LocationInfo(name,str(datetime.date.fromtimestamp(date)),position))
        return self._saved

    def _saveHook(self, arg):
        self._saved = True  

    def _createForm(self, fields):
        return appuifw.Form(fields)

class LocationsView(view.View):
    
    def __init__(self, locationStore, viewManager, engine):
        view.View.__init__(self, 'LocationsView', viewManager)
        self._store = locationStore
        self._locations = None
        self._engine = engine

    def activate(self):
        self._locations = self._store.read()
        if self._locations:
            listItems = self._listItems()
            appuifw.app.body = appuifw.Listbox(listItems,self._selectionCallback)
            appuifw.app.menu = [(u'View', self._view),
                                (u'Navigate', self._navigate),
                                (u'Edit', self._edit),
                                (u'Delete', self._delete),
                                (u'Back to map', self._toMapView)]
            
        else:
            appuifw.note(u'No saved locations', 'info')
            self._toMapView()

    def _selectionCallback(self):
        # TODO: What to do, go to mapview and show the location?
        pass

    def _toMapView(self):
        self.view_manager.change_view('MapView')
    
    def _view(self):
        info = self._selectedInfo()
        self._engine.currentPosition = info.position
        self._toMapView()

    def _navigate(self):
        pass
        
    def _edit(self):
        info = self._selectedInfo()
        dlg = SaveLocationDlg(self._store, info.name, info.date)
        saved = dlg.execute(info.position)
        if saved:
            self._deleteInfo(info)
            self._locations = self._store.read()
            appuifw.app.body.set_list(self._listItems())
        
    def _delete(self):
        self._deleteInfo(self._selectedInfo())
        if self._locations:
            appuifw.app.body.set_list(self._listItems())
        else:
            appuifw.note(u'No more locations', 'info')
            self._toMapView()

    def _deleteInfo(self, info):
        self._locations.remove(info)
        self._store.delete(info)       

    def _listItems(self):
        return [(unicode(info.name),unicode(info.date)) for info in self._locations]

    def _selectedInfo(self):
        return self._locations[appuifw.app.body.current()]

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
        self._save(locationInfo, 'a')

    def delete(self, info):
        infos = self.read()
        infos.remove(info)
        self._openFile('wt').close() # Empties the file
        map(lambda info: self._save(info, 'at'), infos)

    def _openFile(self, mode):
        return open('locations.txt', mode)

    def _save(self,info,mode):
        f = self._openFile(mode)
        f.write(str(info)+'\n')
        f.close()

        
