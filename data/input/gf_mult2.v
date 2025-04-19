// Benchmark "top" written by ABC on Sat Apr 19 10:41:29 2025

module top ( 
    pi1, pi2, pi3, pi4,
    po0, po1  );
  input  pi1, pi2, pi3, pi4;
  output po0, po1;
  wire new_new_n6, new_new_n5, new_new_n7, new_new_n10, new_new_n8,
    new_new_n9, new_new_n11;
  assign new_new_n6 = pi1 & pi3;
  assign new_new_n5 = pi2 & pi4;
  assign new_new_n7 = ~new_new_n6 ^ ~new_new_n5;
  assign new_new_n10 = pi2 & pi3;
  assign new_new_n8 = pi1 & pi4;
  assign new_new_n9 = ~new_new_n8 ^ ~new_new_n5;
  assign new_new_n11 = ~new_new_n10 ^ ~new_new_n9;
  assign po0 = new_new_n7;
  assign po1 = new_new_n11;
endmodule


