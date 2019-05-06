from itertools import chain
from django.views.generic import ListView

class ExtendedListView(ListView):
    def get_queryset(self):
        return chain.from_iterable(map(lambda model: model._default_manager.all(), self.models))
