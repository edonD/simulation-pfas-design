v {xschem version=2.9.9 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 100 -200 100 -180 { lab=#net1}
N 100 -120 100 -100 { lab=VSS}
N 100 -100 130 -100 { lab=VSS}
N 130 -120 130 -100 { lab=VSS}
N 100 -120 130 -120 { lab=VSS}
N 100 -200 100 -180 { lab=#net1}
N 100 -280 100 -260 { lab=VDD}
N 100 -260 130 -260 { lab=VDD}
N 130 -280 130 -260 { lab=VDD}
N 100 -280 130 -280 { lab=VDD}
N 100 -300 100 -280 { lab=VDD}
N 250 -300 250 -280 { lab=VDD}
N 250 -220 250 -200 { lab=#net2}
N 250 -140 250 -120 { lab=#net1}
N 250 -120 100 -120 { lab=#net1}
N 100 -180 100 -120 { lab=#net1}
N 250 -120 250 -100 { lab=#net1}
N 400 -380 400 -340 { lab=VDD}
N 400 -280 400 -260 { lab=VOUT}
N 400 -200 400 -160 { lab=VSS}
N 400 -160 430 -160 { lab=VSS}
N 430 -200 430 -160 { lab=VSS}
N 400 -200 430 -200 { lab=VSS}
N 400 -260 450 -260 { lab=VOUT}
N 250 -200 250 -140 { lab=#net2}
N 250 -200 400 -200 { lab=#net2}
N 500 -120 500 -80 { lab=VSS}
N 500 -80 530 -80 { lab=VSS}
N 530 -120 530 -80 { lab=VSS}
N 500 -120 530 -120 { lab=VSS}
N 500 -200 500 -120 { lab=VBIAS}
N 400 -200 400 -160 { lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 80 -150 0 0 {name=M1
L=0.5
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 80 -230 0 0 {name=M2
L=0.5
W=4
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 230 -170 0 0 {name=M3
L=0.15
W=4
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 230 -250 0 0 {name=M4
L=0.15
W=8
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 380 -310 0 0 {name=M5
L=0.15
W=10
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 380 -230 0 0 {name=M6
L=0.15
W=5
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 480 -150 0 0 {name=M7
L=2
W=2
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 100 -300 0 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 250 -300 0 0 {name=l2 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 400 -380 0 0 {name=l3 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 100 -100 0 0 {name=l4 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 500 -80 0 0 {name=l5 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 400 -160 0 0 {name=l6 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 450 -260 0 1 {name=l7 sig_type=std_logic lab=VOUT}
C {devices/lab_pin.sym} 80 -150 0 0 {name=l8 sig_type=std_logic lab=STEP}
C {devices/lab_pin.sym} 230 -170 0 0 {name=l9 sig_type=std_logic lab=CLK}
C {devices/lab_pin.sym} 230 -250 0 0 {name=l10 sig_type=std_logic lab=CLK}
