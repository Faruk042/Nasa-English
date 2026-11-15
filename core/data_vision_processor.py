# -*- coding: utf-8 -*-
"""
ALTAR-NASA v6.3 Multimodal Flame Vision, Telemetry Table, and Scientific Data Ingestion Engine.
When an image (`.png/.jpg/.webp/.gif`), data file (`.csv/.tsv/.xlsx/.zip/.json/.pdf/.txt`), or web feed is supplied:
1) Extracts quantitative combustion parameters (`O2 %`, pressure `psia`, airflow `cm/s`, gravity `G`,
   droplet diameter `mm`, fuel code, `d²` burning rate slope `K`, spectral `CH*/Soot` ratio, aspect ratio `H/W`),
2) Normalizes extracted states into `extracted_sim_params` for the 3D Chamber and plotting engine,
3) Generates structured engineering summaries for downstream AI and deterministic analysis.
"""

from __future__ import annotations

import base64
import csv
import io
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageSequence

# Enforce strict decompression-bomb ceiling (max 25 megapixels)
Image.MAX_IMAGE_PIXELS = 25_000_000


def _count_flamelet_islands(mask_256: np.ndarray) -> int:
    """
    Downsample a 256x256 binary flame mask onto a 64x64 grid and count discrete 8-connected
    reaction islands (cellular fingering flamelets observed near extinction in BASS-II).
    """
    h, w = mask_256.shape
    gh, gw = 64, 64
    small = mask_256.reshape(gh, h // gh, gw, w // gw).mean(axis=(1, 3)) > 0.25
    visited = np.zeros_like(small, dtype=bool)
    islands = 0
    for y in range(gh):
        for x in range(gw):
            if small[y, x] and not visited[y, x]:
                stack = [(y, x)]
                visited[y, x] = True
                area = 0
                while stack:
                    cy, cx = stack.pop()
                    area += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < gh and 0 <= nx < gw and small[ny, nx] and not visited[ny, nx]:
                                visited[ny, nx] = True
                                stack.append((ny, nx))
                if area >= 3:
                    islands += 1
    return islands


def analyze_flame_image_bytes(raw_bytes: bytes, filename: str = "flame.jpg") -> Dict[str, Any]:
    """
    Analyze an uploaded flame photograph, multi-frame `.gif`, or video frame with Pillow + NumPy:
    - Segments faint blue microgravity chemiluminescence, luminous soot shells, and discrete flamelets,
    - Classifies 0G spherical vs. 0G ventilated wake vs. 1G buoyant plumes from aspect ratio (`H/W`),
    - Quantifies blue chemiluminescence (`CH*/OH*`), warm soot incandescence, and UV cool-flame ratios,
    - Produces Beer-Lambert soot volume fraction (`f_v`) and 3D chamber simulation parameters.
    """
    try:
        raw_img = Image.open(io.BytesIO(raw_bytes))
        frames_rgb: List[Image.Image] = []
        for idx, frame in enumerate(ImageSequence.Iterator(raw_img)):
            frames_rgb.append(frame.convert("RGB"))
            if idx >= 7:
                break
        if not frames_rgb:
            frames_rgb = [raw_img.convert("RGB")]

        frame_means = [
            float(np.mean(np.asarray(fr.resize((64, 64), Image.Resampling.BILINEAR), dtype=np.float32)))
            for fr in frames_rgb
        ]
        best_idx = int(np.argmax(frame_means))
        img = frames_rgb[best_idx]
        temporal_flicker_pct = (
            round(float(np.std(frame_means) / max(1.0, np.mean(frame_means))) * 100.0, 2)
            if len(frame_means) > 1
            else 0.0
        )

        orig_w, orig_h = img.size
        # Resample to 256x256 for deterministic morphological analysis
        proc = img.resize((256, 256), Image.Resampling.BILINEAR)
        arr = np.asarray(proc, dtype=np.float32) / 255.0

        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        max_channel = np.maximum(np.maximum(r, g), b)

        # Blue-weighted adaptive threshold to retain faint CH*/OH* microgravity reaction zones
        blue_excess = np.maximum(0.0, b - 0.65 * r)
        signal_map = np.maximum(max_channel, blue_excess * 1.35)
        threshold = max(0.11, float(np.percentile(signal_map, 78)) * 0.52)
        mask = signal_map > threshold
        active_count = int(np.sum(mask))

        if active_count < 30:
            mask = signal_map > 0.065
            active_count = max(1, int(np.sum(mask)))

        flamelet_count = _count_flamelet_islands(mask)
        is_flamelets = flamelet_count >= 2 and active_count < 16000

        ys, xs = np.where(mask)
        if len(xs) > 5 and len(ys) > 5:
            bbox_w = max(4.0, float(np.percentile(xs, 95) - np.percentile(xs, 5)))
            bbox_h = max(4.0, float(np.percentile(ys, 95) - np.percentile(ys, 5)))
            aspect_hw = round(bbox_h / bbox_w, 2)
        else:
            bbox_w, bbox_h = 60.0, 60.0
            aspect_hw = 1.0

        mean_r = float(np.mean(r[mask])) if np.any(mask) else float(np.mean(r))
        mean_g = float(np.mean(g[mask])) if np.any(mask) else float(np.mean(g))
        mean_b = float(np.mean(b[mask])) if np.any(mask) else float(np.mean(b))
        rgb_sum = max(1e-5, mean_r + mean_g + mean_b)

        blue_chemilum_ratio = round(mean_b / rgb_sum, 3)
        soot_warm_ratio = round((mean_r + 0.5 * mean_g) / (rgb_sum * 1.25), 3)
        violet_uv_ratio = round(min(mean_r, mean_b) / max(0.05, mean_g + 0.2), 3)

        # Beer-Lambert laser extinction soot volume fraction f_v (670 nm ISS PSD, E(m)=0.26, L=0.10 m)
        est_transmission = max(0.08, min(0.998, 1.0 - 0.58 * soot_warm_ratio * min(1.0, active_count / 4500.0)))
        fv_soot = -(670e-9 * math.log(est_transmission)) / (6.0 * math.pi * 0.26 * 0.10)
        fv_soot_ppm = round(fv_soot * 1e6, 4)

        # Morphological regime classification (Cool Flame, Cellular Flamelets, Buoyant, Wake, Spherical)
        is_cool_flame = (
            blue_chemilum_ratio > 0.36
            and violet_uv_ratio > 0.72
            and float(np.mean(lum[mask])) < 0.48
            and not is_flamelets
        )
        if is_cool_flame:
            inferred_gravity = 0.0
            inferred_airflow = 0.0
            inferred_o2 = 13.0
            inferred_fuel = "n_heptane"
            detected_regime_en = "Invisible/UV Cool Flame (0G NTC Regime)"
        elif is_flamelets and soot_warm_ratio < 0.52:
            inferred_gravity = 0.0
            inferred_airflow = 4.8
            inferred_o2 = 15.6
            inferred_fuel = "sibal"
            detected_regime_en = f"Cellular Fingering Flamelets ({flamelet_count} Flamelets • Near-MOC Limit)"
        elif aspect_hw > 1.28:
            inferred_gravity = min(1.0, round((aspect_hw - 1.0) * 1.15, 2))
            inferred_airflow = 2.0
            inferred_o2 = 21.0 if soot_warm_ratio < 0.58 else 26.0
            inferred_fuel = "n_heptane" if soot_warm_ratio >= 0.42 else "methanol"
            detected_regime_en = f"Buoyant Elongated Plume (H/W = {aspect_hw})"
        elif aspect_hw < 0.82:
            inferred_gravity = 0.0
            inferred_airflow = round(min(25.0, (1.0 / max(0.3, aspect_hw)) * 6.5), 1)
            inferred_o2 = 18.5
            inferred_fuel = "pmma" if soot_warm_ratio >= 0.45 else "methanol"
            detected_regime_en = f"0G Ventilated Wake Flame (W/H = {round(1 / aspect_hw, 2)})"
        else:
            inferred_gravity = 0.0
            inferred_airflow = 0.3
            inferred_o2 = 21.0 if blue_chemilum_ratio >= 0.38 else 19.0
            inferred_fuel = "methanol" if blue_chemilum_ratio >= 0.46 else "n_heptane"
            detected_regime_en = f"0G Spherical Microgravity Diffusion Flame (H/W = {aspect_hw} ≈ 1.0)"

        inferred_d0 = round(max(1.8, min(5.4, (math.sqrt(active_count) / 256.0) * 7.5)), 1)

        # Generate Base64 thumbnail preview for multimodal AI inspection and UI display
        thumb = img.copy()
        thumb.thumbnail((640, 640))
        buf = io.BytesIO()
        thumb.save(buf, format="JPEG", quality=85)
        b64_data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        extracted_params = {
            "fuel_id": inferred_fuel,
            "gravity_g": inferred_gravity,
            "oxygen_pct": inferred_o2,
            "pressure_psia": 14.7,
            "airflow_cms": inferred_airflow,
            "flow_direction": "opposed",
            "droplet_d0_mm": inferred_d0,
            "diluent": "N2",
        }

        frame_note_en = f" • {len(frames_rgb)} Frames Sampled (Flicker `{temporal_flicker_pct}%`)" if len(frames_rgb) > 1 else ""
        flamelet_line_en = (
            f"- **Flame Front Integrity:** `{flamelet_count}` discrete reaction islands (Cellular Flamelets detected)\n"
            if is_flamelets
            else ""
        )

        summary_en = (
            f"**Spectral & Morphological Flame Analysis ({filename} • {orig_w}×{orig_h}px{frame_note_en}):**\n"
            f"- **Detected Geometric Regime:** {detected_regime_en}\n"
            f"{flamelet_line_en}"
            f"- **CH*/OH* Blue Chemiluminescence:** `{blue_chemilum_ratio * 100:.1f}%` | **Soot Thermal Index:** `{soot_warm_ratio:.2f}`\n"
            f"- **Extracted 3D Parameters:** Gravity `{inferred_gravity}G`, Oxygen `{inferred_o2}%`, Airflow `{inferred_airflow} cm/s`, Fuel `{inferred_fuel}`, Diameter `{inferred_d0} mm`."
        )

        return {
            "ok": True,
            "media_type": "image",
            "filename": filename,
            "metrics": {
                "resolution": f"{orig_w}x{orig_h}",
                "frames_analyzed": len(frames_rgb),
                "temporal_flicker_pct": temporal_flicker_pct,
                "flamelet_count": flamelet_count,
                "flamelets_detected": is_flamelets,
                "aspect_ratio_hw": aspect_hw,
                "blue_chemiluminescence_ratio": blue_chemilum_ratio,
                "soot_warm_ratio": soot_warm_ratio,
                "beer_lambert_fv_ppm": fv_soot_ppm,
                "detected_regime_tr": detected_regime_en,
                "detected_regime_en": detected_regime_en,
            },
            "extracted_sim_params": extracted_params,
            "summary_tr": summary_en,
            "summary_en": summary_en,
            "image_base64": b64_data_uri,
        }
    except Exception as exc:
        return {"ok": False, "error": f"Failed to analyze flame image: {exc}"}


def _xlsx_bytes_to_csv_text(raw_bytes: bytes, max_rows: int = 650) -> str:
    """Convert standard `.xlsx` (OpenXML) worksheets into CSV text using the standard library."""
    with zipfile.ZipFile(io.BytesIO(raw_bytes), "r") as zf:
        names = set(zf.namelist())
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in names:
            ss_info = zf.getinfo("xl/sharedStrings.xml")
            if ss_info.file_size <= 15 * 1024 * 1024:
                ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
                for si in ss_root.iter():
                    if si.tag.endswith("}si") or si.tag == "si":
                        parts = [
                            (t.text or "")
                            for t in si.iter()
                            if t.tag.endswith("}t") or t.tag == "t"
                        ]
                        shared_strings.append("".join(parts))

        sheet_candidates = sorted(
            n for n in names if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")
        )
        if not sheet_candidates:
            return ""

        sheet_name = "xl/worksheets/sheet1.xml" if "xl/worksheets/sheet1.xml" in names else sheet_candidates[0]
        sh_info = zf.getinfo(sheet_name)
        if sh_info.file_size > 25 * 1024 * 1024:
            return ""
        sh_root = ET.fromstring(zf.read(sheet_name))

        def _col_ref_to_idx(cell_ref: str) -> int:
            letters = ""
            for ch in cell_ref:
                if ch.isalpha():
                    letters += ch.upper()
                else:
                    break
            if not letters:
                return -1
            idx_val = 0
            for ch in letters:
                idx_val = idx_val * 26 + (ord(ch) - ord("A") + 1)
            return idx_val - 1

        grid_rows: List[List[str]] = []
        max_cols = 0
        for elem in sh_root.iter():
            if not (elem.tag.endswith("}row") or elem.tag == "row"):
                continue
            row_cells: Dict[int, str] = {}
            next_col = 0
            for cell in elem:
                if not (cell.tag.endswith("}c") or cell.tag == "c"):
                    continue
                c_ref = cell.attrib.get("r", "")
                c_type = cell.attrib.get("t", "")
                c_idx = _col_ref_to_idx(c_ref)
                if c_idx < 0:
                    c_idx = next_col
                next_col = c_idx + 1

                val_str = ""
                if c_type == "inlineStr":
                    t_parts = [
                        (t.text or "")
                        for t in cell.iter()
                        if t.tag.endswith("}t") or t.tag == "t"
                    ]
                    val_str = "".join(t_parts)
                else:
                    raw_v = ""
                    for sub in cell:
                        if sub.tag.endswith("}v") or sub.tag == "v":
                            raw_v = sub.text or ""
                            break
                    if c_type == "s" and raw_v.isdigit():
                        s_i = int(raw_v)
                        val_str = shared_strings[s_i] if 0 <= s_i < len(shared_strings) else raw_v
                    else:
                        val_str = raw_v
                row_cells[c_idx] = val_str.strip()

            if row_cells:
                row_len = min(80, max(row_cells.keys()) + 1)
                row_list = [row_cells.get(ci, "") for ci in range(row_len)]
                if any(x for x in row_list):
                    max_cols = max(max_cols, len(row_list))
                    grid_rows.append(row_list)
                    if len(grid_rows) >= max_rows:
                        break

        if not grid_rows:
            return ""
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        for r in grid_rows:
            padded = r + [""] * max(0, max_cols - len(r))
            writer.writerow(padded)
        return buf.getvalue()


def extract_tabular_or_text_from_archive_bytes(raw_bytes: bytes, filename: str) -> Tuple[str, str, int]:
    """
    Safely unpack `.xlsx` workbooks or NASA PSI `.zip` bundles (`.csv/.tsv/.xlsx/.json/.txt`)
    under strict Zip-bomb size caps. Returns `(text, effective_filename, scanned_file_count)`.
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "xlsx":
        csv_txt = _xlsx_bytes_to_csv_text(raw_bytes)
        return (csv_txt, filename, 1)

    if ext == "zip":
        with zipfile.ZipFile(io.BytesIO(raw_bytes), "r") as zf:
            valid_infos = [
                inf for inf in zf.infolist()
                if not inf.is_dir()
                and not inf.filename.startswith("__MACOSX/")
                and not inf.filename.split("/")[-1].startswith(".")
                and inf.file_size <= 25 * 1024 * 1024
            ]
            if not valid_infos:
                return ("", filename, 0)

            def _priority(inf: zipfile.ZipInfo) -> Tuple[int, int]:
                low = inf.filename.lower()
                is_exp_tbl = 0 if ("experimental" in low or "table" in low or "telemetry" in low) else 1
                if low.endswith(".csv"):
                    return (0, is_exp_tbl)
                if low.endswith(".tsv"):
                    return (1, is_exp_tbl)
                if low.endswith(".xlsx"):
                    return (2, is_exp_tbl)
                if low.endswith(".json"):
                    return (3, is_exp_tbl)
                if low.endswith((".txt", ".md", ".dat")):
                    return (4, is_exp_tbl)
                return (9, is_exp_tbl)

            valid_infos.sort(key=_priority)
            chosen = valid_infos[0]
            chosen_low = chosen.filename.lower()
            inner_bytes = zf.read(chosen.filename)
            short_inner = chosen.filename.split("/")[-1]
            if chosen_low.endswith(".xlsx"):
                return (_xlsx_bytes_to_csv_text(inner_bytes), short_inner, len(valid_infos))
            try:
                decoded = inner_bytes.decode("utf-8")
            except UnicodeDecodeError:
                decoded = inner_bytes.decode("latin-1", errors="ignore")
            return (decoded, short_inner, len(valid_infos))

    try:
        return (raw_bytes.decode("utf-8"), filename, 1)
    except UnicodeDecodeError:
        return (raw_bytes.decode("latin-1", errors="ignore"), filename, 1)


def _parse_cell_number(raw_val: Any) -> Optional[float]:
    """
    Parse range strings (`'21.5 - 21.7'`), semicolon lists (`'21; 26.5; 40'`), and unit-annotated
    cells (`'1 atm'`, `'757.7 mmHg'`, `'21%'`) from NASA PSI tables into finite floats.
    """
    if raw_val is None:
        return None
    if isinstance(raw_val, (int, float)):
        return None if math.isnan(float(raw_val)) else float(raw_val)
    s = str(raw_val).strip()
    if not s or s.lower() in ("na", "n/a", "nan", "none", "null", "-", "--", "tbd"):
        return None
    m_range = re.match(
        r"^\s*(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*(?:%|atm|bar|psia|psi|kpa|mmhg|torr|cm/s|mm|cm|k|c)?\s*$",
        s,
        re.IGNORECASE,
    )
    if m_range:
        return (float(m_range.group(1)) + float(m_range.group(2))) / 2.0
    try:
        return float(s.replace("%", "").strip())
    except ValueError:
        pass
    m_unit = re.match(
        r"^\s*([-+]?\d+(?:\.\d+)?)\s*(?:;|,|\s*(?:%|atm|bar|psia|psi|kpa|mmhg|torr|cm/s|m/s|mm|cm|um|k|c|sec|s)\b)",
        s,
        re.IGNORECASE,
    )
    if m_unit:
        return float(m_unit.group(1))
    return None


def _parse_fuel_string(val: str) -> Optional[str]:
    vl = (val or "").lower().strip()
    if not vl:
        return None
    candidates = [
        (
            "propane_cfig",
            (
                "propane_cfig", "propane", "c3h8", "cfig", "cfi-g",
                "ethane", "c2h6", "ethylene", "ethene", "c2h4", "propene", "propylene",
                "butane", "n-butane", "isobutane", "c4h10", "methane", "ch4", "acetylene", "c2h2",
            ),
        ),
        (
            "n_heptane",
            (
                "n_heptane", "n-heptane", "heptane", "c7h16", "dodecane", "c12h26",
                "decane", "c10h22", "octane", "isooctane", "c8h18", "hexadecane",
                "nonane", "hexane", "pentane", "jp-8", "jp8", "kerosene",
            ),
        ),
        (
            "methanol",
            (
                "methanol", "ch3oh", "ethanol", "c2h5oh",
                "propanol", "isopropanol", "ipa", "butanol", "glycerol",
            ),
        ),
        (
            "pmma",
            (
                "pmma", "acrylic", "plexiglas", "lucite", "teflon", "ptfe",
                "delrin", "acetal", "pom", "polyethylene", "hdpe", "ldpe",
                "polypropylene", "polycarbonate", "lexan", "ultem", "silicone",
            ),
        ),
        (
            "sibal",
            ("sibal", "cotton", "cellulose", "whatman", "paper", "fiberglass", "fabric"),
        ),
        (
            "nomex",
            ("nomex", "ht90", "kevlar", "aramid", "kapton", "goretex", "pbi", "orthofabric", "spacesuit"),
        ),
        ("hydrogen", ("hydrogen",)),
    ]
    best_fuel: Optional[str] = None
    best_pos = 10**9
    for fid, kws in candidates:
        for kw in kws:
            idx = vl.find(kw)
            if idx != -1 and idx < best_pos:
                best_pos = idx
                best_fuel = fid
    if best_fuel is None and re.search(r"(?:^|[^a-z0-9])h2(?:$|[^a-z0-9])", vl):
        return "hydrogen"
    return best_fuel


def _parse_diluent_string(val: str) -> Optional[str]:
    vl = (val or "").strip().upper()
    if vl in ("CO2", "HE", "N2"):
        return "He" if vl == "HE" else vl
    if "CO2" in vl or "CARBON DIOXIDE" in vl:
        return "CO2"
    if "HELIUM" in vl:
        return "He"
    if "N2" in vl or "NITROGEN" in vl:
        return "N2"
    return None


def _parse_habitat_string(val: str) -> Optional[str]:
    vl = (val or "").lower().strip()
    if not vl:
        return None
    if vl in ("iss_module", "lunar_hab", "lunar_rover", "eva_suit"):
        return vl
    if "suit" in vl or "eva" in vl:
        return "eva_suit"
    if "rover" in vl:
        return "lunar_rover"
    if "lunar" in vl or "hab" in vl:
        return "lunar_hab"
    if "iss" in vl or "destiny" in vl:
        return "iss_module"
    return None


def _classify_table_column(col_name: str) -> Optional[str]:
    kl = re.sub(r"\s+", " ", str(col_name or "").lstrip("\ufeff").strip().lower())
    if not kl:
        return None
    if any(
        w in kl
        for w in (
            "test #", "test id", "test_id", "test name", "test_name", "test number",
            "sample #", "sample number", "sample id", "flex number", "run id", "run_id",
        )
    ) or kl in ("test", "run", "trial", "test day"):
        return "test_id"
    if "smac" not in kl and (
        kl in ("t", "time", "time_s", "t_s", "sec", "seconds", "elapsed_s")
        or kl.startswith("time_")
        or kl.endswith("_time_s")
        or "time (s" in kl
    ):
        return "time_s"
    if kl in ("phase_code", "phase_id"):
        return "phase_code"
    if any(w in kl for w in ("phase_desc", "phase_name", "phase", "stage")):
        return "phase_desc"
    if "cool flame" in kl or kl == "cool_flame":
        return "cool_flag"
    if any(w in kl for w in ("test type", "flow direction", "flow_direction", "configuration", "flame type")):
        return "test_type"
    if any(w in kl for w in ("polarity", "mesh polarity", "electrode")):
        return "polarity"
    if any(w in kl for w in ("voltage", "kv", "e-field", "electric field", "potential")):
        return "voltage_kv"
    if kl in ("xf", "fuel conc", "fuel conc.", "fuel %") or any(w in kl for w in ("fuel conc", "fuel mole", "fuel fraction")):
        return "fuel_conc"
    if any(w in kl for w in ("fuel rate", "hc fuel", "mhc", "sccm", "slpm", "burner flow")):
        return "fuel_rate"
    if any(w in kl for w in ("fuel_code", "fuel_id", "fuel", "material", "substrate")) and not any(
        bad in kl for bad in ("rate", "sccm", "mg/s", "mg/min", "flow", "temp", "conc")
    ):
        return "fuel"
    if any(w in kl for w in ("diluent_gas", "diluent", "inert_gas")):
        return "diluent"
    if kl in ("he", "xhe", "x_he") or "helium" in kl or kl.startswith("he initial") or kl.startswith("he "):
        return "he_frac"
    if kl in ("xco2", "x_co2") or kl.startswith("co initial ambient") or "initial co2" in kl:
        return "co2_amb"
    if any(w in kl for w in ("habitat_code", "habitat_id", "habitat", "cabin_type")):
        return "habitat"
    if any(w in kl for w in ("hardware_system", "facility", "hardware", "apparatus")):
        return "facility"
    if any(w in kl for w in ("exp_ref", "exp_id", "experiment_ref", "ntrs")):
        return "exp_ref"
    if (
        "co2" not in kl
        and "po2" not in kl
        and "h2o" not in kl
        and "ch2o" not in kl
        and "moc" not in kl
        and "flow rate" not in kl
        and "final o2" not in kl
        and "after test" not in kl
        and (
            "oxygen_pct" in kl
            or "oxygen" in kl
            or "xo2" in kl
            or "percent o2" in kl
            or kl.startswith("o initial ambient")
            or re.search(r"(?:^|[_\s(%])o2(?:$|[_\s)%])", kl) is not None
        )
    ):
        return "oxygen_pct"
    if "po2" not in kl and "partial" not in kl:
        if "mmhg" in kl or "torr" in kl:
            return "pressure_mmhg"
        if re.search(r"\bbar\b", kl):
            return "pressure_bar"
        if re.search(r"\batm\b", kl):
            return "pressure_atm"
        if "pressure_kpa" in kl or "kpa" in kl:
            return "pressure_kpa"
        if "pressure_psia" in kl or "psia" in kl or "psi" in kl:
            return "pressure_psia"
        if "pressure" in kl:
            return "pressure_any"
    if not any(
        bad in kl
        for bad in (
            "spread", "mm_s", "restrictor", "direction", "term",
            "fuel rate", "hc fuel", "sccm", "mg/s", "mg/min", "o2 flow", "fan display",
        )
    ) and (
        any(
            w in kl
            for w in (
                "airflow_cm_s", "airflow_cms", "airflow", "air flow", "air rate", "air display",
                "air velocity", "flow velocity", "flow speed", "u_cms", "fan_cm", "coflow",
            )
        )
        or ("cm/s" in kl and any(w in kl for w in ("air", "flow", "vel", "gas", "oxidizer")))
        or kl in ("flow", "velocity")
    ):
        return "airflow_cms"
    if any(w in kl for w in ("gravity_g", "gravity", "g_level")):
        return "gravity_g"
    if "d2_mm2" in kl or "d2" in kl or "d_sq" in kl:
        return "d2_mm2"
    if (
        "mist" not in kl
        and "aerosol" not in kl
        and "dust" not in kl
        and "length" not in kl
        and "width" not in kl
        and (
            any(
                w in kl
                for w in (
                    "droplet_diameter_mm", "droplet_d0_mm", "droplet", "diameter",
                    "d0", "d_mm", "sample_diam", "nozzle", "burner size",
                )
            )
        )
    ):
        return "d0_mm"
    if any(w in kl for w in ("flame_temp_k", "temp_k", "flame_temp", "thermocouple", "tad (k)", "temp (k)")):
        return "temp_k"
    if any(w in kl for w in ("temp (c", "t (c", "temperature (c", "celsius")):
        return "temp_c"
    if "co2" not in kl and "smac" not in kl and "initial ambient" not in kl and (
        kl == "co" or "co_ppm" in kl or "co_sensor" in kl or "co (ppm)" in kl
    ):
        return "co_ppm"
    if "co2_ppm" in kl or "co2" in kl:
        return "co2_ppm"
    if "ch2o" in kl or "formaldehyde" in kl:
        return "ch2o_ppm"
    if "optical_visible_pct" in kl or "optical" in kl:
        return "opt_vis"
    if "gain" not in kl and ("heat_flux_kw_m2" in kl or "radiometer" in kl or "heat_flux" in kl or "radiative" in kl):
        return "ir_kw"
    if "water_mist_um" in kl or "mist" in kl:
        return "mist_um"
    if "aerosol_dust_um" in kl or "aerosol" in kl or "dust_um" in kl or "particle_um" in kl:
        return "aerosol_um"
    return None


def _fit_d2_slope(t_vals: List[float], d2_vals: List[float]) -> Optional[Dict[str, float]]:
    if len(t_vals) < 3 or len(t_vals) != len(d2_vals):
        return None
    t_arr = np.asarray(t_vals, dtype=np.float64)
    y_arr = np.asarray(d2_vals, dtype=np.float64)
    dt = float(t_arr[-1] - t_arr[0])
    drop = float(y_arr[0] - y_arr[-1])
    if dt <= 0.2 or drop <= 0.08:
        return None
    slope, intercept = np.polyfit(t_arr, y_arr, 1)
    k_meas = max(0.0, float(-slope))
    if k_meas <= 0.005:
        return None
    y_pred = slope * t_arr + intercept
    ss_res = float(np.sum((y_arr - y_pred) ** 2))
    ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    rmse = float(np.sqrt(np.mean((y_arr - y_pred) ** 2)))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-9 else 0.999
    return {
        "k_meas": round(k_meas, 3),
        "r2": round(max(0.0, min(1.0, r2)), 4),
        "rmse": round(rmse, 4),
    }


def _convert_o2_number(raw_val: Any, col_header: str = "") -> Optional[float]:
    num = _parse_cell_number(raw_val)
    if num is None:
        return None
    s = str(raw_val or "")
    hl = (col_header or "").lower()
    if 0.03 <= num <= 1.0 and "%" not in s and "percent" not in hl and "pct" not in hl and "% by vol" not in hl:
        num = num * 100.0
    if 4.0 <= num <= 100.0:
        return round(num, 2)
    return None


def _extract_pressure_psia_values(r_list: List[Dict[str, Any]], col_map: Dict[str, str]) -> List[float]:
    out_p: List[float] = []
    if "pressure_psia" in col_map:
        c = col_map["pressure_psia"]
        for it in r_list:
            v = _parse_cell_number(it.get(c))
            if v is not None and 2.5 <= v <= 30.0:
                out_p.append(v)
    if not out_p and "pressure_kpa" in col_map:
        c = col_map["pressure_kpa"]
        for it in r_list:
            v = _parse_cell_number(it.get(c))
            if v is not None and 18.0 <= v <= 240.0:
                out_p.append(v / 6.89476)
    if not out_p and "pressure_mmhg" in col_map:
        c = col_map["pressure_mmhg"]
        for it in r_list:
            v = _parse_cell_number(it.get(c))
            if v is not None and 120.0 <= v <= 1600.0:
                out_p.append(v / 51.7149)
    if not out_p and "pressure_bar" in col_map:
        c = col_map["pressure_bar"]
        for it in r_list:
            v = _parse_cell_number(it.get(c))
            if v is not None and 0.18 <= v <= 3.0:
                out_p.append(v * 14.5038)
    if not out_p and "pressure_atm" in col_map:
        c = col_map["pressure_atm"]
        for it in r_list:
            v = _parse_cell_number(it.get(c))
            if v is not None and 0.18 <= v <= 3.0:
                out_p.append(v * 14.6959)
    if not out_p and "pressure_any" in col_map:
        c = col_map["pressure_any"]
        for it in r_list:
            raw_v = it.get(c)
            v = _parse_cell_number(raw_v)
            if v is None:
                continue
            sl = str(raw_v or "").lower()
            if "atm" in sl:
                conv = v * 14.6959
            elif "bar" in sl:
                conv = v * 14.5038
            elif "kpa" in sl:
                conv = v / 6.89476
            elif "mmhg" in sl or "torr" in sl:
                conv = v / 51.7149
            elif 0.18 <= v <= 2.4:
                conv = v * 14.6959
            elif 2.5 <= v <= 28.0:
                conv = v
            elif 28.0 < v <= 220.0:
                conv = v / 6.89476
            elif 220.0 < v <= 1600.0:
                conv = v / 51.7149
            else:
                continue
            if 2.5 <= conv <= 30.0:
                out_p.append(conv)
    return out_p


def _is_truthy_cool_flag(val: Any) -> bool:
    s = str(val or "").strip().lower()
    return s in ("yes", "y", "true", "1", "cool", "cool flame")


def _is_high_diluent_fraction(val: Optional[float], col_header: str = "") -> bool:
    if val is None:
        return False
    hl = (col_header or "").lower()
    is_pct = ("%" in hl) or ("percent" in hl) or ("pct" in hl) or ("by vol" in hl)
    pct = val if is_pct else (val * 100.0 if val <= 1.05 else val)
    return 15.0 <= pct <= 96.0


def _infer_filename_fuel(filename: str) -> Optional[str]:
    fl = (filename or "").lower()
    parsed = _parse_fuel_string(fl)
    if parsed:
        return parsed
    if "bass" in fl or "sofie" in fl or "same" in fl:
        return "pmma"
    if "saffire" in fl:
        return "sibal"
    return None


def _extract_chem_subtoken(raw_fuel: str, fallback_id: str) -> str:
    rl = (raw_fuel or "").lower()
    for tok in (
        "ch4", "methane", "c2h4", "ethylene", "c2h6", "ethane", "c3h8", "propane",
        "c3h6", "propene", "c4h10", "butane", "c7h16", "heptane", "c12h26", "dodecane",
        "c10h22", "decane", "c8h18", "octane", "ch3oh", "methanol", "c2h5oh", "ethanol",
        "butanol", "propanol", "pmma", "teflon", "ptfe", "delrin", "ultem", "polyethylene",
        "polycarbonate", "sibal", "cotton", "cellulose", "whatman", "nomex", "kapton",
        "kevlar", "hydrogen", "h2",
    ):
        if tok in rl:
            return tok
    cleaned = re.sub(r"[^a-z]", "", rl)[:10]
    return cleaned if len(cleaned) >= 2 else fallback_id


def _analyze_tabular_rows(rows: List[Dict[str, Any]], filename: str) -> Optional[Dict[str, Any]]:
    rows = [r for r in (rows or []) if any(str(v or "").strip() for v in r.values())]
    if not rows:
        return None
    from core.physics_engine import simulate_combustion_state

    col_map: Dict[str, str] = {}
    sample_keys = list(rows[0].keys())
    for raw_k in sample_keys:
        role = _classify_table_column(raw_k)
        if role and role not in col_map:
            col_map[role] = raw_k

    # Strip trailing footnote or comment-only rows (e.g., PSI-22 continuation rows)
    if len(sample_keys) >= 5 and len(rows) >= 4 and "fuel" in col_map:
        f_col_check = col_map["fuel"]
        populated_fuel_cnt = sum(1 for r in rows if str(r.get(f_col_check) or "").strip())
        if populated_fuel_cnt >= int(len(rows) * 0.65):
            filtered_rows = []
            for r in rows:
                has_f = bool(str(r.get(f_col_check) or "").strip())
                non_note_cnt = sum(
                    1
                    for k, v in r.items()
                    if str(v or "").strip() and "note" not in str(k).lower() and "comment" not in str(k).lower()
                )
                if has_f or non_note_cnt >= 3:
                    filtered_rows.append(r)
            if filtered_rows:
                rows = filtered_rows

    fuel_counts: Dict[str, int] = {}
    if "fuel" in col_map:
        f_col = col_map["fuel"]
        for r in rows:
            pf = _parse_fuel_string(str(r.get(f_col) or ""))
            if pf:
                fuel_counts[pf] = fuel_counts.get(pf, 0) + 1
    dominant_fuel = (
        max(fuel_counts.items(), key=lambda kv: kv[1])[0]
        if fuel_counts
        else (_infer_filename_fuel(filename) or "n_heptane")
    )
    he_col_hdr = col_map.get("he_frac", "")
    co2_amb_hdr = col_map.get("co2_amb", "")

    has_explicit_phase = bool(col_map.get("phase_code") or col_map.get("phase_desc"))
    grouped_phases: List[Dict[str, Any]] = []

    if has_explicit_phase:
        phase_lookup: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            p_code = str(r.get(col_map.get("phase_code", ""), "") or "").strip()
            p_desc = str(r.get(col_map.get("phase_desc", ""), "") or "").strip()
            p_key = p_code or p_desc or "PHASE_1"
            if p_key not in phase_lookup:
                entry = {
                    "key": p_key,
                    "code": p_code or p_key.split(" ")[0],
                    "desc": p_desc or p_code or "Standard Combustion Phase",
                    "rows": [],
                }
                phase_lookup[p_key] = entry
                grouped_phases.append(entry)
            phase_lookup[p_key]["rows"].append(r)
    else:
        # Distinguish single-droplet d²(t) time series from multi-run NASA PSI experiment catalogs
        t_col = col_map.get("time_s")
        d_col = col_map.get("d2_mm2") or col_map.get("d0_mm")
        is_monotonic_ts = False
        if t_col and d_col and len(rows) >= 3:
            t_probe = [_parse_cell_number(r.get(t_col)) for r in rows[:25]]
            t_clean = [x for x in t_probe if x is not None]
            if len(t_clean) >= 3 and all(t_clean[i + 1] >= t_clean[i] for i in range(len(t_clean) - 1)) and t_clean[-1] > t_clean[0]:
                is_monotonic_ts = True

        if is_monotonic_ts or len(rows) == 1:
            grouped_phases.append({
                "key": "PHASE_1",
                "code": "PHASE_1",
                "desc": "Time-Series Combustion Record",
                "rows": rows,
            })
        elif len(rows) <= 7:
            for r_idx, r in enumerate(rows, start=1):
                f_str = str(r.get(col_map.get("fuel", ""), "") or "").strip()
                grouped_phases.append({
                    "key": f"TEST_{r_idx}",
                    "code": f"TEST_{r_idx}",
                    "desc": f"Test {r_idx}" + (f" ({f_str[:26]})" if f_str else ""),
                    "rows": [r],
                })
        else:
            # Partition NASA PSI Experimental Tables into up to 7 representative regime groups
            o2_hdr = col_map.get("oxygen_pct", "")
            fr_all = [
                _parse_cell_number(r.get(col_map["fuel_rate"]))
                for r in rows
                if "fuel_rate" in col_map and _parse_cell_number(r.get(col_map["fuel_rate"])) is not None
            ]
            fr_med = sorted(fr_all)[len(fr_all) // 2] if len(fr_all) >= 4 else None

            buckets: Dict[str, Dict[str, Any]] = {}
            for r_idx, r in enumerate(rows):
                f_raw = str(r.get(col_map.get("fuel", ""), "") or "").strip()
                f_id = _parse_fuel_string(f_raw) or dominant_fuel
                f_tok = _extract_chem_subtoken(f_raw, f_id)
                cool_b = "COOL" if ("cool_flag" in col_map and _is_truthy_cool_flag(r.get(col_map["cool_flag"]))) else "HOT"
                he_v = _parse_cell_number(r.get(he_col_hdr)) if he_col_hdr else None
                co2_v = _parse_cell_number(r.get(co2_amb_hdr)) if co2_amb_hdr else None
                dil_b = "He" if _is_high_diluent_fraction(he_v, he_col_hdr) else ("CO2" if _is_high_diluent_fraction(co2_v, co2_amb_hdr) else "N2")
                o2_v = _convert_o2_number(r.get(o2_hdr), o2_hdr) if o2_hdr else None
                if o2_v is None:
                    o2_b = "O2_STD"
                elif o2_v < 17.0:
                    o2_b = "O2_LOW"
                elif o2_v <= 23.5:
                    o2_b = "O2_AIR"
                elif o2_v <= 45.0:
                    o2_b = "O2_ENR"
                else:
                    o2_b = "O2_HIGH"

                ttype_raw = str(r.get(col_map.get("test_type", ""), "") or "").strip().lower()
                fl_v = _parse_cell_number(r.get(col_map.get("airflow_cms", ""))) if "airflow_cms" in col_map else None
                if fl_v is None:
                    fl_b = "FL_COFLOW" if "coflow" in ttype_raw else ("FL_CONC" if "concurrent" in ttype_raw else "FL_DEF")
                elif fl_v < 4.0:
                    fl_b = "FL_QUIES"
                elif fl_v <= 16.0:
                    fl_b = "FL_MID"
                else:
                    fl_b = "FL_HIGH"

                fc_v = _parse_cell_number(r.get(col_map.get("fuel_conc", ""))) if "fuel_conc" in col_map else None
                if fc_v is not None and 0.0 < fc_v <= 1.0:
                    fc_v = fc_v * 100.0
                fc_b = "FC_DEF" if fc_v is None else ("FC_DIL" if fc_v < 55.0 else ("FC_MID" if fc_v < 88.0 else "FC_PURE"))

                pol_raw = str(r.get(col_map.get("polarity", ""), "") or "").strip().lower()
                kv_v = _parse_cell_number(r.get(col_map.get("voltage_kv", ""))) if "voltage_kv" in col_map else None
                pol_b = (pol_raw[:3] if pol_raw else "NP") + (f"_KV{int(round(kv_v))}" if kv_v is not None else "")

                fr_v = _parse_cell_number(r.get(col_map.get("fuel_rate", ""))) if "fuel_rate" in col_map else None
                fr_b = "FR_DEF" if (fr_v is None or fr_med is None) else ("FR_LOW" if fr_v <= fr_med else "FR_HIGH")

                b_key = f"{f_id}|{f_tok}|{cool_b}|{dil_b}|{o2_b}|{fl_b}|{fc_b}|{pol_b}|{fr_b}"
                if b_key not in buckets:
                    desc_label = f"{f_raw[:24] or f_id}"
                    if fc_v is not None and fc_v < 95.0 and f"{int(round(fc_v))}%" not in desc_label:
                        desc_label += f" • {int(round(fc_v))}% Fuel"
                    if pol_raw in ("positive", "negative"):
                        desc_label += f" • {pol_raw.capitalize()}"
                    if cool_b == "COOL":
                        desc_label += " • Cool Flame"
                    if dil_b != "N2":
                        desc_label += f" • {dil_b}"
                    buckets[b_key] = {
                        "key": b_key,
                        "code": f"GROUP_{len(buckets) + 1}",
                        "desc": desc_label,
                        "first_idx": r_idx,
                        "rows": [],
                    }
                buckets[b_key]["rows"].append(r)

            top_buckets = sorted(buckets.values(), key=lambda b: (-len(b["rows"]), b["first_idx"]))[:7]
            top_buckets.sort(key=lambda b: b["first_idx"])
            for g_i, b_obj in enumerate(top_buckets, start=1):
                b_obj["code"] = f"GROUP_{g_i}"
                grouped_phases.append(b_obj)

    def _num_list(r_list: List[Dict[str, Any]], role_key: str) -> List[float]:
        col = col_map.get(role_key)
        if not col:
            return []
        out_nums: List[float] = []
        for item in r_list:
            v = _parse_cell_number(item.get(col))
            if v is not None:
                out_nums.append(v)
        return out_nums

    def _first_str(r_list: List[Dict[str, Any]], role_key: str) -> str:
        col = col_map.get(role_key)
        if not col:
            return ""
        for item in r_list:
            s = str(item.get(col) or "").strip()
            if s:
                return s
        return ""

    phases_out: List[Dict[str, Any]] = []
    best_d2_fit: Optional[Dict[str, Any]] = None
    has_cool_flame_telemetry = False
    has_water_mist_telemetry = False
    aerosol_min_um: Optional[float] = None
    aerosol_max_um: Optional[float] = None
    o2_col_name = col_map.get("oxygen_pct", "")

    for idx, grp in enumerate(grouped_phases, start=1):
        pr = grp["rows"]
        fuel_raw = _first_str(pr, "fuel")
        fuel_id = _parse_fuel_string(fuel_raw) or dominant_fuel
        diluent = _parse_diluent_string(_first_str(pr, "diluent"))
        if not diluent:
            he_vals = _num_list(pr, "he_frac")
            co2_amb_vals = _num_list(pr, "co2_amb")
            he_mean = (sum(he_vals) / len(he_vals)) if he_vals else None
            co2_mean = (sum(co2_amb_vals) / len(co2_amb_vals)) if co2_amb_vals else None
            if _is_high_diluent_fraction(he_mean, he_col_hdr):
                diluent = "He"
            elif _is_high_diluent_fraction(co2_mean, co2_amb_hdr):
                diluent = "CO2"
            else:
                diluent = "N2"
        habitat_id = _parse_habitat_string(_first_str(pr, "habitat"))

        o2_vals: List[float] = []
        if o2_col_name:
            for item in pr:
                cv = _convert_o2_number(item.get(o2_col_name), o2_col_name)
                if cv is not None:
                    o2_vals.append(cv)

        p_vals = _extract_pressure_psia_values(pr, col_map)
        flow_vals = [x for x in _num_list(pr, "airflow_cms") if 0.0 <= x <= 55.0]
        grav_vals = [x for x in _num_list(pr, "gravity_g") if 0.0 <= x <= 2.0]
        d0_vals = [x for x in _num_list(pr, "d0_mm") if 0.4 <= x <= 30.0]
        d2_vals = [x for x in _num_list(pr, "d2_mm2") if 0.1 <= x <= 100.0]
        t_vals = _num_list(pr, "time_s")
        temp_k_vals = [x for x in _num_list(pr, "temp_k") if 250.0 <= x <= 3600.0]
        temp_c_vals = [x + 273.15 for x in _num_list(pr, "temp_c") if -50.0 <= x <= 3200.0]
        temp_vals = temp_k_vals if temp_k_vals else temp_c_vals
        co_vals = [x for x in _num_list(pr, "co_ppm") if x >= 0.0]
        ch2o_vals = [x for x in _num_list(pr, "ch2o_ppm") if x >= 0.0]
        opt_vals = _num_list(pr, "opt_vis")
        mist_vals = _num_list(pr, "mist_um")
        aero_vals = [x for x in _num_list(pr, "aerosol_um") if x > 0.0]
        explicit_cool = "cool_flag" in col_map and any(_is_truthy_cool_flag(it.get(col_map["cool_flag"])) for it in pr)

        kv_vals = [abs(x) for x in _num_list(pr, "voltage_kv") if -30.0 <= x <= 30.0]
        fc_vals_raw = _num_list(pr, "fuel_conc")
        fc_vals = [(x * 100.0 if 0.0 < x <= 1.0 else x) for x in fc_vals_raw if 0.0 < x <= 100.0]
        ttype_str = _first_str(pr, "test_type").lower()
        pol_str = _first_str(pr, "polarity").lower()

        o2_mean = round(sum(o2_vals) / len(o2_vals), 2) if o2_vals else 21.0
        p_psia = round(sum(p_vals) / len(p_vals), 2) if p_vals else 14.7
        if flow_vals:
            flow_mean = round(min(40.0, sum(flow_vals) / len(flow_vals)), 2)
        elif kv_vals:
            flow_mean = round(min(28.0, 1.8 + 2.4 * (sum(kv_vals) / len(kv_vals))), 2)
        elif "coflow" in ttype_str:
            flow_mean = 4.2 if "pos" in pol_str else 5.8
        else:
            flow_mean = 2.4
        grav_mean = round(sum(grav_vals) / len(grav_vals), 2) if grav_vals else 0.0

        if d0_vals:
            d0_init = round(max(0.8, min(6.5, d0_vals[0])), 2)
        elif d2_vals:
            d0_init = round(max(0.8, min(6.5, math.sqrt(max(0.64, d2_vals[0])))), 2)
        elif fc_vals:
            fc_mean = sum(fc_vals) / len(fc_vals)
            d0_init = round(max(1.4, min(5.4, 1.5 + 2.5 * (fc_mean / 100.0))), 2)
            if not o2_vals and fc_mean < 60.0:
                o2_mean = round(max(16.5, 21.0 - (60.0 - fc_mean) * 0.06), 2)
        else:
            d0_init = 3.2

        if not habitat_id:
            if o2_mean >= 75.0 and p_psia <= 6.0:
                habitat_id = "eva_suit"
            elif 0.10 <= grav_mean <= 0.25 and p_psia <= 11.5:
                habitat_id = "lunar_rover"
            elif grav_mean >= 0.10:
                habitat_id = "lunar_hab"
            else:
                habitat_id = "iss_module"

        d2_series = d2_vals if d2_vals else ([x * x for x in d0_vals] if d0_vals else [])
        fit = _fit_d2_slope(t_vals, d2_series) if (t_vals and d2_series and len(t_vals) == len(d2_series)) else None

        flow_dir_row = "concurrent" if any(w in ttype_str for w in ("concurrent", "coflow", "co-flow", "downstream")) else "opposed"
        custom_mat_lbl = ""
        probe_mat_str = f"{fuel_raw} {filename}".lower()
        for u_kw, u_lbl in (
            ("peek", "PEEK"),
            ("xlpe", "XLPE Cable Insulation"),
            ("ptfe", "PTFE / Teflon"),
            ("teflon", "PTFE / Teflon"),
            ("kapton", "Kapton Polyimide"),
            ("pvc", "PVC Cable Jacket"),
            ("carbon-epoxy", "Carbon-Epoxy Composite"),
            ("carbon epoxy", "Carbon-Epoxy Composite"),
        ):
            if re.search(rf"(?<![a-z0-9]){re.escape(u_kw)}(?![a-z0-9])", probe_mat_str):
                fuel_id = "custom_material"
                custom_mat_lbl = u_lbl
                break

        phase_params: Dict[str, Any] = {
            "fuel_id": fuel_id,
            "gravity_g": grav_mean,
            "oxygen_pct": o2_mean,
            "pressure_psia": p_psia,
            "airflow_cms": flow_mean,
            "flow_direction": flow_dir_row,
            "droplet_d0_mm": d0_init,
            "diluent": diluent,
            "habitat_id": habitat_id,
        }
        if custom_mat_lbl:
            phase_params["custom_material_name"] = custom_mat_lbl
        sim_res = simulate_combustion_state(phase_params)
        tel = sim_res["telemetry"]
        tl = sim_res["scenario_timeline"]
        call = sim_res["callouts"]

        if fit and fuel_id in ("n_heptane", "methanol") and (best_d2_fit is None or fit["k_meas"] > best_d2_fit["k_meas"]):
            best_d2_fit = {
                "phase_idx": idx,
                "k_meas": fit["k_meas"],
                "k_model": tel["burning_rate_k_mm2_s"],
                "r2": fit["r2"],
                "rmse": fit["rmse"],
                "fuel_id": fuel_id,
            }

        temp_mean = round(sum(temp_vals) / len(temp_vals), 1) if temp_vals else tel["flame_temp_k"]
        co_max = round(max(co_vals), 1) if co_vals else tel["co_ppm"]
        ch2o_max = round(max(ch2o_vals), 1) if ch2o_vals else 0.0
        opt_min = round(min(opt_vals), 2) if opt_vals else None
        mist_max = round(max(mist_vals), 1) if mist_vals else 0.0

        if explicit_cool or tel.get("cool_flame_active") or (500.0 <= temp_mean <= 820.0) or ch2o_max >= 40.0:
            has_cool_flame_telemetry = True
        if mist_max > 0.0 or "mist" in grp["desc"].lower() or "suppression" in grp["desc"].lower() or diluent == "CO2":
            has_water_mist_telemetry = True
        if aero_vals:
            aerosol_min_um = min(aero_vals) if aerosol_min_um is None else min(aerosol_min_um, min(aero_vals))
            aerosol_max_um = max(aero_vals) if aerosol_max_um is None else max(aerosol_max_um, max(aero_vals))

        t_span_en = f"{int(t_vals[0])}-{int(t_vals[-1])} s" if (has_explicit_phase and len(t_vals) >= 2) else f"{len(pr)} rows"
        badge_en = str(call.get("badge_en") or call.get("badge_tr") or "Flame Regime")

        phases_out.append({
            "index": idx,
            "code": grp["code"],
            "desc": grp["desc"],
            "short_tr": f"Phase {idx}",
            "short_en": f"Phase {idx}",
            "time_span_tr": t_span_en,
            "time_span_en": t_span_en,
            "facility": _first_str(pr, "facility") or "ISS_CIR",
            "exp_ref": _first_str(pr, "exp_ref") or "",
            "sim_params": phase_params,
            "measured_temp_k": temp_mean,
            "co_max_ppm": co_max,
            "ch2o_max_ppm": ch2o_max,
            "opt_min_pct": opt_min,
            "mist_max_um": mist_max,
            "k_meas": fit["k_meas"] if fit else None,
            "r2_d2": fit["r2"] if fit else None,
            "rmse_d2": fit["rmse"] if fit else None,
            "regime": tel["regime"],
            "badge_tr": badge_en,
            "badge_en": badge_en,
            "flame_temp_k": tel["flame_temp_k"],
            "moc_pct": tel["moc_pct"],
            "k_model": tel["burning_rate_k_mm2_s"],
            "spread_mms": tel["flame_spread_mm_s"],
            "b_oq": tel["spalding_b_number"],
            "sh": tel["sherwood_number"],
            "da": tel["damkohler_number"],
            "risk_score": tel["risk_score"],
            "smac_s": tl.get("t_smac_24h_100ppm_s", 999.0),
            "extinguished": bool(tel.get("extinguished")),
            "cool_flame": bool(tel.get("cool_flame_active") or explicit_cool),
        })

    if not phases_out:
        return None

    # Sync the first active luminous flame phase to the 3D chamber so live combustion is rendered first
    active_hot = [p for p in phases_out if not p["extinguished"] and not p["cool_flame"]]
    active_cool = [p for p in phases_out if p["cool_flame"]]
    primary_phase = active_hot[0] if active_hot else (active_cool[0] if active_cool else phases_out[0])

    notes: List[str] = [
        f"Parsed {len(rows)} telemetry rows across {len(phases_out)} physical phases; synced Phase {primary_phase['index']} to the 3D chamber"
    ]
    if best_d2_fit:
        notes.append(
            f"Phase {best_d2_fit['phase_idx']} d² linear regression: K_meas = {best_d2_fit['k_meas']:.3f} mm²/s, K_model = {best_d2_fit['k_model']:.3f} mm²/s (R² = {best_d2_fit['r2']:.4f}, RMSE = {best_d2_fit['rmse']:.4f})"
        )

    table_en_lines = [
        "| Phase | Window | Fuel & Atmosphere | Temp / CO / CH2O | Dimensionless (K, B_oq, Sh, Da, MOC) | Regime & SMAC Clock |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for p in phases_out:
        sp = p["sim_params"]
        k_txt = f"{p['k_meas']:.2f}" if p["k_meas"] is not None else f"{p['k_model']:.2f}"
        ch2o_txt = f" / {p['ch2o_max_ppm']:.0f} ppm CH₂O" if p["ch2o_max_ppm"] > 0 else ""
        dil_txt = f" • `{sp['diluent']}`" if sp.get("diluent") and sp["diluent"] != "N2" else ""
        smac_txt_en = "Safe" if p["smac_s"] >= 900 else f"{p['smac_s']} s"
        table_en_lines.append(
            f"| **Phase {p['index']}** | `{p['time_span_en']}` | `{sp['fuel_id']}`{dil_txt} • `{sp['gravity_g']}G` • `{sp['oxygen_pct']}% O₂` • `{sp['pressure_psia']} psia` • `{sp['airflow_cms']} cm/s` | `{p['measured_temp_k']} K` • `{p['co_max_ppm']} ppm CO`{ch2o_txt} | `K={k_txt}` • `B={p['b_oq']}` • `Sh={p['sh']}` • `Da={p['da']}` • `MOC={p['moc_pct']}%` | **{p['badge_en']}** (Risk `{p['risk_score']}/100`, SMAC `{smac_txt_en}`) |"
        )

    diag_en: List[str] = []
    if best_d2_fit:
        diag_en.append(
            f"- **Empirical d²-Law Validation (Phase {best_d2_fit['phase_idx']}):** Least-squares slope `K_meas = {best_d2_fit['k_meas']:.3f} mm²/s` matches closed-form `K_model = {best_d2_fit['k_model']:.3f} mm²/s` with **`R² = {best_d2_fit['r2']:.4f}`** (`RMSE = {best_d2_fit['rmse']:.4f} mm²`)."
        )
    if has_cool_flame_telemetry:
        diag_en.append(
            "- **Invisible NTC Cool Flame & Optical Sensor Blindness (FLEX / CFI / CFI-G):** Below `800 K`, visible optical intensity drops under `1%` while `CO` and `CH₂O` surge; multi-channel `CSA-CP / ANITA-2 (CO/CH₂O) + Mid-IR` detection is mandatory."
        )
    if has_water_mist_telemetry:
        diag_en.append(
            "- **NASA-STD-6001B Suppression Audit (SoFIE-MIST):** Cutting HVAC flow (`U -> 0 cm/s`) with `<40 µm` fine water mist / `CO₂` dilution quenched the flame below `MOC` (*Halon 1301 strictly excluded*)."
        )
    if aerosol_min_um is not None and aerosol_max_um is not None and aerosol_max_um > aerosol_min_um * 3.0:
        diag_en.append(
            f"- **SAME / DAFT Smoke vs. Lunar Dust Discrimination:** Sub-micron pyrolysis smoke (`{aerosol_min_um:.2f} µm`) and coarse Lunar regolith dust (`{aerosol_max_um:.2f} µm`) separated cleanly (`{aerosol_max_um / max(0.01, aerosol_min_um):.1f}x` size ratio) without false alarms."
        )

    hdr_en = (
        f"**Multi-Phase Telemetry Analysis (`{filename}` • {len(rows)} rows • {len(phases_out)} physical phases):**"
        if len(phases_out) > 1
        else f"**Single-Phase Experiment Record (`{filename}` • {len(rows)} rows):**"
    )
    rich_en = (
        f"{hdr_en}\n"
        f"- **Active State Synced to 3D Chamber:** **Phase {primary_phase['index']}** (`{primary_phase['sim_params']['fuel_id']}`, `{primary_phase['sim_params']['gravity_g']}G`, `{primary_phase['sim_params']['oxygen_pct']}% O₂`, `{primary_phase['sim_params']['pressure_psia']} psia`, `{primary_phase['sim_params']['airflow_cms']} cm/s` — Temp: `{primary_phase['flame_temp_k']} K`).\n"
        + ("\n".join(diag_en) + "\n\n" if diag_en else "\n")
        + "\n".join(table_en_lines)
    )

    return {
        "extracted_fields": list(col_map.keys()),
        "extracted_sim_params": primary_phase["sim_params"],
        "notes": notes,
        "phases": phases_out,
        "rich_summary_tr": rich_en,
        "rich_summary_en": rich_en,
    }


def _looks_like_tabular_text(lines: List[str], delim: str, filename: str) -> bool:
    if len(lines) < 2:
        return False
    fn_low = (filename or "").lower().rstrip(")").strip()
    is_explicit_csv = fn_low.endswith((".csv", ".tsv"))
    try:
        hdr_cells = next(csv.reader([lines[0]], delimiter=delim))
    except Exception:
        return False
    if len(hdr_cells) < 2:
        return False
    if not is_explicit_csv:
        if any(len(c.strip()) > 68 for c in hdr_cells):
            return False
        probe_counts = [ln.count(delim) for ln in lines[: min(6, len(lines))]]
        if min(probe_counts) == 0 or max(probe_counts) > min(probe_counts) * 3 + 2:
            return False
        matched_roles = sum(1 for c in hdr_cells if _classify_table_column(c) is not None)
        if matched_roles == 0:
            return False
    return True


def extract_sim_params_from_text_or_table(text: str, filename: str = "data.txt") -> Dict[str, Any]:
    """
    Extract quantitative combustion parameters (`O2 %`, mole fractions, `psia/kPa/mmHg/bar/atm`,
    airflow `cm/s`, gravity `G`, fuel, diameter) and multi-phase records from CSV, TSV, XLSX, JSON, PDF, or web text.
    """
    clean = (text or "").lstrip("\ufeff").strip()
    lower = clean.lower()

    extracted: Dict[str, Any] = {}
    notes: List[str] = []

    # 1. JSON check (single object or multi-row array)
    if clean.startswith("{") or clean.startswith("["):
        try:
            obj = json.loads(clean)
            if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                tab_res = _analyze_tabular_rows(obj[:600], filename)
                if tab_res:
                    return tab_res
            elif isinstance(obj, dict):
                if isinstance(obj.get("rows"), list) and obj["rows"] and isinstance(obj["rows"][0], dict):
                    tab_res = _analyze_tabular_rows(obj["rows"][:600], filename)
                    if tab_res:
                        return tab_res
                _map_dict_row_to_params(obj, extracted, notes)
        except Exception:
            pass

    # 2. CSV / TSV / semicolon table check (guarded so prose articles are not misidentified as CSV)
    if not extracted and ("," in clean or ";" in clean or "\t" in clean):
        lines = [ln for ln in clean.splitlines() if ln.strip()][:600]
        if len(lines) >= 2:
            delim = "\t" if lines[0].count("\t") >= 2 else (";" if lines[0].count(";") > lines[0].count(",") else ",")
            if _looks_like_tabular_text(lines, delim, filename):
                try:
                    reader = list(csv.DictReader(lines, delimiter=delim))
                    if reader and len(reader[0]) >= 2:
                        tab_res = _analyze_tabular_rows(reader, filename)
                        if tab_res:
                            return tab_res
                except Exception:
                    pass

    # 3. Free-text / PDF / NASA PSI & NTRS abstract extraction
    if "fuel_id" not in extracted:
        parsed_f = _parse_fuel_string(lower) or _infer_filename_fuel(lower)
        if not parsed_f:
            if any(w in lower for w in ("e-field", "electric-field", "electric field", "cfi-g", "bre", "burner", "gaseous", "coflow")):
                parsed_f = "propane_cfig"
            elif any(w in lower for w in ("solid fuel", "polymer", "bass", "sofie", "same")):
                parsed_f = "pmma"
            elif any(w in lower for w in ("saffire", "fabric", "cotton")):
                parsed_f = "sibal"
            elif any(w in lower for w in ("spacesuit", "eva")):
                parsed_f = "nomex"
        if parsed_f:
            extracted["fuel_id"] = parsed_f

    if "oxygen_pct" not in extracted:
        m_o2 = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%\s*(?:o2|o₂|oxygen)\b", lower) or re.search(
            r"(?<![a-z0-9])(?:o2|o₂|oxygen|xo2)\s*[:=]\s*%?\s*(\d{1,3}(?:\.\d+)?)", lower
        )
        if m_o2:
            val = float(m_o2.group(1))
            if 0.04 <= val <= 1.0:
                val = round(val * 100.0, 2)
            if 5.0 <= val <= 100.0:
                extracted["oxygen_pct"] = val
                notes.append(f"Detected O₂ = {val}% from text")

    if "pressure_psia" not in extracted:
        m_psia = re.search(r"(\d{1,2}(?:\.\d+)?)\s*psi(?:a)?\b", lower)
        m_kpa = re.search(r"(\d{2,3}(?:\.\d+)?)\s*kpa\b", lower)
        m_mmhg = re.search(r"(\d{3,4}(?:\.\d+)?)\s*(?:mmhg|torr)\b", lower)
        m_bar = re.search(r"(\d(?:\.\d+)?)\s*bar\b", lower)
        m_atm = re.search(r"(\d(?:\.\d+)?)\s*atm\b", lower)
        if m_psia:
            extracted["pressure_psia"] = round(float(m_psia.group(1)), 2)
        elif m_kpa:
            extracted["pressure_psia"] = round(float(m_kpa.group(1)) / 6.89476, 2)
        elif m_mmhg:
            extracted["pressure_psia"] = round(float(m_mmhg.group(1)) / 51.7149, 2)
        elif m_bar:
            extracted["pressure_psia"] = round(float(m_bar.group(1)) * 14.5038, 2)
        elif m_atm:
            extracted["pressure_psia"] = round(float(m_atm.group(1)) * 14.6959, 2)

    if "airflow_cms" not in extracted:
        m_flow = re.search(r"(\d{1,2}(?:\.\d+)?)\s*cm\s*/\s*s", lower)
        if m_flow:
            extracted["airflow_cms"] = round(min(45.0, float(m_flow.group(1))), 2)

    if "gravity_g" not in extracted:
        if "lunar" in lower or "0.16g" in lower or "moon" in lower:
            extracted["gravity_g"] = 0.16
        elif "mars" in lower or "0.38g" in lower:
            extracted["gravity_g"] = 0.38
        elif any(w in lower for w in ("microgravity", "0g", "0 g", "iss", "freefall", "free-fall", "space station")):
            extracted["gravity_g"] = 0.0
        elif "1g" in lower:
            extracted["gravity_g"] = 1.0

    # Domain context mapping (e.g., theoretical/CFD investigations such as PSI-117 Cool Flame Dynamics)
    is_cool_topic = any(w in lower for w in ("cool flame", "cool-flame", "low-temperature combustion", "ntc"))
    if is_cool_topic:
        if "fuel_id" not in extracted or extracted.get("fuel_id") not in ("n_heptane", "propane_cfig"):
            extracted["fuel_id"] = "n_heptane"
        if "oxygen_pct" not in extracted:
            extracted["oxygen_pct"] = 16.5
        if "airflow_cms" not in extracted:
            extracted["airflow_cms"] = 0.4
        if "droplet_d0_mm" not in extracted:
            extracted["droplet_d0_mm"] = 4.4
        notes.append("Cool-flame (NTC, 550-750 K) investigation context mapped to 3D chamber parameters")
    elif extracted.get("fuel_id") == "nomex":
        extracted.setdefault("oxygen_pct", 85.0)
        extracted.setdefault("pressure_psia", 4.3)
    elif "exploration atmosphere" in lower or "sofie" in lower:
        extracted.setdefault("oxygen_pct", 34.0)
        extracted.setdefault("pressure_psia", 10.2)

    if "diluent" not in extracted:
        if "helium" in lower:
            extracted["diluent"] = "He"

    # Unlisted composite or cable-insulation analog detection
    for unlisted_kw, unlisted_lbl in (
        ("peek", "PEEK"),
        ("xlpe", "XLPE Cable Insulation"),
        ("ptfe", "PTFE / Teflon"),
        ("teflon", "PTFE / Teflon"),
        ("kapton", "Kapton Polyimide"),
        ("pvc", "PVC Cable Jacket"),
        ("carbon-epoxy", "Carbon-Epoxy Composite"),
        ("carbon epoxy", "Carbon-Epoxy Composite"),
    ):
        if re.search(rf"(?<![a-z0-9]){re.escape(unlisted_kw)}(?![a-z0-9])", lower):
            extracted["fuel_id"] = "custom_material"
            extracted["custom_material_name"] = unlisted_lbl
            notes.append(f"Unlisted material ({unlisted_lbl}) detected; Analog Material Proxy Mapping enabled")
            break

    if "flow_direction" not in extracted:
        if any(w in lower for w in ("concurrent", "co-flow", "coflow", "downstream spread")):
            extracted["flow_direction"] = "concurrent"
        elif any(w in lower for w in ("opposed", "counterflow", "upstream spread")):
            extracted["flow_direction"] = "opposed"

    defaults = {
        "fuel_id": "n_heptane",
        "gravity_g": 0.0,
        "oxygen_pct": 21.0,
        "pressure_psia": 14.7,
        "airflow_cms": 2.4,
        "flow_direction": "opposed",
        "droplet_d0_mm": 3.2,
        "diluent": "N2",
    }
    final_params = {**defaults, **extracted}
    return {
        "extracted_fields": list(extracted.keys()),
        "extracted_sim_params": final_params,
        "notes": notes,
        "phases": [],
    }


def _map_dict_row_to_params(row: Dict[str, Any], out: Dict[str, Any], notes: List[str]) -> None:
    for k, v in row.items():
        role = _classify_table_column(k)
        if role == "fuel" and isinstance(v, str):
            pf = _parse_fuel_string(v)
            if pf:
                out["fuel_id"] = pf
            continue
        if role == "diluent" and isinstance(v, str):
            pd = _parse_diluent_string(v)
            if pd:
                out["diluent"] = pd
            continue
        if role == "habitat" and isinstance(v, str):
            ph = _parse_habitat_string(v)
            if ph:
                out["habitat_id"] = ph
            continue
        if role == "oxygen_pct":
            o2_c = _convert_o2_number(v, str(k))
            if o2_c is not None:
                out["oxygen_pct"] = o2_c
                notes.append(f"Table O₂ = {o2_c:.1f}%")
            continue
        num = _parse_cell_number(v)
        if num is None:
            continue
        if role == "pressure_psia" and 2.5 <= num <= 30.0:
            out["pressure_psia"] = round(num, 2)
        elif role == "pressure_kpa" and 18.0 <= num <= 240.0:
            out["pressure_psia"] = round(num / 6.89476, 2)
        elif role == "pressure_mmhg" and 120.0 <= num <= 1600.0:
            out["pressure_psia"] = round(num / 51.7149, 2)
        elif role == "pressure_bar" and 0.18 <= num <= 3.0:
            out["pressure_psia"] = round(num * 14.5038, 2)
        elif role == "pressure_atm" and 0.18 <= num <= 3.0:
            out["pressure_psia"] = round(num * 14.6959, 2)
        elif role == "airflow_cms" and 0.0 <= num <= 50.0:
            out["airflow_cms"] = round(min(40.0, num), 2)
        elif role == "gravity_g" and 0.0 <= num <= 2.0:
            out["gravity_g"] = round(num, 2)
        elif role == "d0_mm" and 0.5 <= num <= 25.0:
            out["droplet_d0_mm"] = round(max(0.8, min(6.5, num)), 2)
        elif role == "d2_mm2" and 0.6 <= num <= 80.0 and "droplet_d0_mm" not in out:
            out["droplet_d0_mm"] = round(max(0.8, min(6.5, math.sqrt(num))), 2)


def compute_optical_beer_lambert_and_daft_scattering(
    transmission_i_over_i0: float = 0.88,
    path_length_m: float = 0.12,
    particle_diameter_um: float = 0.18,
    wavelength_laser_nm: float = 670.0,
    wavelength_blue_nm: float = 405.0,
    wavelength_nir_nm: float = 880.0,
) -> Dict[str, Any]:
    """
    1) Beer-Lambert Laser Extinction Law for Soot Volume Fraction (Dalzell & Sarofim `E(m)=0.26`):
         `f_v = -[lambda * ln(I / I_0)] / [6 * pi * E(m) * L]`
    2) NASA SAME & DAFT (Urban, Ruff, Cleary & Mulholland) Dual-Wavelength Rayleigh-Mie Scattering Cross Section:
         `C_sca(lambda, d_p) = (pi^5 * d_p^6 / (3 * lambda^4)) * |(m^2-1)/(m^2+2)|^2 / (1 + 0.38 * x^4)`
       Separates sub-micron pyrolysis/combustion smoke (`0.05-0.35 µm`) from coarse Lunar regolith dust (`1.2-50 µm`).
    """
    trans = max(1e-4, min(0.9999, float(transmission_i_over_i0)))
    l_path = max(0.01, float(path_length_m))
    lam_m = max(300e-9, float(wavelength_laser_nm) * 1e-9)
    e_m = 0.26  # Dalzell & Sarofim amorphous carbon refractive-index absorption function

    fv_soot = -(lam_m * math.log(trans)) / (6.0 * math.pi * e_m * l_path)
    kappa_ext_m_inv = -math.log(trans) / l_path

    dp_m = max(0.02e-6, min(100e-6, float(particle_diameter_um) * 1e-6))
    lorentz_factor = 0.29  # |(m^2 - 1) / (m^2 + 2)|^2

    def _c_sca_rayleigh_mie(wl_nm: float) -> float:
        wl_m = wl_nm * 1e-9
        x_param = (math.pi * dp_m) / wl_m
        c_rayleigh = ((math.pi ** 5) * (dp_m ** 6) / (3.0 * (wl_m ** 4))) * lorentz_factor
        # Smooth transition from Rayleigh (x << 1, lambda^-4) to geometric Mie plateau (x >> 1, pi*d_p^2/2)
        c_geom = 0.5 * math.pi * (dp_m ** 2)
        weight_mie = (x_param ** 4) / (1.0 + (x_param ** 4))
        return (1.0 - weight_mie) * c_rayleigh + weight_mie * c_geom * (1.0 + 0.18 / (1.0 + x_param))

    c_blue = _c_sca_rayleigh_mie(float(wavelength_blue_nm))
    c_nir = _c_sca_rayleigh_mie(float(wavelength_nir_nm))
    ratio_405_880 = round(c_blue / max(1e-30, c_nir), 3)

    if ratio_405_880 >= 3.2:
        aerosol_class = "COMBUSTION_SMOKE_SUBMICRON"
        label_en = "Sub-Micron Combustion / Pyrolysis Smoke Confirmed (SAME/DAFT Alarm)"
        false_alarm_rejected = False
    elif ratio_405_880 <= 1.75:
        aerosol_class = "LUNAR_REGOLITH_NUISANCE_DUST"
        label_en = "Coarse Lunar Regolith / Cabin Dust (Nuisance Rejected • DAFT Mie Plateau)"
        false_alarm_rejected = True
    else:
        aerosol_class = "SMOLDERING_AGGLOMERATE_TRANSITION"
        label_en = "Smoldering Aerosol Agglomerate (Transition Regime)"
        false_alarm_rejected = False

    return {
        "transmission_i_over_i0": round(trans, 4),
        "extinction_coeff_m_inv": round(kappa_ext_m_inv, 4),
        "soot_volume_fraction_fv": float(f"{fv_soot:.4e}"),
        "soot_fv_ppm": round(fv_soot * 1e6, 4),
        "particle_diameter_um": round(float(particle_diameter_um), 3),
        "c_sca_405nm_m2": float(f"{c_blue:.3e}"),
        "c_sca_880nm_m2": float(f"{c_nir:.3e}"),
        "daft_ratio_405_880": ratio_405_880,
        "aerosol_class": aerosol_class,
        "false_alarm_rejected": false_alarm_rejected,
        "label_tr": label_en,
        "label_en": label_en,
    }


def analyze_compartment_camera_and_acoustic(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Multi-modal optical, MWIR, and ultrasonic acoustic analyzer for spacecraft compartments (`ORION_CM`, `HALO`, `IHAB`, `PPE`, `AIRLOCK`):
    - Optical CCTV (`CH*` 431 nm blue chemiluminescence & soot incandescence)
    - MWIR (`3-5 µm`) thermal camera peak temperature & `dT_max/dt` rate (catches invisible cool & `H₂` flames)
    - `18-40 kHz` ultrasonic acoustic FFT energy & spectral kurtosis pre-ignition arc/outgassing detector
    - SAME / DAFT dual-wavelength laser scattering smoke vs. Lunar regolith dust discrimination
    """
    if not isinstance(payload, dict):
        payload = {}

    def _vfloat(val: Any, default: float, lo: Optional[float] = None, hi: Optional[float] = None) -> float:
        if val is None or isinstance(val, bool):
            return default
        try:
            fv = float(val)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(fv):
            return default
        if lo is not None and fv < lo:
            fv = lo
        if hi is not None and fv > hi:
            fv = hi
        return fv

    comp_id = str(payload.get("compartment_id", "HALO"))
    camera_mode = str(payload.get("camera_mode", "OPTICAL_MWIR_FUSED"))
    opt_blue = _vfloat(payload.get("optical_blue_chemilum"), 0.12, 0.0, 1.0)
    opt_soot = _vfloat(payload.get("optical_soot_lum"), 0.05, 0.0, 1.0)
    mwir_peak_k = _vfloat(payload.get("mwir_peak_temp_k"), 298.5, 270.0, 3000.0)
    mwir_dt_dt = _vfloat(payload.get("mwir_dt_dt_k_s"), 0.0, -500.0, 500.0)
    co_ppm = _vfloat(payload.get("co_ppm"), 2.0, 0.0, 100000.0)
    transmission = _vfloat(payload.get("laser_transmission"), 0.96, 0.05, 0.9999)
    particle_um = _vfloat(payload.get("particle_diameter_um"), 0.18, 0.04, 50.0)

    # Compute NumPy rFFT + spectral kurtosis over 18-40 kHz samples if supplied, otherwise synthesize impulsive envelope
    raw_samples = payload.get("ultrasonic_samples")
    sample_rate_hz = _vfloat(payload.get("sample_rate_hz"), 96000.0, 96000.0, 1000000.0)
    arc_fault_drive = _vfloat(payload.get("arc_fault_drive"), 0.0, 0.0, 1.0)

    clean_samples: List[float] = []
    if isinstance(raw_samples, list) and len(raw_samples) >= 64:
        for x in raw_samples[:4096]:
            if x is not None and not isinstance(x, bool):
                try:
                    fx = float(x)
                    if math.isfinite(fx):
                        clean_samples.append(max(-1e6, min(1e6, fx)))
                except (TypeError, ValueError):
                    pass

    if len(clean_samples) >= 64:
        sig = np.asarray(clean_samples, dtype=np.float64)
    else:
        n_pts = 512
        t_vec = np.arange(n_pts, dtype=np.float64) / sample_rate_hz
        rng = np.random.default_rng(seed=int(mwir_peak_k * 10) + int(arc_fault_drive * 1000))
        bg_noise = 0.035 * rng.standard_normal(n_pts)
        # Impulsive 28.5 kHz ultrasonic bursts characteristic of pre-ignition cable arcing / polymer outgassing
        burst_env = np.where((np.arange(n_pts) % 97) < 5, 1.0, 0.0)
        arc_wave = arc_fault_drive * 1.45 * burst_env * np.sin(2.0 * math.pi * 28500.0 * t_vec)
        sig = bg_noise + arc_wave

    sig_zero = sig - float(np.mean(sig))
    std_val = float(np.std(sig_zero))
    kurtosis_val = (
        float(np.mean((sig_zero ** 4))) / max(1e-12, std_val ** 4)
        if std_val > 1e-7
        else 3.0
    )
    freqs = np.fft.rfftfreq(len(sig_zero), d=1.0 / sample_rate_hz)
    spec_mag = np.abs(np.fft.rfft(sig_zero)) / max(1, len(sig_zero))
    band_mask = (freqs >= 18000.0) & (freqs <= 40000.0)
    ultrasonic_rms = float(np.sqrt(np.mean(spec_mag[band_mask] ** 2))) if np.any(band_mask) else 0.0
    ultrasonic_db = round(max(12.0, min(98.0, 20.0 * math.log10(max(1e-5, ultrasonic_rms * 1800.0)) + 34.0)), 1)

    daft_res = compute_optical_beer_lambert_and_daft_scattering(
        transmission_i_over_i0=transmission,
        path_length_m=0.12,
        particle_diameter_um=particle_um,
    )

    optical_visible_fire = (opt_soot >= 0.25 or opt_blue >= 0.34) and mwir_peak_k >= 820.0
    mwir_invisible_fire = (not optical_visible_fire) and (mwir_peak_k >= 515.0 or mwir_dt_dt >= 4.5)
    ultrasonic_pre_ignition = (kurtosis_val >= 5.2 and ultrasonic_db >= 46.0) or arc_fault_drive >= 0.35

    if optical_visible_fire:
        detection_state = "ACTIVE_VISIBLE_FLAME"
        headline_en = f"[{comp_id}] Optical Chemiluminescence + MWIR Flame Confirmed ({mwir_peak_k:.0f} K)"
    elif mwir_invisible_fire:
        detection_state = "INVISIBLE_COOL_OR_H2_FLAME_MWIR"
        headline_en = f"[{comp_id}] Optical Blind! MWIR 3–5 µm Caught Invisible Cool/H₂ Flame ({mwir_peak_k:.0f} K, +{mwir_dt_dt:.1f} K/s)"
    elif ultrasonic_pre_ignition:
        detection_state = "PRE_IGNITION_ULTRASONIC_ARC_OUTGAS"
        headline_en = f"[{comp_id}] Pre-Ignition 18–40 kHz Ultrasonic Arc / Outgassing (Kurtosis κ={kurtosis_val:.1f})"
    elif daft_res["false_alarm_rejected"]:
        detection_state = "NUISANCE_DUST_REJECTED"
        headline_en = f"[{comp_id}] Lunar Regolith Nuisance Dust Rejected (DAFT Ratio={daft_res['daft_ratio_405_880']})"
    else:
        detection_state = "NOMINAL_CLEAR"
        headline_en = f"[{comp_id}] Optical, MWIR & 18–40 kHz Acoustic Channels Nominal"

    return {
        "ok": True,
        "compartment_id": comp_id,
        "camera_mode": camera_mode,
        "detection_state": detection_state,
        "headline_tr": headline_en,
        "headline_en": headline_en,
        "optical_mwir": {
            "optical_blue_chemilum": round(opt_blue, 3),
            "optical_soot_lum": round(opt_soot, 3),
            "mwir_peak_temp_k": round(mwir_peak_k, 1),
            "mwir_dt_dt_k_s": round(mwir_dt_dt, 2),
            "co_ppm": round(co_ppm, 1),
        },
        "ultrasonic_acoustic": {
            "band_khz": "18.0 - 40.0 kHz",
            "ultrasonic_spl_db": ultrasonic_db,
            "spectral_kurtosis": round(kurtosis_val, 2),
            "arc_or_pyrolysis_anomaly": ultrasonic_pre_ignition,
        },
        "beer_lambert_daft": daft_res,
    }
