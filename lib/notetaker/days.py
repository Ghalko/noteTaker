"""Creates a scrolling canvas in which days are separated into their own
text boxes of varying sizes for easier date reading and fewer days loaded."""

from Tkinter import (Tk, Frame, Scrollbar, Canvas, Button, Text, WORD, BOTH,
                     VERTICAL, END, Y, NW, RIGHT, LEFT, FALSE, TRUE)
import notetaker.ncore
import notetaker.utils
import datetime

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
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
        def _configure_interior(event=None):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event=None):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class Days(object):
    def __init__(self, master=None, ncore=None, project=None, limit=2):
        self.master = master
        self.ncore = ncore
        self.project = project
        self.frame = None
        self.gui_fill()
        self.days = []
        self.limit = limit
        limit = (limit+1) *-1 #Gets the previous two days and this one.
        list_ = sorted(self.ncore.get_all_dates(project))[limit:]
        if list_ == []:
            day = int(datetime.datetime.now().strftime("%Y%m%d"))
            self.append(day)
        for day in list_:
            self.append(day) #uses Days append
        self._repack()

    def gui_fill(self):
        """Creates the vertical scrolled frame"""
        self.frame = VerticalScrolledFrame(self.master)
        self.frame.pack()
        tempf = Frame(self.frame.interior)
        tempf.pack()
        Button(tempf, text="More", command=self._more).pack(side=LEFT)
        Button(tempf, text="Less", command=self._less).pack(side=RIGHT)

    def append(self, date):
        """Appends a new Day instance and repacks."""
        self.days.append(Day(self, date))
        self._repack()

    def get_current(self):
        """Returns current day at the end of the list."""
        return self.days[-1]

    def _more(self, event=None):
        """Adds 3 more days to the beginning of the list."""
        tlist = []
        limit = (self.limit+4) *-1
        oldlimit = (self.limit+1) * -1
        self.limit += 3
        list_ = sorted(self.ncore.get_all_dates(self.project))[limit:oldlimit]
        for day in self.days:
            day.gui_forget()
        for day in list_:
            tlist.append(Day(self, day))
        self.days = tlist + self.days
        self._repack()

    def _less(self, event=None):
        if len(self.days) < 4:
            return
        for day in self.days:
            day.gui_forget()
        self.limit -= 3
        self.days = self.days[3:]
        self._repack()

    def _repack(self):
        """Repacks the list of Day objects"""
        for day in self.days:
            day.gui_pack()
        self.days[-1].text.config(height=10) #For better entry.
        self.days[-1].text.yview(END) #maybe make these two statements
        #a decorator


class Day(object):
    """Text displayed in text boxes."""
    def __init__(self, parent=None, date=None):
        self.date = date
        self.parent = parent
        self.entry = 0
        self.text = None
        self.gui_fill()

    def gui_fill(self):
        """Fills gui."""
        self.text = Text(self.parent.frame.interior, height=10, width=77,
                         wrap=WORD, bg='light blue', spacing1=5)
        lines = 0
        for row in self.parent.ncore.print_project_day(self.parent.project,
                                                       self.date):
            str_ = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2]) + '\n'
            self.text.insert(END, str_)
            lines += utils.count_lines(str_)
        if lines < 10:
            self.text.config(height=lines+1)

    def gui_forget(self):
        """For pack forgetting"""
        self.text.pack_forget()

    def gui_pack(self):
        """For packing"""
        self.text.pack()

    def gui_refresh(self, event=None):
        """Reloads the day's text"""
        self.text.delete('1.0', END)
        for row in self.parent.ncore.print_project_day(self.parent.project,
                                                       self.date):
            str_ = str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2]) + '\n'
            self.text.insert(END, str_)
        self.text.yview(END)


class Test(Frame):
    """Basically just a class to be called if module is not imported."""
    def __init__(self, master=None, ncore=None, project="Other", limit=2):
        self.frame = Frame.__init__(self, master)
        self.pack()
        Days(master=master, ncore=ncore, project=project, limit=limit)


if __name__ == "__main__":
    PATH = "/home/bgorges/Tools/noteTaker"
    ROOT = Tk()
    NOTECORE = ncore.NoteCore(dbpath=PATH)
    APP = Test(master=ROOT, ncore=NOTECORE, project="Other", limit=2)
    APP.mainloop()
