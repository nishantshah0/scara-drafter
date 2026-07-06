// ===== SCARA Drafter — real printable parts, v1 ============================
// Render one part:   openscad -D 'PART="hub"' -o hub.stl scara-parts.scad
// Parts: "base" "arm1" "arm2" "hub" (print 2) "carriage" "spacers" "assembly"
//
// D9 NOTE: CD (motor<->joint center distance) is computed for a 2GT-200
// closed belt + 20T/60T. VERIFY against the real belts, adjust, re-render.
// Tolerances (+0.2/+0.3) are first guesses — the bearing coupon refines them.

PART = "assembly";
$fn = 96;

// ---- key parameters --------------------------------------------------------
LINK       = 130;     // joint-to-joint arm length
CD         = 58.6;    // belt center distance (2GT-200, 20T:60T) — MEASURE (D9)
ARM_T      = 12;      // arm bar thickness
ARM_W      = 34;      // arm bar width
T60_N      = 60;      // printed pulley teeth
HUB_BOSS_H = 12;      // arm-mounting boss height
PUL_H      = 8;       // belt section height
BRG_OD     = 22.3;    // 608 pocket (coupon-tune)
BRG_H      = 7.2;
AXLE_D     = 8.8;     // M8 clearance
HEXAF     = 13.4;     // M8 bolt-head / nut hex across-flats + tol
M3         = 3.4;
BC         = 29;      // bolt circle for arm<->hub (4x M3)
TOWER_H    = 52;      // shoulder tower height (sets belt plane)
NEMA       = 42.3;    // NEMA17 body + tol
NEMA_HOLES = 31;      // NEMA17 mounting square
NEMA_BOSS  = 22.6;    // NEMA17 pilot boss clearance
PEN_D      = 11.0;    // MUJI gel knock-type 0.5 — MEASURE the barrel at its
                      // widest gripped point and set this to measured + 0.4.
                      // The flex slit takes up the slack; clip rides in the slit.

// GT2 60T geometry
function pitch_d(n) = 2*n/PI;
T60_OD = pitch_d(T60_N) - 0.5;             // ~37.7

module m3_ring() { for (a=[45:90:360]) rotate([0,0,a]) translate([BC/2,0,-1]) cylinder(d=M3, h=99); }

// ---- GT2 pulley section ----------------------------------------------------
module gt2_60(h) {
    difference() {
        union() {
            translate([0,0,1.2]) cylinder(d=T60_OD, h=h-2.4);
            cylinder(d=T60_OD+3.6, h=1.2);                       // bottom flange (on the bed)
            // top flange with 45-degree cone underneath: self-supporting,
            // no ring overhang (print-failure lesson, debugging log 2026-07-03)
            translate([0,0,h-3.0]) cylinder(d1=T60_OD, d2=T60_OD+3.6, h=1.8);
            translate([0,0,h-1.2]) cylinder(d=T60_OD+3.6, h=1.2);
        }
        for (i=[0:T60_N-1]) rotate([0,0,i*360/T60_N])
            translate([T60_OD/2+0.25, 0, 1.0])
                cylinder(d=1.7, h=h-2.0);                        // tooth grooves
    }
}

// ---- HUB (print 2 — shoulder boss-up, elbow: same part flipped) ------------
module hub() {
    difference() {
        union() {
            gt2_60(PUL_H);
            translate([0,0,PUL_H]) cylinder(d=36, h=HUB_BOSS_H); // arm boss
        }
        translate([0,0,-1]) cylinder(d=BRG_OD, h=BRG_H+1);       // brg pocket ↓
        // FULL 45° cone above the pocket — zero flat, zero bridging. The
        // bearing gets its flat seat from a drop-in printed washer instead
        // (in spacers.stl). Second iteration of the ring-bridge lesson.
        translate([0,0,BRG_H-0.01]) cylinder(d1=BRG_OD, d2=AXLE_D+6, h=(BRG_OD-(AXLE_D+6))/2);
        translate([0,0,PUL_H+HUB_BOSS_H-BRG_H]) cylinder(d=BRG_OD, h=BRG_H+1);
        cylinder(d=AXLE_D+6, h=99, center=true);                 // inner clear
        m3_ring();                                               // arm bolts
        for (a=[45:90:360]) rotate([0,0,a]) translate([BC/2,0,PUL_H+1.5])
            cylinder(d=6.6, h=3, $fn=6);                         // M3 nut pockets
    }
}

// ---- ARM (shared shape) -----------------------------------------------------
module arm_blank(len, hub_end_d) {
    hull() {
        cylinder(d=hub_end_d, h=ARM_T);
        translate([len,0,0]) cylinder(d=ARM_W, h=ARM_T);
    }
}

