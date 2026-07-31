# Standalone Skeleton Sketch Part (SSP) — SolidWorks Setup Guide
### SAE Aero Design 2026 · **Micro Class** · skeleton-driven top-down workflow

> **Updated from the generic guide.** Three changes: (1) the layout is tailored to the Micro Class parameter set (`Aircraft_Skeleton_Parameters_Micro.md` / `skeleton_equations_micro.txt`), (2) **the aircraft front view now sits on the Front Plane**, which means the longitudinal axis runs along SolidWorks **Z**, and (3) **the airframe is now a rounded fuselage** driven by an **elliptical maximum cross-section** on the Front Plane (§6.4), with the longitudinal axis still on SolidWorks **Z**. The convention swap is detailed in §2.

---

## 0. The core idea

A Skeleton Sketch Part is a **single, body-free `.SLDPRT`** holding *only* reference geometry — planes, sketches, axes, points, coordinate systems, and optionally master surfaces. It is the **single source of truth** for every architectural dimension (span, chords, spar stations, tail arm, thrust-line height, CG, compliance hardpoints). Every downstream component derives its geometry *from* the skeleton, never the reverse. Change one master parameter and the whole airframe updates.

> **Scope — this is the `SKELETON` (published geometry, layers L0–L3).** It carries only what *two or more* downstream parts must agree on: the aircraft datum frame (L0), aero / OML (L1), wing & empennage structure (L2), and the fuselage / interface layer (L3 — stations, bulkheads, mounting planes, keep-out boundaries, CG / NP datums). **Single-consumer component and mechanism geometry — servos, batteries, the payload drop-door, landing-gear wheels, and clearance / linkage studies (L4) — is *not* here.** The payload container is not modeled in *either* file: the water is carried as mass only. It lives in the companion **`INSTALLATION`** layout (`Installation_Layout_Guide_Micro.md`), a body-free part that **Insert-Part-derives this skeleton** and builds those space-claims on the inherited datums. The test: if only *one* part consumes a feature, it is installation, not skeleton.

Why standalone (vs. an in-assembly layout sketch):

- **One-directional dependency** — skeleton → parts. Kills circular references and "in-context hell."
- **Versionable independently** — one member owns the skeleton; structures/aero/payload leads consume it without touching it.
- **Reusable** — one file drives empty / loaded / drained payload configurations (§11).
- **Robust references** — parts link to a stable *file*, not fragile assembly context.

Dependency flow:

```
  sizing spreadsheet (aero/perf, SI)
            │  (linked variables)
            ▼
   SKELETON SKETCH PART  ◄── nothing downstream ever drives this
            │
   ┌────────┼────────┬─────────┬────────┬─────────────────┐
   ▼        ▼        ▼         ▼        ▼                 ▼
  ribs    spars   fuselage   tail    gear      drain port + compliance hardpoints
            │
            ▼
       TOP ASSEMBLY  (mates to skeleton datums)
```

---

## 1. File and naming conventions — step by step

Do all of this **before** you draw any geometry. Once a part references the skeleton, renaming or moving the file breaks the link, so the goal here is to lock the name, path, units, and conventions up front. Budget ~20 minutes.

### 1.1 Build the project folder (one shared, fixed location)
External references resolve by **path**, so every team member must reach the files at the *same* path — a PDM vault, or a synced cloud/network drive mapped to the same drive letter for everyone (e.g. everyone mounts it as `Z:`).

