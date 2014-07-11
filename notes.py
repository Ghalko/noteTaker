import tkSimpleDialog
from Tkinter import (Tk, Menu, Frame, Label, Button, PhotoImage, Text, Entry,
                     Scrollbar, Toplevel, Listbox, RAISED, RIGHT, LEFT, WORD,
                     Y, END, BOTTOM, TOP, X, SINGLE)
import ncore  #note core sql
import timer  #Timer
from days import Days #main display idea.
import sys
import datetime
from utils import GeneralQuery

class Search(object):
    """This is a dialog for searching through notes."""
    def __init__(self, master=None, title=None, nc=None):
        """Must have master, and ncore, title is optional."""
        if master == None or nc ==None:
            return
        self.master = master
        self.nc = nc #ncore, the database to search through
        self.mlist = ["Begin", "End", "Project", "Phrase"]
        self.command = self.search
        genq = GeneralQuery(parent=self)
        self.frame = genq.get_frame()
        self.disp = Text(self.frame, height=10, width=80, wrap=WORD,
                      bg="#008888", spacing1=5)
        self.disp.pack()

    def search(self, list_):
        self.disp.delete('1.0', END)
        beg = list_[0].strip()
        end = list_[1].strip()
        project = list_[2].strip()
        search = list_[3] #can search for things with trailing spaces.
        if search == "":
            self.disp.insert(END, "None")
        if beg != "":
            beg = int(beg)
        else:
            beg = None
        if end != "":
            end = int(end)
        else:
            end = None
        if project == "":
            project = None
        for row in self.nc.ret_notes(search=search, b_date=beg,
                                     e_date=end, project=project):
            #Changes ints to strings and concats
            s = ' '.join([str(r) for r in row]) + "\n"
            self.disp.insert(END, s)
        self.disp.pack()

#**************************************************************************
class LBChoice(object):
    '''This is a listbox for returning projects to be unarchived.'''
    def __init__(self, list_=None, master=None, title=None):
        '''Must have master, title is optional, li is too.'''
        self.master = master
        if self.master is not None:
            self.top = Toplevel(self.master)
        else:
            return
        self.v = None
        if list_ is None or not isinstance(list_, list):
            self.list = []
        else:
            self.list = list_[:]
        self.top.transient(self.master)
        self.top.grab_set()
        self.top.bind("<Return>", self._choose)
        self.top.bind("<Escape>", self._cancel)
        if title:
            self.top.title(title)
        lf = Frame(self.top)         #Sets up the list.
        lf.pack(side=TOP)
        scroll_bar = Scrollbar(lf)
        scroll_bar.pack(side=RIGHT, fill=Y)
        self.lb = Listbox(lf, selectmode=SINGLE)
        self.lb.pack(side=LEFT, fill=Y)
        scroll_bar.config(command=self.lb.yview)
        self.lb.config(yscrollcommand=scroll_bar.set)
        self.list.sort()
        for item in self.list:
            self.lb.insert(END, item)     #Inserts items into the list.
        bf = Frame(self.top)
        bf.pack(side=BOTTOM)
        Button(bf, text="Select", command=self._choose).pack(side=LEFT)
        Button(bf, text="New", command=self._new).pack(side=LEFT)
        Button(bf, text="Cancel", command=self._cancel).pack(side=LEFT)

    def _choose(self, event=None):
        try:
            first = self.lb.curselection()[0]
            self.v = self.list[int(first)]
        except IndexError:
            self.v = None
        self.top.destroy()

    def _new(self, event=None):
        self.v = "NEW"
        self.top.destroy()

    def _cancel(self, event=None):
        self.top.destroy()

    def return_value(self):
        self.master.wait_window(self.top)
        return self.v


