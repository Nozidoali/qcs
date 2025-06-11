module top ( 
    pi1, pi2, pi3,
    po0  );
    input  pi1, pi2, pi3;
    output po0;

    assign n1 = pi1 & pi3;
    assign n2 = pi2 & pi2;

    assign po0 = n1 ^ n2;
endmodule