1. Create the project root, e.g. `Z:\SAE_Micro_2026\`.
2. Inside it, create:
   - `01_Skeleton\` — the skeleton part, nothing else
   - `02_Parts\` — ribs, spars, fuselage, tail, gear
   - `03_Assemblies\`
   - `04_Drawings\`
   - `05_Sizing\` — the aero spreadsheet + the linked `skeleton_equations_micro.txt`
   - `06_Tooling\` — molds, layup jigs, fixtures
   - `99_Archive\` — dated backups
3. Drop `skeleton_equations_micro.txt` into `05_Sizing\` now (you link to it in §3).

Keep the tree shallow and **never reorganize it after parts exist**. If you must relocate it, use **File ▸ Pack and Go** (§10) — never Windows drag-and-drop.

### 1.1.5 Establish the team template folder
Before saving any files, add a dedicated template directory to the shared structure so file paths remain identical for all users.
1. Open your shared project root (e.g., `Z:\SAE_Micro_2026\`).
2. Create a new folder at the top level named `00_Templates`.
3. Your updated project tree will look like this:
   - `00_Templates\` — For team `.prtdot`, `.asmdot`, and `.drwdot` files
   - `01_Skeleton\` — The skeleton part, nothing else
   - `02_Parts\` — Ribs, spars, fuselage, tail, gear
   - `03_Assemblies\`
   - `04_Drawings\`
   - `05_Sizing\` — The aero spreadsheet + the linked `skeleton_equations_micro.txt`
   - `06_Tooling\` — Molds, layup jigs, and fixtures
   - `99_Archive\` — Dated backups

### 1.1a Setting up the shared `Z:` drive (virtual drive mapping)
To ensure every team member uses the exact same absolute file path and avoids broken external references in SolidWorks, follow these steps to map your shared project folder to a virtual `Z:` drive.

#### Method 1: The Windows `subst` Command
*Best for: OneDrive, Dropbox, Box, or standard local network sync folders.*

The `subst` (substitute) command is a built-in Windows utility that associates a local folder path with a virtual drive letter.

##### Step 1: Copy your local folder path
1. Open Windows File Explorer and navigate into your team's shared root directory (e.g., `SAE_Micro_2026`).
2. Click on the file path bar at the top of the window to reveal the full text path.
3. Copy this path (it will look something like `C:\Users\YourName\OneDrive - University\SAE_Micro_2026`).

##### Step 2: Map the drive via Command Prompt
1. Press the **Windows Key**, type **`cmd`**, and press **Enter** to open the Command Prompt.
2. Type `subst Z:` followed by your copied path enclosed in quotation marks:
   `subst Z: "C:\Users\YourName\OneDrive - University\SAE_Micro_2026"`
3. Press **Enter**. Open "This PC" in File Explorer, and you will now see a **`Z:` drive** listed under your locations.

##### Step 3: Make it permanent (Automate on Startup)
By default, Windows clears virtual drives created by `subst` whenever you restart your computer. Follow these quick steps so it runs automatically every time you boot up:
1. Open Notepad.
2. Paste your exact command from Step 2 into the text file:
   ```cmd
   @echo off
   subst Z: "C:\Users\YourName\OneDrive - University\SAE_Micro_2026"
   ```
3. Click **File ▸ Save As**.
4. Change "Save as type" to **All Files (*.*)**.
5. Name the file **`map_z_drive.bat`** and save it somewhere safe (like your local documents folder).
6. Press **Win + R**, type **`shell:startup`**, and click **OK**. This opens your Windows Startup folder.
7. **Right-click** your `map_z_drive.bat` file, select **Copy**, then **Right-click ▸ Paste Shortcut** inside the Startup folder.

#### Verification & Setup Validation
Before opening SolidWorks, run these quick checks to ensure the backbone path is operating correctly:
1. **Command Line Audit:** Open Command Prompt, type plain `subst`, and press **Enter**. It should output: `Z:\: => C:\Your\Local\Path\To\Shared\SAE_Micro_2026`. If it returns nothing, the map is inactive.
2. **Folder Nesting Check:** Open `This PC` ▸ `Z:`. You should *immediately* see your top-level subfolders (`01_Skeleton`, `02_Parts`, `03_Assemblies`). If you see a nested `SAE_Micro_2026` folder first, your path is mapped one level too deep. Clear it with `subst Z: /d` and remap.
3. **Startup Link Test:** Double-click the shortcut in your `shell:startup` folder. A command window should flash briefly, ensuring the `Z:` drive initializes properly on every system boot.

### 1.2 Set the document template and units
1. **File ▸ New ▸ Part**.
2. **Tools ▸ Options ▸ Document Properties ▸ Units** → select **MMGS (millimeter, gram, second)**; set Angle to **degrees**; set length decimals to 2. *(MMGS is required for the equation set to read correctly.)*
3. **File ▸ Save As**, set "Save as type" = **Part Templates (\*.prtdot)**. Browse to `Z:\SAE_Micro_2026\00_Templates\`, and save the file as **`SAE_Micro_Part.prtdot`**.
4. **Map the path locally (Every team member must do this):**
   - Go to **Tools ▸ Options ▸ System Options ▸ File Locations**.
   - Under the **Show folders for:** dropdown, select **Document Templates**.
   - Click **Add**, browse to and select `Z:\SAE_Micro_2026\00_Templates\`, and click **Select Folder**.
   - *(Recommended)* Select the default local `C:` drive paths in this box and click **Delete** to force the team to use the shared repository. Click **Apply**.
5. **Lock it in as the default:**
   - Click the **Default Templates** tab (still within System Options).
   - Click the browse button (**...**) next to the **Parts** field.
   - Click the `00_Templates` tab at the top of the pop-up, select **`SAE_Micro_Part.prtdot`**, and click **OK**.
   - Ensure the radio button for **"Always use these default document templates"** is checked and click **OK**.

Now every part on the team starts in MMGS with the same standard. Anyone who clicks "New Part" will automatically pull from the exact same master file.

### 1.3 Create and name the skeleton file
1. From that part, **File ▸ Save As** → browse to `Z:\SAE_Micro_2026\01_Skeleton\`.
2. File name: **`AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`**. Save.
3. *(Optional)* Give it a distinct look so it's obvious in assemblies: right-click the part name ▸ **Appearances** ▸ pick a flat translucent color.

**Freeze this filename now** — it is the one name every part will link to.

### 1.4 Record the convention inside the file (two places)
So the convention travels with the file and can't be missed:

1. **Custom properties** — **File ▸ Properties ▸ Custom**, add:

   | Property | Value |
   |---|---|
   | `Description` | SAE Micro 2026 master skeleton |
   | `Engineer` | (owner's name) |
   | `Revision` | A |
   | `Units` | MMGS / deg |
   | `Convention` | Front view on Front Plane; +Z forward (nose), +X port, +Y up; symmetric about Right Plane; origin = wing-root LE |
   | `Date` | (today) |

   These surface in PDM, the drawing title block, and BOMs.
2. **On-screen note** — open a sketch on the **Front Plane**, name it `LAY_Datums`, and add a **Note** (**Insert ▸ Annotation ▸ Note**) restating axis directions, symmetry plane, origin, and units. Anyone who opens the file sees it immediately.

### 1.5 Adopt the feature-naming scheme (rename as you go)
Rename **every** feature the moment you create it — slow-double-click it in the FeatureManager tree, or select it and press **F2**. Use these prefixes:

| Feature type | Prefix | Examples |
|---|---|---|
| Layout sketches | `LAY_` | `LAY_Front_View` (Front Plane), `LAY_Side_Profile` (Right Plane), `LAY_Wing_Plan` (Top Plane — fuselage & CG only), `LAY_Wing_Incidence` (`PLN_Incidence` — the whole wing), `LAY_HTail_Incidence` (`PLN_Incidence_HT` — the whole stabilizer), `LAY_VT_Spar` (Right Plane), `LAY_Payload`, `LAY_Gear` |
| Reference planes | `PLN_` | `PLN_RibStn_R01`…, `PLN_Thrust`, `PLN_PropDisk` |
| Reference axes | `AX_` | `AX_MainSpar`, `AX_Thrust`, `AX_Prop`, `AX_GearAxle`, `AX_WingJoiner` |
| Reference points | `PT_` | `PT_CG_loaded`, `PT_CG_drained`, `PT_CG_fwd`, `PT_CG_aft`, `PT_Drain`, `PT_ArmPlug`, `PT_Switch`, `PT_Ballast` |
| Coordinate systems | `CSYS_` | `CSYS_Wing`, `CSYS_HTail` |

One sketch per view/subsystem — **never one giant sketch** (they split poorly across the team and rebuild slowly).

### 1.6 Organize the FeatureManager tree into folders
A ~100-variable skeleton accrues a lot of features; group them so the tree stays navigable. Ctrl-click related features ▸ right-click ▸ **Add to New Folder**, then rename the folder:

`0_DOC` · `1_DATUMS` · `2_LAYOUT_SKETCHES` · `3_RIB_PLANES` · `3B_FUSELAGE_PLANES` · `4_AXES` · `5_POINTS` · `6_CSYS` · `7_SURFACES`

(Folders are organizational only — they don't change rebuild order.) `3B_FUSELAGE_PLANES` holds the dedicated fuselage stations (§7.3.6) and sits deliberately beside — not inside — `3_RIB_PLANES`, so the wing and fuselage grids stay visibly decoupled.

### 1.7 Set the revision and backup rule
- Bump the `Revision` custom property on each meaningful change (A → B → …).
- **No PDM:** before a major edit, copy the file into `99_Archive\` with a dated suffix (`AIRCRAFT_SKELETON_SAE_MICRO26_2026-06-28_revA.SLDPRT`). Never rename the live file.
- **With PDM:** check in with a comment describing the change and let the vault hold history.

### 1.8 Freeze before anyone consumes it
Do not rename or relocate the skeleton once the first part references it (§9). Confirm the filename, folder path, units, and the convention note are all final, then commit / check in. Everything downstream trusts this exact name and path.

> Carry-over rule: **every sketch fully defined (black)** before you move on — under-defined sketches drift unpredictably when parameters change.

---

## 2. Coordinate system and datum planes  ← *front view on the Front Plane*

Decide the convention **once** and pin a sketch note inside the file documenting it.

**Origin:** wing-root **leading edge**, on the plane of symmetry.

**Axis directions (right-handed):**

- **SolidWorks Z = longitudinal** (**+Z forward, toward the nose/motor**; −Z aft, toward the tail) — normal to the Front Plane.
- **SolidWorks Y = vertical** (+Y up) — vertical in the Front Plane.
- **SolidWorks X = lateral / spanwise** (**+X to port; starboard = −X**) — lies horizontal in the Front Plane.

Because the **front view** (what you see looking down the fuselage: span across, height up) lives in the Front Plane, the longitudinal axis is necessarily **Z** (the Front Plane's normal). The aircraft is **symmetric about the Right Plane (the X = 0 plane)** — mirror the wing and tail across the **Right Plane**.

> **Why +X is port:** for a right-handed frame with the nose at +Z and +Y up, the starboard wing falls on −X. This is immaterial — the airframe is symmetric about the Right Plane, so which wingtip is +X is just a label.

**Plane → view mapping (new):**

| SW plane | Normal | Aircraft view | What you draw here |
|---|---|---|---|
| **Front (XY)** | Z (longitudinal) | **FRONT view** (span × height) | Dihedral, frontal silhouette, fin height, gear track, max fuselage cross-section, **prop disk + 9-in keep-out ring**, water-container cross-section |
| **Top (XZ)** | Y (vertical) | **Planform / top view** (span × length) | Wing & tail outlines, spar/web lines, rib stations, MAC, CG (loaded & drained), control-surface stations |
| **Right (YZ)** | X (lateral) | **Side view / plane of symmetry** (length × height) | Fuselage profile, thrust line, longitudinal stations, tail arm, **bottom drain port**, **arming plug & switch on top**, battery side profile |

**Parameter-name crosswalk (important).** The parameter files name longitudinal stations `x_*` in standard aircraft body-axis convention (aircraft *x* = longitudinal). The equation set is pure scalar math — it computes station/length *values* and is **unchanged** by this layout. The convention only dictates which SolidWorks plane/direction each value is applied in:

| Parameter family | Physical direction | Apply along SolidWorks axis |
|---|---|---|
| `x_motor`, `x_CG`, `x_MAC_LE`, `x_HT_c4`, `x_drain`, `x_arm_plug` … (`x_*`) | longitudinal (positive distance from LE) | place point on **+Z** (forward) or **−Z** (aft) side |
| `b`, `b_semi`, `y_MAC`, `y_ail_*`, `track` | lateral / spanwise (+port) | **X** |
| `gear_h`, `h_thrust`, `h_fuse` (vertical extent) | vertical (+up) | **Y** |

All longitudinal globals are **positive distances from the Wing LE**. Positive Z coordinates are forward; negative Z coordinates are aft. Place each station point on the **+Z** (forward) or **−Z** (aft) side of the origin, and Smart Dimension it using the positive global directly. A spanwise value like `y_MAC` goes along **X**; a height like `gear_h` along **Y**.

### Build it — step by step

You won't *create* the frame from scratch — a new part already has the Origin and the three default planes. The work is to (a) declare what they mean, (b) add a master coordinate system and the longitudinal axis, (c) stand up your first parametric datum plane, and (d) verify directions. Budget ~15 minutes.

**2.1 — Know the frame you already have.** A new part's Origin sits at $(0,0,0)$ where the three default planes meet. Declare that point = the **wing-root leading edge**. No rotation is needed: the Front Plane already spans X (horizontal) and Y (vertical) with Z as its normal — exactly span-across / height-up / longitudinal-normal — so the defaults map straight onto the views in the table above.

**2.2 — Confirm axis directions, and know what you'll see on screen.** Check the reference triad (bottom-left of the graphics area): X right, Y up, Z toward you.
- We set **+Z = forward** (toward the nose/motor); **−Z = aft**. All longitudinal globals are positive distances from the LE — place forward features (e.g. `x_motor = 230`) on the **+Z** side and aft features on the **−Z** side, dimensioning with the positive global directly.
- Bonus: SolidWorks' default **Front** view (`Ctrl+1`) looks down −Z toward the nose, so it shows the aircraft's **nose** — the conventional front view. Use **Back** (`Ctrl+2`) to view the tail. The front-view geometry is left-right symmetric, so the choice of camera is only cosmetic.

**2.3 — Create the longitudinal centerline axis (`AX_Long`).** The fuselage reference line everything hangs off.
1. **Insert ▸ Reference Geometry ▸ Axis**.
2. Choose **Two Planes**; select the **Top Plane** and the **Right Plane** (their intersection *is* the Z axis).
3. OK → rename to `AX_Long`.

**2.3.1 — Create the empennage longitudinal axis (`AX_Long_Emp`).** The tail does not hang off the wing-root waterline — it rides the boom, `y_emp_axis` = 25 mm **above** the Top Plane. Give it its own datum so the whole empennage moves as one when that height changes.
1. **Insert ▸ Reference Geometry ▸ Plane**: **First Reference** = the **Top Plane**, **Offset Distance** `= "y_emp_axis"`, flipped so it sits **above** ($+Y$). Green-check; **F2** → `PLN_Emp_Datum`. Drop it into `1_DATUMS`.
2. **Insert ▸ Reference Geometry ▸ Axis**, **Two Planes**: select `PLN_Emp_Datum` and the **Right Plane**. Green-check; **F2** → `AX_Long_Emp`. File it in `1_DATUMS`.
> **What it is.** A fore-aft line at $X = 0$, $Y = $ `y_emp_axis` — parallel to `AX_Long` and 25 mm above it. **Every empennage feature pivots on or attaches to `AX_Long_Emp`, never `AX_Long`.** The wing keeps `AX_Long`. Change `y_emp_axis` and the horizontal stabilizer, its datum planes and its spar all translate together; nothing on the wing moves.

**2.4 — Create the master coordinate system (`CSYS_Master`).** A named, exportable datum and a clean mate target for downstream parts, mass properties, and FEA.
1. **Insert ▸ Reference Geometry ▸ Coordinate System**.
2. **Origin:** click the part **Origin**.
3. **Z axis:** select `AX_Long`; use the flip arrow so +Z points **forward** (toward the nose).
4. Leave X and Y to default; use the flip arrows so the preview triad reads **X-port, Y-up** (starboard = −X). OK → rename `CSYS_Master`.

**2.5 — Lock in the symmetry plane.** The **Right Plane (X = 0)** is the plane of symmetry. Every paired feature — wing halves, both main gear, twin fins — gets a **Symmetric** relation to it (or is mirrored across it). Nothing to build here; just confirm the `LAY_Datums` note (§1.4) states "symmetric about Right Plane" so no one mirrors across the wrong plane.

**2.6 — Build your first parametric datum plane (`PLN_PropDisk`) — the move you'll reuse everywhere.** It anchors the prop disk, thrust line, and 9-in keep-out, and it teaches the offset-plane-driven-by-a-global technique used for every rib station in §7.
1. **Insert ▸ Reference Geometry ▸ Plane**.
2. **First Reference:** the **Front Plane**; pick **Offset Distance**.
3. In the distance box type `= "x_motor"`. Tick **Flip** so the plane lands **forward** of the wing LE (**+Z** side).
4. OK → rename `PLN_PropDisk`. It now tracks `x_motor` automatically; every rib-station plane is built the same way — offset a parent plane by a global.

**2.7 — (Optional) Annotate, don't rename, the defaults.** Leave the three planes named **Front/Top/Right** (renaming them can break template/macro references); rely on the `LAY_Datums` note for their aircraft-view roles. For visual cues, right-click each plane ▸ **Appearance/Color** to tint it while laying out.

**2.8 — Verify and lock.** Before drawing any geometry, confirm:
- Triad reads X-port / Y-up / Z-forward (starboard = −X); `Ctrl+1` (Front) shows the nose.
- `AX_Long`, `AX_Long_Emp` and `CSYS_Master` exist and are oriented correctly; **Measure** `AX_Long_Emp` to `AX_Long` reports `y_emp_axis` = 25 mm.
- `PLN_PropDisk` sits forward of the LE and **moves when you change `x_motor`** (test it, then undo).
- `LAY_Datums` note states origin, axes, symmetry plane, and units.
- `Ctrl-Q` rebuild is clean. Drop `CSYS_Master`, `AX_Long`, `PLN_Emp_Datum`, `AX_Long_Emp`, and `PLN_PropDisk` into the `1_DATUMS` tree folder (§1.6).

---

## 3. Parametric backbone — global variables and equations

This is what makes the skeleton *drive* rather than *describe*: a ~100-variable set where you type a handful of inputs and the geometry-defining values compute themselves. Highlights that differ from a generic airframe:

- **Wing:** geometry-first inputs `b`, `c_root`, `c_tip` → derived `S_w`, `AR`, `MAC`, `y_MAC`, `x_MAC_LE`, `x_MAC_c4`. **No span cap, but span is a scoring penalty → minimize** (Micro wings trend low-AR, big-chord).
- **Tails (from volume coefficients):**

$$S_{HT} = \frac{V_H\,S\,\bar c}{l_{HT}}, \qquad S_{VT} = \frac{V_V\,S\,b}{l_{VT}}, \qquad b_{HT}=\sqrt{AR_{HT}\,S_{HT}}$$

- **Water-payload mass model:** `W_water = V_water · rho_water`; `W_TO = W_empty + W_container + W_water`. Container ≥ 67 fl oz = 1981 cm³.
- **Propulsion limits:** `n_cells = 4`, `P_limit = 450 W`, `keepout = 228.6 mm` (9-in prop safety).
- **Compliance checks** (keep ≥ 0): `arm_clear`, `sw_clear`.

### Load it — step by step

Budget ~15 minutes. You're loading `skeleton_equations_micro.txt` into the part's Equations, verifying it solves, then (optionally) live-linking it to the aero spreadsheet.

**3.1 — Confirm units first.** **Tools ▸ Options ▸ Document Properties ▸ Units ▸ MMGS**, angle in **degrees**. Import reads the file's bare numbers in *document* units — if the part isn't MMGS, every length loads wrong. (You set this in §1.2; confirm it before importing.)

**3.2 — Open the Equations dialog and orient yourself.** **Tools ▸ Equations**. Click the **Equation View** toggle (top-left of the dialog). You'll see three collapsible sections — **Global Variables**, **Features**, **Equations** — plus an **Import…/Export…** pair and the checkboxes **Automatically rebuild** and **Link to external file**. Everything in `skeleton_equations_micro.txt` lands in **Global Variables**.

**3.3 — Import the variable set.** Click **Import…** ▸ browse to `Z:\SAE_Micro_2026\05_Sizing\skeleton_equations_micro.txt` ▸ **Open**. The globals populate; derived values appear computed in the right-hand column.
- *If your SolidWorks version rejects the file on the comment lines:* open the `.txt` in a text editor, delete the full-line `'……` banners (keep every `"name" = value` line), save, re-Import. The `"name" = value` lines are the payload; the `'` comments are cosmetic.
- *Fallback that always works:* copy the `"name" = value` lines from the `.txt`, click the first empty **Global Variables** cell, and paste the rows in.

**3.4 — Verify it solves.** No row should be red. Tick **Automatically rebuild**, click **OK**, then **Ctrl-Q** (force rebuild). A red variable almost always means a typo or a stray comment, not a missing dependency — SolidWorks resolves the dependency graph regardless of line order.

**3.5 — Sanity-check against a hand calc.** With the current inputs (`b=1150`, `c_root=225`, `c_tip=225`, `V_H=0.98`, `l_HT=780`, `AR_HT=2.35`, `V_V=0.073`, `l_VT=780`, `AR_VT=1.54`), the dialog should read approximately:

> **These numbers are deliberately restated — this is the one place that is correct.** Everywhere else in this guide, cite the global and let it carry the value. A cross-check table has to hold an *independent* copy or it checks nothing. Regenerate it by hand whenever a wing or tail input changes; `values_audit.py` will list it, and this section is the expected exception.

| Variable | Expected |
|---|---|
| `taper` | 1.00 (untapered) |
| `S_w` | ≈ 258 750 mm² (25.9 dm²) |
| `AR` | ≈ 5.11 |
| `MAC` | ≈ 225 mm (= `c_root`, untapered) |
| `y_MAC` | ≈ 287.5 mm |
| `S_HT` | ≈ 73 100 mm² |
| `b_HT` | ≈ 414.6 mm |
| `S_VT` | ≈ 27 800 mm² |
| `b_VT` | ≈ 207.1 mm |
| `WL_g_dm2` | ≈ 124.4 g/dm² |

If these match, the import and the equation graph are correct. If `MAC`/`y_MAC` are off, suspect a units mismatch (3.1).

**3.6 — Dialog syntax reminders** (for when you edit or add equations): reference variables in quotes — `"b"`; **`sqr()` is square root**, use `^2` to square; `pi` and `abs()` are built in; store angles as plain numbers in **degrees** and convert *only inside math*, e.g. `tan("sweep_LE"*pi/180)`. Link an angle global directly to an angular *dimension* with no conversion (§2 crosswalk).

**3.7 — (Recommended) Link to the aero spreadsheet for live updates.** Decide between two modes:
- **Import (3.3) = one-time copy.** Values live in the part; edit them in the dialog. Fine for a solo quick start.
- **Link = live pipeline.** In the Equations dialog tick **Link to external file** and browse to the `.txt`. Now SolidWorks *reads* the equations from the file every rebuild — you edit the `.txt` (or have the aero spreadsheet auto-write it), not the dialog. This is the team move: sizing spreadsheet → `.txt` → skeleton → whole airframe.

  Linking caveats: the file must stay in strict `"name" = value` format and sit at the same path for **everyone** (§1.1); if it goes missing the equations break. Keep it in `05_Sizing\`. To go back to editing in-dialog, untick the box to embed the values.

**3.8 — Verify and lock.** Confirm **Automatically rebuild** is on, the `Equations` folder shows near the top of the FeatureManager tree with no errors, and a test edit of `b` (±100 mm, then undo) ripples through `S_w`, `MAC`, `S_HT`, etc. Save. You can reopen anytime via right-click the `Equations` folder ▸ **Manage Equations**.

> **Dynamic-tracking globals (read before laying out the side/front views).** Three globals are deliberately *derived* or *convention-bound* so the airframe self-corrects — never hard-type over them:
> - `y_motor_offset` `= 20` — motor/thrust-line height relative to the wing-root Origin (MMGS), carried as a **positive magnitude** like every other distance global in this model. The global gives the *distance*; **you** pick the *direction* when you dimension it — place the thrust point on the side of the Origin you want, then type the global bare. `0` runs the thrust line through the wing root. It decouples the thrust axis from the wing datum and is consumed by the side profile (§4.5), the front view (§6.6), the Ground Line (§6.7), and the authoritative prop-disk sketch (§7.3.5) — dimension it the same direction in all four or they will disagree on rebuild.
> - `gear_h` `= "gear_h"` — axle height above the Ground Line tracks the tire radius, so the tire bottom stays **permanently flush** on the ground at any `wheel_main`.
> - `prop_clear` `= "prop_clear"` — prop tip-to-ground clearance. Because the Ground Line is anchored `h_thrust` below the **thrust center** (§6.7), not the Origin, this stays valid for **any** `y_motor_offset`.

> **⭐ THE POSITIVE-MAGNITUDE RULE — no value in `skeleton_equations_micro.txt` is ever negative.** Every global is a **magnitude**. Direction is carried by the model, never by a minus sign: by which side of a datum you place a **Smart Dimension**, by the **Flip** toggle on a reference plane, or by the direction arrow on a pattern or offset.
>
> This holds for **angles as well as distances**. `i_HT` = 2.0 is a *magnitude*; the stabilizer is nose-down because `PLN_Incidence_HT` is flipped that way (§5.8.1), not because the number is negative. Likewise `thrust_down`, `thrust_side`, `twist_tip`, `dihedral` and every `sweep_*`.
>
> **Why:** a sign buried in a global is invisible at the point of use. You read `= "i_HT"` in a dimension box and cannot tell which way it points; worse, flipping the geometry *and* the sign silently doubles the error. Directions belong where you can see them on screen. Formulas may of course contain a minus **operator** — `i_tip` `= "i_wing" - "twist_tip"` is fine — the rule governs stored **values**.
>
> Verify with `python3 check.py`, which fails the build on any negative value with no exemptions.

> **⭐ THE ONE-VARIABLE RULE — every Smart Dimension takes exactly one global, never an expression.** If a dimension needs a computed value, the computation belongs in `skeleton_equations_micro.txt` as its own named global, and the **Modify** box gets `= "that_global"` and nothing else. No arithmetic, no `cos`/`tan`, no nested parentheses, no bare numbers typed into SolidWorks.
>
> **Why:** an expression typed into a dimension is invisible to the equations file, so it cannot be audited, cannot be found by `where_used.py`, and silently disagrees with the model the moment one of its inputs moves. A named global is one fact in one place. It also means a value change never requires touching this guide — you edit the `.txt` and rebuild.
>
> This applies to **Smart Dimension**, **Offset Distance** on reference planes, and the **Modify** box everywhere. It does **not** apply to spreadsheet cells in the §8.2 / §8.6 airfoil import, which are Excel formulas, not SolidWorks dimensions. Where this guide shows a global's *definition* (`x_nose` `= "x_motor" + "nose_len"`), that is documentation of the equations file, not something you type into a dimension.
>
> Verify with `python3 check.py` — it fails the build if any dimension instruction in this guide carries an expression.

**Fuselage longitudinal stations (Dedicated Fuselage Plane Strategy).** To decouple the fuselage from the wing rib grid, five stations drive dedicated fuselage planes (§7.3.6) straight off the SolidWorks $Z$-axis — independent of `rib_pitch` / `n_rib`, so flexing the wing never rebuilds the fuselage. Every value is a **positive** offset from the Front Plane; the *Side* column gives which side of the wing-root Origin it lands on (**+Z** = forward / nose, **−Z** = aft / tail). Two boundaries are **hard design limits**: the nose-tip-to-firewall front taper is pinned to **6 in** through `nose_len`, and the tail plane is pinned to **152.40 mm aft** through `x_fuse_tail` — the pod tail-cone exit. The empennage sits far aft of the pod on a **tail boom** that is deliberately **not** modeled in this skeleton; the `M2` → `TT` gap doubles as its sleeve.

| Global | Equation | Value | Side | Drives (§7.3.6) |
|---|---|---|---|---|
| `x_fuse_nose` | `= "x_nose"`  (`x_nose` `= "x_motor" + "nose_len"`) | 304.80 | +Z fwd | `PLN_Fuse_Nose` |
| `x_fuse_firewall` | `= "x_motor"` | 152.40 | +Z fwd | `PLN_Fuse_Firewall` |
| `x_fuse_bay_fwd` | absolute `= 50.00`  (fwd cabin sub-station) | 50.00 | +Z fwd | `PLN_Fuse_Bay_Fwd` |
| `x_fuse_bay_aft` | absolute `= 101.60`  (cabin rear wall) | 101.60 | −Z aft | `PLN_Fuse_Bay_Aft` |
| `x_fuse_tail` | absolute `= 152.40`  (pod tail-cone exit) | 152.40 | −Z aft | `PLN_Fuse_Tail` |

> **Watch the two flip traps.** First, `PLN_Fuse_Bay_Fwd` and `PLN_Fuse_Bay_Aft` sit on **opposite** sides of the Origin — the forward sub-station at **+Z**, the cabin rear wall at **−Z** — so they take **opposite** Flip states despite the shared name stem; they end up 151.60 mm apart. Second, `x_fuse_firewall` and `x_fuse_tail` carry the **same** magnitude, 152.40 mm, but the firewall lands **+Z forward** and the tail cap **−Z aft**, 304.80 mm apart. Read the *Side* column, never the number, when you set the offset direction.

> **The cabin is a `cabin_len`-driven prismatic section.** The firewall (`x_fuse_firewall` = 152.40 mm, **+Z**) and the cabin rear wall (`x_fuse_bay_aft` = 101.60 mm, **−Z**) bound the constant section, and their separation is `cabin_len` = **254 mm (10 in)** — the length is split across **both** walls so neither crosses the Front Plane. The section itself is `w_fuse` = `h_fuse` = **101.6 mm (4 in)** square, so the pod is **4 × 4 × 10 in**. `h_fuse_top` = 76.2 holds **75 %** of that height above the waterline, putting the flat landing floor 25.4 mm below it. Both batteries seat inside this run; the skeleton space-claims nothing else here.

> **`x_fuse_bay_fwd` is a station plane, not a loft face.** It reports the forward cabin sub-station at **50.00 mm, +Z** and publishes `PLN_Fuse_Bay_Fwd` for downstream registration, but the §8.5 loft **skips** it — the cabin is prismatic firewall → cabin-rear, so a mid-cabin section would be redundant. It is now an **absolute** input: its old driver was retired along with the payload-container globals, so the plane holds its station on its own and will **not** track any other change. Edit the number directly if you want it elsewhere.

**Component envelope globals.** Propulsion and avionics hardware are carried as reference globals so the cabin pack is auditable against the OML. All MMGS (1 in = 25.4 mm):

| Global(s) | Value [mm] | Real size |
|---|---|---|
| `motor_L` / `motor_D` | 50.80 / 39.37 | 2.00 × 1.55 in main motor |
| `bat_L` / `bat_W` / `bat_H` | 78.74 / 34.29 / 34.29 | 3.10 × 1.35 × 1.35 in 4S LiPo |
| `avi_bat_L` / `avi_bat_W` / `avi_bat_H` | 60.96 / 30.48 / 22.86 | 2.40 × 1.20 × 0.90 in avionics pack |
| `cabin_len` | 254 | 10 in constant-section cabin |
| `tail_exit_D` | 19.05 | 0.75 in tail-cone exit bounding dia. |

> **These seven globals were added to `skeleton_equations_micro.txt` this revision (136 → 143), and Appendix A of the parameter reference was updated byte-identically to match — the two stay in lock-step.** The motor mounts on the firewall firing forward into the 152.40 mm nose cone; `motor_L` (50.80) leaves ample spinner room. `tail_exit_D` drives the tail-cap closure in §4.4, §5.3.5, and §8.5.

**Transition breakpoint shaping (side-profile dodecagon).** The §4.4 side profile is a **12-sided dodecagon**: two horizontal cabin keels, two vertical apex flats, and four **shoulder transitions** — smoothed into **Style Splines** in §4.4 — each shaped by one mid control point: `M1` (nose-top), `M2` (tail-top), `M3` (tail-bottom), `M4` (nose-bottom), which replace what used to be sharp nose/tail corners. Each breakpoint is pinned by a **longitudinal** station — its column, an absolute global (`x_fuse_midnose` forward, `x_fuse_midtail` aft; the aft column sits **1 in behind `TR`/`BR`**, exactly midway to `TT`/`TB`) — and a **height** off the waterline. These now read as **direct, standalone absolute-millimeter globals** — one exact physical dimension per breakpoint, no fractional split (**Strategy 1: Absolute Millimeter Control**). The seven `h_*` / `w_fuse_break` absolutes were **added to `skeleton_equations_micro.txt`** (143 → 150) and Appendix A was updated byte-identically to match. Type each straight into the §4.4 Smart Dimensions:

| Breakpoint | Longitudinal ($Z$, from Wing-LE datum) | Height ($Y$, from waterline) | Side |
|---|---|---|---|
| `M1` (nose-top) | `= "x_fuse_midnose"` | `= "h_nose_break_top"` | +Z fwd, +Y |
| `M4` (nose-bottom) | `= "x_fuse_midnose"` | `= "h_nose_break_bottom"` | +Z fwd, −Y |
| `M2` (tail-top) | `= "x_fuse_midtail"` | `= "h_tail_break_top"` | −Z aft, +Y |
| `M3` (tail-bottom) | `= "x_fuse_midtail"` | `= "h_tail_break_bottom"` | −Z aft, −Y |

> **These are absolute millimeter dimensions — set them, don't scale them.** Each breakpoint height is a **direct global** typed to the waterline with no multiplier: `h_nose_break_top` = 68.1182 (`M1`), `h_nose_break_bottom` = 13.3096 (`M4`), `h_tail_break_top` = 65.9130 (`M2`), `h_tail_break_bottom` = 21.9710 (`M3`). Every one is a **positive magnitude** — the global carries the distance, the sketch carries the direction, so `M4` and `M3` are dimensioned **downward** from the waterline and `M1`/`M2` upward. Because they no longer track `h_fuse_top` / `h_fuse`, you own the exact shoulder geometry — dial a specific internal clearance straight in. **Envelope check (standard CAD discipline):** keep every **top** break strictly between the nose/tail flat height and the top-keel height (`h_fuse_top` = 76.2), and every **belly** break strictly between the flat and the bottom-keel depth (`h_fuse − h_fuse_top` = 25.4), so the transition stays monotonic — a break at or past its keel merges / over-defines; one below its flat reverses the taper. These seven absolutes will **not** move if you resize the envelope, so re-check them whenever `h_fuse` / `h_fuse_top` changes.

---

That's the parametric backbone live. Every sketch dimension from here on is typed as `= "MAC"`, `= "c_root"`, `= "x_motor"`, and so on — never a hard number.

---

## 4. Side-view layout — Right Plane (`LAY_Side_Profile`)

The Right Plane is the plane of symmetry: longitudinal along **Z**, height along **Y**. This sketch fixes every fore-aft station and the vertical stack-up. Budget ~20 minutes.

**4.1 — Open and orient the sketch.**
1. Select the **Right Plane** in the tree ▸ **Sketch** (Sketch tab ▸ Sketch).
2. **Normal To** (`Ctrl+8`). Note the orientation: **+Z is forward (nose), +Y is up**. The nose (+Z) may appear on the left or right — press **Normal To** again to flip to the conventional nose-left side view if you prefer. It's cosmetic; what's binding is that forward features sit at +Z.
3. After you exit later, rename the sketch `LAY_Side_Profile` (F2) and file it in the `2_LAYOUT_SKETCHES` folder.

**4.2 — Lay the two master datums.** Everything dimensions off the origin (= wing-root LE).
1. **Centerline** (Sketch ▸ Line flyout ▸ Centerline) through the **Origin**, horizontal = the **waterline** (Z datum). Add **Coincident**-to-origin and **Horizontal** relations.
2. **Centerline** through the Origin, vertical = the **wing-LE station** (Z = 0). Coincident + **Vertical**.

**4.3 — Place the longitudinal station points.** With the **Point** tool, drop a point on the waterline for each station, then **Smart Dimension** it from the Origin and type the global with `=`. All longitudinal globals are **positive distances from the Wing LE**, so place the station point on the appropriate side of the origin (**+Z for forward, −Z for aft**), then Smart Dimension it using the positive global variable directly:
- **Forward features** (nose, motor) — place on the **+Z** side: `= "x_nose"`, `= "x_motor"`.
- **Aft features** (wing TE, CG, tail) — place on the **−Z** side: `= "c_root"`, `= "x_CG"`, `= "x_HT_c4"`, `= "x_VT_c4"`.
- Wing LE is the Origin (Z = 0), already placed.

These points seed the reference points in §7; here they're just construction points on the centerline.

**4.4 — Draw the fuselage side profile (spline-smoothed dodecagon cage).**
You are building a single **closed silhouette** that keeps the dodecagon's controllable skeleton — six axial stations, two flat cabin keels, a blunt nose face and an aft **boom-sleeve box** — but replaces the four **cornered polyline transitions** with **Style Splines**, so the lofted Outer Mold Line comes out **smooth instead of faceted**. The property that made the old all-straight cage safe (determinism) is preserved: every spline is **fully dimensioned** — its endpoints and its interior control point are pinned to the same `x_fuse_*` / `h_*` globals as before, and **Tangent** relations weld each spline to its neighbours — so no control point is ever free to wander on rebuild. Forward is $+Z$ (nose), aft is $-Z$ (tail), up is $+Y$, waterline is $Y = 0$.

The profile has **ten elements — six straight, four spline:**

| Element | Type | Spans | Why |
|---|---|---|---|
| Top keel | **straight** (Horizontal) | `TF → TR` | prismatic cabin roof; §8.5 pierce datum |
| Bottom keel | **straight** (Horizontal) | `BF → BR` | flat landing floor / flush mounting shelf |
| Nose flat | **straight** (Vertical) | `NT → NB` | blunt nose end-cap face |
| Sleeve top | **straight** (Horizontal) | `TT → SL_T` | boom-sleeve upper wall, 1 in aft |
| Sleeve end face | **straight** (Vertical) | `SL_T → SL_B` | new aft end of the fuselage; boom-sleeve mouth |
| Sleeve bottom | **straight** (Horizontal) | `SL_B → TB` | boom-sleeve lower wall, closes the silhouette |
| Top-nose shoulder | **Style Spline** | `NT → M1 → TF` | smooth nose-top blend |
| Top-tail shoulder | **Style Spline** | `TR → M2 → TT` | smooth tail-top blend |
| Bottom-tail shoulder | **Style Spline** | `BR → M3 → TB` | smooth tail-belly blend |
| Bottom-nose shoulder | **Style Spline** | `BF → M4 → NB` | smooth nose-belly blend |

> **Why the flats and keels stay straight (best-judgment call).** The two keels must be dead-flat — the bottom keel *is* the landing floor and flush mounting shelf (§6), and the top keel is the constant-section cabin roof both §8.5 sections pierce on-plane — so smoothing them would defeat their purpose. The nose and tail faces stay flat-vertical so the end-cap loft sections keep a finite height. Only the four **shoulders**, where the old cage cornered at `M1`–`M4`, become curves. This is the minimum change that erases the facets while recreating the current silhouette.

**Phase 1 — Lay the four straight segments and the four breakpoint points.** Know the target before you click:

| Vertex | Role | Column ($Z$) |
|---|---|---|
| `NT` / `NB` | nose flat, top / bottom | nose (`x_fuse_nose`) |
| `TF` / `BF` | top-/bottom-front cabin corner | firewall (`x_fuse_firewall`) |
| `TR` / `BR` | top-/bottom-rear cabin corner | cabin-rear (`x_fuse_bay_aft`) |
| `TT` / `TB` | sleeve root, top / bottom | tail (`x_fuse_tail`) |
| `SL_T` / `SL_B` | sleeve end, top / bottom | sleeve (`x_fuse_sleeve_top` / `x_fuse_sleeve_bottom`) |
| `M1` / `M4` | nose-top / nose-bottom shoulder | mid-nose |
| `M2` / `M3` | tail-top / tail-bottom shoulder | mid-tail |

1. **Line** tool: draw the **top keel** (`TF → TR`) and **bottom keel** (`BF → BR`) as two roughly horizontal segments, and the **nose flat** (`NT → NB`) as one roughly vertical segment. Then draw the **boom-sleeve box** as three joined segments running aft from the tail station: `TT → SL_T` (roughly horizontal, aft), `SL_T → SL_B` (roughly vertical, down), `SL_B → TB` (roughly horizontal, forward). Continuous clicking auto-adds a **Coincident** at `SL_T` and `SL_B`. Drop the nose lines forward ($+Z$), the tail / sleeve lines aft ($-Z$). **There is no tail flat** — the old vertical `TT → TB` end-cap line is gone; the silhouette now closes on the sleeve end face.
2. **Point** tool: drop the four **shoulder breakpoints** `M1` (nose-top), `M4` (nose-bottom), `M2` (tail-top), `M3` (tail-bottom) roughly between each flat and its keel. Phases 2–5 pull everything to its true station.

**Phase 2 — Lock the axial ($Z$) stations.** Group the entities into **six vertical columns** and dimension each once, straight to the Wing-LE datum ($Z = 0$). Every station is a **positive** distance; place the column on the correct side (**+Z** forward, **−Z** aft).
1. **Add the column relations.** The nose flat (`NT`–`NB`) and the sleeve end face (`SL_T`–`SL_B`) are already **Vertical** (drawn as vertical lines — confirm the relation). **`TT` and `TB` no longer share a line**, so their column is *not* inherited any more — add an explicit **Vertical** relation between `TT` and `TB` or they will drift apart on rebuild. Then add a **Vertical** relation between each remaining non-adjacent pair so it shares one $Z$: `TF`&`BF`, `TR`&`BR`, `M1`&`M4`, `M2`&`M3`.
2. **Smart Dimension** each column horizontally from the vertical datum and type the global expression:

| Column | Vertices | Dimension ($Z$ to datum) |
|---|---|---|
| Nose | `NT` / `NB` | `= "x_fuse_nose"` (+Z) |
| Mid-nose | `M1` / `M4` | `= "x_fuse_midnose"` (+Z) |
| Firewall | `TF` / `BF` | `= "x_fuse_firewall"` (+Z) |
| Cabin-rear | `TR` / `BR` | `= "x_fuse_bay_aft"` (−Z) |
| Mid-tail | `M2` / `M3` | `= "x_fuse_midtail"` (−Z) |
| Tail (sleeve root) | `TT` / `TB` | `= "x_fuse_tail"` (−Z) |
| Sleeve end | `SL_T` | `= "x_fuse_sleeve_top"` (−Z) |
| Sleeve end | `SL_B` | `= "x_fuse_sleeve_bottom"` (−Z) |

   > **This is what keeps the fuselage decoupled.** Every column lands on an `x_fuse_*` station (§3 / §7.3.6), offset off the **Front Plane** — never off a wing rib plane. Flex `rib_pitch` or `n_rib` and the side profile does not move. The firewall and cabin-rear columns land exactly on `PLN_Fuse_Firewall` and `PLN_Fuse_Bay_Aft`, so the §8.5 mid-body cross-sections pierce the keels on-plane.

**Phase 3 — Straddle the waterline with the constant-height cabin.** The cabin keels span firewall → cabin-rear at a constant height. Do **not** place a single blanket `h_fuse` dimension between them — that leaves the waterline floating and lets the section drift on rebuild. Pin each keel to the waterline instead:
1. Confirm the **Horizontal** relation on the **top keel** (`TF → TR`) and the **bottom keel** (`BF → BR`).
2. **Smart Dimension** the **top keel** to the **waterline** centerline → `= "h_fuse_top"`.
3. **Smart Dimension** the **bottom keel** to the **waterline** centerline → `= "h_fuse_bottom"`.

   The two always sum to `h_fuse`, so the section stays anchored to the waterline on every rebuild; bias the straddle by editing `h_fuse_top` alone. Because the firewall column sits at `x_fuse_firewall` (= `x_motor`), confirm it also clears the battery forward edge (`x_bat + bat_L/2`); the keel then runs aft unbroken to the cabin-rear column.

**Phase 4 — Set the flat nose face and the boom-sleeve box.** The nose face and the sleeve end face are **finite vertical faces**, not points — a zero-height apex would collapse the §8.5 end-cap loft.
1. Nose flat (`NT`–`NB`): **Smart Dimension** `NT` to the waterline → `= "h_nose_top"`, and `NB` to the waterline → `= "h_nose_bottom"`. These are **absolute-millimeter** globals (17.50 / 37.50 mm) — one exact height each, no fractional split.
2. Sleeve root (`TT`–`TB`) — **tail-cone termination.** The tail station does **not** inherit the cabin's top/belly bias; it pinches to the `tail_exit_D` = 0.75-in bounding closure. **Smart Dimension** `TT` to the waterline → `= "h_tail_top"`, and `TB` to the waterline → `= "h_tail_bottom"`. Both are **positive magnitudes above** the waterline. The station closes symmetric about the waterline at a $19.05$ mm bounding height, matching the $19.05$ mm planform width (§5.3.5).
3. Sleeve end (`SL_T`–`SL_B`) — **the new aft end of the fuselage.** Confirm the **Horizontal** relation on `TT → SL_T` and on `SL_B → TB`; the two sleeve walls must run dead-flat so the sleeve is a constant-section box the boom can slide into. **Smart Dimension** `SL_T` to the waterline → `= "h_sleeve_top"` (**above**, $+Y$), and `SL_B` to the waterline → `= "h_sleeve_bottom"` (**below**, $-Y$). Both globals are **positive magnitudes** — the global carries the distance, you pick the side as you place the dimension.
4. **Verify the sleeve is square and 1 in long.** The end face spans `h_sleeve_top` $+$ `h_sleeve_bottom` $= 19.05$ mm, the walls run `x_fuse_sleeve_top` $-$ `x_fuse_tail` $= 25.40$ mm ($1$ in), and the planform half-width (§5.3.5) matches at `w_fuse_sleeve_half` $= 9.5250$ — a clean $19.05 \times 19.05$ mm bore equal to `tail_exit_D`.

   The **nose** flat is set by the two absolute heights `h_nose_top` / `h_nose_bottom` (blunt but exact); the **sleeve root** instead collapses to the `tail_exit_D` cap, and the **sleeve end** is set by the two absolute magnitudes `h_sleeve_top` / `h_sleeve_bottom`. The nose flat lands on `PLN_Fuse_Nose` and the sleeve root on `PLN_Fuse_Tail` for the §8.5 end-caps; the sleeve end face sits 1 in aft of the last fuselage plane (see the flag in §8.5).

**Phase 5 — Dimension the four shoulder breakpoints.** Phase 2 already locked each break's $Z$ (its mid-nose / mid-tail column), so only the **height** ($Y$) degree of freedom remains. Pin each breakpoint **point** to the waterline with the **absolute-millimeter globals** from §3 — one clean dimension per point, no multiplication syntax:
1. `M1` (nose-top) → `= "h_nose_break_top"`.
2. `M2` (tail-top) → `= "h_tail_break_top"`.
3. `M3` (tail-bottom) → `= "h_tail_break_bottom"`.
4. `M4` (nose-bottom) → `= "h_nose_break_bottom"`.

   > **Envelope check (read before editing the absolutes).** Each break height is a direct millimeter global — you set the exact shoulder position. Keep every **top** break (`h_nose_break_top` / `h_tail_break_top`) strictly between the nose/tail flat height and the top-keel height `h_fuse_top`, and every **belly** break (`h_nose_break_bottom` / `h_tail_break_bottom`) strictly between the flat and the bottom-keel depth `h_fuse − h_fuse_top`. Because the shoulder is now a **curve** through this point, a break outside its keel-to-flat window bows the spline past the keel line (a local bulge or reversal) instead of merging a vertex — keep each strictly inside its window for a clean, monotonic shoulder.

**Phase 6 — Draw the four shoulder Style Splines and weld them tangent (this is the smoothing step).** With the eight endpoints and four breakpoints all pinned, connect each flat to its keel with a smooth curve:
1. **Sketch ▸ Spline flyout ▸ Style Spline.** For the **top-nose** shoulder, click `NT`, then `M1`, then `TF` (three control points), and press **`Esc`**. Repeat for **top-tail** (`TR → M2 → TT`), **bottom-tail** (`BR → M3 → TB`), and **bottom-nose** (`BF → M4 → NB`).
2. **Close the loop.** If an endpoint didn't snap, add a **Coincident** of each spline end onto its shared vertex (`NT`, `TF`, `TR`, `TT`, `TB`, `BR`, `BF`, `NB`). The chain now reads: nose flat → top-nose spline → top keel → top-tail spline → **sleeve top → sleeve end face → sleeve bottom** → bottom-tail spline → bottom keel → bottom-nose spline → back to the nose flat — one continuous closed silhouette.
3. **Weld tangent — this is what kills the corners.** At each of the eight spline-to-straight junctions, select the spline **and** the line it meets and add a **Tangent** relation:
   - at `NT` / `NB`: spline **Tangent** to the **nose flat** → the shoulders leave the nose face **vertically** (seamless rounded nose, no corner).
   - at `TT` / `TB`: spline **Tangent** to the **sleeve walls** (`TT → SL_T`, `SL_B → TB`) → the shoulders now leave the tail station **horizontally**, blending smoothly into the constant-section sleeve. **This is a shape change from the pre-sleeve build**, where the same relation welded each spline to the vertical tail flat and forced the shoulders to leave vertically. To keep the old shoulder shape, drop the Tangent at `TT` / `TB` and accept a crease there.
   - at `TF` / `TR` / `BF` / `BR`: spline **Tangent** to the adjacent **keel** → shoulders leave the keels **horizontally** (seamless keel blend).
   Each Tangent relation enforces $G^1$ continuity, converting the old sharp vertex into a smooth transition.
4. **Shoulder fullness = the breakpoint globals.** Each spline's interior control point rides `M1`–`M4`, already pinned (Phase 5) to its mid-station $Z$ and its absolute break height — so a shoulder's plumpness is still driven by **one global**: raise `h_nose_break_top` and the nose-top shoulder pushes outboard, lower it and the shoulder pulls in, exactly as the old polyline break did, but as a smooth curve.

   > **These splines do not wander.** Both endpoints are pinned vertices, the interior control point is pinned to an `M*` global, and the two Tangent relations fix the end directions — the Style Spline has **no free degree of freedom left**, so it rebuilds identically every time. The old "no splines" caution was aimed at *under-dimensioned* splines; a fully pinned, tangent-welded one is as deterministic as a straight line, and it is what removes the OML facets.

**Finalize the loop — wing-chord reference, construction toggle, acceptance.** *(§4.5 and §4.6 add the thrust line and compliance features to this same sketch; §4.7 does the final name / exit.)*
1. **Wing-chord reference.** Draw a line from the **LE (Origin)** aft `= "c_root"`, tilted up from the waterline by the incidence angle — angular **Smart Dimension** `= "i_wing"` (link the angle global directly; no `pi/180`). This seeds the wing seat and the §4.5 thrust line.
2. **Toggle to construction.** Window-select the **entire silhouette** — four lines and four splines — (and the wing-chord line) and tick **For construction**. Both keels, both flats, and the four shoulder splines feed the §8.5 cross-section pierces (and seed the 12-rail `LAY_Fuse_Guides_3D` harness), so the whole cage stays construction geometry — it never generates a solid edge.
3. **Loop acceptance.** The silhouette should read **Fully Defined** — every line, spline, and control point black. Drag-test anything blue: a fully defined sketch won't move.
   - Usual culprits if blue: a missing **Vertical** on a column pair, a missing **Horizontal** on a keel, a breakpoint missing its height dimension, or **a spline missing a Tangent relation at a junction** (the corner returns and the end tangent floats) — add the missing *relation* first, then any dimension.
   - Sweep check: bump `L_fuse` ±50 mm in **Tools ▸ Equations** and confirm the sleeve box, both tail shoulder splines, and the cabin-rear column track while the keels stay horizontal and waterline-locked and the shoulders stay tangent; nudge `h_fuse_top` and confirm the flats and shoulders re-balance about the waterline with no corners reappearing. Undo both.

**4.5 — Draw the thrust line (vertically decoupled from the wing root).** The motor/thrust line no longer rides on the wing-root waterline; its height is a master parameter, `y_motor_offset` (negative = motor dropped below the Origin, `0` = inline). This frees the thrust axis to move for down-thrust packaging without disturbing the wing datum.
1. With the **Point** tool, drop a **thrust-center point** at the motor station. Lock its longitudinal position with a **Coincident** relation to the vertical `x_motor` face (or **Smart Dimension** its Z distance from the Origin `= "x_motor"`). **Do not** pin it to the waterline.
2. Select **Smart Dimension**, click the **thrust-center point**, then click the horizontal **waterline** ($Y = 0$). Pull the preview into a clean vertical gap, click to place it, and type exactly `= "y_motor_offset"`. *(`y_motor_offset` is a **positive magnitude** — place the dimension on the side of the waterline you want the thrust line to sit; setting the global to zero runs it through the wing root.)*
3. From the thrust-center point, draw a **construction Line** for the thrust axis running aft. Angular **Smart Dimension** it to the horizontal `= "thrust_down"` (nose-down positive).
4. This line coincides with `PLN_PropDisk` (§2.6) at the prop station and becomes `AX_Thrust` / `AX_Prop` in §7. Because its anchor is *dimensioned* to the waterline by `y_motor_offset` — not pinned to it — the entire thrust axis rises or drops with that one global.
> **Decoupling check:** select the thrust-center point and confirm it carries **no** Coincident/Collinear relation to the waterline — only the `y_motor_offset` vertical dimension. If a stray waterline-coincident survives from the §4.3 station array, delete it first; otherwise the sketch over-defines (or silently ignores `y_motor_offset`) the moment you flex the motor height.

**4.6 — Place the Micro compliance features.**

**Bottom drain port.**
*Why:* `x_drain` is a longitudinal **positive distance** (Z) measured from the vertical Wing-LE datum (Z = 0). All longitudinal globals are positive distances from the Wing LE; because the drain sits behind the wing it lies on the **aft (−Z)** side of that datum.
1. Grab the **Point** tool and place a point directly on the **bottom cabin keel** (`BF → BR`, −Y) — the constant-height cabin segment, unaffected by any nose/tail transition edit — to give it a **Coincident** relation.
2. Select the **Smart Dimension** tool, click the drain point, then click the **vertical centerline** through the Origin (Z = 0).
3. Pull the dimension out horizontally, type `=`, and enter `"x_drain"`. This locks its longitudinal (Z) position while letting it slide vertically if the keel depth changes. Keep its path to the cabin floor unobstructed for gravity draining.

**Arming plug & RX on/off switch.**
*Why:* `x_arm_plug` and `x_switch` are longitudinal distances (Z) measured from the Wing-LE datum (Z = 0) on the **aft (−Z)** side. Drawing them on the **Right Plane** (X = 0) automatically anchors them on the aircraft's physical centerline; place them on the **upper** fuselage outline so they stay external and accessible.
1. Drop two separate points directly onto the **top cabin keel** (`TF → TR`, +Y upper fuselage outline) — the stable constant-height segment, unaffected by any transition edit — each with a **Coincident** relation.
2. Select **Smart Dimension**, click the first point, click the **vertical centerline**, pull horizontally, and type `= "x_arm_plug"`.
3. Repeat the dimensioning for the second point, linking it to `= "x_switch"`.

**9-in propeller keep-out zone.**
*Why:* SAE rules mandate that the arming plug and power switch sit at least **9 in (228.6 mm)** behind the plane of the propeller. The **authoritative** check is driven by the equations `arm_clear = ("x_motor" + "x_arm_plug") - "keepout"` and `sw_clear = ("x_switch" + "x_motor") - "keepout"` (`keepout = 228.6`). Both must be **≥ 0 mm** in the Equations dialog — the plug/switch are aft and the motor is forward, so their separation is the **sum** of two positive distances.
1. Use the **Line** tool with **For construction** enabled to draw a vertical construction line passing through the fuselage behind the motor.
2. Use **Smart Dimension** to measure the horizontal distance between this line and your **motor point** (or the `PLN_PropDisk` plane).
3. Lock this distance to exactly `= "keepout"` (228.6 mm).
4. Conduct a visual check: verify that your `x_arm_plug` and `x_switch` points sit further toward the tail (**aft / −Z**) than this vertical keep-out boundary line.

**Ballast reference point.**
*Why:* `x_ballast` is a longitudinal **positive distance** (Z) measured from the Wing-LE datum (Z = 0). Trim ballast is used to pull the empty-weight CG forward, so it sits on the **forward (+Z)** side of that datum. Drawing it on the **Right Plane** (X = 0) and pinning it to the **waterline** (Y = 0) keeps it on the aircraft's physical centerline, so it adds no unwanted roll or yaw offset. This is the sketch point §7.1 promotes to the reference Point `PT_Ballast`.
1. Grab the **Point** tool and drop a single point directly on the **waterline centerline** (the horizontal Z datum through the Origin, Y = 0), roughly forward (**+Z**) of the Origin — placing it on the line gives it a **Coincident** relation, locking Y = 0 so it rides the physical centerline.
2. Select the **Smart Dimension** tool, click the ballast point, then click the **vertical centerline** through the Origin (Z = 0). Pull the dimension out horizontally, type `=`, and enter `"x_ballast"`. This locks its longitudinal (Z) position on the **forward (+Z)** side while the Coincident relation holds it on the waterline.
3. Conduct a visual check: verify the point sits **forward of the firewall column** (`x_fuse_firewall`) or otherwise clear of the cabin volume, so it can never be mistaken for internal payload trim.

> **Rules compliance (ballast placement).** The 2026 SAE Micro rules **prohibit ballast inside the payload container**. The container is **not modeled in this skeleton**, so this is an **off-model check**: whatever container you install, `PT_Ballast` must lie completely outside it. With the starter values `x_ballast` = 150 mm **forward** of the Wing LE puts the ballast station ahead of the firewall column (`x_fuse_firewall` = 152.40 mm forward) — well clear of any cabin-mounted container. Re-verify the physical clearance on the assembly whenever `x_ballast` moves.

**Battery-bay profile.**
*Why:* The battery is one of the heaviest single components on the airframe. By tracking its location with `x_bat` on the **forward (+Z)** side of the Wing LE, you can use its mass strategically to counter-balance the heavy tail section and pull the empty-weight CG forward without relying on dead-weight ballast.
1. Drop a rectangle into the **forward** section of the fuselage outline using the **Rectangle** tool, and check **For construction**.
2. Use **Smart Dimension** to set the horizontal length to `= "bat_L"` and the vertical height to `= "bat_H"`.
3. Dimension the horizontal distance from the center or edge of this rectangle to the **vertical datum line (Wing LE, Z = 0)**, pull horizontally, and lock it to `= "x_bat"` on the **forward (+Z)** side.

> **Two packs share the cabin.** This revision houses **both** the propulsion 4S LiPo (`bat_L` × `bat_W` × `bat_H` = 78.74 × 34.29 × 34.29) and the avionics pack (`avi_bat_L` × `avi_bat_W` × `avi_bat_H` = 60.96 × 30.48 × 22.86) inside the constant-section cabin — set side-by-side anywhere in the `cabin_len` = 254 mm run (§3). Both centroids land inside firewall→cabin-rear (`x_bat` = 120 sits within the cabin), so the section stays the 101.6 mm square envelope with no local bulge. If you sketch the avionics rectangle too, drop a second **For construction** box dimensioned `= "avi_bat_L"` × `= "avi_bat_H"` and seat it against whichever cabin wall you prefer.

> If the side profile gets crowded, split the hardpoints (drain, plug, switch, bays) into a second sketch `LAY_Hardpoints` on the Right Plane — one purpose per sketch keeps rebuilds clean.

**4.7 — Fully define, name, exit.**
1. Add relations until the sketch reads **Fully Defined** (status bar, bottom-right; all entities black). Every entity should tie to the two datums or to a global.
2. Exit the sketch; rename `LAY_Side_Profile`; drop it in `2_LAYOUT_SKETCHES`.

**4.8 — Verify.**
- Bump `L_fuse` (±50 mm) and confirm the profile and stations track; undo.
- Confirm `arm_clear`, `sw_clear` ≥ 0 in the Equations dialog.
- Confirm the sketch is fully defined and construction-only (except any keel edges you're intentionally sharing for the OML loft).

---

## 5. Fuselage planform & mass datums — Top Plane (`LAY_Wing_Plan`)

> **⭐ The wing and the horizontal stabilizer are *not* in this sketch.** Both are lifting panels that carry dihedral, so each lives entirely on its own tilted datum plane: the wing in **`LAY_Wing_Incidence`** on `PLN_Dihedral` (§7.2), the stabilizer in **`LAY_HTail_Incidence`** on `PLN_Dihedral_HT` (§5.8.1). Each of those sketches carries its own outline, spars, stations and hinge lines together, so they cannot drift apart. `LAY_Wing_Plan` keeps only what is genuinely flat and on the centreplane: the fuselage footprint, the vertical-tail reference, and the CG band.

On the **Top Plane**, **span runs along $X$, chord/length runs along $Z$**. You draw the port half (the $+X$ side) of the fuselage outline, then mirror them across the center axis.

**5.1 — Open and orient the canvas.**
1. Select the **Top Plane** in the FeatureManager tree ▸ **Sketch** ▸ **Normal To** (`Ctrl+8`).
2. Note your orientation: $+X$ is port span, $+Z$ is forward (toward the nose), and $-Z$ is aft (toward the tail).

**5.2 — Establish the master centerline.**
1. **Fuselage centerline.** Select the **Centerline** tool. Draw a line straight through the sketch **Origin** along the **$Z$-axis**. Add a **Coincident** relation to the Origin and a **Vertical** relation (or **Horizontal**, depending on screen rotation) to lock it as your $X = 0$ symmetry line.
2. **Wing root chord line — not here.** The wing root chord is the first entity of `LAY_Wing_Incidence` (§7.2 Phase B, Step 1), drawn from the Origin on `PLN_Dihedral`.

> **Where the wing went.** Every wing entity that used to be sketched on this plane — root chord, swept leading edge, tip chord, trailing edge, both spars, the joiner, the rib array, the MAC line, the four control-surface stations and both hinge lines — is now in `LAY_Wing_Incidence`. The flat versions are **gone, not duplicated**: re-drawing them here would over-constrain the model against the tilted originals and give you two wings that disagree the moment `dihedral` changes.


**5.3 — Wing half-planform → moved to `LAY_Wing_Incidence` (§7.2 Phase B).** The port wing panel, its swept leading edge, the tip station and the closing trailing edge are now drawn on `PLN_Dihedral` so the outline is a true 3-D shape rather than a flat projection. Nothing wing-related is sketched on the Top Plane. Continue at §5.3.5 for the fuselage cage.

**5.3.5 — Draft the fuselage planform "trapping cage" (native 12-sided dodecagon).** To give §8.5 a stable framework to pierce against, lay out the horizontal envelope of the fuselage independently of the wing — a **12-sided dodecagon** that mirrors the side profile's $Z$ columns exactly. You sketch the **port (+X) half** as an open chain that **runs from the centerline at the nose to the centerline at the tail** — drawing the two half-width flat faces explicitly — then mirror it across the centerline so those halves weld into the full nose and tail faces. **Every line in this subsection must be checked "For construction".**

> **Double-dodecagon symmetry.** The side profile (§4.4) traps *height* at six $Z$ columns; this planform traps *width* at the **same six columns**. Because both are driven by the `x_fuse_*` stations, every §8.5 cross-section plane lands where **both** cages carry a vertex — so the loft captures the flat nose/tail faces and the smoothed shoulders in both views at once.

**Phase 1 — Sketch the continuous port chain (centerline to centerline).** The port half is an **open chain of seven segments** — the two half-width flat faces plus the five profile edges — running from the centerline at the nose to the centerline at the tail. Drawing both flat-face halves explicitly is what lets the mirror seal a gap-free **12-sided** closed loop. Know the six profile vertices before you click:

| Vertex | Role | Column ($Z$) | Half-width ($X$) |
|---|---|---|---|
| `NL` | nose flat, outboard | nose (`x_fuse_nose`, +Z) | `w_fuse / 4` |
| `P1` | nose-to-cabin break | mid-nose (+Z) | `w_fuse_break` |
| `CL` | front cabin corner | firewall (`x_fuse_firewall`, +Z) | `w_fuse / 2` |
| `TL` | rear cabin corner | cabin-rear (`x_fuse_bay_aft`, −Z) | `w_fuse / 2` |
| `P2` | tail-to-end break | mid-tail (−Z) | `w_fuse_break` |
| `EL` | sleeve root, outboard | tail (`x_fuse_tail`, −Z) | `tail_exit_D / 2` |
| `SL_P` | sleeve end, outboard | sleeve (`x_fuse_sleeve_plan`, −Z) | `w_fuse_sleeve_half` |

Two more vertices sit **on the centerline** ($X = 0$) as the mirror seam: **`NC`** at the nose station and **`SL_C`** at the **sleeve-end** station. Neither takes a width dimension — each is **Coincident** to the centerline and inherits its $Z$ from the flat-face relation in step 3.

1. Select the **Line** tool and tick **For construction** in the PropertyManager.
2. Sketch the chain in one continuous run, centerline to centerline: start on the fuselage centerline at the nose (**`NC`**), draw a line **straight outboard ($+X$) to `NL`**, walk the profile **`NL → P1 → CL → TL → P2 → EL`**, then continue **aft ($-Z$) from `EL` to `SL_P`** — the boom-sleeve side wall — and finally draw a line from `SL_P` **straight inboard back to the centerline at the sleeve end (`SL_C`)**. Continuous clicking auto-adds a **Coincident** at every junction; land `NC` and `SL_C` on the centerline so the yellow coincident glyph shows.
3. **Square the two flat faces, and the sleeve wall.** Select the nose flat-face line (`NC → NL`) and add a **Vertical** relation — it runs perpendicular to the horizontal $Z$ centerline; repeat for the sleeve end-face line (`SL_P → SL_C`). This turns each flat face into a pure lateral line and pins `NC` / `SL_C` to the same $Z$ column as `NL` / `SL_P`. Then select the sleeve side wall (`EL → SL_P`) and add a **Horizontal** relation so it runs parallel to the centerline — that is what makes the sleeve a constant-width box rather than a short taper.
4. Don't chase exact positions yet — drop `NL`/`P1`/`CL` forward (+Z) and `TL`/`P2`/`EL`/`SL_P` aft (−Z), all on the **+X (port)** side of the centerline. Phases 2–3 pull them to their true stations.

**Phase 2 — Align the longitudinal ($Z$) stations.** Bind each vertex to the **same $Z$ column** the side profile uses, so the two cages stay locked together. On the Top Plane the longitudinal axis runs horizontally, so each station is a horizontal **Smart Dimension** back to the vertical Wing-LE datum ($Z = 0$); type the *same* global (or mid-station expression) that drives the matching side-profile column:

| Vertex | Dimension ($Z$ to datum) |
|---|---|
| `NL` | `= "x_fuse_nose"` (+Z) |
| `P1` | `= "x_fuse_midnose"` (+Z) |
| `CL` | `= "x_fuse_firewall"` (+Z) |
| `TL` | `= "x_fuse_bay_aft"` (−Z) |
| `P2` | `= "x_fuse_midtail"` (−Z) |
| `EL` | `= "x_fuse_tail"` (−Z) |
| `SL_P` | `= "x_fuse_sleeve_plan"` (−Z) |

   > **The same columns as §4.4.** These are the identical expressions that station the side-profile columns (nose, mid-nose, firewall, cabin-rear, mid-tail, tail). Driving both cages from the same `x_fuse_*` globals is what guarantees each §8.5 cross-section plane cuts *both* at a real vertex. *(If you would rather hold a port vertex on its column with a relation than a dimension, a **Vertical** relation between the port vertex and its post-mirror twin keeps them on one $Z$ — but the dimension above is what actually binds the column.)*

**Phase 3 — Dimension the widths.** Smart Dimension each vertex laterally back to the fuselage centerline ($X = 0$) with the parametric width equations:
1. `NL` (nose flat) → `= "w_fuse_nose_half"`.
   > **`EL` (tail cap) is the exception — `= "w_fuse_tail_half"`, not the nose half-width.** The tail cone terminates at the `tail_exit_D` = 0.75-in bounding, so its half-width shrinks to `tail_exit_D / 2` = 9.525 mm (matching the §4.4 tail-flat half-height). Dimension `EL` to the centerline `= "w_fuse_tail_half"`; leave `NL` at `= "w_fuse_nose_half"`. **`SL_P` (sleeve end) takes `= "w_fuse_sleeve_half"`** — the same 9.5250 mm, held as its own absolute so the sleeve reads as a constant-width box; with the `EL → SL_P` **Horizontal** relation from Phase 1 step 3 the two agree by construction, and this dimension is what proves it.
2. `CL` (cabin max, fwd) → `= "w_fuse_cabin_fwd_half"`; `TL` (cabin max, aft) → `= "w_fuse_cabin_aft_half"`.
3. `P1` and `P2` (transition breaks): select each vertex, **Smart Dimension** it laterally to the fuselage centerline, and type exactly `= "w_fuse_break"` (41.25 mm) — one absolute half-width, no fractional split.

   > **Absolute width control (`w_fuse_break`).** The transition half-width is now a **direct millimeter global**, not a fraction of `w_fuse` — so you lock an exact internal clearance envelope (structural formers, a battery pack, cargo rails) straight from the global equations dashboard, no trial-and-error scaling. **Envelope check:** keep `w_fuse_break` strictly between the nose/tail flat half-width (`NL` = `w_fuse / 4`) and the cabin half-width (`w_fuse / 2`) for a monotonic taper — a value ≥ `w_fuse / 2` bulges the shoulder *outboard* of the cabin and reverses the taper; a value ≤ `w_fuse / 4` collapses the shoulder into the flat. Because it no longer tracks `w_fuse`, re-check `w_fuse_break` whenever you resize `w_fuse`.

**Phase 4 — Mirror for total symmetry.** Close the dodecagon by mirroring the port chain across the centerline:
1. Click **Mirror Entities** on the Sketch tab.
2. In **Entities to Mirror**, box-select the **eight port fuselage segments** — the two flat-face halves (`NC → NL` and `SL_P → SL_C`), the five profile edges (`NL → P1 → CL → TL → P2 → EL`), and the sleeve side wall (`EL → SL_P`). Do **not** select the wing panel, the centerlines, or the empennage.
3. Click inside **Mirror About**, select the main longitudinal **$Z$ centerline** ($X = 0$), confirm **Copy** is ticked, and click the **Green Checkmark**. Each flat-face half welds to its mirror at the seam point — `NC → NL` joins `NC → NR` into the full **nose face**, and `SL_P → SL_C` joins `SL_R → SL_C` into the full **sleeve end face** — closing the footprint with no gap. The mirrored sleeve reads as a constant-width box $2 \times$ `w_fuse_sleeve_half` $= 19.05$ mm across, running 1 in aft of the tail station.
4. Confirm the whole fuselage footprint reads **Fully Defined** — every segment **solid black**. A blue vertex means a missing $Z$ or $X$ dimension (Phases 2–3), or a flat face missing its **Vertical** relation; add the missing constraint, not a stray one.

**5.6 — Map the stability CG band.** The MAC reference line moved to `LAY_Wing_Incidence` (§7.2 Phase B, Step 6) with the rest of the wing; the CG band stays here, because these three points sit on the fuselage centerline at $X = 0$ and are mass datums rather than wing-panel geometry.
3. **Establish the CG centerline band.** Drop three independent points directly on your main central fuselage centerline ($X = 0$). **Smart Dimension** their distance from the **Origin** along $Z$ to set your static limits:
   - Target CG point → `= "x_CG"`
   - Forward CG margin limit → `= "x_CG_fwd"`
   - Aft CG margin limit → `= "x_CG_aft"`

**5.8 — Map out the vertical-tail reference.** The **horizontal** stabilizer is no longer sketched here — outline and spar together live in `LAY_HTail_Incidence` (§5.8.1). Only the VT reference, whose span runs vertically and therefore has no dihedral plane of its own, stays on the Top Plane.
1. **Vertical tail (VT).** Select the **Centerline** tool. Draw a line directly on the main fuselage centerline near the tail apex. Ensure it is **Collinear**, dimension its length to `= "c_root_VT"`, and dimension its forward endpoint back to the master **Origin** to `= "x_VT_LE_root"`.

**5.8.1 — Empennage datum chain (`PLN_Dihedral_HT` → `PLN_Incidence_HT`) → the complete stabilizer sketch (`LAY_HTail_Incidence`).** The horizontal tail gets the same two-plane treatment as the wing, but hung off `AX_Long_Emp` rather than `AX_Long` — the tail rides the boom, `y_emp_axis` = 25 mm above the Top Plane. This replaces the old flat HT outline in `LAY_Wing_Plan` and the retired `LAY_HTspar_Dihedral`.

* **Phase A — create `PLN_Dihedral_HT` (the roll plane).**
  1. Click **Insert ▸ Reference Geometry ▸ Plane**. **First Reference —** `PLN_Emp_Datum` (§2.3.1, the horizontal plane at `y_emp_axis`); **Second Reference —** **`AX_Long_Emp`**, the fore-aft pivot the empennage uses. Choose **At Angle** and type `= "dihedral_HT"`.
  2. **Flip** so the plane rises toward the port (**+X**) HT tip. Green-check; **F2** → `PLN_Dihedral_HT`. Drop it into `3C_TAIL_PLANES`.
  > At `dihedral_HT` = 0 this plane is coincident with `PLN_Emp_Datum` — a flat stabilizer sitting 25 mm up. Every point on it obeys $Y = $ `y_emp_axis` $+\,X\tan(dihedral\_HT)$, so the tail inherits any future HT dihedral with no hard $Y$ number, and it translates bodily with `y_emp_axis`.

* **Phase A2 — the pitch pivot and `PLN_Incidence_HT` (the incidence plane).** The stabilizer really does carry incidence — `i_HT` = −2.0°, i.e. the chord line sits **2° below** `AX_Long_Emp`, nose-down — so this second plane is load-bearing here, not just provision.
  1. **Root-LE station plane.** **Insert ▸ Reference Geometry ▸ Plane**: **First Reference** = the **Front Plane**, **Offset Distance** `= "x_HT_LE_root"`, flipped **aft** ($-Z$). Green-check; **F2** → `PLN_HT_LE`. Drop it into `3C_TAIL_PLANES`.
  2. **Pitch pivot.** **Insert ▸ Reference Geometry ▸ Axis**, **Two Planes**: select `PLN_Dihedral_HT` and `PLN_HT_LE`. Green-check; **F2** → `AX_Pitch_HT`. File it in `4_AXES`.
     > **Why the pivot must sit at the HT root LE.** Incidence is a pitch rotation, so whatever station the hinge line crosses stays put and everything else swings. Pivot at the Front Plane instead and the root LE would drop `x_HT_LE_root` $\times \tan$ `i_HT` $\approx 29.6$ mm off the boom axis — a 30 mm error masquerading as a 2° one.
  3. **Incidence plane.** **Insert ▸ Reference Geometry ▸ Plane**. **First Reference —** `PLN_Dihedral_HT`; **Second Reference —** `AX_Pitch_HT`. Choose **At Angle** and type `= "i_HT"` — a **positive 2.0**, per the positive-magnitude rule (§3).
     **Now set the direction with the Flip toggle, not with a sign.** Watch the preview and tick **Flip Offset** until, running **aft** ($-Z$) from the pivot, the plane **climbs away from `AX_Long_Emp`**. That is the nose-**down** stabilizer: the chord line sits 2° below the boom axis in attitude, leading edge low, trailing edge high. Green-check; **F2** → `PLN_Incidence_HT`. Drop it into `3C_TAIL_PLANES`.
  > **Check it before you sketch on it.** **Measure** the angle between `PLN_Incidence_HT` and `PLN_Emp_Datum` — it must read **2.00°**. Then **Measure** the $Y$ of a point on the plane one root chord aft of the pivot: it must be **higher** than the pivot by `c_root_HT` $\times \sin$ `i_HT` $\approx 6.2$ mm. If it is lower, the Flip is backwards — you have built a nose-**up** stabilizer, a 4° error in tail setting angle and the difference between trimmed and untrimmable. **Fix it with the Flip toggle; do not make `i_HT` negative.**

* **Phase B — draw the complete stabilizer (`LAY_HTail_Incidence`).** Same two-projection rule as the wing (§7.2 Phase B): **spanwise** distances use the `_proj` family, **chordwise** station distances use the `_inc` family, and **line lengths are drawn true**.
  1. **Insert ▸ Sketch** on **`PLN_Incidence_HT`**; **`Ctrl + 8`**; **F2** → `LAY_HTail_Incidence`.
  2. **Root LE.** Select the **Point** tool and drop a point; add a **Coincident** to `AX_Pitch_HT` and a second **Coincident** to the **Right Plane**. That pins it at $X = 0$ on the pitch hinge — the HT root leading edge, exactly `x_HT_LE_root` aft of the Front Plane and exactly on `AX_Long_Emp`. **No chordwise dimension is needed here**; the pivot axis supplies it.
     > At non-zero `dihedral_HT` the Right Plane is no longer perpendicular to this sketch — swap that second Coincident for an in-plane spanwise dimension of `0` from `AX_Pitch_HT`.
  3. **Root chord.** Solid **Line** from the root LE point running **aft**; **Smart Dimension** its length `= "c_root_HT"` (a true in-plane length). Add a **Perpendicular** relation to `AX_Pitch_HT` so the chord runs square to the span.
  4. **Tip station.** **Point** tool, out on the port side; **Smart Dimension** its in-plane spanwise distance **from the root LE** → `= "b_semi_HT_proj"`.
  5. **Leading edge.** Solid **Line** from the root LE to the tip station point. With `sweep_HT` = 0 add a **Perpendicular** relation to the root chord to lock it square. (For non-zero `sweep_HT`, drop that relation and dimension the tip LE in-plane chordwise from the root LE instead, exactly as the wing does with `x_LE_tip_inc`.)
  6. **Tip chord.** Solid **Line** from the tip LE straight aft; **Parallel** to the root chord; **Smart Dimension** `= "c_tip_HT"`.
  7. **Trailing edge.** Solid **Line** closing tip TE back to root TE.
  8. **HT main spar (construction).** **Line** tool, tick **For construction**, root chord to tip chord. **Root end —** **Coincident** to the root chord line, then **Smart Dimension** its in-plane chordwise distance **from the root LE** `= "x_spar_root_HT_inc"`. **Tip end —** in-plane spanwise from the root LE `= "b_semi_HT_proj"`, and in-plane chordwise **from the tip LE** `= "x_spar_tip_HT_inc"`.
     > **Why `spar_main_pct` (no dedicated tail-spar global).** The stabilizer spar is co-located at the **same %-chord fraction** as the wing main spar, so `x_spar_root_HT` / `x_spar_tip_HT` re-use an existing fraction rather than introducing a second one. The elevator hinge line is a separate downstream feature at `c_elev_pct`.
  9. **Mirror the outline only.** **Mirror Entities** ▸ select the **LE, tip chord and TE** ▸ **Mirror About** = the **root chord line** ▸ **Copy** ticked ▸ green-check. Leave the **spar port-only** — like `AX_MainSpar`, the axis rides the single port line.
  10. Confirm `LAY_HTail_Incidence` reads **fully black**; **Exit** and drag it into `2_LAYOUT_SKETCHES`.

* **Phase C — promote to `AX_HTspar_3D`.**
  1. **Insert ▸ Reference Geometry ▸ Axis**, **One Line/Edge/Axis**, click the HT spar construction line inside `LAY_HTail_Incidence`, green-check, **F2** → `AX_HTspar_3D`. File it in `4_AXES` (§7.2).
  > **Success state:** one sketch holds the whole stabilizer, sitting `y_emp_axis` above the wing datum and pitched `i_HT` nose-down, with a single named axis spanning the HT semi-span — the **Normal to Curve** reference §7.3.7 slices against. Changing `y_emp_axis`, `dihedral_HT` or `i_HT` re-solves the outline and the spar together, because they share a sketch and a datum chain.


**5.8.3 — Prep the vertical-tail framework.** The VT root chord from §5.8 step 1 (`= "c_root_VT"`, on the centerline) is the *planform* footprint of the fin. Its span runs **vertically** ($+Y$), so its height master (`= "b_VT"`) and its 3-D fin-spar axis are built next door on the front view — see **§6.8.1**. No further action on the Top Plane.

**5.9 — Harden the sketch.** There is nothing left to mirror here — the fuselage dodecagon was already mirrored and closed in §5.3.5 Phase 4, and the wing and stabilizer are mirrored inside their own sketches (§7.2 Phase B Step 9, §5.8.1 Phase B Step 8).

**5.10 — Rename, file, and flex-test the system.**
1. Slow-double-click the sketch in your FeatureManager tree and rename it exactly `LAY_Wing_Plan`. Drag it into `2_LAYOUT_SKETCHES`, alongside `LAY_Wing_Incidence` and `LAY_HTail_Incidence`.
2. Open your external variables file (`skeleton_equations_micro.txt`) in Notepad to perform your mandatory validation audit.
3. Alter your primary design drivers by $+10\%$: set `"b" = 1210` and `"c_tip" = 198`, save the text file, and hit **Forced Rebuild** (**`Ctrl + Q`**) inside SolidWorks.
4. **Audit the screen:** in `LAY_Wing_Incidence` the panel must scale smoothly, the spars must re-angle to hold their exact chordwise percentages, and the rib-point pattern must re-space across the longer span; in `LAY_HTail_Incidence` the stabilizer must resize with the tail-volume chain; and here the fuselage cage must expand laterally while its nose and tail flat faces stay anchored firmly to the centerline.
5. **Test the re-count engine:** change `"n_rib" = 9`, save, and hit **`Ctrl + Q`**. Verify the rib array adds two new points with zero errors.
6. Revert all variables to your baseline competition metrics, save the text file, run a final **`Ctrl + Q`**, and save your model.

## 6. Front-view layout — Front Plane (`LAY_Front_View`)

The view you asked to live on the Front Plane: **span along X, height along Y**, looking down the longitudinal (Z) axis. This is the sketch where the **vertical stack-up closes** — ground → wheels → axle → thrust line → fuselage → wing root. Budget ~20 minutes.

**6.1 — Open and orient.** Select the **Front Plane** ▸ **Sketch** ▸ **Normal To** (`Ctrl+8`). +X is port span (to the right of screen), +Y is up. Per §2.2 this is the conventional nose-on front view (the view is left-right symmetric, so the side labels are only cosmetic). Rename `LAY_Front_View` on exit; file in `2_LAYOUT_SKETCHES`.

**6.2 — Master datums.**
1. **Centerline** through the **Origin**, vertical (along Y) = the **symmetry / mirror line** (collinear with the Right Plane).
2. **Centerline** through the Origin, horizontal (along X) = the **waterline** reference (the wing-root height).

**6.3 — Dihedral line.**
This section establishes the V-shape profile of the wings from the front view, driving the rib-plane tilt and wing-joiner angles downstream.
* **Phase 1: Draw the Angled Reference Line**
  1. Go to the **Sketch** command manager tab at the top of the screen.
  2. Click the small arrow next to the **Line** tool icon to open its flyout menu, and select **Centerline** (to ensure it remains construction geometry).
  3. Hover your cursor over the sketch **Origin (0,0,0)** until the yellow **Coincident** relation glyph appears next to your cursor.
  4. **Click once** on the Origin to anchor the start of your line.
  5. Move your cursor up and to the right (into the +X, +Y quadrant of your screen) at a shallow upward slope.
  6. **Click a second time** out in space to drop the endpoint of the line.
  7. Press the **Esc** key on your keyboard to exit the line tool.
* **Phase 2: Lock the Horizontal Span ($X = \text{b\_semi}$)**
  1. Click the **Smart Dimension** tool on the Sketch tab.
  2. Click directly on the **outer endpoint** of the angled centerline you just drew.
  3. Click directly on your **vertical centerline** (the Y-axis line).
  4. Move your mouse straight down toward the bottom of the graphics area until the dimension preview flattens into a horizontal linear gap measurement.
  5. **Click once** to place the text box.
  6. In the *Modify* pop-up box, type exactly `= "b_semi"` (include the equals sign and the quotes), and press **Enter**.
* **Phase 3: Lock the Dihedral Angle**
  1. With **Smart Dimension** still active, click directly on your **angled centerline**.
  2. Click directly on your **horizontal centerline** (the X-axis waterline).
  3. Move your cursor into the wedge space between the two lines until the angular arc dimension preview appears.
  4. **Click once** to place the text box.
  5. In the *Modify* box, type exactly `= "dihedral"` and press **Enter**.
  6. Verify that the sketch entity turns completely **black** and the status bar reads **Fully Defined**.
* **Phase 4: Mirror for the Opposite Wing Panel**
  1. Click the **Mirror Entities** tool on the Sketch tab.
  2. In the PropertyManager panel on the left side of your screen:
     * Click inside the **Entities to mirror** box, then click your **angled centerline** in the graphics window.
     * Click inside the **Mirror about** box, then click your **vertical centerline** (the Y-axis line) in the graphics window.
  3. Ensure the **Copy** checkbox is checked.
  4. Click the **Green Checkmark** at the top of the PropertyManager.
> **Tip:** Because Phase 3 ties `= "dihedral"` to an **angular** dimension, no `*pi/180` conversion is used — angles bind directly to angular dimensions (§3.6). The resulting tip rise is $b_{semi}\tan(\text{dihedral})$, which is what drives the rib-plane tilt and the wing-joiner angle in §7.

**6.4 — Cabin cross-section — bulbous flat-bottom tangent arch (Style Spline).**
The cabin cross-section is a **bulbous, pebble-like tangent arch on a flat baseline**: a flat horizontal **floor keel**, closed by a single **Style Spline (B-spline)** that leaves each floor endpoint on a **perfectly flat 0° horizontal tangent** — no sharp corner, no upright wall — then **flares outward past the floor width** to a lateral maximum before pulling smoothly back inward to a **flat horizontal apex**. Where the previous boxy D-section met the floor at a 90° wall (a hard chine) and carried its max width at the floor corner, this profile has a seamless $G^1$ floor blend and carries its **max width out at the flare**, giving a rounded, hydrodynamically clean OML that still wraps inward over the payload. The whole shape is driven by an outer **control-polygon cage** tied to globals, so it scales without flipping or dangling geometry. This is the max-section loft profile in §8.5; the nose/tail sections are the same construction scaled down.

Anchors (symmetric about $X = 0$): floor at $Y = -(\,$`h_fuse` $-$ `h_fuse_top`$\,)$, apex at $Y = +$`h_fuse_top`, **max flare** half-width $= $`w_fuse`$/2$. Three shaping globals drive the cage:
- `w_floor_pct` (= 0.92) — floor-contact half-width as a fraction of the `w_fuse`/2 flare; **< 1**, so the floor is *narrower* than the flare (the source of the bulge).
- `crown_sh_pct` (= 0.65) — flare-vertex **height above the floor** as a fraction of `h_fuse` (how high the widest point rides — the bulge lift).
- `crown_apex_pct` (= 0.30) — flat-apex control half-width as a fraction of `w_fuse`/2 (flat-top width).

* **Phase 1: Establish the framework.**
  1. On the **Front Plane**, open a sketch and press **`Ctrl + 8`**. Draw a horizontal **floor line** below the Origin and a **vertical centerline** on $X = 0$.
  2. Add **Horizontal** to the floor and **Coincident** of its midpoint to the centerline.
  3. **Smart Dimension** the floor line to the **waterline** ($Y = 0$) → `= "h_fuse_bottom"`. **Do not dimension the floor width directly** — its endpoints are pinned in Phase 4 relative to the flare, so its width floats with the cage.

* **Phase 2: Generate the Style Spline.**
  1. **Tools ▸ Sketch Entities ▸ Style Spline** (**B-Spline** mode).
  2. Click the **left floor endpoint**, then **two intermediate control points** sweeping **outward** (the flare) and **upward** (the crown), then the **apex** on the centerline, then mirror the sequence down the right side to the **right floor endpoint**. Press **`Esc`**. This lays a **7-vertex control polygon**: floor-L, flare-L, crown-L, apex, crown-R, flare-R, floor-R.
  3. Select the spline ▸ **For construction**.

* **Phase 3: Constrain the boundary conditions (the no-crease guarantees).**
  1. **Flat 0° floor takeoff.** At each floor endpoint, select the spline **and** the floor line and add a **Tangent** relation — equivalently, select the **first control-polygon segment** (floor-endpoint → flare vertex) and add a **Horizontal**/**Collinear** relation to the floor. Either forces the spline to leave the baseline on a perfect **0° horizontal tangent** — a seamless blend, no upright wall, no crease.
  2. **Flat apex.** Select the **top control segment** spanning the apex (crown-L → apex → crown-R) and add a **Horizontal** relation → a flat peak.
  3. **Symmetry.** Add **Symmetric** (each flare pair, crown pair, floor pair) about the centerline, and **Coincident** the apex vertex to the centerline.

* **Phase 4: Parametric scaling (link the cage to globals).**
  1. **Apex height:** dimension the apex vertex to the waterline → `= "h_fuse_top"`.
  2. **Max flare width:** draw a **vertical construction line** offset from the centerline, **Smart Dimension** it → `= "w_fuse_half"`, and make the **outermost (flare) control vertex** on each side **Coincident** to it. This pins the bulbous maximum to the envelope.
  3. **Flare height:** dimension each flare vertex to the **floor** → `= "h_crown_flare"`, lifting the widest point off the floor for the pebble bulge.
  4. **Floor-contact width:** dimension each floor endpoint to the centerline → `= "w_fuse_floor_half"`. Because `w_floor_pct` < 1 the floor stays **inboard** of the flare, so the spline must bow outward to reach `w_fuse`/2 — that outward bow *is* the flare. (At the defaults: floor half-width 50.6 mm vs a 55 mm flare.)
  5. **Apex flat width:** dimension each crown vertex to the centerline → `= "w_crown_apex_half"`, and to the waterline → `= "h_fuse_top"` (level with the apex so the Horizontal apex relation holds).

* **Phase 5: Verify.** Status bar **Fully Defined**; spline, control polygon, and every vertex **black**. If blue: a missing **Symmetric** (section drifts off-center), a missing **Tangent/Horizontal** boundary relation (the crease or the peak returns), or an unlinked cage dimension. Relation first, then dimension.

> **Why the bulbous tangent arch.** The 0° floor tangent erases the hard chine the boxy D-section carried where its vertical wall met the floor — the OML now sweeps out of the floor with no crease, cleaner hydrodynamically and easier to skin. Pushing the max width out to a mid-height flare (`crown_sh_pct`) past a narrower floor (`w_floor_pct`) gives the pebble form and lets the crown wrap **inward** over the cabin volume. Tune the profile through `w_floor_pct` (floor width), `crown_sh_pct` (flare height / bulge) and `crown_apex_pct` (flat-top width); the flare stays pinned to `w_fuse`/2. `w_floor_pct` was added to `skeleton_equations_micro.txt` this revision (152 → 153) with Appendix A synced byte-identically; `crown_sh_pct` was repurposed from the old vertical-rise to this flare-height role.

**6.6 — Propeller Disk & Safety Keep-Out Zone.**

**Authoritative geometry lives on `PLN_PropDisk`, not here.** The circles drawn in this section sit on the **Front Plane** (inside `LAY_Front_View`) as a **2D visual proxy** — useful for eyeballing front-view clearance against the arming-plug and switch points. But the Front Plane is **static**: a projection on it does **not** translate when `x_motor` changes, so it must never be treated as the governing safety geometry. The **authoritative, dynamically-tracking 3D disk and 9-inch ring MUST be sketched directly on `PLN_PropDisk`** — the offset plane driven `= "x_motor"` (§2.6) — which slides along **+Z** with the motor station and keeps the keep-out zone honest at every value of `x_motor`. Build that governing layer with the click-by-click workflow in **§7.3.5**, and treat the front-view drawing below as alignment scaffolding only.

**Prerequisites.** Before clicking, ensure you are actively editing your **`LAY_Front_View`** sketch on the Front Plane, with your **vertical centerline** (the $X = 0$ plane of symmetry) and the horizontal **waterline** (the $Y = 0$ line through the Origin) drawn and fully defined. The thrust axis is **no longer pinned to the waterline** — its height is the master parameter `y_motor_offset` (negative = motor dropped below the wing-root Origin). You pin the propeller/keep-out center on the $X = 0$ centerline and *dimension* it `y_motor_offset` off the waterline, so the whole disk rides up or down with that one global.

**Step-by-step execution.**
* **Phase 1: Pin the decoupled thrust center and draw the propeller blade arc (`D_prop`)**
  1. On the **Sketch** tab, select the **Point** tool. Drop a point on the **vertical centerline** ($X = 0$) below the Origin — landing on the line adds a **Coincident** relation that locks $X = 0$. Press **`Esc`**.
  2. Select **Smart Dimension**, click this center point, then click the horizontal **waterline** ($Y = 0$). Pull the preview into a clean vertical gap and **click once** to place it. In the **Modify** box, type exactly `= "y_motor_offset"` and press **Enter**. *(`y_motor_offset` is a **positive magnitude** — place the dimension on the side you want; setting the global to zero runs it through the Origin. Use the **same side** here as in §4.5 or the two views will disagree.)* This is the shared prop/thrust center — **do not** give it a Coincident relation to the waterline.
  3. Select the **Circle** tool (or press the **`S`** shortcut and pick the circle icon). Hover over the black center point until the yellow **Coincident** glyph appears and **click once** to anchor the circle's center on it.
  4. Drag your cursor outward diagonally to expand the circle, and **click a second time** to drop it. Press **`Esc`** to release the tool.
  5. Click the **Smart Dimension** tool, click the circle perimeter, drag into clear space, and **click once** to place the box. Type exactly `= "D_prop"` and press **Enter**.
  > *The circle snaps to your exact propeller diameter, concentric with the decoupled center, and turns black.*
* **Phase 2: Create the 9-inch volunteer-access keep-out ring**
  1. Select the **Circle** tool from the Sketch tab once more.
  2. Hover back over the exact same **shared prop/thrust center point** from Phase 1. Ensure you catch the **Coincident** relation so the two circles are perfectly concentric. **Click once** to start the circle.
  3. Drag your cursor outward until this second circle is visibly larger than the first one, and **click a second time** to drop it. Press **`Esc`**.
  4. Click directly on the perimeter of this new, larger circle to open its properties in the left-hand **PropertyManager** panel.
  5. Under the **Options** section, check the box for **For construction**. Click the green checkmark. *(The solid line converts into a dashed reference circle.)*
  6. Click the **Smart Dimension** tool.
  7. Click the dashed perimeter of this outer keep-out circle, drag the cursor out, and **click once** to place the box.
  8. SolidWorks defaults to driving a full circle by its **diameter**. Because the safety rule specifies a 9-inch (228.6 mm) **radius** buffer *beyond* the blade tips, the total diameter equation must account for both sides of the circle. In the **Modify** box, type exactly `= "D_keepout"` and press **Enter**.

**Verification & compliance audit.**
- **Status check:** Look at the bottom-right corner of the SolidWorks window. The status bar must read **Fully Defined**, and both circles, along with their shared center point, must be entirely **black**.
- **Visual safety check:** Look down the longitudinal axis of the aircraft template. The dashed outer ring represents the 3-D cylinder of the exclusion zone projected onto your front view. When you eventually map the layout positions of the **arming plug** and **power switch**, their front-projected points must sit completely *outside* this dashed circle to verify compliance at a glance.
> **Reminder:** this ring is the front-view *visual* proxy only. The governing compliance is still the 3-D axial check — `arm_clear` and `sw_clear` $\ge 0$ (§4) — so a point that clears the ring in front view must also clear the prop disk *along the thrust axis*. The authoritative, `x_motor`-tracking disk and ring are built on `PLN_PropDisk` in **§7.3.5**.

> **Decoupling flag (front view).** The shared center now carries exactly two constraints — **Coincident** to $X = 0$ and a **`y_motor_offset`** vertical dimension to the waterline. It must **not** retain any Coincident/Collinear pin to the $Y = 0$ waterline; a leftover pin fights the dimension and over-defines (or freezes) the disk the instant you flex `y_motor_offset`. Delete the stray relation, keep the dimension. This is the same pin the side profile (§4.5) and the authoritative sketch (§7.3.5) use, so all three views drop together.

**6.7 — Close the vertical stack-up (the point of this view).**
This section connects your aircraft's flight components (wing root, fuselage, and thrust line) to the physical runway surface using a continuous chain of parametric equations. By referencing everything to a single master **Ground Line**, any downstream change to propeller diameter or landing-gear height auto-adjusts the airframe's runway clearance.

* **Phase 1: Establish the Ground Line**
  1. Ensure you are actively editing your **`LAY_Front_View`** sketch on the Front Plane.
  2. On the **Sketch** tab of the CommandManager, click the arrow next to the **Line** tool and select **Centerline**.
  3. Move your cursor into the workspace well below the fuselage ellipse and the origin.
  4. **Click once** on the left side of the screen, drag your cursor perfectly horizontal to the right, and **click a second time** to drop the line. Press **`Esc`**.
  5. Click the centerline you just drew. In the left-hand **PropertyManager**, under *Add Relations*, click **Horizontal**.
* **Phase 2: Position the Ground Line (the stack-up engine)** — anchored to the **thrust center**, not the wing root, so runway clearance follows the motor.
  1. If a Ground-Line dimension pulled from the wing-root **Origin/waterline** already exists (from an earlier build), **delete it** first — the ground must hang off the thrust center, not the wing datum, or `prop_clear` breaks when the motor drops.
  2. Click the **Smart Dimension** tool on the Sketch tab.
  3. Click directly on your newly created **Ground Line**, then click the **shifted prop/thrust center point** from §6.6 (the one dimensioned `y_motor_offset` below the waterline).
  4. Move your cursor out to the side of the graphics area so the dimension preview becomes a clean vertical gap measurement.
  5. **Click once** to place the text box.
  6. In the **Modify** pop-up dialog box, type exactly `= "h_thrust"` and press **Enter**.
  > **Why anchor to the thrust center:** `prop_clear = "h_thrust" - "D_prop" / 2` assumes the thrust axis sits exactly `h_thrust` above the ground. Hanging the Ground Line `h_thrust` below the **thrust center** (not the Origin) makes that true for **any** `y_motor_offset`, so lowering the motor lowers the ground with it and the blade tip never silently creeps toward the runway. With the starter values the thrust center sits `y_motor_offset` = 20 mm off the Origin on whichever side you dimensioned it, the Ground Line `h_thrust` = 160 mm below the thrust center, the prop tip 140 mm ($D_p/2$) below it, and tip-to-ground $= 20$ mm $=$ `prop_clear`.
* **Phase 3: Build the main gear axles and track**
  - **Step 1 — Draw the axle-height reference line.**
    1. Click the arrow next to the **Line** tool on the Sketch tab and select **Centerline**.
    2. Position your cursor slightly above the Ground Line on the **+X (port)** side of the screen.
    3. **Click once**, drag your cursor horizontally to the left until it snaps directly onto the **vertical centerline** ($X = 0$), and **click a second time** to attach it. Press **`Esc`**.
    4. Click this new short line and verify it has a **Horizontal** relation.
    5. Click the **Smart Dimension** tool.
    6. Click your short **axle centerline**, then click your master **Ground Line**.
    7. Pull the dimension out horizontally, click to place it, type `= "gear_h"`, and press **Enter**.
  - **Step 2 — Establish the half-track fence post.**
    1. On the Sketch tab, click the **Point** tool.
    2. Hover over your short axle centerline out to the right (+X side) until the line highlights, then **click once** to drop a point directly on it. Press **`Esc`**.
    3. Click the **Smart Dimension** tool.
    4. Click the **newly placed point**, then click your master **vertical centerline** ($X = 0$).
    5. Pull the dimension down toward the bottom of the screen to create a flat horizontal measurement.
    6. Click to place it, type `= "track_half"`, and press **Enter**.
* **Phase 4: Draw the main wheel profile**
  1. On the Sketch tab, click the arrow next to the **Rectangle** tool and select **Center Rectangle**.
  2. Move your cursor directly over the half-track point you created in Phase 3. When the orange point highlight appears, **click once** to anchor the center of the rectangle.
  3. Drag your cursor diagonally outward to build a box, and **click a second time** to drop it. Press **`Esc`**.
  4. Hold down your **`Ctrl`** key and click all four outer lines of this new rectangle.
  5. In the left-hand PropertyManager under *Options*, check the box for **For construction**, then click the green checkmark.
  6. Click the **Smart Dimension** tool.
  7. Click one of the vertical side edges of the wheel rectangle, drag the text box clear, click to place it, type `= "wheel_main"`, and press **Enter**. *(In this front view the wheel is edge-on, so this vertical edge is the tire diameter.)*
  8. **Tire width (along $X$).** Click the top or bottom horizontal edge of the wheel rectangle, drag the text box clear, click to place it, type exactly `= "w_wheel"`, and press **Enter**. *(In this front view the wheel is edge-on, so this horizontal edge is the tire's axial width.)*
* **Phase 5: Mirror for starboard symmetry and verify**
  1. Click the **Mirror Entities** tool on the Sketch tab.
  2. In the **Mirror** PropertyManager panel on the left side of your screen:
     * Click inside the **Entities to mirror** field, then in the graphics window select the four outer bounding lines of your wheel rectangle, your short axle centerline, and the track point.
     * Click inside the **Mirror about** field, then click your master **vertical centerline** ($X = 0$) in the graphics area.
  3. Ensure the **Copy** checkbox is checked, then click the **Green Checkmark**.
  4. Verify that the sketch status reads **Fully Defined** and all entities have turned **black**.
  5. Conduct a visual check of your clearance gaps: the bottom edge of the tire profiles should sit flush with the Ground Line, and your 9-inch propeller keep-out ring (§6.6) should sit safely above the Ground Line.

> **Parametric note (tire width).** `w_wheel` is defined in `skeleton_equations_micro.txt` as `= 25` — the main tire's axial width (along $X$), which appears edge-on as the horizontal span of the front-view wheel rectangle. The vertical ground-clearance check only relies on the `wheel_main` diameter, so the width is cosmetic for that check, but dimensioning it keeps the wheel rectangle fully defined and correctly proportioned.

> **Closure consistency (thrust line now decoupled).** The Ground Line hangs `h_thrust` below the **thrust center**, which itself sits `y_motor_offset` below the wing-root **Origin** (§6.6). So the wing root is $|y\_motor\_offset| + h\_thrust$ above the ground (starter: $20 + 160 = 180$ mm), the thrust axis is exactly `h_thrust` above it ($160$ mm), and `prop_clear` holds for any motor drop. The gear flush closure is automatic and *doubly* robust: `gear_h = "wheel_main" / 2`, and because Phase 3 dimensions the axle `gear_h` above the **Ground Line**, the tire bottom lands flush at every `wheel_main` **and** every `y_motor_offset` — the whole gear/ground stack rides down together when the motor drops. Guards still hold: `gear_h` < `h_thrust` ($30 < 160$ — a wheel can't be taller than the thrust line is high), and `prop_clear` > 0 ($20$ mm) as long as `D_prop`/2 < `h_thrust`.

**6.8 — Fin height (VT) reference.**
The vertical stabilizer (the fin) projects straight up from the top spine of the fuselage. In this front-on view, because the fin sits perfectly flat on the aircraft's plane of symmetry ($X = 0$), it is represented as a single vertical reference line whose length matches your vertical-tail span global, `b_VT`.
1. In the **FeatureManager Design Tree**, make sure you are still actively editing your **`LAY_Front_View`** sketch on the Front Plane.
2. On the **Sketch** tab of the CommandManager, click the small arrow next to the **Line** tool icon to open its flyout menu, and select **Centerline**.
3. Move your cursor to the **top quadrant point** of your fuselage ellipse (the absolute peak/crown of the fuselage profile).
4. Hover there until an orange feedback dot appears along with a yellow **Coincident** relation glyph, then **click once** to anchor the start of your centerline to the fuselage spine.
5. Drag your cursor straight **up** vertically, following the main vertical axis of the screen.
6. **Click a second time** out in space well above the fuselage to drop the upper endpoint of the line. Press **`Esc`** to exit the tool.
7. Click the centerline you just drew. In the left-hand **PropertyManager**, under *Add Relations*, click **Vertical** (if SolidWorks did not already capture it automatically during the sketch).
8. Click the **Smart Dimension** tool on the Sketch tab.
9. Click directly on your new vertical centerline.
10. Pull the cursor out to the left or right clear of the geometry, **click once** to drop the text box, type exactly `= "b_VT"`, and press **Enter**.
> **Success state:** the centerline turns entirely **black** and carries the **Σ** equation marker. The top apex of this line now serves as the authoritative height master for your vertical stabilizer.

**6.8.1 — Fin-spar sketch (`LAY_VT_Spar`) → true 3-D fin-spar axis (`AX_VTspar_3D`).** The fin is the one surface whose **span runs vertically** — along $+Y$ — and, because `sweep_VT` = 16.70°, its spar rakes **aft** ($-Z$) as it climbs. It needs **no tilted datum plane**: the vertical stabilizer is always perfectly vertical, so it lives in the **Right Plane** ($X = 0$) and every dimension is an ordinary in-plane distance.

> **No cant, by design.** The wing and stabilizer each need tilted planes because they carry dihedral and incidence; the fin carries neither. There is no `dihedral_VT` global, no `PLN_Dihedral_VT` plane, and no $1/\cos$ projection anywhere in the fin chain — the Right Plane *is* the fin plane, so `h_tail_top` and `h_VT_tip` are dimensioned straight to the waterline with no correction. If a canted or V-tail configuration is ever adopted, that is a new surface layer, not a parameter change here.

* **Phase A — draw the fin spar (`LAY_VT_Spar`).**
  1. Select the **Right Plane** ▸ **Insert ▸ Sketch**; press **`Ctrl + 8`** (Normal To); **F2** → `LAY_VT_Spar`. Orientation: $+Y$ up, $+Z$ forward, $-Z$ aft.
  2. Press **`L`**, tick **For construction**, and draw a rough line climbing up-and-aft.
  3. **Root end (fin base) —** **Smart Dimension** its height to the **waterline** ($Y = 0$) `= "h_tail_top"`, and its distance to the **Front Plane** `= "x_VT_spar_root"` on the aft ($-Z$) side.
  4. **Tip end (fin top) —** height to the waterline `= "h_VT_tip"`, and distance to the **Front Plane** `= "x_VT_spar_tip"` on the aft ($-Z$) side.
  > **The tip $Z$ term is the sweep rake.** `b_VT * tan(sweep_VT)` is how far the swept spar walks aft over the full fin height — the vertical analog of the wing's spanwise sweep offset. Store `sweep_VT` in degrees; `* pi/180` converts inside the expression (§14 item 5).
  5. Confirm `LAY_VT_Spar` reads **fully black**; rotate to isometric and verify it climbs in $+Y$ while raking aft in $-Z$, and that it stays flat on $X = 0$. **Exit** and drag it into `2_LAYOUT_SKETCHES`.
     > **Fin-root seat (flag).** `h_tail_top` seats the fin on the aft crown. If the fin should root further forward on the spine — where the hull is taller — swap `h_tail_top` for `h_fuse_top` or a dedicated `y_VT_root` global; `h_VT_tip` tracks it automatically, and the §8.6 transform's base-height cell `K1` must match whichever you choose.
* **Phase B — promote to `AX_VTspar_3D`.**
  1. **Insert ▸ Reference Geometry ▸ Axis**, **One Line/Edge/Axis**, click the `LAY_VT_Spar` line, green-check, **F2**, rename `AX_VTspar_3D`. File it in `4_AXES` (§7.2).
  > **Success state:** a single swept axis rising from the crown seat to $Y = $ `h_VT_tip`, the reference §7.3.8 slices against. Do **not** confuse its $+Y$ span with the wing/HT $+X$ span — that mix-up is the §14 vertical-axis pitfall.


**6.9 — Mirror and fully define.**
This is the final stabilization and hardening pass for the front-view layout. Any geometry representing a left/right paired feature (like the wing dihedral lines or landing-gear components) must be duplicated across the central vertical axis, and any lingering free movements must be locked down until the sketch is completely static.

**Step 1: Mirror all paired geometry.**
1. On the **Sketch** tab of the CommandManager, click the **Mirror Entities** tool.
2. In the **Mirror** PropertyManager panel on the left side of your screen, click inside the **Entities to mirror** box (it will highlight blue).
3. In the graphics area, select any entities that belong on both sides of the aircraft but haven't been duplicated yet:
   * The angled **Dihedral Line** from §6.3.
   * The four outer bounding lines of your **Main Wheel** rectangle, the short **axle centerline**, and the **half-track point** from §6.7 — **only if you did not already mirror them in §6.7 Phase 5**. Mirroring them a second time stacks duplicate, over-defining geometry, so if Phase 5 is done, mirror just the dihedral line here.
4. Click inside the **Mirror about** box in the left-hand PropertyManager panel (the box will highlight blue).
5. In the graphics area, click your master vertical centerline (the $X = 0$ axis passing through the Origin).
6. Ensure the **Copy** checkbox is checked in the PropertyManager, then click the **Green Checkmark** ($\checkmark$).

**Step 2: Clear under-defined entities (the "drag test").**
1. Look at the **Status Bar** in the very bottom-right corner of your SolidWorks window. If it already reads **Fully Defined**, skip to Step 3. If it reads **Under Defined**, you have blue geometry that can still drift.
2. To find the culprit: click and hold a **blue line** or **blue endpoint** in your sketch, then try to physically **drag** it across the screen.
3. Watch how it shifts to identify the missing constraint:
   * *If a wheel rectangle distorts or stretches:* it is missing its horizontal (tire-width) dimension. Add it with `= "w_wheel"` (§6.7 Phase 4 step 8) — do **not** lock it to a hard number.
   * *If a mirrored entity detaches from its partner on rebuild:* select the original point, hold **`Ctrl`**, select its mirrored partner, and click **Horizontal** or **Symmetric** (using the vertical centerline as the symmetry axis) in the Add Relations panel.
   * *If the Ground Line floats vertically:* re-verify that its distance to the origin is locked to `= "h_thrust"` as detailed in §6.7 Phase 2.

**Step 3: Accept and lock the sketch.**
1. Keep adding geometric relations or equation-linked dimensions until **every single line, circle, ellipse, and point turns solid black**.
2. Confirm that the Status Bar in the bottom-right corner explicitly reads **Fully Defined**. Do not exit the workspace while any item is blue.
3. Click the **Exit Sketch** icon (the confirmation-corner symbol) at the top-right of the graphics area to save your changes.

**6.10 — Name, file, verify.**
- Rename `LAY_Front_View`; file in `2_LAYOUT_SKETCHES`.
- Perturb `dihedral`, `track`, `D_prop`, `b_VT` — confirm the view updates; undo.
- Confirm the battery construction rectangles sit inside the `w_fuse × h_fuse` section and the keep-out ring renders.
- Confirm fully defined and construction-only.

---

## 7. Reference geometry (planes, axes, points, coordinate systems)

This converts the layout sketches into the named, top-level references that downstream parts actually select via Insert Part (§9). Build everything **off the sketch entities/globals** so it stays parametric, and build in this order: points → axes → planes → coordinate systems → group. Budget ~25 minutes.

**7.1 — Promote key sketch points to standalone reference Points.** A reference Point feature is significantly cleaner and less fragile to select downstream in a top-down workflow than a point buried inside a 2D sketch.

**Prerequisites — make your layout sketches visible.** Before generating reference geometry, ensure you can see the points on your screen:
1. Go to your **FeatureManager Design Tree** (left-hand panel).
2. Expand your `2_LAYOUT_SKETCHES` folder.
3. Right-click `LAY_Wing_Plan` and click the **Show** icon (the open eyeball).
4. Right-click `LAY_Side_Profile` and click the **Show** icon.

**Group 1 — Promote the wing-planform CG points.** Promote three points from the centerline of the `LAY_Wing_Plan` sketch: the target CG, the forward limit, and the aft limit.

**1. Target CG point (`PT_CG_target`).**
1. Click **Insert** on the top menu bar ▸ **Reference Geometry** ▸ **Point** (alternatively: go to the **Features** tab on the CommandManager, click the **Reference Geometry** dropdown, and select **Point**).
2. In the **Point PropertyManager** on the left, ensure the **Selection** box (the top box under *Reference Entities*) is highlighted blue.
3. In the graphics area, click the first centerline point you sketched for your target CG (located at distance `= "x_CG"` from the Origin).
4. Click the **Green Checkmark** ($\checkmark$) to create the point.
5. The new feature appears at the bottom of your FeatureManager tree named `Point1`. Click it once, press **F2** (or slow double-click), and rename it exactly to `PT_CG_target`.

**2. Forward CG limit point (`PT_CG_fwd`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the centerline point corresponding to your forward safety limit (located at `= "x_CG_fwd"`).
3. Click the **Green Checkmark**.
4. Select the new `Point2` feature in your tree, press **F2**, and rename it to `PT_CG_fwd`.

**3. Aft CG limit point (`PT_CG_aft`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the centerline point corresponding to your aft safety limit (located at `= "x_CG_aft"`).
3. Click the **Green Checkmark**.
4. Select the new `Point3` feature in your tree, press **F2**, and rename it to `PT_CG_aft`.

**Group 2 — Promote the side-profile hardpoints & centroids.** Promote the hardpoints and bay centers located on your `LAY_Side_Profile` sketch. Rotate your viewport slightly into a 3D isometric perspective if the sketch points overlap on screen.

**4. Bottom drain port (`PT_Drain`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the point sitting directly on your **bottom cabin keel** (`BF → BR`, located at `= "x_drain"`).
3. Click the **Green Checkmark**.
4. In the tree, select the new point, press **F2**, and rename it to `PT_Drain`.

**5. Arming plug point (`PT_ArmPlug`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the first point sitting on your **top cabin keel** (`TF → TR`, located at `= "x_arm_plug"`).
3. Click the **Green Checkmark**.
4. Select the new point in your tree, press **F2**, and rename it to `PT_ArmPlug`.

**6. Receiver on/off switch point (`PT_Switch`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the second point sitting on your **top cabin keel** (`TF → TR`, located at `= "x_switch"`).
3. Click the **Green Checkmark**.
4. Select the new point in your tree, press **F2**, and rename it to `PT_Switch`.

**7. Water-mass centroid station (`PT_Bay_Centroid`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. There is no payload construction rectangle to snap to — the container is not modeled. Instead, in `LAY_Side_Profile` drop a construction point on the **waterline centerline** and Smart Dimension it to the vertical Wing-LE datum as `= "x_bay"` on the **aft (−Z)** side, then click that point here. It carries the water-mass station for the §7.8.3 CG markers and nothing else.
3. Click the **Green Checkmark**.
4. Select the feature in your tree, press **F2**, and rename it to `PT_Bay_Centroid`.

**8. Battery-bay centroid (`PT_Bat_Centroid`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the **center point** of your forward construction rectangle representing your 4S battery pack (located at `= "x_bat"`).
3. Click the **Green Checkmark**.
4. Select the feature in your tree, press **F2**, and rename it to `PT_Bat_Centroid`.

**Group 3 — Promote the ballast reference point.** Rules strictly prohibit placing correction ballast inside the payload container, so this point anchors your adjustable lead plates elsewhere on the frame.

**9. Ballast anchor point (`PT_Ballast`).**
1. Click **Insert ▸ Reference Geometry ▸ Point**.
2. Click the dedicated construction point you placed on the waterline forward of the firewall (§4.6, at `= "x_ballast"`).
3. Click the **Green Checkmark**.
4. Select the feature in your tree, press **F2**, and rename it to `PT_Ballast`.

**Clean up your FeatureManager tree.** To maintain proper external-reference hygiene and keep your tree scannable, folder your new points:
1. In your FeatureManager tree, hold **Ctrl** and select all 9 points you just created (`PT_CG_target` down through `PT_Ballast`).
2. Right-click any of the highlighted points and select **Add to New Folder**.
3. Rename the folder to `5_POINTS`.
4. Right-click your `2_LAYOUT_SKETCHES` folder and click the **Hide** icon (the eyeball with a slash) to clean up your workspace canvas. Your 3D reference points remain cleanly visible as crisp, selectable geometry crosses.

**7.2 — Create the reference axes.** Axes convert the layout construction lines into named, top-level datums that downstream parts select directly. Build the first four **off the existing construction lines**; the fifth (`AX_MainSpar_3D`) is drawn on a tilted dihedral datum plane (`PLN_Dihedral`). All stay fully parametric.

**Prerequisites — make your layout sketches visible.** §7.1 hid `2_LAYOUT_SKETCHES`, so show the sketches again before building axes — their construction lines must be selectable:
1. Expand your `2_LAYOUT_SKETCHES` folder in the **FeatureManager Design Tree**.
2. Right-click `LAY_Wing_Plan` and click the **Show** icon (the open eyeball).
3. Right-click `LAY_Side_Profile` and click the **Show** icon.
4. Right-click `LAY_Front_View` and click the **Show** icon.
5. `LAY_Wing_Incidence` does not exist yet — it is created in item 5, Phase B below, and items 1 and 4 select lines from it, so build item 5 first and come back.

**1. Wing spanwise axis (`AX_MainSpar`).** Build this *after* Phase B below, since its source line now lives in `LAY_Wing_Incidence`.
> **`AX_MainSpar` and `AX_MainSpar_3D` are now the same line.** The wing spar is only ever drawn once, on `PLN_Dihedral`, so there is no separate flat plan-view spar any more. Both axis names are kept and both are promoted from that one construction line, so every downstream reference — `AX_MainSpar` at §7.10 (bolt pierce), §9 (spar cutouts) and §13.3; `AX_MainSpar_3D` at §7.3 / §7.7 / §8 — keeps working unchanged. To carry a single axis instead, delete `AX_MainSpar` and repoint those three sections at `AX_MainSpar_3D`.
1. Go to the top menu bar and click **Insert ▸ Reference Geometry ▸ Axis** (alternatively: on the **Features** tab of the CommandManager, click the **Reference Geometry** dropdown and select **Axis**).
2. In the **Axis PropertyManager** on the left, under *Selection*, click the **One Line/Edge/Axis** radio button.
3. Click inside the **Reference Entities** selection box to make it active.
4. In the graphics window, click directly on the dashed **main-spar construction line** inside your `LAY_Wing_Incidence` sketch (Phase B, Step 4).
5. Click the **Green Checkmark** ($\checkmark$) at the top of the left-hand panel.
6. At the bottom of the FeatureManager tree, slow double-click the new `Axis1` feature (or select it and press **F2**), type `AX_MainSpar`, and press **Enter**.

**2. Motor/propeller centerline (`AX_Thrust`, a.k.a. `AX_Prop`).**
1. Click **Insert ▸ Reference Geometry ▸ Axis**.
2. In the left-hand panel, ensure the **One Line/Edge/Axis** radio button is selected.
3. Click inside the **Reference Entities** selection box.
4. In the graphics window, click directly on the **thrust construction line** from your `LAY_Side_Profile` sketch.
5. Click the **Green Checkmark** ($\checkmark$).
6. Find `Axis2` at the bottom of your design tree, press **F2**, and rename it to `AX_Thrust`. (§4.5 and the later prop-disk keep-out visual select this same feature as `AX_Prop` — the two names refer to one axis.)

**3. Landing-gear intercept (`AX_GearAxle`).**
1. Click **Insert ▸ Reference Geometry ▸ Axis**.
2. In the left-hand PropertyManager, click the **Two Points/Vertices** radio button.
3. Click inside the **Reference Entities** selection box to clear it for input.
4. Zoom into the landing-gear region of your `LAY_Front_View` sketch and click directly on the **center point of your port (left) wheel rectangle** (`Point1` appears in the box).
5. Click directly on the **center point of the mirrored starboard (right) wheel rectangle** on the opposite side of the machine (`Point2` populates next to it). *(A two-point axis is direction-agnostic — the order you pick the two centers doesn't change the resulting line.)*
6. Click the **Green Checkmark** ($\checkmark$).
7. Find the new axis feature at the bottom of your tree, press **F2**, and rename it to `AX_GearAxle`.

**4. Removable structural datum (`AX_WingJoiner`).**
1. Click **Insert ▸ Reference Geometry ▸ Axis**.
2. In the left-hand panel, click the radio button back to **One Line/Edge/Axis**.
3. Click inside the **Reference Entities** selection box.
4. In the graphics window, navigate to your wing-root area and click directly on the **spar-tube/joiner construction line** in your `LAY_Wing_Incidence` sketch (Phase B, Step 4).
5. Click the **Green Checkmark** ($\checkmark$).
6. Find the new axis feature at the bottom of your tree, press **F2**, and rename it to `AX_WingJoiner`.

**5. Tilted structural datum planes (`PLN_Dihedral` → `PLN_Incidence`) → the complete wing sketch (`LAY_Wing_Incidence`) → true 3D spar axis (`AX_MainSpar_3D`).** A flat plan-view spar carries **no dihedral**, so planes normal to it are only approximately square to the real spar. Rather than bridge a separate 3-D sketch, **tilt a dedicated structural datum plane to the dihedral angle and draw the spar directly on it** — the spar, and every rib plane that rides it, then lives in one plane in true 3-D, while `LAY_Wing_Plan` stays flat as the projected-planform source. No new global: the plane reuses `= "dihedral"`.

* **Phase A — create the dihedral datum plane (`PLN_Dihedral`).**
  1. Click **Insert ▸ Reference Geometry ▸ Plane**.
  2. **First Reference —** click the **Top Plane** (the horizontal datum).
  3. **Second Reference —** click `AX_Long` (the §2.3 fore-aft centerline). SolidWorks switches to the **At Angle** option; type the angle `= "dihedral"`.
  4. Use the **Flip** toggle so the plane rises toward the port (**+X**) tip — the preview must climb in **+Y** as it runs out in **+X**. Green-check; **F2** → `PLN_Dihedral`. Drop it into `3_RIB_PLANES` with the wing grid it parents.

* **Phase A2 — the pitch pivot and the incidence plane (`PLN_Incidence`).** Dihedral and incidence are two *different* rotations about two *different* axes, so they need two planes in series. `PLN_Dihedral` handles the roll; `PLN_Incidence` handles the pitch, and the wing sketch is drawn on **`PLN_Incidence`**.
  1. **Pitch pivot.** **Insert ▸ Reference Geometry ▸ Axis**, **Two Planes**: select `PLN_Dihedral` and the **Front Plane**. Green-check; **F2** → `AX_Pitch_Wing`. File it in `4_AXES`.
     > **Why the Front Plane.** The wing root LE *is* the Origin, which lies on the Front Plane, so their intersection line runs spanwise through the root LE — exactly the hinge an incidence rotation should turn about. Pitching about any other station would lift or drop the root LE off the Origin.
  2. **Incidence plane.** **Insert ▸ Reference Geometry ▸ Plane**. **First Reference —** `PLN_Dihedral`; **Second Reference —** `AX_Pitch_Wing`. Choose **At Angle** and type `= "i_wing"`. Use **Flip** so a positive incidence pitches the **leading edge up** (the trailing edge drops in $-Y$ as it runs aft). Green-check; **F2** → `PLN_Incidence`. Drop it into `3_RIB_PLANES`.
  > **At `i_wing` = 0 this plane is coincident with `PLN_Dihedral`** — the current wing, unchanged. The plane exists so that setting `i_wing` to any non-zero value rotates the entire wing sketch about the root LE with no other edit. That is the whole point: the wing is *ready* for incidence rather than needing a rebuild to accept it.
  > **Why `AX_Long` as the pivot.** Dihedral is a pure roll about the root fore-aft line, so the plane hinges on `AX_Long` and passes through the wing-root LE at $Y = 0$. Every point on it then obeys $Y = X\tan(dihedral)$ — place a point at its projected span $X$ and the dihedral rise comes for free, with no hard $Y$ number.

* **Phase B — draw the complete wing on `PLN_Incidence` (`LAY_Wing_Incidence`).** This one sketch carries **everything about the wing**: the 3-D planform outline, both spars, the joiner, the rib stations, the MAC line, the control-surface stations, and both hinge lines. It replaces the old flat wing half of `LAY_Wing_Plan` and the retired `LAY_MainSpar_Dihedral` / `LAY_Hinge_Lines_Dihedral` sketches. Everything in it is already at its true 3-D attitude, because the two-plane chain supplies both $Y$ and the pitch.

  > **⭐ Two rotations, two projection families — neither datum plane is perpendicular any more.** `PLN_Incidence` is rolled by $\Gamma =$ `dihedral` about `AX_Long` **and** pitched by $\theta =$ `i_wing` about `AX_Pitch_Wing`. The roll tips the plane away from the **Right Plane**; the pitch tips it away from the **Front Plane**. So SolidWorks offers a clean point-to-plane dimension to *neither*, and every distance in this sketch is measured **in-plane from the Origin**:
  >
  > | Direction | Measured | Global family | Factor |
  > |---|---|---|---|
  > | Spanwise (in-plane, perpendicular to `AX_Long`) | from the Origin | `_proj` — `b_semi_proj`, `y_MAC_proj`, `rib_root_off_proj`, `y_ail_in_proj` … | $1/\cos\Gamma$ |
  > | Chordwise (in-plane, along the chord) | from the Origin | `_inc` — `x_LE_tip_inc`, `x_spar_root_inc`, `x_MAC_LE_inc`, `x_hinge_ail_in_inc` … | $1/\cos\theta$ |
  >
  > **Line *lengths* take no correction** — `c_root`, `c_tip` and `MAC` are physical chords lying in the plane, so they are drawn at their true value. Only *station* distances, which used to be point-to-plane dimensions, need a projection factor. At `dihedral` = 0 every `_proj` global collapses to its plain value, and at `i_wing` = 0 every `_inc` global does the same — which is exactly the case today, so nothing about the current wing moves.

  1. Click **Insert ▸ Sketch**, pick **`PLN_Incidence`** as the sketch plane, and press **`Ctrl + 8`** (Normal To); **F2** → `LAY_Wing_Incidence`. Orientation: in-plane span runs outboard to port, $+Z$ forward, $-Z$ aft.

  **Step 1 — root chord and tip station.**
  1. Select the solid **Line** tool. Start on the sketch **Origin** (the yellow coincident glyph confirms the snap) and drag straight **aft ($-Z$)**; click to drop the root **TE**. **Smart Dimension** this root chord line → `= "c_root"`. Add a **Vertical** relation (parallel to the $Z$ axis) so the chord stays square to the span.
  2. Select the **Point** tool and drop a **tip station point** out on the port side. **Smart Dimension** its in-plane spanwise distance **from the Origin** → `= "b_semi_proj"`.

  **Step 2 — the swept leading edge.**
  1. Select the solid **Line** tool, click the **Origin (root LE)**, and connect it to the tip station point. This is the wing **leading edge**.
  2. **Smart Dimension** the tip station point's in-plane chordwise distance **from the Origin** → `= "x_LE_tip_inc"` on the aft ($-Z$) side. This is what carries the LE sweep out to the tip.
  > **Do not add a Horizontal relation to the leading edge.** With `sweep_LE` = 11.02° the LE is *not* square to the span — a Horizontal relation will fight the `x_LE_tip_inc` dimension and over-define the sketch. The two dimensions (`b_semi_proj` spanwise, `x_LE_tip_inc` chordwise) fully locate the tip LE on their own.

  **Step 3 — tip chord and trailing edge.**
  1. Select the solid **Line** tool, click the tip LE point, drag straight **aft ($-Z$)**, and drop the tip **TE**. Hold **`Ctrl`**, select this tip chord line and the root chord line, and add a **Parallel** relation. **Smart Dimension** it → `= "c_tip"`.
  2. Select the solid **Line** tool and connect the tip TE back to the root TE to close the panel. The half-panel shades light blue and reads black once Steps 1–3 are dimensioned.

  **Step 4 — spars and the joiner (construction).**
  1. **Main spar.** **Line** tool, tick **For construction**; click on the root chord line, drag outboard, click on the tip chord line. **Smart Dimension** the inboard endpoint's in-plane chordwise distance from the Origin `= "x_spar_root_inc"` (aft, $-Z$); dimension the outboard endpoint `= "x_spar_tip_swept_inc"` chordwise and `= "b_semi_proj"` spanwise, both from the Origin.
  2. **Rear spar.** Another **For construction** line, root to tip, behind the main spar. Inboard endpoint, in-plane chordwise from the Origin `= "x_rspar_root_inc"`; outboard endpoint, in-plane chordwise from the **tip LE** `= "x_rspar_tip_inc"`.
  3. **Wing joiner axis.** A **For construction** line starting on `AX_Long` ($X = 0$) and running outboard. **Smart Dimension** its in-plane chordwise distance from the Origin `= "x_joiner_root_inc"` (aft, $-Z$). Because `x_joiner_root` `= "x_spar_root"`, the joiner sits co-linear with the main spar at the root by construction.
  4. **Physical rib-root seed point.** Select the **Point** tool and click **on** the main spar line to drop a coincident point, then **Smart Dimension** from the spar line's **root endpoint** to this seed — both lie on the line, so this is a true along-spar length → `= "rib_root_off_physical"`. This is the Path 2 seed §7.3 uses.

  **Step 5 — rib stations.**
  1. Select the **Point** tool and drop a seed point directly on the **main spar** construction line. **Smart Dimension** its in-plane spanwise distance from the Origin → `= "rib_root_off_proj"`.
  2. Select that point, click **Linear Sketch Pattern**. Under **Direction 1** select the **main spar line** as the pattern axis. Enter placeholders (spacing `50`, instances `2`), tick **Dimension X spacing** and **Display instance count**, green-check.
  3. Double-click the on-screen spacing dimension → `= "rib_pitch_proj"`; double-click the instance count → `= "n_rib"`.
  4. Hold **`Ctrl`**, select the second patterned point and the main spar line, and add a **Coincident** so the array stays welded to the spar.
  > **What `rib_pitch_proj` does and does not correct.** The $1/\cos\Gamma$ factor removes the **dihedral** foreshortening. The pattern still advances *along the spar*, which also rakes in $Z$ with the LE sweep, so the spanwise projection retains the sweep factor exactly as it did on the flat Top Plane — this move changes nothing about that. If you need stations that are physically exact along the real 3-D spar, use §7.3 **Path 2 / Route A**, which is driven by `rib_root_off_physical` and is unaffected.

  **Step 6 — MAC reference line.**
  1. **Line** tool, **For construction**, drawn parallel to the root chord out on the port panel; add a **Parallel** relation to the root chord line. **Smart Dimension** its in-plane spanwise distance from the Origin → `= "y_MAC_proj"`.
  2. Drop three points on this line and **Smart Dimension** each in-plane chordwise from the Origin, aft ($-Z$): LE point `= "x_MAC_LE_inc"`, quarter-chord point `= "x_MAC_c4_inc"`, and the third so the gap from point 1 to point 3 reads `= "MAC"` (a true in-plane length — no correction).
  > **The CG band stays in `LAY_Wing_Plan`.** `PT_CG_loaded` / `_drained` / `_empty` and the fore/aft limits sit on the fuselage centerline at $X = 0$ (§5.6). They are mass datums, not wing-panel geometry, and at $X = 0$ this plane and the Top Plane coincide anyway — leave them where they are.

  **Step 7 — control-surface stations.**
  1. Select the **Point** tool and drop **four** points directly on the main spar construction line.
  2. **Smart Dimension** each point's in-plane spanwise distance from the Origin: `= "y_ail_in_proj"`, `= "y_ail_out_proj"`, `= "y_flap_in_proj"`, `= "y_flap_out_proj"`.
  3. Hold **`Ctrl`**, select each point and the spar line, and add a **Coincident** so all four stay welded to the spar as `b` flexes.
  > **Flap-out meets aileron-in.** `y_flap_out` and `y_ail_in` both resolve to `"ail_in_pct" * "b_semi"`, so the flap and aileron share a seam with no gap or overlap. For a spacer rib between them, lower `flap_out_pct` or raise `ail_in_pct` in the equations file — never by dragging a point.

  **Step 8 — hinge lines.**
  1. **Aileron hinge.** Press **`L`**, tick **For construction**, and draw a rough line across the aileron span. **Inboard end —** in-plane spanwise from the Origin `= "y_ail_in_proj"`, in-plane chordwise from the Origin `= "x_hinge_ail_in_inc"` (aft, $-Z$). **Outboard end —** `= "y_ail_out_proj"` spanwise and `= "x_hinge_ail_out_inc"` chordwise.
  2. **Flap hinge.** In the *same* sketch press **`L`** again, tick **For construction**, and draw a second line inboard of the aileron. **Inboard end —** `= "y_flap_in_proj"` spanwise and `= "x_hinge_flap_in_inc"` chordwise. **Outboard end —** `= "y_flap_out_proj"` spanwise and `= "x_hinge_flap_out_inc"` chordwise.
  > **The flap hinge is *not* collinear with the aileron hinge.** `(1 - "c_flap_pct")` = 0.70 puts the flap on the **70 %** chord line, 5 % of local chord **forward** of the aileron's 75 %. Because `flap_out_pct` = `ail_in_pct` the two surfaces still meet at one spanwise seam, but their hinge axes are offset in $Z$ — that offset is real and intentional, not a defect.

  **Step 9 — mirror and close out.**
  1. Click **Mirror Entities**. In **Entities to Mirror**, box-select the **wing panel outline** (LE, tip chord, TE). Do **not** select the spars, the joiner, the rib points, the MAC line, the control stations, or the hinge lines — like `AX_MainSpar`, those ride the single port line and the starboard side is derived downstream.
  2. Click inside **Mirror About**, select `AX_Long`, confirm **Copy** is ticked, green-check.
  3. Confirm `LAY_Wing_Incidence` reads **fully black** (Fully Defined). Rotate to isometric: the whole panel climbs in $+Y$ as it runs outboard and rakes aft in $Z$ with the LE sweep. **Exit** the sketch and drag it into `2_LAYOUT_SKETCHES`.
  > **Success state:** one sketch holds the entire wing. `AX_MainSpar`, `AX_MainSpar_3D`, `AX_WingJoiner`, `AX_Hinge_Ail`, `AX_Hinge_Flap` and every §7.3 rib plane are promoted from lines inside it, so a single `dihedral` or `sweep_LE` edit re-solves the outline, the spars, the ribs and the hinges together — they can no longer disagree, because they are no longer in separate sketches.


* **Phase C — promote to `AX_MainSpar_3D`.**
  1. Click **Insert ▸ Reference Geometry ▸ Axis**; select **One Line/Edge/Axis** and click the **main-spar construction line** inside `LAY_Wing_Incidence` (Phase B, Step 4).
  2. Green-check; **F2** → `AX_MainSpar_3D`.
  > **Success state:** the same named axis §7.3 slices against — now carrying true sweep **and** dihedral because it lives on `PLN_Dihedral`. Every downstream reference (rib planes §7.3, hinges §7.7, the §8 loft) selects it unchanged.

**Tree housekeeping — folder the axes.** Group the five axes into the `4_AXES` folder from the §1.6 scheme (`LAY_Wing_Incidence` goes into `2_LAYOUT_SKETCHES` with the other layout sketches):
1. In your FeatureManager tree, hold **Ctrl** and select all five axes (`AX_MainSpar`, `AX_Thrust`, `AX_GearAxle`, `AX_WingJoiner`, `AX_MainSpar_3D`).
2. Right-click any highlighted axis and select **Add to New Folder**.
3. Rename the folder to `4_AXES`.

**7.3 — Create the rib-station planes (true-normal to the 3D spar).** Rib planes must sit **perpendicular to the real spar**, which is tilted by **both** the plan-view sweep/taper slope and the front-view **dihedral**. Offsetting flat planes from the Right Plane (normal to X) is only a small-angle approximation; here each plane is sliced **normal to the true 3D axis** `AX_MainSpar_3D` (built in §7.2) **at a parametric station point from §5.5** — so location comes from the §5.5 array and orientation comes from the true spar.

* **Phase 1: Base plane generation (`PLN_RibStn_R01`).**
  1. Click **Insert ▸ Reference Geometry ▸ Plane**.
  2. **First Reference —** click `AX_MainSpar_3D`. SolidWorks defaults to a **Coincident/Parallel** guess (an invalid plane lying *through* the axis); open the constraint dropdown beside the selection box and change it to **Normal to Curve**. The preview flips to a small plane square to the axis.
  3. **Second Reference —** pick the seed that matches your propagation route (Phase 2). The two paths are mutually exclusive; choose by whether you want the wing pinned to exact **spanwise** stations or driven **100% physically** along the spar:
     - **Path 1 — Projected / hybrid (feeds Route B).** Click the **first patterned seed point** on the main-spar line inside `LAY_Wing_Incidence` (§7.2 Phase B Step 5, at `= "rib_root_off_proj"`). SolidWorks projects that spanwise station perpendicularly onto the 3D axis and pins the plane there — tilted by the true sweep **and** dihedral. Location comes from the 2D array's **spanwise ($X$) station**, so this base stays exactly co-planar with the per-station points Route B selects downstream.
     - **Path 2 — Pure physical (feeds Route A).** Click the **3D seed point created directly on the spar line** inside `LAY_Wing_Incidence` (§7.2 Phase B Step 4, dimensioned `= "rib_root_off_physical"`). The point already **lives on the axis**, so there is no projection step at all — its location is a true along-spar physical station. This is the base plane for a fully physical layout; pick it if you will propagate with Route A.
  4. Click the **Green Checkmark** ($\checkmark$) and rename the plane `PLN_RibStn_R01`.
  > **Why this works:** *Normal to Curve* always takes **orientation** from the 3D axis; the second reference supplies only **location**. Neither carries a hard number, so the plane's tilt re-solves with `dihedral`/`sweep_LE`/taper regardless of path, while its station re-solves with `rib_root_off` (**Path 1**, projected spanwise) or `rib_root_off_physical` (**Path 2**, along-spar) — no `->x`, no stale offset either way.
  > **Success state:** `PLN_RibStn_R01` renders as a small rectangle **canted in both Y and Z** (not parallel to the Right Plane). **Measure** it to the Right Plane and it reports a non-zero tilt equal to the compound spar angle.

* **Phase 2: Parametric propagation of the remaining stations.** Two routes — pick per your PDM/naming needs.

  **Route A — Linear Pattern of Reference Geometry (auto-count).** Built on the **Path 2** (pure-physical) base plane — this is what makes the whole set physical end to end.
  1. **Insert ▸ Pattern/Mirror ▸ Linear Pattern**.
  2. **Direction 1 —** click `AX_MainSpar_3D` so the copies march **along the true spar**, not along X.
  3. Spacing `= "rib_pitch"`; instances `= "n_rib"`.
  4. Open the **Features to Pattern ▸ Reference Geometry** box and pick `PLN_RibStn_R01`; green check. The set re-counts and re-spaces whenever `rib_pitch` or `n_rib` changes — flex-safe in both directions.
  5. **Rename the pattern feature.** Slow-double-click the newly created linear-pattern feature at the bottom of the tree (or press **F2**) and rename it exactly `LPTN_RibPlanes`. In SolidWorks the patterned reference planes live *inside* this single master pattern feature rather than as separate top-level planes, so suffix naming (`R02`, `R03`, …) is handled implicitly by the pattern instances — naming the parent feature cleanly is paramount.
  6. **File it immediately.** Drag both the seed plane (`PLN_RibStn_R01`) and the pattern feature (`LPTN_RibPlanes`) up the tree and drop them into the `3_RIB_PLANES` folder.
  > **Why Pure Route A is self-consistent:** the base plane is located by `rib_root_off_physical` — a true along-spar length (§7.2 Phase B Step 4) — **and** the pattern steps `rib_pitch` **along that same 3D axis**. Every station on the wing is therefore measured in one and the same **physical, along-spar metric**. There is no longer a projected-2D base feeding a 3D pattern, so the projected-vs-real mismatch that used to corrupt the **first bay** is gone: the inboard bay is now spaced by the exact same rule as every bay outboard of it. The layout is untangled from `LAY_Wing_Plan`'s flat points from the very first plane.
  > **Honest note — physical pitch ≠ spanwise pitch, by design:** `rib_pitch` is *defined* spanwise (§5.5), and Route A lays it **along** the tilted axis, so the absolute spanwise ($X$) stations sit slightly inboard of the flat §5.5 array by $1/(\cos\Gamma\,\cos\Lambda_{spar})$ (≈ 0.4 % at `dihedral = 4°`, `sweep_LE = 0`). Under Pure Route A this is a **uniform, intentional** physical spacing applied identically to every bay — not an interior inconsistency. If instead you need the ribs pinned to the exact spanwise §5.5 stations, take **Path 1 → Route B**, which is station-exact in $X$.

  **Route B — Manual per-station planes (station-exact, clean names).** Built on the **Path 1** (projected) base plane, keeping the whole set on the 2D spanwise §5.5 stations. Best when each plane needs its own name for tidy **Insert Part** picks or PDM. For each station $n = 2 \ldots$ `n_rib`:
  1. **Insert ▸ Reference Geometry ▸ Plane**.
  2. **First Reference —** `AX_MainSpar_3D`, dropdown → **Normal to Curve**.
  3. **Second Reference —** the **$n$-th patterned point** of the §5.5 array (`Point{n}` of the Linear Sketch Pattern on the spar). The plane pins to that exact spanwise station.
  4. Green check; rename `PLN_RibStn_R{nn}` (`R02`, `R03`, …).
  5. **File it as you go.** Drag each new `PLN_RibStn_R{nn}` immediately into the `3_RIB_PLANES` folder to keep the workspace clear.
  > **Mapping.** Station $n$ lives at spanwise $x_n = rib\_root\_off + (n-1)\,rib\_pitch$ — the §5.5 point — and its plane is **Normal to Curve** on `AX_MainSpar_3D`, so every plane inherits the exact array **location** and the true compound **tilt**. Because each plane's location reference *is* a §5.5 pattern instance, editing `rib_pitch` or `n_rib` re-drives the point and the plane rides with it; there is no hard offset to go stale.
  > **Dangling-ref guard (Route B):** manual planes bind to specific instances `Point{n}`, so **reducing** `n_rib` deletes trailing instances and would leave those planes with a `->x` missing reference. If you flex `n_rib` **down**, delete the now-orphaned high-station planes first (or use Route A, which auto-counts). Flexing `n_rib` **up** simply leaves the new outboard points unplaned until you add planes — no breakage.

**7.3.5 — Authoritative propeller disk & safety ring on `PLN_PropDisk` (click by click).** To make the propeller disk and the 9-inch safety cylinder slide along **+Z** automatically whenever the motor-extension global `x_motor` changes, host the layout **directly on the moving frontal plane** `PLN_PropDisk` (which already exists from §2.6, offset `= "x_motor"`) — never on the static Front Plane. This is the governing geometry that §6.6's front-view drawing only *proxies*.

* **Step 1: Open the sketch on the moving frontal plane.**
  1. Locate the reference plane **`PLN_PropDisk`** in the FeatureManager Design Tree.
  2. Left-click once directly on **`PLN_PropDisk`** to raise its context toolbar.
  3. Click the **Sketch** icon (the pencil-drawing-a-line symbol) to open a new sketch.
  4. Press **`Ctrl + 8`** to snap the viewport **Normal To** the plane.

* **Step 2: Pin the thrust-axis center point.** The center sits on the symmetry plane ($X = 0$) but is **dropped `y_motor_offset` below** the wing-root height ($Y = 0$), matching the decoupled thrust line of §4.5/§6.6. That is one **Coincident** plus one signed **dimension** — and it still rides `x_motor` in **+Z** through the plane offset:
  1. On the **Sketch** tab of the CommandManager, select the **Point** tool.
  2. Move your cursor near the **sketch origin** (the projection of the model Origin onto the plane) and left-click once to drop a point. Press **`Esc`**.
  3. Click your new point, hold **`Ctrl`**, select the default **Right Plane** from the flyout FeatureManager tree, and click **Coincident** under *Add Relations*. This pins the point to $X = 0$. Clear your selections.
  4. Select **Smart Dimension**, click the point, then click the default **Top Plane** ($Y = 0$) from the flyout tree. Pull the preview into a clean vertical gap, click to place it, and type exactly `= "y_motor_offset"` ▸ **Enter**. **Do not** add a Coincident relation to the Top Plane.
  > **Why a `y_motor_offset` dimension, not a Top-Plane coincident:** the thrust line is decoupled from the wing root (§4.5) and sits `y_motor_offset` below it. Pinning this center *coincident* to the Top Plane would re-lock it to $Y = 0$ and silently contradict the side and front views — the authoritative disk would float at the wing datum while the real thrust axis dropped. The signed dimension keeps all three views ($X = 0 \cap y\_motor\_offset$) in lockstep. *(An earlier build used a Top-Plane coincidence here because the thrust line then ran through the Origin; the `y_motor_offset` decoupling supersedes it.)*
  *(The point turns solid black — Fully Defined — marking where the thrust axis pierces the prop-disk plane at the true $Z = $ `x_motor` station.)*

* **Step 3: Draw and parameterize the propeller disk (`D_prop`).**
  1. On the **Sketch** tab, select the **Circle** tool.
  2. Hover over the black thrust-center point until the orange feedback dot and yellow **Coincident** glyph appear, then left-click once to anchor the circle's center.
  3. Drag outward to grow the circle and left-click a second time to place it. Press **`Esc`**.
  4. Click once on the circle line; in the left-hand **PropertyManager** under **Options**, check **For construction**, then click the **Green Checkmark** ($\checkmark$).
  5. Select the **Smart Dimension** tool, click the dashed circle, drag into clear space, and click to drop the text box.
  6. In the **Modify** box, type exactly `= "D_prop"` and press **Enter**.

* **Step 4: Build the 9-inch concentric safety keep-out ring (`D_prop + 2·keepout`).**
  1. Select the **Circle** tool from the Sketch tab again.
  2. Hover back over the black center point, catching the **Coincident** glyph to ensure perfect concentricity. Left-click once to start, drag outward until this circle is clearly larger than the first, and left-click a second time to place it. Press **`Esc`**.
  3. Click once on the outer circle line; in the **PropertyManager** under **Options**, check **For construction**, then click the **Green Checkmark** ($\checkmark$).
  4. Select the **Smart Dimension** tool, click the dashed outer circle, drag clear of the geometry, and click to place the box.
  5. Because SolidWorks drives a full circle by its **diameter**, the 9-inch **radius** buffer beyond the blade tips must be applied to both sides. In the **Modify** box, type this exact string: `= "D_keepout"`.
  6. Press **Enter**.

* **Step 5: Exit, rename, and audit in 3D space.**
  1. Verify the bottom-right status bar reads **Fully Defined** and every sketch entity has turned solid black.
  2. Click the **Exit Sketch** arrow in the top-right confirmation corner of the viewport.
  3. In the FeatureManager tree, slow-double-click the new sketch (or select it and press **F2**), rename it exactly `LAY_Prop_Safety`, and press **Enter**.
  4. Click and drag `LAY_Prop_Safety` up the tree, dropping it into your **`2_LAYOUT_SKETCHES`** folder.
  5. Press **`Ctrl + 7`** for an isometric view and confirm the safety boundaries float out at the engine-face station — the sketch's $Z$ coordinate equals `x_motor`. Now bump `x_motor` in the equations and force-rebuild (**`Ctrl + Q`**): the whole ring must translate along **+Z** with the plane, then undo.
  > **Success state:** `LAY_Prop_Safety` lives on `PLN_PropDisk`, fully defined, with both circles centered on the thrust axis. When `x_motor` changes, this authoritative layer slides in true 3D while the §6.6 front-view proxy stays put — the keep-out zone can never fall out of sync with the motor station.

**7.3.6 — Dedicated Fuselage Reference Planes (Decoupled Strategy).** The fuselage OML (§8.5) is built on its *own* set of longitudinal planes, offset straight from the **Front Plane** by the `x_fuse_*` stations (§3) — never on the wing rib planes. This severs the fuselage from `rib_pitch` / `n_rib`: flex the wing grid, change the rib count, and the fuselage never rebuilds. Build all **seven** planes now, before any fuselage cross-section sketch — the five `x_fuse_*` stations plus two mid-station transition planes (`PLN_Fuse_MidNose`, `PLN_Fuse_MidTail`) for the §8.5 loft.

* **The one-plane recipe (repeat for each station in the table below).**
  1. Click **Insert ▸ Reference Geometry ▸ Plane** from the top menu.
  2. **First Reference:** in the flyout FeatureManager, click the default **Front Plane**.
  3. Under the constraint buttons, pick **Offset Distance** $(\rightarrow|)$.
  4. Clear the distance box and type the station's global exactly — e.g. `= "x_fuse_firewall"` — then press **`Enter`**.
  5. **Direction guard (Flip).** Watch the yellow preview. The **Front Plane** offsets to one side by default; the fuselage convention is **+Z = forward (nose)**, **−Z = aft (tail)**. If a **+Z (forward)** station previews *aft*, tick **Flip**; if a **−Z (aft)** station previews *forward*, tick **Flip**. Confirm the preview lands on the side listed in the table.
  6. Click the **Green Checkmark** $(\checkmark)$, immediately press **F2**, and rename the plane with its `PLN_Fuse_` name.

| Station global | Plane name | Offset [mm] | Side (Flip target) |
|---|---|---|---|
| `= "x_fuse_nose"` | `PLN_Fuse_Nose` | 304.80 | **+Z** forward |
| `= "x_fuse_midnose"` | `PLN_Fuse_MidNose` | 228.60 | **+Z** forward |
| `= "x_fuse_firewall"` | `PLN_Fuse_Firewall` | 152.40 | **+Z** forward |
| `= "x_fuse_bay_fwd"` | `PLN_Fuse_Bay_Fwd` | 50.00 | **+Z** forward |
| `= "x_fuse_bay_aft"` | `PLN_Fuse_Bay_Aft` | 101.60 | **−Z** aft |
| `= "x_fuse_midtail"` | `PLN_Fuse_MidTail` | 127.00 | **−Z** aft |
| `= "x_fuse_tail"` | `PLN_Fuse_Tail` | 152.40 | **−Z** aft |

> **Watch the two 152.40 mm planes — they flip *opposite* ways.** `PLN_Fuse_Firewall` and `PLN_Fuse_Tail` carry the **same** offset magnitude but sit on **opposite** sides of the Origin: the firewall **forward** (+Z), the tail cap **aft** (−Z). They take opposite Flip states. Sanity-check the result: the firewall plane appears ahead of the wing LE, the tail plane behind it, exactly `cabin_len` + `x_fuse_tail` − `x_fuse_bay_aft` = 304.80 mm apart.

> **The two mid-station planes ride dedicated globals.** `PLN_Fuse_MidNose` and `PLN_Fuse_MidTail` are offset by `= "x_fuse_midnose"` and `= "x_fuse_midtail"` — absolute stations in `skeleton_equations_micro.txt` that also anchor the side-profile `M`-breaks (§3) and the planform `P`-breaks (§5.3.5). Link each **Offset Distance** to its global rather than typing a raw expression, so all three subsystems track one station.

* **Housekeeping — dedicated folder.**
  1. In the FeatureManager tree, **`Ctrl`-click** all seven `PLN_Fuse_*` planes.
  2. **Right-click** any one, choose **Add to New Folder**, and name the folder exactly `3B_FUSELAGE_PLANES`.
  3. Drag the folder to sit just below `3_RIB_PLANES`, so the wing grid and the fuselage grid read as **separate, parallel subsystems** in the tree.
  > **Validation (decoupling check).** Open **Tools ▸ Equations**, bump `n_rib` (7 → 9) and `rib_pitch`, and force-rebuild (**`Ctrl + Q`**). The seven `PLN_Fuse_*` planes must **not move or error** — they answer only to `x_fuse_*`, never to the rib grid. Then flex a fuselage input (`x_bay` or `L_fuse`) and confirm the matching plane slides while the rib planes stay put. Undo.

**7.3.7 — Horizontal-tail section planes (Normal-to-Curve on `AX_HTspar_3D`).** Like the wing rib planes (§7.3), HT section planes sit **normal to the true tail-spar axis** and are bounded by the HT semi-span $X = $ `b_HT`$/2$. Build them in a dedicated tail-plane folder so the empennage stays decoupled from both the wing rib grid and the fuselage stations.
* **Root section plane (`PLN_HT_Root`).**
  1. **Insert ▸ Reference Geometry ▸ Plane**.
  2. **First Reference —** click `AX_HTspar_3D`; open the constraint dropdown and set **Normal to Curve** (SolidWorks' first guess lies *through* the axis — override it).
  3. **Second Reference —** click the **HT root-spar point** (inboard end of the §5.8.1 line, at the centerline $X = 0$). The plane pins there, square to the spar.
  4. Green-check; rename `PLN_HT_Root`.
* **Tip section plane (`PLN_HT_Tip`).** Repeat with the **HT tip-spar point** (outboard end, at $X = $ `b_HT`$/2$) as the second reference. Rename `PLN_HT_Tip`.
* **Optional intermediate rib planes (`LPTN_RibPlanes_HT`).** For a multi-rib stabilizer, seed a **Linear Pattern** (**Insert ▸ Pattern/Mirror ▸ Linear Pattern**):
  1. **Features to Pattern —** click `PLN_HT_Root`.
  2. **Direction 1 —** click `AX_HTspar_3D` (copies step outboard along the true tail-spar axis).
  3. **Spacing —** click the spacing field, hit the **equals-arrow** (`=`) to open the equation dropdown, and enter `= "rib_pitch_HT"`.
  4. **Number of Instances —** same equation dropdown, enter `= "n_rib_HT"`.
  5. Preview and confirm the outermost plane lands **at or inside** $X = $ `b_HT`$/2$ (co-planar with `PLN_HT_Tip`). Green-check; press **F2** and rename the feature `LPTN_RibPlanes_HT` — parity with the wing's `LPTN_RibPlanes`.
  > **Pattern globals — `rib_pitch_HT` × `n_rib_HT`.** Both **Spacing** and **Number of Instances** link to globals (`= "rib_pitch_HT"`, `= "n_rib_HT"`), exactly as the wing's `LPTN_RibPlanes` rides `rib_pitch` × `n_rib`. `rib_pitch_HT` is **derived** (`b_semi_HT / (n_rib_HT − 1)`), so the outermost plane tracks `PLN_HT_Tip` automatically as the tail resizes; `n_rib_HT` is a starter (4) — set it to your stabilizer rib count. Both drive pattern-feature parameters, not sketch dimensions, so linking them keeps the tail rib grid flex-safe without touching the parametric-dimension rule.
  > **Currently flat, by design.** With `sweep_HT` = 0 and no HT dihedral, these planes come in normal-to-$X$ (flat) — correct for the present geometry. They auto-tilt the moment `AX_HTspar_3D` gains sweep or dihedral (§5.8.2), because **Normal to Curve** always takes orientation from the live axis.
* **File the planes.** **`Ctrl`**-select `PLN_HT_Root` / `PLN_HT_Tip` (and any pattern), **right-click ▸ Add to New Folder** named `3C_TAIL_PLANES`, and drag it below `3B_FUSELAGE_PLANES` so wing / fuselage / tail read as three parallel, decoupled subsystems.

**7.3.8 — Vertical-tail section planes (the vertical-axis coordinate shift).** The fin is the coordinate-shift case: its **span runs up $+Y$**, so its section planes are **horizontal** (parallel to the Top Plane), stacked in $+Y$ and bounded by the fin height `= "b_VT"` — *not* lateral offsets like the wing/HT. Two builds; pick per how square you need the airfoils to the swept spar.
* **Method 1 — horizontal offsets from the Top Plane (simple; sections square to $+Y$).**
  1. **Insert ▸ Reference Geometry ▸ Plane**, **First Reference** = **Top Plane**, **Offset Distance** `= "h_tail_top"`, and **Flip** so it previews **up** ($+Y$) onto the crown seat. Green-check; rename `PLN_VT_Root`.
  2. Repeat with **Offset Distance** `= "h_VT_tip"` for the fin top. Rename `PLN_VT_Tip`.
     > Sections built on these horizontal planes stay horizontal; the chord still rakes aft between them because the *airfoil $Z$-station* rides `sweep_VT` in the §8.6 transform. This is the standard fin build and it matches how the Excel streams place the root and tip sections.
* **Method 2 — Normal-to-Curve on `AX_VTspar_3D` (rigorous; sections square to the raked spar).**
  1. **Insert ▸ Reference Geometry ▸ Plane**, **First Reference** = `AX_VTspar_3D` → **Normal to Curve**, **Second Reference** = the fin-spar **root** endpoint. Rename `PLN_VT_Root`.
  2. Repeat at the fin-spar **tip** endpoint → `PLN_VT_Tip`.
     > These tilt slightly off-horizontal by the `sweep_VT` rake, giving airfoils truly perpendicular to the swept spar. Use them only if fin-rib fabrication needs square-to-spar sections; otherwise Method 1 is cleaner.
* **Optional intermediate fin planes (`LPTN_RibPlanes_VT`).** For a multi-rib fin, seed a **Linear Pattern** (**Insert ▸ Pattern/Mirror ▸ Linear Pattern**) of the root plane — the fin's vertical analog of the wing / HT rib pattern:
  1. **Features to Pattern —** click `PLN_VT_Root`.
  2. **Direction 1 —** *Method 1 build:* click the **Top Plane** — the pattern steps along its normal, straight up $+Y$, keeping every copy horizontal. *Method 2 build:* click `AX_VTspar_3D` — the copies step along the raked spar and stay **Normal to Curve**.
  3. **Spacing —** click the spacing field, hit the **equals-arrow** (`=`) to open the equation dropdown, and enter `= "rib_pitch_VT"`.
  4. **Number of Instances —** same dropdown, enter `= "n_rib_VT"`.
  5. Preview and confirm the stack climbs in $+Y$ and the outermost copy lands **at or inside** `PLN_VT_Tip` (at $Y = $ `h_tail_top` $+$ `b_VT`). *Method 1 lands the top instance exactly on the tip; Method 2 stops just short of it by the `sweep_VT` rake — both satisfy "at or inside."* Green-check; press **F2** and rename the feature `LPTN_RibPlanes_VT`.
  > **Pattern globals — `rib_pitch_VT` × `n_rib_VT`.** Both fields link to globals, mirroring the wing's `LPTN_RibPlanes` (`rib_pitch` × `n_rib`) and the HT's `LPTN_RibPlanes_HT`. `rib_pitch_VT` is **derived** (`b_VT / (n_rib_VT − 1)`), so the top instance tracks `PLN_VT_Tip` automatically as the fin resizes; `n_rib_VT` is a starter (4) — set it to your fin-rib count. Both drive pattern-feature parameters, not sketch dimensions, so they respect the parametric-dimension rule.
  > **Vertical-axis guard (pattern).** Because the seed is a horizontal plane (Method 1) or a raked-spar plane (Method 2), verify the copies advance in **$+Y$**, not $X$ — the same fin-vs-wing check as the single planes below. If the stack marches in $X$, Direction 1 is pointing at a lateral edge; reselect the Top Plane or `AX_VTspar_3D`.
* **File the planes** into `3C_TAIL_PLANES` alongside the HT planes (the `LPTN_RibPlanes_VT` instances land there too).
  > **Vertical-axis guard.** Whichever method you use, **Measure** `PLN_VT_Root` → `PLN_VT_Tip` and confirm the gap resolves in **$Y$** (= `b_VT`), not $X$. A gap reading in $X$ means you built the fin like a wing — the classic vertical-axis error (§14).

**7.4 — Create the coordinate systems (step-by-step alignment).** This step converts your layout points and orthogonal planes into the named, exportable coordinate-system datums that downstream parts select via **Insert Part** to align automatically without manual positioning.

When selecting references in the **Coordinate System** PropertyManager, selecting a flat **plane** forces that axis **perpendicular (normal)** to the plane, while selecting a **line** forces it **parallel**. We use the default orthogonal planes to lock in the directions, then use the PropertyManager **flip** toggles to match your exact aircraft orientation ($+Z$ forward, $+X$ port, $+Y$ up).

**Prerequisites — prepare your workspace.** Before creating the coordinate systems, ensure the tail datum point is visible:
1. In the **FeatureManager Design Tree**, expand your `2_LAYOUT_SKETCHES` folder.
2. Right-click `LAY_HTail_Incidence` and click the **Show** icon (the open eyeball) to expose your horizontal-tail root point.

**Create `CSYS_Wing` — the wing master datum.** This coordinate system establishes the local master datum for your wing assembly, rooted at the wing-root leading edge.
1. Go to the top menu bar and click **Insert ▸ Reference Geometry ▸ Coordinate System** (or on the **Features** tab of the CommandManager, click the **Reference Geometry** dropdown and select **Coordinate System**).
2. Locate the four selection boxes in the left-hand PropertyManager: *Origin*, *X Axis*, *Y Axis*, and *Z Axis*.
3. **Select the origin:** click inside the **Origin** selection box, then click the global part **Origin** $(0,0,0)$ at the very top of your FeatureManager Design Tree.
4. **Align the X-axis (spanwise / port):**
   - Click inside the **X Axis** selection box.
   - Open the flyout FeatureManager tree in the top-left of the graphics area and select the **Right Plane**.
   - Look at the preview triad. If the red X arrow points to starboard, click the **Flip Axis Direction** button $(\rightleftarrows)$ next to the selection box so that $+X$ **points to port**.
5. **Align the Y-axis (vertical / up):**
   - Click inside the **Y Axis** selection box.
   - In the flyout tree, select the **Top Plane**.
   - If the green Y arrow points down, click the **Flip Axis Direction** button $(\rightleftarrows)$ next to the Y box so that $+Y$ **points up**.
6. **Align the Z-axis (longitudinal / forward):**
   - Click inside the **Z Axis** selection box.
   - In the flyout tree, select the **Front Plane**.
   - Click the **Flip Axis Direction** button $(\rightleftarrows)$ next to the Z box until the blue $+Z$ **arrow points forward** toward the nose.
7. Click the **Green Checkmark** $(\checkmark)$ to accept.
8. Slow double-click the new feature at the bottom of your tree (or press **F2**) and rename it exactly to **`CSYS_Wing`**.

**Create `CSYS_HTail` — the tail local frame.** This duplicates the exact orientation of your master frame but offsets the origin to the tail, giving your empennage components a clean local frame.
1. Click **Insert ▸ Reference Geometry ▸ Coordinate System**.
2. **Select the tail origin:** click inside the **Origin** selection box, zoom into the tail section, and click directly on the **horizontal-tail root leading-edge point** (the construction vertex sketched on the centerline at the `x_HT_LE_root` station in §5.8).
3. **Align the X-axis:** click inside the **X Axis** selection box, select the **Right Plane** from the flyout tree, and ensure the red arrow points to **port** ($+X$), using the flip button $(\rightleftarrows)$ if necessary.
4. **Align the Y-axis:** click inside the **Y Axis** selection box, select the **Top Plane** from the flyout tree, and ensure the green arrow points **up** ($+Y$), using the flip button $(\rightleftarrows)$ if necessary.
5. **Align the Z-axis:** click inside the **Z Axis** selection box, select the **Front Plane** from the flyout tree, and ensure the blue arrow points **forward** ($+Z$) toward the nose, using the flip button $(\rightleftarrows)$ if necessary.
6. Click the **Green Checkmark** $(\checkmark)$ to accept.
7. Select the new feature at the bottom of your tree, press **F2**, and rename it exactly to **`CSYS_HTail`**.

**Verification & housekeeping pass.**
- Clear any active selections and verify that both triads are perfectly parallel on screen, color-coded as **X (red) = port**, **Y (green) = up**, and **Z (blue) = forward**.
- Hold **Ctrl**, select both `CSYS_Wing` and `CSYS_HTail` in your tree, right-click, select **Add to New Folder**, and name the folder **`6_CSYS`** to maintain tree organization.

These give downstream parts clean origins to mate to and a consistent frame for mass properties, FEA, and manufacturing exports.

**7.5 — Group and name.** Ensure your base rib plane (`PLN_RibStn_R01`) and its pattern engine (`LPTN_RibPlanes` for Route A) or individual planes (`PLN_RibStn_R02`+ for Route B) reside completely inside the `3_RIB_PLANES` folder. Confirm every other newly created reference entity carries its correct prefix name into its respective folder (`4_AXES`, `5_POINTS`, `6_CSYS`), leaving no default SolidWorks names (e.g. `Plane3`, `Axis1`) behind.

**7.6 — Verify parametric behavior.**
- Bump `b` → rib planes re-space, `AX_MainSpar` shifts, `CSYS_HTail` tracks `x_HT_LE_root`; undo.
- Change `n_rib` (7 → 9) → the rib-plane pattern re-counts.
- `Ctrl-Q` rebuild is clean with **no dangling references** (no over-defined/yellow flags).
- Confirm the skeleton still carries **no solid bodies** (mass properties ≈ 0).

**7.7 — Control Surfaces, Kinematic Hinge Lines, and Servo Envelopes.** This section governs the wing's moving surfaces — inboard **flaps** and outboard **ailerons** — as pure body-free reference geometry: spanwise station points and true 3-D hinge axes (servo keep-out envelopes move to the Installation guide, §I-1). Everything rides the same globals and the same $+Z$ forward / $+Y$ up / $+X$ port frame, symmetric about the Right Plane, and nothing here adds a solid body. Build order: station points → 3-D hinge axes → (downstream) rib split. Budget ~30 minutes.

> **Globals — the control-surface and servo sets already exist.** The spanwise limits and chord depths are already in `skeleton_equations_micro.txt`: `ail_in_pct` = 0.55, `ail_out_pct` = 0.95, `c_ail_pct` = 0.25 (the aileron is the aft 25 % of chord → hinge at **75 % chord**); `flap_in_pct` = 0.10, `flap_out_pct` = 0.55, `c_flap_pct` = 0.30 (hinge at **70 % chord**); plus the pre-derived lateral stations `y_ail_in` / `y_ail_out` / `y_flap_in` / `y_flap_out` (each = its `*_pct` $\times$ `b_semi`). The **servo hardware block** is also in the equations file, mirrored into Appendix A of `Aircraft_Skeleton_Parameters_Micro.md`, so the Phase 3 box dimensions link straight to it:
>
> | Global | Starter value | Meaning |
> |---|---|---|
> | `"servo_L"` | `23` | servo body length, chordwise ($Z$) [mm] |
> | `"servo_W"` | `12` | servo body width, spanwise ($X$) [mm] |
> | `"servo_H"` | `22` | servo body height, vertical ($Y$) [mm] |
>
> All MMGS millimetre values; the Phase 3 box dimensions reference them directly (`= "servo_L"`, and so on).

**7.7.1 — Phase 1: Spanwise control stations (already drawn in `LAY_Wing_Incidence`).** The four station points live in the merged wing sketch (§7.2 Phase B, Step 7), dimensioned in-plane from the Origin as `= "y_ail_in_proj"`, `= "y_ail_out_proj"`, `= "y_flap_in_proj"` and `= "y_flap_out_proj"` and each **Coincident** to the main spar line. Nothing new to sketch here — promote them to reference points.
1. Expand `2_LAYOUT_SKETCHES` and right-click `LAY_Wing_Incidence` ▸ **Show** so the four vertices are selectable.
2. **Promote to reference points (`5_POINTS`).** For each of the four vertices: **Insert ▸ Reference Geometry ▸ Point**, click the sketch vertex, green-check, **F2**, and rename `PT_Ail_Inboard`, `PT_Ail_Outboard`, `PT_Flap_Inboard`, `PT_Flap_Outboard`.
   > **Port-side masters, mirror downstream.** These live on the port ($+X$) panel only. The starboard surfaces are the Right-Plane mirror; downstream aileron/flap parts either mirror the derived component or re-derive from the mirrored geometry.
   > **They already carry dihedral.** Because the stations sit on `PLN_Dihedral` rather than the Top Plane, each promoted point is already at its true $Y = X\tan\Gamma$ height — no lifting step, and no chance of a control station disagreeing with its own hinge axis.

**7.7.2 — Phase 2: True 3-D hinge axes (`AX_Hinge_Ail` / `AX_Hinge_Flap`).**
> **Why the hinge rides `PLN_Dihedral`.** The hinge is the *physical rotation axis* of the surface — every point of the moving flap swings on one straight line. The Micro wing carries **dihedral** (the tip rides $\approx 38$ mm up at $Y = b_{semi}\tan(dihedral)$), so the 75 %-chord seam climbs in $+Y$ as it runs outboard; a flat Top-Plane line stays at $Y = 0$ and misses it, binding inboard and gapping outboard through the throw. Because the hinge sits at the **same dihedral tilt as the spar**, it lives on the very same structural datum plane `PLN_Dihedral` (§7.2) — draw it there and the dihedral $Y$-rise comes straight from the plane, with **no 3-D bridging sketch and no relation to the front-view dihedral line**.

* **Step 1 — the hinge lines are already drawn.** Both hinge lines were built in the merged wing sketch (§7.2 Phase B, Step 8): the aileron hinge dimensioned `= "y_ail_in_proj"` / `= "y_ail_out_proj"` spanwise and `= "x_hinge_ail_in"` / `= "x_hinge_ail_out"` to the Front Plane, and the flap hinge `= "y_flap_in_proj"` / `= "y_flap_out_proj"` and `= "x_hinge_flap_in"` / `= "x_hinge_flap_out"`. Right-click `LAY_Wing_Incidence` ▸ **Show** so the two construction lines are selectable, then continue at Step 2.
  > **Washout-exact refinement (optional).** `PLN_Dihedral` captures dihedral but not the `twist_tip` rotation of the outboard section. For a hinge that also follows washout, **Pierce** each endpoint to `SURF_Wing_OML` at the local hinge %-chord instead of dimensioning it in-plane. At `twist_tip` = 0 the two are identical.

* **Step 2 — promote to axes (`4_AXES`).**
  1. **Insert ▸ Reference Geometry ▸ Axis**, **One Line/Edge/Axis**, click the **aileron** hinge line inside `LAY_Wing_Incidence`, green-check, **F2** → `AX_Hinge_Ail`.
  2. Repeat on the **flap** hinge line → `AX_Hinge_Flap`. Drag both into `4_AXES` (§7.2).
  > **Success state:** two named axes, each a straight 3-D line rising with dihedral — they lie on `PLN_Dihedral`, so the $\Delta Y / \Delta X = \tan(dihedral)$ check in §13.3.6 passes by construction — ready as the pivot datum for the downstream split (Phase 4) and for the hinge mate in the assembly.

**7.7.3 — Servo packaging (moved to Installation).** Servo keep-out envelopes and the skin-breach audit are **component installation**, not published skeleton geometry — they live in the **Installation guide** (§I-1). The skeleton publishes what that installation consumes: the hinge axes `AX_Hinge_Ail` / `AX_Hinge_Flap` (§7.7.2) and `SURF_Wing_OML` (§8.4).

**7.7.4 — Phase 4: Downstream rib split & trailing-edge consumption.** How a structures engineer turns the kinematic datums into a real, severed control-surface rib — via **Insert Part** (derived), never in-context (§9.1).
1. **New part.** **File ▸ New ▸ Part ▸ OK**; **File ▸ Save As** to `Z:\SAE_Micro_2026\02_Parts\`, name it exactly `Aileron_Rib_R05.SLDPRT`.
2. **Insert the skeleton.** **Insert ▸ Part…**, select `AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`, **Open**. In the **Insert Part PropertyManager**, under **Transfer** check **Surface bodies** (`SURF_Wing_OML`), **Axes** (`AX_Hinge_Ail`), and **Planes** (the local rib station). **Critical:** leave **"Locate part with Move/Copy Feature" UNCHECKED** so the part derives at the coincident origin (§9.1).
3. **Capture the full rib section.** Click the local rib plane (e.g. `PLN_RibStn_R05`) ▸ **Sketch** ▸ **`Ctrl + 8`**. Run **Tools ▸ Sketch Tools ▸ Intersection Curve**, click `SURF_Wing_OML`, green-check — the exact 2-D airfoil at that station, carrying true local twist and taper (§8.7 Workflow 1).
4. **Project the hinge as the split line.** Still in the sketch, **Convert Entities** on `AX_Hinge_Ail` (or drop a point where the hinge axis pierces this plane) to bring the pivot onto the sketch. Draw a short construction line through that pierce point, **Perpendicular** to the local chord — this is the hinge cut at 75 % chord.
5. **Sever the trailing-edge segment.** Use the hinge cut line to divide the airfoil loop into two closed profiles:
   - **Forward ($+Z$)** of the hinge → the **fixed main-rib** segment.
   - **Aft ($-Z$)** of the hinge → the **pivoting aileron-rib** segment.
   Trim the loop at the two hinge intersections (**Sketch ▸ Trim Entities**), or use **Insert ▸ Curve ▸ Split Line** with `SURF_Wing_OML` to split the surface itself along the hinge for a surface deliverable.
6. **Extrude each rib.** Select the aft profile ▸ **Extruded Boss/Base** ▸ **Mid Plane** ▸ depth `= "rib_thk"`; repeat for the forward profile (or spin it off to its own part). The aft rib now pivots about `AX_Hinge_Ail` — bring both into the top assembly and add a **hinge / concentric** mate on that axis for the control-throw study.
   > **Why derive, not in-context.** The rib reads `AX_Hinge_Ail` and `SURF_Wing_OML` one-way from the skeleton (§9.5 golden rule). Flex `dihedral`, `c_ail_pct`, or `ail_out_pct` in the master and the hinge axis, the OML, and this severed rib all re-solve together — the seam never drifts.

**7.8 — Dynamic Payloads and CG Shift Management.** This section adds the water-payload *mass model* to the skeleton as body-free reference geometry: a live three-state CG travel band (loaded → drained → empty). The container itself is **not modeled** — the water is carried as mass at `x_bay` only. The belly drop-door swing envelope is Installation-scoped (§I-2).

> **Globals — the weight and door-mechanism sets already exist.** Phase 3 rides `x_CG`, `W_TO`, `W_water`, `W_empty` = 1100, `W_container` = 120, `x_bay` = 60, `x_NP` = 95, `MAC`, `SM_min` / `SM_max` (all existing). Note `x_bay` is now a **mass-bookkeeping station only** — the water is carried as mass, never as modeled geometry. The **drop-door mechanism block** is likewise in `skeleton_equations_micro.txt`, mirrored into Appendix A of `Aircraft_Skeleton_Parameters_Micro.md`:
>
> | Global | Starter value | Meaning |
> |---|---|---|
> | `"hatch_open_deg"` | `75` | max drop-door open angle from closed [deg] |
> | `"horn_R"` | `12` | servo output-horn radius [mm] |
> | `"link_L"` | `30` | actuation push-link length [mm] |
>
> All MMGS; store the angle in **degrees** and convert with `* pi/180` only inside any trig expression (§14 item 5).

**7.8.1 — Payload drop-door kinematics (moved to Installation).** The door swing envelope and hatch pivot are **mechanism kinematics** → **Installation guide** (§I-2). The skeleton publishes the three-state CG markers (§7.8.3) the mechanism references; no payload container or bay interface geometry is published, so the mechanism engineer sets the door aperture against the OML directly.

**7.8.3 — Phase 3: Multi-configuration CG trajectory tracking.** Lay three centerline points whose stations are computed live from the weight globals, so the CG walks visibly as the water drains.
1. Expand `2_LAYOUT_SKETCHES`, right-click `LAY_Wing_Plan` ▸ **Edit Sketch** (**`Ctrl + 8`**) — the CG band is still on the Top Plane (§5.6). You will dimension all three points along the fuselage centerline ($X = 0$), aft distance from the Origin along $Z$ — the same convention as the §5.6 CG band.
2. **Loaded CG (`PT_CG_loaded`).** Drop a **Point** on the centerline; **Smart Dimension** its $Z$ from the Origin → `= "x_CG"` (the full-water design target; this coincides with the existing `PT_CG_target`, §7.1 — reuse that point instead if you prefer a single loaded marker).
3. **Drained CG (`PT_CG_drained`).** Drop a second centerline point; **Smart Dimension** its $Z$ → the moment balance after the water leaves (container stays aboard):
   `= "x_CG_drained"`
4. **Empty CG (`PT_CG_empty`).** Drop a third centerline point; **Smart Dimension** its $Z$ → the dry-structure balance (water **and** container removed):
   `= "x_CG_empty"`
   > **The moment balance.** Removing a mass $m$ sitting at `x_bay` from a total $W_{TO}$ at `x_CG` moves the CG to $(W_{TO}\,x_{CG} - m\,x_{bay})/(W_{TO}-m)$. Drained subtracts `W_water`; empty subtracts `W_water + W_container`. This assumes **both** the water and the container centroid at `x_bay`. If your empty container drops *with* the water, `PT_CG_drained` and `PT_CG_empty` coincide — delete one; if the container centroid differs from the bay centre, swap `x_bay` for that station in the empty expression. Every term is an existing global, so nothing is added to the equations file.
5. Exit the sketch. **Promote all three** to reference points: **Insert ▸ Reference Geometry ▸ Point** on each vertex, rename `PT_CG_loaded`, `PT_CG_drained`, `PT_CG_empty`, and drag them into **`5_POINTS`** beside `PT_CG_target` / `PT_CG_fwd` / `PT_CG_aft`.
   > **They move on their own.** Because each station is an *expression* of `W_water` / `W_TO` / `x_CG` (and friends), flexing the payload — or switching a §11 configuration that recomputes `W_water` — re-solves all three markers instantly. No manual re-dimensioning, no per-config edits.
6. **Assembly audit of the travel band.** In the top **assembly** (§11), with the real parts loaded:
   - For each of the `Loaded`, `Drained`, and `Empty` configurations: **Tools ▸ Evaluate ▸ Mass Properties**, read the reported **centre-of-mass $Z$** (the aft-distance coordinate).
   - Confirm each actual CG lands on (or near) its matching `PT_CG_loaded` / `_drained` / `_empty` marker, and that **all three fall between `PT_CG_fwd` and `PT_CG_aft`**.
   - Back-check the static margin for each state: $SM = (x_{NP} - x_{CG,\,state}) / MAC$ must stay inside $[SM_{min}, SM_{max}]$ (0.08–0.15).
   > **Skeleton targets vs. real CG.** These markers are *computed targets* on a body-free skeleton (§11); the authoritative CG is the assembly Mass-Properties reading. The audit is confirming the real parts land where the skeleton predicts.

**7.9 — Landing-gear installation (moved to Installation).** Wheel envelopes, the impact-deflection arc, the tailwheel, and the steering linkage are **component installation** → **Installation guide** (§I-3). The skeleton already publishes the gear datums that installation consumes: `AX_GearAxle` and `AX_Thrust` (§7.2), the master **Ground Line** (§6.7), and the `track` / `x_main` / `x_aux` stance globals.

**7.10 — Wing-to-Fuselage Interface & Mounting Planes.** This section builds the structural shelf where the wing cross-beams bolt to the fuselage crown / internal longerons — a horizontal seat plane, two vertical shear-tie faces, and a parametric bolt pattern, all body-free reference geometry on the same $+Z$ forward / $+Y$ up / $+X$ port frame, symmetric about the Right Plane. Budget ~20 minutes.

> **Globals.** The seat and bolt pattern ride four dedicated entries, already in `skeleton_equations_micro.txt` and mirrored into Appendix A of `Aircraft_Skeleton_Parameters_Micro.md`:
>
> | Global | Starter value | Meaning |
> |---|---|---|
> | `"h_wing_seat"` | `20` | wing-seat structural-deck height above the waterline ($+Y$) [mm] |
> | `"w_wing_seat"` | `90` | lateral spacing of the port / starboard shear-tie faces [mm] |
> | `"bolt_pitch"` | `30` | wing-mount bolt-hole spacing along the seat [mm] |
> | `"bolt_dia"` | `5` | wing-mount bolt-hole diameter [mm] |
>
> All MMGS; existing spar globals `x_spar_root` and `x_rspar_root` are reused as-is.

* **Horizontal seat plane (`PLN_Wing_Seat_H`).**
  1. **Insert ▸ Reference Geometry ▸ Plane**; **First Reference** = the default **Top Plane**; constraint **Offset Distance** $(\rightarrow|)$; type `= "h_wing_seat"` ▸ **Enter**.
  2. Watch the preview: if it drops below the waterline, tick **Flip** so it offsets **up ($+Y$)** onto the deck. Green-check, **F2** → `PLN_Wing_Seat_H`.
     > This is the fuselage structural deck the wing beams land on. Because it rides `h_wing_seat`, raising or lowering the deck re-seats the whole mount stack with no rework.
* **Vertical shear-tie planes (`PLN_Wing_Seat_V_Port` / `_Starboard`).**
  1. **Insert ▸ Reference Geometry ▸ Plane**; **First Reference** = the default **Right Plane**; **Offset Distance** `= "w_wing_seat_half"` (= 45 mm).
  2. **Flip** so it previews to **port ($+X$)**. Green-check, **F2** → `PLN_Wing_Seat_V_Port`.
  3. Repeat with the same `= "w_wing_seat_half"` offset, **Flip**ped to **starboard ($-X$)**. Rename `PLN_Wing_Seat_V_Starboard`.
     > These are the inner mounting faces for the aluminum shear ties / carbon structural angles — the Right-Plane mirror of each other, `w_wing_seat` apart. Resize the tie spacing in one global and both faces track.
* **Interface alignment sketch (`LAY_Wing_Mounts`).**
  0. **Prerequisite — a rear-spar axis.** `AX_MainSpar` already exists (§7.2), but the **rear** spar is only a construction line so far (§5). Promote it now: **Insert ▸ Reference Geometry ▸ Axis** ▸ **One Line/Edge/Axis** ▸ click the rear-spar construction line ▸ **F2** → `AX_Rspar`; drop it in `4_AXES`. *(Skip if you already built it, or pierce the rear-spar line directly in step 3.)*
  1. Click `PLN_Wing_Seat_H` ▸ **Sketch**; **`Ctrl + 8`**.
  2. Select the **Point** tool, drop a point, then **`Ctrl`**-select the point **and** `AX_MainSpar` ▸ **Pierce** — this lands the forward bolt row exactly where the main spar crosses the seat.
  3. Repeat: drop a point and **Pierce** it onto `AX_Rspar` — the aft bolt row.
  4. **Bolt circles.** Draw a **Circle** on each pierce point; **Smart Dimension** each diameter → `= "bolt_dia"`. Select a circle ▸ **Linear Sketch Pattern**, **Direction** = the seat's spanwise ($+X$) edge, **Spacing** `= "bolt_pitch"`, instance count to suit the beam; repeat for the aft row.
  5. **Mirror** the whole port pattern across the **Right Plane** for the starboard beam. **F2** → `LAY_Wing_Mounts`; file in `2_LAYOUT_SKETCHES`.
     > **Body-free.** The bolt circles stay **sketch profiles** — do **not** cut them here (that would need a solid). Downstream, the wing-mount part **Insert-Parts** the skeleton and consumes `PLN_Wing_Seat_H` / `_V_*` and `LAY_Wing_Mounts` to drill the real holes (§9.1); the skeleton stays at **0.00 g** (§13.8).

**7.11 — Primary Bulkhead & Load-Distribution Slicing Stations.** Multi-mission airframes need rigid internal formers to bridge point loads across the OML. This builds two high-load **transverse** slicing planes (each normal to the longitudinal axis, i.e. parallel to the Front Plane) on the wing structural datums. Both ride root-chord globals, so a span flex never walks them.

* **Forward spar / main landing-gear bulkhead (`PLN_Bhd_Main`).**
  1. **Insert ▸ Reference Geometry ▸ Plane**; **First Reference** = `AX_Long` (the §2.3 centerline) with constraint **Perpendicular**; **Second Reference** = a point at the main-spar-root station — drop / pierce a point at `= "x_spar_root"` (= `spar_main_pct` $\times$ `c_root`) along `AX_Long`. Green-check, **F2** → `PLN_Bhd_Main`. *(Equivalent shortcut: **Offset** the **Front Plane** aft ($-Z$) by `= "x_spar_root"`.)*
  2. **Handle the spar / gear longitudinal offset.** The main spar root sits at `x_spar_root` (≈ 75 mm-aft with the starter chord) while `AX_GearAxle` sits at `x_main` (= 40 mm-aft) — **~35 mm apart**, so a single transverse plane *cannot* pass through both. Build `PLN_Bhd_Main` on the structurally dominant datum (the **spar root** / wing carry-through), then **Measure** `PLN_Bhd_Main` → `AX_GearAxle` along $Z$ and treat that gap as a **driven check**, not a second constraint. If the gap exceeds your frame width, either **co-locate the gear** (set `x_main = x_spar_root` so both share one frame) or add a short longeron / local doubler bridging the two stations — never force one plane onto two offset features.
* **Aft spar / tie-down bulkhead (`PLN_Bhd_Aft`).**
  1. **Insert ▸ Reference Geometry ▸ Plane**; **First Reference** = `AX_Long` ▸ **Perpendicular**; **Second Reference** = a point at `= "x_rspar_root"` (= `spar_rear_pct` $\times$ `c_root`) along `AX_Long`. Green-check, **F2** → `PLN_Bhd_Aft`. *(Equivalent: **Offset** the **Front Plane** aft by `= "x_rspar_root"`.)*
     > This caps the aft end of the wing torque box; with both `PLN_Bhd_Main` and `PLN_Bhd_Aft` in place, the main + rear spar carry-through loads land on dedicated former datums.

**7.12 — Structural-datum tree organization & hygiene.** Keep the new datums grouped and verified.
1. **`Ctrl`**-select the five new planes — `PLN_Wing_Seat_H`, `PLN_Wing_Seat_V_Port`, `PLN_Wing_Seat_V_Starboard`, `PLN_Bhd_Main`, `PLN_Bhd_Aft` — **right-click ▸ Add to New Folder** ▸ name it **`3C_STRUCTURAL_DATUMS`**.
   > **Folder-name note.** A `3C_TAIL_PLANES` folder already exists (§7.3.7), so you now have two `3C_` folders. That is harmless (folder names are just labels), but if you prefer strict ordering rename this one `3D_STRUCTURAL_DATUMS` — the walkthrough works either way.
2. Confirm `AX_Rspar` landed in `4_AXES` and `LAY_Wing_Mounts` in `2_LAYOUT_SKETCHES`, with no default `Plane#` / `Axis#` names left behind (§7.5).
3. Run the **§13.3.7** structural-datum rebuild check before sign-off — it forces a rebuild after a span / gear flex and confirms the planes re-align with no dangling references and zero mass.

