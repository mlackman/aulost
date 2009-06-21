
class View(object):
    """Base class for views. View classes must implement activate method where,
       view should display itself. Deactivate is called from active view, 
       if implemented, when other view becomes active"""

    def __init__(self, name, viewManager):
        """Creates view and registeres itself to viewManager"""
        self.name = name
        self.view_manager = viewManager
        self.view_manager.add(name, self)
    

class ViewManager(object):
    """Holds views and offers a way to change views. Each view has to implement at least activate method.
       If view implements deactivate it will be called before new view is activated"""
       
    def __init__(self):
        self._views = {}
        self.current_view = None
        
    def change_view(self, name):
        """Activates a view by name. Possible previous view is deactivated.
        Note that from activate and deactivate methods view change cannot 
        be done.
        Precond: has_view(name) == True"""
        assert self.has_view(name),  'ViewManager: No such view ' + name
        
        # Call deactivate for view which has the deactivate method.
        if hasattr(self.current_view, 'deactivate'):
            self.current_view.deactivate()
            
        view = self._views[name]
        view.activate()
        self.current_view = view
            
    def add(self, name, view):
        """Adds a view by name. Precond: has_view(name) == False"""
        assert not self.has_view(name)
        self._views[name] = view
        
    def has_view(self, name):
        """Checks if view with name already added"""
        return self._views.has_key(name)
