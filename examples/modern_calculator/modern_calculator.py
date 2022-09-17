"""
This example of modern calculator app is the same as example before, but with TTK Elements
"""

import XMLTK

if __name__ == '__main__':

    def insert(win, widget):
        display.set(str(display.get()) + widget.configure()["text"][4])


    def clear(win, widget):
        display.set("")


    def equals(win, widget):
        try:
            display.set(eval(display.get()))
        except:
            display.set("")

    app = XMLTK.parse("modern_calculator.xml", {"insert": insert, "clear": clear, "equals": equals } )
    display = app.Variables["display"]
    app.mainloop()
