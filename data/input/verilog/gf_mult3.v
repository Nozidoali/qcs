// Benchmark "top" written by ABC on Sat Apr 19 10:41:29 2025

module top ( 
    pi1, pi2, pi3, pi4, pi5, pi6,
    po0, po1, po2  );
  input  pi1, pi2, pi3, pi4, pi5, pi6;
  output po0, po1, po2;
  wire new_new_n9, new_new_n8, new_new_n10, new_new_n7, new_new_n11,
    new_new_n16, new_new_n14, new_new_n15, new_new_n17, new_new_n12,
    new_new_n13, new_new_n18, new_new_n21, new_new_n20, new_new_n22,
    new_new_n19, new_new_n23;
  assign new_new_n9 = pi1 & pi4;
  assign new_new_n8 = pi3 & pi5;
  assign new_new_n10 = ~new_new_n9 ^ ~new_new_n8;
  assign new_new_n7 = pi2 & pi6;
  assign new_new_n11 = ~new_new_n10 ^ ~new_new_n7;
  assign new_new_n16 = pi2 & pi4;
  assign new_new_n14 = ~pi3 ^ ~pi1;
  assign new_new_n15 = pi5 & new_new_n14;
  assign new_new_n17 = ~new_new_n16 ^ ~new_new_n15;
  assign new_new_n12 = ~pi3 ^ ~pi2;
  assign new_new_n13 = pi6 & new_new_n12;
  assign new_new_n18 = ~new_new_n17 ^ ~new_new_n13;
  assign new_new_n21 = pi3 & pi4;
  assign new_new_n20 = pi2 & pi5;
  assign new_new_n22 = ~new_new_n21 ^ ~new_new_n20;
  assign new_new_n19 = pi6 & new_new_n14;
  assign new_new_n23 = ~new_new_n22 ^ ~new_new_n19;
  assign po0 = new_new_n11;
  assign po1 = new_new_n18;
  assign po2 = new_new_n23;
endmodule


