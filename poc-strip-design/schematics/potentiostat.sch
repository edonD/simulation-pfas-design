v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 200 -280 200 -230 { lab=#net1}
N 400 -280 400 -230 { lab=#net2}
N 200 -170 200 -130 { lab=#net3}
N 400 -170 400 -130 { lab=#net3}
N 200 -130 400 -130 { lab=#net3}
N 300 -130 300 -100 { lab=#net3}
N 300 -100 300 -70 { lab=#net3}
N 300 -70 300 -40 { lab=VSS}
N 200 -380 200 -280 { lab=VDD}
N 200 -380 400 -380 { lab=VDD}
N 400 -380 400 -280 { lab=VDD}
N 200 -280 200 -230 { lab=#net1}
N 200 -230 200 -170 { lab=#net1}
N 400 -230 400 -170 { lab=#net2}
N 400 -380 600 -380 { lab=VDD}
N 600 -380 600 -310 { lab=VDD}
N 600 -250 600 -210 { lab=CE}
N 600 -150 600 -100 { lab=VSS}
N 200 -330 230 -330 { lab=VDD}
N 230 -330 230 -230 { lab=VDD}
N 200 -230 230 -230 { lab=VDD}
N 400 -330 430 -330 { lab=VDD}
N 430 -330 430 -230 { lab=VDD}
N 400 -230 430 -230 { lab=VDD}
C {sky130_fd_pr/nfet_01v8.sym} 180 -200 0 0 {name=M1
L=0.5
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 380 -200 0 0 {name=M2
L=0.5
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 180 -330 0 0 {name=M3
L=0.5
W=8
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 380 -330 0 0 {name=M4
L=0.5
W=8
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 280 -70 0 0 {name=M5
L=1
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 580 -280 0 0 {name=M6
L=0.15
W=40
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 580 -180 0 0 {name=M7
L=0.15
W=20
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 200 -380 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 300 -40 0 0 {name=l2 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 600 -100 0 0 {name=l3 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 180 -200 0 0 {name=l4 sig_type=std_logic lab=VDAC}
C {devices/lab_pin.sym} 380 -200 0 0 {name=l5 sig_type=std_logic lab=RE}
C {devices/lab_pin.sym} 600 -230 0 1 {name=l6 sig_type=std_logic lab=CE}
C {devices/lab_pin.sym} 280 -70 0 0 {name=l7 sig_type=std_logic lab=IBIAS}
