from operator import or_
from functools import wraps, reduce
from django.views.generic import ListView

def ret_or_super(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except:
            self = args[0]
            res = getattr(super(self.__class__, self), func.__name__)(*args, **kwargs)
        
        return res
        
    return wrapper

class ExtendedListView(ListView):
    @ret_or_super
    def get_queryset(self):
        queryset = reduce(or_, map(lambda model: model._default_manager.all(), self.models))
        return queryset
