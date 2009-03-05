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

    def load(self, filename):
        f = open(filename + '_track', 'rt')
        data = f.read()
        f.close()
        strPoints = data.split(';')
        strPoints = map(lambda strPoint: strPoint.split(','), strPoints)
        trackPoints = [(float(lat),float(lon)) for lat,lon in strPoints[:-1]]
        return trackPoints
    
    def save(self, filename, trackPoints):
        filename += '_track'
        if os.path.exists(filename):
            return False
        data = ''
        for location in trackPoints:
            data += '%f,%f;' % location
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
    
    def __init__(self, trackStore, viewManager, engine):
        self._trackStore = trackStore
        self._viewManager = viewManager
        self._trackNames = None
        self._engine = engine

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
        trackPoints = self._trackStore.load(self._selectedTrack())
        self._engine.track = trackPoints
        self._engine.currentPosition = trackPoints[0]
        self._toMapView()

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
        

