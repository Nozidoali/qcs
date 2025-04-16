// Benchmark "ex" written by ABC on Wed Apr  2 15:58:04 2025

module ex ( 
    a, b, c, d, e, f, g, h,
    F0, F1, F2, F3  );
  input  a, b, c, d, e, f, g, h;
  output F0, F1, F2, F3;
  wire new_n13, new_n14, new_n15, new_n16, new_n17, new_n18, new_n19,
    new_n20, new_n21, new_n22, new_n23, new_n24, new_n25, new_n26, new_n28,
    new_n29, new_n30, new_n31, new_n32, new_n33, new_n34, new_n35, new_n36,
    new_n37, new_n38, new_n39, new_n40, new_n41, new_n42, new_n43, new_n44,
    new_n45, new_n46, new_n47, new_n48, new_n49, new_n50, new_n51, new_n52,
    new_n53, new_n54, new_n55, new_n56, new_n57, new_n58, new_n59, new_n60,
    new_n61, new_n62, new_n63, new_n64, new_n65, new_n66, new_n67, new_n68,
    new_n69, new_n70, new_n71, new_n72, new_n74, new_n75, new_n76, new_n77,
    new_n78, new_n79, new_n80, new_n81, new_n82, new_n83, new_n84, new_n85,
    new_n86, new_n87, new_n88, new_n89, new_n90, new_n91, new_n92, new_n93,
    new_n94, new_n95, new_n96, new_n97, new_n98, new_n99, new_n100,
    new_n101, new_n102, new_n103, new_n104, new_n105, new_n106, new_n107,
    new_n108, new_n109, new_n110, new_n111, new_n112, new_n113, new_n114,
    new_n115, new_n116, new_n117, new_n118, new_n119, new_n120, new_n121,
    new_n122, new_n123, new_n124, new_n125, new_n126, new_n127, new_n128,
    new_n129, new_n130, new_n131, new_n132, new_n133, new_n134, new_n135,
    new_n137, new_n138, new_n139, new_n140, new_n141, new_n142, new_n143,
    new_n144, new_n145, new_n146;
  assign new_n13 = ~b & ~g;
  assign new_n14 = ~c & ~f;
  assign new_n15 = d & h;
  assign new_n16 = ~d & e;
  assign new_n17 = a & ~h;
  assign new_n18 = new_n16 & ~new_n17;
  assign new_n19 = ~new_n16 & new_n17;
  assign new_n20 = ~new_n15 & ~new_n18;
  assign new_n21 = ~new_n19 & new_n20;
  assign new_n22 = new_n14 & ~new_n21;
  assign new_n23 = ~new_n14 & new_n21;
  assign new_n24 = ~new_n22 & ~new_n23;
  assign new_n25 = new_n13 & new_n24;
  assign new_n26 = ~new_n13 & ~new_n24;
  assign F0 = new_n25 | new_n26;
  assign new_n28 = ~a & ~c;
  assign new_n29 = e & new_n28;
  assign new_n30 = a & c;
  assign new_n31 = ~b & ~f;
  assign new_n32 = ~new_n30 & new_n31;
  assign new_n33 = ~new_n29 & new_n32;
  assign new_n34 = ~g & ~h;
  assign new_n35 = g & h;
  assign new_n36 = ~new_n34 & ~new_n35;
  assign new_n37 = ~a & ~e;
  assign new_n38 = ~c & new_n37;
  assign new_n39 = ~new_n31 & ~new_n38;
  assign new_n40 = ~new_n33 & ~new_n36;
  assign new_n41 = ~new_n39 & new_n40;
  assign new_n42 = ~a & c;
  assign new_n43 = ~d & ~h;
  assign new_n44 = d & ~g;
  assign new_n45 = ~new_n43 & ~new_n44;
  assign new_n46 = new_n42 & ~new_n45;
  assign new_n47 = a & ~c;
  assign new_n48 = e & ~h;
  assign new_n49 = ~e & h;
  assign new_n50 = ~new_n48 & ~new_n49;
  assign new_n51 = d & ~new_n50;
  assign new_n52 = e & ~g;
  assign new_n53 = ~e & g;
  assign new_n54 = ~new_n52 & ~new_n53;
  assign new_n55 = ~d & ~new_n54;
  assign new_n56 = ~new_n51 & ~new_n55;
  assign new_n57 = new_n47 & ~new_n56;
  assign new_n58 = ~new_n46 & ~new_n57;
  assign new_n59 = ~new_n42 & ~new_n47;
  assign new_n60 = new_n31 & ~new_n59;
  assign new_n61 = new_n58 & new_n60;
  assign new_n62 = ~new_n31 & ~new_n58;
  assign new_n63 = ~d & ~new_n31;
  assign new_n64 = d & new_n31;
  assign new_n65 = ~new_n63 & ~new_n64;
  assign new_n66 = ~new_n30 & ~new_n38;
  assign new_n67 = ~new_n65 & new_n66;
  assign new_n68 = ~new_n29 & new_n65;
  assign new_n69 = new_n36 & ~new_n67;
  assign new_n70 = ~new_n68 & new_n69;
  assign new_n71 = ~new_n41 & ~new_n70;
  assign new_n72 = ~new_n61 & new_n71;
  assign F1 = new_n62 | ~new_n72;
  assign new_n74 = ~b & new_n42;
  assign new_n75 = ~d & ~e;
  assign new_n76 = ~new_n36 & new_n75;
  assign new_n77 = f & ~h;
  assign new_n78 = ~f & h;
  assign new_n79 = ~new_n77 & ~new_n78;
  assign new_n80 = d & new_n37;
  assign new_n81 = new_n79 & new_n80;
  assign new_n82 = ~new_n76 & ~new_n81;
  assign new_n83 = new_n74 & ~new_n82;
  assign new_n84 = b & new_n47;
  assign new_n85 = ~d & new_n84;
  assign new_n86 = ~b & d;
  assign new_n87 = e & new_n42;
  assign new_n88 = new_n86 & new_n87;
  assign new_n89 = ~new_n85 & ~new_n88;
  assign new_n90 = ~new_n79 & ~new_n89;
  assign new_n91 = new_n16 & new_n74;
  assign new_n92 = d & new_n84;
  assign new_n93 = ~new_n91 & ~new_n92;
  assign new_n94 = new_n36 & ~new_n93;
  assign new_n95 = ~d & ~f;
  assign new_n96 = ~new_n44 & ~new_n95;
  assign new_n97 = e & new_n96;
  assign new_n98 = ~e & ~new_n96;
  assign new_n99 = ~b & new_n47;
  assign new_n100 = ~new_n97 & new_n99;
  assign new_n101 = ~new_n98 & new_n100;
  assign new_n102 = new_n29 & new_n86;
  assign new_n103 = f & ~g;
  assign new_n104 = ~f & g;
  assign new_n105 = ~new_n103 & ~new_n104;
  assign new_n106 = b & new_n28;
  assign new_n107 = ~new_n15 & ~new_n43;
  assign new_n108 = new_n106 & ~new_n107;
  assign new_n109 = ~b & new_n30;
  assign new_n110 = ~new_n50 & new_n109;
  assign new_n111 = d & ~new_n110;
  assign new_n112 = new_n50 & new_n109;
  assign new_n113 = ~b & new_n38;
  assign new_n114 = b & new_n30;
  assign new_n115 = ~d & ~new_n114;
  assign new_n116 = ~new_n112 & new_n115;
  assign new_n117 = ~new_n113 & new_n116;
  assign new_n118 = ~new_n111 & ~new_n117;
  assign new_n119 = ~new_n102 & ~new_n105;
  assign new_n120 = ~new_n108 & new_n119;
  assign new_n121 = ~new_n118 & new_n120;
  assign new_n122 = ~h & new_n106;
  assign new_n123 = new_n105 & ~new_n110;
  assign new_n124 = ~new_n113 & ~new_n122;
  assign new_n125 = new_n123 & new_n124;
  assign new_n126 = ~new_n121 & ~new_n125;
  assign new_n127 = d & f;
  assign new_n128 = ~d & g;
  assign new_n129 = b & new_n42;
  assign new_n130 = ~new_n127 & ~new_n128;
  assign new_n131 = new_n129 & new_n130;
  assign new_n132 = ~new_n83 & ~new_n131;
  assign new_n133 = ~new_n90 & ~new_n94;
  assign new_n134 = ~new_n101 & new_n133;
  assign new_n135 = new_n132 & new_n134;
  assign F2 = new_n126 | ~new_n135;
  assign new_n137 = ~c & ~g;
  assign new_n138 = ~b & ~h;
  assign new_n139 = new_n95 & ~new_n138;
  assign new_n140 = ~new_n95 & new_n138;
  assign new_n141 = ~new_n139 & ~new_n140;
  assign new_n142 = new_n37 & ~new_n141;
  assign new_n143 = ~new_n37 & new_n141;
  assign new_n144 = ~new_n142 & ~new_n143;
  assign new_n145 = new_n137 & new_n144;
  assign new_n146 = ~new_n137 & ~new_n144;
  assign F3 = ~new_n145 & ~new_n146;
endmodule


