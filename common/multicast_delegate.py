#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  14:30


class MulticastDelegate(object):
    def __init__(self, target_function):
        self._invocation_list = []
        if target_function and not callable(target_function):
            raise ValueError("Target function must be callable")
        if target_function:
            self._invocation_list.append(target_function)

    def invoke(self, *args, **kwargs):
        return [fun(*args, **kwargs) for fun in self._invocation_list]

    def get_invocation_list(self):
        return list(self._invocation_list)

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def __add__(self, other):
        # type: (callable) -> MulticastDelegate
        if not other and not callable(other):
            raise ValueError("Other must be callable")
        my_functions = self.get_invocation_list()
        ret = MulticastDelegate(None)
        if isinstance(other, MulticastDelegate):
            ret._invocation_list = my_functions + other._invocation_list
        else:
            ret._invocation_list = my_functions
            if not other in my_functions:
                ret._invocation_list.append(other)
        return ret

    def __sub__(self, other):
        # type: (callable) -> MulticastDelegate
        if not other and not callable(other):
            raise ValueError("Other must be callable")
        my_functions = self.get_invocation_list()
        ret = MulticastDelegate(None)
        ret._invocation_list = my_functions
        if isinstance(other, MulticastDelegate):
            ret._invocation_list = [item for item in my_functions if item not in other._invocation_list]
        else:
            ret._invocation_list.remove(other)
        return ret
