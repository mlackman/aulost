import appuifw 
import os

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
        if os.path.exists(filename):
            return False
        data = ''
        for location in track:
            data += '%f,' % location
        f = open(filename,'wt')
        f.write(data)
        f.close()
        return True
        

