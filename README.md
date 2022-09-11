<h1 align="center">XMLTK</h1>
<p align="center"><i>Make your TKinter app just like web app</i></p>

---


XMLTK is Python package, that creates Tkinter window from XML file. 
Instead of typing nearly hundreds lines of code to design GUI, with this
package you are able to write it just like web page with html.


## Basic structure with start

`app.xml`
```xml
<!-- Main window tag -->
<Tk title="Example App">
    <!-- All elements in window, with attributes as settings -->
    <Label font="Arial; 20">
        <!-- Text in element usually means its text value -->
        This is an example app in TKinter using XMLTK
        <!-- Geometry placement function, when not defined, pack is used in default -->
        <pack fill="x" padx="10" pady="10"/>
    </Label>
    <Button>
        Ok thanks, I understand!
        <pack fill="x" padx="10" pady="10"/>
    </Button>
</Tk>
```
`main.py`
```python
import XMLTK

if __name__ == '__main__':
    app = XMLTK.parse("app.xml")
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
- [ ] Listbox
- [ ] Menu
- [ ] Menubutton
- [X] Message
- [ ] OptionMenu
- [ ] PanedWindow
- [ ] Radiobutton
- [ ] Scale
- [ ] Scrollbar
- [ ] ScrolledText
- [ ] Spinbox
- [ ] Text
- [ ] Root a Toplevel