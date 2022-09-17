import tkinter as tk
import tkinter.ttk as ttk
from lxml import etree


def generate():
    HEAD = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="Tkinter">'
    FOOT = '</xs:schema>'
    TK_ATTRS = ["title", "geometry", "resizable", "icon"]
    ENUMS = [
        ("State", ["normal", "active", "disabled", "readonly"]),
        ("Default", ["normal", "active", "disabled"]),
        ("Justify", ["left", "right", "center"]),
        ("Relief", ["raised", "sunken", "groove", "ridge", "flat"]),
        ("Anchor", ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"]),
        ("Fill", ["x", "y", "both"]),
        ("Side", ["right","left","top","bottom"]),
        ("Compound", ["top", "left", "center", "right", "bottom", "none"]),
        ("OverRelief", ["raised", "sunken", "groove", "ridge", "flat"]),
        ("Resizable", ["true true", "true false", "false true", "false false"])
    ]
    TYPES = {
        "image": "xs:anyURI",
        "icon": "xs:anyURI"
    }
    GEOMETRY_MANIPULATOR = """
    <xs:sequence>
        <xs:choice minOccurs="0">
            <xs:element name="pack" type="Pack"/>
            <xs:element name="grid" type="Grid"/>
            <xs:element name="place" type="Place"/>
        </xs:choice>
        <xs:choice minOccurs="0">
            <xs:element name="columnconfig" type="RowColumnConfig"/>
            <xs:element name="rowconfig" type="RowColumnConfig"/>
        </xs:choice>
    </xs:sequence>
    """.strip().replace("\n", "").replace("    ", "")

    def xsd_enumeration(objName, values) -> str:
        xml = f'<xs:simpleType name="{objName}" final="restriction"><xs:restriction base="xs:string">'
        for val in values: xml += f'<xs:enumeration value="{val}"/>'
        xml += '</xs:restriction></xs:simpleType>'
        return xml

    def xsd_extended_type(objName, extends, objAttrs, otherBody="") -> str:
        xml = f'<xs:complexType name="{objName}"><xs:complexContent><xs:extension base="{extends}">' + otherBody
        for a in objAttrs: xml += attribute_declarator(a)
        xml += f'</xs:extension></xs:complexContent></xs:complexType>'
        return xml

    def xsd_complex_type(objName, objAttrs, requiredAttrs=None) -> str:
        if requiredAttrs is None:
            requiredAttrs = []
        xml = f'<xs:complexType name="{objName}">'
        for a in objAttrs: xml += attribute_declarator(a, a in requiredAttrs)
        xml += '</xs:complexType>'
        return xml

    def xsd_element(elemName, elemType):
        return f'<xs:element name="{elemName}" type="{elemType}"/>'

    def attribute_declarator(attrName, required=False) -> str:
        required, aType = 'use="required"' if required else "", ""
        if attrName.capitalize() in [t for t, k in ENUMS]:
            aType = f'type="{attrName.capitalize()}"'
        elif attrName in TYPES.keys():
            aType = f'type="{TYPES[attrName]}"'
        return f'<xs:attribute name="{attrName}" {aType} {required}/>'

    Win = tk.Tk()

    # START
    Xml = HEAD + '<xs:element name="Tk" type="Tk"/>'
    # VARIABLE
    Xml += xsd_complex_type("Variable", ["name", "value"], ["name"])
    # CONFIG CLASS
    AllConfigs = []
    for w in [w for w in tk.Widget.__subclasses__() if w.__name__.lower() != "widget"]:
        for a in w().configure().keys():
            if a not in AllConfigs:
                AllConfigs.append(a)
    Xml += xsd_complex_type("Style",["name","padding"]+AllConfigs,["name"])
    # ENUMS
    for name, attrs in ENUMS: Xml += xsd_enumeration(name, attrs)
    # TK
    Xml += xsd_extended_type("Tk", "BaseWidget", TK_ATTRS + list(tk.Tk().configure().keys()),
        f'<xs:sequence maxOccurs="unbounded" minOccurs="0">{xsd_element("Variable","Variable")}{xsd_element("Style","Style")}</xs:sequence>'
                             )
    # ROW / COLUMN CONFIG
    Xml += xsd_complex_type("RowColumnConfig", ["index"] + list(tk.Button().grid_rowconfigure(index="0").keys()))

    # GRID / PACK / PLACE
    b = tk.Button()
    geo_dec = [(b.grid, b.grid_info, {}), (b.pack, b.pack_info, {}), (b.place, b.place_info, {"x": 0})]
    for geo, geo_info, geo_args in geo_dec:
        b = tk.Button()
        geo(geo_args)
        Xml += xsd_complex_type(geo.__name__.partition("_")[0].capitalize(), [a for a in geo_info() if a not in ["in"]])

    # BASE WIDGET TYPE
    Xml += f'<xs:complexType name="BaseWidget"><xs:choice maxOccurs="unbounded" minOccurs="0">'
    for w in [w for w in tk.Widget.__subclasses__() if w.__name__.lower() != "widget"]: Xml += f'<xs:element name="{w.__name__}" type="{w.__name__}"/>'
    for w in ttk.Widget.__subclasses__(): Xml += f'<xs:element name="T-{w.__name__}" type="T-{w.__name__}"/>'
    Xml += f'</xs:choice></xs:complexType>'

    # PACKABLE ()
    Xml += f'<xs:complexType name="Packable">{GEOMETRY_MANIPULATOR}</xs:complexType>'

    # WIDGET TYPE
    Xml += f'<xs:complexType name="Widget"><xs:complexContent><xs:extension base="BaseWidget">{GEOMETRY_MANIPULATOR}</xs:extension></xs:complexContent></xs:complexType>'

    # WIDGET WITH PARAMS
    for wT, prefix in [(tk.Widget,""),(ttk.Widget,"T-")]:
        for w in [w for w in wT.__subclasses__() if w.__name__.lower() != "widget"]:
            match w.__name__:
                case "Listbox":
                    parent = "Packable"
                case _:
                    parent = "Widget"
            Xml += f'<xs:complexType name="{prefix}{w.__name__}"><xs:complexContent><xs:extension base="{parent}">'
            match w.__name__:
                case "Listbox":
                    Xml += '<xs:choice><xs:element name="Line"/></xs:choice>'
                case _:
                    pass
            for attr in list(w().configure().keys())+["id","style"]: Xml += attribute_declarator(attr)
            Xml += '</xs:extension></xs:complexContent></xs:complexType>'

    return etree.tostring(etree.fromstring(Xml + FOOT), pretty_print=True).decode().replace("  ", "    ")


open("Tkinter.xsd", "w").write(generate())