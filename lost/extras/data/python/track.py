import appuifw 
import os
import utils

class SaveTrackDlg(object):

    def __init__(self, trackStore):
        self._trackStore = trackStore
        
    def execute(self, track):
        success = False
        while not success:
            filename = appuifw.query(u'Name of the track', 'text')
            if filename: 
                success = self._save(filename, track)
                if not success:
                    appuifw.note(u'Track already exists. Choose other name', 'error')
            else:
                break

    def _save(self, filename, track):
        return self._trackStore.save(str(filename), track)

class TrackStore(object):
    
    def save(self, filename, track):
        filename += '_track'
        if os.path.exists(filename):
            return False
        data = ''
        for location in track:
            data += '%f,' % location
        f = open(filename,'wt')
        f.write(data)
        f.close()
        return True

    def delete(self, filename):
        os.remove(filename + '_track')

    def trackNames(self):
        files = utils.findFilesEndsWith('_track', '.')
        return map(lambda file: file[:-len('_track')], files)
        

class TrackView(object):
    
    def __init__(self, trackStore, viewManager):
        self._trackStore = trackStore
        self._viewManager = viewManager
        self._trackNames = None

    def activate(self):
        self._trackNames = self._trackStore.trackNames()
        if self._trackNames:
            appuifw.app.body = appuifw.Listbox(self._listItems(),self._selectionCallback)
            appuifw.app.menu = [(u'View', self._view),
                                (u'Delete', self._delete),
                                (u'Back to map', self._toMapView)]
        else:
            appuifw.note(u'No saved tracks', 'info')
            self._toMapView()

    def _listItems(self):
        return [unicode(trackName) for trackName in self._trackNames]

    def _view(self):
        pass

    def _delete(self):
        self._deleteTrack(self._selectedTrack())
        if self._trackNames:
            appuifw.app.body.set_list(self._listItems())
        else:
            appuifw.note(u'No more tracks', 'info')
            self._toMapView()

    def _deleteTrack(self, trackName):
        self._trackNames.remove(trackName)
        self._trackStore.delete(trackName)      

    def _selectedTrack(self):
        return self._trackNames[appuifw.app.body.current()]

    def _toMapView(self):
        self._viewManager.changeView('MapView')

    def _selectionCallback(self):
        pass
        

