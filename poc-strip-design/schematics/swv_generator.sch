v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 200 -280 200 -230 { lab=#net1}
N 200 -170 200 -130 { lab=VSS}
N 200 -130 200 -100 { lab=VSS}
N 200 -350 200 -280 { lab=VDD}
N 200 -230 200 -170 { lab=#net1}
N 200 -280 230 -280 { lab=VDD}
N 230 -280 230 -170 { lab=VDD}
N 200 -170 230 -170 { lab=VDD}
N 350 -280 350 -230 { lab=#net2}
N 350 -170 350 -130 { lab=#net1}
N 350 -130 200 -130 { lab=#net1}
N 350 -350 350 -280 { lab=VDD}
N 350 -230 350 -170 { lab=#net2}
N 350 -280 500 -280 { lab=#net2}
N 500 -350 500 -310 { lab=VDD}
N 500 -250 500 -220 { lab=VOUT}
N 500 -160 500 -100 { lab=VSS}
N 500 -220 550 -220 { lab=VOUT}
N 650 -200 650 -130 { lab=VBIAS}
N 650 -130 500 -130 { lab=VBIAS}
N 500 -130 500 -100 { lab=VBIAS}
N 650 -260 650 -200 { lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 180 -200 0 0 {name=M1
L=0.5
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 180 -280 0 0 {name=M2
L=0.5
W=4
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 330 -200 0 0 {name=M3
L=0.15
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 330 -280 0 0 {name=M4
L=0.15
W=8
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 480 -280 0 0 {name=M5
L=0.15
W=10
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 480 -130 0 0 {name=M6
L=0.15
W=5
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 630 -230 0 0 {name=M7
L=2
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 200 -350 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 350 -350 0 0 {name=l2 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 200 -100 0 0 {name=l3 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 500 -100 0 0 {name=l4 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 650 -260 0 0 {name=l5 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 550 -220 0 1 {name=l6 sig_type=std_logic lab=VOUT}
C {devices/lab_pin.sym} 180 -200 0 0 {name=l7 sig_type=std_logic lab=STEP}
C {devices/lab_pin.sym} 330 -200 0 0 {name=l8 sig_type=std_logic lab=CLK}
C {devices/lab_pin.sym} 330 -280 0 0 {name=l9 sig_type=std_logic lab=CLK}
