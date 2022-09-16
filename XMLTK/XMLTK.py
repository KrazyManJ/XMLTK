import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import tkinter
from tkinter import Tk, Widget, Variable, PhotoImage
from dataclasses import dataclass
from typing import Callable

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


def parse(filepath: str, functions: dict[str, Callable[[Tk, Widget], None]] | None = None):
    Win = Tk()

    WIN_IGNORE_ATTRS = ["title", "geometry", "icon", "resizable"]
    PLACE_TAGS = ["pack", "grid", "place"]
    GRID_CONFIGURATORS = {
        "rowconfig": Widget.rowconfigure.__name__,
        "columnconfig": Widget.columnconfigure.__name__
    }
    BLACKLIST_TAGS = PLACE_TAGS + list(GRID_CONFIGURATORS.keys()) + ["Variable", "ConfigClass"]
    ROOT_ATTRIBS = {
        "geometry": Win.geometry,
        "title": Win.title,
        "icon": Win.iconbitmap,
    }

    Variables: dict[str, Variable] = {}
    IDWidgets: dict[str, Widget] = {}
    ConfigClasses: dict[str, dict[str, any]] = {}

    if functions is None:
        functions = {}

    def clearNamespace(tag: str):
        return tag.split("}")[1] if tag.__contains__("}") else tag

    def gridPackPlace(w: Widget, e: Element):
        placer = None
        try:
            placer = [chi for chi in e if clearNamespace(chi.tag) in PLACE_TAGS][0]
        except IndexError:
            placer = None
        if placer is not None:
            tag = clearNamespace(placer.tag)
            getattr(w, tag)(placer.attrib)
        else:
            w.pack()
        for ch in [ch for ch in e if clearNamespace(ch.tag) in GRID_CONFIGURATORS.keys()]:
            getattr(w, GRID_CONFIGURATORS[clearNamespace(ch.tag)])(**ch.attrib)

    def applyChild(parentelem: Widget | Tk, xmldata: Element):
        for ch in [ch for ch in xmldata if clearNamespace(ch.tag) not in BLACKLIST_TAGS]:
            fc = getattr(tkinter, clearNamespace(ch.tag))
            elem = fc(parentelem)
            if configureWidget(elem, ch):
                tag = clearNamespace(ch.tag)
                if tag == "Listbox":
                    for line in [l for l in ch if clearNamespace(l.tag) == "Line"]:
                        elem.insert("end", line.text if line.text is not None else "")
                else:
                    applyChild(elem, ch)

    def configureWidget(widget: Widget, xmlelem: Element) -> bool:

        data: dict[str, any] = xmlelem.attrib

        if "configclass" in data:
            for cls in [cls for cls in data["configclass"].split(" ") if cls in ConfigClasses]:
                data.update(ConfigClasses[cls])
            del data["configclass"]
        if "font" in data and data["font"].__contains__(";"):
            data["font"] = tuple(data["font"].split(";", 3))
        if "id" in data:
            IDWidgets[data["id"]] = widget
            del data["id"]
        if "command" in data:
            if data["command"] in functions:
                fct = functions[data["command"]]
                data["command"] = lambda: fct(Win, widget)
            else:
                del data["command"]
        if "image" in data:
            photo = PhotoImage(file=data["image"])
            data["image"] = photo
            widget.image = photo

        gridPackPlace(widget, xmlelem)

        count = [ch for ch in xmlelem if clearNamespace(ch.tag) not in PLACE_TAGS].__len__()
        if count == 0 and xmlelem.text is not None and xmlelem.text.strip().__len__() != 0:
            xmlelem.attrib["text"] = xmlelem.text.strip()
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

    for child in [child for child in root if clearNamespace(child.tag) == "ConfigClass"]:
        if child.attrib.get("name").__contains__(" "):
            raise Exception("ConfigClass name attribute cannot contain spaces!")
        else:
            ConfigClasses[child.attrib.get("name")] = {k: v for k, v in child.attrib.items() if k not in ["name"]}

    applyChild(Win, root)
    return XmlTk(Win, Variables, IDWidgets)
