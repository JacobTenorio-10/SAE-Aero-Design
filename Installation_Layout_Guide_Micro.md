# Installation Layout — SAE Aero 2026 Micro (Systems, Layer L4)

<details>
<summary><b>Body-free installation part · derives from the <code>SKELETON</code> via Insert Part</b></summary>

### Body-free installation part · derives from the `SKELETON` via Insert Part

> **What this is.** The **`INSTALLATION`** layer (L4) — the component space-claims and mechanism kinematics pulled out of the published skeleton because each is consumed by only *one* downstream part (the two-consumer test): servos, the payload drop-door, landing-gear wheels/steering, and the fill / belly / linkage clearance studies.
>
> **How it attaches.** `INSTALLATION_LAYOUT.SLDPRT` is a **body-free part** that **Insert ▸ Part**-derives `SKELETON` one-way (§9 of the skeleton guide), inheriting its datum frame, planes, axes, and OML surfaces. Everything below builds on those **inherited** references — every `§`-reference and datum name (`AX_MainSpar_3D`, `SURF_Wing_OML`, `AX_Hinge_Ail`, `AX_GearAxle`, `AX_Tail_Steer`, the `PLN_Fuse_*` stations, the Ground Line) points to a feature **published by the skeleton** and pulled in here. Real component parts (the actual servos, battery, container, wheels) then **mate to these space-claim envelopes** in the top assembly; they are never modelled in the skeleton.
>
> **Globals.** This part shares the one `skeleton_equations_micro.txt` — the globals live in the skeleton and arrive with the derived insert, so the component globals (`servo_*`, `hatch_open_deg`, `horn_R`, `link_L`, `wheel_*`, `w_wheel`, `tail_steer_rake`, `wheel_tail_dia`, `plumb_drop`, `belly_margin`, `x_steer_servo`, `bat_*`, `motor_*`) resolve automatically. Nothing here adds a solid body; mass stays **0.00 g**.
>
> **Numbering.** The subsection numbers (`§7.x`, `§13.x`) inside each part below are **retained verbatim from the source skeleton guide** so cross-references stay valid; the `## I-N` chapter numbers are this guide's own.

---

> **Battery space-claims.** These are pure envelopes with no separate build here: the propulsion and avionics batteries are the `bat_*` / `avi_bat_*` envelopes seated against the firewall datum. The **payload container is not modeled anywhere** — neither the skeleton nor this file publishes bay bounds or interface planes; the water is carried as mass at `x_bay` for CG bookkeeping only. Drop a **For construction** rectangle per envelope if you want the visual claim.

---

</details>

<details>
<summary><b>I-1. Servo packaging &amp; skin-breach audit  <i>(from skeleton §7.7.3)</i></b></summary>

## I-1. Servo packaging & skin-breach audit  *(from skeleton §7.7.3)*

<details>
<summary><b>7.7.3 — Phase 3: Servo packaging &amp; skin-breach audit</b></summary>

Map each servo as a body-free **keep-out box** ahead of its hinge, then confirm it nests inside the OML skin.

<details>
<summary><b>Step 1 — locate the servo station</b></summary>

The aileron servo seats mid-aileron; its spanwise centre is `= "y_servo_ail"` — one global, per the one-variable rule. Build a local section plane there: **Insert ▸ Reference Geometry ▸ Plane**, First Reference = `AX_MainSpar_3D` → **Normal to Curve**, Second Reference = a point on the spar at that spanwise expression; green-check and rename `PLN_Servo_Ail`. *(Or skip the plane and sketch the plan footprint straight on `LAY_Wing_Plan`.)*

<details>
<summary><b>Step 2 — the plan footprint (<code>LAY_Servo_Bay_Ail</code>), driven by the servo globals</b></summary>

1. Click `PLN_Servo_Ail` ▸ **Sketch**; press **`Ctrl + 8`**. Select **Corner Rectangle**; box-select its four lines and tick **For construction**.
2. Dimension the chordwise edge (along $Z$) → `= "servo_L"` and the spanwise edge (along $X$) → `= "servo_W"`.
3. **Seat it against the hinge.** Make the box's **aft edge Coincident** to the aileron hinge chordline (§7.7.2 Step 1) so the output arm reaches the hinge; the body then extends `servo_L` **forward ($+Z$)**. Dimension its spanwise centre to the centerline → `= "y_servo_ail"`. Exit; **F2** → `LAY_Servo_Bay_Ail`; file in `2_LAYOUT_SKETCHES`.

<details>
<summary><b>Step 3 — the section footprint (thickness / height)</b></summary>

On `PLN_Servo_Ail`, open a second sketch and draw a **For construction** rectangle `= "servo_L"` (chordwise, $Z$) $\times$ `= "servo_H"` (vertical, $Y$), straddling the local chord line. Together the plan box (L $\times$ W) and the section box (L $\times$ H) bound the full 3-D servo keep-out.

