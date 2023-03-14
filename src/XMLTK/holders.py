from dataclasses import dataclass
from tkinter import Tk, Toplevel, Widget


@dataclass(frozen=True,eq=True)
class CommandHolder:
    Win: Tk | Toplevel
    Widget: Widget
    ID: str