// ARM 1: bolts to shoulder hub; carries elbow axle + motor 2 (shaft-down)
module arm1() {
    difference() {
        union() {
            arm_blank(LINK, 42);
            translate([LINK,0,0]) cylinder(d=42, h=ARM_T);
            // rib
            translate([20,-4,ARM_T]) cube([LINK-40,8,6]);
        }
        translate([0,0,-1]) cylinder(d=17, h=99);                // spacer/nyloc access
        m3_ring();                                               // to shoulder hub
        // elbow axle: hex head pocket on TOP, shaft hangs down
        translate([LINK,0,0]) {
            cylinder(d=AXLE_D, h=99, center=true);
            translate([0,0,ARM_T-5.8]) cylinder(d=HEXAF/cos(30), h=6, $fn=6);
        }
        // motor 2: face bolts to arm underside, shaft down through arm
        translate([LINK-CD,0,0]) {
            cylinder(d=NEMA_BOSS, h=99, center=true);
            for (x=[-1,1], y=[-1,1]) translate([x*NEMA_HOLES/2, y*NEMA_HOLES/2, -1])
                hull() { cylinder(d=M3, h=99); translate([4,0,0]) cylinder(d=M3, h=99); } // tension slots
        }
    }
}

// ARM 2: bolts under elbow hub; carries the pen carriage
module arm2() {
    difference() {
        arm_blank(LINK, 42);
        translate([0,0,-1]) cylinder(d=17, h=99);
        m3_ring();
        for (y=[-8,8]) translate([LINK,y,-1]) cylinder(d=M3, h=99); // carriage bolts
    }
}

// ---- BASE -------------------------------------------------------------------
module base() {
    difference() {
        union() {
            hull() for (x=[-80,55], y=[-55,55])                  // deck
                translate([x,y,0]) cylinder(r=14, h=10);
            cylinder(d1=56, d2=44, h=TOWER_H);                   // shoulder tower
            // motor platform: shelf at z=TOWER_H-6, motor hangs beneath, shaft up
            translate([-CD,0,0]) {
                for (y=[-28,22]) translate([-27,y,0]) cube([54,6,TOWER_H]);  // 44mm gap: NEMA fits
                translate([-30,-30,TOWER_H-6]) cube([60,60,6]);
            }
        }
        translate([-CD,0,0]) translate([-22,-22,-1]) cube([44,44,13]);  // deck cutout: motor body passes through
        // shoulder axle: hex pocket at tower TOP (bolt head recessed, shank up
        // through the hub stack — an M8x50 reaches; bottom-pocketed it would
        // need M8x90. Caught in final hand-audit 2026-07-05.)
        cylinder(d=AXLE_D, h=99, center=true);
        translate([0,0,TOWER_H-6]) cylinder(d=HEXAF/cos(30), h=7, $fn=6);
        translate([-CD,0,0]) {
            translate([0,0,TOWER_H-8]) cylinder(d=NEMA_BOSS+4, h=10);   // shaft/boss hole
            for (x=[-1,1], y=[-1,1]) translate([x*NEMA_HOLES/2+ -2, y*NEMA_HOLES/2, TOWER_H-8])
                hull() { cylinder(d=M3, h=10); translate([4,0,0]) cylinder(d=M3, h=10); }
        }
        // electronics tray zip slots
        for (x=[-70,-30], y=[-48,44]) translate([x,y,-1]) cube([5,4,12]);
    }
}

// ---- PEN CARRIAGE -----------------------------------------------------------
module carriage() {
    difference() {
        union() {
            cube([26,34,ARM_T]);                                 // mount foot
            translate([0,4,0]) cube([26,26,40]);                 // pen block
        }
        for (y=[9,25]) translate([13,y,-1]) cylinder(d=M3, h=99); // to arm2
        translate([13,17,-1]) cylinder(d=PEN_D+0.4, h=99);       // pen bore (see PEN_D)
        translate([13-2.5,17,-1]) cube([5,20,99]);               // flex-grip slit (also clears the clip)
        translate([-1,12,20]) cube([28,3.2,14]);                 // zip slots: servo
        translate([-1,24,20]) cube([28,3.2,14]);
    }
}

