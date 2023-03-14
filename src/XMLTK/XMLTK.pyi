from enum import Enum
from tkinter import Variable
from typing import Callable
from src.XMLTK.holders import *

def parse(filepath: str, functions: dict[str, Callable[[CommandHolder], None]] | None = ...,
          parseType: ParseType = ...,events: dict[str,Callable[[any],None]] = ...) -> XmlTk: ...


class ParseType(Enum):
    TK = ...
    TOPLEVEL = ...

class XmlTk:
    """
    Class holding parsed application from XML including
    all variables and identified widgets
    """
    __Win: Tk | Toplevel
    __Variables: dict[str, Variable]
    __IDWidgets: dict[str, Widget]

    def __init__(self, win: Tk | Toplevel, variables: dict[str, Variable], idwidgets: dict[str, Widget]): ...

    def mainloop(self, n: int = ...) -> None: ...

    def getWindow(self) -> Tk | Toplevel: ...

    def getVariable(self, name: str) -> Variable | None: ...

    def getWidgetById(self, wantedId: str) -> Widget | None: ...
