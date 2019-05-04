from django.urls import include, path

class PatternManager:
    """A pattern manager for urlpatterns. 
    
    Subclass it with collections.UserList and then
    add class variables about your routes.
    
        class XXXPatterns(PatternManager, UserList):
            <name> = <path>, <view>
        
        urlpatterns = XXXPatterns()
    
    You dont need to call as_view() for generics. PatternManager
    will call them for you. 
    
    If you need to include urls from another module define a class variable
    called includes (it is reserved for this purpose, you cant use that as a <name>
    for normal route). 
    
        includes = {<path>: <include>, 
                    <path.n>: <include.n>, 
                    'accounts': 'django.contrib.auth.urls'}
    """
    
    def __init__(self):
        self.data = []
        patterns = dict(filter(lambda member: not member[0].startswith('_'), vars(self.__class__).items()))
        
        if 'includes' in patterns:
            for route, module in patterns.pop('includes').items():
                self.data.append(path(route, include(module)))
                
        for name, route in patterns.items():
            route, view = route
            if hasattr(view, 'as_view'):
                view = view.as_view()
                
            pattern = path(route, view, name=name)
            self.data.append(pattern)
