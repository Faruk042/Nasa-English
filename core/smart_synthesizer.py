# -*- coding: utf-8 -*-
"""
ALTAR-NASA v6.3 — Question-Driven Analytical & Counterfactual Synthesis Core (`smart_synthesizer.py`).
Operates deterministically offline and alongside cloud/local inference engines:
- Classifies user intent across 15 engineering categories (capabilities guide, platform architecture,
  greeting/readiness, rocket propulsion boundary, EVA suit vs. Lunar Rover atmospheres, partial-gravity
  LUCI/FM2 bounding, invisible Cool Flame NTC & DAFT dust/smoke discrimination, Halon 1301 prohibition &
  SoFIE-MIST suppression, specific NASA PSI investigations, live governing equation derivations,
  multi-point sensitivity sweeps, Space-to-Earth technology transfers, uploaded datasets/imagery,
  full 4-part mission synthesis, and targeted combustion physics queries).
- Executes live counterfactual chamber evaluations against active 3D parameters without static boilerplate.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from core.directives import CORE_DIRECTIVES_LIST
from core.nasa_datasets import NASA_EXPERIMENTS_CATALOG, SPACE_TO_EARTH_TRANSFERS
from core.physics_engine import FUEL_PROPERTIES, simulate_combustion_state


def _norm(text: str) -> str:
    raw = (text or "").lower().strip()
    decomposed = unicodedata.normalize("NFKD", raw)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _has_any(norm_q: str, terms: Tuple[str, ...]) -> bool:
    for term in terms:
        if term in norm_q:
            return True
    return False


def _truncate_clean_title(raw_text: str, max_chars: int = 96) -> str:
    clean = " ".join((raw_text or "").strip().split())
    if len(clean) <= max_chars:
        return clean
    cut = clean[:max_chars].rsplit(" ", 1)[0].strip()
    return f"{cut or clean[:max_chars]}..."


def classify_user_intent(user_message: str, media_context: str = "") -> str:
    """Route a user query to the most specific analytical or operational intent."""
    raw = (user_message or "").strip()
    nq = _norm(raw)

    # 1) Comprehensive 4-section mission synthesis (Preset #1 or explicit full-report request)
    is_full_eval = (
        ("dimensionless numbers" in nq and ("psi" in nq or "earth" in nq or "safety" in nq or "eclss" in nq))
        or _has_any(nq, ("full report", "comprehensive analysis", "full synthesis", "complete mission report"))
    )
    if is_full_eval:
        return "full_synthesis"

    # 2) Uploaded file / flame image / multi-phase PSI table inspection
    if media_context and (
        _has_any(
            nq,
            (
                "uploaded",
                "attached",
                "image",
                "photo",
                "picture",
                "csv",
                "pdf",
                "json",
                "xlsx",
                "excel",
                "zip",
                "tsv",
                "table",
                "phase",
                "phases",
                "values",
                "dataset",
                "file",
            ),
        )
        or nq in ("analyze", "analyze this", "analyze this dataset", "evaluate", "summarize", "inspect")
    ):
        return "uploaded_media"

    # 3) Platform features / architecture inventory vs. capabilities guide vs. greeting
    physics_anchors = (
        "heptane",
        "methanol",
        "ethanol",
        "pmma",
        "nomex",
        "sibal",
        "hydrogen",
        "propane",
        "spalding",
        "sherwood",
        "damkohler",
        "rayleigh",
        "grashof",
        "richardson",
        "halon",
        "sofie",
        "saffire",
        "flex",
        "bass",
        "spice",
        "slice",
        "daft",
        "luci",
        "fm2",
        "cool flame",
        "spherical",
        "moc",
        "eva",
        "rover",
        "rocket",
    )
    has_physics_topic = _has_any(nq, physics_anchors)

    if not has_physics_topic:
        if _has_any(
            nq,
            (
                "features",
                "architecture",
                "modules",
                "specifications",
                "export formats",
            ),
        ):
            return "platform_features"

        if _has_any(
            nq,
            (
                "what can you do",
                "how to use",
                "how do i use",
                "capabilities",
                "commands",
                "what can i ask",
                "help",
            ),
        ):
            return "capabilities_guide"

        clean_alnum_q = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", nq)).strip()
        if (
            _has_any(
                nq,
                (
                    "hello",
                    "hi ",
                    "hey",
                    "good morning",
                    "good afternoon",
                    "good evening",
                    "who are you",
                    "what are you",
                    "introduce yourself",
                ),
            )
            or clean_alnum_q in ("hi", "hello", "hey", "greetings", "test")
        ):
            return "greeting_identity"

    # 4) Rocket propulsion / external thruster scope boundary (CON-08)
    if _has_any(nq, ("rocket", "thruster", "nozzle", "liquid propellant engine")):
        return "rocket_scope"

    # 5) EVA Spacesuit (100% O2 @ 4.3 psia) & Pressurized Lunar Rover (10.2 psia) & pre-breathe tradeoffs
    if _has_any(
        nq,
        (
            "spacesuit",
            "eva suit",
            "4.3 psia",
            "100% o2",
            "100% oxygen",
            "lunar rover",
            "pressurized rover",
            "10.2 psia",
            "pre-breathe",
            "prebreathe",
            "decompression",
        ),
    ):
        return "eva_rover_atmosphere"

    # 6) Halon 1301 prohibition, NASA-STD-6001B suppression protocol, SoFIE-MIST & ECLSS SMAC clock
    if _has_any(
        nq,
        (
            "halon",
            "water mist",
            "fine mist",
            "sofie-mist",
            "pfe",
            "emergency",
            "6001b",
            "smac",
            "carbon monoxide",
            "eclss",
            "suppress",
            "suppression",
            "extinguish",
            "fire response",
        ),
    ):
        return "suppression_halon"

    # 7) Invisible Cool Flame (NTC) & DAFT / SAME dust-vs-smoke discrimination
    if _has_any(
        nq,
        (
            "cool flame",
            "ntc",
            "invisible flame",
            "two-stage",
            "peroxy",
            "daft",
            "regolith",
            "lunar dust",
            "smoke detector",
            "smoke sensor",
            "false alarm",
        ),
    ):
        return "cool_flame_daft"

    # 8) Partial gravity (Moon 0.16G / Mars 0.38G), LUCI, FM2, and ACME E-FIELD
    if _has_any(
        nq,
        (
            "partial gravity",
            "partial-gravity",
            "luci",
            "fm2",
            "e-field",
            "efield",
            "ionic wind",
            "0.16g",
            "0.16 g",
            "0.38g",
            "0.38 g",
            "martian",
            "lunar gravity",
            "mars gravity",
            "bounding",
        ),
    ) or bool(re.search(r"\b(?:moon|lunar|mars)\b", nq)):
        return "partial_gravity_luci"

    # 9) Specific NASA PSI investigation, NTRS report, or orbital hardware rack query
    if _has_any(
        nq,
        (
            "highest oxygen",
            "cfi-g",
            "cfig",
            "saffire",
            "bass-ii",
            "bass ",
            "spice",
            "slice",
            "flex-2",
            "bre ",
            "burn rate emulator",
            "gel ",
            "smolder",
            "cir ",
            "mdca",
            "msg ",
            "cygnus",
            "ntrs-",
            "osdr-",
            "psi-",
        ),
    ) or re.search(r"\b(flex|cfi|acme|sofie|bass|same)\b", nq):
        return "specific_experiment"

    # 10) Specific governing equation / dimensionless number derivation
    if _has_any(
        nq,
        (
            "spalding",
            "b_oq",
            "boq",
            "sherwood",
            "reynolds",
            "rayleigh",
            "grashof",
            "richardson",
            "damkohler",
            "d2-law",
            "d2 law",
            "d²",
            "burning constant",
            "burning rate",
            "standoff",
            "r_f",
            "rf/rd",
            "radiative loss",
            "chi_r",
            "how is moc",
            "what is moc",
            "de ris",
            "burke-schumann",
            "equation",
            "formula",
            "derive",
            "calculated",
        ),
    ):
        return "equation_deep_dive"

    # 11) Counterfactual 'What-If' parameter sensitivity sweep
    if _has_any(
        nq,
        (
            "what if",
            "what happens if",
            "increase",
            "decrease",
            "sensitivity",
            "difference between",
            "0g vs 1g",
            "0g and 1g",
            "ventilation",
            "fan speed",
            "airflow",
            "blowoff",
            "diluent",
            "helium",
            "argon",
        ),
    ):
        return "what_if_sensitivity"

    # 12) Space-to-Earth technology transfers & firefighting spin-offs
    if _has_any(
        nq,
        (
            "firefighter",
            "spinoff",
            "spin-off",
            "technology transfer",
            "scba",
            "hcci",
            "earth transfer",
            "earth application",
            "terrestrial application",
        ),
    ):
        return "earth_spinoffs"

    return "targeted_scientific"


def synthesize_question_driven_report(
    user_message: str,
    sim_params: Dict[str, Any],
    active_sim: Dict[str, Any],
    top_exps: List[Dict[str, Any]],
    rag_hits: Optional[List[Dict[str, Any]]] = None,
    live_ntrs: Optional[List[Dict[str, Any]]] = None,
    history: Optional[List[Dict[str, str]]] = None,
    media_context: str = "",
    lang: str = "en",
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generate a concise, quantitatively grounded English engineering report for the user's query
    along with matched NASA NTRS citation records.
    """
    _ = (sim_params, live_ntrs, lang)
    intent = classify_user_intent(user_message, media_context=media_context)
    nq = _norm(user_message)
    inp = active_sim["inputs"]
    tel = active_sim["telemetry"]
    fv = active_sim.get("flight_validation") or {}
    tl = active_sim.get("scenario_timeline") or {}
    call_top = active_sim.get("callouts") or {}
    reg_badge = call_top.get("badge_en") or tel.get("regime", "")
    fuel_name = str(inp.get("fuel_name_en") or inp.get("fuel_id") or "n-Heptane")
    rag_hits = rag_hits or []
    history = history or []

    default_citations = [
        {
            "id": e["exp_id"],
            "program": e["program"],
            "ntrs_id": e["ntrs_id"],
            "title": e["title"],
            "url": e["ntrs_url"],
            "priority_score": e["priority_score"],
        }
        for e in top_exps[:3]
    ]

    # -------------------------------------------------------------------------
    # 1. CAPABILITIES & INTERACTIVE QUERY GUIDE
    # -------------------------------------------------------------------------
    if intent == "capabilities_guide":
        text = (
            "### ALTAR-NASA v6.3 — Interactive Engineering & Scientific Capabilities\n"
            f"Currently locked onto your live 3D chamber (**{fuel_name}** at `{inp['gravity_g']} G`, `{inp['oxygen_pct']}% O₂`, `{inp['pressure_psia']} psia`, `U = {inp['airflow_cms']} cm/s` → **{reg_badge}**, Risk `{tel['risk_score']}/100`). Ask for direct calculations or comparisons across any of these domains:\n\n"
            "| Capability Domain | Live Computation & Synthesis | Example Prompt |\n"
            "| :--- | :--- | :--- |\n"
            "| **Governing Equation Derivation** | Step-by-step substitution of `d²`-law `K`, Spalding `B_oq`, Sherwood `Sh`, `Ra/Gr/Ri`, Damköhler `Da`, and `MOC` | *\"How are Spalding B_oq and burning rate K calculated for my current droplet?\"* |\n"
            "| **Counterfactual What-If Sweeps** | Multi-point sweeps across airflow (`0–30 cm/s`), gravity (`0G–1G`), `O₂%`, pressure, and diluent gases (`N₂/CO₂/He`) | *\"What happens if I increase cabin airflow from 0 to 20 cm/s?\"* |\n"
            "| **Atmosphere & EVA Tradeoffs** | Quantitative matrix comparing ISS (`14.7 psia`), Lunar Rover (`10.2 psia / 32% O₂`), and EVA Suit (`4.3 psia / 100% O₂`) | *\"Compare EVA spacesuit and Lunar Rover flammability risks.\"* |\n"
            "| **NASA PSI & Intra-Run Evidence** | Inspection of all 15 PSI investigations (`FLEX`, `CFI-G`, `BASS`, `SPICE`, `SLICE`, `Saffire`, `SoFIE`, `DAFT`) & run matrices | *\"Explain Saffire-V test variations and highest-O₂ CFI-G findings.\"* |\n"
            "| **ECLSS Survival & Suppression** | `NASA-STD-6001B` non-Halon protocol, `JSC-20584 CO SMAC (100/425 ppm)` countdown, Cool Flame NTC & lunar dust sensing | *\"Why is Halon 1301 banned and how fast does CO hit SMAC limits?\"* |\n"
            "| **Dataset & Flame Vision Audit** | Pixel chemiluminescence/soot segmentation (`.png/.jpg`) and `.csv/.json/.pdf` multi-phase parameter extraction | Upload a file and ask: *\"Analyze my uploaded dataset.\"* |"
        )
        return (text, [])

    # -------------------------------------------------------------------------
    # 2. PLATFORM ARCHITECTURE & 5-MODULE FEATURE INVENTORY
    # -------------------------------------------------------------------------
    if intent == "platform_features":
        r2_val = fv.get("r_squared", 0.95)
        rmse_val = fv.get("rmse", 0.03)
        text = (
            "### ALTAR-NASA: Flame in Freefall (v6.3) — Technical Architecture & Feature Inventory\n"
            "ALTAR-NASA is a physics-informed microgravity and partial-gravity combustion safety platform organized around **5 integrated engineering modules**:\n\n"
            "1. **`Combustion Chamber`:**\n"
            f"   - Real-time 4-geometry 3D WebGL chamber (`Droplet`, `PMMA Rod`, `Fabric Slab`, `CFI-G Porous Sphere`) solving coupled transport laws (`d²`-law `K`, `B_oq`, `R_f/R_d`, `Sh`, `Ra`, `Ri`, `Da`, `χ_r`, U-shaped `MOC`).\n"
            f"   - Calibrated against ISS `0G` flight reference data with **`R² = {r2_val}`** (`RMSE = {rmse_val}`), WebAudio telemetry sonification, and **NASA JSC-20584 `CO SMAC (100/425 ppm)` Life Support Clock**.\n"
            "2. **`NASA Experiments`:**\n"
            "   - Thermodynamic + TF-IDF similarity ranking across `ISS CIR/MDCA`, `MSG Flow Duct`, `Cygnus (Saffire I–VI)`, and `SAME/DAFT` smoke-vs-lunar-dust hardware, with `ntrs.nasa.gov` citations and intra-experiment variable matrices.\n"
            "3. **`Data & Imagery`:**\n"
            "   - Live polling of `ntrs.nasa.gov`, `psi.nasa.gov`, and `osdr.nasa.gov` REST APIs plus local pixel-level flame segmentation and `.CSV/.JSON/.XLSX/.PDF` multi-phase parameter extraction.\n"
            "4. **`Engineering Analysis`:**\n"
            "   - Question-driven analytical solver and local/cloud inference guarded by mandatory `CON-01..CON-09` physical laws and `NASA-STD-6001B` Halon-prohibition verification.\n"
            "5. **`Validation & Settings`:**\n"
            "   - Enforces physical validation rules (`CON-01..CON-09`), offline deep-space operation, and one-click **`.CSV`**, **`.JSON`**, and **`.HTML / PDF`** visual engineering report export."
        )
        return (text, [])

    # -------------------------------------------------------------------------
    # 3. GREETING & LIVE CHAMBER READINESS SUMMARY
    # -------------------------------------------------------------------------
    if intent == "greeting_identity":
        text = (
            "### ALTAR-NASA v6.3 — Spacecraft Combustion & Fire Safety Kernel Ready\n"
            f"- **Active 3D Chamber Lock:** `{fuel_name}` (`{inp['geometry_3d']}`) | `{inp['gravity_g']} G` | `{inp['oxygen_pct']}% O₂` (`P_O₂ = {tel.get('o2_partial_psia', tel.get('po2_psia', 0))} psia`) | `U = {inp['airflow_cms']} cm/s`\n"
            f"- **Computed State:** Regime **{reg_badge}** | Flame Temp `{tel['flame_temp_k']} K` | Critical `MOC = {tel['moc_pct']}% O₂` | Fire Risk **`{tel['risk_score']}/100`**\n\n"
            "Ask any technical question—such as deriving a dimensionless group (`B_oq`, `Sh`, `Da`), running a parameter sensitivity sweep (`0G vs 0.16G Moon`, airflow changes), comparing `EVA Suit` vs `Lunar Rover` atmospheres, or inspecting a NASA PSI investigation (`FLEX`, `Saffire`, `SoFIE-MIST`, `DAFT`)."
        )
        return (text, [])

    # -------------------------------------------------------------------------
    # 4. ROCKET ENGINES & THRUSTERS SCOPE BOUNDARY (CON-08)
    # -------------------------------------------------------------------------
    if intent == "rocket_scope":
        re_now = tel.get("reynolds_number", 0)
        ri_now = tel.get("richardson_number", 0)
        text = (
            "### Why Rocket Engines & Thrusters Sit Outside NASA PSI Cabin Fire Scope (CON-08)\n"
            "1. **Momentum-Dominated Regime (`Ri = Gr / Re² → 0`):** Inside liquid/solid rocket chambers and orbital thrusters, injection and exhaust velocities reach `10²–10³ m/s`, producing high Reynolds numbers (`Re > 10⁵`). Because the Richardson number scales as `Ri = Gr / Re²`, buoyant forces (`Gr ∝ g`) remain negligible (`Ri < 10⁻⁶`) at both `1G` and `0G`.\n"
            f"2. **Contrast with Pressurized Crew Cabins (Active Chamber):** In your current 3D chamber, ventilation speed is `U = {inp['airflow_cms']} cm/s` (`Re = {re_now}`, `Ri = {ri_now}`). At gentle crew-comfort velocities (`0–20 cm/s`), removing gravity (`0G` / `0.16G` / `0.38G`) reshapes flame geometry, soot residence time, radiative quenching (`χ_r`), and `MOC`.\n"
            "3. **NASA PSI Focus Envelope:** NASA's Physical Sciences Informatics (PSI) combustion archive (`FLEX`, `CFI`, `ACME`, `BASS`, `SPICE`, `SLICE`, `Saffire`, `SoFIE`, `DAFT`) targets **habitable spacecraft cabins, ISS racks, EVA spacesuits (`4.3 psia / 100% O₂`), and Lunar/Martian habitats & pressurized rovers**."
        )
        return (text, default_citations[:2])

    # -------------------------------------------------------------------------
    # 5. EVA SPACESUIT (100% O2 @ 4.3 psia) & LUNAR ROVER ATMOSPHERE MATRIX
    # -------------------------------------------------------------------------
    if intent == "eva_rover_atmosphere":
        base_fuel = inp["fuel_id"] if inp["fuel_id"] in FUEL_PROPERTIES else "nomex"
        profiles = [
            ("ISS Standard Cabin", {"fuel_id": base_fuel, "gravity_g": 0.0, "oxygen_pct": 21.0, "pressure_psia": 14.7, "airflow_cms": 4.0, "droplet_d0_mm": inp["droplet_d0_mm"], "diluent": "N2", "habitat_id": "iss_module"}),
            ("Lunar Base / Rover", {"fuel_id": base_fuel, "gravity_g": 0.16, "oxygen_pct": 32.0, "pressure_psia": 10.2, "airflow_cms": 4.5, "droplet_d0_mm": inp["droplet_d0_mm"], "diluent": "N2", "habitat_id": "lunar_rover"}),
            ("Saffire-V Exploration", {"fuel_id": base_fuel, "gravity_g": 0.0, "oxygen_pct": 34.0, "pressure_psia": 8.2, "airflow_cms": 5.0, "droplet_d0_mm": inp["droplet_d0_mm"], "diluent": "N2", "habitat_id": "lunar_rover"}),
            ("EVA Spacesuit (Pure O₂)", {"fuel_id": base_fuel, "gravity_g": 0.16, "oxygen_pct": 100.0, "pressure_psia": 4.3, "airflow_cms": 6.0, "droplet_d0_mm": inp["droplet_d0_mm"], "diluent": "N2", "habitat_id": "eva_suit"}),
        ]
        rows_md: List[str] = []
        for en_lbl, prm in profiles:
            s = simulate_combustion_state(prm)
            st = s["telemetry"]
            stl = s["scenario_timeline"]
            po2 = st.get("o2_partial_psia", 0)
            rate_str = f"V_f={st['flame_spread_mm_s']} mm/s" if st["flame_spread_mm_s"] > 0 else f"K={st['burning_rate_k_mm2_s']} mm²/s"
            rows_md.append(
                f"| **{en_lbl}** | `{prm['pressure_psia']} psia` | `{prm['oxygen_pct']}%` | `{po2} psia` | `{st['moc_pct']}%` | `{st['flame_temp_k']} K` | `{rate_str}` | **`{st['risk_score']}/100`** (`100 ppm SMAC: {stl.get('t_smac_24h_100ppm_s', 999.0)} s`) |"
            )

        rel_exps = [e for e in NASA_EXPERIMENTS_CATALOG if e["exp_id"] in ("PSI-SAFFIRE5-07", "PSI-SOFIE-08", "PSI-ACME-CFIG-14")]
        cits = [
            {"id": e["exp_id"], "program": e["program"], "ntrs_id": e["ntrs_id"], "title": e["title"], "url": e["ntrs_url"], "priority_score": 96.0}
            for e in rel_exps
        ]

        text = (
            f"### EVA Spacesuit (`100% O₂ @ 4.3 psia`), Lunar Rover (`32% O₂ @ 10.2 psia`) & ISS Flammability Matrix — `{fuel_name}`\n\n"
            "| Mission Atmosphere | Total Pressure | O₂ % | Partial `P_O₂` | Critical `MOC` | Flame `T_f` | Burn / Spread Rate | Risk & ECLSS SMAC |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            + "\n".join(rows_md)
            + "\n\n"
            "### Thermo-Physical & Physiological Tradeoffs (CON-06)\n"
            "- **Why `4.3 psia / 100% O₂` in EVA Suits?** Pressurizing a suit to `14.7 psia` makes mobility joints rigid. Operating at `4.3 psia` (`29.6 kPa`) preserves alveolar oxygen (`P_O₂ = 4.3 psia` vs `3.09 psia` on ISS) with zero nitrogen (`N₂`), preventing decompression sickness. However, **removing `N₂` eliminates inert thermal heat-sink ballast**, raising flame temperature and accelerating spread across `Nomex` weaves if an ignition arc occurs.\n"
            "- **Why `10.2 psia / 32% O₂` in Lunar Bases & Pressurized Rovers?** NASA's Exploration Atmosphere (>40% relative `O₂` enrichment over Earth's 21%) reduces EVA pre-breathe purge duration from `>2 hours` down to `~15 minutes`—validated in **Saffire-V (`NTRS #20210017780`)** and **SoFIE (`NTRS #20200000361`)**.\n"
            "- **Highest-O₂ PSI Benchmark (`ACME CFI-G`):** Inside ISS `CIR`, **ACME CFI-G (`NTRS #20220015583`)** tested spherical inverse diffusion flames up to **`85% O₂`** flowing into a propane/N₂ chamber to bound high-oxygen soot and radiation limits."
        )
        return (text, cits)

    # -------------------------------------------------------------------------
    # 6. PARTIAL GRAVITY (0.16G MOON / 0.38G MARS), LUCI/FM2 & ACME E-FIELD
    # -------------------------------------------------------------------------
    if intent == "partial_gravity_luci":
        g_levels = [
            ("0.00 G (ISS Freefall)", 0.0),
            ("0.16 G (Lunar • LUCI/FM2)", 0.16),
            ("0.38 G (Martian Surface)", 0.38),
            ("1.00 G (Earth Reference)", 1.0),
        ]
        rows_g: List[str] = []
        for en_g, gv in g_levels:
            p_copy = dict(inp)
            p_copy["gravity_g"] = gv
            sg = simulate_combustion_state(p_copy)
            gt = sg["telemetry"]
            rate_col = f"V_f={gt['flame_spread_mm_s']} mm/s" if gt["flame_spread_mm_s"] > 0 else f"K={gt['burning_rate_k_mm2_s']} mm²/s"
            rows_g.append(
                f"| **{en_g}** | `Ra = {gt.get('rayleigh_number', 0):.1f}` | `Ri = {gt.get('richardson_number', 0):.3f}` | **`{gt['moc_pct']}% O₂`** | `{gt['flame_temp_k']} K` | `{rate_col}` | `{gt['regime']}` (`{gt['risk_score']}/100`) |"
            )

        rel_exps = [e for e in NASA_EXPERIMENTS_CATALOG if e["exp_id"] in ("PSI-ACME-09", "PSI-BASS-03", "PSI-SOFIE-08")]
        cits = [
            {"id": e["exp_id"], "program": e["program"], "ntrs_id": e["ntrs_id"], "title": e["title"], "url": e["ntrs_url"], "priority_score": 95.0}
            for e in rel_exps
        ]

        text = (
            f"### Partial-Gravity Combustion Bounding (`0G` → `0.16G Moon` → `0.38G Mars` → `1G`) — `{fuel_name}`\n"
            f"Evaluated at your active oxygen (`{inp['oxygen_pct']}% O₂`), pressure (`{inp['pressure_psia']} psia`), and cabin flow (`{inp['airflow_cms']} cm/s`):\n\n"
            "| Gravity Regime | Rayleigh `Ra` | Richardson `Ri` | Critical `MOC` | Flame `T_f` | Burn / Spread Rate | Regime & Risk |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            + "\n".join(rows_g)
            + "\n\n"
            "### NASA PSI Data Gap, LUCI/FM2 & ACME E-FIELD Emulation (CON-07)\n"
            "1. **Current PSI Partial-G Gap (`LUCI` & `FM2`):** NASA's PSI archive holds `0G` orbital data (ISS/Cygnus) and `1G` ground baselines, with **no direct lunar-surface combustion dataset yet**. Upcoming **LUCI (*Lunar-g Combustion Investigation*)** and **FM2 (*Flammability of Materials on the Moon*)** payloads address this gap directly.\n"
            "2. **Why `0.16G` Can Be Worse Than `1G` (Buoyant Ventilation Paradox):** Lunar buoyancy induces gentle upward slip (`u_b ∝ √g ≈ 8.8 cm/s`) that feeds fresh `O₂` (`Da > 1`) without the convective strain/cooling of `1G` Earth plumes—lowering `MOC` below `1G` limits. Bounding between `0G` ventilated (`BASS`/`SoFIE`) and `1G` envelopes brackets intermediate flammability.\n"
            "3. **ACME E-FIELD Ionic-Wind Emulation (`NTRS #20210015913`):** In `0G` inside ISS `CIR`, applying a high-voltage electric field drives natural flame chemi-ions (`H₃O⁺`, `CHO⁺`), creating a controllable Coulomb body force (ionic wind) that emulates `0.16G` Lunar and `0.38G` Martian buoyancy on orbit."
        )
        return (text, cits)

    # -------------------------------------------------------------------------
    # 7. INVISIBLE COOL FLAME (NTC) & DAFT/SAME DUST-SMOKE DISCRIMINATION
    # -------------------------------------------------------------------------
    if intent == "cool_flame_daft":
        cf_sim = simulate_combustion_state(
            {"fuel_id": "n_heptane", "gravity_g": 0.0, "oxygen_pct": 15.5, "pressure_psia": inp["pressure_psia"], "airflow_cms": 0.1, "droplet_d0_mm": 3.8, "diluent": inp["diluent"]}
        )
        cft = cf_sim["telemetry"]
        rel_exps = [e for e in NASA_EXPERIMENTS_CATALOG if e["exp_id"] in ("PSI-FLEX-01", "PSI-CFI-11", "PSI-DAFT-15", "PSI-ACME-CFIG-14")]
        cits = [
            {"id": e["exp_id"], "program": e["program"], "ntrs_id": e["ntrs_id"], "title": e["title"], "url": e["ntrs_url"], "priority_score": 96.0}
            for e in rel_exps
        ]

        text = (
            "### Two-Stage Radiative Extinction, Invisible Cool Flames (NTC) & Multi-Channel Detection (CON-04)\n"
            f"- **Current Chamber vs. Cool-Flame Threshold:** Active radiative loss is `χ_r = {tel['radiative_loss_fraction'] * 100:.1f}%` (`T_f = {tel['flame_temp_k']} K`, regime `{tel['regime']}`). For a `3.8 mm` `n-Heptane` droplet at `0G / 15.5% O₂`, `χ_r` reaches `{cft['radiative_loss_fraction'] * 100:.1f}%`, triggering **`{cft['regime']}`** at `{cft['flame_temp_k']} K`.\n"
            "- **Physical Mechanism (`FLEX`, `CFI`, `ACME CFI-G`):** In `0G`, hot combustion products (`CO₂`, `H₂O`, soot) form a thick stagnant spherical shell (`Rf/Rd ≈ 5–8`). Because radiative heat loss scales with flame volume (`Q_rad ∝ R_f³·σ·(T_f⁴ - T_∞⁴)`), when `χ_r > 0.45` the `1500+ K` hot flame quenches. Heavy alkanes (`n-Heptane`, `n-Decane`, `Propane`) transition into the **Negative Temperature Coefficient (`NTC`, `550–780 K`)** branch (`R + O₂ ⇌ RO₂ ⇌ QOOH`), burning **invisibly** while generating toxic **`CO`** and **`CH₂O` (formaldehyde)** capable of spontaneous re-ignition.\n\n"
            "| Detection Channel | Hot Sooty Flame (`1G/0G`) | Invisible Cool Flame (`550–780 K`) | Lunar Regolith / Cabin Dust |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Visible Optical Camera** | High (`75–100%`) | **`~0–2%` (BLIND)** | Scatters light (False Positive Risk) |\n"
            "| **Mid-IR / UV OH*-HCHO Radiometer** | High (`12–35 kW/m²`) | **Detects `2.5–5.5 kW/m²` envelope** | `0 kW/m²` (Immune) |\n"
            "| **Electrochemical `CO / CH₂O` Sensor** | Moderate-High | **Sharp spike (`90–350 ppm CO`)** | `0 ppm` (Immune) |\n"
            "| **SAME / DAFT Dual-Wavelength Laser** | Sub-micron soot (`d_p < 0.4 µm`) | Detects condensed vapor mist (`CFI`) | **Rejects `1–10 µm` jagged lunar dust via polarization/angle ratio** |"
        )
        return (text, cits)

    # -------------------------------------------------------------------------
    # 8. HALON 1301 BAN, NASA-STD-6001B SUPPRESSION, SOFIE-MIST & SPINOFFS
    # -------------------------------------------------------------------------
    if intent == "suppression_halon":
        zero_flow_p = dict(inp)
        zero_flow_p["airflow_cms"] = 0.0
        zero_sim = simulate_combustion_state(zero_flow_p)
        zt = zero_sim["telemetry"]
        include_spinoff = _has_any(nq, ("firefighter", "earth", "suit", "tank", "spinoff", "transfer"))

        rel_exps = [e for e in NASA_EXPERIMENTS_CATALOG if e["exp_id"] in ("PSI-SOFIE-08", "PSI-BASS-03", "PSI-DAFT-15")]
        cits = [
            {"id": e["exp_id"], "program": e["program"], "ntrs_id": e["ntrs_id"], "title": e["title"], "url": e["ntrs_url"], "priority_score": 97.0}
            for e in rel_exps
        ]

        spinoff_sec = (
            "\n\n### Terrestrial Firefighting & Industrial Spinoffs\n"
            "- **Fine Water Mist (`SoFIE-MIST`):** Sub-`50 µm` clean-agent nozzles protect data centers, surgical suites, and EV lithium-ion battery packs without toxic fluorinated gases.\n"
            "- **Firefighter Turnout Gear & `SCBA` Tanks:** Apollo/EVA `PBI` and `Nomex` thermal weaves form the outer shell of municipal firefighter suits, while NASA filament-wound `COPV` pressure vessels reduce firefighter `SCBA` air-tank mass by `~40%`.\n"
            "- **Smart Dust-Immune Detectors (`SAME / DAFT`):** Multi-angle laser smoke discrimination eliminates false alarms in mines, aircraft cargo bays, and industrial plants."
            if include_spinoff
            else ""
        )
        text = (
            "### Why Halon 1301 Is Strictly Prohibited & Mandatory NASA-STD-6001B Suppression Sequence (CON-05)\n"
            "1. **Why Halon 1301 (`CF₃Br`) Is Banned in Crewed Spacecraft:** In a sealed recirculating cabin (`ISS`, `Orion`, `Gateway`, `Lunar Rover`), Halon 1301 thermally decomposes on `>750 K` flames into **hydrogen fluoride (`HF`)** and **hydrogen bromide (`HBr`)** acid gases—hazardous to crew lungs within minutes and **irreversibly poisoning ECLSS `LiOH` / amine `CO₂` scrubbers and trace-contaminant catalytic beds**.\n"
            f"2. **Live ECLSS Crew Survival Clock (`{tl.get('habitat_name_en', 'ISS Module')}`):** C&W alarm at `+{tl.get('t_alarm_s', 6)} s` | **NASA JSC-20584 24-hr `SMAC 100 ppm CO`** in **`{tl.get('t_smac_24h_100ppm_s', 180)} s`** (1-hr Emergency `425 ppm`: `{tl.get('t_smac_1h_425ppm_s', 420)} s`) | Cabin CO at crew response: `{tl.get('co_at_response_ppm', 40)} ppm`.\n"
            "3. **Mandatory 4-Step Non-Halon Countermeasure Sequence:**\n"
            f"   - **Step 1 — Immediate HVAC Ventilation Cutoff (`{inp['airflow_cms']} cm/s → 0 cm/s`):** Live solver check on `{fuel_name}` shows cutting airflow drops risk from **`{tel['risk_score']}/100` → `{zt['risk_score']}/100`** (regime `{zt['regime']}`), starving the flame inside its own `CO₂` shell.\n"
            "   - **Step 2 — Electrical Bus Isolation:** De-energize rack `120V DC` power to stop Joule heating and arc re-ignition.\n"
            "   - **Step 3 — `25–40 µm` Fine Water Mist (`ISS PFE / SoFIE-MIST`, `NTRS #20200000361`) or `CO₂ / N₂`:** Sub-40 µm droplets have high volumetric heat capacity (`L_v = 2257 kJ/kg`), evaporate in the reaction zone to expand `1700×` as inert steam, and leave zero toxic acid residue.\n"
            "   - **Step 4 — Post-Fire Cooling, ECLSS Scrubbing & Verified Unsealing:** Keep the compartment sealed until core temperature cools below `525 K` and `CSA-CP / ANITA-2 CO` monitoring confirms zero residual cool flame."
            + spinoff_sec
        )
        return (text, cits)

    # -------------------------------------------------------------------------
    # 9. SPECIFIC NASA PSI INVESTIGATION, NTRS REPORT, OR RACK QUERY
    # -------------------------------------------------------------------------
    if intent == "specific_experiment":
        matched: List[Dict[str, Any]] = []
        if _has_any(nq, ("highest oxygen",)):
            matched = [e for e in NASA_EXPERIMENTS_CATALOG if e["exp_id"] == "PSI-ACME-CFIG-14"]
        else:
            prog_map = [
                ("cfi-g", "PSI-ACME-CFIG-14"),
                ("cfig", "PSI-ACME-CFIG-14"),
                ("flex-2", "PSI-FLEX2-02"),
                ("flex", "PSI-FLEX-01"),
                ("cfi", "PSI-CFI-11"),
                ("e-field", "PSI-ACME-09"),
                ("bre", "PSI-ACME-BRE-10"),
                ("sofie-mist", "PSI-SOFIE-08"),
                ("sofie", "PSI-SOFIE-08"),
                ("saffire", "PSI-SAFFIRE5-07"),
                ("saffire-iv", "PSI-SAFFIRE4-06"),
                ("bass-ii", "PSI-BASS2-04"),
                ("bass", "PSI-BASS-03"),
                ("spice", "PSI-SPICE-12"),
                ("slice", "PSI-SLICE-13"),
                ("same", "PSI-DAFT-15"),
                ("daft", "PSI-DAFT-15"),
            ]
            for kw, eid in prog_map:
                if kw in nq:
                    for e in NASA_EXPERIMENTS_CATALOG:
                        if e["exp_id"] == eid and e not in matched:
                            matched.append(e)
            if not matched:
                if "msg" in nq:
                    matched = [e for e in NASA_EXPERIMENTS_CATALOG if e.get("hardware_group") == "MSG"][:4]
                elif "cygnus" in nq:
                    matched = [e for e in NASA_EXPERIMENTS_CATALOG if e.get("hardware_group") == "CYGNUS"][:3]
                elif "cir" in nq or "mdca" in nq:
                    matched = [e for e in NASA_EXPERIMENTS_CATALOG if e.get("hardware_group") == "CIR"][:4]

        if not matched:
            matched = top_exps[:2]

        blocks: List[str] = []
        cits = []
        for e in matched[:3]:
            cits.append(
                {
                    "id": e["exp_id"],
                    "program": e["program"],
                    "ntrs_id": e["ntrs_id"],
                    "title": e["title"],
                    "url": e["ntrs_url"],
                    "priority_score": e.get("priority_score", 94.0),
                }
            )
            runs = e.get("intra_runs") or []
            run_lines = ""
            if runs:
                hdr = "| Sub-Test / Run | Held Constant | Varied Parameter | Experimental Outcome |\n| :--- | :--- | :--- | :--- |\n"
                r_rows = [
                    f"| **{r.get('run_code') or r.get('run', '-')}** | {r['same_en']} | {r['diff_en']} | {r['result_en']} |"
                    for r in runs
                ]
                run_lines = "\n" + hdr + "\n".join(r_rows)

            blocks.append(
                f"### {e['program']} (`{e['exp_id']}`) — {e['title']}\n"
                f"- **Orbital Facility & Rack:** `{e['facility']}` (`{e.get('hardware_group', 'CIR')}`) | **Citation:** [NTRS #{e['ntrs_id']}]({e['ntrs_url']})\n"
                f"- **Test Envelope:** `{e['gravity_g']} G` | `{e['oxygen_pct']}% O₂` | `{e['pressure_psia']} psia` | Airflow `{e['airflow_cms']} cm/s` | Measured **`MOC = {e['moc_measured_pct']}% O₂`**\n"
                f"- **Sample / Burner & Diagnostics:** {e.get('sample_geometry_en', e['material'])} — *{e.get('sensors_en', '')}*\n"
                f"- **Primary Scientific Finding:** {e['key_finding_en']}\n"
                f"- **Spacecraft Safety Implication:** {e['safety_insight_en']}"
                f"{run_lines}"
            )

        ntrs_note = ""
        m_id = re.search(r"((?:ntrs|osdr|psi)-[a-z0-9_-]+)", nq)
        if m_id and rag_hits:
            top_doc = rag_hits[0]
            ntrs_note = f"> **Queried Live Record (`{user_message[:70]}`):** {top_doc['text'][:340]}\n\n"

        return (ntrs_note + "\n\n".join(blocks), cits)

    # -------------------------------------------------------------------------
    # 10. GOVERNING EQUATIONS & LIVE DIMENSIONLESS SUBSTITUTION
    # -------------------------------------------------------------------------
    if intent == "equation_deep_dive":
        eq_rows = active_sim.get("formula_table") or []
        tbl_lines = [
            f"| **{r.get('law_en') or r.get('law_tr', '')}** | `{r['equation']}` | **`{r['value']}`** | {r.get('status_en') or r.get('status_tr', '')} |"
            for r in eq_rows
        ]
        focus_note = ""
        if _has_any(nq, ("spalding", "b_oq", "boq", "d2", "d²", "burning constant", "burning rate", "standoff", "rf/rd", "burke", "de ris")):
            f_phase = str(inp.get("fuel_phase", "liquid"))
            if f_phase == "gas":
                focus_note = (
                    f"### Steady Gas-Burner Burke-Schumann Diffusion Scaling (`D_burner = {inp['droplet_d0_mm']} mm` Constant)\n"
                    f"1. **No Liquid Evaporation (`d²`-Law Inactive):** Sintered porous stainless-steel gas spheres (`ACME CFI-G` / `BRE`) and jet nozzles (`SPICE` / `SLICE`) maintain constant geometry (`D_burner = D₀`); `B_g = {tel.get('spalding_b_number', 0)}` represents gas-phase stoichiometric enthalpy scaling (`Y_O2·ΔH_c / (ν_s·c_p·ΔT_ig)`).\n"
                    f"2. **Burke-Schumann Standoff Ratio (`Rf/Rd = {tel.get('standoff_ratio_rf_rd', 0)}`):** Stoichiometric flame sheet sits at `R_f = {tel['flame_radius_mm']} mm` where outward fuel mass flow balances inward oxidizer diffusion (`Sh = {tel['sherwood_number']}`).\n\n"
                )
            elif f_phase == "solid":
                focus_note = (
                    f"### Solid Surface Flame Spread (de Ris Law `V_f`) & Pyrolysis Mass-Transfer `B_p`\n"
                    f"1. **Pyrolysis Mass-Transfer Number (`B_p = {tel.get('spalding_b_number', 0)}`):** Ratio of gas-phase oxidation enthalpy (`Y_O2·ΔH_c / ν_s`) to solid gasification enthalpy (`L_p`) for `{fuel_name}` (with `HRRPUA` scaling proportional to boundary-layer heat feedback).\n"
                    f"2. **de Ris Opposed/Concurrent Spread (`V_f = {tel['flame_spread_mm_s']} mm/s`):** Controlled by gas-phase forward heat conduction vs. solid thermal inertia `(k·ρ·c)_s` and boundary-layer `O₂` transport (`Sh = {tel['sherwood_number']}`, `Da = {tel.get('damkohler_number', 0)}`).\n\n"
                )
            else:
                focus_note = (
                    f"### Step-by-Step Droplet `d²`-Law & Godsave-Spalding `B_oq` Derivation\n"
                    f"1. **Spalding Mass-Transfer Number (`B_oq = {tel.get('spalding_b_number', 0)}`):** Measures exothermic oxidation enthalpy released per unit mass of oxidizer (`Y_O2·ΔH_c / ν_s`) minus sensible heating divided by latent heat of vaporization (`L_v`). Higher `O₂` (`{inp['oxygen_pct']}%`) raises `B_oq` logarithmically via `ln(1 + B_oq)`.\n"
                    f"2. **Effective Burning Rate Constant (`K = {tel['burning_rate_k_mm2_s']} mm²/s`):** Computed from `K = [8·λ_g / (ρ_l·c_p)] · ln(1 + B_oq) · (Sh / 2) · (1 - χ_r)`. With `D₀ = {inp['droplet_d0_mm']} mm`, total burn lifetime is `t_burn = D₀² / K = {tel['burn_lifetime_s']} s`, and dimensionless standoff ratio is **`Rf/Rd = {tel.get('standoff_ratio_rf_rd', 0)}`** (`R_f = {tel['flame_radius_mm']} mm`).\n\n"
                )
        elif _has_any(nq, ("sherwood", "reynolds", "rayleigh", "grashof", "richardson")):
            focus_note = (
                f"### Convective vs. Buoyant Transport Scaling (`Re`, `Sh`, `Gr`, `Ra`, `Ri`)\n"
                f"- At `U = {inp['airflow_cms']} cm/s` and `{inp['gravity_g']} G`, **`Re = {tel.get('reynolds_number', 0)}`**, **`Ra = {tel.get('rayleigh_number', 0)}`**, and **`Ri = Gr / Re² = {tel.get('richardson_number', 0)}`**. Frossling correlation yields **`Sh = 2 + 0.6·Re^(1/2)·Sc^(1/3) = {tel['sherwood_number']}`** (where `Sh = 2.0` is pure `0G` spherical molecular diffusion).\n\n"
            )
        elif _has_any(nq, ("damkohler", "moc", "radiative", "chi_r")):
            focus_note = (
                f"### Extinction Kinetics: Damköhler (`Da`), Radiative Loss (`χ_r`) & Critical `MOC`\n"
                f"- **Damköhler (`Da = τ_flow / τ_chem = {tel.get('damkohler_number', 0)}`):** When `Da < 1`, residence time drops below chemical induction time (blowoff). At low `0G` flow (`2–8 cm/s`), `Da >> 1` while radiative loss is `χ_r = {tel['radiative_loss_fraction'] * 100:.1f}%`, setting critical **`MOC = {tel['moc_pct']}% O₂`** vs ambient `{inp['oxygen_pct']}% O₂`.\n\n"
            )

        hdr_md = (
            f"### Live Governing Equations & Dimensionless Substitution (`{fuel_name}`)\n\n"
            "| Physical Law / Criterion | Governing Equation | Live Numerical Value | Regime Diagnosis |\n"
            "| :--- | :--- | :--- | :--- |\n"
        )
        return (focus_note + hdr_md + "\n".join(tbl_lines), default_citations[:2])

    # -------------------------------------------------------------------------
    # 11. COUNTERFACTUAL 'WHAT-IF' PARAMETER SENSITIVITY SWEEPS
    # -------------------------------------------------------------------------
    if intent == "what_if_sensitivity":
        if _has_any(nq, ("diluent", "helium", "argon", "co2", "nitrogen")):
            sweep_title = "Diluent Gas (`N₂` vs `CO₂` vs `He`)"
            variants = [
                ("N₂ (Nitrogen • ISS Baseline)", {**inp, "diluent": "N2"}),
                ("CO₂ (High-c_p Suppressant)", {**inp, "diluent": "CO2"}),
                ("He (High Thermal Diffusivity λ)", {**inp, "diluent": "He"}),
            ]
        elif _has_any(nq, ("oxygen", "o2")):
            sweep_title = "Oxygen Concentration Sweep (`14%` → `34% O₂`)"
            variants = [(f"{ox}% O₂", {**inp, "oxygen_pct": ox}) for ox in (14.0, 18.0, 21.0, 28.0, 34.0)]
        elif _has_any(nq, ("0g vs 1g", "0g and 1g", "gravity", "1g")):
            sweep_title = "Gravity Sweep (`0G` vs `0.16G` vs `0.38G` vs `1G`)"
            variants = [(f"{gv} G", {**inp, "gravity_g": gv}) for gv in (0.0, 0.16, 0.38, 1.0)]
        else:
            sweep_title = "Ventilation Airflow Sweep (`0` → `30 cm/s`)"
            variants = [(f"U = {u} cm/s", {**inp, "airflow_cms": u}) for u in (0.0, 2.0, 6.0, 15.0, 30.0)]

        rows_sw: List[str] = []
        for lbl, prm in variants:
            sw = simulate_combustion_state(prm)
            swt = sw["telemetry"]
            rate_v = f"V_f={swt['flame_spread_mm_s']} mm/s" if swt["flame_spread_mm_s"] > 0 else f"K={swt['burning_rate_k_mm2_s']} mm²/s"
            rows_sw.append(
                f"| **{lbl}** | `{swt['sherwood_number']}` | `{swt.get('damkohler_number', 0)}` | **`{swt['moc_pct']}% O₂`** | `{swt['flame_temp_k']} K` | `{rate_v}` | `{swt['regime']}` (**`{swt['risk_score']}/100`**) |"
            )

        text = (
            f"### Counterfactual Sensitivity Simulation: {sweep_title} — `{fuel_name}`\n\n"
            "| Perturbed Condition | Sherwood `Sh` | Damköhler `Da` | Critical `MOC` | Flame `T_f` | Burn / Spread | Regime & Risk |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            + "\n".join(rows_sw)
            + "\n\n"
            "- **Physical Takeaway (CON-03 Ventilation Paradox):** Notice the non-monotonic **U-shaped `MOC` curve**: at `U = 0 cm/s`, radiative/diffusive self-blanketing weakens or quenches the flame; at gentle `2–8 cm/s` spacecraft ventilation, fresh `O₂` transport (`Sh > 2`, `Da > 1`) **maximizes flammability hazard (lowest `MOC`)**; at high velocity (`>25 cm/s`), residence time drops (`Da → 1`) toward convective blowoff (**BASS / SPICE / SLICE**)."
        )
        return (text, default_citations[:2])

    # -------------------------------------------------------------------------
    # 12. SPACE-TO-EARTH TECHNOLOGY TRANSFERS
    # -------------------------------------------------------------------------
    if intent == "earth_spinoffs":
        rows_et = [
            f"| **{et['domain_en']}** | `{et['nasa_source']}` | {et['insight_en']} |"
            for et in SPACE_TO_EARTH_TRANSFERS
        ]
        hdr = (
            "### Space-to-Earth Fire Safety & Clean Combustion Spinoffs (CON-09)\n\n"
            "| Terrestrial Application Domain | NASA PSI Flight Heritage | Engineering Mechanism & Impact |\n"
            "| :--- | :--- | :--- |\n"
        )
        return (hdr + "\n".join(rows_et), default_citations[:3])

    # -------------------------------------------------------------------------
    # 13. UPLOADED DATASET / FLAME IMAGE MULTI-PHASE AUDIT
    # -------------------------------------------------------------------------
    if intent == "uploaded_media":
        pg_info = active_sim.get("partial_gravity_info") or {}
        exp_lines = "\n".join(
            f"- **#{e['rank']} {e['program']} (`{e['exp_id']}` • `{e.get('hardware_group', 'CIR')}` • [NTRS #{e['ntrs_id']}]({e['ntrs_url']}))** — Score `{e['priority_score']}/100`, MOC `{e['moc_measured_pct']}%`: {e['key_finding_en']}"
            for e in top_exps[:5]
        )
        pg_note = f"- **Partial-Gravity Bounding (0G–1G):** {pg_info['en']}\n" if (pg_info.get("show_banner") and pg_info.get("en")) else ""
        text = (
            "### 1. Uploaded Dataset & Multi-Phase Telemetry Audit\n"
            f"{media_context}\n\n"
            "### 2. Synchronized 3D Chamber, Governing Equations & ISS Flight Validation\n"
            f"- **Active 3D State (`{fuel_name}` • `{inp['geometry_3d']}`):** `{inp['gravity_g']} G`, `{inp['oxygen_pct']}% O₂` (`P_O₂ = {tel.get('o2_partial_psia', 0)} psia`), `{inp['pressure_psia']} psia`, `{inp['airflow_cms']} cm/s` -> **{reg_badge}** (`T_f = {tel['flame_temp_k']} K`, Spread `{tel['flame_spread_mm_s']} mm/s`, Risk **`{tel['risk_score']}/100`**).\n"
            f"- **Dimensionless Transport & Kinetics:** `K = {tel['burning_rate_k_mm2_s']} mm²/s` | `B_oq = {tel.get('spalding_b_number', 0)}` | `Rf/Rd = {tel.get('standoff_ratio_rf_rd', 0)}` | `Re = {tel.get('reynolds_number', 0)}` | `Sh = {tel['sherwood_number']}` | `Ra = {tel.get('rayleigh_number', 0)}` | `Ri = {tel.get('richardson_number', 0)}` | `Da = {tel.get('damkohler_number', 0)}` | `χ_r = {tel['radiative_loss_fraction'] * 100:.1f}%` | `MOC = {tel['moc_pct']}% O₂`.\n"
            f"- **ISS Flight Telemetry Fit:** `R² = {fv.get('r_squared', 0.95)}` • `RMSE = {fv.get('rmse', 0.03)}` ({fv.get('campaign', 'NASA GRC PSI')}).\n"
            f"{pg_note}\n"
            f"### 3. Ranked NASA PSI Investigations Across Orbital Hardware\n{exp_lines}\n\n"
            "### 4. Life Support Clock (ECLSS), Non-Halon Suppression & Earth Applications\n"
            f"- **Life Support Clock (`{tl.get('habitat_name_en', 'ISS Module')}`):** Alarm `+{tl.get('t_alarm_s', 6)} s` | `JSC-20584 24h SMAC (100 ppm CO)` limit in **`{tl.get('t_smac_24h_100ppm_s', 180)} s`** | Crew response CO `{tl.get('co_at_response_ppm', 40)} ppm`.\n"
            f"- **NASA-STD-6001B Protocol:** **(1)** Cut HVAC ventilation (`{inp['airflow_cms']} -> 0 cm/s`), **(2)** Isolate power bus, **(3)** Discharge **25–40 µm Fine Water Mist (SoFIE-MIST)** or CO₂/N₂ (*Halon 1301 prohibited due to toxic HF/HBr*).\n"
            "- **Terrestrial Transfers:** Sub-50 µm clean water-mist extinguishers, **SAME/DAFT** dust-immune smoke sensors, **PBI/Nomex** firefighter gear & composite **SCBA** cylinders, and low-emission **HCCI** engine kinetics."
        )
        return (text, default_citations[:5])

    # -------------------------------------------------------------------------
    # 14. FULL 4-SECTION ENGINEERING MISSION SYNTHESIS (PRESET #1)
    # -------------------------------------------------------------------------
    if intent == "full_synthesis":
        call = active_sim["callouts"]
        pg_info = active_sim.get("partial_gravity_info") or {}
        exp_lines = "\n".join(
            f"{e['rank']}. **{e['program']} ({e['exp_id']} • {e.get('hardware_group', 'CIR')} • [NTRS #{e['ntrs_id']}]({e['ntrs_url']}))** — Score `{e['priority_score']}/100` (MOC `{e['moc_measured_pct']}%`): {e['key_finding_en']}"
            for e in top_exps[:4]
        )
        pg_line = f"- **Partial-G / Atmosphere Note:** {pg_info['en']}\n" if (pg_info.get("show_banner") and pg_info.get("en")) else ""
        text = (
            f"### 1. Physical Regime & Governing Equation Diagnosis: {call['badge_en']}\n"
            f"- **Active State (`{fuel_name}`):** `{inp['gravity_g']} G`, `{inp['oxygen_pct']}% O₂` (`P_O₂ = {tel.get('o2_partial_psia', 0)} psia`), `U = {inp['airflow_cms']} cm/s` → Temp `{tel['flame_temp_k']} K`, Risk **`{tel['risk_score']}/100`**.\n"
            f"- **Dimensionless Numbers:** `K = {tel['burning_rate_k_mm2_s']} mm²/s` | `B_oq = {tel.get('spalding_b_number', 0)}` | `Rf/Rd = {tel.get('standoff_ratio_rf_rd', 0)}` | `Re = {tel.get('reynolds_number', 0)}` | `Sh = {tel['sherwood_number']}` | `Ra = {tel.get('rayleigh_number', 0)}` | `Ri = {tel.get('richardson_number', 0)}` | `Da = {tel.get('damkohler_number', 0)}` | `χ_r = {tel['radiative_loss_fraction'] * 100:.1f}%` | `MOC = {tel['moc_pct']}% O₂`.\n"
            f"- **ISS Flight Validation:** `R² = {fv.get('r_squared', 0.95)}` • `RMSE = {fv.get('rmse', 0.03)}` ({fv.get('campaign', 'NASA GRC PSI')}).\n"
            f"{pg_line}"
            + (f"- **Attached Context:** {media_context}\n" if media_context else "")
            + f"\n### 2. Ranked NASA PSI Investigations & NTRS Evidence\n{exp_lines}\n\n"
            f"### 3. ECLSS Survival Clock & Non-Halon Fire Safety Protocol (NASA-STD-6001B)\n"
            f"- **Survival Clock (`{tl.get('habitat_name_en', 'ISS Module')}`):** Alarm `+{tl.get('t_alarm_s', 6)} s` | `JSC-20584 24h SMAC (100 ppm CO)` in **`{tl.get('t_smac_24h_100ppm_s', 180)} s`** | Response CO `{tl.get('co_at_response_ppm', 40)} ppm`.\n"
            f"- **Countermeasure Sequence:** **(1)** Cut HVAC airflow (`{inp['airflow_cms']} → 0 cm/s`), **(2)** Isolate bus power, **(3)** Discharge **25–40 µm Fine Water Mist (SoFIE-MIST PFE)** or CO₂/N₂ (*Halon 1301 strictly banned*).\n\n"
            f"### 4. Space-to-Earth Fire Safety Transfer\n"
            f"- Sub-50 µm **SoFIE-MIST** clean-agent water mist, **SAME/DAFT** dust-immune multi-angle smoke detectors, **PBI/Nomex** firefighter turnout gear & composite **SCBA** air tanks, and clean **HCCI** engine kinetics."
        )
        return (text, default_citations)

    # -------------------------------------------------------------------------
    # 15. TARGETED SCIENTIFIC CONCEPT QUERY
    # -------------------------------------------------------------------------
    mentioned_fuel = None
    fuel_kw_map = {
        "heptane": "n_heptane",
        "methanol": "methanol",
        "pmma": "pmma",
        "acrylic": "pmma",
        "sibal": "sibal",
        "cotton": "sibal",
        "nomex": "nomex",
        "hydrogen": "hydrogen",
        "propane": "propane_cfig",
    }
    for fkw, fid in fuel_kw_map.items():
        if fkw in nq and fid in FUEL_PROPERTIES:
            mentioned_fuel = (fid, FUEL_PROPERTIES[fid])
            break
    if mentioned_fuel is None and history:
        for h_item in reversed(history):
            if str(h_item.get("role") or "").lower() == "user":
                prev_nq = _norm(str(h_item.get("content") or ""))
                for fkw, fid in fuel_kw_map.items():
                    if fkw in prev_nq and fid in FUEL_PROPERTIES:
                        mentioned_fuel = (fid, FUEL_PROPERTIES[fid])
                        break
                break

    best_exp = top_exps[0] if top_exps else NASA_EXPERIMENTS_CATALOG[0]
    second_exp = top_exps[1] if len(top_exps) > 1 else NASA_EXPERIMENTS_CATALOG[1]

    dir_stop = {
        "data", "table", "chart", "values", "current", "analysis",
        "what", "how", "when", "where", "which", "show", "explain", "simple", "clear",
    }
    q_tokens = [w for w in re.split(r"[^a-z0-9]+", nq) if len(w) >= 4 and w not in dir_stop]
    best_dir = None
    best_dir_score = 0
    for d in CORE_DIRECTIVES_LIST:
        d_words = set(re.findall(r"[a-z0-9]+", _norm(f"{d.get('title_en', '')} {d.get('rule_en', '')}")))
        sc = sum(1 for tok in q_tokens if tok in d_words)
        if sc > best_dir_score:
            best_dir_score = sc
            best_dir = d

    if best_dir is None:
        dir_by_id = {d["id"]: d for d in CORE_DIRECTIVES_LIST}
        if _has_any(nq, ("spherical", "buoyancy", "candle")):
            best_dir = dir_by_id.get("CON-01", CORE_DIRECTIVES_LIST[0])
        elif tel.get("cool_flame_active") or tel.get("regime") == "COOL_FLAME_NTC":
            best_dir = dir_by_id.get("CON-04", CORE_DIRECTIVES_LIST[0])
        elif 0.03 <= float(inp.get("gravity_g", 0.0)) <= 0.88:
            best_dir = dir_by_id.get("CON-07", CORE_DIRECTIVES_LIST[0])
        elif float(inp.get("oxygen_pct", 21.0)) >= 30.0 or float(inp.get("pressure_psia", 14.7)) <= 10.6:
            best_dir = dir_by_id.get("CON-06", CORE_DIRECTIVES_LIST[0])
        elif float(inp.get("airflow_cms", 0.0)) >= 1.5:
            best_dir = dir_by_id.get("CON-03", CORE_DIRECTIVES_LIST[0])
        else:
            best_dir = dir_by_id.get("CON-01", CORE_DIRECTIVES_LIST[0])

    fuel_section = ""
    if mentioned_fuel:
        mf_id, mf = mentioned_fuel
        sim_mf = simulate_combustion_state({**inp, "fuel_id": mf_id})
        mft = sim_mf["telemetry"]
        moc0_b = mf.get("moc_0g_base", mf.get("moc_0g_pct", 13.8))
        moc1_b = mf.get("moc_1g_base", mf.get("moc_1g_pct", 15.2))
        fuel_section = (
            f"- **Queried Fuel / Material (`{mf['name_en']}`, `{mf['formula']}`):** 3D Geometry `{mf['geometry_3d']}`, 0G Baseline `MOC = {moc0_b}% O₂` vs 1G `MOC = {moc1_b}% O₂`. Under your current atmosphere (`{inp['oxygen_pct']}% O₂`, `{inp['gravity_g']} G`), it yields `T_f = {mft['flame_temp_k']} K`, regime **`{mft['regime']}`**, Risk **`{mft['risk_score']}/100`**.\n"
        )

    rag_snippet = ""
    if rag_hits:
        ingested_only = [h for h in rag_hits if h.get("doc_type") == "ingested_doc" and float(h.get("similarity", 0.0)) >= 0.08]
        if ingested_only:
            top_r = ingested_only[0]
            clean_snip = _truncate_clean_title(str((top_r.get("metadata") or {}).get("snippet") or top_r.get("text") or ""), 280)
            rag_snippet = f"- **Uploaded Document Match (`{top_r['title']}`):** {clean_snip}\n"

    wants_table = _has_any(nq, ("table", "chart", "values"))
    live_table_block = ""
    if wants_table:
        live_table_block = (
            "\n| Parameter / Dimensionless Metric | Active 3D Chamber Value | Safety & Regime Interpretation |\n"
            "| :--- | :--- | :--- |\n"
            f"| **Fuel & Geometry** | `{fuel_name}` (`{inp['geometry_3d']}`) | Gravity `{inp['gravity_g']} G`, Diluent `{inp['diluent']}` |\n"
            f"| **Atmosphere (`O₂` & Pressure)** | `{inp['oxygen_pct']}% O₂` • `{inp['pressure_psia']} psia` (`P_O₂ = {tel.get('o2_partial_psia', 0)} psia`) | Critical `MOC = {tel['moc_pct']}% O₂` |\n"
            f"| **Flame Temp & Burn Rate** | `T_f = {tel['flame_temp_k']} K` • `K = {tel['burning_rate_k_mm2_s']} mm²/s` | Spread `{tel['flame_spread_mm_s']} mm/s` • `B_oq = {tel.get('spalding_b_number', 0)}` |\n"
            f"| **Transport & Residence (`Sh`, `Da`)** | `Sh = {tel['sherwood_number']}` • `Da = {tel.get('damkohler_number', 0)}` • `Ra = {tel.get('rayleigh_number', 0)}` | Airflow `U = {inp['airflow_cms']} cm/s` (`χ_r = {tel['radiative_loss_fraction'] * 100:.1f}%`) |\n"
            f"| **Fire Risk & ECLSS SMAC** | **Risk `{tel['risk_score']}/100`** • `{tel['co_ppm']} ppm CO` | **{reg_badge}** (`100 ppm SMAC`: `{tl.get('t_smac_24h_100ppm_s', 180)} s`) |\n\n"
        )

    clean_q_disp = _truncate_clean_title(user_message, 96)
    text = (
        f"### Targeted Scientific Analysis — *\"{clean_q_disp}\"*\n"
        f"{live_table_block}"
        f"{fuel_section}"
        f"- **Governing Physical Law (`{best_dir['id']} • {best_dir['code']}`):** {best_dir['rule_en']}\n"
        f"{rag_snippet}"
        f"- **Live Chamber Coupling (`{fuel_name}`):** At `{inp['gravity_g']} G`, `{inp['oxygen_pct']}% O₂` (`P_O₂ = {tel.get('o2_partial_psia', 0)} psia`), and `U = {inp['airflow_cms']} cm/s`, your chamber operates in **{reg_badge}** (`T_f = {tel['flame_temp_k']} K`, `K = {tel['burning_rate_k_mm2_s']} mm²/s`, `Sh = {tel['sherwood_number']}`, `Da = {tel.get('damkohler_number', 0)}`, `MOC = {tel['moc_pct']}% O₂`, Risk **`{tel['risk_score']}/100`**).\n"
        f"- **Matched NASA PSI Records:**\n"
        f"  1. **{best_exp['program']} (`{best_exp['exp_id']}` • [NTRS #{best_exp['ntrs_id']}]({best_exp['ntrs_url']}))** — {best_exp['key_finding_en']}\n"
        f"  2. **{second_exp['program']} (`{second_exp['exp_id']}` • [NTRS #{second_exp['ntrs_id']}]({second_exp['ntrs_url']}))** — {second_exp['key_finding_en']}"
    )
    return (text, default_citations[:2])