// ---- SPACERS ----------------------------------------------------------------
module spacers() {
    // print ONE SET PER JOINT (2 sets total)
    difference() { cylinder(d=14, h=5);   cylinder(d=8.7, h=99, center=true); }  // top spacer (above top bearing race)
    translate([25,0,0])
    difference() { cylinder(d=14, h=5);   cylinder(d=8.7, h=99, center=true); }  // bottom spacer (tower/arm1 to lower race — keeps hub off the tower)
    translate([50,0,0])
    difference() { cylinder(d=12, h=6.0); cylinder(d=8.7, h=99, center=true); }  // inner tube (between the two bearing inner races)
    translate([75,0,0])
    difference() { cylinder(d=22.0, h=1.2); cylinder(d=15, h=99, center=true); } // seat washer: drops into the lower pocket, gives the bearing a flat face against the cone
}

// ---- render selector --------------------------------------------------------
if (PART=="hub") hub();
if (PART=="arm1") arm1();
if (PART=="arm2") arm2();
if (PART=="base") base();
if (PART=="carriage") carriage();
if (PART=="spacers") spacers();
// bought-component mockups (assembly view only)
module nema17_body() { color([0.22,0.24,0.28]) translate([-21,-21,0]) cube([42,42,42]); }
module pulley20(z) { color("Silver") translate([0,0,z]) cylinder(d=14, h=8); }
module belt(cd, z) { color("Firebrick") translate([0,0,z]) difference() {
    hull() { cylinder(d=T60_OD+2, h=5); translate([cd,0,0]) cylinder(d=15, h=5); }
    translate([0,0,-1]) hull() { cylinder(d=T60_OD-2, h=7); translate([cd,0,0]) cylinder(d=11, h=7); } } }

// Joint angles (degrees) for the assembly view. Plain overridable variables
// (NOT $t) so each animation frame can be rendered as its own process with
// -D "J1=..." -D "J2=..." -- OpenSCAD 2021.01's --animate loop hits a
// Windows GL context bug across many frames in one process, and $t itself
// isn't reliably overridable via -D. Default pose = the tightest verified
// clearance case (pen at the paper's near edge; arm2 folded closest to the
// tower; numerically confirmed clear by 12mm, see clearance_check.py).
J1 = -78;
J2 = 156;

if (PART=="assembly") {
    color("SteelBlue") base();
    // motor 1: hangs under the base platform, shaft up through the shelf
    translate([-CD,0,TOWER_H-6-42]) nema17_body();
    translate([-CD,0,0]) { color("Silver") cylinder(d=5, h=TOWER_H+16); pulley20(TOWER_H+0.5); }
    rotate([0,0,180]) belt(CD, TOWER_H+1.5);   // shoulder belt: hub -> motor1 at -CD
    translate([0,0,TOWER_H]) rotate([0,0,J1]) {
        color("LightSteelBlue") hub();
        color("Silver") translate([0,0,PUL_H+HUB_BOSS_H+2]) cylinder(d=15,h=4,$fn=6);  // nyloc
        color("SteelBlue") translate([0,0,PUL_H+HUB_BOSS_H]) arm1();
        // motor 2: body above arm1, face down, shaft down through the arm
        translate([LINK-CD,0,PUL_H+HUB_BOSS_H+ARM_T]) nema17_body();
        translate([LINK-CD,0,PUL_H+HUB_BOSS_H-14]) { color("Silver") cylinder(d=5,h=26); pulley20(2); }
        translate([LINK,0,PUL_H+HUB_BOSS_H]) rotate([0,0,J2]) {
            rotate([0,0,180-J2]) translate([0,0,-9]) belt(CD, 0);  // elbow belt toward motor2
            color("LightSteelBlue") translate([0,0,-PUL_H-HUB_BOSS_H]) rotate([180,0,0]) hub();
            color("SteelBlue") translate([0,0,-PUL_H-HUB_BOSS_H-ARM_T-0.5]) arm2();
            translate([LINK,0,-PUL_H-HUB_BOSS_H-ARM_T-0.5]) {
                color("SlateGray") translate([-13,-17,0]) carriage();
                color([0.2,0.4,0.65]) translate([-6,12,22]) cube([12,23,12]);      // MG90S
                color([0.1,0.1,0.12]) translate([0,0,-28]) cylinder(d=10, h=52);   // MUJI pen
            }
        }
    }
    // paper + electronics beside the base (desk layout)
    color("White") translate([60,-74,-8]) cube([210,148,1]);
    color([0.9,0.9,0.87]) translate([-150,-40,-8]) cube([55,82,9]);   // breadboard
    color([0.15,0.35,0.2]) translate([-144,-30,1]) cube([21,52,4]);   // Pico
    color([0.5,0.1,0.12]) translate([-118,-24,1]) cube([13,18,4]);    // TMC2209 x2
    color([0.5,0.1,0.12]) translate([-118,4,1]) cube([13,18,4]);
    color([0.93,0.92,0.88]) translate([-150,-140,-8]) cube([460,300,0.5]); // desk
}
