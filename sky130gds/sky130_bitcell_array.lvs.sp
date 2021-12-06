**************************************************
* OpenRAM generated memory.
* Words: 256
* Data bits: 32
* Banks: 1
* Column mux: 4:1
* Trimmed: False
* LVS: True
**************************************************
* NGSPICE file created from sky130_fd_bd_sram__sram_sp_cell_opt1.ext - technology: sky130A

.subckt sky130_fd_bd_sram__sram_sp_cell_opt1 BL BR VGND VPWR VPB VNB WL
X0 Q_bar WL BR VNB sky130_fd_pr__special_nfet_pass w=0.14u l=0.15u
X1 Q Q_bar VGND VNB sky130_fd_pr__special_nfet_latch w=0.21u l=0.15u
X2 BL WL Q VNB sky130_fd_pr__special_nfet_pass w=0.14u l=0.15u
X3 Q WL Q VPB sky130_fd_pr__special_pfet_pass w=0.07u l=0.095u
X4 Q_bar WL Q_bar VPB sky130_fd_pr__special_pfet_pass w=0.07u l=0.095u
X5 VPWR Q Q_bar VPB sky130_fd_pr__special_pfet_pass w=0.14u l=0.15u
X6 Q Q_bar VPWR VPB sky130_fd_pr__special_pfet_pass w=0.14u l=0.15u
X7 VGND Q Q_bar VNB sky130_fd_pr__special_nfet_latch w=0.21u l=0.15u
.ends
* NGSPICE file created from sky130_fd_bd_sram__sram_sp_cell_opt1.ext - technology: sky130A

.subckt sky130_fd_bd_sram__sram_sp_cell_opt1a BL BR VGND VPWR VPB VNB WL
X0 Q_bar WL BR VNB sky130_fd_pr__special_nfet_pass w=0.14u l=0.15u
X1 Q Q_bar VGND VNB sky130_fd_pr__special_nfet_latch w=0.21u l=0.15u
X2 BL WL Q VNB sky130_fd_pr__special_nfet_pass w=0.14u l=0.15u
X3 Q WL Q VPB sky130_fd_pr__special_pfet_pass w=0.07u l=0.095u
X4 Q_bar WL Q_bar VPB sky130_fd_pr__special_pfet_pass w=0.07u l=0.095u
X5 VPWR Q Q_bar VPB sky130_fd_pr__special_pfet_pass w=0.14u l=0.15u
X6 Q Q_bar VPWR VPB sky130_fd_pr__special_pfet_pass w=0.14u l=0.15u
X7 VGND Q Q_bar VNB sky130_fd_pr__special_nfet_latch w=0.21u l=0.15u
.ends
* NGSPICE file created from sky130_fd_bd_sram__sram_sp_wlstrap.ext - technology: sky130A

.subckt sky130_fd_bd_sram__sram_sp_wlstrap VPWR
.ends
* NGSPICE file created from sky130_fd_bd_sram__sram_sp_wlstrap_p.ext - technology: sky130A

.subckt sky130_fd_bd_sram__sram_sp_wlstrap_p VGND
.ends
* NGSPICE file created from sky130_fd_bd_sram__sram_sp_wlstrapa.ext - technology: sky130A

.subckt sky130_fd_bd_sram__sram_sp_wlstrapa VPWR
.ends

.SUBCKT sky130_bitcell_array bl_0 br_0 bl_1 br_1 bl_2 br_2 wl_0 wl_1 wl_2 vdd gnd
*.PININFO bl_0:B br_0:B bl_1:B br_1:B bl_2:B br_2:B wl_0:I wl_1:I wl_2:I vdd:B gnd:B
* INOUT : bl_0
* INOUT : br_0
* INOUT : bl_1
* INOUT : br_1
* INOUT : bl_2
* INOUT : br_2
* INPUT : wl_0
* INPUT : wl_1
* INPUT : wl_2
* POWER : vdd
* GROUND: gnd

Xrow_0_col_0_bitcell bl_0 br_0 gnd vdd vdd gnd wl_0 sky130_fd_bd_sram__sram_sp_cell_opt1
Xrow_0_col_0_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap
Xrow_0_col_1_bitcell bl_1 br_1 gnd vdd vdd gnd wl_0 sky130_fd_bd_sram__sram_sp_cell_opt1
Xrow_0_col_1_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap_p
Xrow_0_col_2_bitcell bl_2 br_2 gnd vdd vdd gnd wl_0 sky130_fd_bd_sram__sram_sp_cell_opt1
Xrow_0_col_2_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap


Xrow_1_col_0_bitcell bl_0 br_0 gnd vdd vdd gnd wl_1 sky130_fd_bd_sram__sram_sp_cell_opt1a
Xrow_1_col_0_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrapa
Xrow_1_col_1_bitcell bl_1 br_1 gnd vdd vdd gnd wl_1 sky130_fd_bd_sram__sram_sp_cell_opt1a
Xrow_1_col_1_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap_p
Xrow_1_col_2_bitcell bl_2 br_2 gnd vdd vdd gnd wl_1 sky130_fd_bd_sram__sram_sp_cell_opt1a
Xrow_1_col_2_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrapa

Xrow_2_col_0_bitcell bl_0 br_0 gnd vdd vdd gnd wl_2 sky130_fd_bd_sram__sram_sp_cell_opt1
Xrow_2_col_0_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap
Xrow_2_col_1_bitcell bl_1 br_1 gnd vdd vdd gnd wl_2 sky130_fd_bd_sram__sram_sp_cell_opt1
Xrow_2_col_1_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap_p
Xrow_2_col_2_bitcell bl_2 br_2 gnd vdd vdd gnd wl_2 sky130_fd_bd_sram__sram_sp_cell_opt1
Xrow_2_col_2_wlstrap vdd sky130_fd_bd_sram__sram_sp_wlstrap

.ENDS sky130_bitcell_array
