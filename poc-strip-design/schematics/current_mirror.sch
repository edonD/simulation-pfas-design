v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 100 -70 100 -40 { lab=GND}
N 100 -40 250 -40 { lab=GND}
N 250 -40 400 -40 { lab=GND}
N 250 -70 250 -40 { lab=GND}
N 400 -70 400 -40 { lab=GND}
N 100 -190 100 -130 { lab=IREF}
N 250 -190 250 -130 { lab=#net1}
N 400 -190 400 -130 { lab=#net2}
N 100 -310 100 -250 { lab=VCAS}
N 250 -310 250 -250 { lab=IOUT1}
N 400 -310 400 -250 { lab=IOUT2}
N 130 -100 230 -100 { lab=IREF}
N 230 -100 380 -100 { lab=IREF}
N 100 -130 130 -130 { lab=IREF}
N 130 -130 130 -100 { lab=IREF}
N 130 -220 230 -220 { lab=VCAS}
N 230 -220 380 -220 { lab=VCAS}
N 100 -250 130 -250 { lab=VCAS}
N 130 -250 130 -220 { lab=VCAS}
C {sky130_fd_pr/nfet_01v8.sym} 120 -100 0 1 {name=M1
L=1
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 230 -100 0 0 {name=M2
L=1
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 380 -100 0 0 {name=M3
L=1
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 120 -220 0 1 {name=M6
L=0.5
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 230 -220 0 0 {name=M4
L=0.5
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 380 -220 0 0 {name=M5
L=0.5
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 250 -40 0 0 {name=l1 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 100 -310 0 0 {name=l2 sig_type=std_logic lab=VCAS}
C {devices/lab_pin.sym} 250 -310 0 0 {name=l3 sig_type=std_logic lab=IOUT1}
C {devices/lab_pin.sym} 400 -310 0 1 {name=l4 sig_type=std_logic lab=IOUT2}
C {devices/lab_pin.sym} 100 -160 0 0 {name=l5 sig_type=std_logic lab=IREF}
