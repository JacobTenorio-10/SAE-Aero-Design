# Aircraft Skeleton — Parameters, Global Variables & Equations

<details>
<summary><b>SAE Aero Design 2026 · <b>Micro Class</b> · SolidWorks skeleton-driven model</b></summary>

### SAE Aero Design 2026 · **Micro Class** · SolidWorks skeleton-driven model
Tailored to the **2026 SAE Aero Design rules, Section 9 (Micro Class Design Requirements)** and the general aircraft/flight rules that apply to Micro. Rule-driven constraints are cited inline as `[R]`. The full copy-paste SolidWorks block is in **Appendix A**; a matching `skeleton_equations_micro.txt` is provided alongside (Appendix A is kept **byte-identical** to it).
> **What's different for Micro vs. the generic version**
> - **No maximum wingspan**, but span is a **direct scoring penalty** ($Z=-S$, $S$ in ft) — so you *minimize* span, not cap it. The old `b_max`/transport-box variables are removed. `[R: §9 Aircraft Dimension Requirements]`
> - **Payload is liquid water** in one sealed container, **min 67 fl oz ≈ 1981 cm³**, top fill hole + bottom drain hole, plus an **external bottom drain port**. The container is **not modeled in CAD** — it is carried as mass only, and its volume is verified off-model on the physical part. `[R: §9 Payload Requirements]`
> - **Electric only**, **LiPo ≤ 4 cells**, **450 W power limiter** (NeuRacing, 2021+). `[R: §9 Aircraft Systems]`
> - **Takeoff scored in distance bins** (10/25/50/100 ft); **>100 ft = DQ**. Short field is everything. `[R: §9.5]`
> - **9-inch (228.6 mm) prop keep-out** for the red arming plug and RX on/off switch, both on top/exterior near centerline. New compliance hardpoints + checks. `[R: §2 Red Arming Plug / On-Off Switch]`
> - **Micro TDS** requires neutral-point and static-margin plots → keep `x_NP` and `SM` honest. `[R: §TDS Aircraft Performance Prediction]`
---

</details>

<details>
<summary><b>How to use this</b></summary>

## How to use this
- **Set document units to MMGS** (mm · gram · second). Lengths = mm, masses = g, water volume in cm³ (= mL).
- **Reference other variables in quotes:** `"b"`, `"MAC"`.
- **`sqr(x)` is SQUARE ROOT** (use `x^2` to square). `pi` is built in. `abs()` available.
- **Angles** stored as plain numbers in degrees; link directly to angular dimensions, convert only inside math: `tan("sweep_LE"*pi/180)`. **This requires Angular equation units = Radians** (Tools ▸ Equations) — see the radians rule below.
- **All longitudinal `x_*` globals are positive distances from the origin at the wing-root LE.** Coordinate system: **+Z forward (nose), −Z aft (tail), +Y up, +X port**. Place each station on the +Z (forward) or −Z (aft) side; the dimension references the positive global directly.
- **Inputs vs derived:** never hard-type what an equation can produce. Geometry-first here (input $b$, $c_r$, $c_t$); §10 gives the performance-first flip.
- **Offline (SI) block:** aero/takeoff sizing in §10 is unit-messy in MMGS — keep it in your sizing spreadsheet and feed `b`, `c_root`, `c_tip` back in.
---
> **The positive-magnitude rule.** **No value in `skeleton_equations_micro.txt` is ever negative** — angles included. Every global is a magnitude; direction is carried by the model (which side of a datum a dimension is placed, a plane's **Flip** toggle, a pattern's direction arrow), never by a stored sign. `i_HT` = 2.0 is nose-down because `PLN_Incidence_HT` is flipped that way, and `twist_tip` is a positive washout magnitude that `i_tip` **subtracts**. Formulas may contain a minus operator; values may not be negative. `check.py` enforces this with no exemptions.

> **The one-variable rule.** Every SolidWorks Smart Dimension, plane **Offset Distance**, and **Modify** box takes exactly **one** global — `= "some_global"` — never an expression. All derivation lives in `skeleton_equations_micro.txt`. If a dimension needs a computed value, that computation gets its own named global here first. The **Derived-for-dimensioning** globals below exist purely to satisfy this rule: each one wraps a formula that used to be typed into a dimension box.

> **The radians rule.** Trig arguments in this file are converted explicitly, so the SolidWorks **Angular equation units** drop-down (Tools ▸ Equations) must be set to **Radians** in every document that carries this equation set. It is a per-document setting and SolidWorks defaults it to **Degrees**, which converts a second time and silently collapses every swept station toward zero — no error, just wrong geometry. `check.py` cannot read the drop-down, so it enforces the half it can see: no trig call in the file may be written without its `pi/180` conversion. Verify by eye after import — the **Value** column for `x_LE_tip_inc` reads *(≈112.0000)* mm, not *(≈1.93)* mm.

</details>

<details>
<summary><b>1. Wing planform</b></summary>

## 1. Wing planform
**Inputs**
| Variable | Symbol | Description | Units | Starter |
|---|---|---|---|---|
| `b` | $b$ | Wingspan — **no cap, but penalized → minimize** `[R §9]` | mm | 1150 |
| `c_root` | $c_r$ | Root chord | mm | 225 |
| `c_tip` | $c_t$ | Tip chord | mm | 225 |
| `sweep_LE` | $\Lambda_{LE}$ | Leading-edge sweep, over `b_semi` | deg | 12.2004687 |
| `dihedral` | $\Gamma$ | Dihedral angle (inboard) | deg | 4.0 |
| `i_wing` | $i_w$ | Wing incidence / setting angle | deg | 0.0 |
| `twist_tip` | $\varepsilon_t$ | Tip washout (neg = washout) | deg | 0.0 |
**Derived**
| Variable | Symbol | Equation | Units |
|---|---|---|---|
| `b_semi` | — | **absolute** 518 — main lifting-panel semi-span on `PLN_Dihedral`; $b/2 = 575$ is the developed semi-span (518 panel + 57 mm vertical tip, winglet built downstream) | mm |
| `taper` | $\lambda$ | $c_t/c_r$ | — |
| `S_w` | $S$ | $\tfrac{(c_r+c_t)}{2}\,b$ | mm² |
| `AR` | $AR$ | $b^2/S$ | — |
| `MAC` | $\bar c$ | $\tfrac{2}{3}c_r\tfrac{1+\lambda+\lambda^2}{1+\lambda}$ | mm |
| `y_MAC` | $y_{\bar c}$ | $\tfrac{b}{6}\tfrac{1+2\lambda}{1+\lambda}$ | mm |
| `x_MAC_LE` | $x_{\bar c,LE}$ | $y_{\bar c}\tan\Lambda_{LE}$ | mm |
| `x_MAC_c4` | $x_{\bar c,c/4}$ | $x_{\bar c,LE}+0.25\,\bar c$ | mm |
$$S = \frac{(c_r + c_t)}{2}\,b, \quad AR = \frac{b^2}{S}, \quad \bar c = \frac{2}{3}c_r\frac{1+\lambda+\lambda^{2}}{1+\lambda}, \quad y_{\bar c} = \frac{b}{6}\cdot\frac{1+2\lambda}{1+\lambda}$$
Local chord at spanwise station $y$ (drives rib chords / spar line): $\;c(y) = c_r\left[1-(1-\lambda)\tfrac{2y}{b}\right]$
**Micro note:** because span is penalized and area still has to lift ~2 kg of water off a short field, Micro wings trend to **low aspect ratio** (≈4–5) with large chords and aggressive high-lift, rather than high-AR efficiency wings.
---

</details>

<details>
<summary><b>2. Wing structure (ribs &amp; spars)</b></summary>

## 2. Wing structure (ribs & spars)
**Inputs**
| Variable | Description | Units | Starter |
|---|---|---|---|
| `spar_main_pct` | Main spar location | %chord | 0.25 |
| `spar_rear_pct` | Rear spar / shear web | %chord | 0.70 |
| `n_rib` | Ribs per semi-span (incl. root & tip) | — | 7 |
| `rib_root_off` | First rib offset from centerline | mm | 20 |
| `rib_thk` | Rib material thickness (1/16 in wood) | mm | 1.5875 |
| `rib_thk_div` | Divider-rib thickness (1/8 in wood); separates flap from aileron | mm | 3.175 |
| `n_rib_div` | Divider-rib index, 1-based from the root rib | — | 4 |
| `hinge_gap` | Control-surface end to adjacent rib face clearance (1/16 in) | mm | 1.5875 |
| `sparcap_w` | Spar-cap width | mm | 6.0 |
| `sparcap_h` | Spar-cap height | mm | 6.0 |
| `web_thk` | Shear-web thickness | mm | 1.5 |
| `LE_sheet_pct` | LE sheeting extent | %chord | 0.30 |
| `tc_root` | Root airfoil thickness ratio (FX 74-Cl5-140 MOD) | — | 0.14 |
| `tc_tip` | Tip airfoil thickness ratio (FX 74-Cl5-140 MOD) | — | 0.14 |
**Derived**
| Variable | Equation | Units |
|---|---|---|
| `rib_pitch` | $\dfrac{b/2 - y_0}{\,n-1\,}$ | mm |
| `rib_root_off_physical` | $y_0\sqrt{1+\tan^2(\text{dihedral})+\left(\dfrac{\text{spar\_main\_pct}\,(c_r-c_t)}{b/2}\right)^2}$ | mm |
| `x_spar_root` | $\text{spar\_main\_pct}\cdot c_r$ | mm |
| `x_rspar_root` | $\text{spar\_rear\_pct}\cdot c_r$ | mm |
| `x_joiner_root` | $=x_{spar\_root}$ (co-located w/ main spar) | mm |
The spar lines are %chord: absolute spar-X at a station = LE-X + `spar_pct` × $c(y)$. Empty weight is heavily penalized `[R §9]`, so size ribs/caps/webs to the loads from servo-load and structural analysis, not by habit.
---