<details>
<summary><b>Step 4 — the skin-breach audit against <code>SURF_Wing_OML</code></b></summary>

(needs the §8.4 surface).
1. On `PLN_Servo_Ail`, run **Tools ▸ Sketch Tools ▸ Intersection Curve**, click `SURF_Wing_OML`, green-check — SolidWorks traces the true local airfoil section (upper + lower skin contour) at the servo station.
2. Overlay your `= "servo_H"` $\times$ `= "servo_L"` section box on that contour. **Confirm the box sits entirely inside the upper and lower skin lines** — no edge crosses the OML.
3. *Low-aspect-ratio warning.* A Micro wing is big-chord but often **thin**; out at the aileron the taper has thinned the section, so a tall `servo_H` can punch through the skin. If the box breaches: pick a lower-profile servo (drop `servo_H`), move the bay **inboard** (raise the spanwise expression toward `y_ail_in`, where the chord — and thickness — is greater), or recess the servo behind a faired blister on the derived skin part (never on the skeleton OML). See §14 item 25.
> **Body-free.** Every rectangle here is **For construction** — no extrude, no boss. Re-run **Tools ▸ Evaluate ▸ Mass Properties**: mass stays **0.00 g** (§13.8).

---

</details>

</details>

</details>

</details>

</details>

</details>

<details>
<summary><b>I-2. Payload drop-door kinematics  <i>(from skeleton §7.8.1)</i></b></summary>

## I-2. Payload drop-door kinematics  *(from skeleton §7.8.1)*

<details>
<summary><b>7.8.1 — Phase 1: Payload hatch &amp; drop-door kinematics (<code>LAY_Side_Profile</code>)</b></summary>

Sketch the door's swing as a construction overlay on the side profile so the fully-open envelope can be audited against the gear and ground.
1. Expand `2_LAYOUT_SKETCHES`, right-click `LAY_Side_Profile` ▸ **Edit Sketch**; press **`Ctrl + 8`** (Normal To). Orientation on the Right Plane: $+Z$ forward, $+Y$ up, the belly is below the waterline ($-Y$). *(Prefer a clean tree? Open a dedicated **Right-Plane** sketch named `LAY_Hatch_Kinematics` instead and **Convert Entities** the bottom keel into it — the steps below are identical.)*
2. **Hinge pivot.** Select the **Point** tool and drop a point on the **bottom cabin keel** (`BF → BR`, §4). Hold **`Ctrl`**, select the point and the keel line, add **Coincident**; then **Smart Dimension** its $Z$ to the Origin → `= "x_fuse_bay_fwd"` (the forward cabin sub-station, 50.00 mm **+Z**). This is the drop-door hinge. Note the **door length** still has no global — see step 3.
3. **Closed-door line.** Select the **Line** tool, tick **For construction**. Draw from the pivot **aft ($-Z$)** along the keel; **Collinear** to the keel; **Smart Dimension** its length to the door length you want as a plain millimetre value (no global drives it — see the flag at the end of §I-2). Its aft end is the free / latch edge.
4. **Open-door line.** From the *same* pivot, draw a second **For construction** line of the **same** length as the closed-door line (add an **Equal** relation between the two so they track together), swung down and open. **Smart Dimension** the angle between the closed and open lines → `= "hatch_open_deg"`.
5. **Swept arc (clearance envelope).** Select **Centerpoint Arc**: click the **pivot** as centre, then the **closed** free-edge and the **open** free-edge as the two ends (radius auto-locks to the door-line length). Tick **For construction**. This arc is the door's swept keep-out zone.
6. **Servo horn + actuation link.** Drop a construction **Point** for the servo output shaft inside the bay. Draw a **For construction Circle** on it, **Smart Dimension** radius → `= "horn_R"` (the horn sweep). Draw a **For construction Line** from a point on the horn circle to a point on the door → **Smart Dimension** its length `= "link_L"` (the push-link). Together they represent the mechanism that drives `hatch_open_deg`.
7. **Gear / ground clearance relation.** Make `AX_GearAxle` visible (it reads as a point in this side view). Drop a construction point on the **open-door free edge**, then **Smart Dimension** from it to `AX_GearAxle` (a *driven / reference* dimension) — confirm a **positive** margin. The fully-open door must not foul the axle or the Ground Line (§6.7). If the margin collapses to zero, shorten the door line or reduce `hatch_open_deg`.
   > **Construction only.** The arc, both door lines, the horn circle, and the link are all **For construction**, so they carry no mass and never enter the §8.5 fuselage loft — this is a kinematic overlay, not skin.
8. **Promote the pivot (`5_POINTS`).** **Insert ▸ Reference Geometry ▸ Point**, click the hinge-pivot vertex, green-check, **F2** → `PT_Hatch_Pivot`; drag it into the existing **`5_POINTS`** folder (§7.1).
9. Confirm every new entity is **solid black** (Fully Defined), then **Exit** the sketch.

---

