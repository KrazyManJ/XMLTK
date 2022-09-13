from tkinter import *
from lxml import etree

HEAD = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="Tkinter">'
FOOT = '</xs:schema>'
TK_ATTRS = ["title","geometry","resizable","icon"]

def generate():
    # START
    Xml = HEAD + '<xs:element name="Tk" type="Tk"/>'

    # VARIABLE
    Xml += '<xs:complexType name="Variable">' \
           '<xs:attribute name="name" use="required"/>' \
           '<xs:attribute name="value"/>' \
           '</xs:complexType>'

    # TK
    Xml += f'<xs:complexType name="Tk"><xs:complexContent><xs:extension base="BaseWidget">'
    Xml += '<xs:sequence maxOccurs="unbounded" minOccurs="0"><xs:element name="Variable" type="Variable"/></xs:sequence>'
    for attr in TK_ATTRS+list(Tk().configure().keys()): Xml+= f'<xs:attribute name="{attr}"/>'
    Xml += f'</xs:extension></xs:complexContent></xs:complexType>'

    # ROW / COLUMN CONFIG
    Xml += '<xs:complexType name="RowColumnConfig">'
    for key in ["index"]+list(Button().grid_rowconfigure(index="0").keys()):
        Xml += f'<xs:attribute name="{key}"/>'
    Xml += '</xs:complexType>'

    # GRID / PACK / PLACE
    b = Button()
    geo_dec = [(b.grid, b.grid_info, {}), (b.pack, b.pack_info, {}), (b.place, b.place_info, {"x": 0})]
    for geo, geo_info, geo_args in geo_dec:
        b = Button()
        geo(geo_args)
        name: str = geo.__name__
        Xml += f'<xs:complexType name="{name.partition("_")[0].capitalize()}">'
        for attr in [a for a in geo_info() if a not in ["in"]]:
            Xml += f'<xs:attribute name="{attr}"/>'
        Xml += f'</xs:complexType>'

    # BASE WIDGET TYPE
    Xml += f'<xs:complexType name="BaseWidget"><xs:choice maxOccurs="unbounded" minOccurs="0">'
    for w in Widget.__subclasses__(): Xml+=f'<xs:element name="{w.__name__}" type="{w.__name__}"/>'
    Xml += f'</xs:choice></xs:complexType>'

    # WIDGET TYPE (PACKABLE)
    Xml += """
    <xs:complexType name="Widget">
        <xs:complexContent>
            <xs:extension base="BaseWidget">
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
            </xs:extension>
        </xs:complexContent>
    </xs:complexType>
    """.strip().replace("\n","").replace("    ","")

    # WIDGET WITH PARAMS
    for w in Widget.__subclasses__():
        Xml += f'<xs:complexType name="{w.__name__}"><xs:complexContent><xs:extension base="Widget">'
        for attr in w().configure().keys(): Xml += f'<xs:attribute name="{attr}"/>'
        Xml += '</xs:extension></xs:complexContent></xs:complexType>'

    # END + RETURN
    Xml += FOOT
    return etree.tostring(etree.fromstring(Xml),pretty_print=True).decode()

open("Tkinter.xsd","w").write(generate())
