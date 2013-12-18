from Tkinter import *
import time
import datetime
import ncore

#*************************************************************************
class tsummary(object):
    '''For retrieving time data from the data base. And possibly updating.'''
    def __init__(self, th=None, master=None, title=None):
        self.m = master
        self.th = th
        self.b = None #beginning date
        self.e = None #end date
        self.p = None #project
        self.r = IntVar() #to replace or not.
        self.d = {} #dictionary of projects
        if not self.m:
            return
        self.mp = Toplevel(self.m)
        self.mp.transient(self.m)
        self.mp.bind("<Return>", self._search)
        self.mp.bind("<Escape>", self._cancel)
        if title:
            self.mp.title(title)
        #****
        self.f = Frame(self.mp)
        self.f.pack(side=BOTTOM)
        begf = Frame(self.mp) #beginning date
        begf.pack(side=TOP)
        self.bl = Label(begf, text='Begin: ')  #Begin Label
        self.bl.pack(side=LEFT)
        self.be = Entry(begf)
        self.be.pack(side=RIGHT)
        endf = Frame(self.mp)  #end date
        endf.pack(side=TOP)
        self.el = Label(endf, text='End:   ') #End Label
        self.el.pack(side=LEFT)
        self.ee = Entry(endf)
        self.ee.pack(side=RIGHT)
        pf = Frame(self.mp)  #project
        pf.pack(side=TOP)
        Label(pf, text='Project:').pack(side=LEFT)
        self.pe = Entry(pf)
        self.pe.pack(side=RIGHT)
        bf = Frame(self.mp)
        bf.pack(side=TOP)
        self.sb = Button(bf, text="Search", command=self._search) #Search Button
        self.sb.pack(side=LEFT)
        cancel = Button(bf, text="Cancel", command=self._cancel)
        cancel.pack(side=RIGHT)
        Checkbutton(self.mp, text="Replace", variable=self.r,
                    command=self._switch).pack(side=TOP)

    def _switch(self, event=None):
        '''Switches to the replacement view when checked and back
        when unchecked.'''
        if self.r == 1:
            self.bl.config(text="Date: ")
            self.el.config(text="New:  ")
            self.sb.config(text="Replace", command=self._replace)
        else:
            self.bl.config(text="Begin: ")
            self.el.config(text="End:   ")
            self.sb.config(text="Search", command=self._search)

    def _replace(self, event=None):
        '''Gets date, new time and Project and replaces the time.'''
        self.b = self.be.get() #Date
        self.e = self.ee.get() #New time
        self.p = self.pe.get() #project
        if self.b == None or self.e == None or self.p == None:
            print "Need all three."
            return
        self.th.update(self.p, self.e, self.b, replace=1)
        

    def _search(self, event=None):
        self.b = self.be.get()
        self.e = self.ee.get()
        self.p = self.pe.get()
        for e in self.d:
            self.d[e].clear()
        if self.b:
            self.b = int(self.b)
        if self.e:
            self.e = int(self.e)
        if self.p:
            if self.p not in self.d:
                self.d[self.p] = tsdisp(self.f, self.p)
            for row in self.th.ret_notes(self.b, self.e, self.p):
                self.d[self.p].append(row[0], row[1])
            self.d[self.p].update()
        else:
            for row in self.th.ret_notes(self.b, self.e, self.p):
                if row[0] not in self.d:
                    self.d[row[0]] = tsdisp(self.f, row[0])
                self.d[row[0]].append(row[1], row[2])
                self.d[row[0]].update()

    def _cancel(self, event=None):
        self.d = {}
        self.mp.destroy()

#***********************************************************************
class tsdisp(object):
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
        self.f.pack_forget()

#* Project Timer *******************************************************
class projTime(object):
    '''A timer for a project'''
    def __init__(self, project, th):
        self.p = project
        self.th = th
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
        self.th.update(self.p, t, d)

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
        self.th = ncore.timehandler(dbpath=path) #timehandler
        self.d = {} #Holds the different projects

    def newtimer(self, project):
        '''Returns the stop/go for command'''
        if project not in self.d:
            self.d[project] = projTime(project, self.th)
        return self.d[project].click

    def summary(self, m):
        tsummary(th=self.th, master=m, title="Time")