</details>

</details>

<details>
<summary><b>I-3. Landing-gear installation — taildragger, wheels &amp; steering  <i>(from skeleton §7.9)</i></b></summary>

## I-3. Landing-gear installation — taildragger, wheels & steering  *(from skeleton §7.9)*

<details>
<summary><b>7.9 — Kinematic Landing Gear, Taildragger Architecture, and Steering Alignment</b></summary>

This section configures a **conventional (taildragger)** gear as body-free construction geometry: two forward main wheels *ahead of the CG* plus a small steerable tailwheel at the aft, every wheel tied to the one master **Ground Line** (§6.7). Same $+Z$ forward / $+Y$ up / $+X$ port frame, symmetric about the Right Plane, zero solid bodies. Build order: mains + deflection arc → tailwheel + steering axis → three-point stance → downstream struts / formers. Budget ~30 minutes.

> **Config note.** A taildragger swaps the tricycle **nose** wheel (`x_aux`, `wheel_aux`) for an aft **tail** wheel — ignore or remove the nose-wheel globals for a conventional build. The mains ride the existing gear set: `track` = 260, `wheel_main` = 60, `w_wheel` = 25, `gear_h` = `wheel_main`/2, `x_main` = 40, `prop_clear`, `h_thrust` = 160, plus the `AX_GearAxle` datum and the master Ground Line (§6.7). The **tailwheel / steering block** is in `skeleton_equations_micro.txt`, mirrored into Appendix A of `Aircraft_Skeleton_Parameters_Micro.md`:
>
> | Global | Starter value | Meaning |
> |---|---|---|
> | `"tail_steer_rake"` | `12` | tailwheel steering-kingpin rake from vertical [deg] |
> | `"wheel_tail_dia"` | `30` | tailwheel diameter [mm] |
>
> Both MMGS; store the rake in **degrees** and convert with `* pi/180` only inside a trig expression (§14 item 5).

<details>
<summary><b>7.9.1 — Phase 1: Main gear positioning &amp; impact deflection (<code>LAY_Side_Profile</code> / <code>LAY_Front_View</code>)</b></summary>


* **Taildragger longitudinal alignment (mains forward of the CG).**
  1. Expand `2_LAYOUT_SKETCHES`, right-click `LAY_Side_Profile` ▸ **Edit Sketch**; **`Ctrl + 8`**. Right Plane: $+Z$ forward, $+Y$ up.
  2. Select the **Point** tool; drop a construction point for the main-gear axle. **Smart Dimension** its $Z$ from the Origin → `= "x_main"` (40 mm aft of LE).
  3. **Confirm it leads the CG.** *Forward ($+Z$)* means a **smaller aft-distance**: `x_main` = 40 mm-aft sits forward of the 0.28-MAC target CG (`PT_CG_target` ≈ 69 mm-aft), so the mains lead the CG by ~29 mm — the forward offset that keeps the aircraft from nosing over under braking. If your axle lands at or behind `PT_CG_target`, **reduce `x_main`** (move the mains forward) until there is a positive forward margin.
     > **Ground-loop caution.** Too *little* forward offset invites nose-over; too *much* raises ground-loop yaw sensitivity. Keep the mains a modest, deliberate distance ahead of the CG — not on top of it (§14 item 31).
* **Strut deflection travel arc.**
  4. Drop a construction point at the **strut attachment frame vertex** (where the gear leg meets the lower fuselage). This is the arc centre.
  5. Select **Centerpoint Arc**: click the strut-attachment vertex as centre, then the **static axle point** (Phase 1 step 2) as the start. Tick **For construction**. Sweep a short arc **upward** (toward the fuselage) to a second **deflected axle point** — the axle's path as the strut compresses on a hard landing.
  6. At the deflected axle point, trace the tire contour (a **For construction** circle `= "wheel_main"` diameter). **Confirm the fully-compressed tire never crosses the lower fuselage keel / `SURF_Fuse_OML`.** If it breaches: stiffen the strut (less travel), lengthen the leg, or drop the attachment vertex (§13.7.6 / §14).
* **Front-view lateral track alignment ($+X$ port).**
  7. Right-click `LAY_Front_View` ▸ **Edit Sketch**; **`Ctrl + 8`**. Front Plane: span $\times$ height, $+X$ port.
  8. Draw a short horizontal **axle reference line**; **Smart Dimension** its height above the master **Ground Line** → `= "gear_h"` (= `wheel_main`/2, so the tire bottom sits flush on the ground — §6.7).
  9. Lock the wheel-center point horizontally to the fuselage centerline ($X = 0$) → `= "track_half"` on the $+X$ (port) side; the §6-style mirror gives starboard.
  10. Trace the edge-on tire as a **Center Rectangle**, **For construction**: `= "wheel_main"` **vertical** $\times$ `= "w_wheel"` **horizontal**, centred on the axle point.
  11. **Promote** the wheel center: **Insert ▸ Reference Geometry ▸ Point** → `PT_Main_Axle` in `5_POINTS`; the lateral axle line is what `AX_GearAxle` (§7.2) rides.