**7.13 — Systems clearance & linkage studies (moved to Installation).** The top fill-hole clearance vector, the belly plumbing-clearance overlay, and the ground-steering linkage sweep are **clearance / mechanism studies** → **Installation guide** (§I-4 – §I-6). They *reference* published skeleton geometry (the `PLN_Fuse_*` stations, the keel, `AX_Tail_Steer`, the battery interface planes) but publish nothing themselves.

---

## 8. (Optional / advanced) Master OML surfaces

This is the one **optional** section — skip it for a stick-and-tissue balsa build; do it for foam-core composite wings, printed plugs/molds, or any time you want a true outer-mold-line master. Note: **surfaces are reference geometry and carry no mass**, so adding them does *not* break the body-free rule (§13) — only *solid* bodies do. Micro's empty-weight penalty pushes many teams toward composite, where this pays off. Budget ~45 minutes; the airfoil import is the only real friction. You need only **two** airfoil sections (root + tip) — intermediate ribs come from intersecting the lofted surface.

**8.1 — Freeze the airfoil and get coordinates (data sourcing & splicing).** Before importing geometry into SolidWorks, you must source and clean your airfoil coordinates. SolidWorks requires coordinate points to follow a **continuous sequence around the perimeter** of the profile. If the points are out of order, the software generates a chaotic, self-intersecting zigzag instead of a smooth wing profile. Using the standard **Selig format** ensures the points flow sequentially.

