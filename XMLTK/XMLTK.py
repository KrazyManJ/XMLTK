import inspect
import xml.etree.ElementTree as XML
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Tk, Widget, Variable, PhotoImage, Menu, Toplevel
from uuid import uuid4
from warnings import warn
from pyglet.font import add_file as add_font_file
from enum import Enum
import re


class ParseType(Enum):
    TK = Tk
    TOPLEVEL = Toplevel


class XmlTk:
    def __init__(self, win, variables, idwidgets):
        self.__Win = win
        self.__Variables = variables
        self.__IDWidgets = idwidgets

    def mainloop(self, n = 0):
        self.__Win.mainloop(n)

    def getWindow(self):
        return self.__Win

    def getVariable(self, name):
        return self.__Variables.get(name, None)

    def getWidgetById(self, wantedId: str) -> Widget | None:
        return self.__IDWidgets.get(wantedId, None)


class ToolTip(object):
    def __init__(self, widget, text, showtime=500, **config):
        self.showtime = showtime
        self.widget = widget
        self.text = text
        self.labelconfig = config
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.showtime, self.showtip)

    def unschedule(self):
        tempId = self.id
        self.id = None
        if tempId:
            self.widget.after_cancel(tempId)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_pointerx()
        y += self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left', bg="#ffffff", relief='solid', borderwidth=1,
                         wraplength=180)
        label.configure(**self.labelconfig)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class XMLTKParseException(Exception):
    __module__ = Exception.__module__


class XMLSyntaxWarning(Warning):
    __module__ = Warning.__module__


