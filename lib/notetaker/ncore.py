"""Takes care of sqlite interactions with the database."""

import sqlite3
from os.path import isfile

class DatabaseHandler(object):
    """DatabaseHandler handles the databases"""
    def __init__(self, dbpath=None):
        if dbpath:
            self.dbpath = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.dbpath)
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        qlist = None
        query = "CREATE TABLE notes (date INTEGER, time INTEGER, project, note)"
        self.insert(query, qlist)
        query = "CREATE TABLE times (project, date INTEGER, seconds INTEGER)"
        self.insert(query, qlist)
        query = "CREATE TABLE archive (project)"
        self.insert(query, qlist)

    def select(self, query, qlist):
        try:
            return self.cur.execute(query, qlist)
        except sqlite3.Error, error:
            print "-s- %s" % error.args[0]

    def insert(self, query, qlist):
        try:
            self.cur.execute(query, qlist)
        except sqlite3.Error, error:
            print "-s- %s" % error.args[0]

    def query_exists(self, query, qlist):
        """Return query if it exists"""
        pass

    def save(self):
        '''Commit the database.'''
        self.conn.commit()        


class NoteQuery(object):
    """NoteQuery builds queries and returns values"""
    def __init__(self, dbdict=None):
        if dbdict is None:
            print "Requires handler of databases."
            return 1
        self.dbdict = dbdict

    def build_select(self, search=None, b_date=None, e_date=None,
                     project=None, date=None, time=None):
        """Take optional arguments, build query and return results.
        - search - term to search for in notes
        - b_date, e_date - beggining and ending date
        - project - title
        - date, time - specific date and/or time
        """
        query = "SELECT"
        qlist = []
        search_str = "WHERE"
        and_ = "" #gets set after the first argument to AND.
        if search is not None:
            search_str = "WHERE note LIKE ?"
            qlist.append('%'+search+'%')
            and_ = "AND"
        if project is None:
            #If no project then simple.
            query = ' '.join([query, "project,date,time,note FROM notes"])
            query = ' '.join([query, search_str])
        elif project.find(",") != -1:
            #Parse comma and space delimited list, print project
            query = ' '.join([query, "project,date,time,note FROM notes"])
            temp_list = project.split(", ")
            p_list = []
            for each in temp_list:
                p_list.append("project=?")
            p_str = " OR ".join(p_list)
            p_str = "(" + p_str + ")"
            query = ' '.join([query, search_str, and_, p_str])
            qlist = qlist + temp_list
            and_ = "AND"
        else:
            #Leave out project and use it to search.
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
        query = query + " ORDER BY date,time"
        query = ' '.join(query.split()) #remove extra whitespace.
        return (query, qlist)

    def project_day(self, project, date):
        return self.build_select(project=project, date=date)

    def project_time(self, project, date, time):
        return self.build_select(project=project, date=date, time=time)


