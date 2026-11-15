# -*- coding: utf-8 -*-
"""
ALTAR-NASA v6.3 — Multi-Compartment Spacecraft Thermodynamics, Apollo-1 Overpressure (ΔP),
IDSS Docking Hatch Mechanical Load, SoFIE-MIST Phase-Change Cooling, and Multi-Gas FED Toxicology Engine.

Literature References:
- Quintiere, J. G. (2006). Fundamentals of Fire Phenomena (Surface Energy Balance Pyrolysis & HRR).
- NASA JSC-20584: Spacecraft Maximum Allowable Concentrations (SMACs) for Airborne Contaminants.
- ISO 13571 & Purser, D. A. (SFPE Handbook): Fractional Effective Dose (FED) for CO, HCN, HF, HCl & CO₂ Hyperventilation.
- International Docking System Standard (IDSS IDD Rev F): 800 mm Clear Bore Passageway Mechanics.
- NASA GRC SoFIE-MIST & ISS Portable Fire Extinguisher (PFE) Water-Mist Specs (NTRS #20200000361, #20160001858).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

R_UNIV_J_MOLK = 8.314462618
SIGMA_SB_W_M2K4 = 5.670374419e-8
IDSS_BORE_DIAMETER_M = 0.80  # Official NASA IDSS clear bore diameter (800 mm -> A = 0.5027 m²)
IDSS_HATCH_AREA_M2 = math.pi * ((IDSS_BORE_DIAMETER_M * 0.5) ** 2)

# Orion MPCV / Gateway 5-compartment pressurized cabin and subsystem bay topology
SPACECRAFT_COMPARTMENTS: Dict[str, Dict[str, Any]] = {
    "ORION_CM": {
        "id": "ORION_CM",
        "name_tr": "Command Deck (Cockpit)",
        "name_en": "Command Deck (Cockpit)",
        "volume_m3": 9.3,
        "wall_area_m2": 24.5,
        "camera_id": "Camera 1 • Command Deck",
        "bus_120v": "ORION-PCDU-CH1",
    },
    "HALO": {
        "id": "HALO",
        "name_tr": "Power & Avionics Bay",
        "name_en": "Power & Avionics Bay",
        "volume_m3": 19.0,
        "wall_area_m2": 42.0,
        "camera_id": "Camera 3 • Power & Avionics Bay",
        "bus_120v": "ORION-AVIONICS-BUS",
    },
    "IHAB": {
        "id": "IHAB",
        "name_tr": "Crew Living Bay",
        "name_en": "Crew Living Bay",
        "volume_m3": 36.0,
        "wall_area_m2": 68.0,
        "camera_id": "Camera 2 • Crew Living Bay",
        "bus_120v": "ORION-HAB-MAIN",
    },
    "PPE": {
        "id": "PPE",
        "name_tr": "Life Support & Air Bay",
        "name_en": "Life Support & Air Bay",
        "volume_m3": 8.5,
        "wall_area_m2": 22.0,
        "camera_id": "Camera 5 • Life Support & Air Bay",
        "bus_120v": "ORION-ECLSS-ARRAY",
    },
    "AIRLOCK": {
        "id": "AIRLOCK",
        "name_tr": "Docking & Transfer Tunnel",
        "name_en": "Docking & Transfer Tunnel",
        "volume_m3": 6.8,
        "wall_area_m2": 18.5,
        "camera_id": "Camera 4 • Docking & Transfer Tunnel",
        "bus_120v": "ORION-DOCK-TUNNEL",
    },
}

# Inter-compartment bulkhead hatches and IMV airflow ducts
SPACECRAFT_HATCH_LINKS: List[Dict[str, Any]] = [
    {
        "hatch_id": "HATCH_ORION_HALO",
        "name_tr": "Bulkhead Hatch 1 (Command Deck ↔ Power Bay)",
        "name_en": "Bulkhead Hatch 1 (Command Deck ↔ Power Bay)",
        "comp_a": "ORION_CM",
        "comp_b": "HALO",
        "imv_flow_m3_s": 0.045,
    },
    {
        "hatch_id": "HATCH_HALO_IHAB",
        "name_tr": "Bulkhead Hatch 2 (Power Bay ↔ Crew Living Bay)",
        "name_en": "Bulkhead Hatch 2 (Power Bay ↔ Crew Living Bay)",
        "comp_a": "HALO",
        "comp_b": "IHAB",
        "imv_flow_m3_s": 0.055,
    },
    {
        "hatch_id": "HATCH_HALO_PPE",
        "name_tr": "Bulkhead Hatch 3 (Power Bay ↔ Life Support Bay)",
        "name_en": "Bulkhead Hatch 3 (Power Bay ↔ Life Support Bay)",
        "comp_a": "HALO",
        "comp_b": "PPE",
        "imv_flow_m3_s": 0.030,
    },
    {
        "hatch_id": "HATCH_IHAB_AIRLOCK",
        "name_tr": "Bulkhead Hatch 4 (Crew Living Bay ↔ Docking Tunnel)",
        "name_en": "Bulkhead Hatch 4 (Crew Living Bay ↔ Docking Tunnel)",
        "comp_a": "IHAB",
        "comp_b": "AIRLOCK",
        "imv_flow_m3_s": 0.028,
    },
]

# Fuel-specific toxic combustion product yields (kg gas / kg fuel burned — SFPE / NASA-STD-6001B)
TOXIC_YIELD_DB: Dict[str, Dict[str, float]] = {
    "n_heptane": {"y_co": 0.018, "y_hcn": 0.0000, "y_hf": 0.0000, "y_hcl": 0.0000, "y_co2": 2.85},
    "methanol": {"y_co": 0.004, "y_hcn": 0.0000, "y_hf": 0.0000, "y_hcl": 0.0000, "y_co2": 1.36},
    "pmma": {"y_co": 0.022, "y_hcn": 0.0000, "y_hf": 0.0000, "y_hcl": 0.0000, "y_co2": 2.12},
    "sibal": {"y_co": 0.034, "y_hcn": 0.0004, "y_hf": 0.0000, "y_hcl": 0.0003, "y_co2": 1.55},
    "nomex": {"y_co": 0.048, "y_hcn": 0.0145, "y_hf": 0.0012, "y_hcl": 0.0025, "y_co2": 1.78},
    "hydrogen": {"y_co": 0.000, "y_hcn": 0.0000, "y_hf": 0.0000, "y_hcl": 0.0000, "y_co2": 0.00},
    "propane_cfig": {"y_co": 0.015, "y_hcn": 0.0000, "y_hf": 0.0000, "y_hcl": 0.0000, "y_co2": 2.92},
}


def compute_multicompartment_and_toxicology(
    fuel_id: str,
    fuel: Dict[str, Any],
    extinguished: bool,
    cool_flame_active: bool,
    flame_temp_k: float,
    heat_flux_kw_m2: float,
    k_burn: float,
    flame_spread_mms: float,
    oxygen_pct: float,
    pressure_psia: float,
    airflow_cms: float,
    crew_response_s: float = 30.0,
    fire_compartment_id: str = "HALO",
    sealed_hatches: Optional[List[str]] = None,
    imv_fan_cutoff: bool = False,
    water_mist_active: bool = False,
    mist_flow_g_s: float = 18.0,
) -> Dict[str, Any]:
    """
    Solve across the multi-compartment spacecraft network (Orion + Gateway):
    1) Pyrolysis mass flux m''_p and Heat Release Rate Q_HRR (kW) via Quintiere surface energy balance,
    2) SoFIE-MIST fine water mist latent + sensible cooling capacity Q_mist (kW),
    3) Sealed-compartment isochoric pressure rise ΔP (kPa / psia) and IDSS hatch locking load F_hatch (kN),
    4) Inter-compartment smoke/mass transport m_dot_ij (g/s),
    5) Multi-gas (CO + HCN + HF + HCl + CO₂) NASA JSC-20584 / ISO 13571 Fractional Effective Dose (FED).
    """
    comp_id = fire_compartment_id if fire_compartment_id in SPACECRAFT_COMPARTMENTS else "HALO"
    sealed_set = set(sealed_hatches or [])
    comp = SPACECRAFT_COMPARTMENTS[comp_id]
    vol_m3 = float(comp["volume_m3"])

    p0_pa = pressure_psia * 6894.757
    t0_k = 295.15
    gamma = 1.40
    n_tot_mol = (p0_pa * vol_m3) / (R_UNIV_J_MOLK * t0_k)
    rho_gas = (p0_pa * 0.0288) / (R_UNIV_J_MOLK * t0_k)

    # 1. Quintiere Surface Pyrolysis Mass Flux (m''_p, g/m²·s) and Cabin Fire Heat Release Rate (HRR, kW)
    if extinguished:
        pyrolysis_flux_g_m2s = 0.0
        q_hrr_kw = 0.0
    else:
        t_surf_k = float(fuel.get("t_boil_k", 600.0))
        lv_j_kg = max(250000.0, float(fuel.get("lv_kj_kg", 1200.0)) * 1000.0)
        rerad_w_m2 = 0.90 * SIGMA_SB_W_M2K4 * max(0.0, (t_surf_k ** 4) - (t0_k ** 4))
        net_q_surf_w_m2 = max(650.0, heat_flux_kw_m2 * 1000.0 - rerad_w_m2)
        m_flux_kg_m2s = net_q_surf_w_m2 / lv_j_kg
        pyrolysis_flux_g_m2s = round(m_flux_kg_m2s * 1000.0, 2)

        # Reference cabin avionics/panel burn area (Saffire / NASA-STD-3001 scale: ~0.045 m² active surface)
        active_area_m2 = 0.018 if cool_flame_active else (0.048 + 0.012 * min(3.0, flame_spread_mms))
        comb_eff = 0.28 if cool_flame_active else min(0.92, 0.68 + 0.22 * (oxygen_pct / 100.0))
        q_hrr_kw = (active_area_m2 * m_flux_kg_m2s * comb_eff * float(fuel["dhc_kj_kg"]))
        q_hrr_kw = round(max(0.18 if cool_flame_active else 0.65, min(28.0, q_hrr_kw)), 2)

    # 2. SoFIE-MIST Fine Water Mist (25–40 µm) Phase-Change Cooling Capacity (NTRS #20200000361)
    # Q_mist = eta_evap * m_dot_w * [c_pw * (373.15 - T0) + L_vw]  (c_pw=4.184 kJ/kgK, L_vw=2257 kJ/kg)
    eta_evap = 0.86  # Evaporation efficiency of 30 µm fine water mist droplets inside the flame envelope
    q_mist_capacity_kw = round(
        eta_evap * (mist_flow_g_s / 1000.0) * (4.184 * (373.15 - t0_k) + 2257.0),
        2,
    )
    q_mist_applied_kw = q_mist_capacity_kw if water_mist_active else 0.0

    # 3. Isochoric Overpressure Rise ΔP (Apollo-1 Effect) and Bulk Cabin Gas Heating
    dt_eval_s = min(180.0, max(5.0, crew_response_s))
    f_wall_loss = 0.58  # Conductive heat loss fraction into aluminum-lithium cabin hull
    q_net_gas_kw = max(0.0, (1.0 - f_wall_loss) * q_hrr_kw - 0.85 * q_mist_applied_kw)

    # Thornton's rule upper bound (13.1 MJ / kg O2 consumed)
    max_o2_energy_kj = (n_tot_mol * (oxygen_pct / 100.0) * 0.032) * 13100.0
    delta_q_kj = min(max_o2_energy_kj * 0.42, q_net_gas_kw * dt_eval_s)

    # ΔP = ((γ - 1) / V_eff) * ΔQ  (Open hatches vent pressure into adjacent bays; sealed hatches confine ΔP)
    connected_open_vol = vol_m3
    for lk in SPACECRAFT_HATCH_LINKS:
        if lk["hatch_id"] not in sealed_set:
            if lk["comp_a"] == comp_id:
                connected_open_vol += float(SPACECRAFT_COMPARTMENTS[lk["comp_b"]]["volume_m3"])
            elif lk["comp_b"] == comp_id:
                connected_open_vol += float(SPACECRAFT_COMPARTMENTS[lk["comp_a"]]["volume_m3"])

    overpressure_kpa = round(((gamma - 1.0) * (delta_q_kj * 1000.0) / max(1.0, connected_open_vol)) / 1000.0, 2)
    overpressure_psia = round(overpressure_kpa / 6.894757, 3)

    # 4. IDSS Hatch Mechanical Load (F_hatch = ΔP * A_IDSS) and Inter-Compartment Smoke Mass Flow (m_dot_ij)
    hatch_states: List[Dict[str, Any]] = []
    total_smoke_leak_g_s = 0.0
    max_hatch_force_kn = 0.0

    for lk in SPACECRAFT_HATCH_LINKS:
        hid = lk["hatch_id"]
        is_sealed = hid in sealed_set
        involves_fire = (lk["comp_a"] == comp_id or lk["comp_b"] == comp_id)
        dp_pa = (overpressure_kpa * 1000.0) if (involves_fire and is_sealed) else (overpressure_kpa * 180.0 if involves_fire else 0.0)
        force_kn = round((dp_pa * IDSS_HATCH_AREA_M2) / 1000.0, 2)
        max_hatch_force_kn = max(max_hatch_force_kn, force_kn)

        if is_sealed or extinguished:
            smoke_flow_g_s = 0.0
        elif involves_fire:
            imv_q = 0.0 if imv_fan_cutoff else float(lk["imv_flow_m3_s"]) * (airflow_cms / 8.0 + 0.35)
            orifice_vel = math.sqrt(2.0 * max(0.0, dp_pa) / max(0.2, rho_gas))
            orifice_q = 0.62 * 0.06 * orifice_vel  # Effective thermal smoke-layer orifice cross-section
            smoke_flow_g_s = round(rho_gas * (imv_q + orifice_q) * 1000.0, 2)
        else:
            smoke_flow_g_s = 0.0

        total_smoke_leak_g_s += smoke_flow_g_s
        hatch_states.append({
            "hatch_id": hid,
            "name_tr": lk["name_tr"],
            "name_en": lk["name_en"],
            "comp_a": lk["comp_a"],
            "comp_b": lk["comp_b"],
            "sealed": is_sealed,
            "pressure_load_kn": force_kn,
            "smoke_mass_flow_g_s": smoke_flow_g_s,
        })

    # 5. Multi-Gas (CO + HCN + HF + HCl + CO₂) NASA JSC-20584 & ISO 13571 FED Toxicology Integral
    tox = TOXIC_YIELD_DB.get(fuel_id, TOXIC_YIELD_DB["n_heptane"])
    if extinguished or q_hrr_kw <= 0.0:
        co_cabin_ppm = 1.0
        hcn_cabin_ppm = 0.0
        hf_cabin_ppm = 0.0
        hcl_cabin_ppm = 0.0
        co2_cabin_pct = 0.38
        fed_total = 0.001
        t_fed_incap_min = 999.0
    else:
        burn_mass_kg = (q_hrr_kw * dt_eval_s) / max(5000.0, float(fuel["dhc_kj_kg"]))
        # Incomplete combustion / cool-flame CO yield multiplier
        co_incomplete_mult = 3.8 if cool_flame_active else (1.6 if oxygen_pct < 16.0 else 1.0)
        mist_scrub_factor = 0.35 if water_mist_active else 1.0  # Fine water mist scrubs water-soluble HF/HCl acid gases

        mol_co = (burn_mass_kg * tox["y_co"] * co_incomplete_mult) / 0.02801
        mol_hcn = (burn_mass_kg * tox["y_hcn"]) / 0.02703
        mol_hf = (burn_mass_kg * tox["y_hf"] * mist_scrub_factor) / 0.02001
        mol_hcl = (burn_mass_kg * tox["y_hcl"] * mist_scrub_factor) / 0.03646
        mol_co2 = (burn_mass_kg * tox["y_co2"]) / 0.04401

        eff_tox_mol = (p0_pa * connected_open_vol) / (R_UNIV_J_MOLK * t0_k)
        co_cabin_ppm = round(min(12000.0, 1.0 + (mol_co / eff_tox_mol) * 1e6), 1)
        hcn_cabin_ppm = round(min(1500.0, (mol_hcn / eff_tox_mol) * 1e6), 2)
        hf_cabin_ppm = round(min(800.0, (mol_hf / eff_tox_mol) * 1e6), 2)
        hcl_cabin_ppm = round(min(800.0, (mol_hcl / eff_tox_mol) * 1e6), 2)
        co2_cabin_pct = round(min(15.0, 0.38 + (mol_co2 / eff_tox_mol) * 100.0), 2)

        # ISO 13571 / Purser FED (dt_min exposure duration with CO2 hyperventilation factor ψ_CO2 = exp(CO2% / 5))
        dt_min = dt_eval_s / 60.0
        v_co2_hyper = math.exp(co2_cabin_pct / 5.0)
        # Incapacitation dose denominators: CO 35000 ppm·min, HCN exp(5.396 - 0.023*ppm), HF 500 ppm, HCl 1000 ppm
        fed_co = (co_cabin_ppm * dt_min / 35000.0) * v_co2_hyper
        fed_hcn = ((math.exp(hcn_cabin_ppm / 43.0) - 1.0) * dt_min / 12.0) * v_co2_hyper if hcn_cabin_ppm > 0.1 else 0.0
        fed_acid = (hf_cabin_ppm / 500.0 + hcl_cabin_ppm / 1000.0) * dt_min
        fed_total = round(min(9.99, max(0.001, fed_co + fed_hcn + fed_acid)), 4)
        fed_rate_per_min = fed_total / max(0.05, dt_min)
        t_fed_incap_min = round(min(999.0, 1.0 / max(1e-5, fed_rate_per_min)), 1)

    # Per-compartment instantaneous telemetry snapshot for the 5-bay 3D digital twin
    compartments_state: Dict[str, Dict[str, Any]] = {}
    for cid, cmeta in SPACECRAFT_COMPARTMENTS.items():
        if cid == comp_id and not extinguished:
            c_status = "SUPPRESSING" if water_mist_active else ("COOL_FLAME" if cool_flame_active else "FIRE_ACTIVE")
            c_temp_c = round(22.0 + min(320.0, (delta_q_kj * 1000.0) / max(500.0, float(cmeta["volume_m3"]) * 1200.0)), 1)
            c_co = co_cabin_ppm
            c_dp = overpressure_kpa
        else:
            # Adjacent compartment: smoke ingresses if connecting hatch is unsealed, otherwise remains isolated
            leaking_in = any(
                (not h["sealed"]) and h["smoke_mass_flow_g_s"] > 0.0 and (h["comp_a"] == cid or h["comp_b"] == cid)
                for h in hatch_states
            )
            c_status = "SMOKE_INGRESS" if leaking_in else "NOMINAL_ISOLATED"
            c_temp_c = 23.8 if leaking_in else 21.5
            c_co = round(co_cabin_ppm * 0.28, 1) if leaking_in else 0.8
            c_dp = round(overpressure_kpa * 0.35, 2) if leaking_in else 0.0

        compartments_state[cid] = {
            "id": cid,
            "name_tr": cmeta["name_tr"],
            "name_en": cmeta["name_en"],
            "volume_m3": cmeta["volume_m3"],
            "camera_id": cmeta["camera_id"],
            "bus_120v": cmeta["bus_120v"],
            "status": c_status,
            "temp_c": c_temp_c,
            "co_ppm": c_co,
            "overpressure_kpa": c_dp,
        }

    return {
        "fire_compartment_id": comp_id,
        "fire_compartment_name_tr": comp["name_tr"],
        "fire_compartment_name_en": comp["name_en"],
        "pyrolysis_mass_flux_g_m2s": pyrolysis_flux_g_m2s,
        "hrr_kw": q_hrr_kw,
        "water_mist_active": water_mist_active,
        "water_mist_cooling_capacity_kw": q_mist_capacity_kw,
        "net_gas_heating_kw": round(q_net_gas_kw, 2),
        "overpressure_kpa": overpressure_kpa,
        "overpressure_psia": overpressure_psia,
        "idss_hatch_area_m2": round(IDSS_HATCH_AREA_M2, 4),
        "max_hatch_force_kn": max_hatch_force_kn,
        "total_intermodule_smoke_g_s": round(total_smoke_leak_g_s, 2),
        "multi_gas_toxicology": {
            "co_ppm": co_cabin_ppm,
            "hcn_ppm": hcn_cabin_ppm,
            "hf_ppm": hf_cabin_ppm,
            "hcl_ppm": hcl_cabin_ppm,
            "co2_pct": co2_cabin_pct,
            "fed_total": fed_total,
            "time_to_incapacitation_min": t_fed_incap_min,
        },
        "hatches": hatch_states,
        "compartments": compartments_state,
    }
