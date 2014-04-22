import sqlite3

class noteCore(object):
    '''Deals with individual notes and projects through a sql interface'''
    def __init__(self, dbpath=None):
        if dbpath:
            self.db = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.db + "/db/notes.db")
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
    
    def print_project(self, project, date=None, time=None):
        '''Returns a project (date and time optional)'''
        if date == None and time == None:
            return self.c.execute("SELECT * FROM notes WHERE project=?",
                                  (project,))
        if date!=None and time==None:
            return self.c.execute("SELECT * FROM notes WHERE project=? AND date >= ?", [project, date])
        return self.c.execute("SELECT * FROM notes WHERE project=? AND date >= ? AND time>?", [project, date, time])

    def print_project_day(self, project, date):
        return self.c.execute("SELECT * FROM notes WHERE project=? AND date=?",
                              [project, date])
        
    def save(self):
        '''Commits the database.'''
        self.conn.commit()
    
    def note_in(self, project, text, date, time):
        '''Takes date, time, project, and text and submits it to the sql.'''
        q = """SELECT note FROM notes WHERE project=? AND date=? AND time=?"""
        self.c.execute(q, [project, date, time])
        s = self.c.fetchone()
        if s:
            text = s[0] + '\n' + text #Adds text if the minute already exists.
            q = """UPDATE notes
SET note=? WHERE project=? AND date=? AND time=?"""
            self.c.execute(q, [text, project, date, time])
        else:
            self.c.execute("INSERT INTO notes VALUES (?,?,?,?)",
                           [date, time, project, text])
        self.save()
        
    def get_all_projects(self):
        '''Returns a list of distinct projects.'''
        return [r[0] for r in self.c.execute("SELECT DISTINCT project FROM notes")]

    def get_all_dates(self, project=None):
        '''Returns a list of all distinct dates'''
        if project:
            self.c.execute("SELECT DISTINCT date FROM notes WHERE project=?",
                           [project])
            return [r[0] for r in self.c.fetchall()]
        else:
            self.c.execute("SELECT DISTINCT date FROM notes")
            return [r[0] for r in self.c.fetchall()]

#* Archived project handling **********************************************
    def load_archive(self):
        f = open(self.db + '/db/archive.txt', 'r')
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
        f = open(self.db + '/db/archive.txt', 'w')
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

#* Time Handling *********************************************************
class timehandler(object):
    '''Facilitates tracking time and displaying time tracked via sql.'''
    def __init__(self, dbpath=None):
        if dbpath:
            self.db = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.db + "/db/time.db")
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
                self.c.execute("UPDATE times SET seconds=? WHERE project=? AND date=?", [time, project, date])
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
