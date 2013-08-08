import datetime
import sqlite3

class noteCore(object):
    '''Deals with individual notes and projects through a sql interface'''
    def __init__(self, dbpath=None):
        if dbpath:
            self.db = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.db + "/notes.db")
        self.conn.text_factory = str
        self.c = self.conn.cursor()
        self.a = []
        self.load_archive()
        try:
            self.c.execute("CREATE TABLE notes (date INTEGER, time INTEGER, project, note)")
        except sqlite3.Error, e:
            print "--- %s:" % e.args[0]
        
    def ret_notes(self, s, b=None, e=None, project=None):
        '''Takes a search, (beginning, end, and project optional)'''
        if b and e and project:
            return self.c.execute("SELECT date,time,note FROM notes WHERE note LIKE ? AND project=? AND date>=? AND date<=?", ['%'+s+'%', project, b, e])
        elif b and project:
            return self.c.execute("SELECT date,time,note FROM notes WHERE note LIKE ? AND project=? AND date>=?", ['%'+s+'%', project, b])
        elif e and project:
            return self.c.execute("SELECT date,time,note FROM notes WHERE note LIKE ? AND project=? AND date<=?", ['%'+s+'%', project, e])
        elif b and e:
            return self.c.execute("SELECT project,date,time,note FROM notes WHERE note LIKE ? AND date>=? AND date<=?", ['%'+s+'%', b, e])
        elif b:
            return self.c.execute("SELECT project,date,time,note FROM notes WHERE note LIKE ? AND date>=?", ['%'+s+'%', b])
        elif e:
            return self.c.execute("SELECT project,date,time,note FROM notes WHERE note LIKE ? AND date<=?", ['%'+s+'%', e])
        elif project:
            return self.c.execute("SELECT date,time,note FROM notes WHERE note LIKE ? AND project=?", ['%'+s+'%', project])
        else:
            return self.c.execute("SELECT project,date,time,note FROM notes WHERE note LIKE ?", ['%'+s+'%'])
    
    def print_note(self, note, output):
        print note
        pass
    
    def print_day(self, day):
        for row in self.c.execute("SELECT * FROM notes WHERE date=?", (day,)):
            print row[1], row[2], row[3]
    
    def print_project(self, project):
        return self.c.execute("SELECT * FROM notes WHERE project=?", (project,))
        
    
    def format_print(self, text):
        pass
    
    def save(self):
        self.conn.commit()
    
    def note_in(self, project, text, output):
        t = datetime.datetime.now() #time
        d = int(t.strftime("%Y%m%d"))
        t = int(t.strftime("%H%M"))
        self.c.execute("INSERT INTO notes VALUES (?,?,?,?)", (d, t, project, text,))
        self.save()
        
    def get_all_projects(self):
        return [r[0] for r in self.c.execute("SELECT DISTINCT project FROM notes")]
        
    def load_archive(self):
        f = open(self.db + '/archive.txt', 'r')
        for line in f:
            self.a.append(line.strip())
        f.close()
    
    def get_archive(self):
        return self.a
        
    def get_unarchived(self):
        ans = []
        for p in self.get_all_projects():
            if p not in self.a:
                ans.append(p)
        return ans
        
    def set_archive(self):
        f = open(self.db + '/archive.txt', 'w')
        for i in self.a:
            i = i + '\n'
            f.write(i)
        f.close()
        
    def archive(self, p):
        self.a.append(p)
        self.set_archive()
        
    def unarchive(self, p):
        self.a.remove(p)
        self.set_archive()

#*************************************************************************
class timehandler(object):
    def __init__(self, dbpath=None):
        if dbpath:
            self.db = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.db + "/time.db")
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

    def ret_notes(self, b=None, e=None, project=None):
        '''Takes a search, (beginning, end, and project optional)'''
        if b and e and project:
            return self.c.execute("SELECT date,seconds FROM times WHERE project=? AND date>=? AND date<=?", [project, b, e])
        elif b and project:
            return self.c.execute("SELECT date,seconds FROM times WHERE project=? AND date>=?", [project, b])
        elif e and project:
            return self.c.execute("SELECT date,seconds FROM times WHERE project=? AND date<=?", [project, e])
        elif b and e:
            return self.c.execute("SELECT project,date,seconds FROM times WHERE date>=? AND date<=?", [b, e])
        elif b:
            return self.c.execute("SELECT project,date,seconds FROM times WHERE date>=?", [b])
        elif e:
            return self.c.execute("SELECT project,date,seconds FROM times WHERE date<=?", [e])
        elif project:
            return self.c.execute("SELECT date,seconds FROM times WHERE project=?", [project])
