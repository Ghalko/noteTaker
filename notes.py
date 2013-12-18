import tkSimpleDialog
from Tkinter import *
import ncore  #note core sql
import timer  #Timer 
import sys
import datetime

class Search(object):
    '''This is a dialog for searching through notes.'''
    def __init__(self, master=None, title=None, nc=None):
        '''Must have master, and ncore, title is optional.'''
        if master == None or nc == None:
            return
        self.nc = nc #ncore, the database to search through
        self.b = None #beginning date
        self.e = None #end date
        self.p = None #project
        self.s = None #search term
        self.mp = Toplevel(master)
        self.mp.transient(master)
        self.mp.bind("<Return>", self._search)
        self.mp.bind("<Escape>", self._cancel)
        if title:
            self.mp.title(title)
        f = Frame(self.mp)         #Sets up the fields.
        f.pack(side=LEFT)
        self.d = Text(self.mp, height=10, width=80, wrap=WORD,
                      bg='sea green', spacing1=5) #Display
        begf = Frame(self.mp) #beginning date (inclusive)
        begf.pack(side=TOP)
        Label(begf, text='Begin: ').pack(side=LEFT)
        self.be = Entry(begf)
        self.be.pack(side=RIGHT)
        endf = Frame(self.mp) #ending date (inclusive)
        endf.pack(side=TOP)
        Label(endf, text='End:   ').pack(side=LEFT)
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
        self.d.pack_forget()
        
    def _search(self, event=None):
        self.b = self.be.get()
        self.e = self.ee.get()
        self.p = self.pe.get()
        self.s = self.se.get()
        if self.b:
            self.b = int(self.b)
        if self.e:
            self.e = int(self.e)
        if self.p:
            for row in self.nc.ret_notes(self.s, self.b, self.e, self.p):
                s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2]) + '\n'
                self.d.insert(END, s)
        else:
            for row in self.nc.ret_notes(self.s, self.b, self.e, self.p):
                s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2]) + ' ' + str(row[3]) + '\n'
                self.d.insert(END, s)
        self.d.pack(side=RIGHT)

    def _cancel(self, event=None):
        self.mp.destroy()

#**************************************************************************
class LBChoice(object):
    '''This is a listbox for returning projects to be unarchived.'''
    def __init__(self, master=None, title=None, li=[]):
        '''Must have master, title is optional, li is too.'''
        self.m = master
        self.v = None
        self.l = li[:]
        if self.m:
            self.mp = Toplevel(self.m)
        else:
            return
        self.mp.transient(self.m)
        self.mp.grab_set()
        self.mp.bind("<Return>", self._choose)
        self.mp.bind("<Escape>", self._cancel)
        if title:
            self.mp.title(title)
        lf = Frame(self.mp)         #Sets up the list.
        lf.pack(side=TOP)
        scrollBar = Scrollbar(lf)
        scrollBar.pack(side=RIGHT, fill=Y)
        self.lb = Listbox(lf, selectmode=SINGLE)
        self.lb.pack(side=LEFT, fill=Y)
        scrollBar.config(command=self.lb.yview)
        self.lb.config(yscrollcommand=scrollBar.set)
        self.l.sort()
        for item in self.l:
            self.lb.insert(END, item)     #Inserts items into the list.
        bf = Frame(self.mp)
        bf.pack(side=BOTTOM)
        choose = Button(bf, text="Select", command=self._choose)
        choose.pack(side=LEFT)
        cancel = Button(bf, text="Cancel", command=self._cancel)
        cancel.pack(side=RIGHT)
        
    def _choose(self, event=None):
        try:
            firstIndex = self.lb.curselection()[0]
            self.v = self.l[int(firstIndex)]
        except IndexError:
            self.v = None
        self.mp.destroy()

    def _cancel(self, event=None):
        self.mp.destroy()
        return None
        
    def returnValue(self):
        self.m.wait_window(self.mp)
        return self.v

#***********************************************************************
class projArea(object):
    '''Main area for note taking and skimming. Also has time button.'''
    def __init__(self, parent, title, tcmd):
        self.remove = parent.rproject   #Remove function
        self.move = parent.move         #Move function
        self.nc = parent.nc
        self.t = title
        self.tcmd = tcmd
        self.lock = 0
        self.going = PhotoImage(file=path+"/going.gif")
        self.stopped = PhotoImage(file=path+"/stopped.gif")
        self.pdate = None
        self.ptime = None
        self.f = Frame(parent.f, relief=RAISED, borderwidth=2)
        f2 = Frame(self.f)
        f2.pack()
        Button(f2, text='Lock', command=self.ul).pack(side=LEFT)
        l = Label(f2, text=title, width=37, font=("Helvetica", 16))
        l.pack(side=LEFT)
        l.bind("<Button-1>", self._click)
        self.b = Button(f2, image=self.stopped, command=self._timer)
        self.b.pack(side=LEFT)
        Button(f2, text='X', command=self.close).pack(side=LEFT)
        self.prev()
        self.entry = Text(self.f, width=80, height=10, bg='white', wrap=WORD)
        self.entry.bind("<Shift-Key-Return>", self.commit_note)
        self.entry.bind("<Control-Key-Return>", self._refresh)
        self.f.pack()

    def _update(self, date, time):
        for row in self.nc.print_project(self.t, self.pdate, self.ptime):
            s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[3]) + '\n'
            self.p.insert(END, s)
        self.p.yview(END)
        self.pdate = date
        self.ptime = time
        
    def prev(self):
        self.f1 = Frame(self.f)
        scrollbar = Scrollbar(self.f1)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.p = Text(self.f1, height=10, width=77, wrap=WORD, bg='light blue', spacing1=5)
        self.p.pack()
        self.p.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.p.yview)
        self._refresh()
                
    def _refresh(self, event=None):
        self.p.delete('1.0', END)
        for row in self.nc.print_project(self.t):
            s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[3]) + '\n'
            self.p.insert(END, s)
        self.p.yview(END)

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
            
    def ul(self):
        if self.lock == 0:
            self.lock = 1
        else:
            self.lock = 0
        
    def commit_note(self, event):
        s = self.entry.get('1.0',END).strip()
        if s == "":
            return
        t = datetime.datetime.now() #time
        d = int(t.strftime("%Y%m%d"))
        t = int(t.strftime("%H%M"))
        self.nc.note_in(self.t, s, d, t)
        self.entry.delete('1.0', END)
        self._update(d, t)

    def _timer(self):
        temp = self.tcmd()
        if temp:
            self.b.config(image=self.going)
        else:
            self.b.config(image=self.stopped)
        self.b.pack()

    def close(self):
        self.remove(self.t)
        self.nc.archive(self.t)
        self.f.pack_forget()
        self.f.destroy()
        
#*********************************************************************
class noteGui(Frame):
    def __init__(self, master=None, path=None):
        master.protocol("WM_DELETE_WINDOW", self.exit)
        self.m = master
        self.path = path
        self.f = Frame.__init__(self, master)
        self.pack()
        self.nc = ncore.noteCore(dbpath=self.path) #noteCore
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
            self.d[u] = projArea(self, u, t)
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
                self.d[ans] = projArea(self, ans, t)
                self.sl.append(ans)
                
    def oproject(self):
        '''Opens a previously closed project.'''
        p = LBChoice(master=self.m, title='Open',
                     li=self.nc.get_archive()).returnValue()
        if p == None:
            return
        t = self.t.newtimer(p)
        self.d[p] = projArea(self, p, t)
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
    app = noteGui(master=root, path=path)
    app.mainloop()