</details>

<details>
<summary><b>7.9.2 — Phase 2: Aft tailwheel &amp; steering pivot architecture (<code>AX_Tail_Steer</code>)</b></summary>

* **Steering-axis rake angle.**
  1. Re-open `LAY_Side_Profile` (**Edit Sketch**, **`Ctrl + 8`**) and pan to the **far aft ($-Z$)**, near the tail-termination plane (`x_fuse_tail` = 177.80 mm-aft, pod exit).
  2. Draw a **For construction** line for the steering **kingpin**, running roughly top-to-bottom. Draw a second short **vertical Z-datum** construction line beside it.
  3. **Smart Dimension** the angle between the kingpin and the vertical datum → `= "tail_steer_rake"` — the kingpin leans so the contact point trails the pivot, which is what makes the tailwheel self-center and steer.
* **Promote to an axis feature.**
  4. **Insert ▸ Reference Geometry ▸ Axis**, pick **One Line/Edge/Axis**, click the kingpin construction line, green-check, **F2** → `AX_Tail_Steer`; drag it into the **`4_AXES`** folder (§7.2).
* **Tailwheel profile.**
  5. Drop a **Point** at the **base of the kingpin line** — the tailwheel axle. Draw a **circle** (a normal, non-construction sketch circle) centred on it and **Smart Dimension** its diameter → `= "wheel_tail_dia"` to depict the physical steering-wheel envelope.
     > **Still body-free.** A non-construction *sketch* circle is a profile, not a solid — leave it un-extruded and Mass Properties stays **0.00 g** (§13.8). It only reads as "solid" on screen to distinguish the physical wheel from the construction kinematics around it.
  6. **Promote** the axle vertex: **Insert ▸ Reference Geometry ▸ Point** → `PT_Tail_Axle` in `5_POINTS`.

</details>

<details>
<summary><b>7.9.3 — Phase 3: Three-point stance &amp; Ground Line integration</b></summary>

1. **Multi-wheel ground alignment.** Both the forward main tires (Phase 1) and the aft tailwheel (Phase 2) reference the single master **Ground Line** (§6.7) — in `LAY_Front_View` for the mains and `LAY_Side_Profile` for the fore-aft stance.
2. **Static stance rake audit.** Add a **Tangent** relation between the **bottom perimeter of the tailwheel circle** and the **Ground Line**; confirm the forward main-tire rectangles stay **flush** (bottom edge on the Ground Line). With the tall mains forward and the small tailwheel aft, the airframe now rests nose-high.
3. **Decoupled protection — let the axles float on tire radius, never pin them to the waterline.** Each axle must sit its **own tire radius** above the Ground Line: the mains at `= "gear_h"` (already `gear_h`), the tailwheel at `= "gear_h_tail"`. Pin the **ground contact** (the tangent / flush relation), and let each axle *ride up and down* with its radius equation. Then swapping to a taller tire lifts that axle while the Ground Line — and the whole stance datum — stays put.
   > **Why this matters.** This dual contact automatically sets the static three-point stance angle relative to the waterline ($Y = 0$). If instead you hard-pin both axles directly to the waterline, the model over-defines the instant a tire diameter changes and the stance angle freezes or errors (§14 item 29). The waterline is the *airframe* datum; the Ground Line is the *stance* datum — keep them linked only through the tire-radius equations.

</details>

<details>
<summary><b>7.9.4 — Phase 4: Downstream component derivation (struts &amp; former bulkheads)</b></summary>

Structural leads consume the gear datums via **Insert Part** (derived), never in-context (§9.1).
* **Main gear strut (`Main_Gear_Strut.SLDPRT`).**
  1. **File ▸ New ▸ Part**; **Save As** to `Z:\SAE_Micro_2026\02_Parts\Main_Gear_Strut.SLDPRT`.
  2. **Insert ▸ Part…**, select `AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`, **Open**. Under **Transfer** check **Axes** (`AX_GearAxle`) and **Planes**; leave **"Locate part with Move/Copy Feature" UNCHECKED** so it derives at the coincident origin (§9.1).
  3. Model the carbon-fiber or aluminum spring gear off the `AX_GearAxle` datum and the strut-attachment vertex — the leg sweeps from the fuselage frame down to the axle, and re-solves whenever `track`, `wheel_main`, or `gear_h` changes.
