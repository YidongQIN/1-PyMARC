#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yidong QIN'

"""
MARC Bridge with sensors.
Input all data into MongoDB.
"""

from BrIMcollection import *

marc = Group("marc_sensor")
# 0. Parameter
# 0.1 Structural parameter
span_num = Parameter(1, "span_num", 11)
x_spacing = Parameter(2, "x_spacing", 108.0)
y_spacing = Parameter(3, "y_spacing", 84)
z_height = Parameter(4, "z_height", 108)
marc.prm_group.append(span_num, x_spacing, y_spacing, z_height)
# 0.2 Section Parameters
Chord_width = Parameter(14, "Chord_width", 6)
Chord_depth = Parameter(15, "Chord_depth", 6)
BottomChord_thickness = Parameter(13, "BottomChord_thickness", 0.375)
TopChord_thickness = Parameter(16, "TopChord_thickness", 0.3125)
VertiBeam_thickness = Parameter(20, "VertiBeam_thickness", 0.25)
deck_thick = Parameter(17, "deck_thick", "5", "Thickness")
WebRadius = Parameter(18, "WebRadius", 1)
marc.prm_group.append(Chord_width, Chord_depth,
                      BottomChord_thickness, TopChord_thickness,
                      deck_thick, VertiBeam_thickness, WebRadius)
# 1. Material
# 1.1 Steel for truss chord
steel = Material(1, 'Steel', d="0.0000007345", E="29000", Nu="0.3", a="0.0000065", Fy="50", Fu="65")
# 1.2 Concrete for deck
concrete = Material(2, 'Concrete', d='0.0000002248', E="3604.9965", a="0.0000055", Fc28="4")
marc.mat_group.append(steel, concrete)
# 2. Sections
# 2.1 Shapes
# rectangle=6*6
rect_Out = Shape(1, 'Rect 6*6', RectangleOBShape,
                 Chord_depth.value, Chord_width.value)
# rectangle=(6-0.375)
rect_Bot_In = Shape(2, 'Rect_Bot_In 5.625*5.625', RectangleOBShape,
                    Chord_depth.value - BottomChord_thickness.value,
                    Chord_width.value - BottomChord_thickness.value, is_cut=True)
# rectangle=(6-0.3125)
rect_Top_In = Shape(3, 'Rect_Top_In 5.6875*5.6875', RectangleOBShape,
                    Chord_depth.value - TopChord_thickness.value,
                    Chord_width.value - TopChord_thickness.value, is_cut=True)
# rectangle=(6-0.25)
rect_Ver_In = Shape(4, 'Rect_Ver_In 5.75*5.75', RectangleOBShape,
                    Chord_depth.value - VertiBeam_thickness.value,
                    Chord_width.value - VertiBeam_thickness.value, is_cut=True)
# circle=1
cir_Web = Shape(5, 'CircleWeb', OBCircle, WebRadius.value)
marc.sec_group.append(rect_Ver_In,rect_Bot_In,rect_Out,rect_Top_In,cir_Web)
# 2.2 bottom chord 6*6*0.375
sect_bottom = Section(11, 'BottomChord', rect_Out, rect_Bot_In, material=steel)
# 2.3 top chord 6*6*0.3125
sect_top = Section(12, 'TopChord', rect_Out, rect_Top_In, material=steel)
# 2.4 vertical chord 6*6*.025
sect_vert = Section(13, 'VerticalChord', rect_Out, rect_Ver_In, material=steel)
# 2.5 web radius=1
sect_web = Section(14, 'Web', cir_Web, material=steel)
marc.sec_group.append(sect_bottom, sect_top, sect_vert, sect_web)
# 3. Nodes
nodeBL = []
nodeBR = []
nodeTL = []
nodeTR = []
for i in range(span_num.value + 1):
    nodeBL.append(
        FENode(i * x_spacing.value,
               y_spacing.value,
               0,
               id="NodeBL_{}".format(i))
    )
    nodeBR.append(FENode(i * x_spacing.value, 0, 0, id="NodeBR_{}".format(i)))
    nodeTL.append(FENode(i * x_spacing.value, y_spacing.value, z_height.value, id="NodeTL_{}".format(i)))
    nodeTR.append(FENode(i * x_spacing.value, 0, z_height.value, id="NodeTR_{}".format(i)))
