// Benchmark "top" written by ABC on Tue Apr 15 22:49:29 2025

module top ( 
    pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8,
    po0, po1, po2, po3  );
  input  pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8;
  output po0, po1, po2, po3;
  wire new_new_n12, new_new_n11, new_new_n13, new_new_n10, new_new_n14,
    new_new_n9, new_new_n15, new_new_n22, new_new_n20, new_new_n21,
    new_new_n23, new_new_n18, new_new_n19, new_new_n24, new_new_n16,
    new_new_n17, new_new_n25, new_new_n29, new_new_n28, new_new_n30,
    new_new_n27, new_new_n31, new_new_n26, new_new_n32, new_new_n36,
    new_new_n35, new_new_n37, new_new_n34, new_new_n38, new_new_n33,
    new_new_n39;
  assign new_new_n12 = pi1 & pi5;
  assign new_new_n11 = pi4 & pi6;
  assign new_new_n13 = ~new_new_n12 ^ ~new_new_n11;
  assign new_new_n10 = pi3 & pi7;
  assign new_new_n14 = ~new_new_n13 ^ ~new_new_n10;
  assign new_new_n9 = pi2 & pi8;
  assign new_new_n15 = ~new_new_n14 ^ ~new_new_n9;
  assign new_new_n22 = pi2 & pi5;
  assign new_new_n20 = ~pi4 ^ ~pi1;
  assign new_new_n21 = pi6 & new_new_n20;
  assign new_new_n23 = ~new_new_n22 ^ ~new_new_n21;
  assign new_new_n18 = ~pi4 ^ ~pi3;
  assign new_new_n19 = pi7 & new_new_n18;
  assign new_new_n24 = ~new_new_n23 ^ ~new_new_n19;
  assign new_new_n16 = ~pi3 ^ ~pi2;
  assign new_new_n17 = pi8 & new_new_n16;
  assign new_new_n25 = ~new_new_n24 ^ ~new_new_n17;
  assign new_new_n29 = pi3 & pi5;
  assign new_new_n28 = pi2 & pi6;
  assign new_new_n30 = ~new_new_n29 ^ ~new_new_n28;
  assign new_new_n27 = pi7 & new_new_n20;
  assign new_new_n31 = ~new_new_n30 ^ ~new_new_n27;
  assign new_new_n26 = pi8 & new_new_n18;
  assign new_new_n32 = ~new_new_n31 ^ ~new_new_n26;
  assign new_new_n36 = pi4 & pi5;
  assign new_new_n35 = pi3 & pi6;
  assign new_new_n37 = ~new_new_n36 ^ ~new_new_n35;
  assign new_new_n34 = pi2 & pi7;
  assign new_new_n38 = ~new_new_n37 ^ ~new_new_n34;
  assign new_new_n33 = pi8 & new_new_n20;
  assign new_new_n39 = ~new_new_n38 ^ ~new_new_n33;
  assign po0 = new_new_n15;
  assign po1 = new_new_n25;
  assign po2 = new_new_n32;
  assign po3 = new_new_n39;
endmodule


