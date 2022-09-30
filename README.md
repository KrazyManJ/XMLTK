<h1 align="center">XMLTK</h1>
<p align="center"><i>Make your TKinter app just like web app</i></p>

---


XMLTK is Python package, that creates Tkinter window from XML file. 
Instead of typing nearly hundreds lines of code to design GUI, with this
package you are able to write it just like web page with html.

## Features

- <kbd>Easy HTML-like Syntax</kbd> - Creating of app has never been easier without
any kind of graphical designer
- <kbd>Tkinter XML Schema</kbd> - XMLTK Includes schema to add ability to your IDE to give
you hints when writing XML Code like list of available Widgets or Attributes
- <kbd>Functions parsing</kbd> - To apply functionality to the app, you need to use functions also.
For that XMLTK can get functions via getting them in parse section and apply them to the actual
targeted element
- <kbd>Identifiers</kbd> - For working with some special Widgets (Canvas, Entry, ...) you can use ID
attribute to get it via function in parsed application to do anything you want
- <kbd>Variables</kbd> - To get user's input data, you can use variables how you can in normal Tkinter app,
just declare it in XML file and then use its name to retrieve it, and also use it in design
- <kbd>Styles</kbd> - you can create style elements with attributes and then
just link Widgets to apply one configuration to multiple elements
- <kbd>Custom Fonts</kbd> - with XMLTK you can import custom fonts from file using filepath,
and then use them anywhere in your application
- <kbd>Hover Tooltips</kbd> - add custom hints to your program by using tooltips (text that shows upon hovering over widget)

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

## Syntax comparison with already existing tkinter xml package - Pygubu

**Both syntaxes result into same app!!**

`Pygubu syntax`

```xml
<interface version="1.2">
    <object class="tk.Toplevel" id="mainwindow">
        <property name="height">200</property>
        <property name="resizable">both</property>
        <property name="title" translatable="yes">Hello World App</property>
        <property name="width">200</property>
        <child>
            <object class="ttk.Frame" id="mainframe">
                <property name="height">200</property>
                <property name="padding">20</property>
                <property name="width">200</property>
                <layout manager="pack">
                    <property name="expand">true</property>
                    <property name="side">top</property>
                </layout>
                <child>
                    <object class="ttk.Label" id="label1">
                        <property name="anchor">center</property>
                        <property name="font">Helvetica 26</property>
                        <property name="foreground">#0000b8</property>
                        <property name="text" translatable="yes">Hello World !</property>
                        <layout manager="pack">
                            <property name="side">top</property>
                        </layout>
                    </object>
                </child>
            </object>
        </child>
    </object>
</interface>
```

`XMLTK syntax`

```xml
<Tk xmlns="Tkinter" geometry="200x200" title="Hello World App">
    <T-Frame height="200" width="200" padding="20">
        <T-Label anchor="center" font="Helvetica 26" foreground="#0000b8">
            Hello World !
            <pack side="top"/>
        </T-Label>
        <pack expand="true" side="top"/>
    </T-Frame>
</Tk>
```

## Supported elements:

### tkinter

- [X] Button
- [X] Canvas *(Needs to be drawn on it by python)*
- [X] Checkbutton
- [X] Entry
- [X] Frame
- [X] Label
- [X] LabelFrame
- [X] Listbox
- [X] Menu
- [X] Menubutton
- [X] Message
- [X] OptionMenu
- [X] PanedWindow
- [X] Radiobutton
- [X] Scale
- [X] Scrollbar
- [X] Spinbox
- [ ] Text
- [X] Toplevel

### ttk

- [X] Button
- [X] Checkbutton
- [X] Entry
- [X] Frame
- [X] Label
- [X] Labelframe
- [X] Menubutton
- [ ] Notebook
- [X] Panedwindow
- [X] Progressbar
- [X] Radiobutton
- [X] Scale
- [X] Scrollbar
- [X] Separator
- [X] Sizegrip
- [ ] Treeview
