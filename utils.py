"""Utilities for notetaker.
- count_lines,
"""

from collections import OrderedDict

class GeneralQuery(object):
    """To replace Search and TimeSummary gui elements."""
    def __init__(self, mlist, altlist=None, master=None, replace=None,
                 ncommand=None, rcommand=None):
        if master is None or not isinstance(mlist, list):
            print "Need at least master and main list."
            return
        self.master = master
        self.top =  Toplevel(self.master)
        self.maind = OrderedDict()
        for key in mlist:
            self.maind[key] = ""#function that returns a packaged frame:
        if (replace == 1 and isinstance(altlist, list) and
            len(mlist) == len(altlist)):
            self.altl = altlist
            self.rep = IntVar() #to replace or not.
        else:
            replace = 0
        self.svar = StringVar()
        self.svar.set('Search')
        self.gui_build(replace, ncommand)

    def gui_build(self, replace, command):
        self.mp.transient(self.master)
        self.mp.bind("<Return>", self._search)
        self.mp.bind("<Escape>", self._cancel)
        for key,entry in self.maind:
            entry.pack()
        button_frame = Frame(self.master)
        Button(button_frame, textvariable=self.svar, width=9,
               command=self._decide).pack(side=LEFT)
        Button(bf, text="Cancel", command=self._cancel).pack(side=RIGHT)
        

    def replace(self):
        pass

    def _cancel(self, event=None):
        self.d = {}
        self.mp.destroy()


class LabInput(object):
    def __init__(self, master, label=None, in_type=None):
        self.master = master
        self.frame = Frame(self.master)
        self.label = Label(self.frame, text=label)
        self.label.pack(side=LEFT)
        if in_type is None:
            self.input = Entry(self.frame)
            self.input.pack(side=RIGHT)

    def replace(self, new_label):
        self.label.config(text=new_label)
        self.label.pack(side=LEFT)

    def pack(self, **kwargs):
        self.frame.pack(side=TOP)


def count_lines(line, wanted_length=77):
    """Return an approximate line count given a string"""
    lines = line.split("\n")
    count = len(lines) - 1
    for row in lines:
        length = len(row)/wanted_length
        if length < 1.0:
            continue
        count += int(length)
    return count
