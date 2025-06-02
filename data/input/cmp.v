module top (  a, b  );
    input  a, b;
    output lt, eq, gt;

    assign lt = a & ~b;
    assign eq = ~a ^ ~b;
    assign gt = ~a & b;

endmodule