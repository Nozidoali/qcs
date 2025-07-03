.v q0 q1 q2 q3 q4 q5
.i q0 q1 q2 q3

BEGIN
H q5
H q4
cnot q2 q0
T q0
cnot q4 q0
T q0
cnot q4 q0
cnot q4 q0
cnot q2 q0
T q0
cnot q4 q0
cnot q2 q0
cnot q4 q2
T q2
cnot q4 q2
cnot q4 q1
cnot q3 q1
T q1
cnot q4 q1
cnot q3 q1
cnot q4 q1
T q1
cnot q4 q1
cnot q4 q3
T q3
cnot q4 q3
cnot q2 q1
T q1
cnot q2 q1
cnot q5 q1
cnot q2 q1
T q1
cnot q5 q1
cnot q2 q1
cnot q5 q2
T q2
cnot q5 q2
cnot q3 q0
cnot q2 q0
T q0
cnot q3 q0
cnot q2 q0
cnot q5 q0
cnot q2 q0
cnot q3 q0
T q0
cnot q5 q0
cnot q2 q0
cnot q3 q0
cnot q5 q0
cnot q2 q0
T q0
cnot q5 q0
cnot q2 q0
T q1
T q3
T q5
cnot q5 q1
cnot q3 q1
T q1
cnot q5 q1
cnot q3 q1
S q5
H q5
S q4
H q4
Z q3
cnot q3 q5
cnot q3 q4
Z q2
cnot q2 q3
S q3
cnot q2 q3
Z q1
S q1
cnot q1 q3
S q3
cnot q1 q3
cnot q1 q2
S q2
cnot q1 q2
cnot q1 q5
cnot q1 q4
cnot q0 q3
S q3
cnot q0 q3
cnot q0 q5
cnot q0 q4
cnot q2 q0
END