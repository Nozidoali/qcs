// Benchmark "top" written by ABC on Tue Apr 15 22:49:31 2025

module top ( 
    pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12, pi13,
    pi14,
    po0, po1, po2, po3, po4, po5, po6  );
  input  pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12,
    pi13, pi14;
  output po0, po1, po2, po3, po4, po5, po6;
  wire new_new_n21, new_new_n20, new_new_n22, new_new_n19, new_new_n23,
    new_new_n18, new_new_n24, new_new_n17, new_new_n25, new_new_n16,
    new_new_n26, new_new_n15, new_new_n27, new_new_n40, new_new_n38,
    new_new_n39, new_new_n41, new_new_n36, new_new_n37, new_new_n42,
    new_new_n34, new_new_n35, new_new_n43, new_new_n32, new_new_n33,
    new_new_n44, new_new_n30, new_new_n31, new_new_n45, new_new_n28,
    new_new_n29, new_new_n46, new_new_n53, new_new_n52, new_new_n54,
    new_new_n51, new_new_n55, new_new_n50, new_new_n56, new_new_n49,
    new_new_n57, new_new_n48, new_new_n58, new_new_n47, new_new_n59,
    new_new_n66, new_new_n65, new_new_n67, new_new_n64, new_new_n68,
    new_new_n63, new_new_n69, new_new_n62, new_new_n70, new_new_n61,
    new_new_n71, new_new_n60, new_new_n72, new_new_n79, new_new_n78,
    new_new_n80, new_new_n77, new_new_n81, new_new_n76, new_new_n82,
    new_new_n75, new_new_n83, new_new_n74, new_new_n84, new_new_n73,
    new_new_n85, new_new_n92, new_new_n91, new_new_n93, new_new_n90,
    new_new_n94, new_new_n89, new_new_n95, new_new_n88, new_new_n96,
    new_new_n87, new_new_n97, new_new_n86, new_new_n98, new_new_n105,
    new_new_n104, new_new_n106, new_new_n103, new_new_n107, new_new_n102,
    new_new_n108, new_new_n101, new_new_n109, new_new_n100, new_new_n110,
    new_new_n99, new_new_n111;
  assign new_new_n21 = pi1 & pi8;
  assign new_new_n20 = pi7 & pi9;
  assign new_new_n22 = ~new_new_n21 ^ ~new_new_n20;
  assign new_new_n19 = pi6 & pi10;
  assign new_new_n23 = ~new_new_n22 ^ ~new_new_n19;
  assign new_new_n18 = pi5 & pi11;
  assign new_new_n24 = ~new_new_n23 ^ ~new_new_n18;
  assign new_new_n17 = pi4 & pi12;
  assign new_new_n25 = ~new_new_n24 ^ ~new_new_n17;
  assign new_new_n16 = pi3 & pi13;
  assign new_new_n26 = ~new_new_n25 ^ ~new_new_n16;
  assign new_new_n15 = pi2 & pi14;
  assign new_new_n27 = ~new_new_n26 ^ ~new_new_n15;
  assign new_new_n40 = pi2 & pi8;
  assign new_new_n38 = ~pi7 ^ ~pi1;
  assign new_new_n39 = pi9 & new_new_n38;
  assign new_new_n41 = ~new_new_n40 ^ ~new_new_n39;
  assign new_new_n36 = ~pi7 ^ ~pi6;
  assign new_new_n37 = pi10 & new_new_n36;
  assign new_new_n42 = ~new_new_n41 ^ ~new_new_n37;
  assign new_new_n34 = ~pi6 ^ ~pi5;
  assign new_new_n35 = pi11 & new_new_n34;
  assign new_new_n43 = ~new_new_n42 ^ ~new_new_n35;
  assign new_new_n32 = ~pi5 ^ ~pi4;
  assign new_new_n33 = pi12 & new_new_n32;
  assign new_new_n44 = ~new_new_n43 ^ ~new_new_n33;
  assign new_new_n30 = ~pi4 ^ ~pi3;
  assign new_new_n31 = pi13 & new_new_n30;
  assign new_new_n45 = ~new_new_n44 ^ ~new_new_n31;
  assign new_new_n28 = ~pi3 ^ ~pi2;
  assign new_new_n29 = pi14 & new_new_n28;
  assign new_new_n46 = ~new_new_n45 ^ ~new_new_n29;
  assign new_new_n53 = pi3 & pi8;
  assign new_new_n52 = pi2 & pi9;
  assign new_new_n54 = ~new_new_n53 ^ ~new_new_n52;
  assign new_new_n51 = pi10 & new_new_n38;
  assign new_new_n55 = ~new_new_n54 ^ ~new_new_n51;
  assign new_new_n50 = pi11 & new_new_n36;
  assign new_new_n56 = ~new_new_n55 ^ ~new_new_n50;
  assign new_new_n49 = pi12 & new_new_n34;
  assign new_new_n57 = ~new_new_n56 ^ ~new_new_n49;
  assign new_new_n48 = pi13 & new_new_n32;
  assign new_new_n58 = ~new_new_n57 ^ ~new_new_n48;
  assign new_new_n47 = pi14 & new_new_n30;
  assign new_new_n59 = ~new_new_n58 ^ ~new_new_n47;
  assign new_new_n66 = pi4 & pi8;
  assign new_new_n65 = pi3 & pi9;
  assign new_new_n67 = ~new_new_n66 ^ ~new_new_n65;
  assign new_new_n64 = pi2 & pi10;
  assign new_new_n68 = ~new_new_n67 ^ ~new_new_n64;
  assign new_new_n63 = pi11 & new_new_n38;
  assign new_new_n69 = ~new_new_n68 ^ ~new_new_n63;
  assign new_new_n62 = pi12 & new_new_n36;
  assign new_new_n70 = ~new_new_n69 ^ ~new_new_n62;
  assign new_new_n61 = pi13 & new_new_n34;
  assign new_new_n71 = ~new_new_n70 ^ ~new_new_n61;
  assign new_new_n60 = pi14 & new_new_n32;
  assign new_new_n72 = ~new_new_n71 ^ ~new_new_n60;
  assign new_new_n79 = pi5 & pi8;
  assign new_new_n78 = pi4 & pi9;
  assign new_new_n80 = ~new_new_n79 ^ ~new_new_n78;
  assign new_new_n77 = pi3 & pi10;
  assign new_new_n81 = ~new_new_n80 ^ ~new_new_n77;
  assign new_new_n76 = pi2 & pi11;
  assign new_new_n82 = ~new_new_n81 ^ ~new_new_n76;
  assign new_new_n75 = pi12 & new_new_n38;
  assign new_new_n83 = ~new_new_n82 ^ ~new_new_n75;
  assign new_new_n74 = pi13 & new_new_n36;
  assign new_new_n84 = ~new_new_n83 ^ ~new_new_n74;
  assign new_new_n73 = pi14 & new_new_n34;
  assign new_new_n85 = ~new_new_n84 ^ ~new_new_n73;
  assign new_new_n92 = pi6 & pi8;
  assign new_new_n91 = pi5 & pi9;
  assign new_new_n93 = ~new_new_n92 ^ ~new_new_n91;
  assign new_new_n90 = pi4 & pi10;
  assign new_new_n94 = ~new_new_n93 ^ ~new_new_n90;
  assign new_new_n89 = pi3 & pi11;
  assign new_new_n95 = ~new_new_n94 ^ ~new_new_n89;
  assign new_new_n88 = pi2 & pi12;
  assign new_new_n96 = ~new_new_n95 ^ ~new_new_n88;
  assign new_new_n87 = pi13 & new_new_n38;
  assign new_new_n97 = ~new_new_n96 ^ ~new_new_n87;
  assign new_new_n86 = pi14 & new_new_n36;
  assign new_new_n98 = ~new_new_n97 ^ ~new_new_n86;
  assign new_new_n105 = pi7 & pi8;
  assign new_new_n104 = pi6 & pi9;
  assign new_new_n106 = ~new_new_n105 ^ ~new_new_n104;
  assign new_new_n103 = pi5 & pi10;
  assign new_new_n107 = ~new_new_n106 ^ ~new_new_n103;
  assign new_new_n102 = pi4 & pi11;
  assign new_new_n108 = ~new_new_n107 ^ ~new_new_n102;
  assign new_new_n101 = pi3 & pi12;
  assign new_new_n109 = ~new_new_n108 ^ ~new_new_n101;
  assign new_new_n100 = pi2 & pi13;
  assign new_new_n110 = ~new_new_n109 ^ ~new_new_n100;
  assign new_new_n99 = pi14 & new_new_n38;
  assign new_new_n111 = ~new_new_n110 ^ ~new_new_n99;
  assign po0 = new_new_n27;
  assign po1 = new_new_n46;
  assign po2 = new_new_n59;
  assign po3 = new_new_n72;
  assign po4 = new_new_n85;
  assign po5 = new_new_n98;
  assign po6 = new_new_n111;
endmodule


