.v  q0 q1 q2
.i  q0 q1 q2

BEGIN

T    q0
T    q1
T    q2

tof  q0 q1
T q1
S q1
Z q1
tof  q0 q1

tof  q0 q2
T q2
S q2
Z q2
tof  q1 q2

T    q2
tof  q0 q2
T q2
S q2
Z q2
tof  q1 q2

H    q2
T    q2

END
