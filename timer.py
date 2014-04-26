"""Module for timing events and tasks."""

from Tkinter import (Frame, Button, Text, IntVar, Toplevel, StringVar,
                     Label, Entry, Checkbutton, WORD, BOTTOM, TOP,
                     END, RIGHT, LEFT)
import time
import datetime
import ncore

#*************************************************************************
class TimeSummary(object):
    '''For retrieving time data from the data base. And possibly updating.'''
    def __init__(self, th=None, master=None, title=None):
        if master is None:
            return
        self.master = master
        self.timeh = th
        self.b = None #beginning date
        self.e = None #end date
        self.p = None #project
        self.r = IntVar() #to replace or not.
        self.d = {} #dictionary of projects
        self.mp = Toplevel(self.master)
        self.mp.transient(self.master)
        self.mp.bind("<Return>", self._search)
        self.mp.bind("<Escape>", self._cancel)
        if title:
            self.mp.title(title)
        #****
        self.f = Frame(self.mp)
        self.f.pack(side=BOTTOM)
        begf = Frame(self.mp) #beginning date
        begf.pack(side=TOP)
        self.bvar = StringVar()
        self.bvar.set('Begin:')
        Label(begf, textvariable=self.bvar, width=8).pack(side=LEFT)
        self.be = Entry(begf)
        self.be.pack(side=RIGHT)
        endf = Frame(self.mp)  #end date
        endf.pack(side=TOP)
        self.evar = StringVar()
        self.evar.set('End:')
        Label(endf, textvariable=self.evar, width=8).pack(side=LEFT)
        self.ee = Entry(endf)
        self.ee.pack(side=RIGHT)
        pf = Frame(self.mp)  #project
        pf.pack(side=TOP)
        Label(pf, text='Project:', width=8).pack(side=LEFT)
        self.pe = Entry(pf)
        self.pe.pack(side=RIGHT)
        bf = Frame(self.mp)
        bf.pack(side=TOP)
        self.svar = StringVar()
        self.svar.set('Search')
        Button(bf, textvariable=self.svar, width=9,
               command=self._decide).pack(side=LEFT)
        cancel = Button(bf, text="Cancel", command=self._cancel)
        cancel.pack(side=RIGHT)
        Checkbutton(self.mp, text="Replace", variable=self.r,
                    command=self._switch, onvalue=1, offvalue=0).pack(side=TOP)

    def _switch(self, event=None):
        '''Switches to the replacement view when checked and back
        when unchecked.'''
        if self.r.get() == 1:
            self.bvar.set('Date:')
            self.evar.set('New:')
            self.svar.set('Replace')
        else:
            self.bvar.set('Begin:')
            self.evar.set('End:')
            self.svar.set('Search')
        self.master.update_idletasks()

    def _decide(self, event=None):
        if self.r.get() == 1:
            self._replace()
        else:
            self._search()

    def _replace(self, event=None):
        '''Gets date, new time and Project and replaces the time.'''
        date = self.be.get() #Date
        time = self.ee.get() #New time
        if date != "":
            date = int(self.b)
        else:
            print "Need a specific date."
        project = self.pe.get() #project
        if beg == None or end == "" or project == None:
            print "Need all three."
            return
        if end.find(':') > 0: #Time given in hh:mm:ss
            hms = end.split(":")
            end = int(hms[0])*3600 + int(hms[1])*60 + int(hms[2])
        else:
            end = int(end)
        self.timeh.update(project, end, self.b, replace=1)

    def _search(self, event=None):
        self.b = self.be.get().strip()
        self.e = self.ee.get().strip()
        self.p = self.pe.get().strip()
        for e in self.d:
            self.d[e].clear()
        if self.b != "":
            self.b = int(self.b)
        else:
            self.b = None
        if self.e != "":
            self.e = int(self.e)
        else:
            self.e = None
        if self.p:
            if self.p not in self.d:
                self.d[self.p] = TimeDisp(self.f, self.p)
            for row in self.timeh.ret_notes(b_date=self.b, e_date=self.e,
                                         project=self.p):
                self.d[self.p].append(row[0], row[1])
            self.d[self.p].update()
        else:
            for row in self.timeh.ret_notes(b_date=self.b, e_date=self.e):
                if row[0] not in self.d:
                    self.d[row[0]] = TimeDisp(self.f, row[0])
                self.d[row[0]].append(row[1], row[2])
                self.d[row[0]].update()

    def _cancel(self, event=None):
        self.d = {}
        self.mp.destroy()

#***********************************************************************
class TimeDisp(object):
    '''Project time summary and list of dates and times.'''
    def __init__(self, master, project):
        self.f = Frame(master, borderwidth=2)
        Label(self.f, text=project).pack(side=TOP)
        self.t = 0 #total time on project over period.
        self.l = Label(self.f)
        self.l.pack(side=TOP)
        self.p = project
        self.disp = Text(self.f, height=8, width=20, wrap=WORD,
                         bg='sea green', spacing1=5)
        self.disp.pack(side=BOTTOM)

    def append(self, date, time):
        self.t = self.t + time
        hr = int(time/3600.)
        mi = int((time - (hr*3600))/60.)
        sec = time - ((hr * 3600) + (mi * 60))
        s = str(date) + ': ' + str(hr) + ':' + str(mi) + ':' + str(sec) + '\n'
        self.disp.insert(END, s)

    def update(self):
        hr = int(self.t/3600.)
        mi = int((self.t - (hr*3600))/60.)
        sec = self.t - ((hr * 3600) + (mi * 60))
        t = str(hr) + ":" + str(mi) + ":" + str(sec)
        self.l .config(text="Total: "+t)
        self.f.pack(side=LEFT)

    def clear(self):
        self.disp.delete('1.0', END)
        self.t = 0
        self.f.pack_forget()

#* Project Timer *******************************************************
class ProjectTime(object):
    '''A timer for a project'''
    def __init__(self, project, th):
        self.p = project
        self.timeh = th
        self.flag = 0
        self.t = 0

    def _start(self):
        '''Gets the first time.'''
        self.t = time.time()
        self.flag = 1

    def _stop(self):
        '''Gets the second time and takes away the first.'''
        t = int(time.time() - self.t)
        self.flag = 0
        d = int(datetime.datetime.now().strftime("%Y%m%d")) #time
        self.timeh.update(self.p, t, d)

    def click(self):
        if self.flag:
            self._stop()
        else:
            self._start()
        return self.flag

#* Timer Class *********************************************************
class Timer(object):
    '''Timer class allows multiple things to be timed and recorded in SQL.'''
    def __init__(self, path):
        self.timeh = ncore.TimeHandler(dbpath=path) #timehandler
        self.d = {} #Holds the different projects

    def newtimer(self, project):
        '''Returns the stop/go for command'''
        if project not in self.d:
            self.d[project] = ProjectTime(project, self.timeh)
        return self.d[project].click

    def summary(self, m):
        TimeSummary(th=self.timeh, master=m, title="Time")
