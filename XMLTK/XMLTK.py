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
    IDWidgets: dict[str, Widget]

    def mainloop(self, n: int = 0):
        self.Tk.mainloop(n)

    def getWidgetById(self, id: str):
        return self.IDWidgets[id]


def parse(filepath: str, functions: dict[str, Callable[[Tk, Widget], None]] | None = None):
    def parseNamespace(tag: str):
        return tag.split("}")[1] if tag.__contains__("}") else tag

    def childcount(xmlelem: Element):
        return [ch for ch in xmlelem if parseNamespace(ch.tag) not in PLACE_TAGS].__len__()

    def gridPackPlace(w: Widget, e: Element):
        placer = None
        for chi in e:
            if parseNamespace(chi.tag) in PLACE_TAGS:
                placer = chi
                break
        if placer is None:
            w.pack()
            return
        match parseNamespace(placer.tag):
            case "pack":
                w.pack(placer.attrib)
            case "grid":
                w.grid(placer.attrib)
            case "place":
                w.place(placer.attrib)
            case _:
                w.pack()
        for ch in [ch for ch in e if parseNamespace(ch.tag) in GRID_CONFIG_TAGS]:
            index = ch.attrib["index"]
            gridData = ch.attrib
            del gridData["index"]
            match parseNamespace(ch.tag):
                case "rowconfig":
                    w.grid_rowconfigure(index, ch.attrib)
                case "columnconfig":
                    w.grid_columnconfigure(index, ch.attrib)

    def applyChild(parentelem: Widget | Tk, xmldata: Element):
        for ch in [ch for ch in xmldata if parseNamespace(ch.tag) not in BLACKLIST_TAGS]:
            fc = getattr(tkinter, parseNamespace(ch.tag))
            elem: Widget = fc(parentelem)
            if configureWidget(elem, ch): applyChild(elem, ch)

    def configureWidget(widget: Widget, xmlelem: Element) -> bool:

        data: dict[str, any] = xmlelem.attrib

        if "font" in data: data["font"] = tuple(data["font"].split(";", 3))
        if "id" in data:
            IDWidgets[data["id"]] = widget
            del data["id"]
        if "command" in data and parseNamespace(xmlelem.tag) == "Button":
            fct = functions[data["command"]]
            data["command"] = lambda: fct(Win, widget)
        if "image" in data:
            path = data["image"]
            photo = PhotoImage(file=path)
            data["image"] = photo
            widget.image = photo

        match xmlelem.tag:
            case "Toplevel", "Menu":
                pass
            case _:
                gridPackPlace(widget, xmlelem)
        count = childcount(xmlelem)
        if count == 0:
            if xmlelem.text is not None and xmlelem.text.strip().__len__() != 0:
                xmlelem.attrib["text"] = xmlelem.text.strip()
        widget.configure(data)
        return count > 0

    Win = tkinter.Tk()

    WIN_IGNORE_ATTRS = ["title", "geometry", "icon", "resizable", "xmlns"]
    PLACE_TAGS = ["pack", "grid", "place"]
    GRID_CONFIG_TAGS = ["rowconfig", "columnconfig"]
    BLACKLIST_TAGS = PLACE_TAGS + GRID_CONFIG_TAGS + ["Variable"]
    ROOT_ATTRIBS = {
        "geometry": Win.geometry,
        "title": Win.title,
        "icon": Win.iconbitmap,
    }

    Variables: dict[str, Variable] = {}
    IDWidgets: dict[str, Widget] = {}
    root = ET.parse(filepath).getroot()

    for key in ROOT_ATTRIBS.keys():
        if key in root.attrib: ROOT_ATTRIBS[key](root.attrib[key])
    if "resizable" in root.attrib:
        values = root.attrib["resizable"].split(" ", 2)
        Win.resizable(values[0].lower() == "true", values[1].lower() == "true")

    Win.configure({k: v for k, v in root.attrib.items() if k not in WIN_IGNORE_ATTRS})

    for child in [child for child in root if parseNamespace(child.tag) == "Variable"]:
        Variables[child.attrib.get("name")] = Variable(master=Win, name=child.attrib.get("name"),
                                                       value=child.attrib.get("value"))

    applyChild(Win, root)
    return XmlTk(Win, Variables, IDWidgets)