#***********************************************************************
class ProjectArea(object):
    '''Main area for note taking and skimming. Also has time button.'''
    def __init__(self, parent, title, tcmd):
        self.remove = parent.rproject   #Remove function
        self.move = parent.move         #Move function
        self.nc = parent.nc
        self.title = title
        self.tcmd = tcmd #passed in from timehandler
        self.lock = 0
        self.going = PhotoImage(file=path+"/going.gif")
        self.stopped = PhotoImage(file=path+"/stopped.gif")
        self.pdate = None
        self.f = Frame(parent.f, relief=RAISED, borderwidth=2)
        f2 = Frame(self.f)
        f2.pack()
        l = Label(f2, text=title, width=42, font=("Helvetica", 16))
        l.pack(side=LEFT)
        l.bind("<Button-1>", self._click)
        self.b = Button(f2, image=self.stopped, command=self._timer)
        self.b.pack(side=LEFT)
        Button(f2, text='X', command=self.close).pack(side=LEFT)
        self.prev()
        self.entry = Text(self.f1, width=80, height=10, bg='white', wrap=WORD)
        self.entry.bind("<Shift-Key-Return>", self.commit_note)
        self.entry.bind("<Control-Key-Return>", self.p.gui_refresh)
        self.f.pack()

    def prev(self):
        self.f1 = Frame(self.f)
        self.days = Days(master=self.f1, ncore=self.nc, project=self.title)
        self.p = self.days.get_current()

    def _click(self, event=None):
        self.move(title=self.title)

    def ent(self):
        self.f1.pack()
        self.entry.pack()
        self.entry.focus_set()

    def lv(self):
        if self.lock == 0:
            self.f1.pack_forget()
            self.entry.pack_forget()

    def commit_note(self, event=None, initial=None):
        if initial is not None:
            s = "Open"
        else:
            s = self.entry.get('1.0', END).strip()
        # Does not commit empty notes.
        if s == "":
            return
        t = datetime.datetime.now() #time
        d = int(t.strftime("%Y%m%d"))
        t = int(t.strftime("%H%M"))
        self.nc.note_in(self.title, s, d, t)
        self.entry.delete('0.0', END)
        self.entry.mark_set("insert", "%d.%d" % (1, 0))
        if d == self.p.date:
            self.p.gui_refresh()
        else:
            self.days.append(d)
            self.p = self.days.get_current()

    def _timer(self):
        """
        Timer button. Calls tcmd to start or stop the timer.
        Switches the images.
        """
        temp = self.tcmd()
        if temp:
            self.b.config(image=self.going)
        else:
            self.b.config(image=self.stopped)
        self.b.pack()

    def close(self):
        self.tcmd(close=1) #stops the timer when closing.
        self.remove(self.title)
        self.nc.archive_project(self.title)
        self.f.pack_forget()
        self.f.destroy()


#*********************************************************************
class NoteGUI(Frame):
    def __init__(self, master=None, path=None):
        master.protocol("WM_DELETE_WINDOW", self.exit)
        self.m = master
        self.path = path
        self.f = Frame.__init__(self, master)
        self.pack()
        self.nc = ncore.NoteCore(dbpath=self.path) #noteCore
        self.t = timer.Timer(self.path)
        self.d = {}
        self.sl = []  #ordered list of open projects.
        self.focus = 0 #current opened
        self.m.bind("<Shift-Button-5>", self.move)
        self.m.bind("<Shift-Button-4>", self.move)
        self.fillmw()

    def fillmw(self):
        menubar = Menu(self.f)
        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="New", command=self.nproject)
        filemenu.add_command(label="Open", command=self.oproject)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_command(label='Search', command=self.search)
        menubar.add_command(label='Time', command=self._time)
        self.m.config(menu=menubar)
        self.sl = self.nc.get_unarchived()
        for u in self.sl:
            t = self.t.newtimer(u)
            self.d[u] = ProjectArea(self, u, t)
        self.focus = "Other"

    def exit(self):
        for key,project in self.d.iteritems():
            project.tcmd(close=1) #Shutdown and stores all running timers.
            project.commit_note() #commit all uncommitted notes.
        self.m.destroy()

    def save(self):
        self.nc.save()
        self.nc.set_archive()

    def nproject(self):
        '''Starts a new project'''
        ans = tkSimpleDialog.askstring("Project", "New Project Name:",
                                       parent=self.m)
        if ans:
            if ans not in self.nc.get_all_projects():
                t = self.t.newtimer(ans)
                self.d[ans] = ProjectArea(self, ans, t)
                self.d[ans].commit_note(initial=1)
                self.sl.append(ans)

    def oproject(self):
        '''Opens a previously closed project. Has new option'''
        p = LBChoice(self.nc.get_archive(), master=self.m,
                     title='Open').return_value()
        if p is None:
            return
        elif p == "NEW":
            self.nproject()
            return
        t = self.t.newtimer(p)
        self.d[p] = ProjectArea(self, p, t)
        self.sl.append(p)
        self.nc.unarchive(p)

    def rproject(self, title):
        '''Removes project from project list, self.sl'''
        self.sl.remove(title)

    def search(self):
        Search(self.m, 'Search', nc=self.nc)

    def _time(self):
        self.t.summary(self.m)

    def move(self, event=None, title=None):
        self.d[self.focus].lv()
        i = 0
        if event: #Shift+scroll
            if event.num == 5: #Scroll down
                i = self.sl.index(self.focus) + 1
                if i >= len(self.sl):
                    i = 0
            elif event.num == 4: #Scroll up
                i = self.sl.index(self.focus) - 1
                if i < 0:
                    i = len(self.sl) - 1
        elif title: #Click
            i = self.sl.index(title)
        self.focus = self.sl[i] #Setting new focus
        self.d[self.focus].ent() #Entering focus

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Needs -path <path to db>"
        sys.exit()

    pflag = 0
    path = None
    for a in sys.argv:
        if pflag:
            path = str(a)
            pflag = 0
        elif str(a) == '-path':
            pflag = 1

    if not path:
        sys.exit()

    root = Tk()
    root.title("noteTaker")
    app = NoteGUI(master=root, path=path)
    app.mainloop()
