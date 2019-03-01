from tkinter.ttk import Entry
from tkinter import StringVar
import os.path

class AbstactEntry(Entry):
    def __init__(self, *args, **kwargs):
        initial_value = kwargs.pop('initial_value', '')
        self.last_valid_value = initial_value
        self.text = StringVar(value=initial_value)

        Entry.__init__(self, *args, textvariable=self.text, **kwargs)
        self.vcmd = self.register(self.validate)
        self.ivcmd = self.register(self.invalidate)
        self['validate'] = 'focusout'
        self['validatecommand'] = self.vcmd, '%P',
        self['invalidcommand'] = self.ivcmd,

    def validate(self, inp):
        raise NotImplementedError

    def invalidate(self):
        self.text.set(self.last_valid_value)

    def set(self, value):
        self.last_valid_value = value
        self.text.set(value)

class FloatEntry(AbstactEntry):
    def __init__(self, *args, **kwargs):
        initial_value = kwargs.pop('initial_value', '0.5')
        self.last_valid_value = initial_value
        self.text = StringVar(value=initial_value)

        AbstactEntry.__init__(self, *args, initial_value=initial_value, **kwargs)

    def validate(self, inp):
        try:
            float(inp)
        except ValueError:
            return False
        self.last_valid_value = inp
        return True

    def get(self):
        return float(self.text.get())

class IntEntry(AbstactEntry):
    def __init__(self, *args, **kwargs):
        initial_value = kwargs.pop('initial_value', '1')
        self.last_valid_value = initial_value
        self.text = StringVar(value=initial_value)

        AbstactEntry.__init__(self, *args, initial_value=initial_value, **kwargs)

    def validate(self, inp):
        try:
            int(inp)
        except ValueError:
            return False
        self.last_valid_value = inp
        return True

    def get(self):
        return int(self.text.get())

class StringEntry(AbstactEntry):
    def __init__(self, *args, **kwargs):
        initial_value = kwargs.pop('initial_value', '')
        self.last_valid_value = initial_value
        self.text = StringVar(value=initial_value)

        AbstactEntry.__init__(self, *args, initial_value=initial_value, **kwargs)

    def validate(self, inp):
        return True

class FileEntry(AbstactEntry):
    def __init__(self, *args, **kwargs):
        initial_value = kwargs.pop('initial_value', '')
        self.last_valid_value = initial_value
        self.text = StringVar(value=initial_value)

        AbstactEntry.__init__(self, *args, initial_value=initial_value, **kwargs)
        self['validate'] = 'focus'

    def validate(self, inp):
        if os.path.exists(inp):
            self.last_valid_value = inp
            return True
        else:
            return False




