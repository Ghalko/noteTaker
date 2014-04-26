import tkSimpleDialog
from Tkinter import (Tk, Menu, Frame, Label, Button, PhotoImage, Text, Entry,
                     Scrollbar, Toplevel, Listbox, RAISED, RIGHT, LEFT, WORD,
                     Y, END, BOTTOM, TOP, X, SINGLE)
import ncore  #note core sql
import timer  #Timer
from days import Days #main display idea.
import sys
import datetime

class Search(object):
    '''This is a dialog for searching through notes.'''
    def __init__(self, master=None, title=None, nc=None):
        '''Must have master, and ncore, title is optional.'''
        if master == None or nc == None:
            return
        self.nc = nc #ncore, the database to search through
        self.beg = None #beginning date
        self.end = None #end date
        self.pro = None #project
        self.search = None #search term
        self.build_search(master, title)

    def build_search(self, master, title):
        self.mp = Toplevel(master)
        self.mp.transient(master)
        self.mp.bind("<Return>", self._search)
        self.mp.bind("<Escape>", self._cancel)
        if title:
            self.mp.title(title)
        f = Frame(self.mp)         #Sets up the fields.
        f.pack(side=LEFT)
        self.d = Text(self.mp, height=10, width=80, wrap=WORD,
                      bg="#009999", spacing1=5) #Display
        self.d.pack(side=RIGHT)
        begf = Frame(self.mp) #beginning date (inclusive)
        begf.pack(side=TOP)
        Label(begf, text='Begin:  ').pack(side=LEFT)
        self.be = Entry(begf)
        self.be.pack(side=RIGHT)
        endf = Frame(self.mp) #ending date (inclusive)
        endf.pack(side=TOP)
        Label(endf, text='End:    ').pack(side=LEFT)
        self.ee = Entry(endf)
        self.ee.pack(side=RIGHT)
        pf = Frame(self.mp) #project
        pf.pack(side=TOP)
        Label(pf, text='Project:').pack(side=LEFT)
        self.pe = Entry(pf)
        self.pe.pack(side=RIGHT)
        self.se = Entry(self.mp) #search term entry
        self.se.pack(side=TOP, fill=X)
        bf = Frame(self.mp)
        bf.pack(side=TOP)
        search = Button(bf, text="Search", command=self._search)
        search.pack(side=LEFT)
        cancel = Button(bf, text="Cancel", command=self._cancel)
        cancel.pack(side=RIGHT)
        clear = Button(bf, text="Clear", command=self._clear)
        clear.pack(side=LEFT)

    def _clear(self):
        self.d.delete('1.0', END)

    def _search(self, event=None):
        self.d.delete('1.0', END)
        self.beg = self.be.get().strip()
        self.end = self.ee.get().strip()
        self.pro = self.pe.get().strip()
        self.search = self.se.get() #can search for things with trailing spaces.
        if self.search == "":
            self.d.insert(END, "None")
        if self.beg != "":
            self.beg = int(self.beg)
        else:
            self.beg = None
        if self.end != "":
            self.end = int(self.end)
        else:
            self.end = None
        if self.pro != "":
            for row in self.nc.ret_notes(search=self.search, b_date=self.beg,
                                         e_date=self.end, project=self.pro):
                s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2]) + '\n'
                self.d.insert(END, s)
        else:
            for row in self.nc.ret_notes(search=self.search, b_date=self.beg,
                                         e_date=self.end):
                s = str(str(row[0]) + ' ' + str(row[1]) + ' ' +
                        str(row[2]) + ' ' + str(row[3]) + '\n')
                self.d.insert(END, s)
        self.d.pack(side=RIGHT)

    def _cancel(self, event=None):
        self.mp.destroy()

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
        choose = Button(bf, text="Select", command=self._choose)
        choose.pack(side=LEFT)
        cancel = Button(bf, text="Cancel", command=self._cancel)
        cancel.pack(side=RIGHT)

    def _choose(self, event=None):
        try:
            first = self.lb.curselection()[0]
            self.v = self.list[int(first)]
        except IndexError:
            self.v = None
        self.top.destroy()

    def _cancel(self, event=None):
        self.top.destroy()
        return None

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
        self.t = title
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
        self.days = Days(master=self.f1, ncore=self.nc, project=self.t)
        self.p = self.days.get_current()

    def _click(self, event):
        self.move(title=self.t)

    def ent(self): #, event):
        self.f1.pack()
        self.entry.pack()
        self.entry.focus_set()

    def lv(self): #, event):
        if self.lock == 0:
            self.f1.pack_forget()
            self.entry.pack_forget()

    def commit_note(self, event):
        s = self.entry.get('1.0', END).strip()
        if s == "":
            return
        t = datetime.datetime.now() #time
        d = int(t.strftime("%Y%m%d"))
        t = int(t.strftime("%H%M"))
        self.nc.note_in(self.t, s, d, t)
        self.entry.delete('0.0', END)
        self.entry.mark_set("insert", "%d.%d" % (1, 0))
        if d == self.p.date:
            self.p.gui_refresh()
        else:
            self.days.append(d)
            self.p = self.days.get_current()

    def _timer(self):
        '''Timer button. Calls tcmd to start or stop the timer. Switches the
        images.'''
        temp = self.tcmd()
        if temp:
            self.b.config(image=self.going)
        else:
            self.b.config(image=self.stopped)
        self.b.pack()

    def close(self):
        self.remove(self.t)
        self.nc.archive_project(self.t)
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
                self.sl.append(ans)

    def oproject(self):
        '''Opens a previously closed project.'''
        p = LBChoice(self.nc.get_archive(), master=self.m,
                     title='Open').return_value()
        if p == None:
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
