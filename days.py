from Tkinter import *
import ncore

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class Days(Frame):
    def __init__(self, master=None, nc=None, project=None, limit=3):
        self.m = master
        self.nc = nc
        self.project=project
        self.gui_fill()
        self.days = []
        self.limit = limit
        limit = (limit+1) *-1 #Gets the previous two days and this one.
        l = sorted(self.nc.get_all_dates(project))[limit:]
        for day in l:
            self.days.append(Day(self, day))
        self._repack()
    
    def gui_fill(self):
        self.f = Frame.__init__(self, self.m)
        self.pack()
        self.frame = VerticalScrolledFrame(self.f)
        self.frame.pack()
        Button(self.frame.interior, text="More", command=self._more).pack()

    def _more(self, event=None):
        """Adds 3 more days to the beginning of the list."""
        tlist = []
        limit = (self.limit+4) *-1
        oldlimit = (self.limit+1) * -1
        self.limit += 3
        l = sorted(self.nc.get_all_dates(self.project))[limit:oldlimit]
        for day in self.days:
            day.gui_forget()
        for day in l:
            tlist.append(Day(self, day))
        self.days = tlist + self.days
        self._repack()

    def _repack(self):
        for day in self.days:
            day.gui_pack()
        self.days[-1].text.yview(END)


class Day(object):
    def __init__(self, parent=None, date=None):
        self.date = date
        self.p = parent
        self.gui_fill()

    def gui_fill(self):
        """Fills gui."""
        self.text = Text(self.p.frame.interior, height=10, width=77,
                         wrap=WORD, bg='light blue', spacing1=5)
        for row in self.p.nc.print_project_day(self.p.project, self.date):
            s = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[3]) + '\n'
            self.text.insert(END, s)

    def gui_forget(self):
        """For pack forgetting"""
        self.text.pack_forget()

    def gui_pack(self):
        """For packing"""
        self.text.pack()

if __name__=="__main__":
    path = "/home/bgorges/Tools/noteTaker"
    root = Tk()
    nc = ncore.noteCore(dbpath=path)
    app = Days(master=root, nc=nc, project="Other", limit=2)
    app.mainloop()
    
