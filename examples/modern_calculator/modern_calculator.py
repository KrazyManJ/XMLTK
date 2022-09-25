"""
This example of modern calculator app is the same as example before, but with TTK Elements
"""

import XMLTK

if __name__ == '__main__':

    def insert(win, widget, tid):
        display.set(str(display.get()) + widget.configure()["text"][4])


    def clear(win, widget, tid):
        display.set("")


    def equals(win, widget, tid):
        try:
            display.set(eval(display.get()))
        except:
            display.set("")

    app = XMLTK.parse("modern_calculator.xml", {"insert": insert, "clear": clear, "equals": equals } )
    display = app.getVariable("display")
    app.mainloop()
