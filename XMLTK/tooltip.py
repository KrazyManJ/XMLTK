from tkinter import Toplevel, Label

class ToolTip(object):
    def __init__(self, widget, text, showtime=500, **config):
        self.showtime = showtime
        self.widget = widget
        self.text = text
        self.labelconfig = config
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.showtime, self.showtip)

    def unschedule(self):
        tempId = self.id
        self.id = None
        if tempId:
            self.widget.after_cancel(tempId)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_pointerx()
        y += self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left', bg="#ffffff", relief='solid', borderwidth=1,
                         wraplength=180)
        label.configure(**self.labelconfig)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()