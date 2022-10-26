"""
This example of calculator app uses all unusual ascpets/syntax that XMLTK offers:

- XML Syntax
- Variables
- Functions
- Configuration Classes

"""

import XMLTK
from XMLTK import CommandHolder

if __name__ == '__main__':
    def insert(command_holder: CommandHolder):
        display.set(str(display.get()) + command_holder.Widget.configure()["text"][4])


    def clear(command_holder):
        display.set("")


    def equals(command_holder: CommandHolder):
        try:
            display.set(eval(display.get()))
        except:
            display.set("")


    app = XMLTK.parse("calculator.xml", {"insert": insert, "clear": clear, "equals": equals})
    display = app.getVariable("display")

    app.mainloop()
