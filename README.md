<h1 align="center">XMLTK</h1>
<p align="center"><i>Make your TKinter app just like web app</i></p>

---


XMLTK is Python package, that creates Tkinter window from XML file. 
Instead of typing nearly hundreds lines of code to design GUI, with this
package you are able to write it just like web page with html.

## Features

- <kbd>Easy HTML-like Syntax</kbd> - Creating of app has never been easier without
any kind of graphical designer
- <kbd>Functions parsing</kbd> - To apply functionality to the app, you need to use functions also.
For that XMLTK can get functions via getting them in parse section and apply them to the actual
targeted element
- <kbd>Identifiers</kbd> - For working with some special Widgets (Canvas, Entry, ...) you can use ID
attribute to get it via function in parsed application to do anything you want
- <kbd>Variables</kbd> - To get user's input data, you can use variables how you can in normal Tkinter app,
just declare it in XML file and then use its name to retrieve it, and also use it in design
- <kbd>Configuration Classes</kbd> *NEW* - Just like in HTML, you can create class with attributes and then
just link Widgets to apply one configuration to multiple elements

## Example

`app.xml`
```xml
<!-- Main window tag -->
<Tk title="Example App">
    <!-- All elements in window, with attributes as settings -->
    <Label font="Arial; 20" fg="red">
        <!-- Text in element usually means its text value -->
        This is an example app in TKinter using XMLTK
        <!-- Geometry placement function, when not defined, pack is used in default -->
        <pack fill="x" padx="10" pady="10"/>
    </Label>
    <!-- defining button to run "close" command -->
    <Button command="close">
        Ok thanks, I understand!
        <pack fill="x" padx="10" pady="10"/>
    </Button>
</Tk>
```
`main.py`
```python
import XMLTK

#Function to close window
def button_use(win, elem):
    win.destroy()

if __name__ == '__main__':
    app = XMLTK.parse("app.xml",
      { "close": button_use } # Adding function to click on close command 
    )
    app.mainloop() # To run app
```

### Supported elements:

- [X] Button
- [X] Canvas *(Needs to be drawn on it by python)*
- [X] Checkbutton
- [X] Entry
- [X] Frame
- [X] Label
- [X] LabelFrame
- [X] Listbox
- [ ] Menu
- [ ] Menubutton
- [X] Message
- [ ] OptionMenu
- [ ] PanedWindow
- [X] Radiobutton
- [X] Scale
- [ ] Scrollbar
- [X] Spinbox
- [ ] Text
- [ ] Toplevel