nodeBL[0].set_node_attr('tz', -1)
nodeBL[0].set_node_attr('tx', -1)
nodeBR[0].set_node_attr('tz', -1)
nodeBR[0].set_node_attr('tx', -1)
nodeBL[span_num.value].set_node_attr('tz', -1)
nodeBL[span_num.value].set_node_attr('tz', -1)
nodeBR[span_num.value].set_node_attr('tz', -1)
nodeBR[span_num.value].set_node_attr('tz', -1)
marc.fem_nodes.append(*nodeBL, *nodeBR, *nodeTL[1:], *nodeTR[1:])
# 4. Structure Elements = Mechanical View
bottomChordList=[]
for i in range(span_num.value):
    bottomChordList.append(Beam(nodeBL[i], nodeBL[i + 1], sect_bottom, steel,
                         id="Bot_L_{}".format(i)))
    bottomChordList.append(Beam(nodeBR[i], nodeBR[i + 1], sect_bottom, steel,
                         id="Bot_R_{}".format(i)))
topChordList = []
for i in range(1, span_num.value):
    topChordList.append(Beam(nodeTL[i], nodeTL[i + 1], sect_top, steel,
                         id="Top_L_{}".format(i)))
    topChordList.append(Beam(nodeTR[i], nodeTR[i + 1], sect_top, steel,
                         id="Top_R_{}".format(i)))
verChordsList = []
for i in range(1, span_num.value + 1):
    for (a, b) in [(nodeBL, nodeBR), (nodeTR, nodeBR), (nodeTR, nodeTL), (nodeBL, nodeTL)]:
        verChordsList.append(Beam(a[i],b[i],sect_vert,steel,
                                  id='Ver_{}'.format(i)))
webList = []
for i in range(1, span_num.value):
    for (a, b, c) in [(nodeBL, nodeTL, "BL/TL"), (nodeBR, nodeTR,"BR/TR"), (nodeTL, nodeTR, "TL/TR"), (nodeTR, nodeTL, "TR\\TL")]:
        webList.append(Beam(a[i], b[i + 1], sect_web, steel,
                            id='Web_{}_{}'.format(c, i)))
        webList.append(Beam(a[i + 1], b[i], sect_web, steel,
                            id='Web_{}_{}'.format(c, i)))
# for _w in webList:
#     print(_w.name)

z_beams = []
for i in range(span_num.value):
    if (i % 2) == 0:
        z_beams.append(Beam(nodeBL[i], nodeBR[i + 1], sect_bottom, steel, id="Bot_L_{}".format(i)))
    else:
        z_beams.append(Beam(nodeBL[i + 1], nodeBR[i], sect_bottom, steel, id="Bot_L_{}".format(i)))

first_seg = [Beam(nodeBL[0], nodeBR[0], sect_bottom, steel,
                  id="first_seg_Bot"),
             Beam(nodeBL[0], nodeTL[1], sect_bottom, steel,
                  id="first_seg_Left"),
             Beam(nodeBR[0], nodeTR[1], sect_bottom, steel,
                  id="first_seg_Right")]
decks=[]
for i in range(span_num.value):
    decks.append(
        Surface(nodeBL[i], nodeBR[i], nodeBR[i + 1], nodeBL[i + 1],
                deck_thick, concrete, deck_name='concrete deck'))

marc.member_gp.append(*bottomChordList, *topChordList, *verChordsList, *webList, *z_beams, *first_seg, *decks)

# 5. Equipments = Geometry View

ShowTree(marc.openBrIM)
marc.openBrIM.save_project()