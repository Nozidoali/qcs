.v a0 a1 a2 a3 b0 b1 b2 b3 c0 c1 c2 c3
.i a0 a1 a2 a3 b0 b1 b2 b3
BEGIN
X c3
H c3
S c3
Z c3
Z c2
S c2
Z c2
cnot c2 c3
S c3
Z c3
cnot c2 c3
H c2
S c2
Z c2
Z c1
X c1
S c1
Z c1
cnot c1 c2
S c2
Z c2
cnot c1 c2
H c1
S c1
Z c1
Z c0
S c0
Z c0
cnot c0 c1
S c1
Z c1
cnot c0 c1
H c0
S c3
Z c3
Z c2
cnot c2 c3
S c3
Z c3
cnot c2 c3
cnot c1 c3
S c3
Z c3
cnot c1 c3
cnot c1 c2
S c2
Z c2
cnot c1 c2
Z c0
S c0
Z c0
cnot c0 c3
S c3
Z c3
cnot c0 c3
cnot c0 c2
S c2
Z c2
cnot c0 c2
Z b3
S b3
Z b3
cnot b3 c2
S c2
Z c2
cnot b3 c2
Z b2
S b2
Z b2
cnot b2 c3
S c3
Z c3
cnot b2 c3
cnot b2 c1
S c1
Z c1
cnot b2 c1
cnot b2 c0
S c0
Z c0
cnot b2 c0
Z b1
cnot b1 b3
S b3
Z b3
cnot b1 b3
cnot b1 b2
S b2
Z b2
cnot b1 b2
cnot b0 c3
S c3
Z c3
cnot b0 c3
cnot b0 c1
S c1
Z c1
cnot b0 c1
cnot b0 c0
S c0
Z c0
cnot b0 c0
cnot b0 b3
S b3
Z b3
cnot b0 b3
cnot b0 b2
S b2
Z b2
cnot b0 b2
cnot b0 b1
S b1
Z b1
cnot b0 b1
Z a3
cnot a3 c3
S c3
Z c3
cnot a3 c3
cnot a3 b0
S b0
Z b0
cnot a3 b0
Z a2
cnot a2 c2
S c2
Z c2
cnot a2 c2
cnot a2 b2
S b2
Z b2
cnot a2 b2
Z a1
S a1
Z a1
cnot a1 b0
S b0
Z b0
cnot a1 b0
cnot a0 c3
S c3
Z c3
cnot a0 c3
cnot a0 b3
S b3
Z b3
cnot a0 b3
cnot a0 b2
S b2
Z b2
cnot a0 b2
cnot a0 b0
S b0
Z b0
cnot a0 b0
cnot b0 a3
cnot b1 a3
cnot c2 a3
T a3
cnot b0 a3
cnot b1 a3
cnot c2 a3
cnot b0 a3
cnot b1 a3
cnot c0 a3
cnot c1 a3
cnot c2 a3
T a3
cnot b0 a3
cnot b1 a3
cnot c0 a3
cnot c1 a3
cnot c2 a3
cnot b0 a3
cnot c0 a3
cnot c1 a3
cnot c2 a3
T a3
cnot b0 a3
cnot c0 a3
cnot c1 a3
cnot c2 a3
cnot b1 b0
cnot c0 b0
cnot c1 b0
cnot c2 b0
T b0
cnot b1 b0
cnot c0 b0
cnot c1 b0
cnot c2 b0
cnot b3 a2
cnot c0 a2
cnot c1 a2
T a2
cnot b3 a2
cnot c0 a2
cnot c1 a2
cnot b2 a2
cnot b3 a2
cnot c0 a2
cnot c1 a2
T a2
cnot b2 a2
cnot b3 a2
cnot c0 a2
cnot c1 a2
cnot c0 b2
cnot c1 b2
T b2
cnot c0 b2
cnot c1 b2
cnot c0 b0
cnot c1 b0
cnot c2 b0
T b0
cnot c0 b0
cnot c1 b0
cnot c2 b0
cnot b0 a1
cnot b3 a1
cnot c0 a1
cnot c1 a1
cnot c2 a1
T a1
cnot b0 a1
cnot b3 a1
cnot c0 a1
cnot c1 a1
cnot c2 a1
cnot c0 a1
cnot c1 a1
T a1
cnot c0 a1
cnot c1 a1
cnot b3 b0
cnot c0 b0
cnot c1 b0
cnot c2 b0
T b0
cnot b3 b0
cnot c0 b0
cnot c1 b0
cnot c2 b0
cnot b2 a3
cnot c1 a3
cnot c2 a3
T a3
cnot b2 a3
cnot c1 a3
cnot c2 a3
cnot c1 a3
cnot c2 a3
T a3
cnot c1 a3
cnot c2 a3
cnot b3 a2
cnot c1 a2
cnot c2 a2
T a2
cnot b3 a2
cnot c1 a2
cnot c2 a2
cnot b3 a3
cnot c2 a3
cnot c3 a3
T a3
cnot b3 a3
cnot c2 a3
cnot c3 a3
cnot b2 a3
cnot b3 a3
cnot c2 a3
T a3
cnot b2 a3
cnot b3 a3
cnot c2 a3
cnot b0 a3
cnot c2 a3
cnot c3 a3
T a3
cnot b0 a3
cnot c2 a3
cnot c3 a3
cnot b1 a2
T a2
cnot b1 a2
cnot b1 a2
cnot b2 a2
cnot b3 a2
cnot c1 a2
cnot c3 a2
T a2
cnot b1 a2
cnot b2 a2
cnot b3 a2
cnot c1 a2
cnot c3 a2
cnot b2 a2
cnot b3 a2
cnot c3 a2
T a2
cnot b2 a2
cnot b3 a2
cnot c3 a2
cnot b2 b1
cnot b3 b1
cnot c1 b1
cnot c3 b1
T b1
cnot b2 b1
cnot b3 b1
cnot c1 b1
cnot c3 b1
cnot b0 a1
cnot b2 a1
cnot c2 a1
cnot c3 a1
T a1
cnot b0 a1
cnot b2 a1
cnot c2 a1
cnot c3 a1
cnot b0 a1
cnot c2 a1
cnot c3 a1
T a1
cnot b0 a1
cnot c2 a1
cnot c3 a1
cnot b0 a0
cnot b2 a0
cnot c2 a0
cnot c3 a0
T a0
cnot b0 a0
cnot b2 a0
cnot c2 a0
cnot c3 a0
cnot b2 a0
cnot b3 a0
cnot c3 a0
T a0
cnot b2 a0
cnot b3 a0
cnot c3 a0
cnot b0 a2
T a2
cnot b0 a2
cnot b0 a2
cnot c2 a2
T a2
cnot b0 a2
cnot c2 a2
cnot b0 a1
cnot b1 a1
cnot c2 a1
T a1
cnot b0 a1
cnot b1 a1
cnot c2 a1
cnot b1 a1
cnot c2 a1
T a1
cnot b1 a1
cnot c2 a1
cnot b2 a0
cnot b3 a0
cnot c0 a0
cnot c3 a0
T a0
cnot b2 a0
cnot b3 a0
cnot c0 a0
cnot c3 a0
cnot b3 b2
cnot c0 b2
cnot c3 b2
T b2
cnot b3 b2
cnot c0 b2
cnot c3 b2
cnot c1 a1
cnot c2 a1
T a1
cnot c1 a1
cnot c2 a1
cnot c1 a1
T a1
cnot c1 a1
T c2
cnot b0 a0
cnot b1 a0
cnot c2 a0
T a0
cnot b0 a0
cnot b1 a0
cnot c2 a0
cnot b0 a0
cnot c0 a0
cnot c1 a0
T a0
cnot b0 a0
cnot c0 a0
cnot c1 a0
cnot c1 a0
T a0
cnot c1 a0
cnot c0 b0
cnot c1 b0
T b0
cnot c0 b0
cnot c1 b0
cnot b3 a0
cnot c3 a0
T a0
cnot b3 a0
cnot c3 a0
cnot b0 a0
cnot b1 a0
T a0
cnot b0 a0
cnot b1 a0
H c0
S c0
H c1
S c1
H c2
S c2
H c3
S c3
END