module top ( 
    pi1, pi2,
    po0  );
    input  pi1, pi2;
    output po0;

    assign po0 = pi1 & pi2;
endmodule