</details>

<details>
<summary><b>3. Horizontal tail</b></summary>

## 3. Horizontal tail
**Inputs**
| Variable | Symbol | Description | Units | Starter |
|---|---|---|---|---|
| `V_H` | $V_H$ | Horizontal tail volume coefficient | — | 0.98 |
| `l_HT` | $l_{HT}$ | Wing $c/4$ → HT $c/4$ moment arm — **now derived** from `x_tail_LE_root` | mm | 674.0878 |
| `AR_HT` | $AR_{HT}$ | HT aspect ratio | — | 2.35 |
| `taper_HT` | $\lambda_{HT}$ | HT taper ratio | — | 1.00 |
| `i_HT` | $i_{HT}$ | HT incidence | deg | −2.0 |
| `sweep_HT` | $\Lambda_{HT}$ | HT LE sweep | deg | 0.0 |
| `c_elev_pct` | — | Elevator chord fraction | — | 0.35 |
**Derived**
| Variable | Equation | Units |
|---|---|---|
| `S_HT` | $\dfrac{V_H\,S\,\bar c}{l_{HT}}$ | mm² |
| `b_HT` | $\sqrt{AR_{HT}\,S_{HT}}$ | mm |
| `c_root_HT` | $\dfrac{2\,S_{HT}}{b_{HT}(1+\lambda_{HT})}$ | mm |
| `c_tip_HT` | $c_{r,HT}\,\lambda_{HT}$ | mm |
| `MAC_HT` | $\tfrac{2}{3}c_{r,HT}\tfrac{1+\lambda_{HT}+\lambda_{HT}^2}{1+\lambda_{HT}}$ | mm |
| `y_MAC_HT` | $\tfrac{b_{HT}}{6}\tfrac{1+2\lambda_{HT}}{1+\lambda_{HT}}$ | mm |
| `x_HT_c4` | $x_{\bar c,c/4} + l_{HT}$ | mm |
| `x_HT_LE_root` | $x_{HT,c/4} - 0.25\,c_{r,HT}$ | mm |
$$S_{HT} = \frac{V_H\,S\,\bar c}{l_{HT}}, \qquad b_{HT} = \sqrt{AR_{HT}\,S_{HT}}, \qquad c_{r,HT} = \frac{2\,S_{HT}}{b_{HT}\,(1+\lambda_{HT})}$$
---

</details>

<details>
<summary><b>4. Vertical tail</b></summary>

## 4. Vertical tail
**Inputs**
| Variable | Symbol | Description | Units | Starter |
|---|---|---|---|---|
| `V_V` | $V_V$ | Vertical tail volume coefficient | — | 0.073 |
| `l_VT` | $l_{VT}$ | Wing $c/4$ → **fin MAC** $c/4$ moment arm — **now derived**, measured to the AC | mm | 701.0109 |
| `AR_VT` | $AR_{VT}$ | VT aspect ratio, **geometric single-sided** ($h^2/S_{VT}$; XFLR5 reports 2× this) | — | 1.54 |
| `taper_VT` | $\lambda_{VT}$ | VT taper ratio | — | 0.53 |
| `sweep_VT` | $\Lambda_{VT}$ | VT LE sweep | deg | 16.70 |
| `c_rud_pct` | — | Rudder chord fraction | — | 0.40 |
**Derived**
| Variable | Equation | Units |
|---|---|---|
| `S_VT` | $\dfrac{V_V\,S\,b}{l_{VT}}$ | mm² |
| `b_VT` | $\sqrt{AR_{VT}\,S_{VT}}$ (fin height) | mm |
| `c_root_VT` | $\dfrac{2\,S_{VT}}{b_{VT}(1+\lambda_{VT})}$ | mm |
| `c_tip_VT` | $c_{r,VT}\,\lambda_{VT}$ | mm |
| `MAC_VT` | $\tfrac{2}{3}c_{r,VT}\tfrac{1+\lambda_{VT}+\lambda_{VT}^2}{1+\lambda_{VT}}$ | mm |
| `x_VT_c4` | $x_{\bar c,c/4} + l_{VT}$ | mm |
| `x_VT_LE_root` | $x_{VT,c/4} - 0.25\,c_{r,VT}$ | mm |
$$S_{VT} = \frac{V_V\,S\,b}{l_{VT}}, \qquad b_{VT} = \sqrt{AR_{VT}\,S_{VT}}$$
---

</details>

<details>
<summary><b>5. Fuselage</b></summary>

## 5. Fuselage
Longitudinal stations are **positive distances** from the wing-root LE (forward $= +Z$, aft $= -Z$; placement side chosen per each global). The fuselage must house the propulsion battery and route the bottom drain port; the payload container is not modeled. The cross-section is a **dome-arch** profile, lifted so ~**75 %** of `h_fuse` sits above the waterline.

**Primary envelope**
| Variable | Symbol | Description | Units | Value |
|---|---|---|---|---|
| `w_fuse` | $w_f$ | Max fuselage width (cabin, = 4 in) | mm | 101.6 |
| `h_fuse` | $h_f$ | Max fuselage height (cabin, = 4 in) | mm | 101.6 |
| `h_fuse_top` | $h_{f,top}$ | Top keel above waterline; **= 75 % of `h_fuse`** (bottom keel = `h_fuse − h_fuse_top` = 25.4) | mm | 76.2 |
| `x_motor` | — | Motor / prop-plane, **forward** distance from LE (= cabin front wall, 6 in fwd) | mm | 152.40 |
| `nose_len` | — | Nose-cone / front-taper length (= 6 in) | mm | 152.40 |
| `x_nose` | — | Nose-tip, **forward** from LE — derived `= x_motor + nose_len` | mm | 304.80 |
| `L_fuse` | $L_f$ | **Pod** length — derived `= x_fuse_nose + x_fuse_sleeve_top` (the empennage rides a tail boom, deliberately **not** modeled in the skeleton) | mm | 487.20 |
| `cabin_len` | — | Constant-section cabin length (= 10 in), firewall → rear wall | mm | 254 |
| `crown_sh_pct` | — | Cabin-crown Style-Spline side-control height / `h_fuse` | — | 0.65 |
| `crown_apex_pct` | — | Cabin-crown Style-Spline flat-apex half-width / (`w_fuse`/2) | — | 0.30 |

**Absolute cross-section control (dome-arch).** After the 101.6 mm (4 in) cabin resize (full-profile rescale, factor $101.6/139.7 = 8/11$ exact, heights taken about the waterline so the 75 % split holds), the section corners are stored as **absolute** port half-widths ($X$) and waterline-referenced heights ($Y$) — *not* fractions of `w_fuse`/`h_fuse` — so the tuned shoulder-spline shape is frozen and the `crown_*_pct` ratios track it automatically.
| Column | Half-width $X$ [mm] | Height(s) $Y$ [mm] (above +, below −) |
|---|---|---|
| Nose face | `w_fuse_nose_half` 25.4 | `h_nose_top` +60.0364 / `h_nose_bottom` +9.2364 |
| Fwd shoulder break (M1/M4, P1) | `w_fuse_break_fwd` 41.9054 | `h_nose_break_top` +68.1182 / `h_nose_break_bottom` −13.3096 |
| Cabin corners (CL / TL) | `w_fuse_cabin_fwd_half` / `w_fuse_cabin_aft_half` 50.8 | top keel +76.2 / bottom keel −25.4 |
| Aft shoulder break (M2/M3, P2) | `w_fuse_break_aft` 43.9420 | `h_tail_break_top` +65.9130 above WL / `h_tail_break_bottom` 21.9710 below WL |
| Planform break (P1/P2 legacy) | `w_fuse_break` 38.1 | — |
| Tail-cap / sleeve root (EL, TT/TB) | `w_fuse_tail_half` 8.7976 | `h_tail_top` +31.8885 / `h_tail_bottom` +14.2933 |
| **Boom-sleeve end (SL_P, SL_T/SL_B)** | `w_fuse_sleeve_half` 9.5250 | `h_sleeve_top` 9.5250 above WL / `h_sleeve_bottom` 9.5250 below WL |

