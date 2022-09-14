"""
This example of calculator app uses all unusual ascpets/syntax that XMLTK offers:

- XML Syntax
- Variables
- Functions
- Configuration Classes

"""

from tkinter import Widget

import XMLTK

if __name__ == '__main__':
    def insert(win, widget: Widget):
        display.set(str(display.get()) + widget.configure()["text"][4])


    def clear(win, widget):
        display.set("")


    def equals(win, widget):
        try:
            display.set(eval(display.get()))
        except:
            display.set("")


    app = XMLTK.parse("calculator.xml", {"insert": insert, "clear": clear, "equals": equals})
    display = app.Variables["display"]

    app.mainloop()
