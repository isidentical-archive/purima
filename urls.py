from dataclasses import dataclass
from typing import Optional, Sequence

from django.urls import include, path

@dataclass(frozen=True, unsafe_hash=True)
class IncludeFilter:
    """Includes with a set of filters. It requires the module name,
    and if you want to set a filter you need to choose whitelist and/or
    blacklist. """
    
    module: str
    whitelist: Optional[Sequence] = None
    blacklist: Optional[Sequence] = None

    def __str__(self):
        return self.module
        
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
    
    Also you can include in a way that allows you to control what you will have.
    You need to use IncludeFilter in the <include> parameter. The whitelist & blacklist
    for IncludeFilter will used through to patch urlpatterns of imported module."""
    
    
    def __init__(self):
        self.data = []
        patterns = dict(
            filter(
                lambda member: not member[0].startswith("_"),
                vars(self.__class__).items(),
            )
        )

        if "includes" in patterns:
            for route, module in patterns.pop("includes").items():
                included = include(str(module))
                if isinstance(module, IncludeFilter):
                    included = self._filtered_include(module, included)

                self.data.append(path(route, included))

        for name, route in patterns.items():
            route, view = route
            if hasattr(view, "as_view"):
                view = view.as_view()

            pattern = path(route, view, name=name)
            self.data.append(pattern)
    
    def _filtered_include(self, module, included):
        urlconf_module, *meta = included
        urlpatterns = urlconf_module.urlpatterns
        _type = type(urlpatterns)
        if module.blacklist:
            urlpatterns = filter(
                lambda pattern: pattern.name not in module.blacklist,
                urlpatterns,
            )
        if module.whitelist:
            urlpatterns = filter(
                lambda pattern: pattern.name in module.whitelist,
                urlpatterns,
            )

        urlconf_module.urlpatterns = _type(urlpatterns)
        included = urlconf_module, *meta
