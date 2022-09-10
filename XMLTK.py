import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import tkinter
from tkinter import Tk,Widget,Variable

__all__ = ["parse"]

def parse(filepath: str):

    def parseNamespace(tag: str):
        return tag.split("}")[1] if tag.__contains__("}") else tag

    def childcount(xmlelem: Element):
        i = 0
        for ch in xmlelem:
            if parseNamespace(ch.tag) not in PLACE_TAGS: i += 1
        return i

    def gridPackPlace(w: Widget, e: Element):
        def gridConfig(wi: Widget, el: Element):
            for ch in [ch for ch in el if parseNamespace(ch.tag) in GRID_CONFIG_TAGS]:
                index = ch.attrib["index"]
                gridData = ch.attrib
                del gridData["index"]
                match parseNamespace(ch.tag):
                    case "rowconfig":
                        wi.grid_rowconfigure(index, ch.attrib)
                    case "columnconfig":
                        wi.grid_columnconfigure(index, ch.attrib)

        placer = None
        for chi in e:
            if parseNamespace(chi.tag) in PLACE_TAGS:
                placer = chi
                break
        if placer is None:
            w.pack()
            return
        match parseNamespace(placer.tag):
            case "pack": w.pack(placer.attrib)
            case "grid": w.grid(placer.attrib)
            case "place": w.place(placer.attrib)
            case _: w.pack()
        gridConfig(w, e)



    def applyChild(parentelem: Widget | Tk, xmldata: Element):
        for child in [ch for ch in xmldata if parseNamespace(ch.tag) not in BLACKLIST_TAGS]:
            fc = getattr(tkinter, parseNamespace(child.tag))
            elem: Widget = fc(parentelem)
            if configureRuler(elem, child): applyChild(elem, child)

    def configureRuler(widget: Widget, xmlelem: Element) -> bool:

        data: dict[str, any] = xmlelem.attrib

        if "font" in data: data["font"] = tuple(data["font"].split(";", 3))
        if "textvariable" in data: data["textvariable"] = Variables[data["textvariable"]]

        match xmlelem.tag:
            case "Toplevel","Menu":
                pass
            case _:
                gridPackPlace(widget, xmlelem)
        count = childcount(xmlelem)
        if count == 0:
            if xmlelem.text is not None: xmlelem.attrib["text"] = xmlelem.text.strip()
        widget.configure(xmlelem.attrib)
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
    root = ET.parse(filepath).getroot()

    for key in ROOT_ATTRIBS.keys():
        if key in root.attrib: ROOT_ATTRIBS[key](root.attrib[key])

    Win.configure({k: v for k, v in root.attrib.items() if k not in WIN_IGNORE_ATTRS})

    for child in [child for child in root if parseNamespace(child.tag) == "Variable"]:
        Variables[child.attrib.get("name")] = Variable(master=Win,name=child.attrib.get("name"),value=child.attrib.get("value"))

    applyChild(Win,root)
    return Win, Variables