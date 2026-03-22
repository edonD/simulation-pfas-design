v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 70 -100 70 -80 { lab=GND}
N 70 -80 240 -80 { lab=GND}
N 240 -100 240 -80 { lab=GND}
N 240 -130 250 -130 { lab=GND}
N 250 -130 250 -80 { lab=GND}
N 240 -80 250 -80 { lab=GND}
N 240 -180 240 -160 { lab=#net1}
N 70 -180 70 -160 { lab=IREF}
N 70 -160 70 -130 { lab=IREF}
N 70 -130 80 -130 { lab=IREF}
N 80 -130 80 -80 { lab=IREF}
N 70 -80 80 -80 { lab=GND}
N 240 -260 240 -240 { lab=#net2}
N 240 -340 240 -320 { lab=IOUT2}
N 70 -340 70 -320 { lab=IOUT1}
N 70 -340 80 -340 { lab=IOUT1}
N 80 -340 80 -290 { lab=IOUT1}
N 70 -290 80 -290 { lab=IOUT1}
N 240 -340 250 -340 { lab=IOUT2}
N 250 -340 250 -290 { lab=IOUT2}
N 240 -290 250 -290 { lab=IOUT2}
N 240 -420 240 -400 { lab=VCAS}
N 240 -420 250 -420 { lab=VCAS}
N 250 -420 250 -370 { lab=VCAS}
N 240 -370 250 -370 { lab=VCAS}
N 70 -420 70 -400 { lab=VCAS}
N 70 -420 80 -420 { lab=VCAS}
N 80 -420 80 -370 { lab=VCAS}
N 70 -370 80 -370 { lab=VCAS}
N 70 -260 70 -240 { lab=#net3}
C {sky130_fd_pr/nfet_01v8.sym} 90 -130 0 1 {name=M1
L=1
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 220 -130 0 0 {name=M2
L=1
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 220 -370 0 0 {name=M3
L=1
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 70 -100 0 0 {name=l1 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 240 -100 0 0 {name=l2 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 240 -210 0 0 {name=l3 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 70 -210 0 0 {name=l4 sig_type=std_logic lab=GND}
C {devices/lab_pin.sym} 240 -420 0 0 {name=l5 sig_type=std_logic lab=VCAS}
C {devices/lab_pin.sym} 70 -340 0 0 {name=l6 sig_type=std_logic lab=IOUT1}
C {devices/lab_pin.sym} 250 -340 0 1 {name=l7 sig_type=std_logic lab=IOUT2}
C {devices/lab_pin.sym} 70 -180 0 0 {name=l8 sig_type=std_logic lab=IREF}
C {sky130_fd_pr/nfet_01v8.sym} 90 -370 0 1 {name=M4
L=0.5
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 220 -290 0 0 {name=M5
L=0.5
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 220 -420 0 0 {name=M6
L=0.5
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}