**Derived — dedicated longitudinal station planes (§7.3.6).** These drive the decoupled `PLN_Fuse_*` fuselage planes; each is a **positive** offset from the Front Plane, landing on the side shown.
| Variable | Equation / kind | Value | Side | Plane |
|---|---|---|---|---|
| `x_fuse_nose` | $x_{nose}$ | 304.80 | +Z fwd | `PLN_Fuse_Nose` |
| `x_fuse_firewall` | $x_{motor}$ | 152.40 | +Z fwd | `PLN_Fuse_Firewall` |
| `x_fuse_midnose` | absolute | 228.60 | +Z fwd | `PLN_Fuse_MidNose` |
| `x_fuse_bay_fwd` | absolute — fwd cabin sub-station (loft skips this plane) | 50.00 | +Z fwd | `PLN_Fuse_Bay_Fwd` |
| `x_fuse_bay_aft` | absolute — rear cabin wall (`TR`/`BR`) | 101.60 | −Z aft | `PLN_Fuse_Bay_Aft` |
| `x_fuse_midtail` | absolute — `M2`/`M3` column, **1 in aft of `TR`/`BR`** | 127.00 | −Z aft | `PLN_Fuse_MidTail` |
| `x_fuse_tail` | absolute — sleeve root / tail-cone exit (`TT`/`TB`), **1 in aft of `M2`/`M3`** | 152.40 | −Z aft | `PLN_Fuse_Tail` |
| `x_fuse_sleeve_top` | absolute — boom-sleeve end, top vertex (`SL_T`), **1 in aft of `TT`** | 177.80 | −Z aft | — (no plane) |
| `x_fuse_sleeve_bottom` | absolute — boom-sleeve end, bottom vertex (`SL_B`), **1 in aft of `TB`** | 177.80 | −Z aft | — (no plane) |
| `x_fuse_sleeve_plan` | absolute — boom-sleeve end, planform vertices (`SL_P`/`SL_C`) | 177.80 | −Z aft | — (no plane) |
> `x_fuse_bay_fwd` and `x_fuse_bay_aft` sit on **opposite** sides of the Origin (+Z / −Z) and take opposite Flip states. Neither is a payload feature: `x_fuse_bay_fwd` is a forward cabin sub-station whose plane the §8.5 loft skips, and `x_fuse_bay_aft` is the cabin rear wall (constant-section aft bound). Both keep their container-era names so downstream derived parts stay linked. See §3 / §7.3.6.
---

</details>

<details>
<summary><b>6. Control surfaces</b></summary>

## 6. Control surfaces
**Inputs**
| Variable | Description | Units | Starter |
|---|---|---|---|
| `c_ail_pct` | Aileron chord fraction | — | 0.25 |
| `ail_in_pct` | Aileron inboard station | %semi-span | 0.55 |
| `ail_out_pct` | Aileron outboard station | %semi-span | 0.95 |
| `c_flap_pct` | Flap chord fraction (high-lift matters for short takeoff) | — | 0.30 |
| `flap_in_pct` | Flap inboard station | %semi-span | 0.10 |
| `flap_out_pct` | Flap outboard station | %semi-span | 0.55 |
**Derived:** `y_ail_in` $=\text{ail\_in\_pct}\cdot b/2$, `y_ail_out`, `y_flap_in`, `y_flap_out` (same form). Servos must be analysis/test-sized for flight loads with no backlash, and clevises need keepers `[R §2 Control Surface / Servo Sizing / Clevis Keepers]`.
---

</details>

<details>
<summary><b>7. Propulsion (electric only) <code>[R §9]</code></b></summary>

## 7. Propulsion (electric only) `[R §9]`
**Inputs**
| Variable | Symbol | Description | Units | Starter |
|---|---|---|---|---|
| `D_prop` | $D_p$ | Propeller diameter (gearbox / multi-motor / ducted all allowed) | mm | 280 |
| `thrust_down` | — | Downthrust angle | deg | 2 |
| `thrust_side` | — | Sidethrust angle | deg | 1 |
| `h_thrust` | — | Thrust-line height above ground | mm | 160 |
| `y_motor_offset` | — | Motor/thrust-line vertical offset from wing-root Origin (neg = below, 0 = inline) | mm | −20 |
| `n_cells` | — | LiPo cell count — **Micro max = 4** `[R §9]` | — | 4 |
| `P_limit` | — | Power-limiter rating (NeuRacing, 2021+) `[R §9]` | W | 450 |
| `keepout` | — | Prop safety keep-out = **9 in** `[R §2]` | mm | 228.6 |
**Derived:** `prop_clear` $= h_{thrust} - D_p/2$ (must be $>0$; keep ≥ 50–75 mm static and re-check at rotation).
The 450 W limit with a 4S pack is the hard ceiling on installed power — size the prop/gearing to convert that into the static thrust your 10-ft-takeoff target needs, not for top speed.
---

</details>

<details>
<summary><b>8. Landing gear</b></summary>

## 8. Landing gear
Micro rolls for takeoff (main gear stays on the take-off line, one release) and must land within a **200 ft** zone `[R §3.2 / §3.3]`.
**Inputs**
| Variable | Symbol | Description | Units | Starter |
|---|---|---|---|---|
| `track` | $t$ | Main-gear track | mm | 260 |
| `x_main` | — | Main-gear axle, **aft** distance from LE | mm | 40 |
| `x_aux` | — | Nose-wheel, **forward** distance from LE | mm | 260 |
| `wheel_main` | — | Main wheel diameter | mm | 60 |
| `w_wheel` | $w_w$ | Main tire axial width (front-view rectangle width, along $X$) | mm | 25 |
| `wheel_aux` | — | Auxiliary wheel diameter | mm | 45 |
**Derived:** `wheel_base` $= x_{main}+x_{aux}$ (main aft + nose forward — opposite sides of the LE, so the separation is the **sum**); `gear_h` $= \text{wheel\_main}/2$ (axle height above ground = tire radius, so the tire bottom sits **flush**; ≈ 30 mm). Keep CG inside the wheel triangle, main gear just aft of `x_CG`, track $\gtrsim 1.5\times$ CG height.
---

</details>

<details>
<summary><b>9. Mass, CG &amp; stability (water-payload mass model) <code>[R §9]</code></b></summary>

## 9. Mass, CG & stability (water-payload mass model) `[R §9]`
**Inputs**
| Variable | Symbol | Description | Units | Starter |
|---|---|---|---|---|
| `W_empty` | $m_e$ | Empty mass — **penalized → minimize** `[R §9]` | g | 1100 |
| `W_container` | — | Payload-container mass (mass model only; container not modeled) | g | 120 |
| `V_water` | $V_w$ | Water carried (**≥ 1981 cm³ = 67 fl oz min**) `[R §9]` | cm³ | 2000 |
| `rho_water` | $\rho_w$ | Water density | g/cm³ | 1.0 |
| `x_CG_root` | $x_{CG}$ | CG station aft of the wing root LE | mm | 22.0 |
| `x_NP` | $x_{NP}$ | Neutral point (aft distance from LE) from XFLR5/AVL (Micro TDS req.) `[R TDS]` | mm | 95 (set from AVL) |
| `SM_min` | — | Min acceptable static margin | — | 0.08 |
| `SM_max` | — | Max acceptable static margin | — | 0.35 |
**Derived**
| Variable | Equation | Units |
|---|---|---|
| `W_water` | $V_w\,\rho_w$  (scored = water drained & weighed) | g |
| `W_payload` | $W_{water}$ | g |
| `W_TO` | $W_{empty}+W_{container}+W_{water}$ | g |
| `x_CG` | $x_{\bar c,LE} + k_{CG}\,\bar c$ | mm |
| `SM` | $(x_{NP}-x_{CG})/\bar c$ | — |
| `x_CG_aft` | $x_{NP} - \text{SM\_min}\cdot\bar c$ | mm |
| `x_CG_fwd` | $x_{NP} - \text{SM\_max}\cdot\bar c$ | mm |
| `WL_g_dm2` | $\dfrac{W_{TO}}{S}\times 10^{4}$ | g/dm² |
$$W_{water}=V_w\,\rho_w, \qquad W_{TO}=W_{empty}+W_{container}+W_{water}, \qquad SM=\frac{x_{NP}-x_{CG}}{\bar c}$$
Set `x_NP` from your stability tool (Micro must submit NP and static-margin plots). The loaded **and** drained CG must both sit inside `x_CG_fwd…x_CG_aft` — verify both, since the water leaves through the bottom port between scoring states.
---

</details>

