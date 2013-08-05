import time
import datetime
import Tkinter
import sqlite3

class timehandler(object):
    def __init__(self, db="db/time.db"):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        try:
            self.c.execute("CREATE TABLE times (project, date INTEGER, seconds INTEGER)")
        except:
            pass

    def update(self, project, time, date, replace=None):
        self.c.execute("SELECT seconds FROM times WHERE project=? AND date=?", [project, date])
        s = self.c.fetchone()
        if s == None:
            self.c.execute("INSERT INTO times VALUES (?,?,?)", [project, date, time])
        else:
            if replace:
                print "Replace not implemented"
                #self.c.execute("REPLACE INTO times VALUES (?,?,?)"
            else:
                time = time + s[0]
                self.c.execute("UPDATE times SET seconds=? WHERE project=? AND date=?", [time, project, date])
        self.conn.commit()

class ptime(object):
    '''Gets an event time, saves it to subtract from last event time.'''
    def __init__(self, button=None, project=None, th=None):
        if project == None or button == None or th == None:
            print "Class needs project, button and time handler";
            return
        self.p = project
        self.b = button
        self.th = th
        self.going = Tkinter.PhotoImage(file="/home/bgorges/Tools/noteTaker/python/going.gif")
        self.stopped = Tkinter.PhotoImage(file="/home/bgorges/Tools/noteTaker/python/stopped.gif")
        self.b.config(image=self.stopped)
        self.b.pack()
        self.flag = 0
        self.t = 0

    def _start(self):
        '''Gets the first time.'''
        self.t = time.time()
        self.flag = 1
        #button stuff
        self.b.config(image=self.going)
        self.b.pack()

    def _stop(self):
        '''Gets the second time and takes away the first.'''
        t = int(time.time() - self.t)
        self.flag = 0
        d = int(datetime.datetime.now().strftime("%Y%m%d")) #time
        self.th.update(self.p, t, d)
        #button stuff
        self.b.config(image=self.stopped)
        self.b.pack()

    def click(self):
        if self.flag:
            self._stop()
        else:
            self._start()
        
class tsummary(object):
    '''For retrieving time data from the data base. And possibly updating.'''
    def __init__(self, db="db/time.db"):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        try:
            self.c.execute("CREATE TABLE times (project, date INTEGER, seconds INTEGER)")
        except:
            pass

    def gui(self):
        pass