* **Firewall / mount former reinforcement.**
  4. In the fuselage-former part, **Insert ▸ Part…** the skeleton with **Axes** (`AX_Tail_Steer`) and **Reference Points** (`PT_Tail_Axle`) and **Surface bodies** (`SURF_Fuse_OML`) checked.
  5. On the former plane, run **Tools ▸ Sketch Tools ▸ Intersection Curve** against `SURF_Fuse_OML` to capture the true curved shell section (§8.7 Workflow 1), then design the plywood reinforcement former *inside* that curve. Locate the tailwheel bracket on `AX_Tail_Steer` / `PT_Tail_Axle` so the steering kingpin passes cleanly through the reinforced former.
  > **Why derive.** Struts and formers read `AX_GearAxle` / `AX_Tail_Steer` / `SURF_Fuse_OML` one-way from the skeleton (§9.5 golden rule). Flex `x_main`, `track`, `tail_steer_rake`, or `wheel_tail_dia` in the master and every derived leg, bracket, and former re-solves together.

---

</details>

</details>

</details>

<details>
<summary><b>I-4 – I-6. Systems clearance &amp; linkage studies  <i>(from skeleton §7.13 – §7.15)</i></b></summary>

## I-4 – I-6. Systems clearance & linkage studies  *(from skeleton §7.13 – §7.15)*

<details>
<summary><b>7.13 — Top Fill-Hole Access Clearance Vector (<code>AX_Fill_Path</code>)</b></summary>

This establishes a single vertical reference axis rising from the cabin crown face, up through the upper hull, reserving an unobstructed line for the top fill / liquid-deploy port so no downstream deck, wing-seat tie, or former can grow across it. Body-free construction geometry — it adds no mass. Budget ~8 minutes.

1. **Open the side profile.** Edit `LAY_Side_Profile` on the Right Plane ($X = 0$) — the sketch that carries the cabin keels and the `x_fuse_*` station columns (§4.4).
2. **Drop the fill centerline.** Sketch ▸ **Line** — draw one segment from the **top edge** of the bay rectangle straight up.
   * Make the lower endpoint **Coincident** to the bay-rectangle top edge.
   * Select the segment and add a **Vertical** relation so it rises pure $+Y$.
3. **Fix the chordwise station.** Smart-Dimension the segment's $Z$ from the Origin to `= "x_bay"`, co-locating the fill line with the water-mass centroid station — the top fill hole sits directly over wherever the container is installed, so no separate offset global is needed.
4. **Overshoot the crown.** Extend the upper endpoint past the top keel: Smart-Dimension its $Y$ to `= "h_fill_top"` — the crown sits at `= "h_fuse_top"`, so a **15 mm** overshoot clears the hull skin and any crown former. (Alternatively add a **Pierce** to the crown profile curve, *then* add the overshoot dimension above it — never Pierce alone, or the axis stops flush at a re-lofted crown; see §14 item 32.)
5. **Set construction, promote to an axis.** Select the segment ▸ **For construction**. Exit the sketch. Insert ▸ Reference Geometry ▸ **Axis** ▸ pick the construction segment ▸ rename `AX_Fill_Path` and file it in `4_AXES`.

The reserved clear span is fully global-driven — it runs from the bay-rectangle top edge up to the crown at `= "h_fuse_top"` — so it re-sizes automatically with any cabin-height change and never needs a hand-edit.

> **Verification & Success state:** `AX_Fill_Path` is vertical (parallel to $+Y$), lies on the Right Plane at the `x_bay` station, with its lower end **Coincident** to the cabin crown line and its upper end **above** `= "h_fuse_top"`. The sketch is fully defined (black). **Tools ▸ Evaluate ▸ Mass Properties** reads **0.00 g** with an empty Solid Bodies folder.

</details>

<details>
<summary><b>7.14 — Belly Drop-Door Plumbing &amp; Deflection Margin (<code>LAY_Belly_Clearance</code>)</b></summary>

This lays an external clearance overlay tracking beneath the bottom cabin keel, protecting the gravity drain line and plumbing stack through a hard-landing gear compression. It tracks the **flat-bottom keel** — the constant lower keel line at `= "h_fuse_bottom"` relative to the waterline. Body-free overlay — zero mass. Budget ~10 minutes.

1. **Start the overlay sketch.** Insert ▸ Sketch on the Right Plane ($X = 0$); this becomes `LAY_Belly_Clearance`, filed in `2_LAYOUT_SKETCHES`.
2. **Track the keel.** Sketch ▸ **Line** spanning the drain region aft ($-Z$).
   * Make the forward endpoint **Coincident** to the keel profile at the drain station; Smart-Dimension its $Z$ to `= "x_drain"`.
   * Add a **Horizontal** relation so the baseline runs parallel to the waterline at the keel height.
3. **Project the plumbing stack.** Select the baseline ▸ **Offset Entities** ▸ distance `= "plumb_drop"` ▸ direction $-Y$ (down). This lower line is the physical bottom of the drain / plumbing stack.
4. **Add the deflection margin.** Drop a second **Horizontal** construction line a further `= "belly_margin"` below the stack line — the minimum belly-to-ground gap that must survive **full gear compression**. Tie it to the master **Ground Line** (§6.7) through the static axle height `= "gear_h"` so the margin tracks stance changes instead of floating.
5. **Close and constrain.** Bound the overlay into a region with four lines, corners **Coincident**, so it reads as one clearance box. Select all entities ▸ **For construction**.
6. **Do not solidify.** Exit the sketch. Do **not** extrude, thicken, revolve, or surface it — the overlay stays a flat construction sketch (§14 item 33).

