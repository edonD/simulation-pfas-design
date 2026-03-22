v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 200 -300 200 -280 { lab=NET1}
N 200 -220 200 -200 { lab=VREF}
N 200 -200 200 -180 { lab=VREF}
N 200 -180 230 -180 { lab=VREF}
N 230 -180 230 -140 { lab=VREF}
N 200 -140 230 -140 { lab=VREF}
N 200 -300 300 -300 { lab=NET1}
N 300 -300 300 -280 { lab=NET1}
N 300 -220 300 -200 { lab=NET1}
N 300 -200 330 -200 { lab=VDD}
N 330 -250 330 -200 { lab=VDD}
N 300 -250 330 -250 { lab=VDD}
N 300 -380 300 -340 { lab=VDD}
N 200 -380 200 -360 { lab=VDD}
N 200 -380 300 -380 { lab=VDD}
N 400 -380 400 -340 { lab=VDD}
N 300 -380 400 -380 { lab=VDD}
N 400 -280 400 -260 { lab=VOUT}
N 400 -200 400 -160 { lab=VSS}
N 400 -160 400 -120 { lab=VSS}
N 400 -260 450 -260 { lab=VOUT}
N 400 -120 430 -120 { lab=VSS}
N 430 -160 430 -120 { lab=VSS}
N 400 -160 430 -160 { lab=VSS}
N 500 -260 500 -220 { lab=VOUT}
N 450 -260 500 -260 { lab=VOUT}
N 500 -160 500 -120 { lab=SENSOR_IN}
N 500 -120 200 -120 { lab=SENSOR_IN}
N 200 -120 200 -140 { lab=SENSOR_IN}
N 550 -100 550 -60 { lab=VSS}
N 550 -60 550 -40 { lab=VSS}
N 550 -40 580 -40 { lab=VSS}
N 580 -100 580 -40 { lab=VSS}
N 550 -100 580 -100 { lab=VSS}
N 550 -160 550 -100 { lab=VBIAS}
N 400 -200 400 -160 { lab=VSS}
N 300 -300 300 -280 { lab=NET1}
C {sky130_fd_pr/nfet_01v8.sym} 180 -250 0 0 {name=M1
L=0.5
W=10
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 280 -250 0 0 {name=M2
L=0.5
W=20
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 380 -310 0 0 {name=M3
L=0.15
W=20
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 380 -190 0 0 {name=M4
L=0.15
W=10
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 480 -190 0 0 {name=M5
L=10
W=0.5
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 530 -130 0 0 {name=M6
L=2
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 200 -380 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 400 -120 0 0 {name=l2 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 550 -40 0 0 {name=l3 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 200 -120 0 0 {name=l4 sig_type=std_logic lab=SENSOR_IN}
C {devices/lab_pin.sym} 450 -260 0 1 {name=l5 sig_type=std_logic lab=VOUT}
C {devices/lab_pin.sym} 200 -200 0 0 {name=l6 sig_type=std_logic lab=VREF}
