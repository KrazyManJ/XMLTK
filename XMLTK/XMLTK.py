import inspect
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Tk, Widget, Variable, PhotoImage, Menu
from dataclasses import dataclass
from typing import Callable
import uuid
import warnings
import pyglet.font

__all__ = ["parse"]


@dataclass(frozen=True)
class XmlTk:
    Tk: Tk
    Variables: dict[str, Variable]
    __IDWidgets: dict[str, Widget]

    def mainloop(self, n: int = 0):
        self.Tk.mainloop(n)

    def getWidgetById(self, wantedId: str) -> Widget | None:
        return self.__IDWidgets.get(wantedId, None)


class XMLTKParseException(Exception):
    __module__ = Exception.__module__

class XMLSyntaxWarning(Warning):
    __module__ = Warning.__module__

def parse(filepath: str, functions: dict[str, Callable[[Tk, Widget, str | None], None]] | None = None):
    Win = Tk()

    WIN_IGNORE_ATTRS = ["title", "geometry", "icon", "resizable"]
    PLACE_TAGS = ["pack", "grid", "place"]
    GRID_CONFIGURATORS = {
        "rowconfig": Widget.rowconfigure.__name__,
        "columnconfig": Widget.columnconfigure.__name__
    }
    BLACKLIST_TAGS = PLACE_TAGS + list(GRID_CONFIGURATORS.keys()) + ["Variable", "Style","Font"]
    ROOT_ATTRIBS = {
        "geometry": Win.geometry,
        "title": Win.title,
        "icon": Win.iconbitmap,
    }

    Variables: dict[str, Variable] = {}
    IDWidgets: dict[str, Widget] = {}
    Styles: dict[str, dict[str, any]] = {}
    TStyle = ttk.Style()

    if functions is None:
        functions = {}

    def XMLSyntaxWarn(text):
        warnings.warn(text, category=XMLSyntaxWarning,stacklevel=inspect.stack().__len__())

    def clearNamespace(tag: str):
        return tag.split("}")[1] if tag.__contains__("}") else tag

    def widgetName(widget: Widget | Tk):
        return widget.widgetName if isinstance(widget, Widget) else "tk"

    def gridPackPlace(widget: Widget, parent: Widget, e: Element):
        placer = None
        try:
            placer = [chi for chi in e if clearNamespace(chi.tag) in PLACE_TAGS][0]
        except IndexError:
            placer = None
        if placer is not None:
            tag = clearNamespace(placer.tag)
            getattr(widget, tag)(placer.attrib)
        else:
            widget.pack()
        for ch in [ch for ch in e if clearNamespace(ch.tag) in GRID_CONFIGURATORS.keys()]:
            getattr(widget, GRID_CONFIGURATORS[clearNamespace(ch.tag)])(**ch.attrib)

    def applyChild(parentelem: Widget | Tk, xmldata: Element):
        for ch in [ch for ch in xmldata if clearNamespace(ch.tag) not in BLACKLIST_TAGS]:
            tag = clearNamespace(ch.tag)
            if widgetName(parentelem) == "menu":
                try:
                    menucmd = getattr(parentelem,"add_"+tag.lower())
                except:
                    XMLSyntaxWarn(f"Invalid tag '{tag}' inside Menu widget!")
                    menucmd = None
                if menucmd is not None:
                    if tag == "Cascade":
                        elem = Menu(tearoff=0)
                        menucmd(label=ch.text.strip(),menu=elem)
                        applyChild(elem,ch)
                    elif tag == "Separator":
                        menucmd(ch.attrib)
                    else:
                        menucmd(label=ch.text.strip(),**attrsConvertor(ch.attrib,parentelem))
            else:
                if tag.startswith("T-"):
                    fc = getattr(ttk, tag.split("-")[1])
                else:
                    fc = getattr(tk, tag)
                elem = fc(parentelem)
                if configureWidget(elem, parentelem, ch):
                    tag = tag
                    if tag == "Listbox":
                        for line in [l for l in ch if clearNamespace(l.tag) == "Line"]:
                            elem.insert("end", line.text if line.text is not None else "")
                    else:
                        applyChild(elem, ch)

    def attrsConvertor(dataDict,widget) -> dict:
        if "font" in dataDict and dataDict["font"].__contains__(";"):
            dataDict["font"] = tuple(dataDict["font"].split(";", 3))
        if "command" in dataDict:
            cmd:str = dataDict["command"]
            fctName = cmd.split("(")[0]
            fctArgs = cmd[cmd.find("(")+1:cmd.find(")")] if cmd.__contains__("(") and cmd.__contains__(")") else None
            if fctName in functions:
                fct = functions[fctName]
                dataDict["command"] = lambda: fct(Win, widget, fctArgs)
            else:
                XMLSyntaxWarn(f"Invalid function name '{fctName}'!")
                del dataDict["command"]
        return dataDict

    def configureWidget(widget: Widget, parent: Widget, xmlelem: Element) -> bool:

        data: dict[str, any] = xmlelem.attrib

        isTtk = widget.__module__ == "tkinter.ttk"
        if "style" in data:
            for stl in [cls for cls in data["style"].split(" ") if cls in Styles]:
                if isTtk:
                    data["style"] = f"{stl}.T{widget.widgetName.split('::')[1].capitalize()}"
                    break
                else:
                    data.update(Styles[stl])
            if not isTtk:
                del data["style"]
        elif isTtk:
            styleId = uuid.uuid4()
            name = widget.widgetName.split("::")[1].capitalize()
            TStyle.configure(f"{styleId}.T{name}",**{k: v for k, v in data.items() if k not in widget.configure().keys()})
            data = {k: v for k, v in data.items() if k in widget.configure().keys()}
            data["style"] = f"{styleId}.T{name}"
        data = attrsConvertor(data,widget)
        if "id" in data:
            IDWidgets[data["id"]] = widget
            del data["id"]
        if "image" in data:
            photo = PhotoImage(file=data["image"])
            data["image"] = photo
            widget.image = photo
        if widget.widgetName == "menu":
            data["tearoff"] = 0
            parent.configure(menu=widget)
        else:
            gridPackPlace(widget, parent, xmlelem)

        count = [ch for ch in xmlelem if clearNamespace(ch.tag) not in PLACE_TAGS].__len__()
        if count == 0 and xmlelem.text is not None and xmlelem.text.strip().__len__() != 0:
            data["text"] = xmlelem.text.strip()
        widget.configure(data)
        return count > 0

    try:
        root = ET.parse(filepath).getroot()
    except Exception as exce:
        raise XMLTKParseException(exce.args[0]) from None

    for key in [key for key in ROOT_ATTRIBS.keys() if key in root.attrib]:
        ROOT_ATTRIBS[key](root.attrib[key])
    if "resizable" in root.attrib:
        values = root.attrib["resizable"].split(" ", 2)
        Win.resizable(values[0].lower() == "true", values[1].lower() == "true")

    Win.configure({k: v for k, v in root.attrib.items() if k not in WIN_IGNORE_ATTRS})

    for child in [child for child in root if clearNamespace(child.tag) == "Variable" and "name" in child.attrib]:
        Variables[child.attrib["name"]] = Variable(**child.attrib)

    for child in [child for child in root if clearNamespace(child.tag) == "Font" and "path" in child.attrib]:
        pyglet.font.add_file(child.attrib["path"])

    for child in [child for child in root if clearNamespace(child.tag) == "Style" and "name" in child.attrib]:
        if child.attrib["name"].__contains__(" "):
            raise Exception("Style name attribute cannot contain spaces!")
        else:
            styleName = child.attrib["name"]
            Styles[styleName] = attrsConvertor({k: v for k, v in child.attrib.items() if k not in ["name"]},Win)
            for w in [x.__name__ for x in ttk.Widget.__subclasses__() if x.__name__.lower() != "widget"]:
                TStyle.configure(f"{styleName}.T{w}",**Styles[styleName])

    applyChild(Win, root)
    return XmlTk(Win, Variables, IDWidgets)
