import tkSimpleDialog
from Tkinter import *
import ncore
import ptime

class Search(object):
    '''This is a dialog for searching.'''
    def __init__(self, master=None, title=None, nc=None):
        '''Must have master, title is optional, li is too.'''
        self.m = master
        self.nc = nc
        self.b = None #beginning date
        self.e = None #end date
        self.p = None #project
        self.s = None #search term
        if not self.m:
            return
        self.mp = Toplevel(self.m)
        self.mp.transient(self.m)
        #self.mp.grab_set()
        self.mp.bind("<Return>", self._search)
        self.mp.bind("<Escape>", self._cancel)
        if title:
            self.mp.title(title)
        f = Frame(self.mp)         #Sets up the fields.
        f.pack(side=LEFT)
        self.d = Text(self.mp, height=10, width=80, wrap=WORD, bg='sea green', spacing1=5) #Display
        begf = Frame(self.mp)
        begf.pack(side=TOP) #beginning
        Label(begf, text='Begin: ').pack(side=LEFT)
        self.be = Entry(begf)
        self.be.pack(side=RIGHT)
        endf = Frame(self.mp)
        endf.pack(side=TOP)
        Label(endf, text='End:   ').pack(side=LEFT)
        self.ee = Entry(endf)
        self.ee.pack(side=RIGHT)
        pf = Frame(self.mp)
        pf.pack(side=TOP)
        Label(pf, text='Project:').pack(side=LEFT)
        self.pe = Entry(pf)
        self.pe.pack(side=RIGHT)
        self.se = Entry(self.mp)
        self.se.pack(side=TOP, fill=X)
        bf = Frame(self.mp)
        bf.pack(side=TOP)
        search = Button(bf, text="Search", command=self._search)
        search.pack(side=LEFT)
        cancel = Button(bf, text="Cancel", command=self._cancel)
        cancel.pack(side=RIGHT)
        clear = Button(f, text="Clear", command=self._clear)
        clear.pack(side=BOTTOM)
        
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


class LBChoice(object):
    '''This is a general list box and returning mechanism. Mostly for unarchiving.'''
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

class projArea(object):
        def __init__(self, mf, t, nc, th):
            self.nc = nc
            self.th = th
            self.t = t
            self.lock = 0
            self.f = Frame(mf, relief=RAISED, borderwidth=2)
            f2 = Frame(self.f)
            f2.pack()
            Button(f2, text='Lock', command=self.ul).pack(side=LEFT)
            Label(f2, text=t, width=37, font=("Helvetica", 16)).pack(side=LEFT)
            b = Button(f2)
            b.pack(side=LEFT)
            pt = ptime.ptime(project=self.t, button=b, th=self.th)
            b.config(command=pt.click)
            Button(f2, text='X', command=self.close).pack(side=LEFT)
            self.f.bind("<Enter>", self.ent)
            self.f.bind("<Leave>", self.lv)
            self.prev()
            self.entry = Text(self.f, width=80, height=10, bg='white', wrap=WORD)
            self.entry.bind("<Shift-Key-Return>", self.commit_note)
            self.f.pack()
        
        def prev(self):
            self.f1 = Frame(self.f)
            scrollbar = Scrollbar(self.f1)
            scrollbar.pack(side=RIGHT, fill=Y)
            self.p = Text(self.f1, height=10, width=77, wrap=WORD, bg='light blue', spacing1=5)
            self.p.pack()
            self.p.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.p.yview)
            self.uprev()
                
        def uprev(self):
            self.p.delete('1.0', END)
            for row in self.nc.print_project(self.t):
                s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[3]) + '\n'
                self.p.insert(END, s)
            self.p.yview(END)
        
        def ent(self, event):
                self.f1.pack()
                self.entry.pack()
                self.entry.focus_set()
            
        def lv(self, event):
            if self.lock == 0:
                self.f1.pack_forget()
                self.entry.pack_forget()
            
        def ul(self):
            if self.lock == 0:
                self.lock = 1
            else:
                self.lock = 0
        
        def commit_note(self, event):
            self.nc.note_in(self.t, self.entry.get('1.0',END).strip(), None)
            self.entry.delete('1.0', END)
            self.uprev()
            
        def close(self):
            self.nc.archive(self.t)
            self.f.pack_forget()
            self.f.destroy()

class noteGui(Frame):
    def __init__(self, master=None):
        self.m = master
        self.f = Frame.__init__(self, master)
        self.pack()
        self.nc = ncore.noteCore() #noteCore
        self.th = ptime.timehandler()
        self.d = {}
        self.l = 0         #The listbox to unarchive.
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
        self.m.config(menu=menubar)
        un = self.nc.get_unarchived()
        for u in un:
            self.d[u] = projArea(self.f, u, self.nc, self.th)
        
    def save(self):
        self.nc.save()
        self.nc.set_archive()
        
    def nproject(self):
        ans = tkSimpleDialog.askstring("Project", "New Project Name:", parent=self.m)
        if ans:
            if ans not in self.nc.get_all_projects():
                self.d[ans] = projArea(self.f, ans, self.nc, self.th)
                
    def oproject(self):
        p = LBChoice(master=self.m, title='Open', li=self.nc.get_archive()).returnValue()
        if p == None:
            return
        self.d[p] = projArea(self.f, p, self.nc, self.th)
        self.nc.unarchive(p)
        
    def search(self):
        Search(self.m, 'Search', nc=self.nc)
        
root = Tk()
root.title("noteTaker")
app = noteGui(master=root)
app.mainloop()
#root.destroy()