**Step 1 — search and select the airfoil on AirfoilTools.**
1. Open your web browser and navigate to **airfoiltools.com**.
2. Locate the **Search** box in the top-right corner of the homepage.
3. Type the name of your team's chosen airfoil (e.g., `S1223` or `FX 63-137`) and press **Enter**.
4. From the search results list, locate the exact profile variant required and click the blue **Details** link next to its name.

**Step 2 — access the raw Selig DAT file.**
1. On the airfoil's dedicated data page, look directly below the geometry preview plot at the top.
2. Locate the row of text links and click the one explicitly labeled **Selig format DAT file**.
3. A plain-text webpage opens displaying a header line followed by two columns of numeric coordinates running from the trailing edge, over the upper surface to the leading edge, and back along the lower surface to the trailing edge.

**Step 3 — save the data to the project repository.**
1. Right-click anywhere on the plain-text coordinate page and select **Save as…** (or press **`Ctrl + S`**).
2. In the file-browser pop-up, navigate directly to your shared project repository: `Z:\SAE_Micro_2026\05_Sizing\`.
3. Name the file clearly to reflect the profile, such as `s1223_coords_raw.txt`.
4. Ensure the **Save as type** dropdown is set to **Text Document (*.txt)** or **All Files (*.*)** so Windows does not append hidden formatting extensions. Click **Save**.

**Step 4 — audit and format the coordinate loop.** Open the saved file in **Notepad** (or a plain-text editor) and perform a structural "loop check" to guarantee a clean import:
1. **Line 1 (the header line):** verify that the very first line contains *only* text describing the airfoil name — SolidWorks uses this row as a non-numeric label. If there are stray numbers or blank spaces on line 1, delete them.
2. **Upper-surface stream (trailing edge to nose):** look at the first block of numbers. The first coordinate pair represents the trailing edge (TE) and should read `1.000000  0.000000` — **exactly**, if you will build Method A curves (see *Trailing-edge closure* in the checklist below). Scrolling down row by row, the first-column $X$ values must **steadily decrease** from $1.0$ toward $0.0$.
3. **Leading-edge intercept:** locate the exact row where the first column hits `0.000000` (or its absolute lowest value). This is the frontmost apex of your profile, the leading edge (LE).
4. **Lower-surface stream (nose back to tail):** scroll past the LE point. The first-column values must now **steadily increase** from $0.0$ back toward $1.0$. The final line of data must land back at the trailing edge (`1.000000  0.000000`), completing the loop — and for a sharp TE this **final row must be identical to the first row**, or a Method A curve will not close (see the *Trailing-edge closure* checklist item and §8.3 Path 1).

**Data-sourcing & clean-up checklist.** Before using this coordinate file to drive any 3D curves or import macros, verify the data against this checklist:
- [ ] **No duplicate LE points (within a single stream):** inside any one continuous stream there must be only **one** row at the LE apex ($X = 0.0$, or its minimum). If the upper surface ends at `0.0000  0.0000` and the next row repeats it, delete one to prevent rebuild lock-ups. *(The split below deliberately repeats the LE apex once as the **boundary** of the Upper and Lower streams — that shared anchor is intentional, not an adjacent duplicate.)*
- [ ] **Trailing-edge closure (exact for Method A):** the **first** and **last** data rows are both the TE. For a sharp TE they must be the *identical* point — snap both to exactly `1.000000  0.000000`. A file that is only *"very close"* (e.g. `1.000000 0.00009` upper vs `1.000000 -0.00003` lower) hides a micro-gap: Method B's fit-spline import seals it with **Merge points closer than 0.05 mm** (§8.2), but **Method A / Path 1** (Curve Through XYZ Points) has no merge step, so a non-coincident TE yields an **open curve** — a visible fork at the tail (§8.3, Path 1). Force first = last before exporting.
- [ ] **Split into Upper + Lower streams (Method A → split-curve loft):** the 3D-rail loft (§8.4) imports each airfoil as **two** curves, so slice the continuous loop at the LE apex into an **Upper stream** (starting **TE** row → **LE apex** row, $X$ decreasing $1 \to 0$) and a **Lower stream** (**LE apex** row → terminating **TE** row, $X$ increasing $0 \to 1$). The **LE apex row must appear in *both* streams** — it is the shared boundary anchor that welds the two curves at the nose with zero gap; both streams also start/terminate on the identical closed **TE** point (`1.000000  0.000000`). This is what turns the LE and TE into explicit, selectable **3D vertices** (§8.3) for the guide rails.
- [ ] **Strict two-column space delimitation:** ensure the file contains exactly two columns of numeric data separated cleanly by spaces or tabs. Strip out all commas, semicolons, text notes, or trailing blank rows at the bottom of the document.
- [ ] **Normalized verification:** confirm that all first-column values fall strictly within $0.0000$ to $1.0000$. This confirms the dataset is normalized to a **unit chord** (scale factor of $1$), letting you parametrically scale it up to your actual `"c_root"` and `"c_tip"` equations later.

**8.2 — Bring the airfoil in (step-by-step import workflows).** Depending on your design-optimization loop, choose one of the three verified import methods below to bring your cleaned dataset into SolidWorks.

**Method A — Curve Through XYZ Points (the spreadsheet pipeline).** This method processes normalized coordinates in Excel to handle 3D position, incidence angle, twist, sweep, and dihedral *before* sending data to SolidWorks. Because it reads raw text columns, it generates a perfectly smooth, unconstrained 3D reference curve feature.

**Step 1 — set up your Excel calculation engine.** Open a new Excel spreadsheet and paste your normalized coordinate pairs ($x_{norm}$, $y_{norm}$) into **Column A** and **Column B**, starting on Row 3. In Row 1, define your master scalar constants matching your skeleton parameters:
- Cell `E1`: target chord length (e.g., `300` for root, or `180` for tip).
- Cell `F1`: incidence/twist angle in degrees (e.g., `"i_wing"` or `"i_wing + twist_tip"`).
- Cell `G1`: semi-span distance (set to `0` for the root profile; set to your true `"b_semi"` value for the tip profile).
- Cell `H1`: leading-edge sweep angle (`"sweep_LE"`).
- Cell `I1`: dihedral angle (`"dihedral"`).

**Step 2 — apply the geometric transformation formulas.** To align with the aircraft coordinate system ($+Z$ forward, $+Y$ up, $+X$ port), configure three calculation columns in Excel:
1. **Column C (SolidWorks X — spanwise position):** in cell `C3`, enter `=$G$1`. Drag this formula down to match all coordinate rows.
2. **Column D (SolidWorks Y — thickness, dihedral & pitch rotation):** to rotate coordinates around the quarter-chord point ($x_{norm} = 0.25$), re-anchor the **leading edge** to $Y = 0$, and add the vertical dihedral lift, enter this formula in cell `D3`:
   `=(( -A3 - (-0.25) ) * SIN(RADIANS($F$1)) + (B3 - 0) * COS(RADIANS($F$1)) - 0.25 * SIN(RADIANS($F$1))) * $E$1 + ($G$1 * TAN(RADIANS($I$1)))`
   > **LE-anchor term.** The trailing `- 0.25 * SIN(RADIANS($F$1))` is the vertical mirror of the `+(-0.25)` shift in Column E: it cancels the upward swing the incidence rotation would otherwise give the LE. Without it the section rotates about the quarter-chord but stays pinned to the waterline *at the quarter-chord*, so the LE floats up by $0.25\,c\sin(i)$ ($\approx 2.6$ mm at the root) and no longer coincides with the Origin. With it, the root LE lands on $(0,0,0)$ and the tip LE on the dihedral line — consistent with the *origin = wing-root LE* convention (§2) and the §4.4 chord reference. The tip is unaffected either way, since its net incidence $i\_wing + twist\_tip = 0$.
3. **Column E (SolidWorks Z — chordwise, incidence rotation & sweep taper):** to handle chordwise position, trailing-edge rake, and backward sweep, enter this formula in cell `E3`:
   `=(( -A3 - (-0.25) ) * COS(RADIANS($F$1)) - (B3 - 0) * SIN(RADIANS($F$1)) + (-0.25)) * $E$1 - ($G$1 * TAN(RADIANS($H$1)))`
Drag all three formulas down to the final row of coordinate data. The transform is identical for every point, so **the same `C`/`D`/`E` columns serve both the Upper and Lower streams** — you split the airfoil at *export* (Step 3), not with different formulas.

**Step 3 — export the four coordinate streams.** You export the *same* computed `C`/`D`/`E` columns in two slices per airfoil, split at the LE apex row (the row where Column A reads `0` — its minimum). Both slices **include** that LE row.
1. **Root — Upper stream.** On the root sheet, select **Columns C, D, E from the starting TE row down through the LE apex row** (no headers). Copy (**`Ctrl + C`**), paste into a clean **Notepad** window (tab-delimited), and **File ▸ Save As** to `Z:\SAE_Micro_2026\05_Sizing\airfoil_root_upper_xyz.txt`, encoding **UTF-8**.
2. **Root — Lower stream.** Back on the root sheet, select **Columns C, D, E from the LE apex row down through the final TE row** — the **LE apex row is included again** as the shared boundary anchor. Copy, paste into Notepad, save as `airfoil_root_lower_xyz.txt`.
3. **Tip — Upper / Lower streams.** Repeat both slices on the tip sheet, saving `airfoil_tip_upper_xyz.txt` (TE → LE) and `airfoil_tip_lower_xyz.txt` (LE → TE).
   > **Four files, one LE row shared per airfoil.** Each upper file *ends* on the exact LE point its lower file *begins* on, and both start/end on the identical closed TE point. That double coincidence is what welds the imported curves into selectable nose and tail vertices (§8.3) — never trim the shared rows to "de-duplicate."

**Step 4 — import the four curves into SolidWorks.**
1. Click **Insert ▸ Curve ▸ Curve Through XYZ Points**. Click **Browse**, set the filter to **Text Files (*.txt)**, select `airfoil_root_upper_xyz.txt`, click **Open**, then **OK**.
2. Select the new curve, press **F2**, and rename it exactly `CRV_Airfoil_Root_Upper`.
3. Repeat for the other three files, renaming each curve to match: `CRV_Airfoil_Root_Lower`, `CRV_Airfoil_Tip_Upper`, `CRV_Airfoil_Tip_Lower`.
   > **Result — a paired curve network.** Each airfoil is now two open curves that physically meet at the LE and TE. Because they share exact endpoints there, SolidWorks exposes clean, snappable **3D vertices** at every nose and tail — the anchors the §8.4 guide rails weld to.

---

**Method B — Airfoil-import macro (the dynamic spline).** This is the most highly parametric option. Running an import macro drops a flexible spline directly onto an open sketch plane, allowing you to tie its sizing dimensions directly to your global design equations.

**Step 1 — open your destination sketch plane.**
1. In the FeatureManager design tree, click once on the plane where the airfoil profile will live (e.g., select the default **Right Plane** for your root section, or your custom station plane `PLN_RibStn_R01`).
2. Click the **Sketch** icon from the pop-up context toolbar to open an active sketch.

**Step 2 — initialize and run the macro engine.**
1. Go to the top main menu bar and select **Tools ▸ Macro ▸ Run…**
2. In the file browser, navigate to your saved engineering-utilities folder, select your macro file (e.g., `Geometry_Airfoil_Importer.swp`), and click **Open**.
3. In the macro interface pop-up, click **Browse**, select your clean Selig-format coordinate text file (`s1223_coords_raw.txt`), and click **Open**.
4. In the configuration options area, check the radio button for **Spline** (do not select lines/arcs) and verify that the target scale factor is set to `1.0`.
5. Click the **Import** button to trace a smooth, closed spline directly onto your open sketch plane. Close the macro window.

**Step 3 — parametrically harden the imported spline.**
1. Select the **Centerline** tool from your Sketch tab.
2. Click directly on the absolute front nose point of the spline (the leading-edge vertex), drag the cursor straight aft horizontally, and click on the sharp tail intersection point (the trailing-edge vertex). Press **`Esc`**.
3. Click this new centerline and add a **Horizontal** relation in the PropertyManager to lock the profile angle.
4. Select the **Smart Dimension** tool. Click the centerline, pull the text out, type `=`, and enter your global variable tracking parameter (`"c_root"` or `"c_tip"`) to lock down the scale.
5. Click the front leading-edge vertex point, hold **Ctrl**, select your master sketch **Origin**, and click **Coincident** to lock the wing-root placement in 3D space.
6. Exit the sketch and rename it to **`LAY_Airfoil_Profile_Root`** (or `LAY_Airfoil_Profile_Tip`).

---

**Method C — DXF import (the legacy vector path).** Use this method if your aero leads output pre-scaled, vector-based cross-sections straight out of aerodynamic-analysis software like XFOIL or Profili.

**Step 1 — initialize the vector import wizard.**
1. On the top main menu bar, click **File ▸ Open** (or press **`Ctrl + O`**).
2. Click the file-type drop-down filter in the bottom-right corner and change it from *SolidWorks Files* to **DXF (*.dxf)** or **DWG (*.dwg)**.
3. Select your airfoil profile vector file (e.g., `clarky_unit_chord.dxf`) and click **Open**.

**Step 2 — configure the import target layers.**
1. In the DXF/DWG Import Wizard dialog box under *Repository Target*, select the radio button labeled **Import to a new part as a:** and check the sub-box for **2D sketch**. Click **Next**.
2. Set the *Data Units* dropdown option to **Millimeters**.
3. Check the box for **Import data As Centerlines/Construction** if you want this profile to act purely as a reference layout, then click **Next**.
4. In the final panel, check the box labeled **Merge points closer than:** and set the value tolerance entry to `0.05 mm` to seal any tiny micro-gaps at the trailing-edge tip. Click **Finish**.

**Step 3 — extract and scale the profile inside the skeleton.**
1. Box-select the entire imported airfoil contour curve in the graphics window of the temporary file that opens and copy it to your clipboard (**`Ctrl + C`**). Close the temporary file.
2. Return to your master file `AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`.
3. Open an active sketch on your destination reference plane (e.g., click **Right Plane ▸ Edit Sketch**).
4. Paste the vector coordinates into the workspace (**`Ctrl + V`**).
5. Open your sketch toolbar panel, click the small arrow next to the *Move Entities* tool icon to expand its options, and select **Scale Entities**.
6. In the PropertyManager panel:
   - Click inside the **Entities to Scale** selection box and select all pasted airfoil lines.
   - Click inside the **Scale About** point box, then click the absolute front leading-edge vertex of your pasted profile.
   - In the **Scale Factor** box, type an equation string linking it to your master parameters (e.g., if it was a unit-chord 1 mm file, enter `= "c_root"` to expand the vector loop to its full aerodynamic scale).
7. Click the **Green Checkmark** $(\checkmark)$, exit the sketch canvas, and rename the file-tree item to **`LAY_Airfoil_DXF_Import`**.

**8.3 — Place the root and tip sections (3D alignment & constraints).** Because the intake mechanics split between 3D space curves and flat 2D sketch entities, choose the corresponding alignment path below to anchor your profiles.

**Path 1 — if you used Method A (spreadsheet XYZ curves).** Your Excel transform already baked in chord scaling, incidence, washout, dihedral lift, and sweep rake, so all four curves — `CRV_Airfoil_Root_Upper` / `_Lower` and `CRV_Airfoil_Tip_Upper` / `_Lower` — float in their exact spatial destinations with no manual sketches, moves, or mates. Crucially, because each airfoil's **upper and lower curves physically meet at the leading and trailing edges** (they share the identical LE and TE rows from §8.1/§8.2), SolidWorks automatically generates **explicit, perfectly selectable 3D vertices** at those master locations. Those endpoint vertices — not the un-snappable interior point of a single seamless spline — are what the §8.4 guide rails weld to, giving permanent endpoint stability.

> **Endpoint closure (Method A has no merge).** Curve Through XYZ Points joins points in list order with **no merge tolerance**, so a clean shared vertex forms only where two curves carry the *identical* endpoint. Both the **LE apex row** (repeated across each airfoil's Upper and Lower streams) and the closed **TE point** (`1.000000  0.000000`, first = last) must be exact — a merely *near* coincidence (e.g. `1.000000 0.00009` vs `1.000000 -0.00003`) leaves a micro-fork with no snappable vertex. Fix it at the data level in the Excel `A`/`B` columns (§8.1 split + closure items) and re-export. *(Method B's fit-spline import tolerates this via **Merge points closer than 0.05 mm**, §8.2 — Method A does not.)*

**Spatial alignment verification pass.**
1. Expand your `2_LAYOUT_SKETCHES` folder, right-click `LAY_Wing_Incidence`, and click **Show** (the open eyeball) — the wing tip station point lives there now. Right-click `LAY_Side_Profile` and click **Show**.
2. Press **`Ctrl + 7`** to switch to an isometric viewport.
3. **Verify the root nose vertex:** zoom into the master global Origin $(0,0,0)$. The shared **LE vertex** where `CRV_Airfoil_Root_Upper` and `CRV_Airfoil_Root_Lower` meet must sit exactly on the Origin.
4. **Verify the tip nose vertex:** zoom out to the port wingtip. The shared **LE vertex** of the two `CRV_Airfoil_Tip_*` curves must meet the outer tip station point in `LAY_Wing_Incidence` — which already sits at its true dihedral height, so there is nothing to lifted to the dihedral line at $Y = b_{semi}\tan(dihedral) \approx 38$ mm.
5. **Verify the TE vertices:** confirm each airfoil's upper/lower curves also close to a **single TE vertex** (no fork) at root and tip. If any nose or tail shows two separate endpoints, the shared row isn't exact — see the closure blockquote above.
6. *Troubleshooting:* if a curve floats off-target, the error is in your Excel cells, not SolidWorks. Re-verify your spreadsheet parameters against §8.2 Method A.

---

**Path 2 — if you used Method B or C (sketch-based splines/vectors).** If your airfoil is currently a flat, unconstrained sketch profile, you must explicitly bind it to the master layout framework using geometric relations across two separate sketches.

**Part 1 — set up the master tip plane (`PLN_Tip`).** If you did not already generate a dedicated tip station plane during the rib-array setup, build it now:
1. Click **Insert ▸ Reference Geometry ▸ Plane** from the top main menu.
2. Click inside the **First Reference** box, expand your flyout FeatureManager tree in the graphics area, and select the default **Right Plane**.
3. Under the constraint options, select **Offset Distance** $(\rightarrow|)$.
4. Delete any placeholder numbers in the distance box, type exactly `= "b_semi"`, and press **`Enter`**.
5. Click the **Green Checkmark** $(\checkmark)$. Rename the feature at the bottom of your tree to **`PLN_Tip`**.

**Part 2 — align the root airfoil profile (Right Plane).**
1. Click your default **Right Plane** once and click the **Sketch** icon from the pop-up context toolbar. Press **`Ctrl + 8`** to snap normal to the plane.
2. Paste your imported Method B/C spline contour into the workspace canvas (**`Ctrl + V`**).
3. Select the **Centerline** tool from the Sketch tab. Click directly on the frontmost nose apex of the airfoil (leading edge), drag straight aft horizontally, and click the sharp tail intersection (trailing edge). Press **`Esc`** to establish your root **chord line**.
4. Select the **Centerline** tool again. Click the master global **Origin**, drag your cursor straight aft horizontally along the $-Z$ axis, and click. Press **`Esc`**. Verify this reference line holds a **Horizontal** relation.
5. Select the **Smart Dimension** tool. Click your airfoil's **chord line**, then click the horizontal reference line. Pull the cursor into the wedge space between them, click to place, type `= "i_wing"`, and press **`Enter`** to lock root incidence.
6. Click the airfoil's **chord line** itself with **Smart Dimension**, drag clear, click to place, type `= "c_root"`, and press **`Enter`**.
7. Click the airfoil's front **leading-edge vertex**, hold the **`Ctrl`** key, select the master global **Origin** point, and click the **Coincident** relation in the PropertyManager.
8. Once the entire profile turns solid black, click the **Exit Sketch** icon in the confirmation corner, press **F2** on the sketch feature in your tree, and rename it to **`LAY_Airfoil_Placed_Root`**.

**Part 3 — align the tip airfoil profile (`PLN_Tip`).**
1. Right-click your `LAY_Wing_Incidence` sketch in the tree and ensure it is set to **Show** so the outer layout points are visible.
2. Click your custom **`PLN_Tip`** plane feature once and click the **Sketch** icon. Press **`Ctrl + 8`** to snap normal to the plane.
3. Paste your imported airfoil spline contour into the canvas (**`Ctrl + V`**).
4. Select the **Centerline** tool. Click the airfoil's front **leading-edge vertex**, drag straight aft horizontally, and click the sharp **trailing-edge point**. Press **`Esc`** to establish your tip **chord line**.
5. Select the **Centerline** tool again. Click the airfoil's **leading-edge vertex**, drag straight aft horizontally to drop a reference line, and press **`Esc`**. Verify this line holds a **Horizontal** relation.
6. Select the **Smart Dimension** tool. Click your tip **chord line**, click the flat horizontal reference line, pull clear, click to place, type `= "i_tip"`, and press **`Enter`** to lock aerodynamic washout.
7. Click the tip **chord line** with **Smart Dimension**, drag clear, type `= "c_tip"`, and press **`Enter`**.
8. **3D spatial constraints:** rotate your viewport slightly into a 3D isometric perspective. Click your airfoil's front **leading-edge vertex point**, hold down the **`Ctrl`** key, and click directly on the outer **tip leading-edge point** drawn in your underlying `LAY_Wing_Plan` sketch.
9. In the left-hand PropertyManager under *Add Relations*, click **Coincident** (or **Pierce** if a standard coincidence over-defines the plane's bounds). The profile will snap to its true 3D coordinates and turn solid black.
10. Click **Exit Sketch** in the confirmation corner, select the feature in your tree, press **F2**, and rename it to **`LAY_Airfoil_Placed_Tip`**.

**8.4 — Loft the wing OML (surface generation via 3D guide rails).** This step bridges your root and tip airfoil sections into a continuous, zero-thickness outer mold line (OML) skin. The Micro wing carries both **dihedral** (tip lifted to $Y = b_{semi}\tan(dihedral) \approx 38$ mm) and **washout** (tip rotated by `twist_tip`), so the tip section floats *above and rotated off* the Top Plane — while the leading-edge, spar, and trailing-edge lines inside `LAY_Wing_Plan` lie flat on $Y = 0$. SolidWorks enforces a hard rule: **every guide curve must pierce every profile it guides.** The flat 2D lines touch the root at the Origin but pass *underneath* the elevated tip, so they can never guide this loft. The fix is to build dedicated **3D rails** that span root-to-tip through true space — welded to the explicit LE/TE **vertices** exposed by the split upper/lower curves (§8.2) — and guide the loft with those.

> **Why the flat planform lines fail here (the breakdown you hit).** A guide curve is legal only if it intersects **every** profile. The $Y = 0$ LE/TE lines satisfy that at the root (on the waterline) but miss the tip, which dihedral raises $\approx 38$ mm and washout tilts. And a rail drawn "dot-to-dot" onto a *single closed* airfoil spline has nothing to grab at the nose — a seamless curve carries no vertex there. Splitting each airfoil into upper + lower curves (§8.2) cures both: the curves meet at genuine LE/TE **endpoints**, so the rails weld to hard vertices that never dangle.

**Prerequisites — expose your split profiles.**
1. Confirm all four airfoil curves are **Shown**: `CRV_Airfoil_Root_Upper` / `_Lower` and `CRV_Airfoil_Tip_Upper` / `_Lower` (Method A). *(Method B / Path 2 users have single closed contours instead — `LAY_Airfoil_Placed_Root` / `_Tip`; their sketches already carry explicit LE/TE vertices, so the rails below weld to those and you loft the two closed profiles in a **single** loft — see the Path 2 note at Step 2.)*
2. Expand `2_LAYOUT_SKETCHES`, right-click `LAY_Wing_Incidence`, and click **Show** — kept visible only as a *planform reference*, no longer as a guide-curve source.
3. Press **`Ctrl + 7`** for an isometric view.

**Step 1 — build the 3D guide rails (`LAY_Wing_Guides_3D`).** These are the physical bridges the loft follows from root to tip. Because the split curves meet at hard vertices, this is a clean dot-to-dot — no pierce workaround, no reference points.
1. On the **Sketch** tab, click the **3D Sketch** icon to open a new 3D sketch. Rename it `LAY_Wing_Guides_3D` (**F2**).
2. **3D leading-edge rail.** Select the solid **Line** tool. Hover the **nose vertex** where `CRV_Airfoil_Root_Upper` and `_Lower` meet until the endpoint snap highlights, and **click**; draw straight outboard to the **nose vertex** where the two `CRV_Airfoil_Tip_*` curves meet, and **click**. Press **`Esc`**. The line snaps endpoint-to-endpoint and turns **black (Fully Defined) immediately** — both ends are bounded by the pre-positioned curve vertices, so no dimension or extra relation is needed.
3. **3D trailing-edge rail.** Select the **Line** tool again. Click the **root TE vertex** (where the root upper/lower curves close), draw outboard to the **tip TE vertex**, and press **`Esc`**. It fully defines on contact, exactly like the LE rail.
4. Confirm both rails are **black**, **Exit** the 3D sketch, and drag `LAY_Wing_Guides_3D` into `2_LAYOUT_SKETCHES`.
   > **Endpoint stability — why this never dangles.** Each rail endpoint is welded to a real curve **vertex**, not a projected point or a mid-spline location. Swap or flex the master airfoil text files later and the curves rebuild, the vertices move with them, and the rails ride along — still solved, no `->x`. This is the payoff of splitting the sections in §8.1/§8.2. **Do not** add a *Parallel* / *Along Z* relation to the flat 2D `LAY_Wing_Plan` line: the rail rises with dihedral while that line stays flat, so a literal parallel relation would fight the dihedral or over-define the sketch — the two welded vertices already fully define each rail.

> **Why LE + TE only (no spar rail).** The OML skin is bounded by the leading and trailing edges; the main spar is *internal* structure, not a mold-line edge, so it never belonged in the OML loft's guide set. It still drives the rib planes and spar part (§7.2–§7.3) — it just isn't a surface boundary here.

**Step 2 — loft the upper skin (no SelectionManager).** With the sections split, you skin the top and bottom separately, then knit. Each profile is a single, directly-clickable curve — no open-loop isolation, no SelectionManager.
1. Click **Insert ▸ Surface ▸ Loft…** (or the **Lofted Surface** icon on the **Surfaces** tab).
2. With the **Profiles** field active, click `CRV_Airfoil_Root_Upper`, then `CRV_Airfoil_Tip_Upper` — each near its **leading-edge vertex** so the green connector handles anchor LE-to-LE.
3. **Connector audit:** if the preview twists or wraps the TE, drag a green dot onto the leading-edge vertex until it straightens.
4. Click inside the **Guide Curves** box, then in the graphics area click the **3D leading-edge rail** and the **3D trailing-edge rail** of `LAY_Wing_Guides_3D`. The preview snaps to the true 3D edges.
   > If a rail refuses to add ("guide curve does not intersect a profile"), its endpoint vertex isn't truly shared — re-check the LE/TE closure (§8.3).
5. Click the top **Green Checkmark** $(\checkmark)$. Rename the feature `SURF_Wing_OML_Upper`.
   > **Path 2 (Method B/C) — single loft instead.** Your placed profiles are single closed contours, so skip the upper/lower split: select `LAY_Airfoil_Placed_Root` then `_Tip` as the two **Profiles**, add the same two rails as **Guide Curves**, green-check, and rename straight to `SURF_Wing_OML`. Then jump to Step 5.

**Step 3 — loft the lower skin.** Repeat Step 2 exactly, swapping in the lower curves.
1. **Insert ▸ Surface ▸ Loft…**; set **Profiles** = `CRV_Airfoil_Root_Lower`, then `CRV_Airfoil_Tip_Lower` (anchor the connectors at the LE vertex again).
2. **Guide Curves** = the same **3D leading-edge** and **trailing-edge** rails.
3. Green-check; rename the feature `SURF_Wing_OML_Lower`.

**Step 4 — knit into a single OML.** The two skins share their LE and TE rail edges, so they fuse seamlessly.
1. Click **Insert ▸ Surface ▸ Knit…**.
2. In the **Selections** box, click both `SURF_Wing_OML_Upper` and `SURF_Wing_OML_Lower`.
3. Leave **Merge entities** checked and click the **Green Checkmark** $(\checkmark)$.
4. Rename the knit result exactly `SURF_Wing_OML`.
   > **Single-loft alternative.** If you would rather have one loft than two-plus-knit, group each section's upper + lower curves with the **SelectionManager ▸ Select Group** into two composite profiles, then loft those with the same two rails. Two skin lofts + a knit is simpler and flexes more robustly, so it's the default here.

**Step 5 — finalize and organize.**
1. Confirm `SURF_Wing_OML` is one continuous surface with a clean leading edge and a sharp trailing edge, translucent from root to tip.
2. Drag `SURF_Wing_OML` — and the `SURF_Wing_OML_Upper` / `_Lower` skins, if you kept them — into your `7_SURFACES` folder.

**8.5 — Loft the fuselage OML (cross-section piercing & skinning).** To build a dynamically updating, flat-bottom **bulbous tangent-arch** fuselage, SolidWorks relies on **Pierce** relations. Think of a Pierce relation like a needle and thread: your active sketch plane acts as the fabric, and the 3D layout lines (`LAY_Side_Profile` or `LAY_Wing_Plan`) are needles passing straight through it. A pierced sketch point permanently locks itself to the exact coordinate where that 3D curve punches through the 2D sketch plane. As your wireframe layout tapers inward toward the nose and tail, the sketch planes intercept them at narrower positions, forcing the cross-sections to scale down automatically with zero hardcoded dimensions.

**Prerequisites — expose the wireframe architecture.** Before drawing cross-sections, ensure your underlying layout lines are fully visible to allow point-to-line selections:
1. In the FeatureManager Design Tree, expand your `2_LAYOUT_SKETCHES` folder.
2. Right-click `LAY_Side_Profile` and click the **Show** icon (the open eyeball).
3. Right-click `LAY_Wing_Plan` (or `LAY_Front_View`) and click **Show**.
4. Press **`Ctrl + 7`** to position your viewport in a 3D isometric perspective.

**Phase 1 — build the six station cross-sections (two of them mid-transitions).** Because the side profile and the planform both break at the mid-nose and mid-tail stations, a 3-section loft would cut straight across those breaks and distort. Build **six** flat-bottom **bulbous tangent-arch** cross-sections instead — one on every fuselage plane that carries a vertex in *either* cage. `PLN_Fuse_Bay_Fwd` is **skipped**: the cabin is constant in both height and width from firewall to cabin-rear, so a mid-cabin section is redundant.

| # | Plane (§7.3.6) | Height pierce — `LAY_Side_Profile` | Width target — `LAY_Wing_Plan` | Rename to |
|---|---|---|---|---|
| 1 | `PLN_Fuse_Nose` | `NT` / `NB` (nose flat) | `NL` (`w_fuse / 4`) | `SET_Fuse_Nose` |
| 2 | `PLN_Fuse_MidNose` *(new)* | `M1` / `M4` | `P1` (`w_fuse_break`) | `SET_Fuse_MidNose` |
| 3 | `PLN_Fuse_Firewall` | top keel `TF → TR` / bottom keel `BF → BR` | `CL` (`w_fuse / 2`) | `SET_Fuse_Firewall` |
| 4 | `PLN_Fuse_Bay_Aft` | keels `TF → TR` / `BF → BR` | `TL` (`w_fuse / 2`) | `SET_Fuse_Bay_Aft` |
| 5 | `PLN_Fuse_MidTail` *(new)* | `M2` / `M3` | `P2` (`w_fuse_break`) | `SET_Fuse_MidTail` |
| 6 | `PLN_Fuse_Tail` | `TT` / `TB` (sleeve root, `tail_exit_D / 2`) | `EL` (`tail_exit_D / 2`) | `SET_Fuse_Tail` |

> **⚠ The boom sleeve is *not* in this loft.** Sections 1–6 run nose → `PLN_Fuse_Tail`, which is now the **sleeve root**, not the aft end of the fuselage. The 1-in sleeve box (`SL_T` / `SL_B` / `SL_P` / `SL_C` at 177.80 mm aft) sits beyond the last fuselage plane, so this loft stops at the sleeve mouth. Close it downstream either by (a) adding a seventh fuselage plane at the sleeve station plus a seventh identical section — the sleeve is constant-section, so section 7 is a copy of section 6 — or (b) leaving the loft at six and extruding the sleeve 1 in aft off `SET_Fuse_Tail` in the solid part. **No seventh plane has been added to §7.3.6**; that changes the published plane set, so it is your call.

> **The two new planes come from §7.3.6.** `PLN_Fuse_MidNose` and `PLN_Fuse_MidTail` are the expression-offset planes you added there; they sit at the exact `M`-break / `P`-break stations, so a section built on each cuts both cages at a real vertex.

Recipe (identical on every plane; the height and width pierces are Phase 2):
1. Click the target plane in the tree, click the **Sketch** icon, and press **`Ctrl + 8`** to snap normal to it.
2. **Draw the bulbous tangent-arch section** exactly as in §6.4: a horizontal **flat floor**, closed by a **Style Spline** that leaves both floor endpoints on a **0° horizontal tangent**, **flares out to `w_fuse`/2**, and runs **Horizontal across the apex** — driven by the cage (`w_floor_pct`, `crown_sh_pct`, `crown_apex_pct`). This closed profile *is* the section; Phase 2 pierces and rails it to size.
3. **Lock symmetry:** the cage's **Symmetric** relations about the **Right Plane** ($X = 0$) keep the section mirror-true and the apex on the centerline.
4. **Place the five belly clock vertices on the flat floor.** Drop sketch **Points** on the floor line: **6 o'clock** (centerline), **4 / 8 o'clock** (floor corners = the spline's floor endpoints, at `= "w_fuse_floor_half"`), and **5 / 7 o'clock** (midway between corner and centre). The floor's **Horizontal** relation holds all five on one flat $Y$.
5. **Place the crown clock vertices on the Style Spline** — three per side:
   - **3 / 9 o'clock (flare):** the **outermost flare control vertex** — the section's maximum width. Phase 2 binds it to the planform rail.
   - **2 / 10 o'clock:** a **Point** pierced **Coincident** onto the spline, dimensioned to the waterline → `= "h_clock_2_10"`.
   - **1 / 11 o'clock:** a point on the spline → `= "h_clock_1_11"`.
   - **12 o'clock:** the **apex** (on the centerline at `h_fuse_top`).
   Each crown point's $X$ rides the spline; its dimensioned $Y$ (or, for the flare, its coincidence to the width rail) fixes it along the curve.
   > **No literal clock angles.** The crown is a **Style Spline**, so its vertices are located by *proportional height* (`h_fuse_top * 2/3`, `* 1/3`) and by the **flare's coincidence to the planform width rail** — not by any circle-centre angle. Every dimension in the section is a global or a fractional expression of one.

**Phase 2 — pierce the heights and bind the flare width to the planform.** Every bulbous section takes its **crown height** and **flat-floor depth** from the side profile and its **maximum (flare) width** from the planform. Do both on each of the six sections.

*Height (side profile, `LAY_Side_Profile`).* Rotate slightly into a 3D view, then pierce the section's apex and floor to the entities for that plane:
- **Crown apex (12 o'clock):** **Pierce** / **Coincident** it to the **top** entity — the top keel `TF → TR` on the cabin sections, the **top-nose / top-tail shoulder spline** (through `M1` / `M2`) on the mid-transitions, `NT` / `TT` on the end-caps. The upper-crown points (1 / 2 / 10 / 11) ride the **spline** at their proportional heights, so the apex pierce plus the flare-rail bind fix the whole crown.
- **Flat floor (6 o'clock + the floor line):** **Pierce** / **Coincident** the floor midpoint to the **bottom** entity — the bottom keel `BF → BR` on the cabin sections (a single flat $Y$), the **bottom-nose / bottom-tail shoulder spline** (through `M4` / `M3`) on the mid-transitions, `NB` / `TB` on the end-caps. The floor's **Horizontal** relation carries the 4 / 5 / 7 / 8 belly points to that same $Y$.

> **Flat only through the cabin.** The floor is a true flat landing plane on `SET_Fuse_Firewall` and `SET_Fuse_Bay_Aft` (both piercing `BF → BR` at `= "h_fuse_bottom"`); on the mid and end sections the belly rises along the bottom shoulder splines to `NB` / `TB` as the ends pinch up. The cabin run reads flat; the ends taper into it.

*Width (planform, `LAY_Wing_Plan`) — the Flare-Width Rail Method.* Because the maximum width now sits at the **flare** (mid-height), not the floor corner, bind the **flare** — not the floor — to the planform:
1. **Pierce the planform.** With the **Point** tool, drop a point out to the side, hold **`Ctrl`**, select it and the **port fuselage-outline segment where it crosses this plane** in `LAY_Wing_Plan`, and click **Pierce**. It lands at the station's planform half-width (`w_fuse / 2` at the cabin, `w_fuse_break` at a break, `w_fuse / 4` at the nose flat, `tail_exit_D / 2` at the tail cap). Repeat starboard.
2. **Vertical width rail.** With the **Centerline** tool, start on the pierced point and drag straight down through the section, click, press **`Esc`**, and confirm a **Vertical** relation. Repeat starboard.
3. **Bind the flare vertex.** Make the **outermost flare control vertex** (3 / 9 o'clock) **Coincident** to the matching rail. This binds the section's **maximum lateral expansion** to the planform wireframe, while the height and the floor coordinates resolve independently via the side-profile pierces. The floor corners (4 / 8) keep their `w_floor_pct` fraction of that width along the flat floor; the upper-crown points (1 / 2) ride the spline in between.
   > **Why bind the flare, not the floor.** In the old boxy section the widest point *was* the floor corner, so the floor pierced the planform. Here the bulge carries the max width at mid-height, so the **flare vertex** is the point that must lock to the planform — otherwise the section's true widest ring floats free between stations and the loft bulges or pinches. The floor is now a *narrower* inboard chord (`w_floor_pct`), free to stay flat.
4. **Verify & name.** The bulbous profile and its twelve clock vertices turn solid **black** (Fully Defined). **Exit Sketch**, press **F2**, and rename it per the Phase 1 table (`SET_Fuse_Nose`, `SET_Fuse_MidNose`, …).
   > **Tail cap.** `SET_Fuse_Tail` closes to the `tail_exit_D` = 0.75-in bounding — flare, floor and apex all collapse toward the ±`tail_exit_D / 2` cap, so the loft terminates on a clean ≈ 19 mm ring.
   > **Decoupling stays intact.** Each section's $Z$ comes only from its `PLN_Fuse_*` plane, so the fuselage never rebuilds when the wing rib grid flexes.

**Phase 2.5 — build the unified 12-rail 3D harness (`LAY_Fuse_Guides_3D`).** Flat 2D lines from `LAY_Wing_Plan` and the open loops of `LAY_Side_Profile` cannot serve as clean diagonal loft guides — each lives on a single plane and cannot pierce the bulbous section's off-axis flare, crown and flat-floor vertices ($Y \neq 0$) out at the diagonals. Unify all twelve longitudinal rails inside **one master 3D sketch** so every rail pierces the true clock vertex on all six sections.
1. **Expose the framework.** In the tree, toggle all six cross-section sketches (`SET_Fuse_Nose` through `SET_Fuse_Tail`) to **Show** so their twelve clock vertices are selectable.
2. **Open the master 3D sketch.** Click **Insert ▸ Sketch ▸ 3D Sketch**, then press **F2** and rename the feature exactly **`LAY_Fuse_Guides_3D`**.
3. Select the standard solid **Line** tool (**`L`**).
4. **Trace all twelve rails, nose to tail.** For one clock position at a time, click the matching vertex on `SET_Fuse_Nose`, then `SET_Fuse_MidNose`, `SET_Fuse_Firewall`, `SET_Fuse_Bay_Aft`, `SET_Fuse_MidTail`, and `SET_Fuse_Tail` in order — every click must snap **Coincident** (pierce) to the existing section vertex (watch for the yellow glyph). Walk the clock systematically:
   - **Rail 1** — 12 o'clock (top centerline)
   - **Rail 2** — 1 o'clock (upper-port shoulder)
   - **Rail 3** — 2 o'clock (mid-port shoulder)
   - **Rail 4** — 3 o'clock (port flare — max width)
   - **Rails 5 & 6** — 4 & 5 o'clock (port belly)
   - **Rail 7** — 6 o'clock (bottom centerline)
   - **Rails 8–12** — 7 / 8 / 9 / 10 / 11 o'clock (mirror the sequence down the starboard side)
5. **Verify & file.** Because every rail endpoint is Coincident to an already fully-defined section vertex, the whole 3D sketch reads **Fully Defined** (all black) on completion — a blue rail means a click missed its vertex; re-snap it. **Exit** the 3D sketch and drag **`LAY_Fuse_Guides_3D`** into the **`2_LAYOUT_SKETCHES`** folder.
   > **Why one 3D sketch, not twelve guides picked off the flat layouts.** A loft guide is legal only if it pierces every profile it crosses at a real point. The diagonal clock vertices sit at $X \neq 0$ **and** $Y \neq 0$ at once — no single flat layout sketch contains them, and a `LAY_Side_Profile` open loop only ever touches the 12 and 6 o'clock line. Collecting all twelve rails in one 3D sketch guarantees a clean pierce on all six sections and hands the loft a rigid circumferential cage that traps the diagonal fields.

**Phase 3 — execute the six-profile surface loft over the 12-rail harness.**
1. Open **Insert ▸ Surface ▸ Loft…** (or **Lofted Surface** on the Surfaces tab). The **Profiles** box is highlighted.
2. **Profiles (unchanged).** Click the six sections in exact order front (**+Z**) → back (**−Z**): `SET_Fuse_Nose` → `SET_Fuse_MidNose` → `SET_Fuse_Firewall` → `SET_Fuse_Bay_Aft` → `SET_Fuse_MidTail` → `SET_Fuse_Tail`. Click near the **same clock vertex** on each so the green sync handles align and the skin does not twist.
3. **Clear the old guides.** Click inside the **Guide Curves** box and remove any curve still listed there — the retired `LAY_Side_Profile` upper / lower open loops. The harness replaces them entirely.
4. **Load the twelve rails.** One at a time, select all **12 individual line paths** inside `LAY_Fuse_Guides_3D` from the graphics area, populating the Guide Curves list Rail 1 → Rail 12. Each rail pierces all six profiles at its clock position.
   > **Why twelve rails beat four quadrants.** A 4-quadrant loft leaves the diagonal fields (1 / 2 / 4 / 5 / 7 / 8 / 10 / 11 o'clock) unconstrained *between* sections, so the blend algorithm is free to bow the OML outward there. Twelve rails nail every clock position along the full length — the diagonals can no longer pop out.
5. **Confirm the mesh.** The preview should read as a tight, even **quadrant grid with zero intermediate bulging** between the rails. If a diagonal still bows, a rail missed a pierce — re-check Phase 2.5, step 4.
6. Click the large **Green Checkmark** $(\checkmark)$ to generate the skin.
7. Select the feature, press **F2**, rename it exactly **`SURF_Fuse_OML`**, and drag it into the **`7_SURFACES`** folder.

**8.6 — Empennage OML surfaces (HT & VT airfoil skinning).** The tail wireframes (§5.8/§6.8) and section planes (§7.3.7/§7.3.8) now carry true spar axes, so the empennage skins loft exactly like the wing (§8.4): a symmetric airfoil at root and tip, split into upper/lower streams, guided by 3-D leading- and trailing-edge rails welded to the shared curve vertices. Both `SURF_HTail_OML` and `SURF_VTail_OML` are **reference surfaces — zero mass** (§9.5 golden rule; body-free rule §13.8), so they never break the body-free constraint. Budget ~30 minutes.

**Part A — the symmetric-airfoil Excel transform (NACA 0012).** Reuse the §8.2 Method-A engine with two changes: a symmetric section (equal-and-opposite upper/lower ordinates, zero camber) and one constant that shifts each airfoil **aft** ($-Z$) onto its tail station. Paste the cleaned NACA 0012 loop into Columns **A** / **B** (§8.1), one sheet per surface (HT root, HT tip, VT root, VT tip).

* **Master constants (Row 1).** The §8.2 layout, plus one (VT: two) new cells:
   - `E1` chord — `c_root_HT` / `c_tip_HT` (HT sheets) or `c_root_VT` / `c_tip_VT` (VT sheets).
   - `F1` incidence — `i_HT` for **both** HT sections (no HT twist global, so root and tip share it); **0** for the VT (a symmetric fin at zero incidence).
   - `G1` span station — **0** at each root; `b_HT`$/2$ at the HT tip; `b_VT` at the VT tip.
   - `H1` sweep — `sweep_HT` (HT) or `sweep_VT` (VT).
   - `I1` dihedral — **0** for both (no empennage dihedral global).
   - `J1` root-LE station — `x_HT_LE_root` (HT) or `x_VT_LE_root` (VT). **This is the aft shift** that lands the tail airfoils behind the wing.
   - `K1` (VT sheets only) fin-root seat — `h_tail_top`. Places the VT root section on the crown; it must equal the §6.8.1 root-$Y$ reference.

* **Horizontal tail — the wing axis map, shifted aft.** The HT spans laterally ($X$), so it uses the §8.2 Columns C/D/E verbatim, with `J1` folded into the $Z$ column:
   - **Column C (SW $X$ — spanwise):** `=$G$1` (identical to §8.2).
   - **Column D (SW $Y$ — thickness + incidence; dihedral term zeroes):** the §8.2 `D3` formula unchanged — with `$I$1` = 0 the dihedral term drops out on its own.
   - **Column E (SW $Z$ — chord + sweep + tail station):** take the §8.2 `E3` formula and append `- $J$1`:
     `=(( -A3 - (-0.25) ) * COS(RADIANS($F$1)) - (B3 - 0) * SIN(RADIANS($F$1)) + (-0.25)) * $E$1 - ($G$1 * TAN(RADIANS($H$1))) - $J$1`
     > The trailing `- $J$1` slides the whole HT aft ($-Z$) onto the `x_HT_LE_root` station; everything ahead of it is the identical wing rotation/sweep math.

* **Vertical tail — the $+Y$-span coordinate swap.** The fin spans **vertically**, so the span and thickness axes trade places versus the wing. A symmetric section at zero incidence means **no chord rotation**, so the columns collapse cleanly:

  | SolidWorks axis | Wing / HT (span along $X$) | **VT (span along $+Y$)** |
  |---|---|---|
  | $X$ | spanwise station `=$G$1` | **thickness** → `= B3 * $E$1` |
  | $Y$ | thickness + dihedral | **span station + seat** → `= $G$1 + $K$1` |
  | $Z$ | chord + sweep | **chord + sweep + tail station** → `= -A3 * $E$1 - ($G$1 * TAN(RADIANS($H$1))) - $J$1` |

   - **Column C (SW $X$ — lateral thickness):** `= B3 * $E$1`. The airfoil's $y_{norm}$ thickness becomes the fin's lateral half-thickness; symmetry places the two skins at $\pm$ this value about $X = 0$.
   - **Column D (SW $Y$ — vertical span):** `= $G$1 + $K$1`. The root row sits at $Y = $ `h_tail_top`; tip rows climb to `h_tail_top + b_VT`.
   - **Column E (SW $Z$ — chord, sweep rake, tail station):** `= -A3 * $E$1 - ($G$1 * TAN(RADIANS($H$1))) - $J$1`. The `-A3 * $E$1` runs the chord aft ($-Z$) from LE to TE; `- $G$1 * TAN(sweep_VT)` rakes higher sections aft; `- $J$1` seats the root LE at `x_VT_LE_root`.
   > **Why no rotation block for the VT.** A NACA 0012 is symmetric and the fin sits at zero incidence, so the quarter-chord pitch rotation the wing/HT applies (the paired `SIN` / `COS` terms) is the identity here — dropping it is exact, not an approximation. If you ever cant the fin or use a cambered section, reinstate the §8.2 rotation block in Columns C/E with the fin's angle.

* **Export the eight streams.** Split each sheet at the LE apex row into an **Upper** stream (TE → LE) and a **Lower** stream (LE → TE), the LE row shared by both (§8.1), and save Columns **C/D/E** as UTF-8 text to `Z:\SAE_Micro_2026\05_Sizing\`: `airfoil_HT_root_upper_xyz.txt` / `_lower_`, `airfoil_HT_tip_upper_` / `_lower_`, and the four `airfoil_VT_*` equivalents.

**Part B — import the eight curves and build the tail guide rails.**
1. **Insert ▸ Curve ▸ Curve Through XYZ Points** for each of the eight files (§8.2 Step 4). Rename: `CRV_HT_Root_Upper` / `_Lower`, `CRV_HT_Tip_Upper` / `_Lower`, `CRV_VT_Root_Upper` / `_Lower`, `CRV_VT_Tip_Upper` / `_Lower`.
   > Symmetric sections still split upper/lower — the shared LE/TE rows weld each pair into snappable nose and tail **vertices** (§8.3), which is what the rails grab. A single closed spline gives the rails nothing to bite at the nose.
2. **HT rails (`LAY_HT_Guides_3D`).** Open a **3D Sketch** (**F2** → `LAY_HT_Guides_3D`). With the **Line** tool: click the **root nose vertex** (where `CRV_HT_Root_Upper` / `_Lower` meet) → the **tip nose vertex** (`CRV_HT_Tip_*`) for the **LE rail**; then the **root TE vertex** → **tip TE vertex** for the **TE rail**. Each line fully defines on contact — both ends welded to curve vertices. **Exit**; drag into `2_LAYOUT_SKETCHES`.
3. **VT rails (`LAY_VT_Guides_3D`).** Same, on the fin curves: LE rail root-nose → tip-nose, TE rail root-TE → tip-TE. These rails **rise in $+Y$ and rake aft in $-Z$** — the fin's swept edges. Confirm both black; **Exit**; file in `2_LAYOUT_SKETCHES`.
   > **Endpoint stability.** Every rail endpoint welds to a real curve vertex, so re-exporting a tail airfoil rebuilds the curves and the rails ride along — no `->x` (§8.4).

**Part C — loft `SURF_HTail_OML` and `SURF_VTail_OML`.** Skin upper and lower separately, then knit — identical to the wing (§8.4 Steps 2–4).
* **Horizontal tail.**
  1. **Insert ▸ Surface ▸ Loft…**; **Profiles** = `CRV_HT_Root_Upper` then `CRV_HT_Tip_Upper`, each clicked near its **LE vertex** so the green sync handles anchor LE-to-LE (a mismatched pick corkscrews the skin — §14 item 20).
  2. **Guide Curves** = the LE and TE rails of `LAY_HT_Guides_3D`. Green-check; rename `SURF_HTail_OML_Upper`.
  3. Repeat with the two `_Lower` curves → `SURF_HTail_OML_Lower`.
  4. **Insert ▸ Surface ▸ Knit…**, select both skins, leave **Merge entities** checked, green-check; rename `SURF_HTail_OML`.
* **Vertical tail.** Repeat exactly on the VT curves and `LAY_VT_Guides_3D` rails → `SURF_VTail_OML_Upper` / `_Lower`, knit → `SURF_VTail_OML`.
  > **Sync-handle audit (fin).** Because the fin sections stack in $+Y$, drag each profile's green connector to the **same** vertex (both LE) before accepting — the vertical stack makes a top-vs-side mismatch easy to miss, and it twists the skin (§14 item 20).
* **File & verify.** Drag `SURF_HTail_OML`, `SURF_VTail_OML` (and the `_Upper` / `_Lower` skins if kept) plus all eight `CRV_*` tail curves into `7_SURFACES`. Then run the §8.8 mass-properties audit: the **Solid Bodies** folder must stay empty and mass must read **0.00 g** — surfaces are weightless reference geometry (§9.5 golden rule).

**8.7 — How downstream parts consume it (derived part workflows).** This section marks the pivot from a weightless, body-free reference skeleton to real, solid, manufactured parts. Because you will uncheck **"Locate part with Move/Copy Feature"** when importing the skeleton into your child parts, every component shares the exact same global coordinate space. When you later bring these parts into your top assembly, they snap into their perfect physical locations with zero manual assembly mates.

---

**Workflow 1 — manufacturing a rib (Intersection Curve method).** This workflow slices your master 3D wing surface with a specific parametric rib plane to instantly capture an exact 2D airfoil profile carrying the true local twist and taper.

**Step 1 — initialize the new part file.**
1. Go to the top main menu bar and click **File ▸ New**. Select **Part** and click **OK**.
2. Click **File ▸ Save As**. Navigate straight to your parts folder: `Z:\SAE_Micro_2026\02_Parts\`.
3. Name the file exactly **`Rib_R03.SLDPRT`** (or match your target station number) and click **Save**.

**Step 2 — extract references from the master skeleton.**
1. On the top main menu bar, click **Insert ▸ Part…**
2. In the file browser, navigate to `Z:\SAE_Micro_2026\01_Skeleton\`, select **`AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`**, and click **Open**.
3. In the left-hand **Insert Part PropertyManager**, under the **Transfer** section, check these explicit boxes:
   - **Surface bodies** (pulls in `SURF_Wing_OML`).
   - **Planes** (pulls in your parametric rib stations).
   - **Coordinate systems**.
4. Under the **Locate Part** section — **critical hygiene guard:** ensure the checkbox for **"Locate part with Move/Copy Feature" is UNCHECKED**.
5. Click the **Green Checkmark** $(\checkmark)$ at the top of the PropertyManager. The skeleton reference entities load cleanly into your canvas.

**Step 3 — splay and capture the airfoil shape.**
1. In your FeatureManager Design Tree, locate the imported skeleton base feature, expand its internal hierarchy, and click once on the plane named **`PLN_RibStn_R03`**.
2. Click the **Sketch** icon from the pop-up context toolbar to launch an active sketch. Press **`Ctrl + 8`** to snap normal to the plane.
3. On the **Sketch** tab of the CommandManager, click the drop-down arrow next to the *Convert Entities* tool icon and select **Intersection Curve**.
4. Click directly on the translucent **`SURF_Wing_OML`** master wing surface body in the graphics window.
5. Click the **Green Checkmark** $(\checkmark)$ inside the Intersection Curve PropertyManager panel. SolidWorks instantly traces a smooth, closed 2D loop representing the true spatial intersection of the wing at that station.

**Step 4 — add structural thickness and features.**
1. Use **Offset Entities** if you need to offset the airfoil curve inward to account for thin composite skin boundaries. Otherwise, leave the profile outer boundary intact.
2. Sketch any necessary internal modifications, such as rectangular slots for the main spar or circular bores for a wing-joiner tube.
3. Switch to the **Features** tab of the CommandManager and click **Extruded Boss/Base**.
4. In the Extrude PropertyManager:
   - Change the *Direction 1* **End Condition** dropdown from *Blind* to **Mid Plane** (ensuring the material accurately straddles the station datum).
   - In the depth box, link to your global thickness variable by typing `= "rib_thk"`, or input your physical stock thickness (e.g., `2.00 mm` for balsa/plywood).
5. Click the **Green Checkmark** $(\checkmark)$ and save the file.

---

**Workflow 2 — creating the wing skin (Offset & Thicken method).** This workflow duplicates the master outer mold line layout and instantly hardens it into a solid, manufacturable shell skin.

**Step 1 — initialize the skin file.**
1. Click **File ▸ New**, select **Part**, and click **OK**.
2. Click **File ▸ Save As**, navigate to `Z:\SAE_Micro_2026\02_Parts\`, name the file **`Wing_Skin.SLDPRT`**, and click **Save**.

**Step 2 — import the master surface shell.**
1. Click **Insert ▸ Part…** from the top main menu, select **`AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`**, and click **Open**.
2. In the PropertyManager, check **Surface bodies** (leave all other data types unchecked) and confirm that **"Locate part with Move/Copy Feature" is UNCHECKED**.
3. Click the **Green Checkmark** $(\checkmark)$.

**Step 3 — duplicate the master OML shape.**
1. Click **Insert ▸ Surface ▸ Offset…** from the top menu bar (or click **Offset Surface** on your Surfaces CommandManager tab).
2. Click directly on the imported `SURF_Wing_OML` surface body in your graphics area.
3. In the Offset Surface PropertyManager, set the **Offset Distance** text box to exactly **`0 mm`** to generate an unlinked, flawless 1:1 surface clone. Click the **Green Checkmark** $(\checkmark)$.

**Step 4 — solidify the shell.**
1. Click **Insert ▸ Boss/Base ▸ Thicken** (or click the **Thicken** icon on your Surfaces tab).
2. Click directly on your newly created offset surface body in the graphics area.
3. In the Thicken PropertyManager:
   - Look at the **Thicken Side** directional buttons. Click the icon for **Thicken Side 1** or **Thicken Side 2** to force the solid material thickness to build *inward*, preserving your exact aerodynamic outer mold line geometry.
   - In the **Thickness** text box, enter your structural layup or casing thickness value (e.g., `1.00 mm`).
4. Click the **Green Checkmark** $(\checkmark)$ and save your file.

---

**Workflow 3 — modeling spars and shear webs (OML referencing).** Spars must bridge the internal gap between the upper and lower skins perfectly. By referencing the skeleton's 3D axes and master surface, you can ensure they fit flush against the inside of the wing capsule without structural gaps.

**Step 1 — initialize the spar file.**
1. Click **File ▸ New**, select **Part**, and click **OK**.
2. Click **File ▸ Save As**, navigate to `Z:\SAE_Micro_2026\02_Parts\`, name the file **`Main_Spar.SLDPRT`**, and click **Save**.

**Step 2 — siphon wireframes and surfaces.**
1. Click **Insert ▸ Part…** from the top main menu, select **`AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`**, and click **Open**.
2. In the PropertyManager, check **Surface bodies** (`SURF_Wing_OML`), check **Axes** (`AX_MainSpar_3D`), and check **Planes** to pull in your boundary stations. Verify that **"Locate part with Move/Copy Feature" is UNCHECKED**, then click the **Green Checkmark** $(\checkmark)$.

**Step 3 — generate the core alignment plane and reference track.**
1. Build a plane running continuously down your spar line: click **Insert ▸ Reference Geometry ▸ Plane**.
2. Select your imported **`AX_MainSpar_3D`** axis as the first reference, and select the default **Top Plane** as your second reference, setting the relation to **Perpendicular**. Click the **Green Checkmark** $(\checkmark)$.
3. Click this new plane in the tree and select **Sketch**.
4. Go to **Tools ▸ Sketch Tools ▸ Intersection Curve**. Click directly on the **`SURF_Wing_OML`** surface body and click the **Green Checkmark** $(\checkmark)$. SolidWorks draws two curves representing the inner ceiling and floor bounds of your wing.

**Step 4 — extrude the web profile.**
1. Select the standard **Line** tool from your Sketch tab.
2. Draw your spar web or C-channel profile bounded directly between the top and bottom intersection curves. Use the intersection lines as **Coincident** track constraints to make the profile follow the airfoil thickness contour perfectly.
3. Once the sketch turns completely solid **black** (Fully Defined), open the **Features** tab and click **Extruded Boss/Base**.
4. Set the end condition to **Blind** or **Mid Plane**, define your material web thickness (e.g., `3.00 mm` foam core or carbon web), and click the **Green Checkmark** $(\checkmark)$. Save your file.

**8.8 — Keep it clean and verify (quality-assurance pass).** This section serves as your final structural gate. It ensures that the surfaces modeled have not accidentally introduced unwanted physical mass into the skeleton file, and validates that your parametric links are fully robust before routing the file to downstream team leads.

**Step 1 — the mass-properties audit (body-free verification).** Surface bodies are zero-thickness mathematical references, but a single accidental solid feature will leak unwanted mass into every part that derives from this skeleton. Audit the file to confirm its physical weight remains zero.
1. Navigate to the CommandManager tabs at the top of your screen and click the **Evaluate** tab.
2. Click the **Mass Properties** icon (or go to the top main menu bar and click **Tools ▸ Evaluate ▸ Mass Properties**).
3. Review the data layout inside the pop-up dialog box:
   - **Solid-bodies check:** the text tree inside the selection box must completely lack a *Solid Bodies* folder, or it must read *0*. A *Surface Bodies* folder listing `SURF_Wing_OML`, `SURF_Fuse_OML`, `SURF_HTail_OML`, and `SURF_VTail_OML` is correct.
   - **Mass-value verification:** read the **Mass** line string. It must report exactly **0.00 grams** (or `0.00 pounds`).
4. *Troubleshooting:* if the mass registers greater than zero, close the box, scan your FeatureManager Design Tree for solid yellow block features, right-click the offending feature, select **Edit Feature**, and delete it or convert it to a surface.

**Step 2 — tree housekeeping (populating the `7_SURFACES` folder).** To keep the master file navigable for the rest of the team, group your surface assets and curves into their dedicated tree folder:
1. Go to your **FeatureManager Design Tree** on the left.
2. Hold down the **`Ctrl`** key on your keyboard.
3. Click on every surface asset and curve profile generated in Chapter 8:
   - Click **`SURF_Wing_OML`**.
   - Click **`SURF_Fuse_OML`**.
   - Click **`SURF_HTail_OML`** and **`SURF_VTail_OML`** (with their `_Upper` / `_Lower` skins if you kept them).
   - Click your airfoil curves or generation sketches (e.g., `CRV_Airfoil_Root_Upper` / `_Lower`, `CRV_Airfoil_Tip_Upper` / `_Lower`, the eight `CRV_HT_*` / `CRV_VT_*` tail curves, or your `LAY_Airfoil_Placed_*` sketches).
4. Release the **`Ctrl`** key, **right-click** any of the highlighted items, and select **Add to New Folder** from the context menu.
5. Type exactly **`7_SURFACES`** into the folder text box and press **`Enter`**.

**Step 3 — the Knit Surface evaluation (to stitch or separate).** Splicing multiple independent surface bodies together consumes excessive computing power and can create edge-tolerance errors on complex geometry.
- **When to leave them un-knit (default approach):** leave `SURF_Wing_OML` and `SURF_Fuse_OML` as completely separate bodies if your team members are extracting components independently (e.g., the rib lead only needs the wing profile, while the internal-bulkhead lead only needs the fuselage capsule).
- **When to use the Knit Surface tool:** only execute a surface knit if you are actively generating a blended wing-body joint or complex aerodynamic filleting where the wing root meets the fuselage skin.
  1. Click **Insert ▸ Surface ▸ Knit…** from the top main menu.
  2. Click inside the **Selections** box, then click `SURF_Wing_OML` and `SURF_Fuse_OML` in the graphics area.
  3. Leave **Merge entities** and **Form solid** unchecked (to preserve the body-free constraint) and click the **Green Checkmark** $(\checkmark)$.

**Step 4 — the parametric flex & rebuild check (forced perturbation test).** This is the ultimate test of your framework's stability. You will deliberately alter your master design variables to confirm the 3D surface mesh follows your equations without breaking.
1. Go to the top main menu bar and click **Tools ▸ Equations** (or right-click your tree's `Equations` folder and select **Manage Equations**).
2. Ensure you are in the **Equation View** (the top-left toggle icon).
3. Locate your primary driving parameters and apply a +10 % temporary shift:
   - Click the value cell for your root chord **`"c_root"`** and increase it (e.g., change `300` to `330`).
   - Click the value cell for your **`"dihedral"`** angle and increase it by a couple of degrees (e.g., change `4` to `6`).
4. Click **OK** to exit the Equations dialog box.
5. **Execute the force-rebuild engine:** hold down **`Ctrl`** and press **`Q`** (**`Ctrl + Q`**). Do *not* use a standard rebuild (**`Ctrl + B`**). **`Ctrl + Q`** forces a cold, top-down re-evaluation of every geometric relationship in the file, catching latent errors that a standard rebuild skips.
6. **Conduct the architecture audit:** watch the screen as the engine re-solves:
   - *Success state:* the wing planform expands, the dihedral angle lifts, and your translucent `SURF_Wing_OML` skin smoothly conforms to the new geometry with zero warning flags.
   - *Failure state:* if any feature in your tree flags yellow or red, or triggers a "What's Wrong" prompt, an entity has lost its path. Double-click the error to repair the broken intersection or pierce constraint.
7. **Revert to baseline:** open **Tools ▸ Equations**, restore your original baseline competitive values for `"c_root"` and `"dihedral"`, click **OK**, and hit **`Ctrl + Q`** to return the aircraft skeleton to its true competition configuration. Save the file.

---

## 9. Consuming the skeleton downstream — the actual top-down mechanics

Two mechanisms. **Insert Part (derived) is the default** for a distributed team; in-context is the fallback. The payoff of everything so far: change a skeleton global and every part rebuilds to match. Budget ~30 minutes for the first part; minutes each thereafter.

### 9.1 Derived part via Insert Part — *preferred* (worked example: a rib)
1. **File ▸ New ▸ Part**; **Save As** → `02_Parts\Rib_R03.SLDPRT`.
2. **Insert ▸ Part…** → browse to `AIRCRAFT_SKELETON_SAE_MICRO26.SLDPRT`. In the **Insert Part** PropertyManager, **tick only what this part needs** — for a rib: **Surface bodies** (`SURF_Wing_OML`), **Planes** and **Axes** (`PLN_RibStn_R03`, `AX_MainSpar`, `AX_WingJoiner`), **Coordinate systems**. Leave **"Locate part with Move/Copy Feature" UNCHECKED** so it lands at the **coincident origin** (this is what keeps every part in the skeleton's frame). Click in the graphics area / OK.
3. Hide the imported reference you won't draw on (right-click ▸ Hide) to cut clutter.
4. Open a **sketch on `PLN_RibStn_R03`** and capture the rib profile: **Tools ▸ Sketch Tools ▸ Intersection Curve** of `SURF_Wing_OML` with that plane (or **Convert Entities** off the airfoil). **Offset Entities** inward by the skin thickness if the rib sits under skin.
5. Add the **spar cutouts** referencing `AX_MainSpar` / the spar lines, plus lightening holes.
6. **Features ▸ Extruded Boss/Base**, end condition **Mid Plane**, depth `= "rib_thk"` (straddles the rib plane). Save.
7. The rib now holds a **one-way external link** to the skeleton (a `->` marker on the base feature) and rebuilds whenever the airfoil, chord, or rib station changes.

> **Pro-tip:** build one rib fully, then **Save As** for each station and just re-point its sketch to the next `PLN_RibStn_*` (or drive the plane choice with a configuration). Spars, fuselage frames, and the tail follow the same Insert-Part pattern against their own references.

> **Internal bulkheads & formers (round-section, top-down).** The same mechanic gives you curved fuselage frames straight off the master surface: create a new part, **Insert ▸ Part…** the skeleton and tick **`SURF_Fuse_OML`** plus the target station plane (a `PLN_RibStn_*` or a dedicated former plane). Open a **sketch on that plane** and run **Tools ▸ Sketch Tools ▸ Intersection Curve** with `SURF_Fuse_OML` selected — SolidWorks drops a **perfectly curved former profile** matching the round OML at that station in one click. **Offset Entities** inward by the former/skin thickness for the web, add lightening holes, and **Extruded Boss/Base** with **Mid Plane** end condition. Because the profile is an *intersection with the master surface*, it **re-cuts automatically** whenever `w_fuse`, `h_fuse`, `h_fuse_top`, or the station location changes — no manual re-drawing of the bulkhead curve.

### 9.2 Keep derived parts light
Only tick the entities a part actually consumes, and hide imported reference you don't sketch on. This speeds rebuilds and keeps each part's tree readable. The imported skeleton shows as a single base feature carrying the external reference.

### 9.3 Build the assembly — parts snap into place
1. **File ▸ New ▸ Assembly**; **Save As** → `03_Assemblies\Aircraft_Micro26.SLDASM`.
2. **Insert the skeleton first** and drop it at the assembly origin (the first component is **fixed** automatically) — it's the reference master.
3. Insert each derived part. Because every part was derived at the skeleton's **coincident origin**, mate **part Origin ▸ assembly Origin** (Coincident), or mate `CSYS_Master`↔`CSYS_Master`. Each part snaps to its correct relative position with **no manual positioning**.
4. Hide the skeleton's sketches/planes for a clean view (keep the component so rebuilds still propagate), or suppress the skeleton once all parts are placed by origin mates.

### 9.4 In-context within the assembly — *fallback only*
1. New assembly; **insert the skeleton first**, fixed at origin.
2. **Insert Components ▸ New Part**, pick a skeleton plane to start, edit in-context, reference the skeleton's sketches/edges/surface.
3. References flow skeleton → part *through the assembly* (`->` in-context refs).
4. More fragile: depends on the assembly being open and rebuilt in order, moving the skeleton breaks refs, and parts are harder to check in independently. Use only when a part genuinely needs live assembly context (e.g., a mating-driven fit between two parts).

### 9.5 Lock the links and respect the golden rule
Once the architecture freezes, **lock** the external references (§10) so finished parts stop silently re-propagating. **Golden rule:** the skeleton references nothing downstream — data flows strictly **skeleton → parts → assembly**. A part must never drive the skeleton.

### 9.6 Verify the propagation (the whole point)
Change one skeleton global — e.g. `c_root` +20 mm — then open `Rib_R03` and the assembly and confirm both rebuilt to match. One edit, whole airframe updates: that's the top-down payoff you built the skeleton for.

---

## 10. External-reference hygiene and locking

This is the discipline that keeps a 100-variable, many-part top-down model from quietly corrupting itself. The §9 links are powerful and fragile in equal measure — these are the exact moves to manage them.

**10.1 — Learn to read the reference markers.** Every externally-referenced feature shows a suffix after its name in the tree — your at-a-glance health check:
- `->`  in context, resolvable and current.
- `->?`  out of context (the skeleton isn't loaded right now; can't be evaluated).
- `->*`  **locked** (deliberately frozen — won't update).
- `->x`  **dangling / broken** (the reference is lost — fix immediately).
Scan for `->x` regularly; it means a part has lost its link to the skeleton.

**10.2 — Set the prevention defaults (once).** **Tools ▸ Options ▸ System Options ▸ External References**:
- **Uncheck** "Allow multiple contexts for parts when editing in assembly" (prevents accidental multi-context refs).
- Set "Load referenced documents" to **All** (or **Prompt**) so refs resolve on open.
- Tick "Open referenced documents with read-only access" if several people open the skeleton at once.
Combined with the one-folder/one-path rule from §1.1, this is most of prevention.

**10.3 — Audit references (Find References).** **File ▸ Find References** lists the full dependency set and each file's path. Confirm nothing points outside the project folder (a stray path to someone's Desktop is a future broken ref). The dialog's **Copy Files** can bundle the set.

**10.4 — Relocate or rename safely (Pack and Go).** **File ▸ Pack and Go** is the *only* safe way to move/rename/copy linked files. Tick to include drawings, simulation, and the linked `skeleton_equations_micro.txt`; set destination and any prefix/suffix; flatten or keep the structure; Save. It rewrites every internal link so nothing breaks. **Never** rename or move a linked file in Windows Explorer.

**10.5 — Lock references as each subsystem freezes.** Right-click the part (or a specific feature) ▸ **External References…** ▸ **Lock All**. Locked features show `->*` and stop updating from the skeleton.
- **Workflow:** keep refs **live** (unlocked) during active design; **lock per-subsystem** as each geometry freezes; **lock everything** before a release / competition build. Use **Unlock All** only when you deliberately want to re-propagate a skeleton change.
- **Break All** *permanently* severs the link (irreversible after save) and makes the geometry dumb — use it only to detach a part for archival, never as routine cleanup.

**10.6 — Rebuild & propagate in order.** After any skeleton global edit:
1. In the **skeleton**: **Ctrl-Q** (forced full rebuild — catches latent errors a normal `Ctrl-B` skips), then **save**.
2. Open the **assembly resolved** (right-click ▸ Set Lightweight to Resolved if needed), **Ctrl-Q**; live (unlocked) parts rebuild off the skeleton.
3. Scan the tree for error/warning flags and any `->x`. Fix dangling refs before continuing. Locked (`->*`) parts intentionally stay put.

**10.7 — Keep the skeleton body-free.** **Tools ▸ Evaluate ▸ Mass Properties** → mass should read ≈ 0. The **Solid Bodies** folder must be empty (a **Surface Bodies** folder is fine — surfaces carry no mass). A stray solid body would leak mass into every derived part.

**10.8 — Periodic health check.**
- No `->x` anywhere in the skeleton, parts, or assembly.
- Frozen subsystems show `->*`; active ones show `->`.
- A **Pack and Go** test relocates the set with zero broken refs.
- Skeleton mass ≈ 0; clean `Ctrl-Q` top to bottom.

---

## 11. Configurations — payload states from one skeleton

Micro flies **one geometry in three mass states**, so configurations drive the **water mass**, never the shape. Work in two layers: the skeleton configs show the **target** CG move (planning); the assembly configs with real mass show the **actual** CG (the real check). Budget ~20 minutes.

**11.1 — Skeleton: add the configurations.** Click the **ConfigurationManager** tab (top of the FeatureManager panel) ▸ right-click the part name ▸ **Add Configuration** → create `Empty`, `Loaded`, `Drained`.

**11.2 — Skeleton: drive `V_water` per config.** **Insert ▸ Tables ▸ Design Table** ▸ **Blank** (place it, then click outside to edit the embedded Excel):
- Row labels = the config names; first data column header `$VALUE@V_water`.
- Values: `Empty` = 0, `Loaded` = your design water (e.g. 2000), `Drained` = residual (e.g. 50).
- Add `$VALUE@W_empty` or other columns if they differ by state.
- Click outside the table ▸ it builds the configs. *(If a header string is rejected, confirm the exact global name as it appears in the Equations dialog.)*

Switching configs now recomputes `W_water`, `W_TO`, `x_CG` and moves `PT_CG_target`. Remember the skeleton is **body-free**, so these are **computed targets**, not real CG.

**11.3 — Assembly: represent the water as mass.** In the aircraft assembly, model the water either as a **solid body/part** filling the container, assigned **water density** (custom material, $\rho = 1.0\ \mathrm{g/cm^3}$), or a component with a **mass override**. For parts not yet fully modeled, assign **mass overrides** (Tools ▸ Evaluate ▸ **Mass Properties ▸ Override Mass Properties**) so the CG estimate is realistic before every detail exists.

**11.4 — Assembly: create the matching configs.** In the assembly **ConfigurationManager** add `Empty` / `Loaded` / `Drained`. Right-click the water component ▸ **Configure component** (Modify Configurations grid): **suppress** the water in `Empty`, full mass in `Loaded`, **residual** mass (or suppressed + a small residual body) in `Drained`.

**11.5 — Read and check the CG per config (the real test).** For each config: **Tools ▸ Evaluate ▸ Mass Properties** → read the longitudinal CG. Then verify against the band from §5.6:

$$x_{CG,fwd} \le x_{CG} \le x_{CG,aft}, \qquad SM = \frac{x_{NP}-x_{CG}}{\bar c}\in[SM_{min},\,SM_{max}]$$

- **Both** the loaded and the drained actual CG must fall inside `PT_CG_fwd…PT_CG_aft`.
- The **loaded→drained CG travel** is the central Micro stability concern — minimize it by keeping the water-mass centroid `x_bay` near the CG; trim with ballast at `PT_Ballast` if needed (never inside the container).
- Set `x_NP` from XFLR5/AVL first, or the band is meaningless.

**11.6 — When you actually need a geometry variant.** Configurations are for **mass states only**. For a genuinely different shape (backup wing, alternate tail), do **not** overload one skeleton with geometry configs — keep a **template skeleton** and make a **derived copy** (separate file) so the variants don't entangle.

**11.7 — Verify.** Cycle `Empty → Loaded → Drained` in both the skeleton and the assembly; confirm the target `PT_CG_target` and the **actual** assembly CGs all land in band, with no rebuild errors and the design table driving the configs cleanly.

---

## 12. Micro Class reference geometry & compliance  `[2026 rules §9, §2]`

Most of these features already exist from §2–§7 — this is the **compliance sign-off pass**: confirm every 2026 Micro rule is captured as geometry or a check equation, add the few compliance-only features, and verify. Budget ~20 minutes.

**12.1 — Surface the check equations (a compliance dashboard).** The margins `arm_clear`, `sw_clear` and the scoring readouts `span_ft`, `W_pay_lb`, `W_empty_lb` already compute in **Tools ▸ Equations** — read them there; **both margins must be ≥ 0**. Optional at-a-glance dashboard: **File ▸ Properties ▸ Custom** and add a property per check referencing the global (e.g. value `"arm_clear"`), or an **Insert ▸ Annotation ▸ Note** linked to those values. If a property string won't evaluate on your version, just rely on the Equations dialog.

**12.3 — External bottom drain path** `[R §9]`.
1. From the **lowest point of the cabin floor**, sketch a **construction line** straight down to **`PT_Drain`** on the external underside — gravity-fed and unobstructed.
2. Confirm it's the lowest point so the water fully drains within 60 s with no squeezing and without opening the airframe.

**12.4 — 9-in prop keep-out** `[R §2]`.
1. On **`PLN_PropDisk`**, confirm the **`D_prop`** circle and the concentric **`D_prop/2 + keepout`** ring (§6/§7).
2. *Optional visual:* **Insert ▸ Surface ▸ Revolve** a reference disc/cylinder of radius `= "R_keepout"` about **`AX_Prop`** to see the exclusion zone in 3-D.
3. *Authoritative:* confirm **`arm_clear` ≥ 0** and **`sw_clear` ≥ 0** — the arming plug and on/off switch (both top, external, near centerline) sit ≥ 9 in aft of the prop disk.

**12.5 — Propulsion envelope** `[R §9]`.
1. Confirm the **4S LiPo bay** (`bat_L×W×H`) walls are smooth — no protrusions that could penetrate the pack — and add a reference line for the **retention strap** (positively secured).
2. Keep the **450 W power limiter** location accessible/inspectable.
3. `n_cells = 4` and `P_limit = 450` are documentation globals; size the prop/gearing for **static thrust** toward the ≤ 10 ft takeoff (offline, §10), not top speed.

**12.6 — Ballast outside the container** `[R §2]`.
- Confirm **`PT_Ballast`** lies **outside** the installed container (ballast inside the payload container is prohibited) — an **off-model check**, since the container is not modeled. Use it to trim the actual CG into the band (§11).

**12.7 — Wingspan: penalty, not cap** `[R §9]`.
- There is **no `b_max`** — don't build a span-limit construction. The **`span_ft`** readout mirrors the scoring penalty $Z = -S$; keep `b` minimal for the area you need (Micro favors low-AR, big-chord).

**12.8 — Final compliance sign-off.** Confirm every item, then commit/lock (§10):
- [ ] Payload container volume ≥ 67 fl oz (1981 cm³) — **off-model check**, verified on the physical container; not dimensioned in the skeleton
- [ ] `arm_clear ≥ 0` and `sw_clear ≥ 0` (9-in prop keep-out)
- [ ] external **bottom** drain, gravity-fed, ≤ 60 s, no squeezing
- [ ] container **non-structural**; airframe flightworthy empty
- [ ] **ballast outside** the payload container
- [ ] 4S LiPo / 450 W documented; battery secured, no penetrating protrusions
- [ ] loaded **and** drained actual CG inside `PT_CG_fwd…PT_CG_aft` (§11)
- [ ] span minimized (no cap to hit)

> Always re-verify against the **current official rules PDF** and confirm your class — figures (volumes, distances, power, cell count) change year to year. The takeoff-distance multipliers in particular came from a table that was garbled in the rules conversion; check them before they reach any scoring model.

This completes §1–§12: an empty part is now a fully parametric, rule-compliant Micro skeleton that drives the entire airframe from one edit.

---

## 13. Validation checklist

Run this as a repeatable **acceptance test** before you release the skeleton or hand it to the team. Each check below is the exact action, the expected result, and the fix if it fails. Budget ~15 minutes.

**13.1 — Sketch & feature integrity.** Scan the FeatureManager tree for prefixes: `(-)` = under-defined, `(+)` = over-defined, `(?)` = unsolvable; **fully defined sketches have no prefix**. Then right-click the top of the tree ▸ **What's Wrong** to list any feature errors/warnings. In each sketch, run **Display/Delete Relations** ▸ filter **Dangling** to catch orphaned relations.
- *Expected:* no prefixes, no errors, no dangling relations.
- *Fix:* add relations/dimensions to under-defined sketches; remove conflicts from over-defined ones.

**13.2 — Everything parametric (no hard-typed dimensions).** Equation-driven dimensions display with a **Σ** link marker (and a distinct color); a bare numeric dimension is hard-typed. Visually scan, but the real proof is 13.3.
- *Fix:* link any bare dimension to its global (`= "…"`).

**13.3 — Parametric behavior (perturbation test).** **Tools ▸ Equations**: change `b` by +100 mm ▸ OK ▸ **Ctrl-Q**. Watch the planform, rib pattern, tail, MAC, and CG points all move. Then change `n_rib` (7 → 9) and confirm the rib pattern **re-counts**; change `c_tip` (taper) and confirm the planform re-shapes. **Then flex the two decoupled vertical chains:** change `wheel_main` (60 → 100 mm) and confirm the front-view tire rectangles **grow while their bottoms stay flush** on the Ground Line (the axle rides up because `gear_h = "wheel_main" / 2`); change `y_motor_offset` (−20 → −45 mm) and confirm the prop disk, the 9-in ring, **and** the Ground Line all **drop together** so the thrust axis stays `h_thrust` above the ground and `prop_clear` is defended — with **no rebuild errors, no blue geometry, and no over-defined (+) flags**. **Then flex the fuselage double-dodecagon:** change `h_fuse_top` (35 → 20 mm) and confirm the two cabin keels, both vertical nose/tail flats, and all four side breakpoints (`M1`–`M4`) **hold their absolute heights** (`h_*_break_*`) while the keels re-balance about the waterline and the four **shoulder splines stay tangent** (no facets return) — confirm each break still sits inside the new keel window (they do **not** auto-track `h_fuse_top`); **sweep `w_fuse` (110 → 140 mm)** and confirm the planform dodecagon scales in lockstep — cabin corners (`CL`/`TL`) hold `w_fuse / 2`, the nose flat (`NL`) holds `w_fuse / 4`, and the lateral breaks (`P1`/`P2`) **hold the absolute `w_fuse_break`** and do **not** scale with `w_fuse` — confirm they stay inboard of the new cabin half-width (`w_fuse / 2`); a break now at or outboard of the cabin means `w_fuse_break` needs lowering; the tail cap (`EL`) is **independent** — it holds `tail_exit_D / 2` and must **not** move when `w_fuse` sweeps. Nudge `x_fuse_tail` (±50 mm) and confirm the tail cap, mid-tail breaks, and both mid-transition cross-sections track while `L_fuse` (now derived, `= "x_fuse_nose" + "x_fuse_tail"`) follows — all with **no wing rib plane moving** (fuselage stays decoupled). **Undo all** (or reset the values).
- *Expected:* every dependent feature tracks; nothing stays stuck.
- *Fix:* anything that doesn't move has a hard-typed dimension (13.2) — link it.

**13.3.5 — Empennage flex & twist test.** Extend the §13.3 perturbation to the tail. **Tools ▸ Equations**: bump `b_HT` (+50 mm), `b_VT` (+40 mm), and `sweep_VT` (20 → 25°), then **`Ctrl + Q`**.
- *Expected:* the HT planform and `SURF_HTail_OML` grow spanwise; the fin and `SURF_VTail_OML` grow **upward in $+Y$** and their swept edges rake further aft; `AX_HTspar_3D` / `AX_VTspar_3D` and the `3C_TAIL_PLANES` planes track; both tail surfaces stay clean — no self-intersection, no twist — and the **wing rib planes and fuselage stations do not move** (empennage stays decoupled).
- *Fix (twist / corkscrew):* a loft that spirals means the profile sync handles anchored to different clock vertices — reopen the loft and drag each green handle to the same LE vertex (§14 item 20).
- *Fix (dangling):* a `->x` on a tail rail, or "guide curve does not intersect a profile," means a rail endpoint is not welded to a shared curve vertex — re-check LE/TE closure in the tail streams (§8.1 / §8.6 Part B; §14 item 22).
- *Fix (vertical-axis):* if the fin grows sideways instead of up, its section planes or its Excel columns used $X$ for span — rebuild on the $+Y$ map (§7.3.8 / §8.6 Part A; §14 item 21).
- *Body-free:* re-run Mass Properties — the two new surfaces must add **0.00 g** (§13.8).

**13.3.6 — Hinge-line & servo-envelope check.** After the §13.3 perturbation, validate the §7.7 control geometry.
- **Dihedral-match:** **Measure** `AX_Hinge_Ail` end-to-end and read the X/Y/Z breakdown — the **$\Delta Y / \Delta X$ ratio must equal $\tan(dihedral)$** (a non-zero $\Delta Y$), i.e. the hinge climbs on the *same* slope as the wing. A $\Delta Y = 0$ means the hinge is still a flat 2-D line — rebuild it as a true 3-D axis (§7.7.2). Bump `dihedral` (4 → 6°) ▸ **`Ctrl + Q`** and confirm the hinge slope re-tilts to match the wing.
- **Span-tracking:** change `ail_out_pct` (0.95 → 0.90) ▸ **`Ctrl + Q`** and confirm `PT_Ail_Outboard`, `AX_Hinge_Ail`, and the servo bay all slide inboard together; undo.
- **Skin-breach:** re-run the §7.7.3 Intersection-Curve overlay — the `servo_H` box must stay inside `SURF_Wing_OML`. Bump `servo_H` until it breaches to prove the audit catches it, then restore.
- **Body-free:** Mass Properties still **0.00 g** — all control geometry is construction / reference (§13.8).
- *Fix:* a hinge that will not tilt has a stray flat relation (§14 item 23); a servo dimension that will not drive is a dangling `= "servo_*"` link — the globals are not yet in the equations file (§7.7 intro; §14 item 24).

**13.3.7 — Structural-datum rebuild check (§7.10–§7.12).** Prove the wing-mount and bulkhead datums stay locked to their drivers under a hard flex. **Tools ▸ Equations**: scale the wingspan `b` (+120 mm) **and** change a landing-gear variable (`x_main` 40 → 55, `track` 260 → 300), then force a full **`Ctrl + Q`** rebuild.
- *Expected:* the rebuild completes **clean** — no `->x` dangling markers, no yellow over-defined flags. `AX_MainSpar` / `AX_Rspar` lengthen with `b`, but the **root-anchored** datums hold: `PLN_Bhd_Main` stays on `x_spar_root`, `PLN_Bhd_Aft` on `x_rspar_root`, and the `LAY_Wing_Mounts` bolt pierces stay welded to the spar axes (a root-chord datum should **not** move when only the tip extends — that is correct, not a fault).
- *Gear-offset re-check:* after the `x_main` change, **Measure** `PLN_Bhd_Main` → `AX_GearAxle` along $Z$ and confirm the offset is still inside your frame width (§7.11); if not, co-locate the gear or add the bridging longeron.
- *Body-free:* **Tools ▸ Evaluate ▸ Mass Properties** → the skeleton must still read **0.00 g** with an **empty Solid Bodies folder** — the seat planes, bulkheads, and bolt circles are reference / sketch geometry only (§13.8).
- *Fix:* a dangling `->x` on a bolt pierce means its spar axis was renamed or deleted — re-pierce onto `AX_MainSpar` / `AX_Rspar` (§7.10); a bulkhead that drifts on a `b` flex was built off a span-dependent reference instead of `x_spar_root` / `x_rspar_root` — rebuild it on the root-chord global.

**13.3.8 — Systems-clearance rebuild check (moved to Installation).** Fill / belly / steering clearance validation is an installation concern → **Installation guide §I-7**.

**13.4 — Convention check.** Open `LAY_Front_View` ▸ **Normal To** — confirm it's the span×height view (front view on the **Front Plane**). Confirm mirrored features mirror across the **Right Plane** (X = 0). Use **Tools ▸ Evaluate ▸ Measure** from a station point to the Origin and confirm it reports a **Z** distance. Triad reads **X-port / Y-up / Z-forward** (starboard = −X). **Rib-plane true-pitch check:** **Measure** the normal distance between two adjacent rib planes (`PLN_RibStn_R01` → `PLN_RibStn_R02`) — it must report the **true along-spar pitch** $= rib\_pitch/(\cos\Gamma\,\cos\Lambda_{spar})$, i.e. slightly **greater** than the flat `rib_pitch`, and the Measure X/Y/Z breakdown must show a **non-zero $\Delta Y$** from dihedral. A reading of exactly the flat `rib_pitch` with $\Delta Y = 0$ means the planes are still flat normal-to-X and must be rebuilt **Normal to Curve** on `AX_MainSpar_3D` (§7.3).
- *Fix:* re-mirror across the Right Plane; re-apply stations along Z (§2 crosswalk); rebuild any flat rib planes as **Normal to Curve** on `AX_MainSpar_3D` (§7.3).

**13.5 — Numerical correctness (hand-calc cross-check).** In **Tools ▸ Equations**, read the derived values and compare to the §3.5 sanity table (`MAC ≈ 245`, `y_MAC ≈ 252`, `S_w ≈ 264 000`, `AR ≈ 4.58`, `S_HT ≈ 53 900`, `b_HT ≈ 464`). Then **back-check the tail volume coefficients**:

$$V_H = \frac{S_{HT}\,l_{HT}}{S\,\bar c} \stackrel{?}{=} 0.50, \qquad V_V = \frac{S_{VT}\,l_{VT}}{S\,b} \stackrel{?}{=} 0.04$$

- *Expected:* values match the table and the coefficients return your inputs.
- *Fix:* a mismatch means a units error (§3.1) or a mistyped equation.

**13.6 — Micro compliance.** In **Tools ▸ Equations** confirm `arm_clear ≥ 0`, `sw_clear ≥ 0` (§12).
- *Fix:* move the plug/switch station aft of the keep-out.

**13.7 — Stability / CG band.** Confirm `x_NP` is set (not 0) from XFLR5/AVL. In the **assembly** (§11), run **Tools ▸ Evaluate ▸ Mass Properties** in both `Loaded` and `Drained` and confirm **both** actual CGs fall between `PT_CG_fwd` and `PT_CG_aft`, i.e. $SM=(x_{NP}-x_{CG})/\bar c \in [SM_{min},SM_{max}]$.
- *Fix:* move the water-mass centroid `x_bay` toward the CG or trim with ballast (`PT_Ballast`, outside the container).

**13.7.5 — Dynamic CG travel-band check (§7.8 markers).** Confirm the water-drop CG walk stays legal end to end. **Measure** the $Z$ station of `PT_CG_loaded`, `PT_CG_drained`, and `PT_CG_empty`, and confirm **all three lie between `PT_CG_fwd` and `PT_CG_aft`** — the loaded *and* drained states in particular must never cross a limit, since the aircraft flies through both.
- *Expected:* the three markers sit inside the band; the drained/empty markers shift off the loaded station in the direction set by whether `x_bay` is forward or aft of `x_CG`.
- *Flex test:* in **Tools ▸ Equations** drive `W_water` toward 0 ▸ **`Ctrl + Q`** and confirm `PT_CG_loaded` walks onto the `PT_CG_drained` station (an empty bay = drained); restore.
- *Fix:* if drained or empty leaves the band, shift `x_bay` toward `x_CG`, add ballast (`PT_Ballast`, outside the container), or re-split the payload; re-confirm $SM = (x_{NP} - x_{CG}) / MAC \in [SM_{min}, SM_{max}]$ for **every** state, not just loaded.
- *Body-free:* the three markers and the §7.8 door overlay are construction / reference only — Mass Properties stays **0.00 g** (§13.8).

**13.7.6 — Taildragger stance & prop-clearance (moved to Installation).** Gear stance and prop-ground clearance validation → **Installation guide §I-7**.

**13.8 — Body-free check.** **Tools ▸ Evaluate ▸ Mass Properties** on the skeleton → mass ≈ 0. The **Solid Bodies** folder must be empty (a **Surface Bodies** folder is fine).
- *Fix:* delete or convert any stray solid body (§10.7).

**13.9 — File & reference health.** **File ▸ Find References** — confirm every path is inside the project folder. **File ▸ Pack and Go** to a temp folder, reopen the packed assembly, and confirm **no `->x`** broken refs anywhere.
- *Fix:* re-path stray references; only ever relocate via Pack and Go (§10.4).

**13.10 — Sign-off & lock.** All checks pass → bump the **Revision** custom property, **lock** the external references of frozen subsystems (§10.5), update the date/rev in the `LAY_Datums` note, and commit / check in.

---

## 14. Common pitfalls

Each is framed as **Detect → Fix → Prevent** so it's actionable when you hit it.

**1. Mixing the axis convention.** With the front view on the Front Plane, longitudinal is **Z**, span is **X**, height is **Y**.
- *Detect:* the airframe looks rotated; **Measure** a known station to the Origin and it reports the wrong axis; derived parts come in rotated.
- *Fix:* open the offending sketch, delete the wrong-axis dimension, re-dimension along the correct axis (§2 crosswalk).
- *Prevent:* keep the §2 crosswalk visible; pin the `LAY_Datums` note; Measure your first few stations.

**2. Mirroring across the wrong plane.** Symmetry is the **Right Plane** (X = 0), not the Front Plane.
- *Detect:* the mirrored half is flipped fore/aft or stacked vertically; wings overlap or splay.
- *Fix:* delete the bad **Mirror Entities**; redo it with the **Z centerline** as the mirror line.
- *Prevent:* verify the mirror line is X = 0 before accepting.

**3. "Locate part with Move/Copy" left checked on Insert Part.** Parts then come in offset and won't mate origin-to-origin.
- *Detect:* a derived part is displaced from the origin; assembly mates fight you.
- *Fix:* delete the base (imported) feature and re-run **Insert Part** with that box **unchecked**.
- *Prevent:* always uncheck it (§9.1) so parts derive at the coincident origin.

**4. Units not MMGS before importing equations.** Lengths load wrong.
- *Detect:* `MAC`, `S_w`, etc. are off by ~25.4× or nonsensical after import.
- *Fix:* set **Document Properties ▸ Units ▸ MMGS**, then re-Import the equation file.
- *Prevent:* confirm MMGS first (§3.1); use the team template (§1.2).

**5. Angle used in math without converting to radians.** Sweep/incidence geometry comes out wrong.
- *Detect:* the tip-LE sweep offset or a trig-driven value is far off.
- *Fix:* wrap the angle in `*pi/180` inside the equation (e.g. `tan("sweep_LE"*pi/180)`).
- *Prevent:* store angles as plain degrees; convert only inside math; link angles directly to angular *dimensions* with no conversion (§2.6/§3.6).

**6. One mega-sketch / hard-coded dimensions.**
- *Detect:* slow rebuilds; the §13.3 perturbation test leaves features stuck.
- *Fix:* split into per-view `LAY_` sketches; link bare dimensions to globals.
- *Prevent:* one sketch per view/subsystem; always dimension `= "global"`.

**7. In-context circular references.**
- *Detect:* a "circular references" rebuild error; features that won't resolve; a part driving the skeleton.
- *Fix:* **List External Refs**, break/re-route the offending in-context ref; convert the part to a derived (Insert Part) part.
- *Prevent:* use Insert Part (§9.1), not in-context; turn off "Allow multiple contexts" (§10.2); skeleton references nothing downstream.

**8. Renaming/moving files outside Pack-and-Go.**
- *Detect:* `->x` broken refs and "unable to locate" prompts on open.
- *Fix:* **File ▸ Find References ▸ Replace** to re-point, or re-run **Pack and Go**.
- *Prevent:* relocate only via Pack and Go (§10.4); never Windows-rename linked files.

**9. Under-defined sketches (and freeform curves in layout sketches).**
- *Detect:* a `(-)` prefix in the tree; geometry shifts when you drag or change a parameter. A **spline or arc drawn into a layout sketch** is the usual hidden culprit — its control points/handles carry free degrees of freedom that wander on every rebuild and can make a fuselage loft self-intersect.
- *Fix:* add relations/dimensions until the sketch is black (**Fully Define Sketch** can help — review what it adds); any layout spline must be **fully pinned** — endpoints and interior control points dimensioned to globals, plus **Tangent** relations at its junctions (§4.4) — otherwise replace it with a straight construction line.
- *Prevent:* fully define every sketch before exiting (§13.1). The §4.4 side profile now uses **Style Splines for its four shoulders**, but they are safe because every control point is pinned to a global and welded **Tangent** to its neighbours — that is what stops them wandering. Hold any other layout curve to the same standard (fully dimensioned + tangent) or use straight construction lines; the OML still takes its primary curvature from the §8.5 surface loft riding this cage.

**10. Ignoring the drained CG.** Water leaving mid-mission shifts the CG.
- *Detect:* trims fine full, goes tail-heavy/unstable as it drains; you only ever checked the Loaded config.
- *Fix:* switch to the **Drained** config, run Mass Properties, confirm CG in band; move `x_bay` toward the CG or add ballast.
- *Prevent:* always check both Loaded and Drained (§11.5/§13.7); keep the water-mass centroid near the CG.

**11. Plug/switch inside the 9-in prop keep-out.** A hard safety rule.
- *Detect:* `arm_clear` or `sw_clear` < 0 in the Equations dialog; inside the keep-out ring.
- *Fix:* move `x_arm_plug`/`x_switch` aft until the clearances are ≥ 0, or mount them radially outboard of the prop disk.
- *Prevent:* bake `arm_clear`/`sw_clear` into the checks early; place both well aft on top.

**12. Flat (normal-to-X) rib planes on a dihedral/swept wing.** Offsetting rib planes from the Right Plane ignores the true spar tilt, so ribs come in skewed to the real spar.
- *Detect:* **Measure** between adjacent `PLN_RibStn_*` planes returns exactly the flat `rib_pitch` with a **zero $\Delta Y$**; ribs derived on the planes don't sit square to the spar and leave wedge gaps under the skin.
- *Fix:* rebuild the planes **Normal to Curve** on the true 3D axis `AX_MainSpar_3D` at each §5.5 station point (§7.3); re-confirm the §13.4 true-pitch measurement.
- *Prevent:* always host rib planes on `AX_MainSpar_3D`, never a flat Right-Plane offset; keep the true-pitch check in the §13 sign-off. Build `AX_MainSpar_3D` before the planes (§7.2).

**13. Hard-pinning the thrust line to the wing-root waterline.** A Coincident/Collinear relation locking the prop/thrust center to the $Y = 0$ waterline freezes the motor at the wing-root height, so `y_motor_offset` can't move it — and if the Ground Line still hangs off the Origin, `prop_clear` silently breaks when the motor is meant to drop.
- *Detect:* editing `y_motor_offset` does nothing, or throws an over-defined **(+)** prefix, or the disk snaps back to the wing datum; **Display/Delete Relations** on the center point shows a **Coincident** to the waterline sitting alongside the `y_motor_offset` dimension.
- *Fix:* delete the stray waterline **Coincident/Collinear** on the thrust center (keep only its $X = 0$ coincident and the `y_motor_offset` vertical dimension); re-anchor the Ground Line `= "h_thrust"` off the **thrust center**, not the Origin (§6.7 Phase 2).
- *Prevent:* dimension the thrust center to the waterline with `= "y_motor_offset"` in **every** view (§4.5, §6.6, §7.3.5) and hang the Ground Line off that center — never pin the axis to $Y = 0$.

**14. Shoulder-spline bulge / reversal (dodecagon).** A shoulder breakpoint (`M1`–`M4`) height set to or past its keel value bows the shoulder spline out to (or beyond) the keel line — a local bulge or taper reversal instead of a clean blend; a break station pushed past its cabin face folds the spline back on itself. Keep each break strictly inside its keel-to-flat window (§4.4 Phase 5).
- *Detect:* a transition segment "disappears," two segments read as one line, or the sketch throws an over-defined **(+)** prefix after you edit a break.
- *Fix:* re-dimension the breakpoint height strictly between the apex-flat half-height and the full keel height (default `* 3 / 4`), and keep its station between the apex column and the cabin-face column (§3 / §4.4 Phase 5).
- *Prevent:* never set a breakpoint height `= "h_fuse_top"` or `= "h_fuse_bottom"`; keep every break inside its zone.

**15. Dangling relations from an apex-to-flat split.** Converting a sharp apex into a vertical flat — or editing the end geometry — orphans any relation that referenced the old single apex vertex, including the §8.5 end-cap pierces.
- *Detect:* `SET_Fuse_Nose` / `SET_Fuse_Tail` (or `SURF_Fuse_OML`) flag a rebuild error; **Display/Delete Relations** ▸ filter **Dangling** lists orphaned pierces.
- *Fix:* clear the dangling relations, then re-pierce the end-cap top / bottom quadrants to the current `NT`/`NB` (`TT`/`TB`) flat-face vertices (§8.5 Phase 2).
- *Prevent:* after any §4.4 end-geometry edit, run **What's Wrong** and the Dangling filter before rebuilding the downstream loft (§13.1).

**16. Unconstrained breakpoint drift (blue sketch entities).** A transition breakpoint left with an open degree of freedom wanders on every rebuild and can make the fuselage loft self-intersect.
- *Detect:* a `(-)` prefix on `LAY_Side_Profile`; `M1`–`M4` or a flat vertex shows **blue**; the shoulder shape shifts when an unrelated global changes.
- *Fix:* give each breakpoint both its **column** ($Z$, via the Vertical relation + one dimension) and its **height** ($Y$) dimension; give each flat its **Vertical** relation and both endpoint heights (§4.4 Phases 2, 4, 5).
- *Prevent:* fully define `LAY_Side_Profile` before exiting (§13.1); add the missing *relation* first, then the dimension — never a stray extra dimension.

**17. Horizontal breakpoint drift (planform dodecagon).** A planform break (`P1`/`P2`) or flat vertex (`NL`/`EL`) left short a dimension wanders laterally on rebuild, warping the fuselage width envelope.
- *Detect:* a `(-)` prefix on `LAY_Wing_Plan`; `P1`/`P2`/`NL`/`EL` shows **blue**; the footprint width shifts when an unrelated global changes.
- *Fix:* give every port vertex both its **column** ($Z$ to the datum, §5.3.5 Phase 2) and its **width** ($X$ to the centerline, §5.3.5 Phase 3), then re-confirm the mirror closed (Phase 4).
- *Prevent:* fully define the port chain before mirroring; keep `P1`/`P2` at `= "w_fuse_break"` — strictly inboard of the cabin's `w_fuse / 2`.

**18. Cross-section rail mismatch (height and width off different stations).** A section whose height pierces one column while its width rail pierces a planform segment from a *different* station skews and can self-intersect the loft.
- *Detect:* an ellipse tilts or refuses to go black; **Display/Delete Relations** shows the height pierce and the width rail resolving to different $Z$ values; the loft preview kinks at that section.
- *Fix:* confirm each section sits on the correct `PLN_Fuse_*` plane and that its height entity and width segment belong to the **same** column per the §8.5 Phase 1 table (e.g. `MidNose` → `M1`/`M4` **and** `P1`).
- *Prevent:* build one section per plane straight from the table; never reuse a rail anchor across planes.

**19. Loft twisting from misaligned ellipse quadrant selections.** Picking a different relative quadrant on each profile makes the loft connect top-to-side and corkscrew the skin.
- *Detect:* the OML visibly spirals between sections; the green sync handles on the loft profiles point to different clock positions.
- *Fix:* in the Loft PropertyManager, drag each profile's green sync handle to the **same** vertex (e.g. every top quadrant), or re-pick each profile by clicking near the same relative point.
- *Prevent:* when selecting the six profiles, always click near the **same quadrant** (§8.5 Phase 3, step 3); keep every ellipse symmetric about the Right Plane so the quadrants are unambiguous.

**20. Twisted empennage loft (misaligned sync handles).** Picking a different relative vertex on the root vs. tip tail section makes the loft connect LE-to-TE and corkscrew the skin — the fin is especially prone because its sections stack vertically.
- *Detect:* `SURF_HTail_OML` / `SURF_VTail_OML` visibly spirals; the loft's green sync handles point to different clock positions on root vs. tip.
- *Fix:* in the Loft PropertyManager, drag each profile's green handle onto the **same** vertex (both LE), or re-pick each profile near the same relative point (§8.6 Part C).
- *Prevent:* always click both tail profiles near the **LE vertex**; keep each section symmetric about its plane so the vertices are unambiguous.

**21. Vertical-axis confusion (building the fin like a wing).** The VT spans **up $+Y$**, not laterally along $X$. Treating its span as $X$ — offsetting section planes laterally, or leaving the wing's `=$G$1`→SW-$X$ span map in the VT Excel columns — lays the fin on its side.
- *Detect:* the fin renders horizontal or grows sideways on a `b_VT` bump; **Measure** `PLN_VT_Root` → `PLN_VT_Tip` reports the gap in $X$, not $Y$; the VT curves import lying flat.
- *Fix:* rebuild the VT section planes as **$+Y$** offsets from the Top Plane (or Normal-to-Curve on `AX_VTspar_3D`), and swap the VT Excel columns to the $+Y$ map — span → SW $Y$ (`= $G$1 + $K$1`), thickness → SW $X$ (`= B3 * $E$1`), chord → SW $Z$ (§8.6 Part A).
- *Prevent:* keep the §8.6 Part A axis-map table in view; run the §7.3.8 vertical-axis guard (Measure resolves in $Y$) before lofting.

**22. Dangling empennage relations (tail rails lose their vertices).** Re-exporting a tail airfoil, or editing a tail global, can orphan a guide-rail endpoint that referenced an old curve vertex — the same failure class as the fuselage end-cap pierces (§14 item 15).
- *Detect:* `LAY_HT_Guides_3D` / `LAY_VT_Guides_3D` or a tail loft flags a rebuild error; **Display/Delete Relations** ▸ filter **Dangling** lists orphaned endpoints; the loft throws "guide curve does not intersect a profile."
- *Fix:* clear the dangling relations and re-weld each rail endpoint to the current shared LE/TE curve vertex (§8.6 Part B); confirm the tail airfoil streams still share exact LE/TE rows (§8.1 closure).
- *Prevent:* after any tail-airfoil re-export or empennage-global edit, run **What's Wrong** + the Dangling filter before rebuilding the tail lofts (§13.1 / §13.3.5).

**23. Unconstrained hinge line (flat or drifting 3-D axis).** A hinge line left on the Top Plane, or a 3-D hinge endpoint short a relation, either sits at $Y = 0$ (ignoring dihedral) or wanders on rebuild — the surface then binds and gaps through its travel.
- *Detect:* `LAY_Wing_Incidence` shows a `(-)` prefix or a **blue** hinge endpoint; **Measure** `AX_Hinge_Ail` returns $\Delta Y = 0$; the aileron pivots on an axis that does not match the wing dihedral.
- *Fix:* draw the hinge on `PLN_Dihedral` (§7.7.2) and dimension each end's span to the **Right Plane** and chord to the **Front Plane** — the plane then supplies the dihedral $Y$ by construction.
- *Prevent:* never draw a hinge as a flat Top-Plane line; build it on `PLN_Dihedral` (§7.7.2) so it inherits the wing dihedral by construction, and keep the §13.3.6 $\Delta Y / \Delta X = \tan(dihedral)$ check in sign-off.

**24. Installation pitfalls (moved to Installation).** The servo, payload drop-door, landing-gear, and clearance/linkage pitfalls (former items 24–34) now live in the **Installation guide** (§I-8), beside the sections that produce them.

---

### Suggested first session (30–45 min)
Set the convention (§1–2, note the Front-Plane front view + Right-Plane symmetry) → Import `skeleton_equations_micro.txt` (§3) → planform with MAC/CG (§5) → side profile with drain port + plug/switch stations (§4) → front view with dihedral, prop disk + keep-out, gear track (§6) → rib planes + key axes + hardpoints (§7). Lock it, run the §13 checklist (especially the three compliance checks), then hand it to structures to derive ribs/spars via Insert Part (§9.1).
