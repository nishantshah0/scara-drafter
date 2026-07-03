// SCARA Drafter — visual concept mockup (proportions real, details simplified)
$fn = 48;

PRINTED = "SteelBlue"; PRINTED2 = "LightSteelBlue"; MOTOR = [0.25,0.27,0.3];
BELT = "Firebrick"; STEEL = "Silver"; PAPER = "White"; INK = [0.1,0.1,0.12];

module rounded_bar(l, w, h) {
    hull() { cylinder(d=w, h=h); translate([l,0,0]) cylinder(d=w, h=h); }
}
module belt_band(l, d1, d2, z, h=5) {
    color(BELT) translate([0,0,z]) difference() {
        hull() { cylinder(d=d1, h=h); translate([l,0,0]) cylinder(d=d2, h=h); }
        translate([0,0,-1]) hull() { cylinder(d=d1-4, h=h+2); translate([l,0,0]) cylinder(d=d2-4, h=h+2); }
    }
}
module motor(s=42, hsh=12) {
    color(MOTOR) translate([-s/2,-s/2,0]) cube([s,s,40]);
    color(STEEL) translate([0,0,40]) cylinder(d=5, h=hsh+8);
    color(STEEL) translate([0,0,40+hsh]) cylinder(d=14, h=8);  // 20T pulley
}

// ---------------- table & paper -------------------------------------------
color([0.93,0.92,0.88]) translate([-140,-130,-4]) cube([500,290,4]);
color(PAPER) translate([130,-64,0]) cube([210,148,1]);
// a half-drawn CAD sketch on the paper (ink)
color(INK) translate([170,-25,1.01]) cube([120,1.2,0.4]);
color(INK) translate([170,25,1.01]) cube([70,1.2,0.4]);
color(INK) translate([170,-25,1.01]) cube([1.2,50,0.4]);
color(INK) translate([215,0,1.01]) difference(){cylinder(d=34,h=0.5);translate([0,0,-0.2])cylinder(d=31,h=1);}

// ---------------- base ------------------------------------------------------
color(PRINTED) hull() {
    translate([-95,-55,0]) cylinder(r=12, h=18);
    translate([ 25,-55,0]) cylinder(r=12, h=18);
    translate([-95, 55,0]) cylinder(r=12, h=18);
    translate([ 25, 55,0]) cylinder(r=12, h=18);
}
// electronics on the base tray
color([0.9,0.9,0.87]) translate([-92,-40,18]) cube([55,80,9]);          // breadboard
color([0.15,0.35,0.2]) translate([-84,-30,27]) cube([21,52,4]);         // Pico
color([0.5,0.1,0.12]) translate([-58,-28,27]) cube([15,20,4]);          // driver 1
color([0.5,0.1,0.12]) translate([-58,2,27]) cube([15,20,4]);            // driver 2
// shoulder motor (slotted mount region)
translate([-42,34,18]) motor();
// shoulder tower
color(PRINTED) cylinder(d=42, h=34);

// ---------------- shoulder joint + link 1 ----------------------------------
rotate([0,0,-14]) {
    // hub = printed 60T pulley
    color(PRINTED2) translate([0,0,34]) cylinder(d=58, h=10);
    color(PRINTED)  translate([0,0,44]) cylinder(d=48, h=12);
    color(STEEL)    translate([0,0,56]) cylinder(d=15, h=5);   // nyloc
    // link 1 body
    color(PRINTED) translate([0,0,44]) rounded_bar(130, 34, 12);
    // elbow motor riding link 1
    translate([78,0,56]) rotate([0,0,90]) motor(s=36, hsh=6);
    // elbow tower on link1 end
    color(PRINTED) translate([130,0,44]) cylinder(d=34, h=14);

    // ---------------- elbow joint + link 2 ---------------------------------
    translate([130,0,0]) rotate([0,0,52]) {
        color(PRINTED2) translate([0,0,24]) cylinder(d=48, h=9);   // 60T hub
        color(PRINTED)  translate([0,0,33]) cylinder(d=38, h=8);
        color(STEEL)    translate([0,0,41]) cylinder(d=13, h=4);
        color(PRINTED)  translate([0,0,24]) rounded_bar(130, 26, 9);
        // pen carriage
        color(PRINTED) translate([120,-11,10]) cube([26,22,30]);
        color([0.2,0.4,0.65]) translate([133,14,26]) cube([14,10,12]); // servo
        color(INK) translate([133,0,1]) cylinder(d=9, h=30);           // pen
        color(INK) translate([133,0,0.5]) cylinder(d1=2, d2=9, h=6);
    }
}
// shoulder belt (motor1 -> shoulder hub), drawn in base frame
translate([0,0,0]) {
    b1l = norm([-42-0, 34-0]);
    rotate([0,0,atan2(34,-42)]) belt_band(b1l, 58, 16, 36);
}
