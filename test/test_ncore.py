import unittest
import random
import string
import sqlite3
import notetaker.ncore as ncore
import os

'''This test file is intended to test the database and the gui to a good extent.
This should:
  - create random entries with somewhat random timestamps.
  - Save entries to a text file for comparison.
  - Enter each entry into the database
  - search for some of the random terms.
  - Remove database after testing
  - Collect and show statistics throughout
  - Push buttons to see if there is a place where things break down.'''

class TestNoteCore(unittest.TestCase):
    def setUp(self, seed=None):
        self.filename = "test/note-test.db"
        with open(self.filename, 'a'):
            os.utime(self.filename, None)
        self.nc = ncore.NoteCore(dbpath=self.filename)
        self.sql = sqlite3.connect(self.filename)
        self.cur = self.sql.cursor()
        self.listed = [] #List of entries
        self.dates = [] #fill this in with dates.
        self.times = [] #fill in with times
        self.projects = [] #fill in with projects
        self.texts = [] #fill in with notes.
        self.seed = seed #To make random tests somewhat repeatable.
        if seed is None:
            self.seed = random.randint(1000000000, 9999999999)
        random.seed(self.seed)
        print "seed" + str(self.seed)
        self.fillrand()

    def tearDown(self):
        self.nc = None
        os.remove(self.filename)

    def test_note_in(self):
        """Tests that a note goes into the database."""
        for i in range(10):
            ent = self.randEntry()
            self.listed.append(ent)
            self.nc.note_in(ent[0], ent[1], ent[2], ent[3])
            self.cur.execute("SELECT * FROM notes WHERE project=? AND date=? AND time=?",
                             [ent[0], ent[2], ent[3]])
            row = self.cur.fetchone()
            self.assertEqual([row[0], row[1], str(row[2]), str(row[3])], [ent[2], ent[3], ent[0], ent[1]])

    def test_ret_notes(self):
        pass

    def randEntry(self):
        """Returns a random entry from generated lists"""
        ent = []
        ent.append(random.choice(self.projects))
        ent.append(random.choice(self.texts))
        ent.append(random.choice(self.dates))
        ent.append(random.choice(self.times))
        return ent

    def fillrand(self):
        for i in range(100):
            date = random.randint(10000000, 99999999)
            self.dates.append(date)
            hour = random.randint(0,23)
            minute = random.randint(0,59)
            self.times.append(int(str(hour) + str(minute)))
            project = ''.join(random.choice(string.ascii_letters + "# " + string.digits) for _ in range(random.randint(4, 30)))
            self.projects.append(project)
            text = ''.join(random.choice(string.ascii_letters + "#.,   " + string.digits) for _ in range(random.randint(4, 1000)))
            self.texts.append(text)
