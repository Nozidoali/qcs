// Benchmark "top" written by ABC on Tue Apr 15 22:49:30 2025

module top ( 
    pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12,
    po0, po1, po2, po3, po4, po5  );
  input  pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12;
  output po0, po1, po2, po3, po4, po5;
  wire new_new_n18, new_new_n17, new_new_n19, new_new_n16, new_new_n20,
    new_new_n15, new_new_n21, new_new_n14, new_new_n22, new_new_n13,
    new_new_n23, new_new_n34, new_new_n32, new_new_n33, new_new_n35,
    new_new_n30, new_new_n31, new_new_n36, new_new_n28, new_new_n29,
    new_new_n37, new_new_n26, new_new_n27, new_new_n38, new_new_n24,
    new_new_n25, new_new_n39, new_new_n45, new_new_n44, new_new_n46,
    new_new_n43, new_new_n47, new_new_n42, new_new_n48, new_new_n41,
    new_new_n49, new_new_n40, new_new_n50, new_new_n56, new_new_n55,
    new_new_n57, new_new_n54, new_new_n58, new_new_n53, new_new_n59,
    new_new_n52, new_new_n60, new_new_n51, new_new_n61, new_new_n67,
    new_new_n66, new_new_n68, new_new_n65, new_new_n69, new_new_n64,
    new_new_n70, new_new_n63, new_new_n71, new_new_n62, new_new_n72,
    new_new_n78, new_new_n77, new_new_n79, new_new_n76, new_new_n80,
    new_new_n75, new_new_n81, new_new_n74, new_new_n82, new_new_n73,
    new_new_n83;
  assign new_new_n18 = pi1 & pi7;
  assign new_new_n17 = pi6 & pi8;
  assign new_new_n19 = ~new_new_n18 ^ ~new_new_n17;
  assign new_new_n16 = pi5 & pi9;
  assign new_new_n20 = ~new_new_n19 ^ ~new_new_n16;
  assign new_new_n15 = pi4 & pi10;
  assign new_new_n21 = ~new_new_n20 ^ ~new_new_n15;
  assign new_new_n14 = pi3 & pi11;
  assign new_new_n22 = ~new_new_n21 ^ ~new_new_n14;
  assign new_new_n13 = pi2 & pi12;
  assign new_new_n23 = ~new_new_n22 ^ ~new_new_n13;
  assign new_new_n34 = pi2 & pi7;
  assign new_new_n32 = ~pi6 ^ ~pi1;
  assign new_new_n33 = pi8 & new_new_n32;
  assign new_new_n35 = ~new_new_n34 ^ ~new_new_n33;
  assign new_new_n30 = ~pi6 ^ ~pi5;
  assign new_new_n31 = pi9 & new_new_n30;
  assign new_new_n36 = ~new_new_n35 ^ ~new_new_n31;
  assign new_new_n28 = ~pi5 ^ ~pi4;
  assign new_new_n29 = pi10 & new_new_n28;
  assign new_new_n37 = ~new_new_n36 ^ ~new_new_n29;
  assign new_new_n26 = ~pi4 ^ ~pi3;
  assign new_new_n27 = pi11 & new_new_n26;
  assign new_new_n38 = ~new_new_n37 ^ ~new_new_n27;
  assign new_new_n24 = ~pi3 ^ ~pi2;
  assign new_new_n25 = pi12 & new_new_n24;
  assign new_new_n39 = ~new_new_n38 ^ ~new_new_n25;
  assign new_new_n45 = pi3 & pi7;
  assign new_new_n44 = pi2 & pi8;
  assign new_new_n46 = ~new_new_n45 ^ ~new_new_n44;
  assign new_new_n43 = pi9 & new_new_n32;
  assign new_new_n47 = ~new_new_n46 ^ ~new_new_n43;
  assign new_new_n42 = pi10 & new_new_n30;
  assign new_new_n48 = ~new_new_n47 ^ ~new_new_n42;
  assign new_new_n41 = pi11 & new_new_n28;
  assign new_new_n49 = ~new_new_n48 ^ ~new_new_n41;
  assign new_new_n40 = pi12 & new_new_n26;
  assign new_new_n50 = ~new_new_n49 ^ ~new_new_n40;
  assign new_new_n56 = pi4 & pi7;
  assign new_new_n55 = pi3 & pi8;
  assign new_new_n57 = ~new_new_n56 ^ ~new_new_n55;
  assign new_new_n54 = pi2 & pi9;
  assign new_new_n58 = ~new_new_n57 ^ ~new_new_n54;
  assign new_new_n53 = pi10 & new_new_n32;
  assign new_new_n59 = ~new_new_n58 ^ ~new_new_n53;
  assign new_new_n52 = pi11 & new_new_n30;
  assign new_new_n60 = ~new_new_n59 ^ ~new_new_n52;
  assign new_new_n51 = pi12 & new_new_n28;
  assign new_new_n61 = ~new_new_n60 ^ ~new_new_n51;
  assign new_new_n67 = pi5 & pi7;
  assign new_new_n66 = pi4 & pi8;
  assign new_new_n68 = ~new_new_n67 ^ ~new_new_n66;
  assign new_new_n65 = pi3 & pi9;
  assign new_new_n69 = ~new_new_n68 ^ ~new_new_n65;
  assign new_new_n64 = pi2 & pi10;
  assign new_new_n70 = ~new_new_n69 ^ ~new_new_n64;
  assign new_new_n63 = pi11 & new_new_n32;
  assign new_new_n71 = ~new_new_n70 ^ ~new_new_n63;
  assign new_new_n62 = pi12 & new_new_n30;
  assign new_new_n72 = ~new_new_n71 ^ ~new_new_n62;
  assign new_new_n78 = pi6 & pi7;
  assign new_new_n77 = pi5 & pi8;
  assign new_new_n79 = ~new_new_n78 ^ ~new_new_n77;
  assign new_new_n76 = pi4 & pi9;
  assign new_new_n80 = ~new_new_n79 ^ ~new_new_n76;
  assign new_new_n75 = pi3 & pi10;
  assign new_new_n81 = ~new_new_n80 ^ ~new_new_n75;
  assign new_new_n74 = pi2 & pi11;
  assign new_new_n82 = ~new_new_n81 ^ ~new_new_n74;
  assign new_new_n73 = pi12 & new_new_n32;
  assign new_new_n83 = ~new_new_n82 ^ ~new_new_n73;
  assign po0 = new_new_n23;
  assign po1 = new_new_n39;
  assign po2 = new_new_n50;
  assign po3 = new_new_n61;
  assign po4 = new_new_n72;
  assign po5 = new_new_n83;
endmodule


