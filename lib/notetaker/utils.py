"""Utilities for notetaker.
- GeneralQuery
- count_lines,
"""

from collections import OrderedDict
from Tkinter import *

from tkFileDialog import askopenfilename, askdirectory
import tkSimpleDialog

class GeneralQuery(object):
    """To replace Search and TimeSummary query gui elements.
       Parent needs master, command, and mlist
       If there is a replace, then it needs alist
    """
    def __init__(self, parent=None, replace=None):
        if (parent is None or not hasattr(parent, 'master')
            or not hasattr(parent, 'command')
            or not hasattr(parent, 'mlist')):
            print "Need parent, command, master, and mlist."
            return
        if replace is not None and not hasattr(parent, 'alist'):
            print "Replace is true yet no alternative list."
            return
        self.parent = parent
        self.top = None #toplevel window
        self.cmdb = None #command button
        self.frame = None #frame for inputs
        self.rep = None #replace indicator
        self.fout = None #output frame for parent.
        self._gui_build(replace) #Lays out the toplevel
        self.mainl = []
        for i in parent.mlist:
            self.mainl.append(LabInput(self.frame, label=i))
        self.pack()

    def _gui_build(self, replace):
        """Build top level gui."""
        self.top = Toplevel(self.parent.master)
        self.top.transient(self.parent.master)
        self.top.bind("<Return>", self._get)
        self.top.bind("<Escape>", self._cancel)
        self.frame = Frame(self.top)
        self.frame.pack(side=TOP)
        button_frame = Frame(self.top)
        button_frame.pack(side=TOP)
        self.fout = Frame(self.top)
        self.fout.pack(side=TOP)
        self.cmdb = Button(button_frame, text="Search", width=9,
                           command=self._get)
        self.cmdb.pack(side=LEFT)
        Button(button_frame, text="Cancel",
               command=self._cancel).pack(side=RIGHT)
        self.rep = IntVar() #to replace or not.
        self.rep.set(-1)
        if replace is not None:
            Checkbutton(self.top, text="Replace", command=self.replace,
                        variable=self.rep).pack(side=RIGHT)

    def get_frame(self):
        return self.fout

    def _get(self, event=None):
        """Return input from entries."""
        out_list = []
        for entry in self.mainl:
            out_list.append(entry.get())
        if self.rep.get() == -1:
            self.parent.command(out_list)
        else:
            self.parent.command(out_list, self.rep.get())

    def pack(self):
        """Pack all entries."""
        for entry in self.mainl:
            entry.pack()

    def replace(self, event=None):
        """Replace the old command with a new command. Also replace text."""
        if self.rep.get() == 1:
            for i in range(len(self.mainl)):
                self.mainl[i].replace(self.parent.alist[i])
            self.cmdb.config(text="Replace")
        else:
            for i in range(len(self.mainl)):
                self.mainl[i].replace(self.parent.mlist[i])
            self.cmdb.config(text="Search")
        self.pack()
        self.cmdb.pack(side=LEFT)

    def _cancel(self, event=None):
        self.top.destroy()


class LabInput(object):
    def __init__(self, master, label=None, in_type=None):
        self.master = master
        self.frame = Frame(self.master)
        label = label + ": "
        self.label = Label(self.frame, text=label)
        self.label.pack(side=LEFT)
        if in_type is None or in_type == "Entry":
            self.input = Entry(self.frame)
            self.input.pack(side=RIGHT)

    def get(self):
        return self.input.get()

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


class DBFile(object):
    def __init__(self, master=None, path=None):
        self.master = master
        self.path = path
        self.file = None
        self.top = Toplevel(master)
        self.top.transient(master)
        self.top.grab_set()
        Label(self.top, text="Database").pack(side=TOP)
        Button(self.top, text="New", command=self._new).pack(side=TOP)
        Button(self.top, text="Open", command=self._open).pack(side=TOP)

    def _new(self, event=None):
        self.path = askdirectory(initialdir=self.path)
        print self.path
        ans = tkSimpleDialog.askstring("", "New DB file:",
                                       parent=self.master)
        self.file = self.path + "/" + ans
        self.top.destroy()

    def _open(self, event=None):
        if self.path is None:
            self.file =  askopenfilename(filetypes=(("database", "*.db"),
                                          ("All files", "*.*")))
        else:
            self.file = askopenfilename(filetypes=(("database", "*.db"),
                                          ("All files", "*.*")),
                                initialdir=self.path)
        if self.file == ():
            self._new()
        else:
            self.top.destroy()

    def return_value(self):
        self.master.wait_window(self.top)
        return self.file
