from functools import reduce
from operator import or_

def multi_qs(*models):
    return reduce(or_, map(lambda model: model._default_manager.all(), self.models))
