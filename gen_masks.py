#!/usr/bin/env python3

import sys
sys.path.append("/usr/local/klayout/pymod")
import pya

in_name = "sky130gds/sky130_bitcell_array.gds"
flat_name = "sky130_bitcell_array_flat.gds"
opc_name = "sky130_bitcell_array_opc.gds"

layout = pya.Layout()
top = layout.read(in_name)
top_cells = list(layout.each_top_cell())

for idx in top_cells:
    print("Flattening {}".format(layout.cell(idx).name))
    # all layers, prune unused cells
    layout.flatten(idx, -1, True)
    
print("Saving gds {}".format(flat_name))
layout.write(flat_name)

top_cell = layout.top_cell()

#layout2 = pya.Layout()
# top_cell2 = layout2.create_cell(top_cell.name)

l_diff = layout.layer(65, 20)
l_cfom_maskAdd = layout.layer(22, 21)
l_cfom_maskDrop = layout.layer(22, 22)

l_poly = layout.layer(66, 20)
l_cp1m_maskAdd = layout.layer(33, 43)
l_cp1m_maskDrop = layout.layer(33, 42)

l_li = layout.layer(67, 20)
l_cli1m_maskAdd = layout.layer(115, 43)
l_cli1m_maskDrop = layout.layer(115, 42)

# List of mask, add, drop
layers = [(l_diff, l_cfom_maskAdd, l_cfom_maskDrop),
          (l_poly, l_cp1m_maskAdd, l_cp1m_maskDrop),
          (l_li, l_cli1m_maskAdd, l_cli1m_maskDrop)]

p = pya.ShapeProcessor()
s = pya.Shapes()

for mask, add, drop in layers:
    p.boolean(layout, top_cell, mask,
              layout, top_cell, add,
              s,
              pya.EdgeProcessor().ModeOr,
              True, True, True)

    p.boolean(layout, top_cell, mask,
              layout, top_cell, drop,
              top_cell.shapes(mask),
              pya.EdgeProcessor().ModeANotB,
              True, True, True)
    
print("Saving gds {}".format(opc_name))
layout.write(opc_name)

sys.exit(0)
# all except purpose (datatype) 5 -- label and 44 -- via

mcon_wildcard = "67/44"

m1_wildcard = "68/0-4,6-43,45-*"
via_wildcard = "68/44"

m2_wildcard = "69/0-4,6-43,45-*"
via2_wildcard = "69/44"

poly = polygons(66, 20)
cp1m_maskAdd = input(33, 43)
cp1m_maskDrop = input(33, 42)

licon = polygons(66, 44)

li = polygons(li_wildcard)
cli1m_maskAdd = input(115, 43)
cli1m_maskDrop = input(115, 42)

mcon = polygons(mcon_wildcard)
m1 = polygons(m1_wildcard)
via = polygons(via_wildcard)
m2 = polygons(m2_wildcard)
via2 = polygons(via2_wildcard)

clic1m_maskAdd = input(106, 43)
clic1m_maskDrop = input(106, 42)

cmm1_maskAdd = input(62, 21)
cmm1_maskDrop = input(62, 22)
cmvia1_maskAdd = input(105, 21)
cmvia1_maskDrop = input(105, 22)
cmm2_maskAdd = input(105, 43)
cmm2_maskDrop = input(105, 42)
cmvia2_maskAdd = input(108, 21)
cmvia2_maskDrop = input(108, 22)
