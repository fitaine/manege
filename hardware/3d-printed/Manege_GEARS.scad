// Manège Turntable Gears
  // Optimized for 146.8mm lazy susan inner diameter
  // Date: 2026-01-02

  include <gears.scad>;

  // === CONFIGURATION ===
  module_size = 1.25;      // Module (tooth size)
  pinion_teeth = 22;       // Motor gear
  ring_teeth = 110;        // Lazy susan gear
  gear_width = 18;         // Can be 15-20mm
  pinion_bore = 5;         // Motor shaft diameter (adjust to your motor)
  rim_thickness = 3;       // Ring gear rim
  backlash = 0.2;          // Clearance between gears (mm)

  // === CALCULATED VALUES ===
  gear_ratio = ring_teeth / pinion_teeth;  // 5:1
  pinion_pitch_radius = (module_size * pinion_teeth) / 2;  // 13.75mm
  ring_pitch_radius = (module_size * ring_teeth) / 2;      // 68.75mm (internal)
  center_distance = ring_pitch_radius - pinion_pitch_radius - backlash;  // 54.8mm

  pinion_od = module_size * (pinion_teeth + 2);  // ~30mm
  ring_od = module_size * ring_teeth + (2 * rim_thickness);  // ~143.5mm

  echo("=== GEAR SPECIFICATIONS ===");
  echo(str("Gear Ratio: ", gear_ratio, ":1"));
  echo(str("Pinion OD: ", pinion_od, "mm"));
  echo(str("Ring OD: ", ring_od, "mm"));
  echo(str("Center Distance: ", center_distance, "mm"));
  echo(str("Steps per revolution (1/32 microstepping): ", 200 * 32 * gear_ratio));

  // === RING GEAR (Lazy Susan - Centered) ===
  herringbone_ring_gear(
      modul=module_size,
      tooth_number=ring_teeth,
      width=gear_width,
      rim_width=rim_thickness,
      pressure_angle=20,
      helix_angle=30
  );

  // === PINION GEAR (Motor - Left Side, INSIDE ring) ===
  translate([-center_distance, 0, 0])
  herringbone_gear(
      modul=module_size,
      tooth_number=pinion_teeth,
      width=gear_width,
      bore=pinion_bore,
      pressure_angle=20,
      helix_angle=30,
      optimized=true
  );