> **Verification & Success state:** `LAY_Belly_Clearance` is fully defined (black), lives on $X = 0$, and brackets the keel from `= "x_drain"` aft ($-Z$). The stack line sits `= "plumb_drop"` below the keel; the margin line sits a further `= "belly_margin"` below and references `= "gear_h"` off the Ground Line. Every entity is construction; the skeleton still reads **0.00 g** with an empty Solid Bodies folder.

</details>

<details>
<summary><b>7.15 — Mechanical Ground-Steering Linkage Sweep (<code>LAY_Steering_Links</code>)</b></summary>

This maps the tailwheel pushrod / cable trajectory from the steering kingpin forward to the servo, bounding it against the cabin rear wall (`x_fuse_bay_aft`) and the propulsion-battery envelope so no linkage fouls an internal envelope. Everything rides in the Right Plane on the same $+Z$ forward / $+Y$ up frame as pure construction geometry — zero solid bodies. Budget ~12 minutes.

1. **Start the linkage sketch.** Insert ▸ Sketch on the Right Plane ($X = 0$); this becomes `LAY_Steering_Links`, filed in `2_LAYOUT_SKETCHES`.
2. **Seed the horn sweep.** Sketch ▸ **Circle** (construction) centered where `AX_Tail_Steer` (§7.9.2) meets the deck, radius `= "horn_R"`. Add a **Coincident** between the circle center and the axis endpoint (use **Pierce** if the kingpin crosses the sketch plane). This arc is the output-horn envelope.
3. **Lay the push-link.** Sketch ▸ **Line** from a point on the horn arc forward ($+Z$), length `= "link_L"`. Add a **Coincident** of its aft end onto the horn circle so the link origin rides the arc.
4. **Run the trajectory.** Continue a line from the link's forward end toward the servo, forward ($+Z$) along the internal deck; add a **Horizontal** relation (or dimension its run angle). Terminate it at the servo station — Smart-Dimension to `= "x_steer_servo"`, aft ($-Z$).
5. **Build the clearance corridor.** **Offset Entities** the trajectory line symmetrically by `= "horn_R"` to each side ($\pm Y$), forming a band; set the band lines **For construction**.
6. **Bound against the internal walls.** Drop a **Vertical** construction reference line at the bay aft wall, $Z = -$`"x_fuse_bay_aft"`, and a second at the propulsion-battery aft face, `= "x_bat_aft"`. Confirm the corridor band — including its full steering sweep — stays **aft of** the bay wall and clear of the battery reference. This is a **measured / visual audit**, not an auto-compute compliance equation — wire a hard `link_clear` check only once the servo and wall stations are frozen (offer stands).
7. **Set construction, exit.** Select every trajectory, corridor, and bound entity ▸ **For construction**. Exit the sketch — no sweep feature, no body.

> **Verification & Success state:** `LAY_Steering_Links` is fully defined (black) on $X = 0$, originates at `AX_Tail_Steer` through the `= "horn_R"` arc, carries a `= "link_L"` push-link, and runs forward to `= "x_steer_servo"`. The corridor band does **not** intersect the bay-aft-wall line ($Z = -$`"x_fuse_bay_aft"`) or the battery-front reference. All entities are construction; the skeleton reads **0.00 g** with an empty Solid Bodies folder.

---

</details>

</details>

<details>
<summary><b>I-7. Validation — installation checks  <i>(from skeleton §13.3.8 / §13.7.6)</i></b></summary>

## I-7. Validation — installation checks  *(from skeleton §13.3.8 / §13.7.6)*

<details>
<summary><b>13.3.8 — Fluid-systems &amp; steering clearance rebuild check (§7.13–§7.15)</b></summary>

Prove the fill, belly, and steering datums re-track their drivers under a combined cabin / gear flex. **Tools ▸ Equations**: raise `h_fuse_top` (+20 mm), shift `x_bay` (60 → 75), and grow a tire (`wheel_main` 60 → 90, so `gear_h` rises), then force a **`Ctrl + Q`** rebuild.
- *Fill path:* `AX_Fill_Path` re-extends so its upper end still clears `h_fuse_top` (the overshoot holds) and its lower end stays **Coincident** to the cabin crown as the fill station walks with `x_bay`.
- *Belly overlay:* the `LAY_Belly_Clearance` baseline re-drops with the keel (`= "h_fuse_bottom"`) and still holds `plumb_drop` below it and `belly_margin` below that, the margin line tracking the Ground Line through `gear_h`.
- *Steering corridor:* `LAY_Steering_Links` re-sweeps off `AX_Tail_Steer` and the corridor stays aft of `PLN_Fuse_Bay_Aft` (`x_fuse_bay_aft`) and clear of the battery reference.
- *Body-free:* **Tools ▸ Evaluate ▸ Mass Properties** → still **0.00 g**, Solid Bodies folder empty (§13.8). **Undo all.**

