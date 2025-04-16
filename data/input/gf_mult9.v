// Benchmark "top" written by ABC on Tue Apr 15 22:49:31 2025

module top ( 
    pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12, pi13,
    pi14, pi15, pi16, pi17, pi18,
    po0, po1, po2, po3, po4, po5, po6, po7, po8  );
  input  pi1, pi2, pi3, pi4, pi5, pi6, pi7, pi8, pi9, pi10, pi11, pi12,
    pi13, pi14, pi15, pi16, pi17, pi18;
  output po0, po1, po2, po3, po4, po5, po6, po7, po8;
  wire new_new_n30, new_new_n29, new_new_n31, new_new_n28, new_new_n32,
    new_new_n27, new_new_n33, new_new_n26, new_new_n34, new_new_n25,
    new_new_n35, new_new_n23, new_new_n24, new_new_n36, new_new_n21,
    new_new_n22, new_new_n37, new_new_n19, new_new_n20, new_new_n38,
    new_new_n47, new_new_n46, new_new_n48, new_new_n45, new_new_n49,
    new_new_n44, new_new_n50, new_new_n43, new_new_n51, new_new_n42,
    new_new_n52, new_new_n41, new_new_n53, new_new_n40, new_new_n54,
    new_new_n39, new_new_n55, new_new_n64, new_new_n63, new_new_n65,
    new_new_n62, new_new_n66, new_new_n61, new_new_n67, new_new_n60,
    new_new_n68, new_new_n59, new_new_n69, new_new_n58, new_new_n70,
    new_new_n57, new_new_n71, new_new_n56, new_new_n72, new_new_n81,
    new_new_n80, new_new_n82, new_new_n79, new_new_n83, new_new_n78,
    new_new_n84, new_new_n77, new_new_n85, new_new_n76, new_new_n86,
    new_new_n75, new_new_n87, new_new_n74, new_new_n88, new_new_n73,
    new_new_n89, new_new_n103, new_new_n102, new_new_n104, new_new_n101,
    new_new_n105, new_new_n100, new_new_n106, new_new_n98, new_new_n99,
    new_new_n107, new_new_n96, new_new_n97, new_new_n108, new_new_n94,
    new_new_n95, new_new_n109, new_new_n92, new_new_n93, new_new_n110,
    new_new_n90, new_new_n91, new_new_n111, new_new_n120, new_new_n119,
    new_new_n121, new_new_n118, new_new_n122, new_new_n117, new_new_n123,
    new_new_n116, new_new_n124, new_new_n115, new_new_n125, new_new_n114,
    new_new_n126, new_new_n113, new_new_n127, new_new_n112, new_new_n128,
    new_new_n137, new_new_n136, new_new_n138, new_new_n135, new_new_n139,
    new_new_n134, new_new_n140, new_new_n133, new_new_n141, new_new_n132,
    new_new_n142, new_new_n131, new_new_n143, new_new_n130, new_new_n144,
    new_new_n129, new_new_n145, new_new_n154, new_new_n153, new_new_n155,
    new_new_n152, new_new_n156, new_new_n151, new_new_n157, new_new_n150,
    new_new_n158, new_new_n149, new_new_n159, new_new_n148, new_new_n160,
    new_new_n147, new_new_n161, new_new_n146, new_new_n162, new_new_n171,
    new_new_n170, new_new_n172, new_new_n169, new_new_n173, new_new_n168,
    new_new_n174, new_new_n167, new_new_n175, new_new_n166, new_new_n176,
    new_new_n165, new_new_n177, new_new_n164, new_new_n178, new_new_n163,
    new_new_n179;
  assign new_new_n30 = pi1 & pi10;
  assign new_new_n29 = pi9 & pi11;
  assign new_new_n31 = ~new_new_n30 ^ ~new_new_n29;
  assign new_new_n28 = pi8 & pi12;
  assign new_new_n32 = ~new_new_n31 ^ ~new_new_n28;
  assign new_new_n27 = pi7 & pi13;
  assign new_new_n33 = ~new_new_n32 ^ ~new_new_n27;
  assign new_new_n26 = pi6 & pi14;
  assign new_new_n34 = ~new_new_n33 ^ ~new_new_n26;
  assign new_new_n25 = pi5 & pi15;
  assign new_new_n35 = ~new_new_n34 ^ ~new_new_n25;
  assign new_new_n23 = ~pi9 ^ ~pi4;
  assign new_new_n24 = pi16 & new_new_n23;
  assign new_new_n36 = ~new_new_n35 ^ ~new_new_n24;
  assign new_new_n21 = ~pi8 ^ ~pi3;
  assign new_new_n22 = pi17 & new_new_n21;
  assign new_new_n37 = ~new_new_n36 ^ ~new_new_n22;
  assign new_new_n19 = ~pi7 ^ ~pi2;
  assign new_new_n20 = pi18 & new_new_n19;
  assign new_new_n38 = ~new_new_n37 ^ ~new_new_n20;
  assign new_new_n47 = pi2 & pi10;
  assign new_new_n46 = pi1 & pi11;
  assign new_new_n48 = ~new_new_n47 ^ ~new_new_n46;
  assign new_new_n45 = pi9 & pi12;
  assign new_new_n49 = ~new_new_n48 ^ ~new_new_n45;
  assign new_new_n44 = pi8 & pi13;
  assign new_new_n50 = ~new_new_n49 ^ ~new_new_n44;
  assign new_new_n43 = pi7 & pi14;
  assign new_new_n51 = ~new_new_n50 ^ ~new_new_n43;
  assign new_new_n42 = pi6 & pi15;
  assign new_new_n52 = ~new_new_n51 ^ ~new_new_n42;
  assign new_new_n41 = pi5 & pi16;
  assign new_new_n53 = ~new_new_n52 ^ ~new_new_n41;
  assign new_new_n40 = pi17 & new_new_n23;
  assign new_new_n54 = ~new_new_n53 ^ ~new_new_n40;
  assign new_new_n39 = pi18 & new_new_n21;
  assign new_new_n55 = ~new_new_n54 ^ ~new_new_n39;
  assign new_new_n64 = pi3 & pi10;
  assign new_new_n63 = pi2 & pi11;
  assign new_new_n65 = ~new_new_n64 ^ ~new_new_n63;
  assign new_new_n62 = pi1 & pi12;
  assign new_new_n66 = ~new_new_n65 ^ ~new_new_n62;
  assign new_new_n61 = pi9 & pi13;
  assign new_new_n67 = ~new_new_n66 ^ ~new_new_n61;
  assign new_new_n60 = pi8 & pi14;
  assign new_new_n68 = ~new_new_n67 ^ ~new_new_n60;
  assign new_new_n59 = pi7 & pi15;
  assign new_new_n69 = ~new_new_n68 ^ ~new_new_n59;
  assign new_new_n58 = pi6 & pi16;
  assign new_new_n70 = ~new_new_n69 ^ ~new_new_n58;
  assign new_new_n57 = pi5 & pi17;
  assign new_new_n71 = ~new_new_n70 ^ ~new_new_n57;
  assign new_new_n56 = pi18 & new_new_n23;
  assign new_new_n72 = ~new_new_n71 ^ ~new_new_n56;
  assign new_new_n81 = pi4 & pi10;
  assign new_new_n80 = pi3 & pi11;
  assign new_new_n82 = ~new_new_n81 ^ ~new_new_n80;
  assign new_new_n79 = pi2 & pi12;
  assign new_new_n83 = ~new_new_n82 ^ ~new_new_n79;
  assign new_new_n78 = pi1 & pi13;
  assign new_new_n84 = ~new_new_n83 ^ ~new_new_n78;
  assign new_new_n77 = pi9 & pi14;
  assign new_new_n85 = ~new_new_n84 ^ ~new_new_n77;
  assign new_new_n76 = pi8 & pi15;
  assign new_new_n86 = ~new_new_n85 ^ ~new_new_n76;
  assign new_new_n75 = pi7 & pi16;
  assign new_new_n87 = ~new_new_n86 ^ ~new_new_n75;
  assign new_new_n74 = pi6 & pi17;
  assign new_new_n88 = ~new_new_n87 ^ ~new_new_n74;
  assign new_new_n73 = pi5 & pi18;
  assign new_new_n89 = ~new_new_n88 ^ ~new_new_n73;
  assign new_new_n103 = pi5 & pi10;
  assign new_new_n102 = pi11 & new_new_n23;
  assign new_new_n104 = ~new_new_n103 ^ ~new_new_n102;
  assign new_new_n101 = pi12 & new_new_n21;
  assign new_new_n105 = ~new_new_n104 ^ ~new_new_n101;
  assign new_new_n100 = pi13 & new_new_n19;
  assign new_new_n106 = ~new_new_n105 ^ ~new_new_n100;
  assign new_new_n98 = ~pi6 ^ ~pi1;
  assign new_new_n99 = pi14 & new_new_n98;
  assign new_new_n107 = ~new_new_n106 ^ ~new_new_n99;
  assign new_new_n96 = ~pi9 ^ ~pi5;
  assign new_new_n97 = pi15 & new_new_n96;
  assign new_new_n108 = ~new_new_n107 ^ ~new_new_n97;
  assign new_new_n94 = ~new_new_n23 ^ ~pi8;
  assign new_new_n95 = pi16 & new_new_n94;
  assign new_new_n109 = ~new_new_n108 ^ ~new_new_n95;
  assign new_new_n92 = ~new_new_n21 ^ ~pi7;
  assign new_new_n93 = pi17 & new_new_n92;
  assign new_new_n110 = ~new_new_n109 ^ ~new_new_n93;
  assign new_new_n90 = ~new_new_n19 ^ ~pi6;
  assign new_new_n91 = pi18 & new_new_n90;
  assign new_new_n111 = ~new_new_n110 ^ ~new_new_n91;
  assign new_new_n120 = pi6 & pi10;
  assign new_new_n119 = pi5 & pi11;
  assign new_new_n121 = ~new_new_n120 ^ ~new_new_n119;
  assign new_new_n118 = pi12 & new_new_n23;
  assign new_new_n122 = ~new_new_n121 ^ ~new_new_n118;
  assign new_new_n117 = pi13 & new_new_n21;
  assign new_new_n123 = ~new_new_n122 ^ ~new_new_n117;
  assign new_new_n116 = pi14 & new_new_n19;
  assign new_new_n124 = ~new_new_n123 ^ ~new_new_n116;
  assign new_new_n115 = pi15 & new_new_n98;
  assign new_new_n125 = ~new_new_n124 ^ ~new_new_n115;
  assign new_new_n114 = pi16 & new_new_n96;
  assign new_new_n126 = ~new_new_n125 ^ ~new_new_n114;
  assign new_new_n113 = pi17 & new_new_n94;
  assign new_new_n127 = ~new_new_n126 ^ ~new_new_n113;
  assign new_new_n112 = pi18 & new_new_n92;
  assign new_new_n128 = ~new_new_n127 ^ ~new_new_n112;
  assign new_new_n137 = pi7 & pi10;
  assign new_new_n136 = pi6 & pi11;
  assign new_new_n138 = ~new_new_n137 ^ ~new_new_n136;
  assign new_new_n135 = pi5 & pi12;
  assign new_new_n139 = ~new_new_n138 ^ ~new_new_n135;
  assign new_new_n134 = pi13 & new_new_n23;
  assign new_new_n140 = ~new_new_n139 ^ ~new_new_n134;
  assign new_new_n133 = pi14 & new_new_n21;
  assign new_new_n141 = ~new_new_n140 ^ ~new_new_n133;
  assign new_new_n132 = pi15 & new_new_n19;
  assign new_new_n142 = ~new_new_n141 ^ ~new_new_n132;
  assign new_new_n131 = pi16 & new_new_n98;
  assign new_new_n143 = ~new_new_n142 ^ ~new_new_n131;
  assign new_new_n130 = pi17 & new_new_n96;
  assign new_new_n144 = ~new_new_n143 ^ ~new_new_n130;
  assign new_new_n129 = pi18 & new_new_n94;
  assign new_new_n145 = ~new_new_n144 ^ ~new_new_n129;
  assign new_new_n154 = pi8 & pi10;
  assign new_new_n153 = pi7 & pi11;
  assign new_new_n155 = ~new_new_n154 ^ ~new_new_n153;
  assign new_new_n152 = pi6 & pi12;
  assign new_new_n156 = ~new_new_n155 ^ ~new_new_n152;
  assign new_new_n151 = pi5 & pi13;
  assign new_new_n157 = ~new_new_n156 ^ ~new_new_n151;
  assign new_new_n150 = pi14 & new_new_n23;
  assign new_new_n158 = ~new_new_n157 ^ ~new_new_n150;
  assign new_new_n149 = pi15 & new_new_n21;
  assign new_new_n159 = ~new_new_n158 ^ ~new_new_n149;
  assign new_new_n148 = pi16 & new_new_n19;
  assign new_new_n160 = ~new_new_n159 ^ ~new_new_n148;
  assign new_new_n147 = pi17 & new_new_n98;
  assign new_new_n161 = ~new_new_n160 ^ ~new_new_n147;
  assign new_new_n146 = pi18 & new_new_n96;
  assign new_new_n162 = ~new_new_n161 ^ ~new_new_n146;
  assign new_new_n171 = pi9 & pi10;
  assign new_new_n170 = pi8 & pi11;
  assign new_new_n172 = ~new_new_n171 ^ ~new_new_n170;
  assign new_new_n169 = pi7 & pi12;
  assign new_new_n173 = ~new_new_n172 ^ ~new_new_n169;
  assign new_new_n168 = pi6 & pi13;
  assign new_new_n174 = ~new_new_n173 ^ ~new_new_n168;
  assign new_new_n167 = pi5 & pi14;
  assign new_new_n175 = ~new_new_n174 ^ ~new_new_n167;
  assign new_new_n166 = pi15 & new_new_n23;
  assign new_new_n176 = ~new_new_n175 ^ ~new_new_n166;
  assign new_new_n165 = pi16 & new_new_n21;
  assign new_new_n177 = ~new_new_n176 ^ ~new_new_n165;
  assign new_new_n164 = pi17 & new_new_n19;
  assign new_new_n178 = ~new_new_n177 ^ ~new_new_n164;
  assign new_new_n163 = pi18 & new_new_n98;
  assign new_new_n179 = ~new_new_n178 ^ ~new_new_n163;
  assign po0 = new_new_n38;
  assign po1 = new_new_n55;
  assign po2 = new_new_n72;
  assign po3 = new_new_n89;
  assign po4 = new_new_n111;
  assign po5 = new_new_n128;
  assign po6 = new_new_n145;
  assign po7 = new_new_n162;
  assign po8 = new_new_n179;
endmodule