class NoteCore(object):
    """Open sql database. Provide functions to read and write.
    Main functionality note_in and ret_notes.
    """
    def __init__(self, dbpath=None):
        if dbpath:
            self.dbpath = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.dbpath)
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.archive_file = None
        self.archive = []
        self.load_archive()
        query = "CREATE TABLE notes (date INTEGER, time INTEGER, project, note)"
        try:
            self.cur.execute(query)
        except sqlite3.Error, error:
            print "--- %s:" % error.args[0]

    def ret_notes(self, search=None, b_date=None, e_date=None,
                  project=None, date=None, time=None):
        """Take optional arguments, build query and return results.
        - search - term to search for in notes
        - b_date, e_date - beggining and ending date
        - project - title
        - date, time - specific date and/or time
        """
        query = "SELECT"
        qlist = []
        search_str = "WHERE"
        and_ = "" #gets set after the first argument to AND.
        if search is not None:
            search_str = "WHERE note LIKE ?"
            qlist.append('%'+search+'%')
            and_ = "AND"
        if project is None:
            #If no project then simple.
            query = ' '.join([query, "project,date,time,note FROM notes"])
            query = ' '.join([query, search_str])
        elif project.find(",") != -1:
            #Parse comma and space delimited list, print project
            query = ' '.join([query, "project,date,time,note FROM notes"])
            temp_list = project.split(", ")
            p_list = []
            for each in temp_list:
                p_list.append("project=?")
            p_str = " OR ".join(p_list)
            p_str = "(" + p_str + ")"
            query = ' '.join([query, search_str, and_, p_str])
            qlist = qlist + temp_list
            and_ = "AND"
        else:
            #Leave out project and use it to search.
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
        query = query + " ORDER BY date,time"
        query = ' '.join(query.split()) #remove extra whitespace.
        return self.cur.execute(query, qlist)

    def print_project_day(self, project, date):
        """Return specific day from a project."""
        return self.ret_notes(project=project, date=date)

    def save(self):
        '''Commit the database.'''
        self.conn.commit()

    def note_in(self, project, text, date, time):
        '''Take project, text, date, time and submit it to the database.'''
        previous = self.ret_notes(project=project, date=date, time=time)
        prev_note = previous.fetchone()
        if prev_note is not None:
            text = prev_note[2] + '\n' + text #Add if minute already exists.
            query = """
            UPDATE notes SET note=?
            WHERE project=? AND date=? AND time=?
            """
            self.cur.execute(query, [text, project, date, time])
        else:
            self.cur.execute("INSERT INTO notes VALUES (?,?,?,?)",
                             [date, time, project, text])
        self.save()

    def get_all_projects(self):
        '''Return a list of distinct projects.'''
        query = "SELECT DISTINCT project FROM notes"
        return [r[0] for r in self.cur.execute(query)]

    def get_all_dates(self, project=None):
        '''Return a list of all distinct dates'''
        if project is not None:
            self.cur.execute("SELECT DISTINCT date FROM notes WHERE project=?",
                           [project])
            return [r[0] for r in self.cur.fetchall()]
        else:
            self.cur.execute("SELECT DISTINCT date FROM notes")
            return [r[0] for r in self.cur.fetchall()]

#* Archived project handling **********************************************
    def load_archive(self):
        """Load archived project titles from text file."""
        temp_path = "/".join(self.dbpath.split("/")[:-1])
        self.archive_file = temp_path + '/archive.txt'
        if isfile(self.archive_file) != True:
            return
        with open(self.archive_file, 'r') as open_file:
            for line in open_file:
                self.archive.append(line.strip())

    def get_archive(self):
        """Return archive list."""
        return self.archive

    def get_unarchived(self):
        """Return list of unarchived projects."""
        ans = []
        for project in self.get_all_projects():
            if project not in self.archive:
                ans.append(project)
        return ans

    def set_archive(self):
        """Write archive to file."""
        with open(self.archive_file, 'w') as open_file:
            for i in self.archive:
                i = i + '\n'
                open_file.write(i)

    def archive_project(self, project):
        """Append project to archive list and save archive."""
        self.archive.append(project)
        self.set_archive()

    def unarchive(self, project):
        """Removes title from archive list."""
        self.archive.remove(project)
        self.set_archive()


#* Time Handling *********************************************************
class TimeHandler(object):
    '''Facilitates tracking time and displaying time tracked via sql.'''
    def __init__(self, dbpath=None):
        if dbpath:
            self.dbpath = dbpath
        else:
            print "Need path to database directory."
            return
        self.conn = sqlite3.connect(self.dbpath)
        self.cur = self.conn.cursor()
        try:
            query = """CREATE TABLE times
(project, date INTEGER, seconds INTEGER)"""
            self.cur.execute(query)
        except sqlite3.Error, error:
            print "--- %s:" % error.args[0]

    def update(self, project, time, date, replace=None):
        """Update a time for a project on a specific date.
        If replace is true then replace time.
        """
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
        """Take optional arguments, build a query, return results.
        - b_date, e_date - beggining and ending date.
        - project - title
        - date - specific date
        """
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
