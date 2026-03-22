v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 200 -280 200 -230 { lab=NET1}
N 200 -170 200 -130 { lab=VREF}
N 200 -230 200 -170 { lab=NET1}
N 200 -280 350 -280 { lab=NET1}
N 350 -280 350 -230 { lab=NET1}
N 350 -170 350 -130 { lab=VDD}
N 350 -130 350 -100 { lab=VDD}
N 200 -130 200 -100 { lab=VREF}
N 200 -350 200 -280 { lab=VDD}
N 200 -350 350 -350 { lab=VDD}
N 350 -350 350 -280 { lab=VDD}
N 350 -350 500 -350 { lab=VDD}
N 500 -350 500 -310 { lab=VDD}
N 500 -250 500 -220 { lab=VOUT}
N 500 -160 500 -100 { lab=VSS}
N 500 -220 550 -220 { lab=VOUT}
N 550 -220 650 -220 { lab=VOUT}
N 650 -220 650 -200 { lab=VOUT}
N 650 -140 650 -100 { lab=SENSOR_IN}
N 650 -100 200 -100 { lab=SENSOR_IN}
N 750 -170 750 -100 { lab=VBIAS}
N 750 -100 750 -70 { lab=VBIAS}
N 750 -70 500 -70 { lab=VBIAS}
N 500 -100 500 -70 { lab=VBIAS}
N 750 -230 750 -170 { lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 180 -200 0 0 {name=M1
L=0.5
W=10
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 330 -200 0 0 {name=M2
L=0.5
W=20
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 480 -280 0 0 {name=M3
L=0.15
W=20
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 480 -130 0 0 {name=M4
L=0.15
W=10
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 630 -170 0 0 {name=M5
L=10
W=0.5
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 730 -200 0 0 {name=M6
L=2
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 200 -350 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 500 -100 0 0 {name=l2 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 750 -230 0 0 {name=l3 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 200 -100 0 0 {name=l4 sig_type=std_logic lab=SENSOR_IN}
C {devices/lab_pin.sym} 550 -220 0 1 {name=l5 sig_type=std_logic lab=VOUT}
C {devices/lab_pin.sym} 200 -130 0 0 {name=l6 sig_type=std_logic lab=VREF}
