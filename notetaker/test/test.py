import utils
from Tkinter import *

def help():
    print '''This test file is intended to test the database and the gui to a good extent.
This should:
  - create random entries with somewhat random timestamps.
  - Save entries to a text file for comparison.
  - Enter each entry into the database
  - search for some of the random terms.
  - Remove database after testing
  - Collect and show statistics throughout
  - Push buttons to see if there is a place where things break down.'''

class DBTester(object):
    '''Tests input and searching the gui.'''
    def __init__(self):
        pass

    def randEntry(self):
        return -1

    def randTime(self):
        return -1

    def input(self): #inputs into text file and database
        e = self.randEntry()
        t = self.randTime()
        #add to text file
        #add to database
        return

    def search(self): #take a random word out of the text file and search
        pass

class GUITester(object):
    def __init__(self):
        pass

    def randp(self): #new project
        pass

    def archivep(self): #'x' project
        pass

    def openp(self): #open project
        pass

    def move(self):
        pass

class TimeTester(object):
    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def replace(self):
        pass


help()
