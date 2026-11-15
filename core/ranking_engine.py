# -*- coding: utf-8 -*-
"""
ALTAR-NASA v6.3 Experiment Ranking, Domain-Synonym Semantic Vector Search (RAG),
Orbital Hardware Rack Filter (CIR/MDCA • MSG/SPICE • Cygnus • Cabin/DAFT), and Cross-Experiment Comparison Engine.
Uses NumPy TF-IDF + character 4-gram features + scientific domain synonym expansion
with cosine similarity and physical mission-parameter affinity scoring.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional

import numpy as np

from core.nasa_datasets import NASA_EXPERIMENTS_CATALOG
from core.physics_engine import simulate_combustion_state

ENGLISH_STOP_WORDS = {
    "the", "and", "for", "with", "from", "into", "that", "this", "are", "was",
    "were", "has", "have", "had", "not", "but", "what", "when", "where", "which",
    "who", "how", "why", "can", "will", "about", "between", "under", "over",
}

# English combustion & spacecraft fire-safety domain synonym expansion map
BILINGUAL_SCIENTIFIC_SYNONYMS: Dict[str, str] = {
    "cool flame": "cool flame ntc low temperature radiative extinction heptane decane flex cfi cfi-g",
    "ntc": "negative temperature coefficient cool flame peroxy low temperature flex cfi cfi-g",
    "droplet": "droplet spherical liquid heptane methanol decane d2 spalding flex flex-2 cfi mdca",
    "ventilation": "ventilation airflow forced flow fan low velocity bass bass-ii spice slice moc",
    "airflow": "ventilation airflow low velocity opposed concurrent flow msg spice duct",
    "fan": "ventilation airflow low velocity opposed flow hvac msg spice duct",
    "oxygen": "oxygen o2 moc concentration partial pressure exploration atmosphere cfi-g saffire-v",
    "spacesuit": "spacesuit eva 4.3 psia 100% o2 pure oxygen nomex pre-breathe",
    "eva": "spacesuit eva 4.3 psia 100% o2 pure oxygen nomex airlock",
    "rover": "pressurized rover lunar base 10.2 psia 30% o2 32% o2 sofie saffire-v",
    "artemis": "exploration atmosphere 34% o2 8.2 psia 10.2 psia lunar habitat orion gateway saffire-v sofie",
    "lunar": "lunar moon 0.16g exploration atmosphere 8.2 psia 10.2 psia 34% o2 luci fm2 daft daft-2",
    "moon": "lunar partial gravity 0.16g luci fm2 regolith dust daft-2 exploration atmosphere",
    "mars": "martian 0.38g exploration habitat low pressure partial gravity",
    "partial gravity": "partial gravity lunar-g 0.16g 0.38g luci fm2 acme e-field ionic wind",
    "fabric": "fabric textile cloth sibal cotton fiberglass nomex bass-ii saffire",
    "textile": "fabric textile sibal cotton fiberglass nomex bass-ii saffire",
    "acrylic": "pmma polymer solid cast acrylic bass sofie saffire-iv saffire-v",
    "polymer": "pmma polymer solid fuel pyrolysis sofie bass bre",
    "water mist": "water mist fine mist suppression pfe sofie-mist flex-2 latent heat",
    "suppression": "suppression extinguish quenching blowoff water mist pfe non-halon",
    "halon": "suppression water mist pfe non-halon hf hbr nasa-std-6001b",
    "soot": "soot radiation yellow shell luminous acme spice smoke point",
    "smoke point": "smoke point co-flow spice soot msg laminar jet",
    "liftoff": "liftoff blowout blowoff triple flame slice msg",
    "electric field": "electric field ionic wind e-field partial gravity chemi-ion acme",
    "large scale": "large scale meter scale cygnus spacecraft cabin saffire",
    "smoke": "smoke aerosol co carbon monoxide scrubber psd saffire-iv same daft",
    "dust": "dust aerosol regolith nuisance discrimination daft daft-2 same smoke detector",
    "sensor": "sensor radiometer thermocouple optical uv ir laser co anita-2 csa-cp daft",
    "burner": "burner porous spherical bre cfi-g acme spice",
}


def _expand_bilingual_text(text: str) -> str:
    lower = text.lower()
    extras: List[str] = []
    for term, expansion in BILINGUAL_SCIENTIFIC_SYNONYMS.items():
        if term in lower:
            extras.append(expansion)
    return f"{lower} {' '.join(extras)}"


def _tokenize_features(text: str) -> Counter:
    """Extract word tokens and character 4-gram root features with English domain synonym expansion."""
    expanded = _expand_bilingual_text(text)
    words = [w for w in re.findall(r"[a-z0-9]{2,}", expanded) if w not in ENGLISH_STOP_WORDS]
    counts: Counter = Counter()
    for w in words:
        counts[f"w:{w}"] += 2.0
        if len(w) >= 4:
            for i in range(len(w) - 3):
                counts[f"g:{w[i:i+4]}"] += 0.5
    return counts


class SemanticKnowledgeIndex:
    """
    Lightweight, portable NumPy TF-IDF cosine-similarity vector index.
    Indexes both the built-in 15 NASA PSI investigations and user-ingested PDF/NTRS documents.
    """

    def __init__(self) -> None:
        self.documents: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Optional[np.ndarray] = None
        self.matrix: Optional[np.ndarray] = None
        self._seed_catalog()

    def _seed_catalog(self) -> None:
        for exp in NASA_EXPERIMENTS_CATALOG:
            runs_txt = " ".join(
                f"{r.get('run_code', '')} {r.get('diff_en', '')} {r.get('result_en', '')}"
                for r in exp.get("intra_runs", [])
            )
            combined = (
                f"{exp['exp_id']} {exp['program']} {exp.get('hardware_group', '')} {exp['facility']} "
                f"{exp['title']} {exp['material']} "
                f"{exp.get('sample_geometry_en', '')} {exp.get('sensors_en', '')} "
                f"{exp['key_finding_en']} {exp['safety_insight_en']} "
                f"{runs_txt} {' '.join(exp['tags'])}"
            )
            summary_txt = f"{exp['key_finding_en']} {exp['safety_insight_en']}"
            self.documents.append({
                "doc_id": exp["exp_id"],
                "doc_type": "nasa_experiment",
                "title": exp["title"],
                "title_tr": exp["title"],
                "title_en": exp["title"],
                "source": f"{exp['program']} • NTRS {exp['ntrs_id']}",
                "url": exp["ntrs_url"],
                "text": combined,
                "text_tr": summary_txt,
                "text_en": summary_txt,
                "metadata": exp,
            })
        self._rebuild_matrix()

    def add_custom_document(self, title: str, content: str, source: str = "User Upload", url: str = "") -> int:
        """Chunk and index an uploaded PDF/Web/NTRS document into the semantic vector matrix."""
        clean = (content or "").strip()
        if not clean:
            return 0
        chunk_size = 1200
        overlap = 150
        chunks: List[str] = []
        idx = 0
        while idx < len(clean) and len(chunks) < 40:
            chunks.append(clean[idx:idx + chunk_size])
            idx += (chunk_size - overlap)

        base_num = len(self.documents)
        for i, ch in enumerate(chunks, 1):
            part_title = f"{title} (Part {i}/{len(chunks)})"
            self.documents.append({
                "doc_id": f"DOC-{base_num + i}",
                "doc_type": "ingested_doc",
                "title": part_title,
                "title_tr": part_title,
                "title_en": part_title,
                "source": source,
                "url": url,
                "text": f"{title}\n{ch}",
                "text_tr": f"{title}\n{ch}",
                "text_en": f"{title}\n{ch}",
                "metadata": {"snippet": ch[:450]},
            })
        self._rebuild_matrix()
        return len(chunks)

    def _rebuild_matrix(self) -> None:
        if not self.documents:
            return
        tokenized_docs = [_tokenize_features(d["text"]) for d in self.documents]
        df: Counter = Counter()
        for tdoc in tokenized_docs:
            for feat in tdoc.keys():
                df[feat] += 1

        most_common = [feat for feat, _ in df.most_common(4096)]
        self.vocab = {feat: idx for idx, feat in enumerate(most_common)}
        n_docs = len(self.documents)
        n_vocab = len(self.vocab)

        idf_arr = np.zeros(n_vocab, dtype=np.float32)
        for feat, idx in self.vocab.items():
            idf_arr[idx] = math.log((1.0 + n_docs) / (1.0 + df[feat])) + 1.0
        self.idf = idf_arr

        mat = np.zeros((n_docs, n_vocab), dtype=np.float32)
        for d_idx, tdoc in enumerate(tokenized_docs):
            for feat, cnt in tdoc.items():
                v_idx = self.vocab.get(feat)
                if v_idx is not None:
                    mat[d_idx, v_idx] = (1.0 + math.log(cnt)) * idf_arr[v_idx]
            norm = np.linalg.norm(mat[d_idx])
            if norm > 1e-8:
                mat[d_idx] /= norm
        self.matrix = mat

    def search(self, query: str, top_k: int = 5, doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.matrix is None or self.idf is None or not self.vocab:
            return []
        q_feats = _tokenize_features(query or "microgravity combustion")
        q_vec = np.zeros(len(self.vocab), dtype=np.float32)
        for feat, cnt in q_feats.items():
            v_idx = self.vocab.get(feat)
            if v_idx is not None:
                q_vec[v_idx] = (1.0 + math.log(cnt)) * self.idf[v_idx]
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 1e-8:
            q_vec /= q_norm

        scores = self.matrix @ q_vec
        ranked_indices = np.argsort(-scores)

        results: List[Dict[str, Any]] = []
        for idx in ranked_indices:
            doc = self.documents[int(idx)]
            if doc_type and doc["doc_type"] != doc_type:
                continue
            sim = float(scores[int(idx)])
            results.append({
                "doc_id": doc["doc_id"],
                "doc_type": doc["doc_type"],
                "title": doc["title"],
                "title_tr": doc.get("title_tr", doc["title"]),
                "title_en": doc.get("title_en", doc["title"]),
                "source": doc["source"],
                "url": doc["url"],
                "similarity": round(max(0.0, sim), 4),
                "text": doc["text"][:800],
                "text_tr": (doc.get("text_tr") or doc["text"])[:800],
                "text_en": (doc.get("text_en") or doc["text"])[:800],
                "metadata": doc["metadata"],
            })
            if len(results) >= top_k:
                break
        return results


class ExperimentRankingEngine:
    """
    Execute the core 'Summarize, Rank, Compare & Interpret' workflow across NASA PSI datasets.
    Scores and ranks investigations against the target mission atmosphere, orbital rack filter
    (CIR / MSG / CYGNUS / CABIN), and natural-language query using:
    1) Physical Parameter Affinity (O₂ %, Pressure psia, Airflow cm/s, Fuel class, Partial-G)
    2) Semantic Query Cosine Similarity
    3) Predicted Mission Fire Hazard Score
    """

    def __init__(self, knowledge_index: Optional[SemanticKnowledgeIndex] = None) -> None:
        self.index = knowledge_index if knowledge_index is not None else SemanticKnowledgeIndex()
        self.dynamic_experiments: List[Dict[str, Any]] = []

    def _all_experiments(self) -> List[Dict[str, Any]]:
        return list(self.dynamic_experiments) + list(NASA_EXPERIMENTS_CATALOG)

    def register_dynamic_experiment(
        self,
        filename: str,
        sim_params: Dict[str, Any],
        sim_state: Dict[str, Any],
        summary_tr: str = "",
        summary_en: str = "",
    ) -> Dict[str, Any]:
        """Register an uploaded NASA PSI or laboratory dataset dynamically into the ranking catalog."""
        _ = sim_params
        inp = sim_state.get("inputs", {})
        tel = sim_state.get("telemetry", {})
        clean_name = re.sub(r"\.[a-zA-Z0-9]{1,5}$", "", filename or "Uploaded_Dataset").strip() or "Uploaded_Dataset"
        existing = next((x for x in self.dynamic_experiments if x.get("source_filename") == filename), None)
        exp_id = existing["exp_id"] if existing else f"PSI-USR-{len(self.dynamic_experiments) + 1:02d}"

        flow_val = float(inp.get("airflow_cms", 0.0))
        flow_dir = str(inp.get("flow_direction", "opposed"))
        flow_regime = "quiescent" if flow_val < 1.0 else flow_dir
        spread_val = float(tel.get("flame_spread_mm_s", 0.0))
        k_val = float(tel.get("burning_rate_k_mm2_s", 0.0))
        rate_str = (
            f"Spread = {spread_val:.2f} mm/s"
            if spread_val > 0.05
            else f"K = {k_val:.3f} mm²/s"
        )
        raw_sum = summary_en or summary_tr or ""
        short_sum_en = raw_sum.splitlines()[0][:200] if raw_sum else f"Experiment record extracted from uploaded dataset ({filename})."
        short_sum_clean = short_sum_en.replace("**", "")

        prog_label = f"Uploaded ({clean_name[:18]})"
        title_label = f"Uploaded Dataset — {clean_name}"
        fac_label = "User Dataset Upload / PSI Table"
        geom_label = f"Uploaded dataset geometry (D₀ = {inp.get('droplet_d0_mm', 3.2)} mm)"
        sens_label = "Uploaded file telemetry (Temperature, O₂, Pressure, Radiometer / CO)"
        insight_label = "Uploaded test parameters were automatically benchmarked against target cabin conditions."
        run_same = f"File: {filename}, Pressure: {inp.get('pressure_psia', 14.7)} psia"
        run_diff = f"O₂: {inp.get('oxygen_pct', 21.0)}%, Flow: {flow_val} cm/s ({flow_dir})"
        run_res = f"Evaluated T_f = {tel.get('flame_temp_k', 0)} K, MOC = {tel.get('moc_pct', 0)}%, {rate_str}."

        record: Dict[str, Any] = {
            "exp_id": exp_id,
            "source_filename": filename,
            "is_dynamic_upload": True,
            "program": prog_label,
            "program_tr": prog_label,
            "program_en": prog_label,
            "hardware_group": "CIR" if inp.get("fuel_phase") != "solid" else "MSG",
            "title": title_label,
            "title_tr": title_label,
            "title_en": title_label,
            "facility": fac_label,
            "facility_tr": fac_label,
            "facility_en": fac_label,
            "year": 2026,
            "fuel_id": str(inp.get("fuel_id", "n_heptane")),
            "custom_material_name": str(inp.get("custom_material_name", "")),
            "material": str(inp.get("fuel_name_en", inp.get("fuel_id", "Sample"))),
            "sample_geometry_tr": geom_label,
            "sample_geometry_en": geom_label,
            "sensors_tr": sens_label,
            "sensors_en": sens_label,
            "gravity_g": float(inp.get("gravity_g", 0.0)),
            "oxygen_pct": float(inp.get("oxygen_pct", 21.0)),
            "pressure_psia": float(inp.get("pressure_psia", 14.7)),
            "airflow_cms": flow_val,
            "moc_measured_pct": float(tel.get("moc_pct", 15.0)),
            "scale_class_tr": "Uploaded Dataset",
            "scale_class_en": "Uploaded Dataset",
            "hrrpua_kw_m2": float(tel.get("hrrpua_kw_m2", 120.0)),
            "flow_regime": flow_regime,
            "burning_rate_or_spread": rate_str,
            "cool_flame_observed": bool(tel.get("cool_flame_active", False)),
            "ntrs_id": "USER-DATA",
            "ntrs_url": "https://psi.nasa.gov/",
            "psi_id": exp_id,
            "psi_url": "https://psi.nasa.gov/",
            "key_finding_tr": short_sum_clean,
            "key_finding_en": short_sum_clean,
            "safety_insight_tr": insight_label,
            "safety_insight_en": insight_label,
            "intra_runs": [
                {
                    "run_code": f"{exp_id}-R1",
                    "same_tr": run_same,
                    "same_en": run_same,
                    "diff_tr": run_diff,
                    "diff_en": run_diff,
                    "result_tr": run_res,
                    "result_en": run_res,
                }
            ],
            "tags": ["user upload", "dynamic", clean_name.lower(), str(inp.get("fuel_id", ""))],
        }
        if existing:
            idx = self.dynamic_experiments.index(existing)
            self.dynamic_experiments[idx] = record
        else:
            self.dynamic_experiments.insert(0, record)
            doc_summary = f"{record['key_finding_en']} {record['safety_insight_en']}"
            self.index.documents.append({
                "doc_id": exp_id,
                "doc_type": "nasa_experiment",
                "title": record["title_en"],
                "title_tr": record["title_tr"],
                "title_en": record["title_en"],
                "source": f"{record['program']} • {filename}",
                "url": record["ntrs_url"],
                "text": f"{exp_id} {clean_name} {record['material']} {record['key_finding_en']}",
                "text_tr": doc_summary,
                "text_en": doc_summary,
                "metadata": record,
            })
            self.index._rebuild_matrix()
        return record

    def rank_experiments(
        self,
        mission_params: Optional[Dict[str, Any]] = None,
        query: str = "",
        hardware_filter: str = "ALL",
    ) -> Dict[str, Any]:
        if not isinstance(mission_params, dict):
            mission_params = {}

        def _rfloat(val: Any, default: float, lo: float, hi: float) -> float:
            if val is None or isinstance(val, bool):
                return default
            try:
                fv = float(val)
            except (TypeError, ValueError):
                return default
            if not math.isfinite(fv):
                return default
            return max(lo, min(hi, fv))

        target_o2 = _rfloat(mission_params.get("oxygen_pct"), 21.0, 5.0, 100.0)
        target_p = _rfloat(mission_params.get("pressure_psia"), 14.7, 2.0, 30.0)
        target_flow = _rfloat(mission_params.get("airflow_cms"), 3.5, 0.0, 100.0)
        target_flow_dir = "concurrent" if str(mission_params.get("flow_direction", "opposed")).lower() == "concurrent" else "opposed"
        target_fuel = str(mission_params.get("fuel_id", "n_heptane"))
        if target_fuel == "custom_material":
            from core.physics_engine import resolve_analog_material
            target_fuel = resolve_analog_material(mission_params)["base_fuel_id"]
        target_g = _rfloat(mission_params.get("gravity_g"), 0.0, 0.0, 2.0)
        hw_norm = (hardware_filter or "ALL").strip().upper()

        all_exps = self._all_experiments()
        sem_map: Dict[str, float] = {}
        if query and query.strip():
            sem_hits = self.index.search(query.strip(), top_k=len(all_exps), doc_type="nasa_experiment")
            for h in sem_hits:
                sem_map[h["doc_id"]] = h["similarity"]

        ranked: List[Dict[str, Any]] = []
        for exp in all_exps:
            if hw_norm not in ("", "ALL") and exp.get("hardware_group", "").upper() != hw_norm:
                continue

            # 1) Atmosphere, Flow Direction, and Scale Affinity Score (0 - 100)
            o2_diff = abs(target_o2 - float(exp["oxygen_pct"]))
            p_diff = abs(target_p - float(exp["pressure_psia"]))
            flow_diff = abs(target_flow - float(exp["airflow_cms"]))
            exp_fuel = exp["fuel_id"]
            fuel_bonus = 22.0 if exp_fuel == target_fuel else 0.0
            partial_g_bonus = 14.0 if (0.04 <= target_g <= 0.85 and exp["exp_id"] in ("PSI-ACME-09", "PSI-SOFIE-08", "PSI-SAFFIRE5-07", "PSI-DAFT-15")) else 0.0

            exp_freg = str(exp.get("flow_regime", "opposed")).lower()
            if target_flow < 1.0 and exp_freg == "quiescent":
                flow_dir_bonus = 8.0
            elif target_flow >= 1.0 and (exp_freg == target_flow_dir or exp_freg == "both"):
                flow_dir_bonus = 7.5
            else:
                flow_dir_bonus = 0.0
            dyn_bonus = 10.0 if exp.get("is_dynamic_upload") else 0.0

            param_affinity = max(
                10.0,
                100.0 - (min(42.0, o2_diff * 1.6) + p_diff * 2.6 + flow_diff * 1.3) + fuel_bonus + partial_g_bonus + flow_dir_bonus + dyn_bonus,
            )
            param_affinity = min(100.0, param_affinity)

            # 2) Predicted physical fire hazard of the investigation's fuel under target mission conditions
            sim_eval = simulate_combustion_state({
                "fuel_id": exp["fuel_id"],
                "custom_material_name": exp.get("custom_material_name", ""),
                "gravity_g": target_g,
                "oxygen_pct": target_o2,
                "pressure_psia": target_p,
                "airflow_cms": target_flow,
                "flow_direction": target_flow_dir,
                "droplet_d0_mm": 3.5,
                "diluent": mission_params.get("diluent", "N2"),
            })
            hazard_score = float(sim_eval["telemetry"]["risk_score"])

            # 3) Semantic query relevance
            sem_score = sem_map.get(exp["exp_id"], 0.0) * 100.0

            if query and query.strip():
                composite = 0.44 * sem_score + 0.32 * param_affinity + 0.24 * hazard_score
            else:
                composite = 0.56 * param_affinity + 0.44 * hazard_score

            ranked.append({
                **exp,
                "priority_score": round(min(99.9, composite), 1),
                "param_affinity": round(param_affinity, 1),
                "mission_hazard_score": int(hazard_score),
                "predicted_regime_in_mission": sim_eval["telemetry"]["regime"],
                "predicted_moc_in_mission": sim_eval["telemetry"]["moc_pct"],
                "predicted_hrrpua_kw_m2": sim_eval["telemetry"].get("hrrpua_kw_m2", exp.get("hrrpua_kw_m2", 120.0)),
            })

        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        for rank_no, item in enumerate(ranked, 1):
            item["rank"] = rank_no

        return {
            "count": len(ranked),
            "hardware_filter": hw_norm,
            "mission_evaluated": {
                "oxygen_pct": target_o2,
                "pressure_psia": target_p,
                "airflow_cms": target_flow,
                "flow_direction": target_flow_dir,
                "gravity_g": target_g,
                "fuel_id": target_fuel,
            },
            "ranked_experiments": ranked,
        }

    def compare_experiments(self, exp_ids: List[str], mission_params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare 2 to 4 NASA PSI investigations across facility hardware, HRRPUA scale, sensors, MOC, and worst-case safety bounds."""
        _ = mission_params
        all_exps = self._all_experiments()
        selected = [e for e in all_exps if e["exp_id"] in exp_ids]
        if len(selected) < 2:
            selected = all_exps[:3]

        lowest_moc_exp = min(selected, key=lambda x: x["moc_measured_pct"])
        highest_moc_exp = max(selected, key=lambda x: x["moc_measured_pct"])
        highest_o2_exp = max(selected, key=lambda x: x["oxygen_pct"])
        max_hrrpua_exp = max(selected, key=lambda x: float(x.get("hrrpua_kw_m2", 0.0)))
        cool_flame_exps = [x["program"] for x in selected if x["cool_flame_observed"]]
        facilities = sorted(list({x.get("hardware_group", "CIR") for x in selected}))
        scales_en = sorted(list({str(x.get("scale_class_en", "Medium Scale")).split("(")[0].strip() for x in selected}))

        # Data discrepancy and conservative safety bounding (Worst-Case Bounding)
        conflict_reasons_en: List[str] = []
        sel_ids = {x["exp_id"] for x in selected}
        moc_span = round(float(highest_moc_exp["moc_measured_pct"]) - float(lowest_moc_exp["moc_measured_pct"]), 2)

        if "PSI-BASS-03" in sel_ids or "PSI-BASS2-04" in sel_ids:
            conflict_reasons_en.append("samples self-extinguishing in quiescent 0G yet burning steadily under gentle 3–8 cm/s ventilation")
        if "PSI-SAFFIRE4-06" in sel_ids or "PSI-SAFFIRE1-05" in sel_ids:
            conflict_reasons_en.append("thick/flat slabs quenching while thin or ribbed geometries accelerate flame spread by +45%")
        if len(scales_en) >= 2:
            conflict_reasons_en.append(f"scale divergence across facilities ({' vs. '.join(scales_en)})")
        if moc_span >= 2.2:
            conflict_reasons_en.append(f"a {moc_span:.1f}% O₂ spread in measured MOC thresholds")

        has_conflict = len(conflict_reasons_en) > 0
        worst_moc = float(lowest_moc_exp["moc_measured_pct"])
        worst_hrrpua = float(max_hrrpua_exp.get("hrrpua_kw_m2", 180.0))
        conflict_warning_en = (
            f"Data Discrepancy & Worst-Case Bounding: Detected {'; '.join(conflict_reasons_en)}. "
            f"Instead of averaging conflicting outcomes, conservative safety bounding enforces MOC Ceiling = {worst_moc:.1f}% O₂ ({lowest_moc_exp['program']}) "
            f"and Peak HRRPUA = {worst_hrrpua:.0f} kW/m² ({max_hrrpua_exp['program']})."
            if has_conflict else ""
        )
        conflict_warning_tr = conflict_warning_en

        hw_note_en = (
            f"All selected investigations share the **{facilities[0]}** orbital hardware facility. "
            if len(facilities) == 1
            else f"Spans distinct orbital facilities (**{' vs. '.join(facilities)}**), normalized via scale-independent Heat Release Rate Per Unit Area (`HRRPUA`). "
        )

        synthesis_en = (
            f"**Cross-Experiment Comparison Summary ({len(selected)} NASA PSI Records):** {hw_note_en}"
            f"**{lowest_moc_exp['program']}** ({lowest_moc_exp['material']}) exhibits the lowest Minimum Oxygen Concentration "
            f"(**{lowest_moc_exp['moc_measured_pct']}% O₂**), while **{max_hrrpua_exp['program']}** reaches **{worst_hrrpua:.0f} kW/m² HRRPUA** (Max O₂: **{highest_o2_exp['oxygen_pct']}%**). "
        )
        if cool_flame_exps:
            synthesis_en += (
                f"Invisible NTC Cool Flame persistence in **{', '.join(cool_flame_exps)}** mandates CIR UV/IR radiometry and CSA-CP/ANITA-2 CO/CH₂O gas monitoring alongside DAFT/SAME dust-immune smoke detection."
            )
        else:
            synthesis_en += "Immediate cabin HVAC shutoff and fine water mist (SoFIE-MIST) remain the universal non-Halon countermeasures."
        synthesis_tr = synthesis_en

        return {
            "compared_count": len(selected),
            "experiments": selected,
            "lowest_moc_program": lowest_moc_exp["program"],
            "synthesis_tr": synthesis_tr,
            "synthesis_en": synthesis_en,
            "conflict_bounding": {
                "has_conflict": has_conflict,
                "worst_case_moc_pct": worst_moc,
                "worst_case_hrrpua_kw_m2": worst_hrrpua,
                "warning_tr": conflict_warning_tr,
                "warning_en": conflict_warning_en,
            },
        }