</details>

<details>
<summary><b>13.7.6 — Taildragger stance &amp; prop-clearance check (§7.9)</b></summary>

A taildragger flies through two attitudes, so the propeller clearance must be legal in **both**.
- **3-point stance (static, tail down):** confirm both main-tire rectangles and the tailwheel circle rest on the Ground Line (Tangent / flush, §7.9.3). Nose-high, so the blade tip sits *higher* — record the tip-to-ground here as the loose case.
- **2-point / takeoff attitude (tail up, waterline level):** rotate the model so the fuselage waterline runs parallel to the Ground Line. **Measure** the prop-disk bottom to the Ground Line — this is the **tight** case and must stay $\ge$ `prop_clear` (`= "prop_clear"`; §6.7). A taildragger's blade is closest to the runway just as the tail lifts, so this attitude, not the static one, governs.
- **Mains-forward check:** **Measure** `PT_Main_Axle` (or `AX_GearAxle`) to `PT_CG_target` along $Z$ and confirm the axle is **forward ($+Z$, smaller aft-distance)** — a positive nose-over margin.
- **Radius-float check:** bump `wheel_main` (60 → 70) and `wheel_tail_dia` (30 → 40) ▸ **`Ctrl + Q`**; the axles must rise on their radius equations while the Ground Line holds and the stance angle re-solves (not error). A rebuild fault here means an axle is pinned to the waterline (§14 item 29). Restore.
- *Body-free:* all wheels, arcs, and the kingpin are construction / reference — Mass Properties stays **0.00 g** (§13.8).

---

</details>

</details>

<details>
<summary><b>I-8. Common pitfalls — installation  <i>(former skeleton §14 items 24–34; numbers retained)</i></b></summary>

## I-8. Common pitfalls — installation  *(former skeleton §14 items 24–34; numbers retained)*

**24. Dangling servo references (globals not in the equations file).** The servo box drives off `servo_L` / `servo_W` / `servo_H`, which are **new** — if they are not in `skeleton_equations_micro.txt`, every box dimension dangles and the bay cannot rebuild.
- *Detect:* `= "servo_L"` dimensions show the dangling link colour; **Tools ▸ Equations** lists `servo_*` as unresolved; deleting the servo station orphans the plan / section boxes.
- *Fix:* add `"servo_L" = 23`, `"servo_W" = 12`, `"servo_H" = 22` to the equations file (and mirror into Appendix A), then **`Ctrl + Q`**; re-point any box edge left pinned to a stale value.
- *Prevent:* confirm the three servo globals are present in the equations file (§7.7 intro); keep servo geometry **For construction** so a missing global never leaks a solid body.

**25. OML skin breach on a low-aspect-ratio wing.** Micro's big-chord / thin sections mean a tall servo — or an aggressive `c_ail_pct` chord change — can push the keep-out box or the moving surface through `SURF_Wing_OML`.
- *Detect:* the §7.7.3 Intersection-Curve overlay shows the `servo_H` box crossing the upper / lower skin line; the aileron LE at 75 % chord protrudes past the OML at the thin outboard station.
- *Fix:* reduce `servo_H` (lower-profile servo), move the bay inboard toward `y_ail_in` (thicker section), or deepen the section locally on the derived skin part — never bulge the skeleton OML.
- *Prevent:* run the skin-breach audit at the **thinnest** (outboard) servo station, not the root; re-check whenever `c_tip`, `taper`, or a servo dimension changes (§13.3.6).

**26. Unconstrained door-swing geometry.** A drop-door line, arc, horn, or link left short a relation drifts on rebuild, so the fully-open envelope you audited is not the one that flies.
- *Detect:* a `(-)` prefix on `LAY_Side_Profile` (or `LAY_Hatch_Kinematics`); a **blue** door line, arc, or `PT_Hatch_Pivot`; the swept arc changes shape when an unrelated global moves.
- *Fix:* pin the pivot to the keel (**Coincident**) *and* its $Z$ to `= "x_fuse_bay_fwd"`; make the two door lines **Equal**, the open angle `= "hatch_open_deg"`, and the horn / link `= "horn_R"` / `= "link_L"` (§7.8.1).
- *Prevent:* fully define the kinematic sketch before exiting (§13.1); keep the gear-clearance dimension (§7.8.1 step 7) in the §13.7.5 sign-off so a drifted door is caught.


