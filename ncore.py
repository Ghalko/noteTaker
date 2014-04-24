"""Takes care of sqlite interactions with the database."""

import sqlite3

class NoteCore(object):
    """Deals with individual notes and projects through a sql interface"""
    def __init__(self, dbpath=None):
        if dbpath:
            self.db = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.db + "/db/notes.db")
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.archive = []
        self.load_archive()
        query = "CREATE TABLE notes (date INTEGER, time INTEGER, project, note)"
        try:
            self.cur.execute(query)
        except sqlite3.Error, e:
            print "--- %s:" % e.args[0]

    def ret_notes(self, search=None, b_date=None, e_date=None,
                  project=None, date=None, time=None):
        """Takes a search, (beginning, end, and project optional)"""
        query = "SELECT"
        qlist = []
        search_str = "WHERE"
        and_ = "" #gets set after the first argument to AND.
        if search is not None:
            search_str = "WHERE note LIKE ?"
            qlist.append('%'+search+'%')
            and_ = "AND"
        if project is None:
            #If no project then include project in output.
            query = ' '.join([query, "project,date,time,note FROM notes"])
            query = ' '.join([query, search_str])
        else:
            #Otherwise leave out project and use it to search.
            query = ' '.join([query, "date,time,note FROM notes"])
            query = ' '.join([query, search_str, and_, "project=?"])
            qlist.append(project)
            and_ = "AND"
        if b_date is not None:
            #beginning date
            query = ' '.join([query, and_, "date>=?"])
            qlist.append(b_date)
            and_ = "AND"
        if e_date is not None:
            #ending date
            query = ' '.join([query, and_, "date<=?"])
            qlist.append(e_date)
            and_ = "AND"
        if date is not None:
            #Specific date probably not used with b_date or e_date
            query = ' '.join([query, and_, "date=?"])
            qlist.append(date)
            and_ = "AND"
        if time is not None:
            #Specific time
            query = ' '.join([query, and_, "time=?"])
            qlist.append(time)
            and_ = "AND"
        query = ' '.join(query.split()) #remove extra whitespace.
        return self.cur.execute(query, qlist)

    def print_project_day(self, project, date):
        return self.ret_notes(project=project, date=date)

    def save(self):
        '''Commits the database.'''
        self.conn.commit()

    def note_in(self, project, text, date, time):
        '''Takes date, time, project, and text and submits it to the sql.'''
        previous = self.ret_notes(project=project, date=date, time=time)
        prev_note = previous.fetchone()
        if prev_note is not None:
            text = prev_note[2] + '\n' + text #Add if the minute already exists.
            query = """UPDATE notes SET note=?
WHERE project=? AND date=? AND time=?"""
            self.cur.execute(query, [text, project, date, time])
        else:
            self.cur.execute("INSERT INTO notes VALUES (?,?,?,?)",
                             [date, time, project, text])
        self.save()

    def get_all_projects(self):
        '''Returns a list of distinct projects.'''
        query = "SELECT DISTINCT project FROM notes"
        return [r[0] for r in self.cur.execute(query)]

    def get_all_dates(self, project=None):
        '''Returns a list of all distinct dates'''
        if project is not None:
            self.cur.execute("SELECT DISTINCT date FROM notes WHERE project=?",
                           [project])
            return [r[0] for r in self.cur.fetchall()]
        else:
            self.cur.execute("SELECT DISTINCT date FROM notes")
            return [r[0] for r in self.cur.fetchall()]

#* Archived project handling **********************************************
    def load_archive(self):
        f = open(self.db + '/db/archive.txt', 'r')
        for line in f:
            self.archive.append(line.strip())
        f.close()

    def get_archive(self):
        return self.archive

    def get_unarchived(self):
        ans = []
        for p in self.get_all_projects():
            if p not in self.archive:
                ans.append(p)
        return ans

    def set_archive(self):
        f = open(self.db + '/db/archive.txt', 'w')
        for i in self.archive:
            i = i + '\n'
            f.write(i)
        f.close()

    def archive(self, p):
        self.archive.append(p)
        self.set_archive()

    def unarchive(self, p):
        self.archive.remove(p)
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
        self.cur = self.conn.cursor()
        try:
            query = """CREATE TABLE times
(project, date INTEGER, seconds INTEGER)"""
            self.cur.execute(query)
        except:
            pass

    def update(self, project, time, date, replace=None):
        previous = self.ret_notes(project=project, date=date)
        prev_time = previous.fetchone()
        if prev_time is None:
            self.cur.execute("INSERT INTO times VALUES (?,?,?)",
                           [project, date, time])
        else:
            if replace:
                query = "UPDATE times SET seconds=? WHERE project=? AND date=?"
                self.cur.execute(query, [time, project, date])
            else:
                time = time + prev_time[1]
                query = "UPDATE times SET seconds=? WHERE project=? AND date=?"
                self.cur.execute(query, [time, project, date])
        self.conn.commit()

    def ret_notes(self, b_date=None, e_date=None, project=None, date=None):
        '''Takes a search, (beginning, end, and project optional)'''
        query = "SELECT"
        qlist = []
        and_ = "" #gets set after the first argument to AND.
        if project is None:
            #If no project then include project in output.
            query = ' '.join([query, "project,date,seconds FROM times"])
            query = ' '.join([query, "WHERE"])
        else:
            #Otherwise leave out project and use it to search.
            query = ' '.join([query, "date,seconds FROM times"])
            query = ' '.join([query, "WHERE project=?"])
            qlist.append(project)
            and_ = "AND"
        if b_date is not None:
            #beginning date
            query = ' '.join([query, and_, "date>=?"])
            qlist.append(b_date)
            and_ = "AND"
        if e_date is not None:
            #ending date
            query = ' '.join([query, and_, "date<=?"])
            qlist.append(e_date)
            and_ = "AND"
        if date is not None:
            #Specific date probably not used with b_date or e_date
            query = ' '.join([query, and_, "date=?"])
            qlist.append(date)
            and_ = "AND"
        query = ' '.join(query.split()) #remove extra whitespace.
        return self.cur.execute(query, qlist)
