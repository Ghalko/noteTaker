"""Module for timing events and tasks."""

from Tkinter import (Frame, Text, Label, WORD, BOTTOM, TOP,
                     END, LEFT)
import time
import datetime
import notetaker.ncore as ncore
from notetaker.utils import GeneralQuery

#*************************************************************************
class TimeSummary(object):
    """For retrieving times from the data base. And possibly updating."""
    func = None

    def __init__(self, th=None, master=None):
        if master is None:
            return
        self.master = master
        self.timeh = th
        self.mlist = ["Begin", "End", "Project"]
        self.alist = ["Date", "New", "Project"]
        self.command = self._decide
        genq = GeneralQuery(parent=self, replace=1)
        self.frame = genq.get_frame()
        self.dict = {} #dictionary of projects

    def _decide(self, list_, replace=None):
        """Decide which command to call"""
        if replace == 1:
            self.replace(list_)
        else:
            self.search(list_)

    def replace(self, list_):
        """Gets date, new time and Project and replaces the time."""
        (date, time_, project) = list_
        if date != "":
            date = int(date)
        else:
            print "Need a specific date."
            return
        if time_ == "" or project == None:
            print "Need all three."
            return
        if time_.find(':') > 0: #time given in hh:mm:ss
            hms = time_.split(":")
            time_ = int(hms[0])*3600 + int(hms[1])*60 + int(hms[2])
        else:
            time_ = int(time_)
        self.timeh.update(project, time_, date, replace=1)

    def search(self, list_):
        """Search for times in projects on specified days."""
        beg = list_[0].strip()
        end = list_[1].strip()
        project = list_[2].strip()
        for each in self.dict:
            self.dict[each].clear()
        if beg != "":
            beg = int(beg)
        else:
            beg = None
        if end != "":
            end = int(end)
        else:
            end = None
        if project:
            if project not in self.dict:
                self.dict[project] = TimeDisp(self.frame, project)
            for row in self.timeh.ret_notes(b_date=beg, e_date=end,
                                            project=project):
                self.dict[project].append(row[0], row[1])
            self.dict[project].update()
        else:
            for row in self.timeh.ret_notes(b_date=beg, e_date=end):
                if row[0] not in self.dict:
                    self.dict[row[0]] = TimeDisp(self.frame, row[0])
                self.dict[row[0]].append(row[1], row[2])
                self.dict[row[0]].update()


#***********************************************************************
class TimeDisp(object):
    '''Project time summary and list of dates and times.'''
    def __init__(self, master, project):
        self.frame = Frame(master, borderwidth=2)
        Label(self.frame, text=project).pack(side=TOP)
        self.time = 0 #total time on project over period.
        self.label = Label(self.frame)
        self.label.pack(side=TOP)
        self.disp = Text(self.frame, height=8, width=20, wrap=WORD,
                         bg='sea green', spacing1=5)
        self.disp.pack(side=BOTTOM)

    def append(self, date, time_):
        """Insert new date and time at the end."""
        self.time = self.time + time_
        hour = int(time_/3600.)
        minute = int((time_ - (hour*3600))/60.)
        sec = time_ - ((hour * 3600) + (minute * 60))
        time_str = (str(date) + ': ' + str(hour) + ':' + str(minute) +
                    ':' + str(sec) + '\n')
        self.disp.insert(END, time_str)

    def update(self):
        """Take the time and put it into readable format."""
        hour = int(self.time/3600.)
        minute = int((self.time - (hour*3600))/60.)
        sec = self.time - ((hour * 3600) + (minute * 60))
        time_str = str(hour) + ":" + str(minute) + ":" + str(sec)
        self.label.config(text="Total: "+time_str)
        self.frame.pack(side=LEFT)

    def clear(self):
        """Clear the text display and forgets the pack"""
        self.disp.delete('1.0', END)
        self.time = 0
        self.frame.pack_forget()

#* Project Timer *******************************************************
class ProjectTime(object):
    '''A timer for a project'''
    def __init__(self, project, th):
        self.project = project
        self.timeh = th
        self.flag = 0
        self.time = 0

    def _start(self):
        '''Gets the first time.'''
        self.time = time.time()
        self.flag = 1

    def _stop(self):
        '''Gets the second time and takes away the first.'''
        time_sec = int(time.time() - self.time)
        self.flag = 0
        date_str = int(datetime.datetime.now().strftime("%Y%m%d"))
        self.timeh.update(self.project, time_sec, date_str)

    def click(self, close=None):
        """
        Run the correct action, depending on the flag.
        Close is when project is closed.
        """
        if self.flag:
            self._stop()
        else:
            if close is not None:
                return None
            self._start()
        return self.flag

#* Timer Class *********************************************************
class Timer(object):
    '''Timer class allows multiple things to be timed and recorded in SQL.'''
    def __init__(self, path):
        self.timeh = ncore.TimeHandler(dbpath=path) #timehandler
        self.dict = {} #Holds the different projects

    def newtimer(self, project):
        '''Returns the stop/go for command'''
        if project not in self.dict:
            self.dict[project] = ProjectTime(project, self.timeh)
        return self.dict[project].click

    def summary(self, master_):
        """Run up new timer summary"""
        TimeSummary(th=self.timeh, master=master_)
