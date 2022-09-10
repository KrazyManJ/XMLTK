<h1 align="center">XMLTK</h1>
<p align="center"><i>Make your TKinter app just like web app</i></p>

---


XMLTK is Python package, that creates Tkinter window from XML file. 
Instead of typing nearly hundreds lines of code to design GUI, with this
package you are able to write it just like web page with html.


## Basic structure

```xml
<!-- Main window tag -->
<Tk title="Example App">
    <!-- All elements in window, with attributes as settings -->
    <Label font="Arial; 20">
        <!-- Text in element usually means its text value -->
        This is an example app in TKinter using TKXML
        <!-- Geometry placement function, when not defined, pack is used in default -->
        <pack fill="x" padx="10" pady="10"/>
    </Label>
    <Button>
        Ok thanks, i understand!
        <pack fill="x" padx="10" pady="10"/>
    </Button>
</Tk>
```