def parse(filepath, functions=None, parseType=ParseType.TK):
    Win = parseType.value()

    WIN_IGNORE_ATTRS = ["title", "geometry", "icon", "resizable"]
    PLACE_TAGS = ["pack", "grid", "place"]
    GRID_CONFIGURATORS = {
        "rowconfig": Widget.rowconfigure.__name__,
        "columnconfig": Widget.columnconfigure.__name__
    }
    BLACKLIST_TAGS = PLACE_TAGS + list(GRID_CONFIGURATORS.keys()) + ["Variable", "Style", "Font", "ToolTip"]
    ROOT_ATTRIBS = {
        "geometry": Win.geometry,
        "title": Win.title,
        "icon": Win.iconbitmap,
    }

    Variables = {}
    IDWidgets = {}
    Styles = {}
    TStyle = ttk.Style()

    if functions is None:
        functions = {}

    def XMLSyntaxWarn(text):
        warn(text, category=XMLSyntaxWarning, stacklevel=inspect.stack().__len__())

    def clearNamespace(tag):
        return tag.split("}")[1] if tag.__contains__("}") else tag

    def widgetName(widget):
        return widget.widgetName if isinstance(widget, Widget) else "tk"

    def configGrid(widget,e):
        for ch in [ch for ch in e if clearNamespace(ch.tag) in GRID_CONFIGURATORS.keys()]:
            getattr(widget, GRID_CONFIGURATORS[clearNamespace(ch.tag)])(**ch.attrib)

    def gridPackPlace(widget, parent, e):
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
        configGrid(widget,e)

    def applyChild(parentelem, xmldata):
        for ch in [ch for ch in xmldata if clearNamespace(ch.tag) not in BLACKLIST_TAGS]:
            tag = clearNamespace(ch.tag)
            if widgetName(parentelem) == "menu":
                try:
                    menucmd = getattr(parentelem, "add_" + tag.lower())
                except:
                    XMLSyntaxWarn(f"Invalid tag '{tag}' inside Menu widget!")
                    menucmd = None
                if menucmd is not None:
                    if tag == "Cascade":
                        elem = Menu(tearoff=0)
                        menucmd(label=ch.text.strip(), menu=elem)
                        applyChild(elem, ch)
                    elif tag == "Separator":
                        menucmd(ch.attrib)
                    else:
                        menucmd(label=ch.text.strip(), **attrsConvertor(ch.attrib, parentelem, True))
            elif widgetName(parentelem) == "listbox" and tag == "Line":
                parentelem.insert("end", ch.text if ch.text is not None else "")
            elif tag in ["Scrollbar","T-Scrollbar"]:
                scrl = tk.Scrollbar() if tag == "Scrollbar" else ttk.Scrollbar()
                scrl.config(command=parentelem.yview)
                parentelem.configure(yscrollcommand=scrl.set)
                gridPackPlace(scrl,parentelem.winfo_parent(),ch)

            else:
                if tag.startswith("T-"):
                    fc = getattr(ttk, tag.split("-")[1])
                else:
                    fc = getattr(tk, tag)
                elem = fc(parentelem)
                if configureWidget(elem, parentelem, ch):
                    applyChild(elem, ch)

    def attrsConvertor(dataDict, widget, fcParse=False):
        if "font" in dataDict and dataDict["font"].__contains__(";"):
            dataDict["font"] = tuple(dataDict["font"].split(";", 3))
        if "command" in dataDict and fcParse:
            cmd: str = dataDict["command"]
            fctName = cmd.split("(")[0]
            fctArgs = cmd[cmd.find("(") + 1:cmd.find(")")] if cmd.__contains__("(") and cmd.__contains__(")") else None
            if fctName in functions:
                fct = functions[fctName]
                dataDict["command"] = lambda: fct(Win, widget, fctArgs)
            else:
                XMLSyntaxWarn(f"Invalid function name '{fctName}'!")
                del dataDict["command"]
        return dataDict

    def configureWidget(widget, parent, xmlelem):
        data = xmlelem.attrib
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
            styleId = uuid4()
            name = widget.widgetName.split("::")[1].capitalize()
            TStyle.configure(f"{styleId}.T{name}",
                             **{k: v for k, v in data.items() if k not in widget.configure().keys()})
            data = {k: v for k, v in data.items() if k in widget.configure().keys()}
            data["style"] = f"{styleId}.T{name}"
        data = attrsConvertor(xmlelem.attrib, widget, True)
        if "id" in data:
            IDWidgets[data["id"]] = widget
            del data["id"]
        if "image" in data:
            photo = PhotoImage(file=data["image"])
            data["image"] = photo
            widget.image = photo
        if widget.widgetName == "menu":
            data["tearoff"] = 0
            parent.configure({"menu": widget})
        elif widgetName(parent) in ["panedwindow", "ttk::panedwindow"]:
            parent.add(widget)
        else:
            gridPackPlace(widget, parent, xmlelem)

        count = [ch for ch in xmlelem if clearNamespace(ch.tag) not in PLACE_TAGS + ["ToolTip"]].__len__()
        if count == 0 and xmlelem.text is not None and xmlelem.text.strip().__len__() != 0:
            data["text"] = xmlelem.text.strip()
        try:
            tooltip = [ch for ch in xmlelem if clearNamespace(ch.tag) == "ToolTip"][0]
        except:
            tooltip = None
        if tooltip is not None:
            tabSize = re.match("\s+", tooltip.text, re.MULTILINE).group(0).__len__() - 1
            ToolTip(widget, "\n".join([t[tabSize:] for t in tooltip.text.splitlines()]).strip(), **tooltip.attrib)
        widget.configure(data)
        return count > 0

    try:
        root = XML.parse(filepath).getroot()
    except Exception as exce:
        raise XMLTKParseException(exce.args[0]) from None

    for key in [key for key in ROOT_ATTRIBS.keys() if key in root.attrib]:
        ROOT_ATTRIBS[key](root.attrib[key])
    if "resizable" in root.attrib:
        values = root.attrib["resizable"].split(" ", 2)
        Win.resizable(values[0].lower() == "true", values[1].lower() == "true")

    Win.configure({k: v for k, v in root.attrib.items() if k not in WIN_IGNORE_ATTRS})

    for child in root:
        childTag = clearNamespace(child.tag)
        if childTag == "Variable" and "name" in child.attrib:
            Variables[child.attrib["name"]] = Variable(**child.attrib)
        elif childTag == "Font" and "path" in child.attrib:
            add_font_file(child.attrib["path"])
        elif childTag == "Style" and "name" in child.attrib:
            if child.attrib["name"].__contains__(" "):
                raise Exception("Style name attribute cannot contain spaces!")
            else:
                styleName = child.attrib["name"]
                Styles[styleName] = attrsConvertor({k: v for k, v in child.attrib.items() if k not in ["name"]}, Win)
                for w in [x.__name__ for x in ttk.Widget.__subclasses__() if x.__name__.lower() != "widget"]:
                    TStyle.configure(f"{styleName}.T{w}", **Styles[styleName])
    configGrid(Win,root)

    applyChild(Win, root)
    return XmlTk(Win, Variables, IDWidgets)