**28. Payload door breaching the lower fuselage OML when closed.** A closed drop-door must sit *flush with* the belly skin; if its construction line is dimensioned below the keel — or the OML is re-lofted deeper — the closed door pokes through `SURF_Fuse_OML`.
- *Detect:* the closed-door line sits below the `BF → BR` keel; an Intersection Curve of `SURF_Fuse_OML` on the Right Plane shows the door outboard of (below) the skin; the belly reads a step or gap at the hatch.
- *Fix:* re-pin the closed-door line **Collinear** to the bottom keel and the pivot **Coincident** to it (§7.8.1 step 2–3); if the OML moved, re-verify the keel station against `h_fuse` / `h_fuse_top`.
- *Prevent:* always seat the *closed* door on the keel line, never on a free dimension; re-check the belly after any §4.4 or §8.5 fuselage edit (§13.1).

**29. Over-constrained Ground Line (both axles hard-pinned to the waterline).** Pinning each axle directly to the $Y = 0$ waterline locks the stance angle and over-defines the model the instant a tire diameter changes — the Ground Line can no longer float on tire radius.
- *Detect:* changing `wheel_main` or `wheel_tail_dia` throws an over-defined / rebuild error; the axle rectangles turn **yellow**; the stance angle will not update.
- *Fix:* delete the axle-to-waterline pins; instead hold each axle its **tire radius** above the Ground Line (`= "gear_h"`, `= "gear_h_tail"`) and pin only the **ground contact** (Tangent / flush) to the Ground Line (§7.9.3).
- *Prevent:* keep the waterline as the *airframe* datum and the Ground Line as the *stance* datum, coupled **only** through the radius equations; run the §13.7.6 radius-float check before sign-off.

**30. Steering axis binding due to trailing-edge / tail-cone flex.** If `AX_Tail_Steer` is welded to a thin, unsupported aft tail-cone section, the kingpin drifts as the fuselage flexes and the tailwheel binds or won't self-center.
- *Detect:* `AX_Tail_Steer` moves when an aft fuselage global (`x_fuse_tail`, tail-cone taper) is flexed; the kingpin no longer passes through the reinforcement former; `PT_Tail_Axle` shifts off the Ground Line tangent.
- *Fix:* anchor the kingpin to a **reinforced former station** (a `PLN_Fuse_*` plane through the plywood reinforcement, §7.9.4), not to the bare skin; re-add the tail-cone former if the aft bay is unsupported.
- *Prevent:* always route `AX_Tail_Steer` through a structural former; keep the rake dimension on `= "tail_steer_rake"` and confirm the axis holds when `x_fuse_tail` flexes (§13.1).

**31. Ground-loop instability (mains too close to the target CG).** A taildragger whose main axles sit almost under the CG has a tiny anti-nose-over arm and a short yaw base — it noses over on braking and ground-loops on rollout.
- *Detect:* **Measure** `PT_Main_Axle` → `PT_CG_target` returns a near-zero (or aft) $Z$ offset; the mains are level with or behind the CG.
- *Fix:* reduce `x_main` to move the mains **forward ($+Z$)** of the CG, restoring a deliberate anti-nose-over arm; re-confirm the §13.7.6 mains-forward check.
- *Prevent:* treat "mains forward of `PT_CG_target`" as a hard rule for the conventional config; re-check the offset whenever `CG_pct`, `x_bay`, or `x_main` changes (§7.9.1).

**32. Fill-path axis stops short of a re-lofted crown.** `AX_Fill_Path` Pierced to the crown profile *without* an overshoot dimension ends flush at the keel; a later taller crown re-loft then leaves the fill line buried inside the hull.
- *Detect:* the axis top sits *on* the crown curve, not above it; after a `h_fuse_top` bump the deploy line no longer breaks the skin.
- *Fix:* add the `= "h_fill_top"` overshoot dimension above the Pierce (§7.13 step 4).
- *Prevent:* always overshoot the crown; never Pierce-only.

**33. Fluid / steering overlay left non-construction (mass creep).** A belly-clearance or steering entity left as normal (not construction) geometry — or worse, thickened / lofted — puts a solid body into a body-free master and breaks the §13.8 zero-mass rule.
- *Detect:* **Mass Properties** reads non-zero; the Solid Bodies folder is no longer empty; the clearance box shades as a filled region.
- *Fix:* select the offending entities ▸ **For construction**; delete any extrude / thicken feature.
- *Prevent:* set every overlay entity construction before exiting the sketch (§7.14 step 6, §7.15 step 7).

**34. New fluid / steering globals absent from the equations file.** `LAY_Belly_Clearance` and `LAY_Steering_Links` drive off `plumb_drop`, `belly_margin`, and `x_steer_servo` — if these are not in `skeleton_equations_micro.txt`, every dimension referencing them dangles and the sketches cannot rebuild (same failure class as the servo globals, §14 item 24).
- *Detect:* `->x` dangling markers on the belly / steering dimensions; the sketches will not solve.
- *Fix:* confirm the three globals (and `horn_R` / `link_L` from §7.8) are present in the equations file and re-Import.
- *Prevent:* keep Appendix A of the parameter reference byte-identical to the equations file; add new globals to both before referencing them.

</details>