<details>
<summary><b>10. Performance &amp; sizing inputs (offline, SI)</b></summary>

## 10. Performance & sizing inputs (offline, SI)
Compute in the aero spreadsheet (SI), then feed `b`, `c_root`, `c_tip` into §1. Stall-limited area (mass $m$, $g=9.81$):
$$S = \frac{2\,m\,g}{\rho\,V_{stall}^{2}\,C_{L,\max}}$$
**Performance-first planform** (input $S$, $AR$, $\lambda$): $\;b=\sqrt{AR\,S},\quad c_r=\dfrac{2S}{b(1+\lambda)},\quad c_t=\lambda c_r$
Operating Reynolds ($\nu_{SL}\approx1.46\times10^{-5}\,\mathrm{m^2/s}$): $\;Re=\dfrac{V\,\bar c}{\nu}$
**Micro takeoff scoring** `[R §9.5]` — the entire flight score scales with the takeoff-distance multiplier $M$ below, so the design point is the **10 ft** bin:
| Takeoff ground roll $x$ | Multiplier $M$ |
|---|---|
| $0 \le x \le 10$ ft | **20** |
| $10 < x \le 25$ ft | 15 |
| $25 < x \le 50$ ft | 9 |
| $50 < x \le 100$ ft | 0 |
| $x > 100$ ft | **disqualified** |
Other field limits: **one** takeoff try and **one** launch release per attempt; first turn only after **400 ft** from start; **landing within 200 ft**; **60 s** flight-prep time limit; one escort + pilot `[R §3.2, §3.3, flight tables]`.
**Scoring drivers (qualitative):** the flight score rewards **payload water weight** $\times$ the **takeoff multiplier** and penalizes **empty weight** and **wingspan**; the final score is the sum of your top **three** flights `[R §9 Micro Flight Scoring]`. So: maximize water, minimize empty weight, minimize span, take off in ≤ 10 ft.
Spreadsheet inputs to keep: $\rho$, $V_{stall}$, $V_{cruise}$, $C_{L,\max}$ (with flaps), $C_{L,cruise}$, target $AR$, target $\lambda$, available static thrust at 450 W.
---

</details>

<details>
<summary><b>11. Micro Class constraints, compliance &amp; hardpoints <code>[R §9, §2]</code></b></summary>

## 11. Micro Class constraints, compliance & hardpoints `[R §9, §2]`
Capture every rule constraint as geometry so violations are visible and parametric.
**Payload container** `[R §9 Payload Requirements]` — mass model only; no CAD geometry
| Variable | Description | Units | Starter |
|---|---|---|---|
| `x_bay` | Water-mass centroid station (keep near CG) — **mass bookkeeping only, not dimensioned** | mm | 60 |
| `x_drain` | External **bottom** drain-port station (under bay) | mm | 70 |
Container must be **fully enclosed**, with **two sealable holes** — top for filling, bottom for unloading — and the aircraft must **drain from an external bottom port within 60 s** without opening the bay or squeezing. Payload is **non-structural**; airframe must be flightworthy empty `[R §2 Payload / §9]`.
**Safety hardpoints** `[R §2 Red Arming Plug / On-Off Switch / Battery]`
| Variable | Description | Units | Starter |
|---|---|---|---|
| `x_arm_plug` | Red arming-plug station — **top, near centerline, external** | mm | 30 |
| `x_switch` | RX on/off switch station — exterior | mm | 70 |
| `x_ballast` | Ballast — **forward** distance from LE; **must NOT sit inside the payload container** (off-model check) | mm | 150 |
| `bat_L` / `bat_W` / `bat_H` | Propulsion 4S-LiPo envelope (3.10 / 1.35 / 1.35 in; no penetrating protrusions) | mm | 78.74 / 34.29 / 34.29 |
| `avi_bat_L` / `avi_bat_W` / `avi_bat_H` | Avionics (RX) battery envelope (2.40 / 1.20 / 0.90 in) | mm | 60.96 / 30.48 / 22.86 |
| `x_bat` | Propulsion-battery, **forward** distance from LE | mm | 120 |
Both the arming plug and the on/off switch must sit **≥ 9 in (228.6 mm) from any point of the prop disk**. A separate RX battery or BEC is required (separate pack ≥ 1000 mAh LiPo/LiFE) `[R §2 Receiver System Battery]`.
**Derived checks (watch these — all must be ≥ 0)**
| Variable | Equation | Meaning |
|---|---|---|
| `arm_clear` | $x_{arm\_plug} + x_{motor} - keepout$ | arming plug ≥ 9 in aft of prop |
| `sw_clear` | $x_{switch} + x_{motor} - keepout$ | switch ≥ 9 in aft of prop |
| `span_ft` | $b/304.8$ | wingspan in ft (scoring penalty $Z=-S$) |
| `W_pay_lb` | $W_{payload}/453.592$ | payload in lb (scoring) |
| `W_empty_lb` | $W_{empty}/453.592$ | empty weight in lb (scoring penalty) |
> The `arm_clear`/`sw_clear` checks are **conservative** — they assume the plug/switch sit near centerline (radially inside the prop disk), so axial separation ≥ keep-out guarantees ≥ 9 in to the disk. If you mount them outboard of the prop radius, the true clearance is larger.
---

</details>

<details>
<summary><b>12. Derived-for-dimensioning globals (one-variable rule)</b></summary>

## 12. Derived-for-dimensioning globals (one-variable rule)

Each of these exists so a SolidWorks dimension can reference **one** name instead of an expression. None is a new design input — every value is derived from globals above it, so they all re-solve automatically. Do not type these numbers; type the name.

| Global | Value | Wraps a formula formerly typed into | 
|---|---|---|
| `b_semi_proj` | 519.2649 | wing spar tip, in-plane span (§7.2) |
| `x_spar_tip` | 56.2500 | main spar @ tip (§5.4) |
| `x_spar_tip_swept` | 157.1267 | wing spar tip, chordwise (§7.2) |
| `i_tip` | 0.0000 | tip chord incidence (§8.3) |
| `y_ail_in_proj` | 285.5957 | aileron inbd, in-plane span (§7.7.2) |
| `y_ail_out_proj` | 493.3017 | aileron outbd, in-plane span (§7.7.2) |
| `y_flap_in_proj` | 51.9265 | flap inbd, in-plane span (§7.7.2) |
| `y_flap_out_proj` | 285.5957 | flap outbd, in-plane span (§7.7.2) |
| `x_hinge_ail_in` | 224.2322 | aileron inbd hinge, chordwise (§7.7.2) |
| `x_hinge_ail_out` | 264.5828 | aileron outbd hinge, chordwise (§7.7.2) |
| `x_hinge_flap_in` | 167.5877 | flap inbd hinge, chordwise (§7.7.2) |
| `x_hinge_flap_out` | 212.9822 | flap outbd hinge, chordwise (§7.7.2) |
| `y_servo_ail` | 388.5000 | aileron servo station (§I-1) |
| `x_spar_root_HT` | 44.1066 | HT spar @ root from HT LE (§5.8.1) |
| `x_spar_tip_HT` | 44.1066 | HT spar @ tip from HT LE (§5.8.1) |
| `x_HT_spar_root` | 892.2385 | HT spar root, chordwise (§5.8.2) |
| `x_HT_spar_tip` | 892.2385 | HT spar tip, chordwise (§5.8.2) |
| `b_semi_HT_proj` | 207.3009 | HT spar tip, in-plane span (§5.8.2) |
| `x_VT_spar_root` | 892.2385 | VT spar root, chordwise (§6.8.1) |
| `x_VT_spar_tip` | 954.3691 | VT spar tip, chordwise (§6.8.1) |
| `h_VT_tip` | 242.8813 | VT fin top height — fin spar tip and `PLN_VT_Tip` (§6.8.1, §7.3.8) |
| `h_fuse_bottom` | 25.4000 | bottom keel below WL (§4.4, §6.4, §8.5) |
| `w_fuse_half` | 50.8000 | cabin max half-width, flare (§6.4) |
| `h_crown_flare` | 66.0400 | flare vertex height (§6.4) |
| `w_crown_apex_half` | 15.2400 | crown apex half-width (§6.4) |
| `w_fuse_floor_half` | 38.1000 | flat-floor half-width (§6.4, §8.5) — STARTER |
| `h_clock_2_10` | 25.4000 | 2/10 o-clock spline point (§8.5) |
| `h_clock_1_11` | 50.8000 | 1/11 o-clock spline point (§8.5) |
| `h_fill_top` | 91.2000 | fill-path top, crown +15 (§7.13) |
| `D_keepout` | 737.2000 | prop keep-out circle diameter (§4.6, §7.3.5) |
| `R_keepout` | 368.6000 | prop keep-out radius (§12.2) |
| `track_half` | 130.0000 | main-gear half-track (§6.6, §I-3) |
| `gear_h_tail` | 15.0000 | tailwheel axle height (§I-3) |
| `w_wing_seat_half` | 45.0000 | wing-seat plane offset (§7.10) |
| `x_bat_aft` | 80.6300 | battery aft face (§I-5) |
| `x_CG_drained` | 215.6909 | drained CG (§7.8.3) |
| `x_CG_empty` | 232.6754 | empty CG (§7.8.3) |
| `x_LE_tip` | 112.0000 | wing tip LE, chordwise (§7.2 Phase B) |
| `y_MAC_proj` | 288.2020 | MAC line, in-plane span (§7.2 Phase B) |
| `rib_root_off_proj` | 20.0488 | rib seed, in-plane span (§7.2 Phase B) |
| `rib_pitch_proj` | 83.2027 | rib pattern, in-plane pitch (§7.2 Phase B) |
| `y_emp_axis` | 25.0000 | empennage datum height above Top Plane (§2.3.1) — INPUT |
| `x_LE_tip_inc` | 112.0000 | wing tip LE, in-plane chordwise (§7.2 Phase B) |
| `x_spar_root_inc` | 56.2500 | main spar root, in-plane chordwise (§7.2 Phase B) |
| `x_spar_tip_swept_inc` | 157.1267 | main spar tip, in-plane chordwise (§7.2 Phase B) |
| `x_rspar_root_inc` | 157.5000 | rear spar root, in-plane chordwise (§7.2 Phase B) |
| `x_rspar_tip_inc` | 157.5000 | rear spar tip, in-plane chordwise (§7.2 Phase B) |
| `x_joiner_root_inc` | 56.2500 | wing joiner, in-plane chordwise (§7.2 Phase B) |
| `x_MAC_LE_inc` | 55.9884 | MAC LE, in-plane chordwise (§7.2 Phase B) |
| `x_MAC_c4_inc` | 112.2384 | MAC c/4, in-plane chordwise (§7.2 Phase B) |
| `x_hinge_ail_in_inc` | 224.4000 | aileron inbd hinge, in-plane chordwise (§7.2 Phase B) |
| `x_hinge_ail_out_inc` | 264.7000 | aileron outbd hinge, in-plane chordwise (§7.2 Phase B) |
| `x_hinge_flap_in_inc` | 167.6000 | flap inbd hinge, in-plane chordwise (§7.2 Phase B) |
| `x_hinge_flap_out_inc` | 212.9000 | flap outbd hinge, in-plane chordwise (§7.2 Phase B) |
| `x_spar_root_HT_inc` | 44.1342 | HT spar root, in-plane chordwise (§5.8.1 Phase B) |
| `x_spar_tip_HT_inc` | 44.1342 | HT spar tip, in-plane chordwise (§5.8.1 Phase B) |

