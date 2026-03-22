v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 100 -200 100 -180 { lab=#net1}
N 100 -200 300 -200 { lab=#net1}
N 300 -200 300 -180 { lab=#net1}
N 300 -120 300 -100 { lab=#net2}
N 300 -100 300 -80 { lab=#net2}
N 100 -120 100 -100 { lab=#net3}
N 100 -100 300 -100 { lab=#net3}
N 100 -40 100 -20 { lab=vsd}
N 300 -40 300 -20 { lab=vdd}
N 100 -150 100 -120 { lab=#net3}
N 300 -150 300 -120 { lab=#net2}
N 100 -280 100 -260 { lab=#net1}
N 100 -280 300 -280 { lab=#net1}
N 300 -280 300 -260 { lab=#net1}
N 100 -360 100 -340 { lab=vdd}
N 100 -360 300 -360 { lab=vdd}
N 300 -360 300 -340 { lab=vdd}
N 100 -230 120 -230 { lab=vss}
N 120 -230 120 -130 { lab=vss}
N 100 -130 120 -130 { lab=vss}
N 300 -230 320 -230 { lab=vss}
N 320 -230 320 -130 { lab=vss}
N 300 -130 320 -130 { lab=vss}
N 100 -310 100 -280 { lab=#net1}
N 300 -310 300 -280 { lab=#net1}
N 300 -340 300 -310 { lab=#net1}
N 100 -340 100 -310 { lab=vdd}
N 300 -200 320 -200 { lab=#net1}
N 320 -200 320 -170 { lab=#net1}
N 300 -170 320 -170 { lab=#net1}
N 300 -260 300 -230 { lab=vss}
N 100 -260 100 -230 { lab=vss}
N 100 -80 100 -40 { lab=vsd}
N 300 -80 300 -40 { lab=vdd}
N 300 -360 500 -360 { lab=vdd}
N 500 -360 500 -340 { lab=vdd}
N 500 -280 500 -260 { lab=ce}
N 500 -200 500 -180 { lab=ibias}
N 500 -120 500 -100 { lab=vsd}
N 500 -40 500 -20 { lab=vss}
N 500 -150 500 -120 { lab=vsd}
N 500 -230 520 -230 { lab=vss}
N 520 -230 520 -130 { lab=vss}
N 500 -130 520 -130 { lab=vss}
N 500 -310 500 -280 { lab=ce}
N 300 -310 500 -310 { lab=vdd}
N 500 -340 500 -310 { lab=vdd}
N 500 -260 500 -230 { lab=vss}
N 500 -230 520 -230 { lab=vss}
N 500 -100 500 -40 { lab=vsd}
N 300 -100 500 -100 { lab=vsd}
N 100 -200 100 -180 { lab=#net1}
N 300 -200 300 -180 { lab=#net1}
N 500 -360 700 -360 { lab=vdd}
N 700 -360 700 -340 { lab=vdd}
N 700 -280 700 -260 { lab=ce}
N 700 -200 700 -180 { lab=ibias}
N 700 -120 700 -100 { lab=vsd}
N 700 -40 700 -20 { lab=vss}
N 700 -150 700 -120 { lab=vsd}
N 700 -230 720 -230 { lab=vss}
N 720 -230 720 -130 { lab=vss}
N 700 -130 720 -130 { lab=vss}
N 700 -310 700 -280 { lab=ce}
N 500 -310 700 -310 { lab=vdd}
N 500 -340 500 -310 { lab=vdd}
N 500 -260 500 -230 { lab=vss}
N 500 -230 700 -230 { lab=vss}
N 700 -260 700 -230 { lab=vss}
N 700 -100 700 -40 { lab=vsd}
N 500 -100 700 -100 { lab=vsd}
C {sky130_fd_pr/nfet_01v8.sym} 80 -150 0 0 {name=M1
W=4
L=0.5
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 280 -150 0 0 {name=M2
W=4
L=0.5
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 80 -230 0 0 {name=M3
W=8
L=0.5
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 280 -230 0 0 {name=M4
W=8
L=0.5
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 100 -360 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 100 -20 0 0 {name=l2 sig_type=std_logic lab=vsd}
C {devices/lab_pin.sym} 300 -20 0 0 {name=l3 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 120 -130 0 1 {name=l4 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 320 -130 0 1 {name=l5 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 300 -280 0 0 {name=l6 sig_type=std_logic lab=#net1}
C {devices/lab_wire.sym} 300 -100 0 0 {name=l7 sig_type=std_logic lab=#net2}
C {devices/lab_wire.sym} 100 -150 0 0 {name=l8 sig_type=std_logic lab=#net3}
C {sky130_fd_pr/nfet_01v8.sym} 280 -20 0 0 {name=M5
W=4
L=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 100 -100 0 0 {name=l9 sig_type=std_logic lab=#net3}
C {devices/lab_pin.sym} 300 -80 0 0 {name=l10 sig_type=std_logic lab=#net2}
C {devices/lab_pin.sym} 300 -100 0 0 {name=l11 sig_type=std_logic lab=#net3}
C {devices/lab_pin.sym} 300 -20 0 0 {name=l12 sig_type=std_logic lab=IBIAS}
C {devices/lab_pin.sym} 300 -360 0 0 {name=l13 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 500 -100 0 0 {name=l14 sig_type=std_logic lab=vsd}
C {devices/lab_pin.sym} 500 -20 0 0 {name=l15 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 500 -360 0 0 {name=l16 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 500 -260 0 1 {name=l17 sig_type=std_logic lab=ce}
C {devices/lab_pin.sym} 500 -180 0 1 {name=l18 sig_type=std_logic lab=ibias}
C {sky130_fd_pr/pfet_01v8.sym} 480 -230 0 0 {name=M6
W=40
L=0.15
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 480 -130 0 0 {name=M7
W=20
L=0.15
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 520 -130 0 1 {name=l19 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 500 -230 0 0 {name=l20 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 700 -20 0 0 {name=l21 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 700 -360 0 0 {name=l22 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 700 -260 0 1 {name=l23 sig_type=std_logic lab=ce}
C {devices/lab_pin.sym} 700 -180 0 1 {name=l24 sig_type=std_logic lab=ibias}
C {devices/lab_pin.sym} 720 -130 0 1 {name=l25 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 680 -130 0 0 {name=M8
W=2
L=2
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 700 -100 0 0 {name=l26 sig_type=std_logic lab=vsd}
C {devices/lab_pin.sym} 680 -150 0 0 {name=l27 sig_type=std_logic lab=IBIAS}
C {devices/lab_pin.sym} 680 -110 0 0 {name=l28 sig_type=std_logic lab=IBIAS}