</details>

<details>
<summary><b>Appendix A — Complete SolidWorks equation block (copy-paste)</b></summary>

## Appendix A — Complete SolidWorks equation block (copy-paste)
This block is kept **byte-identical** to `skeleton_equations_micro.txt` (bulbous tangent-arch section, 101.6 mm cabin pod). Paste via **Tools ▸ Equations ▸ Import**, or edit the `.txt` and re-import — never maintain the two separately.
```text
"b"             = 1150      'wingspan [mm]  NO cap, but span is PENALIZED -> minimize
"c_root"        = 225       'root chord [mm]
"c_tip"         = 225       'tip chord [mm]
"sweep_LE"              = 12.2004687   'wing LE sweep [deg] = arctan(112/518) over b_semi, from XFLR5 Section 2 offset'
"dihedral"      = 4         'dihedral [deg]
"i_wing"        = 0.0       'wing incidence [deg]
"twist_tip"     = 0.0       'tip WASHOUT magnitude [deg]; POSITIVE = tip incidence lower than root (subtracted in i_tip), never enter a negative
"i_tip"                 = "i_wing" - "twist_tip"   'tip chord incidence [deg] = root incidence MINUS the washout magnitude
"b_semi"        = 518       'main lifting-panel semi-span on PLN_Dihedral [mm]; ABSOLUTE (was "b"/2). b/2 = 575 = 518 panel + 57 vertical tip; winglet modeled downstream
"taper"         = "c_tip" / "c_root"
"S_w"           = ("c_root" + "c_tip") / 2 * "b"
"AR"            = "b"^2 / "S_w"
"MAC"           = (2/3) * "c_root" * (1 + "taper" + "taper"^2) / (1 + "taper")
"y_MAC"         = ("b" / 6) * (1 + 2*"taper") / (1 + "taper")
"x_MAC_LE"      = "y_MAC" * tan("sweep_LE" * pi/180)   'AFT distance of MAC LE from wing LE [mm]
"x_MAC_c4"      = "x_MAC_LE" + 0.25 * "MAC"            'AFT distance of MAC c/4 [mm]
"spar_main_pct" = 0.25      'main spar @ %chord
"spar_rear_pct" = 0.70      'rear spar @ %chord
"n_rib"         = 7         'ribs per semi-span
"rib_root_off"  = 20        'first rib offset from centerline [mm] (spanwise)
"rib_thk"               = 1.5875    'standard rib thickness [mm] = 1/16 in wood'
"rib_thk_div"           = 3.175     'divider-rib thickness [mm] = 1/8 in wood; the rib between flap and aileron'
"n_rib_div"             = 4         'divider-rib index, 1-based from the root rib; must be <= n_rib'
"hinge_gap"             = 1.5875    'spanwise clearance between a control-surface end and the adjacent rib face [mm] = 1/16 in'
"sparcap_w"     = 6.0
"sparcap_h"     = 6.0
"web_thk"       = 1.5
"LE_sheet_pct"  = 0.30
"tc_root"       = 0.14
"tc_tip"        = 0.14
"rib_pitch"     = ("b_semi" - "rib_root_off") / ("n_rib" - 1)   'spanwise pitch [mm]
"y_rib_div"             = "rib_root_off" + ("n_rib_div" - 1) * "rib_pitch"   'spanwise station of the 1/8 in divider rib [mm]'
"rib_root_off_physical" = "rib_root_off" * sqr("b_semi"^2 + ("b_semi"*tan("dihedral"*pi/180))^2 + ("b_semi"*tan("sweep_LE"*pi/180) - "spar_main_pct"*("c_root"-"c_tip"))^2) / "b_semi"   'first rib offset ALONG the 3D spar [mm]; now includes the sweep term'
"rib_root_off_proj"     = "rib_root_off" / cos("dihedral" * pi/180)   'RIB SEED: in-plane spanwise dist from Origin on PLN_Dihedral [mm]; /cos projects to X = rib_root_off
"rib_pitch_proj"        = "rib_pitch" / cos("dihedral" * pi/180)   'RIB PATTERN: in-plane spanwise pitch on PLN_Dihedral [mm]; /cos projects to spanwise rib_pitch
"x_spar_root"   = "spar_main_pct" * "c_root"   'AFT distance of main spar @ root [mm]
"x_rspar_root"  = "spar_rear_pct" * "c_root"   'AFT distance of rear spar @ root [mm]
"x_rspar_tip"   = "spar_rear_pct" * "c_tip"    'AFT distance of rear spar @ tip [mm]
"x_spar_tip"            = "spar_main_pct" * "c_tip"   'AFT distance of main spar @ tip [mm]
"x_spar_tip_swept"      = "b_semi" * tan("sweep_LE" * pi/180) + "spar_main_pct" * "c_tip"   'SPAR TIP: dist to Front Plane, aft (-Z) [mm]; LE sweep carried to tip + spar fraction of tip chord
"x_LE_tip"              = "b_semi" * tan("sweep_LE" * pi/180)   'WING TIP LE: dist to Front Plane, aft (-Z) [mm]; LE-sweep walk out to the tip station
"x_LE_tip_inc"          = "x_LE_tip" / cos("i_wing" * pi/180)   'WING TIP LE: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_spar_root_inc"       = "x_spar_root" / cos("i_wing" * pi/180)   'MAIN SPAR ROOT: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_spar_tip_swept_inc"  = "x_spar_tip_swept" / cos("i_wing" * pi/180)   'MAIN SPAR TIP: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_rspar_root_inc"      = "x_rspar_root" / cos("i_wing" * pi/180)   'REAR SPAR ROOT: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_rspar_tip_inc"       = "x_rspar_tip" / cos("i_wing" * pi/180)   'REAR SPAR TIP: in-plane chordwise dist from the TIP LE on PLN_Incidence [mm]
"x_joiner_root" = "x_spar_root"   'AFT distance of wing joiner/spar-tube @ root [mm]; co-located with main spar
"x_joiner_root_inc"     = "x_joiner_root" / cos("i_wing" * pi/180)   'WING JOINER: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_MAC_LE_inc"          = "x_MAC_LE" / cos("i_wing" * pi/180)   'MAC LE: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_MAC_c4_inc"          = "x_MAC_c4" / cos("i_wing" * pi/180)   'MAC c/4: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"c_root_HT"             = 170.0     'HT root chord [mm]; XFLR5 elevator Section 1'
"c_tip_HT"              = 170.0     'HT tip chord [mm]; XFLR5 elevator Section 2'
"b_HT"                  = 400.0     'HT full span [mm]; XFLR5 2 x Section 2 y'
"x_tail_LE_root"        = 750.0     'TAIL DATUM: HT and VT root LE station aft of the wing root LE [mm]; XFLR5 plane position'
"i_HT"          = 2.0       'HT incidence magnitude [deg]; POSITIVE, nose-DOWN vs AX_Long_Emp - direction set by the PLN_Incidence_HT Flip (5.8.1), never by a sign
"sweep_HT"      = 0
"c_elev_pct"    = 0.35
"taper_HT"              = "c_tip_HT" / "c_root_HT"   'HT taper ratio (derived from the two chords)'
"b_semi_HT"             = "b_HT" / 2   'horizontal tail semi-span [mm]'
"S_HT"                  = ("c_root_HT" + "c_tip_HT") / 2 * "b_HT"   'HT planform area [mm^2]'
"AR_HT"                 = "b_HT"^2 / "S_HT"   'HT aspect ratio'
"MAC_HT"                = (2/3) * "c_root_HT" * (1 + "taper_HT" + "taper_HT"^2) / (1 + "taper_HT")   'HT mean aerodynamic chord [mm]'
"y_MAC_HT"              = ("b_HT" / 6) * (1 + 2*"taper_HT") / (1 + "taper_HT")   'HT MAC spanwise station from the root [mm]'
"x_HT_LE_root"          = "x_tail_LE_root"   'AFT distance of HT root LE [mm]'
"x_HT_c4"               = "x_HT_LE_root" + 0.25 * "c_root_HT"   'AFT distance of HT root c/4 [mm]; = MAC c/4 because sweep_HT=0 and taper_HT=1'
"l_HT"                  = "x_HT_c4" - "x_MAC_c4"   'wing MAC c/4 -> HT c/4 moment arm [mm] (derived from the tail datum)'
"V_H"                   = "S_HT" * "l_HT" / ("S_w" * "MAC")   'horizontal tail volume coeff (REPORTED, not a design input)'
"x_spar_root_HT"        = "spar_main_pct" * "c_root_HT"   'AFT distance of HT main spar @ root, from HT root LE [mm]
"x_spar_tip_HT"         = "spar_main_pct" * "c_tip_HT"   'AFT distance of HT main spar @ tip, from HT tip LE [mm]
"x_spar_root_HT_inc"    = "x_spar_root_HT" / cos("i_HT" * pi/180)   'HT SPAR ROOT: in-plane chordwise dist from the HT root LE on PLN_Incidence_HT [mm]
"x_spar_tip_HT_inc"     = "x_spar_tip_HT" / cos("i_HT" * pi/180)   'HT SPAR TIP: in-plane chordwise dist from the HT tip LE on PLN_Incidence_HT [mm]
"x_HT_spar_root"        = "x_HT_LE_root" + "spar_main_pct" * "c_root_HT"   'HT SPAR ROOT: dist to Front Plane, aft (-Z) [mm]
"x_HT_spar_tip"         = "x_HT_LE_root" + "b_semi_HT" * tan("sweep_HT" * pi/180) + "spar_main_pct" * "c_tip_HT"   'HT SPAR TIP: dist to Front Plane, aft (-Z) [mm]
"c_root_VT"             = 170.0     'fin root chord [mm]; XFLR5 fin Section 1'
"c_tip_VT"              = 90.0      'fin tip chord [mm]; XFLR5 fin Section 2'
"b_VT"                  = 200.0     'fin height [mm]; XFLR5 fin Section 2 y'
"sweep_VT"              = 21.8014095   'fin LE sweep [deg] = arctan(80/200) from XFLR5; NOT its c/4 sweep of 16.70'
"c_rud_pct"     = 0.40
"taper_VT"              = "c_tip_VT" / "c_root_VT"   'fin taper ratio (derived from the two chords)'
"S_VT"                  = ("c_root_VT" + "c_tip_VT") / 2 * "b_VT"   'fin planform area [mm^2]'
"AR_VT"                 = "b_VT"^2 / "S_VT"   'fin aspect ratio'
"MAC_VT"                = (2/3) * "c_root_VT" * (1 + "taper_VT" + "taper_VT"^2) / (1 + "taper_VT")   'fin mean aerodynamic chord [mm]'
"y_MAC_VT"              = ("b_VT" / 3) * (1 + 2*"taper_VT") / (1 + "taper_VT")   'fin MAC height above the fin root [mm]'
"x_VT_LE_root"          = "x_tail_LE_root"   'AFT distance of VT root LE [mm]'
"x_MAC_LE_VT"           = "x_VT_LE_root" + "y_MAC_VT" * tan("sweep_VT" * pi/180)   'AFT distance of the fin MAC LE [mm]'
"x_MAC_c4_VT"           = "x_MAC_LE_VT" + 0.25 * "MAC_VT"   'AFT distance of the fin MAC c/4 = the fin aerodynamic centre [mm]'
"x_VT_c4"               = "x_VT_LE_root" + 0.25 * "c_root_VT"   'AFT distance of VT ROOT c/4 [mm]; root-section geometry only, not the AC'
"l_VT"                  = "x_MAC_c4_VT" - "x_MAC_c4"   'wing MAC c/4 -> fin MAC c/4 moment arm [mm]; measured to the AC, not the root c/4'
"V_V"                   = "S_VT" * "l_VT" / ("S_w" * "b")   'vertical tail volume coeff (REPORTED, not a design input)'
"x_VT_spar_root"        = "x_VT_LE_root" + "spar_main_pct" * "c_root_VT"   'VT SPAR ROOT: dist to Front Plane, aft (-Z) [mm]
"x_VT_spar_tip"         = "x_VT_LE_root" + "spar_main_pct" * "c_root_VT" + "b_VT" * tan("sweep_VT" * pi/180)   'VT SPAR TIP: dist to Front Plane, aft (-Z) [mm]
"w_fuse"        = 101.6      'max width [mm] = 4 in (cabin cross-section)
"h_fuse"        = 101.6      'max height [mm] = 4 in (cabin cross-section)
"h_fuse_top"    = 76.2       'top keel ABOVE waterline [mm]; = 75% of h_fuse (3 in); bottom keel = h_fuse - h_fuse_top (1 in)
"y_emp_axis"            = 25        'EMPENNAGE DATUM: height of AX_Long_Emp above the Top Plane / waterline [mm]; boom centerline
"h_fuse_bottom"         = "h_fuse" - "h_fuse_top"   'bottom keel BELOW waterline [mm]; positive magnitude, dimension downward
"w_fuse_half"           = "w_fuse" / 2   'cabin max half-width (cross-section flare) [mm]
"x_motor"       = 152.40    'motor/prop FORWARD distance from LE [mm]  (+Z side)
"nose_len"      = 152.40    'nose-cone / front-taper length [mm] = 6 in (nose tip -> firewall)
"x_nose"        = "x_motor" + "nose_len"   'nose-tip FORWARD distance from LE [mm]  (+Z side); firewall + 6 in taper
"crown_sh_pct"  = 0.65      'cabin crown Style-Spline side-control height / h_fuse (vertical rise; larger=squarer)
"crown_apex_pct"= 0.30      'cabin crown Style-Spline flat-apex control half-width / (w_fuse/2)
"h_crown_flare"         = "crown_sh_pct" * "h_fuse"   'cabin cross-section flare-vertex height above the floor [mm]
"w_crown_apex_half"     = "crown_apex_pct" * "w_fuse" / 2   'cabin crown flat-apex control half-width [mm]
"w_fuse_floor_half"     = 38.10     'cabin flat-floor contact half-width [mm]; STARTER - replaces the undefined "w_floor_pct" expression, confirm against your floor width
"h_clock_2_10"          = "h_fuse_top" * 1 / 3   'cross-section 2/10 o-clock spline point height above waterline [mm]
"h_clock_1_11"          = "h_fuse_top" * 2 / 3   'cross-section 1/11 o-clock spline point height above waterline [mm]
"h_fill_top"            = "h_fuse_top" + 15   'fill-path upper endpoint height above waterline [mm]; 15 mm crown overshoot
"c_ail_pct"     = 0.25
"ail_in_pct"            = ("y_rib_div" + "rib_thk_div"/2 + "hinge_gap") / "b_semi"   'aileron inboard end: hinge_gap clear of the divider-rib outboard face'
"ail_out_pct"           = ("b_semi" - "rib_thk"/2 - "hinge_gap") / "b_semi"   'aileron outboard end: hinge_gap clear of the tip rib face'
"c_flap_pct"    = 0.30
"flap_in_pct"           = ("rib_root_off" + "rib_thk"/2 + "hinge_gap") / "b_semi"   'flap inboard end: hinge_gap clear of the root rib face'
"flap_out_pct"          = ("y_rib_div" - "rib_thk_div"/2 - "hinge_gap") / "b_semi"   'flap outboard end: hinge_gap clear of the divider-rib inboard face'
"y_ail_in"      = "ail_in_pct"   * "b_semi"
"y_ail_out"     = "ail_out_pct"  * "b_semi"
"y_flap_in"     = "flap_in_pct"  * "b_semi"
"y_flap_out"    = "flap_out_pct" * "b_semi"
"y_ail_in_proj"         = "y_ail_in" / cos("dihedral" * pi/180)   'AIL INBD: in-plane spanwise dist from Origin on PLN_Dihedral [mm]; /cos projects to X = y_ail_in
"y_ail_out_proj"        = "y_ail_out" / cos("dihedral" * pi/180)   'AIL OUTBD: in-plane spanwise dist from Origin on PLN_Dihedral [mm]
"y_flap_in_proj"        = "y_flap_in" / cos("dihedral" * pi/180)   'FLAP INBD: in-plane spanwise dist from Origin on PLN_Dihedral [mm]
"y_flap_out_proj"       = "y_flap_out" / cos("dihedral" * pi/180)   'FLAP OUTBD: in-plane spanwise dist from Origin on PLN_Dihedral [mm]
"x_hinge_ail_in"        = "y_ail_in" * tan("sweep_LE" * pi/180) + (1 - "c_ail_pct") * ("c_root" - ("c_root" - "c_tip") * "ail_in_pct")   'AIL INBD hinge: dist to Front Plane, aft (-Z) [mm]; 75%c station + LE-sweep walk
"x_hinge_ail_in_inc"    = "x_hinge_ail_in" / cos("i_wing" * pi/180)   'AIL INBD hinge: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_hinge_ail_out"       = "y_ail_out" * tan("sweep_LE" * pi/180) + (1 - "c_ail_pct") * ("c_root" - ("c_root" - "c_tip") * "ail_out_pct")   'AIL OUTBD hinge: dist to Front Plane, aft (-Z) [mm]
"x_hinge_ail_out_inc"   = "x_hinge_ail_out" / cos("i_wing" * pi/180)   'AIL OUTBD hinge: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_hinge_flap_in"       = "y_flap_in" * tan("sweep_LE" * pi/180) + (1 - "c_flap_pct") * ("c_root" - ("c_root" - "c_tip") * "flap_in_pct")   'FLAP INBD hinge: dist to Front Plane, aft (-Z) [mm]; 70%c station + LE-sweep walk
"x_hinge_flap_in_inc"   = "x_hinge_flap_in" / cos("i_wing" * pi/180)   'FLAP INBD hinge: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"x_hinge_flap_out"      = "y_flap_out" * tan("sweep_LE" * pi/180) + (1 - "c_flap_pct") * ("c_root" - ("c_root" - "c_tip") * "flap_out_pct")   'FLAP OUTBD hinge: dist to Front Plane, aft (-Z) [mm]
"x_hinge_flap_out_inc"  = "x_hinge_flap_out" / cos("i_wing" * pi/180)   'FLAP OUTBD hinge: in-plane chordwise dist from Origin on PLN_Incidence [mm]
"y_servo_ail"           = ("y_ail_in" + "y_ail_out") / 2   'aileron servo spanwise centre (mid-aileron) [mm]
"b_semi_proj"           = "b_semi" / cos("dihedral" * pi/180)   'SPAR TIP: in-plane spanwise dist from Origin on PLN_Dihedral [mm]; /cos projects to X = b_semi
"y_MAC_proj"            = "y_MAC" / cos("dihedral" * pi/180)   'MAC line: in-plane spanwise dist from Origin on PLN_Dihedral [mm]; /cos projects to X = y_MAC
"D_prop"        = 280       'prop diameter [mm]
"motor_L"       = 50.80     'main motor length [mm] = 2.00 in
"motor_D"       = 39.37     'main motor max diameter [mm] = 1.55 in
"thrust_down"   = 2         'down-thrust [deg]
"thrust_side"   = 1         'right-thrust [deg]
"h_thrust"      = 160       'thrust-line height above ground [mm]
"y_motor_offset" = 20       'motor/thrust-line vertical offset from wing-root Origin [mm]; 0 = inline
"n_cells"       = 4         'LiPo cells (<=4 per rules)
"P_limit"       = 450       'power limiter [W]
"keepout"       = 228.6     'prop safety keep-out = 9 in [mm]
"D_keepout"             = "D_prop" + (2 * "keepout")   'prop keep-out circle DIAMETER [mm]; D_prop + 2x the 9 in radius buffer
"R_keepout"             = "D_prop" / 2 + "keepout"   'prop keep-out RADIUS [mm]; for the optional revolved exclusion disc
"prop_clear"    = "h_thrust" - "D_prop" / 2   'prop tip-to-ground clearance [mm] (vertical, >0)
"track"         = 260       'main-gear track [mm] (lateral)
"track_half"            = "track" / 2   'main-gear half-track, wheel centre to centerline [mm]
"x_main"        = 40        'main-gear axle AFT distance from LE [mm]  (-Z side)
"x_aux"         = 260       'nose-wheel FORWARD distance from LE [mm]  (+Z side)
"wheel_main"    = 60
"w_wheel"       = 25        'main tire axial width [mm] (along X; front-view wheel-rectangle width)
"wheel_aux"     = 45
"gear_h"        = "wheel_main" / 2   'axle ht above ground = wheel_main/2 (tire flush) [mm]
"wheel_base"    = "x_main" + "x_aux"   'main (aft) + nose (fwd) on opposite sides -> SUM [mm]
"W_empty"       = 1100      'empty weight [g]
"W_container"   = 120       'payload container [g]
"V_water"       = 2000      'water volume [cm^3] (>= 1981 = 67 fl oz)
"rho_water"     = 1.0       '[g/cm^3]
"x_CG_root"             = 22.0      'CG station AFT of the wing root LE [mm]; XFLR5 Type 7 stability run'
"x_NP"                  = 90.0      'neutral point aft of wing root LE [mm]; XFLR5 Type 7 VLM2 stability run'
"SM_min"        = 0.08      'min static margin
"SM_max"                = 0.35      'max static margin; +30.2% is intentional for heavy-payload launch stability'
"W_water"       = "V_water" * "rho_water"
"W_payload"     = "W_water"
"W_TO"          = "W_empty" + "W_container" + "W_water"
"x_CG"                  = "x_CG_root"   'AFT distance of target CG [mm]'
"x_MAC_CG"              = ("x_MAC_LE" - "x_CG_root") / "MAC"   'CG as a fraction of MAC, FORWARD of the MAC LE (positive magnitude)'
"SM"            = ("x_NP" - "x_CG") / "MAC"        'static margin (NP, CG both aft distances)
"x_CG_aft"      = "x_NP" - "SM_min" * "MAC"        'aft CG limit, AFT distance [mm]
"x_CG_fwd"      = "x_NP" - "SM_max" * "MAC"        'fwd CG limit, AFT distance [mm]
"WL_g_dm2"      = "W_TO" / "S_w" * 10000           'wing loading [g/dm^2]
"cabin_len"     = 254        'constant-section cabin length [mm] = 10 in (firewall 6 in fwd + rear wall 4 in aft)
"x_bay"         = 60        'water-mass centroid AFT station from LE [mm]  (-Z side); MASS BOOKKEEPING ONLY - no geometry, no plane, not dimensioned
"x_drain"       = 70        'bottom drain-port AFT distance from LE [mm]  (-Z side)
"x_arm_plug"    = 30        'arming-plug AFT distance from LE [mm]  (-Z side, on top)
"x_switch"      = 70        'on/off switch AFT distance from LE [mm]  (-Z side, on top)
"x_ballast"     = 150       'ballast FORWARD distance from LE [mm]  (+Z side)
"bat_L"         = 78.74     'propulsion 4S LiPo length [mm] = 3.10 in
"bat_W"         = 34.29     'propulsion 4S LiPo width [mm] = 1.35 in
"bat_H"         = 34.29     'propulsion 4S LiPo height [mm] = 1.35 in
"avi_bat_L"     = 60.96     'avionics battery length [mm] = 2.40 in
"avi_bat_W"     = 30.48     'avionics battery width [mm] = 1.20 in
"avi_bat_H"     = 22.86     'avionics battery height [mm] = 0.90 in
"x_bat"         = 120       'battery FORWARD distance from LE [mm]  (+Z side)
"x_CG_drained"          = ("W_TO" * "x_CG" - "W_water" * "x_bay") / ("W_empty" + "W_container")   'AFT distance of drained CG (water gone, container aboard) [mm]
"x_CG_empty"            = ("W_TO" * "x_CG" - ("W_water" + "W_container") * "x_bay") / "W_empty"   'AFT distance of empty CG (water + container gone) [mm]
"x_bat_aft"             = "x_bat" - "bat_L" / 2   'propulsion-battery AFT face, FORWARD distance from LE [mm]  (+Z side)
"arm_clear"     = "x_arm_plug" + "x_motor" - "keepout"   'plug (aft) + prop (fwd), opposite sides -> SUM, minus 9 in
"sw_clear"      = "x_switch" + "x_motor" - "keepout"     'switch (aft) + prop (fwd), opposite sides -> SUM, minus 9 in
"x_fuse_nose"    = "x_nose"                'FUSE STATION: nose-tip plane, FORWARD of Origin [mm]  (+Z side)
"x_fuse_firewall" = "x_motor"              'FUSE STATION: firewall / engine-face plane, FORWARD [mm]  (+Z side)
"x_fuse_bay_fwd" = 50.00  'FUSE STATION: fwd cabin sub-station plane, FORWARD of Origin [mm]  (+Z side); ABSOLUTE (self-anchored, tracks nothing); loft skips this plane
"x_fuse_bay_aft" = 101.60 'FUSE STATION: cabin (constant-section) AFT wall, AFT of Origin [mm]  (-Z side)
"x_fuse_tail"    = 152.40    'FUSE STATION: pod tail-tip plane, AFT of Origin [mm]  (-Z side); 2 in aft of cabin rear; M2->TT gap = boom sleeve
"span_ft"       = "b" / 304.8
"W_pay_lb"      = "W_payload" / 453.592
"W_empty_lb"    = "W_empty" / 453.592
"TO_target_ft"  = 10
"h_nose_top"            = 60.0364   'Exact height of nose flat top ABOVE waterline [mm] (raised +47.5 for 75% lift)
"h_nose_bottom"         = 9.2364    'Exact height of nose flat bottom ABOVE waterline [mm] (crossed above WL after 75% lift)
"h_nose_break_top"      = 68.1182   'Exact height of nose top shoulder break (M1) ABOVE waterline [mm] (raised +47.5 for 75% lift)
"h_nose_break_bottom"   = 13.3096   'Exact depth of nose belly shoulder break (M4) BELOW waterline [mm] (still below; raised +47.5)
"h_tail_break_top"      = 60        'Exact height of the tail top shoulder break (M2) ABOVE waterline [mm]; absolute, user-set'
"h_tail_break_bottom"   = 13.3096   'Exact depth of the tail belly shoulder break (M3) BELOW waterline [mm]; positive magnitude, dimension downward'
"w_fuse_break"          = 38.10     'Exact port half-width at planform transition breaks (P1/P2) [mm]
"h_tail_top"            = 35.78915    'Exact height of tail flat top ABOVE waterline [mm]
"h_tail_bottom"         = 10.38915    'Exact height of tail flat bottom ABOVE waterline [mm]
"x_fuse_midnose"        = 228.60 'Absolute Z-station of the fwd break column (M1/M4/P1) forward of LE [mm]; nose midpoint
"x_fuse_midtail"        = 127.00 'Absolute Z-station of the aft break column (M2/M3/P2) aft of LE [mm]; = x_fuse_bay_aft + 1 in
"w_fuse_nose_half"      = 25.40     'Exact port half-width of blunt nose face [mm] (Old: w_fuse / 4)
"w_fuse_break_fwd"      = 41.9054   'Exact port half-width at forward shoulder break (P1) [mm]
"w_fuse_cabin_fwd_half" = 50.80     'Exact port half-width at front firewall corner (CL) [mm] (Old: w_fuse / 2)
"w_fuse_cabin_aft_half" = 50.80     'Exact port half-width at rear cabin corner (TL) [mm] (Old: w_fuse / 2)
"w_fuse_break_aft"      = 33.6493   'Exact port half-width at rear taper shoulder break (P2) [mm]
"w_fuse_tail_half"      = 12.7    'Exact port half-width of tail cone exit cap (EL) [mm] (Old: tail_exit_D / 2)
"x_fuse_sleeve_top"     = 177.80    'Absolute Z-station of sleeve top-aft vertex (SL_T) aft of LE [mm]; = x_fuse_tail + 1 in
"L_fuse"                = "x_fuse_nose" + "x_fuse_sleeve_top"   'total fuselage length [mm]; the outline reaches the sleeve top, not x_fuse_tail'
"h_sleeve_top"          = 35.78915   'Exact height of sleeve top-aft vertex (SL_T) ABOVE waterline [mm]; = h_tail_top (constant-section sleeve)
"x_fuse_sleeve_bottom"  = 177.80    'Absolute Z-station of sleeve bottom-aft vertex (SL_B) aft of LE [mm]; = x_fuse_tail + 1 in
"h_sleeve_bottom"       = 10.38915   'Exact height of sleeve bottom-aft vertex (SL_B) ABOVE waterline [mm]; = h_tail_bottom (constant-section sleeve)
"x_fuse_sleeve_plan"    = 177.80    'Absolute Z-station of planform sleeve vertices (SL_P/SL_C) aft of LE [mm]; = x_fuse_tail + 1 in
"w_fuse_sleeve_half"    = 12.7      'Exact port half-width at sleeve end (SL_P) [mm]; = w_fuse_tail_half (constant-section sleeve)
"servo_L"        = 23        'ail/flap servo body length, chordwise +Z [mm] (starter)
"servo_W"        = 12        'ail/flap servo body width, spanwise X [mm] (starter)
"servo_H"        = 22        'ail/flap servo body height, vertical Y [mm] (starter)
"hatch_open_deg" = 75        'payload drop-door max open angle from closed [deg] (starter)
"horn_R"         = 12        'drop-door servo output-horn radius [mm] (starter)
"link_L"         = 30        'drop-door actuation push-link length [mm] (starter)
"tail_steer_rake"= 12        'taildragger tailwheel kingpin rake from vertical [deg] (starter)
"wheel_tail_dia" = 30        'taildragger tailwheel diameter [mm] (starter)
"gear_h_tail"           = "wheel_tail_dia" / 2   'tailwheel axle ht above ground = wheel_tail_dia/2 (tire flush) [mm]
"h_wing_seat"    = 20        'wing-seat structural-deck height above waterline +Y [mm] (starter)
"w_wing_seat"    = 90        'lateral spacing of port/starboard shear-tie faces [mm] (starter)
"w_wing_seat_half"      = "w_wing_seat" / 2   'wing-seat shear-tie plane offset from Right Plane [mm]
"bolt_pitch"     = 30        'wing-mount bolt-hole spacing along seat [mm] (starter)
"bolt_dia"       = 5         'wing-mount bolt-hole diameter [mm] (starter)
"plumb_drop"     = 25        'drain/plumbing stack projection BELOW bottom keel [mm] (starter)
"belly_margin"   = 15        'min belly-to-ground gap retained at full gear compression [mm] (starter)
"x_steer_servo"  = 250       'ground-steering servo AFT station from LE [mm] (-Z) (starter)
"n_rib_HT"       = 4         'ribs per HT semi-span; HT section-plane pattern count (starter)
"rib_pitch_HT"   = "b_semi_HT" / ("n_rib_HT" - 1)   'HT rib-plane spanwise pitch [mm]; seeds LPTN_RibPlanes_HT, last plane at b_HT/2 (derived, tracks n_rib_HT)
"n_rib_VT"       = 4         'section planes per VT fin height; VT pattern count (starter)
"rib_pitch_VT"   = "b_VT" / ("n_rib_VT" - 1)   'VT section-plane pitch up +Y [mm]; seeds LPTN_RibPlanes_VT, last plane at b_VT (derived, tracks n_rib_VT)
"dihedral_HT"    = 0         'HT dihedral [deg]; drives PLN_Dihedral_HT tilt (0 = flat, on Top Plane)
"b_semi_HT_proj"        = "b_semi_HT" / cos("dihedral_HT" * pi/180)   'HT SPAR TIP: in-plane spanwise dist from Origin on PLN_Dihedral_HT [mm]
"h_VT_tip"              = "y_emp_axis" + "b_VT"   'VT fin-top height above the waterline [mm]; the fin roots on AX_Long_Emp'
```
---

<details>
<summary><b>After entering</b></summary>

### After entering
- Force-rebuild (`Ctrl-Q`); confirm no equation flags red and that `arm_clear`, `sw_clear` are both ≥ 0.
- Set `x_NP` from XFLR5/AVL; re-check that loaded and drained CG both land in `x_CG_fwd…x_CG_aft`.
- Drive `V_water` up (more payload) and watch `W_TO`, `WL_g_dm2`, and your takeoff prediction respond — that's the central Micro trade.
- Starters describe a ~1.1 m, ~2 kg-water Micro airframe for illustration, **not** a design point — replace with your team's sizing outputs.

</details>

</details>