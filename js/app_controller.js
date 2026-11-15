/* ============================================================================
   ALTAR-NASA Mission Control Main Controller v6.3 (app_controller.js)
   - 3D WebGL Combustion Chamber, Artemis Orion MCP Digital Twin & 3D Cabin Camera
   - Analytical ±1σ Uncertainty Bounds, 5-Phase Material Certification & 0G Cooling
   - Multi-File NASA PSI Bundle Ingestion & Dynamic Custom Equation Verifier
   - Offline Visual Engineering Report with 4 Vector Charts (.html / PDF) + CSV / JSON
   - Pure Aerospace Engineering Interface (Strict CSP Compliant)
   ============================================================================ */

(function () {
    "use strict";

    const UI_I18N = {
        en: {
            doc_title: "ALTAR-NASA • Flame in Freefall | Microgravity Combustion & Orion MCP Fire Safety Platform",
            brand_sub: "Microgravity Combustion Analysis & Fire Safety Platform",
            nav_lab: "Combustion Chamber",
            nav_rank: "NASA Experiments",
            nav_live: "Data & Imagery",
            nav_copilot: "Engineering Analysis",
            nav_settings: "Validation & Settings",
            tip_stream_pill: "Live Telemetry Stream Status",
            tip_engine_pill: "Active Analytical Solver Status",
            tip_export_report: "Download Visual Engineering Report (.html / PDF)",
            tip_unload: "Clear Memory",
            mission_cert_title: "Mission Material Certification",
            quick_ingest_title: "Quick File Load",
            quick_ingest_desc: "Parameters from single or multi-file datasets and flame photos/videos are automatically merged and applied to 3D:",
            presets_title: "Mission Presets",
            controls_title: "Chamber Controls",
            lbl_fuel: "Fuel Type",
            lbl_custom_mat_name: "Material Name",
            custom_mat_ph: "e.g. PEEK, XLPE, PTFE, Kapton",
            ph_auto: "Auto",
            lbl_custom_rho: "Density (kg/m³)",
            lbl_custom_lambda: "Conductivity (W/mK)",
            lbl_gravity: "Gravity Level",
            lbl_oxygen: "Oxygen Level",
            lbl_pressure: "Ambient Pressure",
            lbl_airflow: "Airflow Speed",
            lbl_flow_dir: "Flow Direction",
            btn_flow_opposed: "Opposed Flow",
            btn_flow_concurrent: "Concurrent Flow",
            lbl_droplet: "Sample Diameter",
            lbl_diluent: "Diluent Gas",
            audio_title: "Telemetry Sonification",
            audio_start: "Play Audio",
            audio_stop: "Mute Audio",
            audio_desc: "Maps flame temperature, radiative flux, and invisible Cool Flame telemetry to audio frequencies for eyes-free monitoring (data sonification).",
            chamber_title: "3D Combustion Chamber & Orion MCP",
            vp_mode_chamber: "3D Combustion Chamber",
            vp_mode_spacecraft: "Orion MCP",
            orion_hull_ext: "Outer Hull",
            orion_hull_cut: "Cutaway",
            orion_sec_0: "Command",
            orion_sec_2: "Living",
            orion_sec_1: "Power",
            orion_sec_3: "Tunnel",
            orion_sec_4: "Air",
            spec_v2_live: "Live ISS 0G Computing",
            cam_reignite: "Re-Ignite",
            leg_blue: "Blue Flame",
            leg_soot: "Soot Glow",
            leg_cool: "Cool Flame",
            leg_geom: "Fuel Sample",
            chart_sensor_title: "Sensor Time Chart",
            chart_sensor_sub: "Optical • IR • CO",
            tel_panel_title: "Live Measurements",
            btn_ai_interpret: "Detailed Analysis",
            lbl_risk_score: "FIRE RISK SCORE",
            card_temp: "Flame Temperature",
            card_moc: "Critical Oxygen",
            card_kburn: "Burn Constant",
            card_spread: "Spread Rate",
            card_rad: "Radiative Loss",
            card_co: "Carbon Monoxide",
            chart_moc_title: "Flammability Map",
            chart_moc_desc: "0G, 0.16G Lunar (LUCI/FM2), 0.38G Mars, 1G MOC curves and ±1σ analytical confidence band bound partial-gravity flammability.",
            formula_table_title: "Governing Equations",
            th_law: "Physical Law",
            th_eq: "Equation",
            th_val: "Live Value",
            th_status: "Status",
            live_synthesis_title: "Instant Summary",
            btn_full_ai_report: "Full Report",
            cabin_clock_title: "Life Support Clock",
            rank_main_title: "Experiment Ranking",
            rank_main_desc: "Ranks and compares 15 verified NASA PSI experiments by physical similarity across stations, EVA suits, Lunar/Mars bases, and pressurized rovers.",
            rank_placeholder: "e.g., cool flame, CFI-G, DAFT dust, SPICE, rover...",
            btn_rerank: "Sort",
            btn_compare: "Compare Selected",
            lbl_hw_filter: "Hardware Filter:",
            hw_all: "All Experiments",
            hw_cir: "ISS CIR / ACME",
            hw_msg: "MSG Flow Duct",
            hw_cygnus: "Cygnus Vehicle",
            hw_cabin: "Smoke & Dust",
            psi_rocket_scope_note: "NASA PSI Scope Note: High gas velocities inside rocket engines and thrusters render combustion effectively gravity-independent; PSI focuses on fire safety in crew cabins, spacesuits, and surface habitats.",
            th_sel: "Pick",
            th_rank: "Rank",
            th_prog: "Program",
            th_exp_detail: "Summary & Findings",
            th_cond: "Test Conditions",
            th_prio: "Match Score",
            th_evid: "Actions",
            intra_runs_hint: "Click \"Test Variations\" on any experiment above to see how runs inside the same facility differed and stayed constant:",
            cmp_section_title: "Experiment Comparison",
            earth_section_title: "Earth Applications (Live Impact Calculator)",
            stream_panel_title: "Live NASA Stream",
            stream_panel_desc: "Polls official NASA databases (NTRS / OSDR-PSI) or custom JSON / CSV links at your chosen interval and updates the simulation.",
            stream_target_ph: "Query ('auto' = cycles through all NASA experiments) or https://... URL",
            btn_stream_start: "Start Stream",
            btn_stream_stop: "Stop Stream",
            btn_stream_now: "Fetch Now",
            chk_stream_sync: "Automatically apply incoming data to 3D Chamber",
            stream_not_started: "Stream has not started yet.",
            live_search_title: "NASA Archive Search",
            live_search_desc: "Search official psi.nasa.gov, ntrs.nasa.gov, and osdr.nasa.gov services in real time for scientific reports and experiment records.",
            btn_fetch_live: "Search Archive",
            ingest_panel_title: "Data Bundle & Flame Analysis",
            ingest_panel_desc: "Upload single or multi-file NASA PSI bundles (.csv, .tsv, .xlsx, .zip, .pdf, .json) and flame photos/videos (.png, .jpg, .mp4); automatically merged and synced to 3D.",
            lbl_scrape_url: "Parse Web Link",
            btn_scrape_url: "Sync to 3D",
            lbl_choose_file: "Choose Data Bundle or Photo (Multi-File)",
            chk_media_sync: "Automatically apply extracted parameters to 3D Chamber",
            btn_upload_doc: "Analyze File Bundle",
            custom_eq_title: "Custom Equation Verifier",
            custom_eq_desc: "Enter a custom combustion correlation using (O2, P, U, G, D0, B_oq, Sh, Da, Re, Ra, Tf, chi_r) and validate against solver curves:",
            eq_pre_d2: "d²-Law (K)",
            btn_eval_custom_eq: "Validate Equation",
            rag_test_title: "Text Search",
            rag_search_ph: "Search concepts in experiment records...",
            btn_rag_search: "Search",
            copilot_tasks_title: "Quick Questions",
            cp_btn_1: "Evaluate Active Chamber",
            cp_btn_2: "Compare Suit & Rover",
            cp_btn_3: "Partial Gravity Analysis",
            cp_btn_4: "Cool Flame & Sensors",
            cp_btn_5: "Water Mist & Spinoffs",
            copilot_attach_title: "Attach File",
            copilot_attach_desc: "Selecting a flame photo/video (.png/.jpg/.gif/.mp4) or data file (.csv/.xlsx/.zip/.pdf/.json) updates both the 3D simulation and governing equation analysis:",
            chk_6stage: "NASA-STD-6001B Safety Check Active",
            lbl_active_engine: "Analysis Mode:",
            copilot_ctx_tag: "3D Chamber & 15 PSI Experiments Linked",
            welcome_title: "Engineering Analysis & Decision Support",
            kv_solver_lbl: "NUMERICAL SOLVER",
            kv_solver_val: "d² • de Ris • B_oq • Sh • Da",
            kv_corpus_lbl: "DATA SOURCES",
            kv_auditor_lbl: "SAFETY STANDARD",
            welcome_p1: "This module evaluates the active 3D chamber state, dimensionless transport numbers, ±1σ analytical uncertainty bounds, ISS flight validation (R² / RMSE), and 15 verified NASA PSI experiments.",
            welcome_p2: "Ask about flammability bounds, invisible cool-flame behavior, and fine water mist protocols across ISS modules, Orion MCP, EVA suits (100% O₂ @ 4.3 psia), Lunar/Mars bases, and pressurized rovers (10.2 psia).",
            chat_input_ph: "Ask about combustion equations, spacesuit/rover atmospheres, or NASA PSI experiments...",
            btn_stop_chat: "Stop",
            btn_send_chat: "Run Analysis",
            set_card1_title: "Solver Status",
            set_ollama_hub_title: "Local Model Settings",
            spec_k1: "TRANSPORT SOLVER",
            spec_k2: "ISS VALIDATION",
            spec_k3: "OPERATING MODE",
            spec_v3: "Offline / Local",
            spec_k4: "SAFETY STANDARD",
            con_enforced_badge: "ACTIVE AUDIT",
            acc_opt_badge: "OPTIONAL",
            btn_check_all: "Refresh Status",
            lbl_def_provider: "Default Analysis Mode",
            lbl_agy_model: "Local System Bridge",
            lbl_ollama_host: "Local Service Address",
            lbl_ollama_model: "Installed Local Model",
            lbl_ollama_pull: "Download Model or Clear Memory",
            ollama_pull_ph: "Model name",
            btn_pull: "Download",
            btn_unload: "Clear",
            btn_test_provider: "Test Solver",
            set_card2_title: "Advanced Connections",
            set_card2_desc: "Connection keys are never embedded in source code; stored only in your local user configuration file.",
            lbl_gemini_key: "Google Gemini Key",
            lbl_gemini_model: "Google Gemini Model",
            lbl_agy_key: "Local Bridge Key (Optional)",
            agy_key_ph: "Optional API Key...",
            lbl_or_key: "OpenRouter Key",
            lbl_or_model: "OpenRouter Model",
            lbl_custom_gw: "Custom Endpoint Connection",
            custom_key_ph: "API Key",
            custom_model_ph: "Model",
            btn_save_cfg: "Save Settings",
            set_card3_title: "Physical Rules",
            set_card3_desc: "The following transport laws, dimensionless regime bounds, and NASA-STD-6001B flight safety rules are strictly enforced across all solver calculations:",
            lbl_extra_dir: "Reporting Notes",
            extra_dir_ph: "e.g., Always include psia alongside metric kPa pressure units in technical outputs...",
            btn_save_dir: "Update Notes",
            btn_export_report: "Download Report",
            btn_clear_chat: "Reset",
            shield_badge: "Offline Mode",
            lbl_audience: "View:",
            chk_flight_pts: "ISS 0G Benchmark",
            btn_export_csv: "Download CSV",
            btn_export_json: "Download JSON",
        },
    };
    UI_I18N.tr = UI_I18N.en;

    const state = {
        lang: "en",
        audienceMode: "researcher",
        presets: [],
        directives: [],
        earthTransfers: [],
        currentSim: null,
        activeSourceLabel: "Combustion Chamber",
        activeCertPhaseId: "iss_0g",
        lastCustomEqData: null,
        lastCustomEqResult: null,
        lastCustomEquation: null,
        lastConfigData: null,
        lastUrlScrapeStatus: null,
        lastQuickMediaStatus: null,
        lastRagResults: null,
        activeHardwareFilter: "ALL",
        activeIntraExpId: "PSI-FLEX-01",
        rankedList: [],
        selectedCompareIds: new Set(["PSI-FLEX-01", "PSI-BASS-03", "PSI-SAFFIRE5-07", "PSI-ACME-CFIG-14"]),
        chatHistory: [],
        attachedImageB64: null,
        attachedMediaSummary: "",
        attachedMediaSummaryTr: "",
        attachedMediaSummaryEn: "",
        attachedMediaPhases: [],
        attachedMediaName: "",
        activeChatJobId: null,
        chamber3D: null,
        spacecraftStudio: null,
        viewportMode: "chamber",
        flowDirection: "opposed",
        sonifier: null,
        simDebounceTimer: null,
        rankDebounceTimer: null,
        streamEnabled: false,
        lastStreamSeqId: 0,
        streamPollTimer: null,
        lastStreamStatus: null,
        lastLiveNasaData: null,
        lastProvidersData: null,
        lastSearchPickerData: null,
    };

    function $(id) {
        return document.getElementById(id);
    }

    function getCsrfToken() {
        const meta = document.querySelector('meta[name="altar-csrf"]');
        return meta ? (meta.getAttribute("content") || "").trim() : "";
    }

    function formatFriendlyError(err) {
        const raw = err && err.message ? String(err.message).trim() : "";
        if (!raw || /failed to fetch|networkerror|load failed|network request failed/i.test(raw)) {
            return "Could not reach the local server or target web address. Please check the connection and try again.";
        }
        return raw;
    }

    function normalizeUserWebUrl(rawUrl) {
        let u = String(rawUrl || "").trim();
        if (!u) return "";
        const barePsi = u.match(/^PSI-(\d{1,4})$/i);
        if (barePsi) {
            return `https://psi.nasa.gov/physci/repo/data/investigations/PSI-${barePsi[1]}`;
        }
        if (!/^https?:\/\//i.test(u) && /^[a-z0-9.-]+\.[a-z]{2,}(\/|$)/i.test(u)) {
            return `https://${u}`;
        }
        return u;
    }

    async function apiFetch(url, options) {
        if (typeof window.ALTAR_SERVERLESS_FETCH === "function") {
            return window.ALTAR_SERVERLESS_FETCH(url, options || {});
        }
        const opts = Object.assign({}, options || {});
        const hdrs = Object.assign({}, opts.headers || {});
        const tok = getCsrfToken();
        if (tok) {
            hdrs["X-Altar-CSRF"] = tok;
        }
        opts.headers = hdrs;
        try {
            return await fetch(url, opts);
        } catch (firstErr) {
            if (opts.signal && opts.signal.aborted) {
                throw firstErr;
            }
            await new Promise((resolve) => setTimeout(resolve, 220));
            try {
                return await fetch(url, opts);
            } catch (secondErr) {
                if (typeof window.ALTAR_FALLBACK_FETCH === "function") {
                    return window.ALTAR_FALLBACK_FETCH(url, options || {});
                }
                throw secondErr;
            }
        }
    }

    function tStr(key) {
        return UI_I18N.en[key] || key;
    }

    function normalizeSourceLabelForLang(rawLbl) {
        const s = String(rawLbl || "").trim();
        if (!s) return "Combustion Chamber";
        return s;
    }

    function applyLanguageToDOM() {
        state.lang = "en";
        document.documentElement.lang = "en";
        if (UI_I18N.en && UI_I18N.en.doc_title) {
            document.title = UI_I18N.en.doc_title;
        }
        document.querySelectorAll("[data-i18n]").forEach((el) => {
            const key = el.getAttribute("data-i18n");
            if (key === "audio_start" && state.sonifier && state.sonifier.active) {
                el.textContent = tStr("audio_stop");
                return;
            }
            if (key === "btn_stream_start" && state.streamEnabled) {
                el.textContent = tStr("btn_stream_stop");
                return;
            }
            if (UI_I18N.en && UI_I18N.en[key]) {
                el.textContent = UI_I18N.en[key];
            }
        });

        document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
            const key = el.getAttribute("data-i18n-placeholder");
            if (UI_I18N.en && UI_I18N.en[key]) {
                el.setAttribute("placeholder", UI_I18N.en[key]);
            }
        });

        document.querySelectorAll("[data-i18n-title]").forEach((el) => {
            const key = el.getAttribute("data-i18n-title");
            if (UI_I18N.en && UI_I18N.en[key]) {
                el.setAttribute("title", UI_I18N.en[key]);
            }
        });

        document.querySelectorAll("[data-en]").forEach((el) => {
            el.textContent = el.getAttribute("data-en");
        });
        document.querySelectorAll(".msg-body-md[data-reply-en]").forEach((el) => {
            const md = el.getAttribute("data-reply-en");
            if (md) el.innerHTML = renderSafeMarkdown(md);
        });

        state.activeSourceLabel = normalizeSourceLabelForLang(state.activeSourceLabel);

        if (window.ALTAR_SERVERLESS_MODE) {
            if ($("isolation-shield-pill")) {
                $("isolation-shield-pill").textContent = "Browser Mode";
            }
            document.querySelectorAll('[data-i18n="spec_v3"]').forEach((el) => {
                el.textContent = "In-Browser";
            });
        }

        if (!state.streamEnabled && $("header-stream-text")) {
            $("header-stream-text").textContent = "Stream: Ready";
        }
        if ($("live-api-badge") && !state.lastLiveNasaData) {
            $("live-api-badge").textContent = "Ready";
        }
        if (state.attachedMediaName && (state.attachedMediaSummaryEn || state.attachedMediaSummaryTr)) {
            state.attachedMediaSummary = state.attachedMediaSummaryEn || state.attachedMediaSummaryTr;
            renderUploadedMediaUI();
        }
        if (state.lastCustomEqResult || state.lastCustomEqData) {
            renderCustomEquationResult(state.lastCustomEqResult || state.lastCustomEqData);
        }
        if (state.lastUrlScrapeStatus) {
            renderUrlScrapeStatusLine();
        }
        if (state.lastQuickMediaStatus) {
            renderQuickMediaStatusLine();
        }
        if (state.lastRagResults) {
            renderRagSearchResults();
        }
        if (state.spacecraftStudio) {
            state.spacecraftStudio._updateLocalizedHeader();
        }
        renderAudienceBanner();
    }

    function setUrlScrapeStatus(trMsg, enMsg, color) {
        if (!trMsg && !enMsg) {
            state.lastUrlScrapeStatus = null;
            if ($("url-scrape-status-line")) {
                $("url-scrape-status-line").textContent = "";
            }
            return;
        }
        const cleanEn = enMsg || trMsg;
        state.lastUrlScrapeStatus = { tr: cleanEn, en: cleanEn, color: color || "#7dd3fc" };
        renderUrlScrapeStatusLine();
    }

    function renderUrlScrapeStatusLine() {
        const statusLine = $("url-scrape-status-line");
        if (!statusLine || !state.lastUrlScrapeStatus) return;
        statusLine.style.color = state.lastUrlScrapeStatus.color || "#7dd3fc";
        statusLine.textContent = state.lastUrlScrapeStatus.en;
    }

    function setQuickMediaStatus(targetStatusElId, trMsg, enMsg, color, mediaName, isBundle) {
        const statusEl = targetStatusElId ? $(targetStatusElId) : null;
        if (!statusEl) return;
        const cleanEn = enMsg || trMsg;
        const payload = {
            elId: targetStatusElId,
            tr: cleanEn,
            en: cleanEn,
            color: color || "#6ee7b7",
            mediaName: mediaName || "",
            isBundle: Boolean(isBundle),
        };
        if (targetStatusElId === "quick-lab-media-status") {
            state.lastQuickMediaStatus = payload;
        }
        renderStatusPayloadIntoEl(payload);
    }

    function renderStatusPayloadIntoEl(payload) {
        if (!payload || !payload.elId) return;
        const statusEl = $(payload.elId);
        if (!statusEl) return;
        statusEl.style.color = payload.color || "#6ee7b7";
        const msg = payload.en;
        if (!payload.mediaName) {
            statusEl.textContent = msg;
            return;
        }
        statusEl.innerHTML = `${escapeHtml(msg)} <button class="btn-secondary" id="dyn-ask-ai-${payload.elId}" style="margin-left:6px; padding:2px 8px; font-size:11px;">Detailed Analysis</button>`;
        const dynBtn = $(`dyn-ask-ai-${payload.elId}`);
        if (dynBtn) {
            dynBtn.addEventListener("click", () => {
                switchTab("tab-copilot");
                sendChatMessage(
                    payload.isBundle
                        ? `Analyze my uploaded multi-file NASA PSI bundle '${payload.mediaName}', its merged phases, R²/RMSE calibration, and 3D combustion telemetry.`
                        : `Analyze my uploaded dataset/image '${payload.mediaName}', its extracted combustion parameters, and 3D telemetry using governing equations (K, B_oq, Sh, Ra, Da, MOC) and compare with NASA PSI investigations.`
                );
            });
        }
    }

    function renderQuickMediaStatusLine() {
        if (state.lastQuickMediaStatus) {
            renderStatusPayloadIntoEl(state.lastQuickMediaStatus);
        }
    }

    function renderRagSearchResults() {
        const box = $("rag-search-results");
        if (!box || !Array.isArray(state.lastRagResults)) return;
        box.innerHTML = "";
        state.lastRagResults.forEach((r) => {
            const d = document.createElement("div");
            d.className = "live-result-card";
            const titleTxt = r.title_en || r.title || "";
            const bodyTxt = r.text_en || r.text || "";
            d.innerHTML = `
                <div style="display:flex; justify-content:space-between;">
                    <strong style="color:#38bdf8;">${escapeHtml(titleTxt)}</strong>
                    <span class="preset-badge">${(Number(r.similarity || 0) * 100).toFixed(1)}%</span>
                </div>
                <p style="font-size:12px; color:#cbd5e1; margin-top:4px;">${escapeHtml(bodyTxt.slice(0, 260))}...</p>
            `;
            box.appendChild(d);
        });
    }

    function renderAudienceBanner() {
        const box = $("audience-guide-banner");
        if (!box) return;
        const mode = state.audienceMode || "researcher";

        const copy = {
            researcher:
                "**Researcher View:** Phase-specific `d²` droplet (`K`, `B_oq`), `de Ris` solid spread (`V_f`, `B_p`), and `Burke-Schumann` gas diffusion equations (`Sh`, `Da`, `χ_r`) active. **ISS 0G benchmark markers** overlay published NASA GRC `0G` reference curves with `R²` / `RMSE` metrics; download predictive datasets via **Download CSV / JSON** above.",
            student:
                "**Student View:** On Earth (`1G`), rising hot gas stretches flames into teardrops. In freefall (`0G`), buoyancy vanishes (`Ra = 0`); oxygen arrives purely via molecular diffusion, turning the flame into a **sapphire-blue sphere** or an invisible **550–780 K Cool Flame** that blinds optical smoke detectors.",
            engineer:
                "**Engineer View:** Reduced N₂ thermal ballast in EVA suits (`4.3 psia / 100% O₂`) and Lunar rovers (`10.2 psia / 32% O₂`) accelerates flame spread. Monitor the **Life Support Clock** below for official `NASA JSC-20584 CO SMAC` (`100 ppm` 24-hr / `425 ppm` 1-hr) margins; execute **HVAC Cutoff + Fine Water Mist (SoFIE-MIST)** (*Halon 1301 strictly prohibited*).",
        };
        const msg = copy[mode] || copy.researcher;
        box.innerHTML = `<div>${renderSafeMarkdown(msg)}</div>`;
    }

    function showToast(msg) {
        const t = $("app-toast");
        if (!t) return;
        t.textContent = msg;
        t.style.display = "block";
        clearTimeout(t._hideTimer);
        t._hideTimer = setTimeout(() => {
            t.style.display = "none";
        }, 3600);
    }

    function escapeHtml(str) {
        return String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function renderSafeMarkdown(mdText) {
        let cleaned = String(mdText || "")
            .replace(/\\text\{([^}]*)\}/g, "$1")
            .replace(/\\mathrm\{([^}]*)\}/g, "$1")
            .replace(/\\mum\b/g, "µm")
            .replace(/\\mu(?![a-zA-Z])/g, "µ")
            .replace(/\\chi(?![a-zA-Z])/g, "χ")
            .replace(/\\lambda(?![a-zA-Z])/g, "λ")
            .replace(/\\rho(?![a-zA-Z])/g, "ρ")
            .replace(/\\sigma(?![a-zA-Z])/g, "σ")
            .replace(/\\nu(?![a-zA-Z])/g, "ν")
            .replace(/\\tau(?![a-zA-Z])/g, "τ")
            .replace(/\\alpha(?![a-zA-Z])/g, "α")
            .replace(/\\beta(?![a-zA-Z])/g, "β")
            .replace(/\\Delta(?![a-zA-Z])/g, "Δ")
            .replace(/\\nabla(?![a-zA-Z])/g, "∇")
            .replace(/\\infty(?![a-zA-Z])/g, "∞")
            .replace(/\\approx(?![a-zA-Z])/g, "≈")
            .replace(/\\propto(?![a-zA-Z])/g, "∝")
            .replace(/\\(?:leq|le)(?![a-zA-Z])/g, "≤")
            .replace(/\\(?:geq|ge)(?![a-zA-Z])/g, "≥")
            .replace(/\\pm(?![a-zA-Z])/g, "±")
            .replace(/\\cdot(?![a-zA-Z])/g, "·")
            .replace(/\\(?:rightarrow|to)(?![a-zA-Z])/g, "→")
            .replace(/\\times(?![a-zA-Z])/g, "×")
            .replace(/\\%/g, "%")
            .replace(/\$([^$\n]{1,80})\$/g, "$1");
        let html = escapeHtml(cleaned);

        html = html.replace(
            /(?:^\|.+\|[ \t]*(?:\n|$))+/gm,
            (tableBlock) => {
                const lines = tableBlock
                    .trim()
                    .split("\n")
                    .map((ln) => ln.trim())
                    .filter((ln) => ln.startsWith("|") && ln.endsWith("|"));
                if (lines.length < 2 || !/^\|[\s:\-\|]+\|$/.test(lines[1])) {
                    return tableBlock;
                }
                const parseCells = (rowStr) =>
                    rowStr
                        .slice(1, -1)
                        .split("|")
                        .map((c) => c.trim());
                const headers = parseCells(lines[0]);
                const bodyRows = lines.slice(2).map(parseCells);
                const thHtml = headers
                    .map((h) => `<th style="padding:6px 9px; border-bottom:1px solid rgba(56,189,248,0.3); text-align:left; color:#7dd3fc;">${h}</th>`)
                    .join("");
                const trHtml = bodyRows
                    .map(
                        (cols) =>
                            `<tr>${cols
                                .map((c) => `<td style="padding:5px 9px; border-bottom:1px solid rgba(148,163,184,0.14); vertical-align:top;">${c}</td>`)
                                .join("")}</tr>`
                    )
                    .join("");
                return `<div class="chat-table-wrap"><table class="nasa-table" style="width:100%; border-collapse:collapse; font-size:12px;"><thead><tr>${thHtml}</tr></thead><tbody>${trHtml}</tbody></table></div>\n`;
            }
        );

        html = html.replace(/^####\s+(.+)$/gm, "<h4>$1</h4>");
        html = html.replace(/^###\s+(.+)$/gm, "<h3>$1</h3>");
        html = html.replace(/^##\s+(.+)$/gm, "<h3>$1</h3>");
        html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        html = html.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
        html = html.replace(
            /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
            '<a class="ext-link" href="$2" target="_blank" rel="noopener">$1</a>'
        );
        html = html.replace(
            /^&gt;\s*(.+)$/gm,
            '<div style="margin:8px 0; padding:8px 12px; border-left:3px solid #f59e0b; background:rgba(245,158,11,0.1); border-radius:4px;">$1</div>'
        );
        html = html.replace(/^\s*\-\s+(.+)$/gm, "• $1");
        html = html.replace(/^\s*(\d+)\.\s+(.+)$/gm, '<strong style="color:#38bdf8;">$1.</strong> $2');
        html = html.replace(/<\/div>\n/g, "</div>");
        html = html.replace(/\n/g, "<br/>");
        return html;
    }

    function redrawActiveLabCharts() {
        if (!state.currentSim) return;
        const showOverlay = $("chk-flight-overlay") ? $("chk-flight-overlay").checked : true;
        window.AltarCharts.drawFlammabilityMap(
            "chart-flammability",
            state.currentSim.flammability_map,
            state.lang,
            state.currentSim.flight_validation,
            showOverlay
        );
        window.AltarCharts.drawMultiSensorChart(
            "chart-multisensor",
            state.currentSim.sensor_timeseries,
            state.lang,
            state.currentSim.flight_validation,
            showOverlay
        );
    }

    // =========================================================================
    // TAB & 3D VIEWPORT SWITCHING
    // =========================================================================
    function setLabViewportMode(mode) {
        const cleanMode = mode === "spacecraft" ? "spacecraft" : "chamber";
        const prevMode = state.viewportMode;
        state.viewportMode = cleanMode;
        const chGroup = $("chamber-stage-group");
        const scStage = $("spacecraft-3d-stage");
        const bCh = $("btn-vp-chamber");
        const bSc = $("btn-vp-spacecraft");
        const orionSecBar = $("orion-section-bar");

        if (cleanMode === "chamber") {
            if (chGroup) chGroup.style.display = "block";
            if (scStage) scStage.classList.remove("active");
            if (orionSecBar) orionSecBar.style.display = "none";
            if (state.spacecraftStudio) {
                state.spacecraftStudio.setActive(false);
            }
            if (bCh) bCh.classList.add("active");
            if (bSc) bSc.classList.remove("active");
            setTimeout(() => {
                if (state.chamber3D) state.chamber3D.resize();
            }, 30);
            if (prevMode !== "chamber") {
                scheduleSimUpdate();
            }
        } else {
            if (chGroup) chGroup.style.display = "none";
            if (scStage) scStage.classList.add("active");
            if (orionSecBar) orionSecBar.style.display = "inline-flex";
            if (state.spacecraftStudio) {
                state.spacecraftStudio.setActive(true);
                if (state.currentSim) {
                    state.spacecraftStudio.syncFromSimulation(state.currentSim);
                }
            }
            if (bCh) bCh.classList.remove("active");
            if (bSc) bSc.classList.add("active");
            if (prevMode === "chamber") {
                scheduleSimUpdate();
            }
        }
    }

    function switchTab(tabId) {
        document.querySelectorAll(".nav-tab").forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.tab === tabId);
        });
        document.querySelectorAll(".tab-section").forEach((sec) => {
            sec.classList.toggle("active", sec.id === tabId);
        });

        if (tabId === "tab-lab") {
            setTimeout(() => {
                if (state.chamber3D) state.chamber3D.resize();
                if (state.spacecraftStudio && state.viewportMode !== "chamber") {
                    state.spacecraftStudio.resize();
                }
                redrawActiveLabCharts();
            }, 40);
        } else if (tabId === "tab-rank") {
            refreshRankingTable();
        }
    }

    // =========================================================================
    // SIMULATION, 3D WEBGL, PARTIAL GRAVITY & EQUATION TABLE UPDATES
    // =========================================================================
    function syncCustomMaterialBox() {
        const box = $("custom-material-box");
        const fuelSel = $("inp-fuel");
        if (!box || !fuelSel) return;
        box.style.display = fuelSel.value === "custom_material" ? "block" : "none";
    }

    function setFlowDirectionUI(dir) {
        const clean = dir === "concurrent" ? "concurrent" : "opposed";
        state.flowDirection = clean;
        const bOpp = $("btn-flow-opposed");
        const bCon = $("btn-flow-concurrent");
        if (bOpp) bOpp.classList.toggle("active", clean === "opposed");
        if (bCon) bCon.classList.toggle("active", clean === "concurrent");
    }

    function getSimParamsFromUI() {
        const fuelVal = $("inp-fuel").value;
        const base = {
            fuel_id: fuelVal,
            gravity_g: parseFloat($("inp-gravity").value),
            oxygen_pct: parseFloat($("inp-oxygen").value),
            pressure_psia: parseFloat($("inp-pressure").value),
            airflow_cms: parseFloat($("inp-airflow").value),
            droplet_d0_mm: parseFloat($("inp-droplet").value),
            diluent: $("inp-diluent").value,
            flow_direction: state.flowDirection || "opposed",
            habitat_id: $("sel-habitat-volume") ? $("sel-habitat-volume").value : "iss_module",
            crew_response_s: $("sel-crew-response") ? parseFloat($("sel-crew-response").value) : 30.0,
        };
        if (fuelVal === "custom_material") {
            const rawName = $("inp-custom-mat-name") ? $("inp-custom-mat-name").value.trim() : "";
            base.custom_material_name = rawName || "PEEK";
            const rawRho = $("inp-custom-rho") ? parseFloat($("inp-custom-rho").value) : NaN;
            const rawLambda = $("inp-custom-lambda") ? parseFloat($("inp-custom-lambda").value) : NaN;
            if (Number.isFinite(rawRho) && rawRho > 0) {
                base.custom_density_kg_m3 = rawRho;
            }
            if (Number.isFinite(rawLambda) && rawLambda > 0) {
                base.custom_conductivity_w_mk = rawLambda;
            }
        }
        if (state.spacecraftStudio && state.viewportMode !== "chamber") {
            Object.assign(base, state.spacecraftStudio.getSimulationOverrides());
        }
        return base;
    }

    function applyParamsToSliders(p) {
        if (!p) return;
        if (p.custom_material_name) {
            if ($("inp-custom-mat-name")) $("inp-custom-mat-name").value = p.custom_material_name;
            if ($("inp-custom-rho") && p.custom_density_kg_m3 !== undefined) {
                $("inp-custom-rho").value = p.custom_density_kg_m3 || "";
            }
            if ($("inp-custom-lambda") && p.custom_conductivity_w_mk !== undefined) {
                $("inp-custom-lambda").value = p.custom_conductivity_w_mk || "";
            }
            if (Array.from($("inp-fuel").options).some((o) => o.value === "custom_material")) {
                $("inp-fuel").value = "custom_material";
            }
        } else if (p.fuel_id && Array.from($("inp-fuel").options).some((o) => o.value === p.fuel_id)) {
            $("inp-fuel").value = p.fuel_id;
        }
        syncCustomMaterialBox();
        if (p.flow_direction) {
            setFlowDirectionUI(p.flow_direction);
        }
        if (p.gravity_g !== undefined) $("inp-gravity").value = p.gravity_g;
        if (p.oxygen_pct !== undefined) $("inp-oxygen").value = p.oxygen_pct;
        if (p.pressure_psia !== undefined) $("inp-pressure").value = p.pressure_psia;
        if (p.airflow_cms !== undefined) $("inp-airflow").value = p.airflow_cms;
        if (p.droplet_d0_mm !== undefined) $("inp-droplet").value = p.droplet_d0_mm;
        if (p.diluent) $("inp-diluent").value = p.diluent;
        if (p.habitat_id && $("sel-habitat-volume")) {
            $("sel-habitat-volume").value = p.habitat_id;
        } else if ($("sel-habitat-volume") && p.pressure_psia !== undefined && p.oxygen_pct !== undefined) {
            if (p.pressure_psia <= 5.2 && p.oxygen_pct >= 80) {
                $("sel-habitat-volume").value = "eva_suit";
            } else if (p.pressure_psia <= 11.2 && p.oxygen_pct >= 28) {
                $("sel-habitat-volume").value =
                    p.gravity_g >= 0.3 ? "mars_hab" : p.gravity_g >= 0.1 ? "lunar_rover" : "lunar_hab";
            } else {
                $("sel-habitat-volume").value = "iss_module";
            }
        }
        syncSliderLabels();
    }

    function syncSliderLabels() {
        $("val-gravity").textContent = `${parseFloat($("inp-gravity").value).toFixed(2)} G`;
        $("val-oxygen").textContent = `${parseFloat($("inp-oxygen").value).toFixed(1)}%`;
        $("val-pressure").textContent = `${parseFloat($("inp-pressure").value).toFixed(1)} psia`;
        $("val-airflow").textContent = `${parseFloat($("inp-airflow").value).toFixed(1)} cm/s`;
        $("val-droplet").textContent = `${parseFloat($("inp-droplet").value).toFixed(1)} mm`;
    }

    function applySimulationStateEverywhere(simData, sourceLabel) {
        if (!simData) return;
        state.currentSim = simData;
        if (sourceLabel) {
            state.activeSourceLabel = normalizeSourceLabelForLang(sourceLabel);
        } else {
            state.activeSourceLabel = normalizeSourceLabelForLang(state.activeSourceLabel);
        }
        renderTelemetryAndFormulaTables(simData);
        if (state.chamber3D) {
            state.chamber3D.updateFromSimulation(simData);
        }
        if (state.spacecraftStudio) {
            state.spacecraftStudio.syncFromSimulation(simData);
        }
        if (state.sonifier) {
            state.sonifier.updateTelemetry(simData.telemetry);
        }
        clearTimeout(state.rankDebounceTimer);
        state.rankDebounceTimer = setTimeout(refreshRankingTable, 160);
    }

    async function runSimulationUpdate(sourceLabel) {
        syncSliderLabels();
        const params = getSimParamsFromUI();
        try {
            const res = await apiFetch("/api/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(params),
            });
            const data = await res.json();
            applySimulationStateEverywhere(data, sourceLabel || "Combustion Chamber");
        } catch (err) {
            console.error("Simulation API error:", err);
        }
    }

    function scheduleSimUpdate() {
        syncSliderLabels();
        clearTimeout(state.simDebounceTimer);
        state.simDebounceTimer = setTimeout(() => {
            runSimulationUpdate("Combustion Chamber");
        }, 45);
    }

    function renderCabinTimeline(tl) {
        if (!tl) return;
        const badgeEl = $("cabin-severity-badge");
        const sumEl = $("cabin-timeline-summary");
        const gridEl = $("cabin-milestones-grid");
        if (!badgeEl || !sumEl || !gridEl) return;

        badgeEl.textContent = tl.badge_en || tl.badge_tr || "";
        badgeEl.style.color =
            tl.severity === "CRITICAL" ? "#fca5a5" : tl.severity === "WARNING" ? "#fcd34d" : "#6ee7b7";
        badgeEl.style.borderColor =
            tl.severity === "CRITICAL" ? "rgba(239,68,68,0.5)" : tl.severity === "WARNING" ? "rgba(245,158,11,0.5)" : "rgba(16,185,129,0.5)";

        sumEl.innerHTML = renderSafeMarkdown(tl.summary_en || tl.summary_tr || "");
        gridEl.innerHTML = "";
        (tl.milestones || []).forEach((m) => {
            const div = document.createElement("div");
            div.className = `milestone-card ${m.state || "ok"}`;
            const title = m.title_en || m.title_tr || "";
            const det = m.detail_en || m.detail_tr || "";
            div.innerHTML = `
                <div style="font-weight:700; color:#f8fafc; margin-bottom:4px;">${escapeHtml(title)}</div>
                <div style="color:#cbd5e1;">${escapeHtml(det)}</div>
            `;
            gridEl.appendChild(div);
        });
    }

    function renderMissionCertificationBar(sim) {
        const pillsBox = $("mission-cert-pills");
        const matLbl = $("mission-cert-mat-lbl");
        if (!pillsBox || !sim || !Array.isArray(sim.mission_certification)) return;
        const inp = sim.inputs || {};
        if (matLbl) {
            const mName = inp.fuel_name_en || inp.fuel_name_tr || inp.fuel_id;
            matLbl.textContent = `${mName} • NASA-STD-6001B`;
        }

        pillsBox.innerHTML = "";
        sim.mission_certification.forEach((ph) => {
            const btn = document.createElement("button");
            btn.type = "button";
            const clsStatus =
                ph.status === "PASS"
                    ? "cert-pass"
                    : ph.status === "CAUTION" || ph.status === "CONDITIONAL"
                    ? "cert-cond"
                    : "cert-fail";
            const isMatchingAtm =
                Math.abs((inp.gravity_g || 0) - ph.gravity_g) < 0.03 &&
                Math.abs((inp.oxygen_pct || 21) - ph.oxygen_pct) < 1.6 &&
                Math.abs((inp.pressure_psia || 14.7) - ph.pressure_psia) < 1.2;
            btn.className = `mission-cert-pill ${clsStatus}${isMatchingAtm ? " active-phase" : ""}`;
            const labelTxt = ph.label_en || ph.label_tr || "";
            const stTxt = ph.status_en || ph.status_tr || "";
            btn.title = `${labelTxt}: O₂ ${ph.oxygen_pct}% @ ${ph.pressure_psia} psia | MOC ${ph.moc_pct}% O₂`;
            btn.innerHTML = `<span>${escapeHtml(labelTxt)}</span><span class="cert-status-tag">${escapeHtml(stTxt)}</span>`;
            btn.addEventListener("click", () => {
                state.activeCertPhaseId = ph.phase_id;
                $("inp-gravity").value = ph.gravity_g;
                $("inp-oxygen").value = ph.oxygen_pct;
                $("inp-pressure").value = ph.pressure_psia;
                $("inp-airflow").value = ph.airflow_cms;
                if ($("sel-habitat-volume") && ph.habitat_id) {
                    const mapHab = ph.habitat_id === "orion_gateway" ? "lunar_hab" : ph.habitat_id;
                    if (Array.from($("sel-habitat-volume").options).some((o) => o.value === mapHab)) {
                        $("sel-habitat-volume").value = mapHab;
                    }
                }
                syncSliderLabels();
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                runSimulationUpdate(labelTxt);
            });
            pillsBox.appendChild(btn);
        });
    }

    function renderTelemetryAndFormulaTables(sim) {
        const tel = sim.telemetry;
        const call = sim.callouts;
        const unc = sim.uncertainty_bounds || {};

        $("tel-temp").textContent = `${tel.flame_temp_k.toFixed(0)} K`;
        const tempSigmaTxt = unc.temp_sigma_k ? ` • ±${Math.round(unc.temp_sigma_k)} K` : "";
        $("tel-temp-c").textContent = `${tel.flame_temp_c.toFixed(0)} °C${tempSigmaTxt}`;
        $("tel-moc").textContent = `${tel.moc_pct}%`;
        const po2Psia = tel.o2_partial_psia !== undefined ? tel.o2_partial_psia : tel.po2_psia;
        const po2Kpa = tel.o2_partial_kpa !== undefined ? tel.o2_partial_kpa : tel.po2_kpa;
        $("tel-po2").textContent = `P_O₂: ${po2Psia} psia (${po2Kpa} kPa)`;
        $("tel-kburn").textContent = `${tel.burning_rate_k_mm2_s} mm²/s`;
        const isSteadyGas = sim.inputs && sim.inputs.fuel_phase === "gas" && !tel.extinguished;
        $("tel-lifetime").textContent = isSteadyGas
            ? "Steady Gas Feed (D = D₀)"
            : tel.burn_lifetime_s > 0
            ? `Burn Life: ~${tel.burn_lifetime_s} s`
            : "Extinguished";
        $("tel-spread").textContent = `${tel.flame_spread_mm_s} mm/s`;
        const rfRd = tel.standoff_ratio_rf_rd !== undefined ? tel.standoff_ratio_rf_rd : tel.standoff_ratio;
        $("tel-radius").textContent = `B_oq: ${tel.spalding_b_number} • Rf/Rd: ${rfRd}`;
        $("tel-radloss").textContent = `${(tel.radiative_loss_fraction * 100).toFixed(1)}%`;
        $("tel-flux").textContent = `Heat Flux: ${tel.heat_flux_kw_m2} kW/m²`;
        $("tel-co").textContent = `${tel.co_ppm} ppm`;
        $("tel-soot").textContent = `Soot: ${tel.soot_index} • Sh: ${tel.sherwood_number} • Da: ${tel.damkohler_number}`;

        $("tel-risk-score").textContent = `${tel.risk_score} / 100`;
        $("tel-risk-bar").style.width = `${tel.risk_score}%`;
        $("tel-risk-score").style.color =
            tel.risk_score >= 70 ? "#f87171" : tel.risk_score >= 40 ? "#fcd34d" : "#6ee7b7";
        const riskDriverEl = $("tel-risk-driver");
        if (riskDriverEl) {
            const drv = tel.risk_driver_en || tel.risk_driver_tr || "";
            riskDriverEl.textContent = drv;
            riskDriverEl.style.display = drv ? "block" : "none";
        }

        if ($("flight-val-badge") && sim.flight_validation) {
            $("flight-val-badge").textContent = sim.flight_validation.benchmark_en || sim.flight_validation.benchmark_tr || "";
        }
        if ($("settings-flight-val-spec") && sim.flight_validation) {
            $("settings-flight-val-spec").textContent = `R² = ${sim.flight_validation.r_squared} • RMSE = ${sim.flight_validation.rmse}`;
        }

        const badgeEl = $("hud-regime-badge");
        badgeEl.textContent = call.badge_en || call.badge_tr || "";
        badgeEl.className = "regime-pill";
        const wrapEl = $("chamber-viewport-wrap");
        wrapEl.classList.remove("uv-mode");

        if (tel.cool_flame_active) {
            badgeEl.classList.add("cool-flame");
            wrapEl.classList.add("uv-mode");
        } else if (tel.extinguished) {
            badgeEl.classList.add("extinguished");
        }

        $("hud-callout-summary").textContent = call.summary_en || call.summary_tr || "";
        $("formula-active-source-badge").textContent = `Source: ${state.activeSourceLabel}`;

        const analogBanner = $("analog-material-banner");
        if (analogBanner) {
            const amInfo = sim.analog_match_info;
            if (amInfo && amInfo.show_banner) {
                analogBanner.innerHTML = renderSafeMarkdown(amInfo.en || amInfo.tr || "");
                analogBanner.style.display = "block";
            } else {
                analogBanner.style.display = "none";
            }
        }

        const pgBanner = $("partial-g-banner");
        if (pgBanner) {
            const pgInfo = sim.partial_gravity_info;
            if (pgInfo && pgInfo.show_banner) {
                pgBanner.innerHTML = renderSafeMarkdown(pgInfo.en || pgInfo.tr || "");
                pgBanner.style.display = "block";
            } else {
                pgBanner.style.display = "none";
            }
        }

        const ftBody = $("formula-results-tbody");
        if (ftBody) {
            ftBody.innerHTML = "";
            (sim.formula_table || []).forEach((row) => {
                const tr = document.createElement("tr");
                const name = row.law_en || row.parameter_en || row.law_tr || row.parameter_tr || "";
                const status = row.status_en || row.status || row.status_tr || "";
                tr.innerHTML = `
                    <td><strong style="color:#f8fafc;">${escapeHtml(name)}</strong></td>
                    <td><span class="formula-eq-code">${escapeHtml(row.equation)}</span></td>
                    <td style="font-family:Consolas,monospace; font-weight:700; color:#fcd34d;">${escapeHtml(row.value)}</td>
                    <td><span class="preset-badge">${escapeHtml(status)}</span></td>
                `;
                ftBody.appendChild(tr);
            });
        }

        const liveAiBox = $("live-formula-ai-box");
        if (liveAiBox && sim.instant_ai_summary) {
            const rawSummary = sim.instant_ai_summary.en || sim.instant_ai_summary.tr || "";
            const mediaBanner = state.attachedMediaName
                ? `<div style="margin-bottom:8px; padding:5px 9px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.35); border-radius:6px; font-size:11.8px; color:#6ee7b7;">Active File: <strong>${escapeHtml(state.attachedMediaName)}</strong></div>`
                : "";
            liveAiBox.innerHTML = mediaBanner + renderSafeMarkdown(rawSummary);
        }

        if (sim.scenario_timeline) {
            renderCabinTimeline(sim.scenario_timeline);
        }
        renderMissionCertificationBar(sim);
        renderEarthTransfers();
        renderAudienceBanner();
        redrawActiveLabCharts();
    }

    // =========================================================================
    // FILE BUNDLE (.CSV/.JSON/.PDF/.TXT) & FLAME IMAGERY (.PNG/.JPG) INGESTION
    // =========================================================================
    function activateUploadedPhase(ph, jumpToLab) {
        if (!ph || !ph.sim_params) return;
        applyParamsToSliders(ph.sim_params);
        if (state.chamber3D) state.chamber3D.reigniteDroplet();
        const phTag = `${state.attachedMediaName} (${ph.short_en || "Phase " + ph.index})`;
        runSimulationUpdate(phTag);
        refreshRankingTable();
        if (jumpToLab) {
            switchTab("tab-lab");
        }
        showToast(`${ph.short_en || "Phase " + ph.index} loaded into 3D Chamber (${ph.flame_temp_k} K).`);
    }

    function renderUploadedMediaUI() {
        if (!state.attachedMediaName) return;

        if ($("copilot-live-context-tag")) {
            $("copilot-live-context-tag").textContent = `Active File: ${state.attachedMediaName} + 3D Chamber`;
        }

        const phases = state.attachedMediaPhases || [];
        const makePhasePillsHtml = (prefix) => {
            if (phases.length <= 1) return "";
            const btns = phases
                .map((p) => {
                    const bTxt = p.short_en || `Phase ${p.index}`;
                    const tip = `${p.desc || bTxt} (${p.flame_temp_k} K)`;
                    return `<button type="button" class="btn-secondary ${prefix}-phase-btn" data-pidx="${p.index}" title="${escapeHtml(tip)}" style="padding:2px 7px; font-size:10.8px;">${escapeHtml(bTxt)}</button>`;
                })
                .join("");
            return `<div style="margin-top:6px; display:flex; gap:5px; flex-wrap:wrap; align-items:center;"><span style="font-size:11px; color:#94a3b8;">3D Phase:</span>${btns}</div>`;
        };

        const previewBox = $("media-analysis-result-box");
        if (previewBox && state.attachedMediaSummary) {
            const thumbHtml = state.attachedImageB64
                ? `<img src="${state.attachedImageB64}" alt="Flame Preview" />`
                : "";
            previewBox.innerHTML = `
                <div class="media-preview-card">
                    ${thumbHtml}
                    <div style="flex:1; font-size:12px;">
                        <div>${renderSafeMarkdown(state.attachedMediaSummary)}</div>
                        ${makePhasePillsHtml("prev")}
                        <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
                            <button class="btn-primary" id="btn-preview-goto-3d" style="padding:4px 10px; font-size:11.5px;">View in 3D</button>
                            <button class="btn-secondary" id="btn-preview-ask-ai" style="padding:4px 10px; font-size:11.5px;">Detailed Analysis</button>
                        </div>
                    </div>
                </div>
            `;
            $("btn-preview-goto-3d").addEventListener("click", () => switchTab("tab-lab"));
            $("btn-preview-ask-ai").addEventListener("click", () => {
                switchTab("tab-copilot");
                sendChatMessage(
                    `Analyze my uploaded '${state.attachedMediaName}' data via governing combustion laws (d²-law, Spalding B_oq, Sherwood Sh, MOC) and rank matching NASA PSI experiments.`
                );
            });
            previewBox.querySelectorAll(".prev-phase-btn").forEach((btn) => {
                btn.addEventListener("click", () => {
                    const idx = parseInt(btn.getAttribute("data-pidx"), 10);
                    const found = phases.find((x) => x.index === idx);
                    if (found) activateUploadedPhase(found, true);
                });
            });
        }

        const chatSt = $("chat-image-status");
        if (chatSt) {
            chatSt.innerHTML = `<div><strong>${escapeHtml(state.attachedMediaName)}</strong> <button class="btn-secondary" id="btn-clear-chat-media" style="padding:1px 6px; font-size:10.5px; margin-left:5px;">Clear</button></div>${makePhasePillsHtml("chat")}`;
            const clr = $("btn-clear-chat-media");
            if (clr) {
                clr.addEventListener("click", () => {
                    state.attachedImageB64 = null;
                    state.attachedMediaSummary = "";
                    state.attachedMediaSummaryTr = "";
                    state.attachedMediaSummaryEn = "";
                    state.attachedMediaPhases = [];
                    state.attachedMediaName = "";
                    chatSt.textContent = "";
                    $("inp-chat-image").value = "";
                    $("copilot-live-context-tag").textContent = tStr("copilot_ctx_tag");
                });
            }
            chatSt.querySelectorAll(".chat-phase-btn").forEach((btn) => {
                btn.addEventListener("click", () => {
                    const idx = parseInt(btn.getAttribute("data-pidx"), 10);
                    const found = phases.find((x) => x.index === idx);
                    if (found) activateUploadedPhase(found, false);
                });
            });
        }
    }

    function renderSearchPickerUI(data) {
        const previewBox = $("media-analysis-result-box");
        if (!previewBox || !data || !Array.isArray(data.search_items)) return;
        const repo = data.repository || "PSI";
        const allItems = data.search_items;

        const headerTxt = `Search Page Detected (${allItems.length} NASA ${repo} Records) — Select an investigation to load into the 3D Chamber:`;
        const filterPh = "Filter by ID, acronym, fuel, or title (e.g., PSI-69, PSI-117, PSI-22, FLEX, Saffire)...";

        previewBox.innerHTML = `
            <div class="psi-search-picker">
                <div style="font-size:12.2px; font-weight:700; color:#7dd3fc; margin-bottom:7px;">
                    ${escapeHtml(headerTxt)}
                </div>
                ${allItems.length > 5 ? `<input type="text" class="nasa-input" id="psi-picker-filter-inp" placeholder="${escapeHtml(filterPh)}" style="margin-bottom:8px; padding:6px 10px; font-size:12px;" />` : ""}
                <div class="psi-picker-list" id="psi-picker-items-list"></div>
            </div>
        `;

        const listEl = $("psi-picker-items-list");
        const renderFiltered = (needle) => {
            const q = (needle || "").trim().toLowerCase();
            const filtered = q
                ? allItems.filter((it) =>
                      `${it.id || ""} ${it.acronym || ""} ${it.title || ""} ${it.table_file || ""} ${it.abstract || ""}`
                          .toLowerCase()
                          .includes(q)
                  )
                : allItems;

            listEl.innerHTML = "";
            if (filtered.length === 0) {
                listEl.innerHTML = `<div style="padding:8px; font-size:12px; color:#94a3b8;">No matching records.</div>`;
                return;
            }
            filtered.forEach((it) => {
                const row = document.createElement("div");
                row.className = "psi-picker-item";
                const phBadge =
                    it.phase_count > 1
                        ? `<span class="preset-badge" style="margin-left:5px;">${it.phase_count} Phases</span>`
                        : it.table_file
                        ? `<span class="preset-badge" style="margin-left:5px;">Exp. Table</span>`
                        : "";
                const cleanT = String(it.title || it.id || "").replace(new RegExp(`^${it.id}\\s*[—\\-]\\s*`, "i"), "");
                row.innerHTML = `
                    <div style="min-width:0; flex:1;">
                        <div style="display:flex; align-items:center; flex-wrap:wrap; gap:4px;">
                            <strong style="color:#38bdf8; font-size:12.2px;">${escapeHtml(it.id || "PSI")}</strong>
                            ${phBadge}
                        </div>
                        <div style="font-size:11.8px; color:#e2e8f0; margin-top:2px; line-height:1.35;">${escapeHtml(cleanT)}</div>
                    </div>
                    <button type="button" class="btn-primary psi-pick-load-btn" data-target-url="${escapeHtml(it.url || "")}" style="padding:4px 10px; font-size:11.3px; white-space:nowrap; flex-shrink:0;">
                        Load to 3D
                    </button>
                `;
                row.querySelector(".psi-pick-load-btn").addEventListener("click", () => {
                    if (it.url) {
                        $("inp-scrape-url").value = it.url;
                        executeUrlScrape(it.url);
                    }
                });
                listEl.appendChild(row);
            });
        };

        renderFiltered("");
        const fInp = $("psi-picker-filter-inp");
        if (fInp) {
            fInp.addEventListener("input", () => renderFiltered(fInp.value));
        }
    }

    async function executeUrlScrape(rawUrl) {
        const url = normalizeUserWebUrl(rawUrl);
        const btn = $("btn-scrape-url");
        const previewBox = $("media-analysis-result-box");

        if (!url) {
            showToast("Please enter a web link (https://...).");
            return;
        }
        if ($("inp-scrape-url") && $("inp-scrape-url").value.trim() !== url) {
            $("inp-scrape-url").value = url;
        }

        if (btn) {
            btn.disabled = true;
            btn.textContent = "Loading...";
        }
        setUrlScrapeStatus(
            "Connecting to NASA repository and parsing parameters...",
            "Connecting to NASA repository and parsing parameters...",
            "#7dd3fc"
        );

        try {
            const res = await apiFetch("/api/scrape-url", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });
            const data = await res.json();

            if (!data.ok) {
                state.lastSearchPickerData = null;
                const errMsg = data.error_en || data.error || "Web link could not be parsed.";
                setUrlScrapeStatus(errMsg, errMsg, "#fca5a5");
                if (previewBox) {
                    previewBox.innerHTML = `<div class="media-preview-card" style="border-color:rgba(248,113,113,0.45); color:#fecaca; font-size:12.2px;">${escapeHtml(errMsg)}</div>`;
                }
                showToast(errMsg);
                return;
            }

            if (data.mode === "search_results" && Array.isArray(data.search_items)) {
                state.lastSearchPickerData = data;
                renderSearchPickerUI(data);
                state.lastLiveNasaData = {
                    ok: true,
                    source_status: "live_online",
                    count: data.search_items.length,
                    items: data.search_items,
                };
                renderLiveNasaCards(state.lastLiveNasaData);
                const msgEn = `${data.search_items.length} investigations listed — select a record below to load into 3D.`;
                setUrlScrapeStatus(msgEn, msgEn, "#6ee7b7");
                showToast(msgEn);
                return;
            }

            state.lastSearchPickerData = null;
            state.attachedImageB64 = null;
            state.attachedMediaName = data.title || url;
            const sumEn = data.summary_en || data.summary_tr || `**Web (${url}):** ${data.title}\n${data.preview || ""}`;
            state.attachedMediaSummaryTr = sumEn;
            state.attachedMediaSummaryEn = sumEn;
            state.attachedMediaSummary = sumEn;
            state.attachedMediaPhases = data.phases || [];

            const shortTitle =
                state.attachedMediaName.length > 58
                    ? `${state.attachedMediaName.slice(0, 58)}...`
                    : state.attachedMediaName;

            if ($("chk-media-autosync").checked && data.extracted_sim_params) {
                applyParamsToSliders(data.extracted_sim_params);
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                const srcLbl = `Web (${shortTitle.slice(0, 36)})`;
                if (data.simulation) {
                    applySimulationStateEverywhere(data.simulation, srcLbl);
                } else {
                    await runSimulationUpdate(srcLbl);
                }
                refreshRankingTable();
            }

            renderUploadedMediaUI();
            const okEn = `'${shortTitle}' parsed and synced to the 3D Chamber.`;
            setUrlScrapeStatus(okEn, okEn, "#6ee7b7");
            showToast(okEn);
        } catch (err) {
            const netMsg = formatFriendlyError(err);
            setUrlScrapeStatus(netMsg, netMsg, "#fca5a5");
            showToast(netMsg);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = tStr("btn_scrape_url");
            }
        }
    }

    function extractVideoFrameFile(fileObj) {
        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(fileObj);
            const video = document.createElement("video");
            video.preload = "auto";
            video.muted = true;
            video.playsInline = true;
            video.src = url;

            let settled = false;
            const cleanup = () => {
                URL.revokeObjectURL(url);
                video.removeAttribute("src");
                video.load();
            };
            const timer = setTimeout(() => {
                if (!settled) {
                    settled = true;
                    cleanup();
                    reject(new Error("Video frame extraction timed out."));
                }
            }, 7000);

            video.onerror = () => {
                if (!settled) {
                    settled = true;
                    clearTimeout(timer);
                    cleanup();
                    reject(new Error("Unsupported video codec."));
                }
            };

            video.onloadedmetadata = async () => {
                try {
                    const dur = Number.isFinite(video.duration) && video.duration > 0 ? video.duration : 1.0;
                    const cw = Math.min(480, Math.max(96, video.videoWidth || 320));
                    const ch = Math.min(360, Math.max(72, video.videoHeight || 240));
                    const canvas = document.createElement("canvas");
                    canvas.width = cw;
                    canvas.height = ch;
                    const ctx = canvas.getContext("2d", { willReadFrequently: true });

                    const sampleFracs = [0.15, 0.38, 0.62, 0.85];
                    const lumas = [];
                    let bestBlob = null;
                    let bestScore = -1;

                    const seekAndCapture = (tSec) =>
                        new Promise((resSeek) => {
                            let done = false;
                            const onSeeked = () => {
                                if (done) return;
                                done = true;
                                video.removeEventListener("seeked", onSeeked);
                                ctx.drawImage(video, 0, 0, cw, ch);
                                const imgData = ctx.getImageData(0, 0, cw, ch).data;
                                let sumL = 0;
                                let brightCnt = 0;
                                const totalPx = cw * ch;
                                for (let i = 0; i < imgData.length; i += 16) {
                                    const r = imgData[i];
                                    const g = imgData[i + 1];
                                    const b = imgData[i + 2];
                                    const l = 0.299 * r + 0.587 * g + 0.114 * b;
                                    sumL += l;
                                    if (l > 42 || b > 65 || r > 80) brightCnt++;
                                }
                                const meanL = sumL / Math.max(1, totalPx / 4);
                                lumas.push(meanL);
                                const score = meanL + brightCnt * 0.05;
                                if (score > bestScore) {
                                    bestScore = score;
                                    canvas.toBlob((bl) => {
                                        if (bl) bestBlob = bl;
                                        resSeek();
                                    }, "image/png");
                                } else {
                                    resSeek();
                                }
                            };
                            video.addEventListener("seeked", onSeeked);
                            try {
                                video.currentTime = Math.min(Math.max(0.01, tSec), Math.max(0.02, dur - 0.02));
                            } catch (_) {
                                onSeeked();
                            }
                            setTimeout(onSeeked, 800);
                        });

                    for (let k = 0; k < sampleFracs.length; k++) {
                        await seekAndCapture(dur * sampleFracs[k]);
                    }

                    let flickerPct = 0.0;
                    if (lumas.length >= 2) {
                        const avgL = lumas.reduce((a, b) => a + b, 0) / lumas.length;
                        const maxDiff = Math.max(...lumas) - Math.min(...lumas);
                        flickerPct = Math.min(100, Math.round((maxDiff / Math.max(8.0, avgL)) * 1000) / 10);
                    }

                    if (!settled) {
                        settled = true;
                        clearTimeout(timer);
                        cleanup();
                        if (!bestBlob) {
                            reject(new Error("Could not extract video frame."));
                            return;
                        }
                        const stem = fileObj.name.replace(/\.[^.]+$/, "");
                        const frameFile = new File([bestBlob], `${stem}_frame.png`, { type: "image/png" });
                        resolve({
                            frameFile,
                            framesSampled: lumas.length,
                            flickerPct,
                        });
                    }
                } catch (ex) {
                    if (!settled) {
                        settled = true;
                        clearTimeout(timer);
                        cleanup();
                        reject(ex);
                    }
                }
            };
        });
    }

    async function ingestMediaBundle(fileList, syncTo3D, targetStatusElId) {
        const files = Array.from(fileList || []).filter(Boolean);
        if (files.length === 0) return;
        if (files.length === 1) {
            return ingestMediaFile(files[0], syncTo3D, targetStatusElId);
        }

        const statusEl = targetStatusElId ? $(targetStatusElId) : null;
        if (statusEl) {
            statusEl.style.color = "#7dd3fc";
            statusEl.textContent = `Merging and calibrating ${files.length} files...`;
        }
        showToast(`Processing ${files.length}-file NASA PSI bundle...`);

        const fd = new FormData();
        for (let i = 0; i < files.length; i++) {
            const f = files[i];
            const isVid = /\.(mp4|webm)$/i.test(f.name || "") || /^video\/(mp4|webm)/i.test(f.type || "");
            if (isVid) {
                try {
                    const vm = await extractVideoFrameFile(f);
                    fd.append("files", vm.frameFile);
                } catch (_) {
                    fd.append("files", f);
                }
            } else {
                fd.append("files", f);
            }
        }

        try {
            const res = await apiFetch("/api/ingest-bundle", { method: "POST", body: fd });
            const data = await res.json();
            if (!data.ok) {
                const errTxt = data.error || "Bundle analysis failed.";
                if (statusEl) {
                    statusEl.style.color = "#fca5a5";
                    statusEl.textContent = errTxt;
                }
                showToast(errTxt);
                return;
            }

            state.lastSearchPickerData = null;
            setUrlScrapeStatus(null, null, null);
            const sumEn = data.summary_en || data.summary_tr || "";
            state.attachedMediaSummaryTr = sumEn;
            state.attachedMediaSummaryEn = sumEn;
            state.attachedMediaName = data.filename || `${files.length} Files`;
            state.attachedMediaSummary = sumEn;
            state.attachedMediaPhases = data.phases || [];
            state.attachedImageB64 = data.image_base64 || null;

            if (syncTo3D && data.extracted_sim_params) {
                applyParamsToSliders(data.extracted_sim_params);
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                const srcTag = `Uploaded Bundle (${files.length} files)`;
                if (data.simulation) {
                    applySimulationStateEverywhere(data.simulation, srcTag);
                } else {
                    await runSimulationUpdate(srcTag);
                }
                refreshRankingTable();
            }

            const phaseEn = state.attachedMediaPhases.length > 1 ? `${state.attachedMediaPhases.length} phases` : "1 record";
            const cal = data.calibration || data.bundle_calibration || {};
            const r2Note = cal.r_squared !== undefined && cal.r_squared !== null ? ` • R²=${cal.r_squared}` : "";
            const shortEn = `${state.attachedMediaName} (${phaseEn}${r2Note})`;

            if (targetStatusElId) {
                setQuickMediaStatus(targetStatusElId, shortEn, shortEn, "#6ee7b7", state.attachedMediaName, true);
            }

            renderUploadedMediaUI();
            showToast(`${files.length} files merged and synced to 3D Chamber.`);
        } catch (err) {
            const friendlyMsg = formatFriendlyError(err);
            if (statusEl) {
                statusEl.style.color = "#fca5a5";
                statusEl.textContent = friendlyMsg;
            }
            showToast(friendlyMsg);
        }
    }

    function renderCustomEquationResult(data) {
        const box = $("custom-eq-result-box");
        if (!box || !data) return;
        if (!data.ok) {
            const errMsg = data.error_en || data.error || "Invalid equation";
            box.innerHTML = `<div style="padding:7px 10px; border-radius:6px; background:rgba(239,68,68,0.14); border:1px solid rgba(248,113,113,0.42); color:#fecaca; font-size:11.8px;">${escapeHtml(errMsg)}</div>`;
            return;
        }
        const diffVal = Number(data.relative_diff_pct ?? 0);
        const badgeColor = diffVal <= 12 ? "#6ee7b7" : diffVal <= 28 ? "#fcd34d" : "#fca5a5";
        const usedVars = Array.isArray(data.used_variables) && data.used_variables.length > 0
            ? data.used_variables.join(", ")
            : "-";
        const r2Str = data.r_squared !== null && data.r_squared !== undefined ? `R² = ${data.r_squared}` : "";
        const rmseStr = data.rmse !== null && data.rmse !== undefined ? `RMSE = ${data.rmse}` : "";
        const calBadge = [r2Str, rmseStr].filter(Boolean).join(" • ");

        box.innerHTML = `
            <div style="padding:8px 10px; border-radius:7px; background:rgba(15,23,42,0.78); border:1px solid rgba(56,189,248,0.35); font-size:11.8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:4px;">
                    <span style="color:#e2e8f0;">
                        <strong>Formula Output:</strong>
                        <code style="color:#38bdf8; font-weight:700;">${escapeHtml(String(data.evaluated_value))}</code>
                        <span style="color:#94a3b8; margin:0 4px;">|</span>
                        <strong>Solver Ref:</strong>
                        <code style="color:#fcd34d;">${escapeHtml(String(data.reference_value))}</code>
                    </span>
                    <span style="font-family:Consolas,monospace; font-weight:700; color:${badgeColor};">
                        Diff: ${escapeHtml(String(diffVal))}%${calBadge ? ` • ${escapeHtml(calBadge)}` : ""}
                    </span>
                </div>
                <div style="color:#94a3b8; font-size:11px;">
                    Active Variables: <code>${escapeHtml(usedVars)}</code>
                </div>
            </div>
        `;
    }

    async function evaluateCustomEquation() {
        const eqInp = $("inp-custom-eq");
        const targetSel = $("sel-custom-eq-target");
        if (!eqInp || !targetSel) return;
        const expression = eqInp.value.trim();
        if (!expression) {
            showToast("Enter an equation to verify.");
            return;
        }
        try {
            const res = await apiFetch("/api/evaluate-formula", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    expression,
                    target_metric: targetSel.value,
                    sim_params: getSimParamsFromUI(),
                }),
            });
            const data = await res.json();
            state.lastCustomEqData = data;
            state.lastCustomEqResult = data;
            state.lastCustomEquation = data;
            renderCustomEquationResult(data);
        } catch (err) {
            const friendly = formatFriendlyError(err);
            const errObj = { ok: false, error: friendly };
            state.lastCustomEqData = errObj;
            state.lastCustomEqResult = errObj;
            state.lastCustomEquation = errObj;
            renderCustomEquationResult(errObj);
        }
    }

    async function ingestMediaFile(fileObj, syncTo3D, targetStatusElId) {
        if (!fileObj) return;
        const statusEl = targetStatusElId ? $(targetStatusElId) : null;
        if (statusEl) {
            statusEl.style.color = "#7dd3fc";
            statusEl.textContent = `Analyzing '${fileObj.name}' and extracting parameters...`;
        }
        showToast(`Processing '${fileObj.name}'...`);

        const isVideoFile =
            /\.(mp4|webm)$/i.test(fileObj.name || "") || /^video\/(mp4|webm)/i.test(fileObj.type || "");
        let uploadTarget = fileObj;
        let videoMeta = null;
        if (isVideoFile) {
            try {
                videoMeta = await extractVideoFrameFile(fileObj);
                uploadTarget = videoMeta.frameFile;
            } catch (_vidErr) {
                const msg = "Could not decode video stream in browser; please upload MP4 (H.264), WebM, GIF, or PNG.";
                if (statusEl) {
                    statusEl.style.color = "#fca5a5";
                    statusEl.textContent = msg;
                }
                showToast(msg);
                return;
            }
        }

        const fd = new FormData();
        fd.append("file", uploadTarget);
        if (videoMeta) {
            fd.append("original_filename", fileObj.name);
            fd.append("video_flicker_pct", String(videoMeta.flickerPct));
        }

        try {
            const res = await apiFetch("/api/ingest-media", { method: "POST", body: fd });
            const data = await res.json();
            if (!data.ok) {
                if (statusEl) {
                    statusEl.style.color = "#fca5a5";
                    statusEl.textContent = `${data.error || "Error"}`;
                }
                showToast(`${data.error || "Failed"}`);
                return;
            }

            state.lastSearchPickerData = null;
            setUrlScrapeStatus(null, null, null);
            const videoSuffixEn = videoMeta
                ? `\n- **Video Frame Sampling:** \`${videoMeta.framesSampled} frames\` • Optical Flicker: \`${videoMeta.flickerPct}%\``
                : "";
            const pickedSummary = (data.summary_en || data.summary_tr || "") + videoSuffixEn;
            state.attachedMediaSummaryTr = pickedSummary;
            state.attachedMediaSummaryEn = pickedSummary;
            state.attachedMediaName = videoMeta ? fileObj.name : (data.filename || fileObj.name);
            state.attachedMediaSummary = pickedSummary;
            state.attachedMediaPhases = data.phases || [];
            if (data.media_type === "image" && data.image_base64) {
                state.attachedImageB64 = data.image_base64;
            } else {
                state.attachedImageB64 = null;
            }

            if (syncTo3D && data.extracted_sim_params) {
                applyParamsToSliders(data.extracted_sim_params);
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                const srcTag = `Uploaded (${state.attachedMediaName})`;
                if (data.simulation) {
                    applySimulationStateEverywhere(data.simulation, srcTag);
                } else {
                    await runSimulationUpdate(srcTag);
                }
                refreshRankingTable();
            }

            const regEn = data.metrics ? (data.metrics.detected_regime_en || data.metrics.detected_regime_tr || "") : "";
            const phaseEn = state.attachedMediaPhases.length > 1 ? `${state.attachedMediaPhases.length} phases` : "1 record";
            const shortEn =
                data.media_type === "image"
                    ? `${state.attachedMediaName} — ${regEn}`
                    : `${state.attachedMediaName} (${phaseEn}) — O₂:${data.extracted_sim_params.oxygen_pct}%, ${data.extracted_sim_params.airflow_cms} cm/s`;

            if (targetStatusElId) {
                setQuickMediaStatus(targetStatusElId, shortEn, shortEn, "#6ee7b7", state.attachedMediaName, false);
            }

            renderUploadedMediaUI();
            showToast(`'${state.attachedMediaName}' synced to 3D Chamber and Data Records.`);
        } catch (err) {
            const friendlyMsg = formatFriendlyError(err);
            if (statusEl) {
                statusEl.style.color = "#fca5a5";
                statusEl.textContent = friendlyMsg;
            }
            showToast(friendlyMsg);
        }
    }

    // =========================================================================
    // CONTINUOUS LIVE NASA STREAM ENGINE
    // =========================================================================
    function updateStreamHeaderAndUI(st) {
        if (!st) return;
        state.lastStreamStatus = st;
        state.streamEnabled = Boolean(st.enabled);
        const dot = $("header-stream-dot");
        const txt = $("header-stream-text");
        const badge = $("stream-state-badge");
        const btn = $("btn-stream-toggle");
        const panel = $("continuous-stream-panel");
        const meta = $("stream-meta-info");

        if (state.streamEnabled) {
            dot.style.background = "#10b981";
            dot.style.boxShadow = "0 0 8px #10b981";
            txt.textContent = `Stream Live (#${st.seq_id || 0})`;
            badge.textContent = `Active (${st.interval_sec} s)`;
            btn.textContent = tStr("btn_stream_stop");
            btn.className = "btn-danger";
            panel.classList.add("stream-panel-active");
        } else {
            dot.style.background = "#64748b";
            dot.style.boxShadow = "none";
            txt.textContent = "Stream: Idle";
            badge.textContent = "Idle (Ready)";
            btn.textContent = tStr("btn_stream_start");
            btn.className = "btn-primary";
            panel.classList.remove("stream-panel-active");
        }

        if (st.last_error) {
            meta.innerHTML = `<span style="color:#fca5a5;">(${escapeHtml(st.last_fetch_time)}): ${escapeHtml(st.last_error)}</span>`;
        } else if (st.last_fetch_time) {
            meta.textContent = `Last Poll: ${st.last_fetch_time} • Packets: ${st.seq_id} • Source: ${st.source.toUpperCase()}`;
        }

        if (st.seq_id && st.seq_id > state.lastStreamSeqId) {
            const isFirstBoot = state.lastStreamSeqId === 0 && !state.streamEnabled;
            state.lastStreamSeqId = st.seq_id;
            renderStreamEventsList(st.events || []);

            if (!isFirstBoot && $("chk-stream-autosync").checked && st.latest_sim_params) {
                const topEv = st.events && st.events[0] ? st.events[0] : null;
                const srcTag = topEv ? `Live Stream (${topEv.id})` : "Live Stream";
                if (topEv) {
                    state.attachedMediaName = `${topEv.id}: ${topEv.title.slice(0, 48)}`;
                    state.attachedMediaSummary = `**Live Stream (${topEv.id} • ${topEv.time}):** ${topEv.title}\n${topEv.summary}`;
                }
                applyParamsToSliders(st.latest_sim_params);
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                runSimulationUpdate(srcTag);
                showToast(`New NASA Packet (${topEv ? topEv.id : "#" + st.seq_id}) synced to 3D Chamber.`);
            }
        } else if (st.events && $("stream-events-box").children.length === 0 && st.events.length > 0) {
            renderStreamEventsList(st.events);
        }
    }

    function renderStreamEventsList(events) {
        const box = $("stream-events-box");
        if (!box) return;
        box.innerHTML = "";
        events.forEach((ev) => {
            const p = ev.extracted_sim_params || {};
            const div = document.createElement("div");
            div.className = "stream-event-item";
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:3px;">
                    <div>
                        <span class="preset-badge">#${ev.seq_id} • ${escapeHtml(ev.time)}</span>
                        <strong style="color:#38bdf8; margin-left:6px;">[${escapeHtml(ev.id)}] ${escapeHtml(ev.title)}</strong>
                    </div>
                    <span style="font-family:Consolas,monospace; font-size:11.5px; color:#fcd34d;">
                        ${escapeHtml(p.fuel_id || "n_heptane")} • ${p.oxygen_pct ?? 21}% O₂ • ${p.pressure_psia ?? 14.7} psia • ${p.airflow_cms ?? 2} cm/s
                    </span>
                </div>
                <div style="color:#cbd5e1; margin-bottom:6px;">${escapeHtml(ev.summary)}</div>
                <div style="display:flex; gap:10px; align-items:center;">
                    ${ev.url ? `<a class="ext-link" href="${escapeHtml(ev.url)}" target="_blank" rel="noopener" style="font-size:11.5px;">Open Source</a>` : ""}
                    <button class="btn-secondary stream-ev-sync-btn" style="padding:2px 8px; font-size:11px;">Apply &amp; Analyze</button>
                </div>
            `;
            div.querySelector(".stream-ev-sync-btn").addEventListener("click", () => {
                applyParamsToSliders(p);
                state.attachedMediaName = `${ev.id} (${ev.title.slice(0, 45)})`;
                state.attachedMediaSummary = `**[${ev.id}]:** ${ev.title}\n${ev.summary}`;
                runSimulationUpdate(`Live (${ev.id})`);
                switchTab("tab-copilot");
                sendChatMessage(
                    `Analyze live web stream record [${ev.id}] '${ev.title}', its extracted parameters, and current 3D equation telemetry.`
                );
            });
            box.appendChild(div);
        });
    }

    async function configureContinuousStream(enableFlag, immediateFlag) {
        const src = $("sel-stream-source").value;
        const target = $("inp-stream-target").value.trim() || "auto";
        const intervalSec = parseInt($("sel-stream-interval").value, 10) || 25;
        const autoSync = $("chk-stream-autosync").checked;

        try {
            const res = await apiFetch("/api/stream/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    enabled: enableFlag,
                    source: src,
                    query_or_url: target,
                    interval_sec: intervalSec,
                    auto_sync_sim: autoSync,
                    trigger_immediate: Boolean(immediateFlag),
                }),
            });
            const st = await res.json();
            updateStreamHeaderAndUI(st);
            if (enableFlag || immediateFlag) {
                setTimeout(pollStreamStatusOnce, 1400);
                setTimeout(pollStreamStatusOnce, 3200);
            }
        } catch (err) {
            showToast(formatFriendlyError(err));
        }
    }

    async function pollStreamStatusOnce() {
        try {
            const res = await apiFetch("/api/stream/status");
            const st = await res.json();
            updateStreamHeaderAndUI(st);
        } catch (_) {}
    }

    // =========================================================================
    // TAB 2: EXPERIMENT RANKING, HARDWARE FILTER, VARIATIONS & COMPARISON
    // =========================================================================
    async function refreshRankingTable() {
        const params = getSimParamsFromUI();
        const query = $("inp-rank-query") ? $("inp-rank-query").value.trim() : "";
        try {
            const res = await apiFetch("/api/rank", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    mission_params: params,
                    query,
                    hardware_filter: state.activeHardwareFilter,
                }),
            });
            const data = await res.json();
            state.rankedList = data.ranked_experiments || [];
            renderRankingRows();
            const activeIntra =
                state.rankedList.find((x) => x.exp_id === state.activeIntraExpId) || state.rankedList[0];
            if (activeIntra) {
                renderIntraRunsForExperiment(activeIntra);
            }
            runComparisonUpdate();
        } catch (err) {
            console.error("Ranking error:", err);
        }
    }

    function renderRankingRows() {
        const tbody = $("ranking-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        state.rankedList.forEach((exp) => {
            const tr = document.createElement("tr");
            const checked = state.selectedCompareIds.has(exp.exp_id) ? "checked" : "";
            const scoreCls =
                exp.priority_score >= 72 ? "score-high" : exp.priority_score >= 52 ? "score-med" : "score-low";
            const title = exp.title_en || exp.title || "";
            const progLabel = exp.program_en || exp.program || "";
            const finding = exp.key_finding_en || exp.key_finding_tr || "";
            const insight = exp.safety_insight_en || exp.safety_insight_tr || "";
            const geom = exp.sample_geometry_en || exp.material || "";
            const sens = exp.sensors_en || exp.sensors_tr || "";

            const scaleLbl = exp.scale_class_en || exp.scale_class_tr || "";
            const hrrpuaVal = exp.hrrpua_kw_m2 !== undefined ? exp.hrrpua_kw_m2 : exp.predicted_hrrpua_kw_m2;
            const dynBadge = exp.is_dynamic_upload
                ? `<span class="preset-badge" style="margin-top:3px; margin-left:4px; display:inline-block; background:rgba(16,185,129,0.18); border-color:rgba(16,185,129,0.48); color:#6ee7b7;">New Data</span>`
                : "";
            const ntrsLinkHtml =
                exp.ntrs_id === "USER-DATA" || exp.ntrs_id === "USER-UPLOAD" || !exp.ntrs_url
                    ? `<span style="font-size:11px; color:#6ee7b7; font-weight:600;">Uploaded File</span>`
                    : `<a class="ext-link" href="${escapeHtml(exp.ntrs_url)}" target="_blank" rel="noopener">NTRS ${escapeHtml(exp.ntrs_id)}</a>`;

            tr.innerHTML = `
                <td><input type="checkbox" class="cmp-check" data-id="${escapeHtml(exp.exp_id)}" ${checked} /></td>
                <td><strong>#${exp.rank}</strong></td>
                <td>
                    <strong style="color:#38bdf8;">${escapeHtml(progLabel)}</strong><br/>
                    <span class="preset-badge" style="margin-top:3px; display:inline-block;">${escapeHtml(exp.hardware_group || "CIR")}</span>${dynBadge}<br/>
                    <span style="font-size:10.8px; color:#94a3b8;">${escapeHtml(exp.exp_id)} (${exp.year})</span>
                    ${scaleLbl ? `<div style="font-size:10.4px; color:#93c5fd; margin-top:2px;">${escapeHtml(scaleLbl)}</div>` : ""}
                </td>
                <td>
                    <div style="font-weight:700; color:#f8fafc; margin-bottom:4px;">${escapeHtml(title)}</div>
                    <div style="font-size:12.4px; color:#cbd5e1;">${escapeHtml(finding)}</div>
                    <div class="meta-detail-line"><strong>Sample / Burner:</strong> ${escapeHtml(geom)}</div>
                    ${sens ? `<div class="meta-detail-line" style="color:#c4b5fd;"><strong>Sensors:</strong> ${escapeHtml(sens)}</div>` : ""}
                    <div style="font-size:12px; color:#6ee7b7; margin-top:4px;">${escapeHtml(insight)}</div>
                </td>
                <td style="font-family:Consolas,monospace; font-size:12px;">
                    O₂: ${exp.oxygen_pct}% | ${exp.pressure_psia} psia<br/>
                    Flow: ${exp.airflow_cms} cm/s<br/>
                    MOC: <strong>${exp.moc_measured_pct}%</strong>
                    ${hrrpuaVal !== undefined ? `<br/><span style="color:#fcd34d;">HRRPUA: ${hrrpuaVal} kW/m²</span>` : ""}
                </td>
                <td>
                    <span class="score-badge ${scoreCls}">${exp.priority_score}</span>
                    <div style="font-size:11px; color:#94a3b8; margin-top:4px;">Risk: ${exp.mission_hazard_score}/100</div>
                </td>
                <td>
                    ${ntrsLinkHtml}<br/>
                    <button class="btn-secondary load-exp-sim-btn" data-id="${escapeHtml(exp.exp_id)}" style="margin-top:5px; padding:3px 8px; font-size:11px; width:100%; justify-content:center;">
                        Load in 3D
                    </button>
                    <button class="btn-secondary show-intra-runs-btn" data-id="${escapeHtml(exp.exp_id)}" style="margin-top:4px; padding:3px 8px; font-size:11px; width:100%; justify-content:center; border-color:rgba(56,189,248,0.45); color:#7dd3fc;">
                        Test Variations
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll(".cmp-check").forEach((chk) => {
            chk.addEventListener("change", (e) => {
                const id = e.target.dataset.id;
                if (e.target.checked) {
                    if (state.selectedCompareIds.size >= 4) {
                        e.target.checked = false;
                        showToast("Select up to 4 experiments at once.");
                        return;
                    }
                    state.selectedCompareIds.add(id);
                } else {
                    state.selectedCompareIds.delete(id);
                }
                runComparisonUpdate();
            });
        });

        tbody.querySelectorAll(".load-exp-sim-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                const exp = state.rankedList.find((x) => x.exp_id === btn.dataset.id);
                if (exp) {
                    applyParamsToSliders({
                        fuel_id: exp.fuel_id,
                        gravity_g: exp.gravity_g,
                        oxygen_pct: exp.oxygen_pct,
                        pressure_psia: exp.pressure_psia,
                        airflow_cms: exp.airflow_cms,
                        flow_direction: exp.flow_regime === "concurrent" ? "concurrent" : "opposed",
                    });
                    switchTab("tab-lab");
                    runSimulationUpdate(`NASA PSI (${exp.program} • ${exp.exp_id})`);
                    showToast(`${exp.program} conditions loaded into 3D Chamber.`);
                }
            });
        });

        tbody.querySelectorAll(".show-intra-runs-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                const exp = state.rankedList.find((x) => x.exp_id === btn.dataset.id);
                if (exp) {
                    state.activeIntraExpId = exp.exp_id;
                    renderIntraRunsForExperiment(exp);
                    const sec = $("intra-runs-section");
                    if (sec) sec.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
            });
        });
    }

    function renderIntraRunsForExperiment(exp) {
        const box = $("intra-runs-cards");
        const titleEl = $("intra-runs-title");
        const badgeEl = $("intra-runs-badge");
        if (!box || !exp) return;

        const expProg = exp.program_en || exp.program || "";
        const expFac = exp.facility_en || exp.facility || "";
        titleEl.textContent = `Test Variations (${expProg})`;
        badgeEl.textContent = `${exp.exp_id} • ${expFac}`;

        box.innerHTML = "";
        (exp.intra_runs || []).forEach((r) => {
            const card = document.createElement("div");
            card.className = "intra-run-card";
            const sameTxt = r.same_en || r.same_tr || "";
            const diffTxt = r.diff_en || r.diff_tr || "";
            const resTxt = r.result_en || r.result_tr || "";
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <strong style="color:#38bdf8; font-family:Consolas,monospace; font-size:13px;">${escapeHtml(r.run_code)}</strong>
                    <span class="preset-badge">${escapeHtml(expProg)}</span>
                </div>
                <div style="margin-bottom:5px; color:#cbd5e1;">
                    <strong style="color:#94a3b8;">Held Constant:</strong> ${escapeHtml(sameTxt)}
                </div>
                <div style="margin-bottom:5px; color:#fde68a;">
                    <strong>Varied:</strong> ${escapeHtml(diffTxt)}
                </div>
                <div style="color:#6ee7b7;">
                    <strong>Outcome:</strong> ${escapeHtml(resTxt)}
                </div>
            `;
            box.appendChild(card);
        });
    }

    async function runComparisonUpdate() {
        const ids = Array.from(state.selectedCompareIds);
        try {
            const res = await apiFetch("/api/compare", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ exp_ids: ids, mission_params: getSimParamsFromUI() }),
            });
            const data = await res.json();
            const cbBanner = $("comparison-conflict-banner");
            if (cbBanner) {
                const cb = data.conflict_bounding;
                const warnMsg = cb ? (cb.warning_en || cb.en || cb.warning_tr || cb.tr || "") : "";
                if (cb && cb.has_conflict && warnMsg) {
                    cbBanner.innerHTML = renderSafeMarkdown(warnMsg);
                    cbBanner.style.display = "block";
                } else {
                    cbBanner.style.display = "none";
                }
            }
            $("comparison-synthesis-banner").innerHTML = renderSafeMarkdown(
                data.synthesis_en || data.synthesis_tr || ""
            );

            const box = $("comparison-cards-container");
            box.innerHTML = "";
            (data.experiments || []).forEach((e) => {
                const card = document.createElement("div");
                card.className = "compare-card";
                const geom = e.sample_geometry_en || e.material || "";
                const sens = e.sensors_en || e.sensors_tr || "";
                const scaleTxt = e.scale_class_en || e.scale_class_tr || "";
                const hrrLine = e.hrrpua_kw_m2 !== undefined ? `HRRPUA: ${e.hrrpua_kw_m2} kW/m²` : "";
                const ntrsFooter =
                    e.ntrs_id === "USER-DATA" || e.ntrs_id === "USER-UPLOAD" || !e.ntrs_url
                        ? `<span style="font-size:11.5px; color:#6ee7b7; font-weight:600;">Uploaded File</span>`
                        : `<a class="ext-link" href="${escapeHtml(e.ntrs_url)}" target="_blank" rel="noopener" style="font-size:12px;">NTRS #${escapeHtml(e.ntrs_id)}</a>`;
                const eProg = e.program_en || e.program || "";
                const eFac = e.facility_en || e.facility || "";
                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <strong style="color:#38bdf8; font-size:14px;">${escapeHtml(eProg)}</strong>
                        <span class="preset-badge">MOC: ${e.moc_measured_pct}% O₂</span>
                    </div>
                    <div style="font-size:12.3px; font-weight:700; margin-bottom:5px; color:#f8fafc;">${escapeHtml(geom)}</div>
                    <div style="font-size:11.8px; color:#94a3b8; margin-bottom:6px; line-height:1.5;">
                        ${escapeHtml(eFac)}${scaleTxt ? ` • ${escapeHtml(scaleTxt)}` : ""}<br/>
                        ${e.oxygen_pct}% O₂ • ${e.pressure_psia} psia • ${e.airflow_cms} cm/s<br/>
                        ${escapeHtml(e.burning_rate_or_spread)}${hrrLine ? ` • <strong style="color:#fcd34d;">${escapeHtml(hrrLine)}</strong>` : ""}<br/>
                        ${escapeHtml(sens)}<br/>
                        Cool Flame: <strong>${e.cool_flame_observed ? "Observed" : "None"}</strong>
                    </div>
                    ${ntrsFooter}
                `;
                box.appendChild(card);
            });
        } catch (err) {
            console.error("Compare error:", err);
        }
    }

    // =========================================================================
    // TAB 3: NASA ARCHIVE SEARCH
    // =========================================================================
    async function fetchLiveNasaData() {
        const q = $("inp-live-nasa-q").value.trim() || "microgravity combustion";
        const source = $("sel-live-source").value;
        const badge = $("live-api-badge");
        const listBox = $("live-nasa-results-list");

        badge.textContent = "Connecting...";
        listBox.innerHTML = `<div style="padding:14px; color:#94a3b8;">Fetching live NASA records...</div>`;

        try {
            const res = await apiFetch(`/api/nasa-live?source=${encodeURIComponent(source)}&q=${encodeURIComponent(q)}`);
            const data = await res.json();
            state.lastLiveNasaData = data;
            renderLiveNasaCards(data);
        } catch (err) {
            badge.textContent = "Offline";
            listBox.innerHTML = `<div style="padding:14px; color:#fca5a5;">${escapeHtml(formatFriendlyError(err))}</div>`;
        }
    }

    function renderLiveNasaCards(data) {
        if (!data) return;
        const badge = $("live-api-badge");
        const listBox = $("live-nasa-results-list");

        badge.textContent =
            data.source_status === "live_online"
                ? `NASA Live (${data.count})`
                : data.source_status === "cached_live"
                ? `Cached (${data.count})`
                : "Offline";

        listBox.innerHTML = "";
        if (!data.items || data.items.length === 0) {
            listBox.innerHTML = `<div style="padding:14px; color:#fca5a5;">No records found. ${escapeHtml(data.error || "")}</div>`;
            return;
        }

        async function syncArchiveItemTo3D(item) {
            let simParams = item.extracted_sim_params || null;
            let phases = Array.isArray(item.phases) ? item.phases : [];
            let sumEn = item.summary_en || item.summary_tr || `**NASA [${item.id}]:** ${item.title}\n${item.abstract}`;
            let simObj = null;

            if (item.url && /\bPSI-\d+\b/i.test(item.url) && phases.length === 0 && !item.summary_en) {
                try {
                    const sRes = await apiFetch("/api/scrape-url", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url: item.url }),
                    });
                    const sData = await sRes.json();
                    if (sData && sData.ok && !sData.mode) {
                        simParams = sData.extracted_sim_params || simParams;
                        phases = sData.phases || phases;
                        sumEn = sData.summary_en || sData.summary_tr || sumEn;
                        simObj = sData.simulation || null;
                    }
                } catch (_) {}
            }

            state.lastSearchPickerData = null;
            state.attachedImageB64 = null;
            state.attachedMediaName = `${item.id}: ${String(item.title || "").slice(0, 48)}`;
            state.attachedMediaSummaryTr = sumEn;
            state.attachedMediaSummaryEn = sumEn;
            state.attachedMediaSummary = sumEn;
            state.attachedMediaPhases = phases;

            if (simParams) {
                applyParamsToSliders(simParams);
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                if (simObj) {
                    applySimulationStateEverywhere(simObj, `NASA (${item.id})`);
                } else {
                    await runSimulationUpdate(`NASA (${item.id})`);
                }
                refreshRankingTable();
            }
            renderUploadedMediaUI();
        }

        data.items.forEach((item) => {
            const div = document.createElement("div");
            div.className = "live-result-card";
            const phChip =
                item.phase_count > 1
                    ? `<span class="preset-badge" style="margin-left:5px;">${item.phase_count} Phases</span>`
                    : "";
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; gap:8px; margin-bottom:4px; align-items:center; flex-wrap:wrap;">
                    <div>
                        <span class="preset-badge">${escapeHtml(item.id)} • ${escapeHtml(item.source)}</span>
                        ${phChip}
                    </div>
                    <span style="font-size:11.5px; color:#94a3b8;">${escapeHtml(item.date || item.mission || "")}</span>
                </div>
                <div style="font-weight:700; font-size:13.5px; color:#ffffff; margin-bottom:5px;">
                    ${escapeHtml(item.title)}
                </div>
                <p style="font-size:12.3px; color:#cbd5e1; margin-bottom:8px;">
                    ${escapeHtml(item.abstract)}
                </p>
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                    <a class="ext-link" href="${escapeHtml(item.url)}" target="_blank" rel="noopener">Official Record</a>
                    ${item.pdf_url ? `<a class="ext-link" href="${escapeHtml(item.pdf_url)}" target="_blank" rel="noopener">PDF</a>` : ""}
                    <button type="button" class="btn-secondary load-live-3d-btn" style="padding:3px 9px; font-size:11.5px;">Load in 3D</button>
                    <button type="button" class="btn-secondary index-ntrs-btn" style="padding:3px 9px; font-size:11.5px;">Analyze Record</button>
                </div>
            `;
            div.querySelector(".load-live-3d-btn").addEventListener("click", async () => {
                await syncArchiveItemTo3D(item);
                switchTab("tab-lab");
                showToast(`${item.id} conditions loaded into 3D Chamber.`);
            });
            div.querySelector(".index-ntrs-btn").addEventListener("click", async () => {
                await syncArchiveItemTo3D(item);
                await apiFetch("/api/rag-add-text", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        title: item.title,
                        content: `${item.title}\nAuthors: ${item.authors || ""}\nAbstract:\n${item.abstract}`,
                        source: item.id,
                        url: item.url,
                    }),
                });
                showToast(`${item.id} synced to 3D Chamber and Engineering Analysis.`);
                switchTab("tab-copilot");
                sendChatMessage(
                    `Analyze NASA record ${item.id} (${item.title}) using microgravity combustion equations and spacecraft fire safety protocols.`
                );
            });
            listBox.appendChild(div);
        });
    }

    // =========================================================================
    // TAB 4: ENGINEERING ANALYSIS & DECISION SUPPORT
    // =========================================================================
    function formatKernelDisplayName(providerId) {
        const p = String(providerId || "").toLowerCase();
        if (p === "local_cli_bridge" || p === "antigravity") {
            return "Local System Bridge";
        }
        if (p === "deterministic_physics") {
            return "Analytical Physics Solver";
        }
        if (p === "ollama") {
            return "Offline Local Model";
        }
        if (p === "gemini") {
            return "Google Gemini";
        }
        if (p === "openrouter") {
            return "OpenRouter";
        }
        return providerId || "Analytical Solver";
    }

    function appendChatBubble(role, htmlContent, metaInfo) {
        const box = $("chat-messages-box");
        const div = document.createElement("div");
        div.className = `msg-bubble ${role === "user" ? "msg-user" : "msg-ai"}`;
        div.innerHTML = htmlContent;

        if (metaInfo) {
            appendMetaFooter(div, metaInfo);
        }

        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
        return div;
    }

    function appendMetaFooter(bubbleEl, metaInfo) {
        const existing = bubbleEl.querySelector(".msg-meta");
        if (existing) existing.remove();
        const oldActions = bubbleEl.querySelector(".chat-suggested-actions");
        if (oldActions) oldActions.remove();

        const metaDiv = document.createElement("div");
        metaDiv.className = "msg-meta";
        const dispProv = formatKernelDisplayName(metaInfo.provider);

        let chips = "";
        const sg = metaInfo.scope_guard || null;
        if (sg && sg.status) {
            let badgeCls = "scope-direct";
            let enLbl = "Direct Analysis";
            if (sg.status === "boundary_context") {
                badgeCls = "scope-boundary";
                enLbl = "Fire Safety Link";
            } else if (sg.status === "off_topic" || sg.status === "rule_locked") {
                badgeCls = "scope-offtopic";
                enLbl = "Off-Topic";
            }
            chips += `<span class="scope-status-badge ${badgeCls}" data-en="${escapeHtml(enLbl)}">${escapeHtml(enLbl)}</span>`;
            if (sg.physics_note) {
                chips += `<span class="scope-status-badge scope-physics-note" data-en="Physics Note">Physics Note</span>`;
            }
        }

        chips += `<span><span data-en="Solver:">Solver:</span> <strong>${escapeHtml(dispProv)} (${escapeHtml(metaInfo.model)})</strong></span>`;
        if (metaInfo.citations && metaInfo.citations.length) {
            metaInfo.citations.forEach((c) => {
                chips += `<a class="citation-chip" href="${escapeHtml(c.url)}" target="_blank" rel="noopener">${escapeHtml(c.program)} • ${escapeHtml(c.ntrs_id || c.id)}</a>`;
            });
        }
        metaDiv.innerHTML = chips;
        bubbleEl.appendChild(metaDiv);

        if (Array.isArray(metaInfo.suggested_actions) && metaInfo.suggested_actions.length > 0) {
            const actWrap = document.createElement("div");
            actWrap.className = "chat-suggested-actions";
            metaInfo.suggested_actions.forEach((act) => {
                if (!act || !act.type) return;
                const btn = document.createElement("button");
                btn.type = "button";
                const isPrimaryAct = act.type === "apply_3d_sim" || act.type === "run_orion_sequence";
                btn.className = "chat-action-btn " + (isPrimaryAct ? "chat-action-primary" : "chat-action-prompt");
                const enText = String(act.label_en || act.label_tr || "");
                btn.setAttribute("data-en", enText);
                btn.setAttribute("data-action-type", String(act.type));
                btn.textContent = enText;

                btn.addEventListener("click", () => {
                    if (act.type === "apply_3d_sim") {
                        switchTab("tab-lab");
                        setLabViewportMode("chamber");
                        if (act.sim_params) {
                            applyParamsToSliders(act.sim_params);
                        }
                        if (state.chamber3D) {
                            state.chamber3D.reigniteDroplet();
                        }
                        runSimulationUpdate("3D Chamber Applied");
                        showToast("Parameters applied to the 3D Chamber.");
                    } else if (act.type === "run_orion_sequence") {
                        switchTab("tab-lab");
                        setLabViewportMode("spacecraft");
                        if (state.spacecraftStudio && typeof state.spacecraftStudio.triggerFullSequentialIntervention === "function") {
                            state.spacecraftStudio.triggerFullSequentialIntervention(act.compartment_id || "ORION_CM", true);
                        }
                        showToast("5-step fire response started on Orion MCP.");
                    } else if (act.type === "ask_prompt") {
                        const promptNow = act.prompt_en || act.label_en || act.prompt_tr || "";
                        if (promptNow) {
                            sendChatMessage(promptNow);
                        }
                    }
                });
                actWrap.appendChild(btn);
            });
            if (actWrap.childElementCount > 0) {
                bubbleEl.appendChild(actWrap);
            }
        }
    }

    function setChatGeneratingUI(isRunning) {
        $("btn-send-chat").disabled = isRunning;
        $("btn-send-chat").style.opacity = isRunning ? "0.55" : "1";
        $("btn-cancel-chat").style.display = isRunning ? "inline-flex" : "none";
    }

    async function sendChatMessage(customPrompt, extraSimOverrides) {
        if (state.activeChatJobId) {
            showToast("Analysis in progress — wait or click Stop.");
            return;
        }
        const input = $("inp-chat-msg");
        const text = (customPrompt || input.value || "").trim();
        if (!text) return;
        if (!customPrompt) input.value = "";

        const chosenProvider = $("sel-copilot-provider") ? $("sel-copilot-provider").value : "auto";
        const userDisplay = state.attachedMediaName
            ? `<div style="font-size:11px; color:#bae6fd; margin-bottom:4px;">${escapeHtml(state.attachedMediaName)}</div>${escapeHtml(text)}`
            : escapeHtml(text);

        appendChatBubble("user", userDisplay);

        const aiBubble = appendChatBubble(
            "ai",
            `<div class="stage-log-box">[1/4] Computing dimensionless laws, 3D telemetry &amp; NASA PSI evidence...</div><div class="live-stream-body"><em>Preparing engineering analysis...</em></div>`
        );
        const box = $("chat-messages-box");
        setChatGeneratingUI(true);

        try {
            const buildLocalSimFallbackReply = () => {
                const sim = state.currentSim;
                if (!sim || !sim.inputs || !sim.telemetry) {
                    return "### Offline Analytical Summary\nLocal server connection momentarily interrupted; adjust any chamber slider to refresh telemetry.";
                }
                const inp = sim.inputs;
                const tel = sim.telemetry;
                const tl = sim.scenario_timeline || {};
                const call = sim.callouts || {};
                const t100 = tl.t_smac_24h_100ppm_s ?? 180;
                const t425 = tl.t_smac_1h_425ppm_s ?? 420;
                return `### Analytical Physics Synthesis: ${call.badge_en || tel.regime}\n- **Active Chamber (\`${inp.fuel_name_en}\`):** \`${inp.gravity_g} G\`, \`${inp.oxygen_pct}% O₂\`, \`${inp.pressure_psia} psia\`, \`U = ${inp.airflow_cms} cm/s\` → \`T_f = ${tel.flame_temp_k} K\`, \`MOC = ${tel.moc_pct}% O₂\`, Risk **\`${tel.risk_score}/100\`**.\n- **Dimensionless Transport:** \`B = ${tel.spalding_b_number}\` • \`Sh = ${tel.sherwood_number}\` • \`Da = ${tel.damkohler_number}\` • \`χ_r = ${(tel.radiative_loss_fraction * 100).toFixed(1)}%\`.\n- **NASA JSC-20584 CO SMAC (${tl.habitat_name_en || "Habitat"}):** Alarm \`+${tl.t_alarm_s || 4} s\` • 24-hr SMAC (\`100 ppm\`) \`${t100} s\` • 1-hr SMAC (\`425 ppm\`) \`${t425} s\`.\n- **NASA-STD-6001B Action:** Cut HVAC airflow (\`U → 0 cm/s\`), isolate power, apply **25–40 µm Fine Water Mist (SoFIE-MIST)** or CO₂/N₂ (*Halon 1301 prohibited*).`;
            };

            const reqPayload = {
                message: text,
                sim_params: Object.assign(getSimParamsFromUI(), extraSimOverrides || {}),
                history: state.chatHistory.slice(-6),
                image_base64: state.attachedImageB64,
                media_context: state.attachedMediaSummary,
                provider_override: chosenProvider,
            };

            let startData = null;
            try {
                const startRes = await apiFetch("/api/chat/start", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(reqPayload),
                });
                startData = await startRes.json();
            } catch (_firstErr) {
                await new Promise((r) => setTimeout(r, 350));
                const retryRes = await apiFetch("/api/chat/start", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(Object.assign({}, reqPayload, { provider_override: "physics" })),
                });
                startData = await retryRes.json();
            }

            if (!startData || !startData.ok || !startData.job_id) {
                setChatGeneratingUI(false);
                const fb = buildLocalSimFallbackReply();
                aiBubble.innerHTML = renderSafeMarkdown(fb);
                return;
            }

            const jobId = startData.job_id;
            state.activeChatJobId = jobId;
            let transientFailures = 0;

            while (state.activeChatJobId === jobId) {
                await new Promise((r) => setTimeout(r, 380));
                if (state.activeChatJobId !== jobId) break;

                let pollData = null;
                try {
                    const pRes = await apiFetch(`/api/chat/poll/${encodeURIComponent(jobId)}`);
                    pollData = await pRes.json();
                    transientFailures = 0;
                } catch (_netErr) {
                    transientFailures += 1;
                    if (transientFailures >= 6) {
                        state.activeChatJobId = null;
                        setChatGeneratingUI(false);
                        const fb = buildLocalSimFallbackReply();
                        aiBubble.innerHTML = renderSafeMarkdown(fb);
                        return;
                    }
                    continue;
                }

                if (!pollData || !pollData.ok) {
                    state.activeChatJobId = null;
                    setChatGeneratingUI(false);
                    aiBubble.innerHTML = `<span style="color:#fca5a5;">${escapeHtml((pollData && pollData.error) || "Error")}</span>`;
                    return;
                }

                const stagesText = (pollData.stages || []).slice(-2).join(" • ");
                const partial = pollData.partial_reply || "";

                if (pollData.status === "running") {
                    const stageHtml = `<div class="stage-log-box">${escapeHtml(stagesText || "Solver active...")} ${pollData.model ? `<strong>(${escapeHtml(pollData.model)})</strong>` : ""}</div>`;
                    const bodyHtml = partial
                        ? `<div>${renderSafeMarkdown(partial)}</div>`
                        : `<em>Evaluating governing equations and NASA PSI evidence...</em>`;
                    aiBubble.innerHTML = stageHtml + bodyHtml;
                    box.scrollTop = box.scrollHeight;
                } else if (pollData.status === "done") {
                    state.activeChatJobId = null;
                    setChatGeneratingUI(false);
                    const finalReply = pollData.reply || partial || "Completed.";
                    const sgObj = pollData.scope_guard || null;
                    const bodyDiv = document.createElement("div");
                    bodyDiv.className = "msg-body-md";
                    if (sgObj && sgObj.reply_en) {
                        bodyDiv.setAttribute("data-reply-en", sgObj.reply_en);
                        bodyDiv.innerHTML = renderSafeMarkdown(sgObj.reply_en);
                    } else {
                        bodyDiv.innerHTML = renderSafeMarkdown(finalReply);
                    }
                    aiBubble.innerHTML = "";
                    aiBubble.appendChild(bodyDiv);
                    appendMetaFooter(aiBubble, {
                        provider: pollData.provider,
                        model: pollData.model,
                        citations: pollData.citations,
                        scope_guard: sgObj,
                        suggested_actions: pollData.suggested_actions,
                    });
                    const sgStatus = sgObj && sgObj.status;
                    if (sgStatus !== "off_topic" && sgStatus !== "rule_locked") {
                        state.chatHistory.push({ role: "user", content: text });
                        state.chatHistory.push({ role: "assistant", content: finalReply });
                    }
                    box.scrollTop = box.scrollHeight;
                    return;
                } else if (pollData.status === "cancelled") {
                    state.activeChatJobId = null;
                    setChatGeneratingUI(false);
                    aiBubble.innerHTML = partial
                        ? `${renderSafeMarkdown(partial)}<div style="margin-top:8px; font-size:11.5px; color:#fcd34d;">Stopped by user.</div>`
                        : `<em style="color:#fcd34d;">Stopped by user.</em>`;
                    return;
                } else {
                    state.activeChatJobId = null;
                    setChatGeneratingUI(false);
                    const fb = buildLocalSimFallbackReply();
                    aiBubble.innerHTML = renderSafeMarkdown(fb);
                    return;
                }
            }
        } catch (_err) {
            state.activeChatJobId = null;
            setChatGeneratingUI(false);
            const sim = state.currentSim;
            if (sim && sim.inputs && sim.telemetry) {
                const inp = sim.inputs;
                const tel = sim.telemetry;
                const tl = sim.scenario_timeline || {};
                const t100 = tl.t_smac_24h_100ppm_s ?? 180;
                const fallbackMd = `### Offline Analytical Physics Summary (\`${inp.fuel_name_en}\`)\n- **Chamber State:** \`${inp.gravity_g} G\`, \`${inp.oxygen_pct}% O₂\`, \`${inp.pressure_psia} psia\`, \`U = ${inp.airflow_cms} cm/s\` → \`T_f = ${tel.flame_temp_k} K\`, \`MOC = ${tel.moc_pct}% O₂\`, Risk **\`${tel.risk_score}/100\`**.\n- **NASA JSC-20584 24-hr CO SMAC (\`100 ppm\`):** \`${t100} s\` • **Protocol:** Cut HVAC airflow + **SoFIE-MIST** fine water mist (*Halon 1301 banned*).`;
                aiBubble.innerHTML = renderSafeMarkdown(fallbackMd);
            } else {
                aiBubble.innerHTML = `<span style="color:#fcd34d;">Local solver reconnecting — please click Run Analysis again.</span>`;
            }
        }
    }

    async function cancelActiveChatJob() {
        const jid = state.activeChatJobId;
        if (!jid) return;
        state.activeChatJobId = null;
        setChatGeneratingUI(false);
        try {
            await apiFetch(`/api/chat/cancel/${encodeURIComponent(jid)}`, { method: "POST" });
            showToast("Analysis stopped.");
        } catch (_) {}
    }

    // =========================================================================
    // TAB 5: VALIDATION & SETTINGS
    // =========================================================================
    async function loadSystemBootstrap() {
        try {
            const res = await apiFetch("/api/bootstrap");
            const data = await res.json();

            state.presets = data.presets || [];
            state.directives = data.directives || [];
            state.earthTransfers = data.earth_transfers || [];
            state.lang = "en";

            applyLanguageToDOM();
            renderPresetButtons();
            renderDirectivesList();
            renderEarthTransfers();
            populateConfigForm(data.config, data.providers);
            updateHeaderEngineBadge(data.providers);
            if (data.stream) {
                updateStreamHeaderAndUI(data.stream);
            }

            await runSimulationUpdate("Combustion Chamber");
            refreshRankingTable();
            fetchLiveNasaData();
        } catch (err) {
            console.error("Bootstrap error:", err);
        }
    }

    function renderPresetButtons() {
        const box = $("preset-buttons-container");
        box.innerHTML = "";
        state.presets.forEach((pr, idx) => {
            const btn = document.createElement("button");
            btn.className = "preset-btn" + (idx === 0 ? " active" : "");
            const label = pr.name_en || pr.name_tr || "";
            const badgeTxt = pr.badge_en || pr.badge || "";
            btn.innerHTML = `<span>${escapeHtml(label)}</span><span class="preset-badge">${escapeHtml(badgeTxt)}</span>`;
            btn.addEventListener("click", () => {
                box.querySelectorAll(".preset-btn").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                applyParamsToSliders(pr.params);
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                runSimulationUpdate(label);
            });
            box.appendChild(btn);
        });
    }

    function renderEarthTransfers() {
        const box = $("earth-transfer-container");
        if (!box) return;
        box.innerHTML = "";
        const liveImpact = state.currentSim && state.currentSim.space_to_earth_live ? state.currentSim.space_to_earth_live : null;
        state.earthTransfers.forEach((tr, idx) => {
            const card = document.createElement("div");
            card.className = "compare-card";
            const dom = tr.domain_en || tr.domain_tr || "";
            const ins = tr.insight_en || tr.insight_tr || "";
            let liveHtml = "";
            if (liveImpact) {
                if (idx === 0) {
                    liveHtml = `<div class="earth-live-box"><strong>Live Chamber Calc:</strong> Sauter <code>D₃₂ = ${liveImpact.mist_sauter_d32_um} µm</code> • Water Savings: <code>${liveImpact.mist_water_saving_pct}%</code></div>`;
                } else if (idx === 1) {
                    liveHtml = `<div class="earth-live-box"><strong>Live Sensor Calc:</strong> Early-Warning Gain: <code>+${liveImpact.ev_early_warning_gain_s} s</code> • Dust False-Alarm Rejection: <code>${liveImpact.dust_false_alarm_rejection_pct}%</code></div>`;
                } else if (idx === 2) {
                    liveHtml = `<div class="earth-live-box"><strong>Live Thermal Calc:</strong> Protective Fabric Margin: <code>${liveImpact.protective_fabric_margin_kw_m2} kW/m²</code> (@ <code>${liveImpact.active_flame_temp_k} K</code>)</div>`;
                }
            }
            card.innerHTML = `
                <div style="font-weight:700; color:#38bdf8; margin-bottom:5px;">${escapeHtml(dom)}</div>
                <div style="font-size:11.5px; color:#fcd34d; margin-bottom:6px;">NASA Origin: ${escapeHtml(tr.nasa_source)}</div>
                <p style="font-size:12.5px; color:#cbd5e1;">${escapeHtml(ins)}</p>
                ${liveHtml}
            `;
            box.appendChild(card);
        });
    }

    function renderDirectivesList() {
        const box = $("directives-list-container");
        if (!box) return;
        box.innerHTML = "";
        state.directives.forEach((d) => {
            const div = document.createElement("div");
            div.className = "directive-card";
            const title = d.title_en || d.title_tr || "";
            const rule = d.rule_en || d.rule_tr || "";
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <strong style="color:#ffffff;">[${escapeHtml(d.id)}] ${escapeHtml(title)}</strong>
                    <span class="preset-badge">${escapeHtml(d.code)} • ${escapeHtml(d.severity)}</span>
                </div>
                <div style="font-size:12.5px; color:#cbd5e1;">${escapeHtml(rule)}</div>
            `;
            box.appendChild(div);
        });
    }

    function populateConfigForm(cfg, providers) {
        if (!cfg) return;
        state.lastConfigData = cfg;
        const activeProv = cfg.active_provider || "auto";
        $("cfg-active-provider").value = activeProv;
        if ($("sel-copilot-provider") && ["auto", "physics", "ollama", "antigravity", "gemini", "openrouter"].includes(activeProv)) {
            $("sel-copilot-provider").value = activeProv;
        }
        $("cfg-ollama-host").value = cfg.ollama_host || "http://127.0.0.1:11434";
        $("cfg-gemini-key").value = cfg.gemini_api_key || "";
        $("cfg-gemini-model").value = cfg.gemini_model || "gemini-2.5-flash";
        $("cfg-antigravity-key").value = cfg.antigravity_api_key || "";
        $("cfg-openrouter-key").value = cfg.openrouter_api_key || "";
        $("cfg-openrouter-model").value = cfg.openrouter_model || "google/gemini-2.0-flash-exp:free";
        $("cfg-custom-url").value = cfg.custom_base_url || "";
        $("cfg-custom-key").value = cfg.custom_api_key || "";
        $("cfg-custom-model").value = cfg.custom_model || "";
        $("cfg-extra-directives").value = cfg.custom_extra_directives || "";
        $("chk-deep-6stage").checked = Boolean(cfg.deep_verify_6stage);

        $("st-gemini-key").textContent = cfg.gemini_api_key_configured ? "Saved" : "Not set";
        $("st-gemini-key").style.color = cfg.gemini_api_key_configured ? "#10b981" : "#94a3b8";

        if (providers) {
            populateLocalBridgeDropdown(providers.antigravity, cfg.antigravity_model, cfg.antigravity_api_key_configured);
            populateOllamaDropdown(providers.ollama, cfg.ollama_model);
        }
    }

    function populateLocalBridgeDropdown(bridgeSt, savedModel, keyConfigured) {
        const sel = $("cfg-agy-model");
        const badge = $("agy-cli-badge");
        const sdkLabel = $("st-agy-sdk");
        if (!sel || !badge) return;

        sel.innerHTML = "";
        if (bridgeSt && bridgeSt.cli_ready && bridgeSt.models && bridgeSt.models.length > 0) {
            badge.textContent = `Ready (${bridgeSt.models.length} Profiles)`;
            badge.style.color = "#6ee7b7";
            sdkLabel.textContent = "Local Bridge Active";
            bridgeSt.models.forEach((m) => {
                const opt = document.createElement("option");
                opt.value = m.id;
                const lbl = m.label_en || m.label || m.id;
                opt.textContent = `${lbl} (${m.id})`;
                sel.appendChild(opt);
            });
            const normSaved = (!savedModel || savedModel.startsWith("gemini-3.8")) ? "gemini-2.5-flash" : savedModel;
            const targetM = normSaved || "gemini-2.5-flash";
            if (Array.from(sel.options).some((o) => o.value === targetM)) {
                sel.value = targetM;
            }
        } else {
            const normSaved = (!savedModel || savedModel.startsWith("gemini-3.8")) ? "gemini-2.5-flash" : savedModel;
            const opt = document.createElement("option");
            opt.value = normSaved;
            opt.textContent = normSaved;
            sel.appendChild(opt);
            badge.textContent = keyConfigured ? "Key Mode" : "Inactive";
            badge.style.color = keyConfigured ? "#fcd34d" : "#94a3b8";
            sdkLabel.textContent = keyConfigured ? "Key Saved" : "Optional";
        }
    }

    function populateOllamaDropdown(ollamaSt, savedModel) {
        const sel = $("cfg-ollama-model");
        const badge = $("ollama-online-badge");
        sel.innerHTML = `<option value="auto">Auto (Recommended Local Model)</option>`;

        if (ollamaSt && ollamaSt.online) {
            badge.textContent = `Online (${ollamaSt.models.length})`;
            badge.style.color = "#6ee7b7";
            ollamaSt.models.forEach((m) => {
                const opt = document.createElement("option");
                opt.value = m.name;
                opt.textContent = `${m.name} (${m.size_gb} GB)`;
                sel.appendChild(opt);
            });
            if (savedModel && savedModel !== "auto" && Array.from(sel.options).some((o) => o.value === savedModel)) {
                sel.value = savedModel;
            }
        } else {
            badge.textContent = "Service Offline";
            badge.style.color = "#fca5a5";
        }
    }

    function updateHeaderEngineBadge(providers) {
        if (!providers) return;
        state.lastProvidersData = providers;
        const dot = $("header-status-dot");
        const txt = $("header-engine-text");
        const pref = providers.active_provider || "auto";

        if (pref === "physics" || pref === "deterministic") {
            dot.style.background = "#10b981";
            txt.textContent = "Solver: Analytical Physics";
        } else if (pref === "ollama" && providers.ollama && providers.ollama.online) {
            dot.style.background = "#38bdf8";
            txt.textContent = "Solver: Analytical + Local";
        } else if (pref === "antigravity" && providers.antigravity_ready) {
            dot.style.background = "#10b981";
            txt.textContent = "Solver: Analytical + Bridge";
        } else if (providers.gemini_ready) {
            dot.style.background = "#10b981";
            txt.textContent = "Solver: Analytical + Gemini";
        } else if (providers.openrouter_ready) {
            dot.style.background = "#10b981";
            txt.textContent = "Solver: Analytical + OpenRouter";
        } else if (providers.ollama && providers.ollama.online) {
            dot.style.background = "#38bdf8";
            txt.textContent = "Solver: Analytical + Local";
        } else if (providers.antigravity_ready && pref === "auto") {
            dot.style.background = "#10b981";
            txt.textContent = "Solver: Analytical + Hybrid";
        } else if (window.ALTAR_SERVERLESS_MODE) {
            dot.style.background = "#38bdf8";
            txt.textContent = "Solver: Browser Physics";
        } else {
            dot.style.background = "#10b981";
            txt.textContent = "Solver: Analytical Physics";
        }
    }

    async function saveAllSettings(silentToast) {
        const payload = {
            active_provider: $("cfg-active-provider").value,
            antigravity_model: $("cfg-agy-model").value,
            ollama_host: $("cfg-ollama-host").value,
            ollama_model: $("cfg-ollama-model").value,
            gemini_api_key: $("cfg-gemini-key").value,
            gemini_model: $("cfg-gemini-model").value,
            antigravity_api_key: $("cfg-antigravity-key").value,
            openrouter_api_key: $("cfg-openrouter-key").value,
            openrouter_model: $("cfg-openrouter-model").value,
            custom_base_url: $("cfg-custom-url").value,
            custom_api_key: $("cfg-custom-key").value,
            custom_model: $("cfg-custom-model").value,
            custom_extra_directives: $("cfg-extra-directives").value,
            deep_verify_6stage: $("chk-deep-6stage").checked,
            language: "en",
        };
        const res = await apiFetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        populateConfigForm(data.config, data.providers);
        updateHeaderEngineBadge(data.providers);
        if (!silentToast) {
            showToast("Solver and connection settings saved.");
        }
    }

    // =========================================================================
    // DATASET EXPORT (CSV & JSON) & VISUAL ENGINEERING REPORT (.HTML / PDF)
    // =========================================================================
    function triggerBlobDownload(blob, filename) {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    }

    function exportPredictiveCSV() {
        const sim = state.currentSim;
        if (!sim || !sim.sensor_timeseries) return;
        const isEn = state.lang === "en";
        const inp = sim.inputs || {};
        const tel = sim.telemetry || {};
        const fv = sim.flight_validation || {};
        const ts = sim.sensor_timeseries;
        const tl = sim.scenario_timeline || {};
        const ub = sim.uncertainty_bounds || {};
        const pfc = sim.post_fire_cooling || {};

        const header = [
            "time_s",
            "d2_over_d02_model",
            "thermocouple_temp_k",
            "optical_visible_pct",
            "ir_radiometer_kw_m2",
            "co_sensor_ppm",
            "fuel_id",
            "flow_direction",
            "gravity_g",
            "oxygen_pct",
            "pressure_psia",
            "airflow_cms",
            "diluent",
            "regime",
            "flame_temp_k",
            "flame_temp_1sigma_lower_k",
            "flame_temp_1sigma_upper_k",
            "moc_pct",
            "moc_1sigma_lower_pct",
            "moc_1sigma_upper_pct",
            "burning_rate_k_mm2_s",
            "k_1sigma_lower_mm2_s",
            "k_1sigma_upper_mm2_s",
            "flame_spread_mm_s",
            "hrrpua_kw_m2",
            "iss_r_squared",
            "iss_rmse",
            "habitat_id",
            "t_smac_24h_100ppm_s",
            "t_smac_1h_425ppm_s",
            "reignition_risk_pct",
            "safe_reentry_0g_s",
        ].join(",");

        const rows = [header];
        const times = ts.time_s || [];
        for (let i = 0; i < times.length; i++) {
            rows.push(
                [
                    times[i],
                    (ts.d2_normalized && ts.d2_normalized[i] !== undefined) ? ts.d2_normalized[i] : "",
                    (ts.thermocouple_k && ts.thermocouple_k[i] !== undefined) ? ts.thermocouple_k[i] : "",
                    (ts.optical_intensity_pct && ts.optical_intensity_pct[i] !== undefined) ? ts.optical_intensity_pct[i] : "",
                    (ts.radiometer_kw_m2 && ts.radiometer_kw_m2[i] !== undefined) ? ts.radiometer_kw_m2[i] : "",
                    (ts.co_ppm && ts.co_ppm[i] !== undefined) ? ts.co_ppm[i] : "",
                    inp.fuel_id || "",
                    inp.flow_direction || "opposed",
                    inp.gravity_g ?? "",
                    inp.oxygen_pct ?? "",
                    inp.pressure_psia ?? "",
                    inp.airflow_cms ?? "",
                    inp.diluent || "",
                    tel.regime || "",
                    tel.flame_temp_k ?? "",
                    ub.temp_lower_k ?? "",
                    ub.temp_upper_k ?? "",
                    tel.moc_pct ?? "",
                    ub.moc_lower_pct ?? "",
                    ub.moc_upper_pct ?? "",
                    tel.burning_rate_k_mm2_s ?? "",
                    ub.k_lower_mm2_s ?? "",
                    ub.k_upper_mm2_s ?? "",
                    tel.flame_spread_mm_s ?? "",
                    tel.hrrpua_kw_m2 ?? "",
                    fv.r_squared ?? "",
                    fv.rmse ?? "",
                    tl.habitat_id || "",
                    tl.t_smac_24h_100ppm_s ?? "",
                    tl.t_smac_1h_425ppm_s ?? "",
                    pfc.reignition_risk_pct ?? "",
                    pfc.safe_reentry_s ?? "",
                ].join(",")
            );
        }

        const stamp = new Date().toISOString().slice(0, 16).replace(/[:T-]/g, "");
        const blob = new Blob(["\uFEFF" + rows.join("\n")], { type: "text/csv;charset=utf-8" });
        triggerBlobDownload(blob, `ALTAR_NASA_Predictive_Dataset_${inp.fuel_id || "sim"}_${stamp}.csv`);
        showToast("Predictive CSV dataset downloaded.");
    }

    function localizeObjectForExport(node) {
        if (Array.isArray(node)) {
            return node.map((item) => localizeObjectForExport(item));
        }
        if (!node || typeof node !== "object") {
            return node;
        }
        const out = {};
        const handledBases = new Set();
        Object.keys(node).forEach((k) => {
            if (k.endsWith("_tr") || k.endsWith("_en")) {
                const base = k.slice(0, -3);
                if (handledBases.has(base)) return;
                handledBases.add(base);
                const chosen = node[`${base}_en`] !== undefined ? node[`${base}_en`] : node[k];
                out[base] = localizeObjectForExport(chosen);
            } else {
                out[k] = localizeObjectForExport(node[k]);
            }
        });
        return out;
    }

    function exportPredictiveJSON() {
        const sim = state.currentSim;
        if (!sim) return;
        const rawPayload = {
            platform: "ALTAR-NASA Flame in Freefall v6.3",
            language: "en",
            generated_utc: new Date().toISOString(),
            active_data_source: normalizeSourceLabelForLang(state.activeSourceLabel),
            audience_mode: state.audienceMode,
            inputs: sim.inputs,
            telemetry: sim.telemetry,
            uncertainty_bounds_1sigma: sim.uncertainty_bounds || null,
            mission_material_certification: sim.mission_certification || [],
            post_fire_0g_cooling: sim.post_fire_cooling || null,
            space_to_earth_live_impact: sim.space_to_earth_live || null,
            analog_material_matching: sim.analog_match_info || null,
            flight_validation_iss: sim.flight_validation || null,
            eclss_scenario_timeline: sim.scenario_timeline || null,
            governing_equations: sim.formula_table || [],
            flammability_boundary_map: sim.flammability_map || {},
            multisensor_timeseries_0_30s: sim.sensor_timeseries || {},
            top_ranked_psi_investigations: (state.rankedList || []).slice(0, 8).map((e) => ({
                rank: e.rank,
                exp_id: e.exp_id,
                program: e.program_en || e.program,
                hardware_group: e.hardware_group,
                priority_score: e.priority_score,
                moc_measured_pct: e.moc_measured_pct,
                hrrpua_kw_m2: e.hrrpua_kw_m2,
                ntrs_id: e.ntrs_id,
                ntrs_url: e.ntrs_url,
            })),
        };
        const payload = localizeObjectForExport(rawPayload);
        const stamp = new Date().toISOString().slice(0, 16).replace(/[:T-]/g, "");
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
        triggerBlobDownload(blob, `ALTAR_NASA_Predictive_Bundle_${(sim.inputs && sim.inputs.fuel_id) || "sim"}_${stamp}.json`);
        showToast("Predictive JSON bundle downloaded.");
    }

    function _buildReportSvgPolyline(xs, ys, xMin, xMax, yMin, yMax, padL, padT, plotW, plotH) {
        if (!xs || !ys || xs.length === 0) return "";
        const n = Math.min(xs.length, ys.length);
        const pts = [];
        for (let i = 0; i < n; i++) {
            const xv = Number(xs[i]);
            const yv = Number(ys[i]);
            if (!Number.isFinite(xv) || !Number.isFinite(yv)) continue;
            const px = padL + ((xv - xMin) / Math.max(1e-6, xMax - xMin)) * plotW;
            const py = padT + plotH - ((Math.max(yMin, Math.min(yMax, yv)) - yMin) / Math.max(1e-6, yMax - yMin)) * plotH;
            pts.push(`${px.toFixed(1)},${py.toFixed(1)}`);
        }
        return pts.join(" ");
    }

    function exportScientificMissionReport() {
        const sim = state.currentSim;
        if (!sim) return;
        const inp = sim.inputs || {};
        const tel = sim.telemetry || {};
        const call = sim.callouts || {};
        const fv = sim.flight_validation || {};
        const tl = sim.scenario_timeline || {};
        const ub = sim.uncertainty_bounds || {};
        const pfc = sim.post_fire_cooling || {};
        const fmap = sim.flammability_map || {};
        const ts = sim.sensor_timeseries || {};
        const certs = Array.isArray(sim.mission_certification) ? sim.mission_certification : [];
        const ste = sim.space_to_earth_live || {};
        const cn = sim.compartment_network || {};
        const tox = cn.multi_gas_toxicology || {};
        const am = sim.analog_match_info || {};
        const nowStr = new Date().toISOString().slice(0, 19).replace("T", " ") + " UTC";

        const r2Txt = fv.r_squared !== undefined ? fv.r_squared : "N/A";
        const rmseTxt = fv.rmse !== undefined ? fv.rmse : "N/A";
        const fuelName = inp.fuel_name_en || inp.fuel_id;
        const regimeBadge = call.badge_en || tel.regime;

        // --- SVG CHART 1: Flammability Boundary Map + ±1σ Band ---
        const c1W = 540, c1H = 250, c1L = 48, c1T = 26, c1PW = 468, c1PH = 184;
        const fFlows = fmap.airflow_cms || fmap.flows_cms || [0, 5, 10, 20, 40];
        const fMaxX = Math.max(40, ...fFlows, Number(inp.airflow_cms || 0));
        const fMinY = 8, fMaxY = Math.max(42, Number(inp.oxygen_pct || 21) + 4);
        const p0g = _buildReportSvgPolyline(fFlows, fmap.moc_0g_pct || [], 0, fMaxX, fMinY, fMaxY, c1L, c1T, c1PW, c1PH);
        const pMoon = _buildReportSvgPolyline(fFlows, fmap.moc_lunar_016g_pct || [], 0, fMaxX, fMinY, fMaxY, c1L, c1T, c1PW, c1PH);
        const pMars = _buildReportSvgPolyline(fFlows, fmap.moc_mars_038g_pct || [], 0, fMaxX, fMinY, fMaxY, c1L, c1T, c1PW, c1PH);
        const p1g = _buildReportSvgPolyline(fFlows, fmap.moc_1g_pct || [], 0, fMaxX, fMinY, fMaxY, c1L, c1T, c1PW, c1PH);
        const pAct = _buildReportSvgPolyline(fFlows, fmap.moc_active_g_pct || fmap.moc_0g_pct || [], 0, fMaxX, fMinY, fMaxY, c1L, c1T, c1PW, c1PH);

        let bandPoly = "";
        if (Array.isArray(fmap.moc_upper_1sigma_pct) && Array.isArray(fmap.moc_lower_1sigma_pct)) {
            const upPts = [];
            const dnPts = [];
            for (let i = 0; i < fFlows.length; i++) {
                const px = c1L + (fFlows[i] / fMaxX) * c1PW;
                const pyU = c1T + c1PH - ((Math.max(fMinY, Math.min(fMaxY, fmap.moc_upper_1sigma_pct[i])) - fMinY) / (fMaxY - fMinY)) * c1PH;
                const pyL = c1T + c1PH - ((Math.max(fMinY, Math.min(fMaxY, fmap.moc_lower_1sigma_pct[i])) - fMinY) / (fMaxY - fMinY)) * c1PH;
                upPts.push(`${px.toFixed(1)},${pyU.toFixed(1)}`);
                dnPts.unshift(`${px.toFixed(1)},${pyL.toFixed(1)}`);
            }
            bandPoly = `<polygon points="${upPts.concat(dnPts).join(" ")}" fill="rgba(56,189,248,0.18)" stroke="none" />`;
        }
        const opX = c1L + (Math.min(fMaxX, Number(inp.airflow_cms || 0)) / fMaxX) * c1PW;
        const opY = c1T + c1PH - ((Math.max(fMinY, Math.min(fMaxY, Number(inp.oxygen_pct || 21))) - fMinY) / (fMaxY - fMinY)) * c1PH;
        let c1Grid = "";
        [10, 20, 30, 40].forEach((yv) => {
            if (yv > fMaxY) return;
            const gy = c1T + c1PH - ((yv - fMinY) / (fMaxY - fMinY)) * c1PH;
            c1Grid += `<line x1="${c1L}" y1="${gy.toFixed(1)}" x2="${c1L + c1PW}" y2="${gy.toFixed(1)}" stroke="#1e293b" stroke-width="1" />`;
            c1Grid += `<text x="${c1L - 6}" y="${(gy + 3.5).toFixed(1)}" fill="#94a3b8" font-size="10" text-anchor="end">${yv}%</text>`;
        });
        [0, 10, 20, 30, 40].forEach((xv) => {
            const gx = c1L + (xv / fMaxX) * c1PW;
            c1Grid += `<line x1="${gx.toFixed(1)}" y1="${c1T}" x2="${gx.toFixed(1)}" y2="${c1T + c1PH}" stroke="#1e293b" stroke-width="1" />`;
            c1Grid += `<text x="${gx.toFixed(1)}" y="${c1T + c1PH + 15}" fill="#94a3b8" font-size="10" text-anchor="middle">${xv}</text>`;
        });
        const svgChart1 = `
            <svg viewBox="0 0 ${c1W} ${c1H}" width="100%" height="auto" role="img" aria-label="Flammability Boundary Map">
                <rect x="0" y="0" width="${c1W}" height="${c1H}" rx="8" fill="#0b1220" />
                ${c1Grid}
                ${bandPoly}
                <polyline points="${p0g}" fill="none" stroke="#38bdf8" stroke-width="2.2" />
                <polyline points="${pMoon}" fill="none" stroke="#34d399" stroke-width="1.6" stroke-dasharray="5,3" />
                <polyline points="${pMars}" fill="none" stroke="#f87171" stroke-width="1.6" stroke-dasharray="3,3" />
                <polyline points="${p1g}" fill="none" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="6,4" />
                <polyline points="${pAct}" fill="none" stroke="#e0f2fe" stroke-width="1.4" />
                <circle cx="${opX.toFixed(1)}" cy="${opY.toFixed(1)}" r="5.5" fill="#ef4444" stroke="#ffffff" stroke-width="1.8" />
                <text x="${c1L + 6}" y="16" fill="#38bdf8" font-size="10.5" font-weight="700">0G</text>
                <text x="${c1L + 36}" y="16" fill="#34d399" font-size="10.5">0.16G</text>
                <text x="${c1L + 80}" y="16" fill="#f87171" font-size="10.5">0.38G</text>
                <text x="${c1L + 124}" y="16" fill="#f59e0b" font-size="10.5">1G</text>
                <text x="${c1L + 154}" y="16" fill="#bae6fd" font-size="10.5">±1σ (${inp.gravity_g}G)</text>
                <text x="${c1L + c1PW}" y="${c1H - 6}" fill="#94a3b8" font-size="10" text-anchor="end">Airflow U (cm/s) -&gt; MOC (O₂%)</text>
            </svg>`;

        // --- SVG CHART 2: Multi-Sensor & d²/d₀² Timeseries (0-30 s) ---
        const tArr = ts.time_s || [];
        const d2Pct = (ts.d2_normalized || []).map((v) => Number(v) * 100);
        const optPct = ts.optical_intensity_pct || [];
        const maxT = Math.max(1200, ...(ts.thermocouple_k || [300]));
        const tempNorm = (ts.thermocouple_k || []).map((v) => ((Number(v) - 290) / Math.max(1, maxT - 290)) * 100);
        const maxCo = Math.max(250, ...(ts.co_ppm || [10]));
        const coNorm = (ts.co_ppm || []).map((v) => (Number(v) / maxCo) * 100);
        const pD2 = _buildReportSvgPolyline(tArr, d2Pct, 0, 30, 0, 105, c1L, c1T, c1PW, c1PH);
        const pOpt = _buildReportSvgPolyline(tArr, optPct, 0, 30, 0, 105, c1L, c1T, c1PW, c1PH);
        const pTmp = _buildReportSvgPolyline(tArr, tempNorm, 0, 30, 0, 105, c1L, c1T, c1PW, c1PH);
        const pCo = _buildReportSvgPolyline(tArr, coNorm, 0, 30, 0, 105, c1L, c1T, c1PW, c1PH);
        let c2Grid = "";
        [0, 25, 50, 75, 100].forEach((yv) => {
            const gy = c1T + c1PH - (yv / 105) * c1PH;
            c2Grid += `<line x1="${c1L}" y1="${gy.toFixed(1)}" x2="${c1L + c1PW}" y2="${gy.toFixed(1)}" stroke="#1e293b" stroke-width="1" />`;
            c2Grid += `<text x="${c1L - 6}" y="${(gy + 3.5).toFixed(1)}" fill="#94a3b8" font-size="10" text-anchor="end">${yv}%</text>`;
        });
        [0, 10, 20, 30].forEach((xv) => {
            const gx = c1L + (xv / 30) * c1PW;
            c2Grid += `<line x1="${gx.toFixed(1)}" y1="${c1T}" x2="${gx.toFixed(1)}" y2="${c1T + c1PH}" stroke="#1e293b" stroke-width="1" />`;
            c2Grid += `<text x="${gx.toFixed(1)}" y="${c1T + c1PH + 15}" fill="#94a3b8" font-size="10" text-anchor="middle">${xv}s</text>`;
        });
        const svgChart2 = `
            <svg viewBox="0 0 ${c1W} ${c1H}" width="100%" height="auto" role="img" aria-label="Multi-Sensor Timeseries">
                <rect x="0" y="0" width="${c1W}" height="${c1H}" rx="8" fill="#0b1220" />
                ${c2Grid}
                <polyline points="${pD2}" fill="none" stroke="#38bdf8" stroke-width="2.2" />
                <polyline points="${pTmp}" fill="none" stroke="#f97316" stroke-width="2.0" />
                <polyline points="${pOpt}" fill="none" stroke="#eab308" stroke-width="1.8" stroke-dasharray="5,3" />
                <polyline points="${pCo}" fill="none" stroke="#a855f7" stroke-width="1.9" />
                <text x="${c1L + 6}" y="16" fill="#38bdf8" font-size="10.5" font-weight="700">d²/d₀²</text>
                <text x="${c1L + 58}" y="16" fill="#f97316" font-size="10.5">T_max (${Math.round(maxT)} K)</text>
                <text x="${c1L + 154}" y="16" fill="#eab308" font-size="10.5">Optical PSD</text>
                <text x="${c1L + 236}" y="16" fill="#a855f7" font-size="10.5">CO (${Math.round(maxCo)} ppm)</text>
                <text x="${c1L + c1PW}" y="${c1H - 6}" fill="#94a3b8" font-size="10" text-anchor="end">Time (0-30 s, Normalized Scale)</text>
            </svg>`;

        // --- SVG CHART 3: 0G Post-Fire Core Cooling & Re-Ignition Curve (0-180 s) ---
        const cTimes = pfc.time_s || [0, 30, 60, 120, 180];
        const c0g = pfc.core_temp_0g_k || [800, 720, 650, 540, 460];
        const cMist = pfc.core_temp_mist_k || [800, 480, 350, 305, 296];
        const c1g = pfc.core_temp_1g_k || [800, 610, 490, 370, 320];
        const cMaxK = Math.max(900, ...c0g);
        const cMinK = 280;
        const pCool0g = _buildReportSvgPolyline(cTimes, c0g, 0, 180, cMinK, cMaxK, c1L, c1T, c1PW, c1PH);
        const pCoolMist = _buildReportSvgPolyline(cTimes, cMist, 0, 180, cMinK, cMaxK, c1L, c1T, c1PW, c1PH);
        const pCool1g = _buildReportSvgPolyline(cTimes, c1g, 0, 180, cMinK, cMaxK, c1L, c1T, c1PW, c1PH);
        const yAutoIg = c1T + c1PH - (((pfc.autoignition_temp_k || 525) - cMinK) / (cMaxK - cMinK)) * c1PH;
        const ySafeEn = c1T + c1PH - (((pfc.safe_reentry_temp_k || 335) - cMinK) / (cMaxK - cMinK)) * c1PH;
        let c3Grid = "";
        [300, 500, 700, 900].forEach((kv) => {
            if (kv > cMaxK) return;
            const gy = c1T + c1PH - ((kv - cMinK) / (cMaxK - cMinK)) * c1PH;
            c3Grid += `<line x1="${c1L}" y1="${gy.toFixed(1)}" x2="${c1L + c1PW}" y2="${gy.toFixed(1)}" stroke="#1e293b" stroke-width="1" />`;
            c3Grid += `<text x="${c1L - 6}" y="${(gy + 3.5).toFixed(1)}" fill="#94a3b8" font-size="10" text-anchor="end">${kv}K</text>`;
        });
        [0, 60, 120, 180].forEach((xv) => {
            const gx = c1L + (xv / 180) * c1PW;
            c3Grid += `<text x="${gx.toFixed(1)}" y="${c1T + c1PH + 15}" fill="#94a3b8" font-size="10" text-anchor="middle">${xv}s</text>`;
        });
        const svgChart3 = `
            <svg viewBox="0 0 ${c1W} ${c1H}" width="100%" height="auto" role="img" aria-label="0G Post-Fire Cooling Curve">
                <rect x="0" y="0" width="${c1W}" height="${c1H}" rx="8" fill="#0b1220" />
                ${c3Grid}
                <line x1="${c1L}" y1="${yAutoIg.toFixed(1)}" x2="${c1L + c1PW}" y2="${yAutoIg.toFixed(1)}" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="4,4" />
                <line x1="${c1L}" y1="${ySafeEn.toFixed(1)}" x2="${c1L + c1PW}" y2="${ySafeEn.toFixed(1)}" stroke="#10b981" stroke-width="1.2" stroke-dasharray="4,4" />
                <polyline points="${pCool0g}" fill="none" stroke="#f97316" stroke-width="2.3" />
                <polyline points="${pCoolMist}" fill="none" stroke="#38bdf8" stroke-width="2.3" />
                <polyline points="${pCool1g}" fill="none" stroke="#94a3b8" stroke-width="1.6" stroke-dasharray="5,3" />
                <text x="${c1L + 6}" y="16" fill="#f97316" font-size="10.5" font-weight="700">0G Unassisted</text>
                <text x="${c1L + 114}" y="16" fill="#38bdf8" font-size="10.5" font-weight="700">SoFIE-MIST</text>
                <text x="${c1L + 194}" y="16" fill="#94a3b8" font-size="10.5">1G Ref</text>
                <text x="${c1L + 250}" y="16" fill="#fca5a5" font-size="10.5">Flash Limit 525K</text>
                <text x="${c1L + c1PW}" y="${c1H - 6}" fill="#94a3b8" font-size="10" text-anchor="end">Post-Suppression Time (s) -&gt; T_core (K)</text>
            </svg>`;

        // --- SVG CHART 4: Top Ranked NASA PSI Match Score & Measured MOC ---
        const topExps = (state.rankedList || []).slice(0, 6);
        let c4Bars = "";
        topExps.forEach((e, idx) => {
            const by = 28 + idx * 34;
            const prog = escapeHtml(e.program_en || e.program).slice(0, 18);
            const scoreW = Math.max(6, (Math.min(100, Number(e.priority_score || 0)) / 100) * 250);
            const mocW = Math.max(6, (Math.min(40, Number(e.moc_measured_pct || 0)) / 40) * 140);
            c4Bars += `
                <text x="12" y="${by + 11}" fill="#e2e8f0" font-size="10.5" font-weight="600">#${e.rank} ${prog}</text>
                <rect x="148" y="${by}" width="${scoreW.toFixed(1)}" height="11" rx="3" fill="#38bdf8" />
                <text x="${(153 + scoreW).toFixed(1)}" y="${by + 9.5}" fill="#bae6fd" font-size="9.5">${e.priority_score}/100</text>
                <rect x="148" y="${by + 13}" width="${mocW.toFixed(1)}" height="8" rx="2" fill="#f59e0b" />
                <text x="${(153 + mocW).toFixed(1)}" y="${by + 20}" fill="#fde68a" font-size="9">MOC ${e.moc_measured_pct}% O₂</text>
            `;
        });
        const svgChart4 = `
            <svg viewBox="0 0 ${c1W} ${c1H}" width="100%" height="auto" role="img" aria-label="NASA PSI Match Comparison">
                <rect x="0" y="0" width="${c1W}" height="${c1H}" rx="8" fill="#0b1220" />
                <text x="12" y="17" fill="#38bdf8" font-size="10.5" font-weight="700">Investigation</text>
                <text x="148" y="17" fill="#bae6fd" font-size="10.5">Similarity Score (/100) &amp; Measured MOC (O₂%)</text>
                ${c4Bars || `<text x="20" y="120" fill="#94a3b8" font-size="12">NASA PSI records ready.</text>`}
            </svg>`;

        const certRowsHtml = certs
            .map((c) => {
                const stCls =
                    c.status === "PASS"
                        ? "pill-pass"
                        : c.status === "CAUTION" || c.status === "CONDITIONAL"
                        ? "pill-cond"
                        : "pill-fail";
                return `<tr>
                    <td><strong>${escapeHtml(c.label_en || c.label_tr || "")}</strong></td>
                    <td><code>${c.gravity_g} G</code></td>
                    <td><code>${c.oxygen_pct}% O₂ @ ${c.pressure_psia} psia</code></td>
                    <td><code>${c.moc_pct}% O₂</code></td>
                    <td><code>${c.margin_pct > 0 ? "+" : ""}${c.margin_pct}%</code></td>
                    <td><span class="status-pill ${stCls}">${escapeHtml(c.status_en || c.status_tr || "")}</span></td>
                </tr>`;
            })
            .join("");

        const eqRowsHtml = (sim.formula_table || [])
            .map(
                (r) => `<tr>
                    <td><strong>${escapeHtml(r.law_en || r.law_tr || "")}</strong></td>
                    <td><code>${escapeHtml(r.equation)}</code></td>
                    <td><strong>${escapeHtml(r.value)}</strong></td>
                    <td>${escapeHtml(r.status_en || r.status_tr || "")}</td>
                </tr>`
            )
            .join("");

        const expRowsHtml = topExps
            .map(
                (e) => `<tr>
                    <td><strong>#${e.rank}</strong></td>
                    <td><strong>${escapeHtml(e.program_en || e.program)}</strong><br/><span class="muted">${escapeHtml(e.exp_id)} • ${escapeHtml(e.hardware_group || "CIR")}</span></td>
                    <td>${escapeHtml(e.sample_geometry_en || e.material)}</td>
                    <td><code>${e.oxygen_pct}% O₂ • ${e.pressure_psia} psia • ${e.airflow_cms} cm/s</code></td>
                    <td><code>${e.moc_measured_pct}%</code></td>
                    <td><strong>${e.priority_score}/100</strong></td>
                    <td>${e.ntrs_url ? `<a href="${escapeHtml(e.ntrs_url)}" target="_blank" rel="noopener">NTRS #${escapeHtml(e.ntrs_id)}</a>` : escapeHtml(e.ntrs_id || "-")}</td>
                </tr>`
            )
            .join("");

        const lastAssistant = [...state.chatHistory].reverse().find((m) => m.role === "assistant");
        const aiSectionHtml = lastAssistant
            ? `<section class="card"><h2>6. Engineering Decision Support Synthesis</h2><div class="prose">${renderSafeMarkdown(lastAssistant.content)}</div></section>`
            : "";

        const reportTitle = "ALTAR-NASA Flame in Freefall (v6.3) — Visual Engineering & Fire Safety Report";

        const htmlDoc = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>${escapeHtml(reportTitle)}</title>
<style>
    :root { --bg:#070d19; --card:#0f172a; --border:#1e293b; --text:#f1f5f9; --muted:#94a3b8; --accent:#38bdf8; }
    * { box-sizing:border-box; }
    body { margin:0; padding:24px; font-family:"Segoe UI",system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; }
    .container { max-width:1160px; margin:0 auto; }
    .top-bar { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; padding:18px 22px; background:linear-gradient(135deg,#0f172a,#111c33); border:1px solid #334155; border-radius:12px; margin-bottom:18px; }
    h1 { margin:0 0 6px 0; font-size:20px; color:#f8fafc; letter-spacing:0.2px; }
    h2 { margin:0 0 12px 0; font-size:15px; color:#38bdf8; text-transform:uppercase; letter-spacing:0.6px; border-bottom:1px solid var(--border); padding-bottom:6px; }
    .meta-line { font-size:12.5px; color:var(--muted); }
    .print-btn { padding:9px 16px; border-radius:8px; border:1px solid #38bdf8; background:#0284c7; color:#ffffff; font-weight:700; font-size:12.5px; cursor:pointer; white-space:nowrap; }
    .print-btn:hover { background:#0369a1; }
    .kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }
    .kpi { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:12px 14px; }
    .kpi-lbl { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; }
    .kpi-val { font-size:20px; font-weight:800; color:#f8fafc; margin-top:3px; font-family:Consolas,monospace; }
    .kpi-sub { font-size:11.5px; color:#7dd3fc; margin-top:3px; }
    .charts-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; margin-bottom:18px; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:16px 18px; margin-bottom:16px; break-inside:avoid; }
    table { width:100%; border-collapse:collapse; font-size:12.2px; }
    th, td { padding:8px 10px; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; }
    th { color:#bae6fd; font-weight:700; background:rgba(15,23,42,0.85); }
    code { font-family:Consolas,monospace; color:#fcd34d; font-size:11.6px; }
    a { color:#38bdf8; text-decoration:none; }
    .muted { color:var(--muted); font-size:11px; }
    .status-pill { display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }
    .pill-pass { background:rgba(16,185,129,0.18); color:#6ee7b7; border:1px solid rgba(16,185,129,0.45); }
    .pill-cond { background:rgba(245,158,11,0.18); color:#fcd34d; border:1px solid rgba(245,158,11,0.45); }
    .pill-fail { background:rgba(239,68,68,0.18); color:#fca5a5; border:1px solid rgba(239,68,68,0.45); }
    .prose h3, .prose h4 { color:#e2e8f0; margin:10px 0 6px 0; }
    @media (max-width:860px) { .kpi-grid, .charts-grid { grid-template-columns:1fr; } }
    @media print {
        body { background:#ffffff; color:#0f172a; padding:0; }
        .no-print { display:none !important; }
        .top-bar, .kpi, .card { background:#ffffff; border-color:#cbd5e1; color:#0f172a; box-shadow:none; }
        h1, .kpi-val { color:#0f172a; }
        h2 { color:#0369a1; border-color:#cbd5e1; }
        th { background:#f1f5f9; color:#0f172a; }
        td, th { border-color:#e2e8f0; }
        code { color:#b45309; }
        .kpi-sub, .meta-line, .muted { color:#475569; }
    }
</style>
</head>
<body>
<div class="container">
    <div class="top-bar">
        <div>
            <h1>${escapeHtml(reportTitle)}</h1>
            <div class="meta-line">Generated: <strong>${escapeHtml(nowStr)}</strong> • Source: <strong>${escapeHtml(state.activeSourceLabel)}</strong></div>
            <div class="meta-line">Material / Burner: <strong>${escapeHtml(fuelName)} (${escapeHtml(inp.formula || "")})</strong> • Regime: <strong>${escapeHtml(regimeBadge)}</strong> • ISS R² = <strong>${escapeHtml(String(r2Txt))}</strong>, RMSE = <strong>${escapeHtml(String(rmseTxt))}</strong></div>
            ${am.show_banner ? `<div class="meta-line" style="color:#6ee7b7; margin-top:3px;">${escapeHtml(am.en || am.tr || "")}</div>` : ""}
        </div>
        <button type="button" class="print-btn no-print" id="btn-print-pdf">Print / Save as PDF</button>
    </div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-lbl">Fire Risk Score</div>
            <div class="kpi-val">${tel.risk_score} / 100</div>
            <div class="kpi-sub">P_O₂: ${tel.o2_partial_psia ?? tel.po2_psia} psia (${tel.o2_partial_kpa ?? tel.po2_kpa} kPa)</div>
        </div>
        <div class="kpi">
            <div class="kpi-lbl">Flame Temperature (T_f)</div>
            <div class="kpi-val">${tel.flame_temp_k} K</div>
            <div class="kpi-sub">${tel.flame_temp_c} °C ${ub.temp_sigma_k ? `(±1σ: ${ub.temp_sigma_k} K)` : ""}</div>
        </div>
        <div class="kpi">
            <div class="kpi-lbl">Critical Oxygen (MOC)</div>
            <div class="kpi-val">${tel.moc_pct}%</div>
            <div class="kpi-sub">${ub.moc_lower_pct !== undefined ? `±1σ: [${ub.moc_lower_pct}%, ${ub.moc_upper_pct}%]` : ""}</div>
        </div>
        <div class="kpi">
            <div class="kpi-lbl">Burn Rate &amp; 0G Safe Entry</div>
            <div class="kpi-val">${tel.burning_rate_k_mm2_s} mm²/s</div>
            <div class="kpi-sub">Safe Re-Entry: ${pfc.safe_reentry_s ?? 0} s (Mist: ${pfc.safe_reentry_mist_s ?? 0} s)</div>
        </div>
    </div>

    <div class="charts-grid">
        <div class="card" style="margin-bottom:0;">
            <h2>1. Flammability Boundary Map (MOC &amp; ±1σ)</h2>
            ${svgChart1}
        </div>
        <div class="card" style="margin-bottom:0;">
            <h2>2. Multi-Sensor &amp; d²/d₀² Timeseries (0-30 s)</h2>
            ${svgChart2}
        </div>
        <div class="card" style="margin-bottom:0;">
            <h2>3. 0G Post-Fire Core Cooling &amp; Re-Ignition</h2>
            ${svgChart3}
        </div>
        <div class="card" style="margin-bottom:0;">
            <h2>4. Ranked NASA PSI Match &amp; MOC</h2>
            ${svgChart4}
        </div>
    </div>

    <section class="card">
        <h2>2. 5-Phase Mission Material Certification (NASA-STD-6001B)</h2>
        <table>
            <thead>
                <tr>
                    <th>Mission Phase</th>
                    <th>Gravity</th>
                    <th>Cabin Atmosphere</th>
                    <th>MOC</th>
                    <th>O₂ Margin</th>
                    <th>Certification</th>
                </tr>
            </thead>
            <tbody>${certRowsHtml}</tbody>
        </table>
    </section>

    <section class="card">
        <h2>3. Governing Equations, Dimensionless Numbers &amp; Cabin Safety</h2>
        <p class="meta-line" style="margin-top:0; margin-bottom:10px;">
            <strong>Atmosphere &amp; Scale:</strong> ${inp.gravity_g} G • ${inp.oxygen_pct}% O₂ • ${inp.pressure_psia} psia • U = ${inp.airflow_cms} cm/s (${escapeHtml(inp.flow_direction || "opposed")}) • D₀ = ${inp.droplet_d0_mm} mm • ${escapeHtml(inp.diluent || "N2")} |
            <strong>JSC-20584 SMAC:</strong> 24h (100 ppm) = ${tl.t_smac_24h_100ppm_s ?? "-"} s • 1h (425 ppm) = ${tl.t_smac_1h_425ppm_s ?? "-"} s • FED = ${tox.fed_total ?? 0} |
            <strong>SoFIE-MIST:</strong> D₃₂ = ${ste.mist_sauter_d32_um ?? "-"} µm (Water Saving: ${ste.mist_water_saving_pct ?? "-"}%)
        </p>
        <table>
            <thead>
                <tr>
                    <th>Physical Law</th>
                    <th>Governing Equation</th>
                    <th>Computed Value</th>
                    <th>Regime / Note</th>
                </tr>
            </thead>
            <tbody>${eqRowsHtml}</tbody>
        </table>
    </section>

    <section class="card">
        <h2>5. Top Ranked NASA PSI Investigations (NTRS Citations)</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Program / ID</th>
                    <th>Sample / Burner</th>
                    <th>Test Conditions</th>
                    <th>MOC</th>
                    <th>Match</th>
                    <th>NTRS</th>
                </tr>
            </thead>
            <tbody>${expRowsHtml}</tbody>
        </table>
    </section>

    ${aiSectionHtml}
</div>
<script>
    (function () {
        var btn = document.getElementById("btn-print-pdf");
        if (btn) {
            btn.addEventListener("click", function () {
                window.print();
            });
        }
    })();
</script>
</body>
</html>`;

        const blob = new Blob([htmlDoc], { type: "text/html;charset=utf-8" });
        const stamp = new Date().toISOString().slice(0, 16).replace(/[:T-]/g, "");
        triggerBlobDownload(blob, `ALTAR_NASA_Visual_Report_v6_3_${stamp}.html`);
        showToast("Visual Engineering Report (.html / Print-to-PDF) downloaded.");
    }

    function clearCopilotChat() {
        if (state.activeChatJobId) {
            cancelActiveChatJob();
        }
        state.chatHistory = [];
        const box = $("chat-messages-box");
        if (!box) return;
        box.innerHTML = `
            <div class="msg-bubble msg-ai console-readiness-card" id="welcome-ai-bubble">
                <h3 data-i18n="welcome_title">${escapeHtml(tStr("welcome_title"))}</h3>
                <div class="console-readiness-grid">
                    <div class="console-kv-item">
                        <div class="console-kv-label" data-i18n="kv_solver_lbl">${escapeHtml(tStr("kv_solver_lbl"))}</div>
                        <div class="console-kv-val" data-i18n="kv_solver_val">${escapeHtml(tStr("kv_solver_val"))}</div>
                    </div>
                    <div class="console-kv-item">
                        <div class="console-kv-label" data-i18n="kv_corpus_lbl">${escapeHtml(tStr("kv_corpus_lbl"))}</div>
                        <div class="console-kv-val">15 NASA PSI + NTRS + OSDR</div>
                    </div>
                    <div class="console-kv-item">
                        <div class="console-kv-label" data-i18n="kv_auditor_lbl">${escapeHtml(tStr("kv_auditor_lbl"))}</div>
                        <div class="console-kv-val">NASA-STD-6001B • JSC-20584 SMAC</div>
                    </div>
                </div>
                <p data-i18n="welcome_p1">${escapeHtml(tStr("welcome_p1"))}</p>
                <p style="margin-top:6px;" data-i18n="welcome_p2">${escapeHtml(tStr("welcome_p2"))}</p>
            </div>
        `;
        showToast("Analysis log reset.");
    }

    // =========================================================================
    // EVENT BINDINGS
    // =========================================================================
    document.addEventListener("DOMContentLoaded", () => {
        try {
            state.chamber3D = new window.Chamber3DEngine("three-canvas-container");
        } catch (err) {
            console.warn("Chamber3DEngine WebGL init skipped:", err);
            state.chamber3D = null;
        }
        if (window.SpacecraftUltraHDStudio) {
            try {
                state.spacecraftStudio = new window.SpacecraftUltraHDStudio({
                    apiFetch: apiFetch,
                    getLang: () => "en",
                    onHardwareStateChange: () => scheduleSimUpdate(),
                    onRequestAiCopilot: (compId, roomLabel) => {
                        const roomNamesEn = {
                            ORION_CM: "Command Section (Cockpit)",
                            IHAB: "Crew Living Section",
                            HALO: "Power & Electronics Section",
                            AIRLOCK: "Docking & Transfer Tunnel",
                            PPE: "Life Support & Air Unit",
                        };
                        const rEn = roomNamesEn[compId] || roomLabel || compId;
                        switchTab("tab-copilot");
                        sendChatMessage(
                            `Evaluate active fire safety, entry-exit hatch isolation, ventilation cutoff, cabin pressure rise, toxic gas accumulation, and water mist intervention in Orion MCP's '${rEn}' section using governing equations and matching NASA PSI experiments.`,
                            { fire_compartment_id: compId }
                        );
                    },
                });
            } catch (err) {
                console.warn("SpacecraftUltraHDStudio WebGL init skipped:", err);
                state.spacecraftStudio = null;
            }
        }
        state.sonifier = new window.AltarCharts.TelemetrySonifier("audio-scope-canvas");

        if ($("btn-vp-chamber")) {
            $("btn-vp-chamber").addEventListener("click", () => setLabViewportMode("chamber"));
        }
        if ($("btn-vp-spacecraft")) {
            $("btn-vp-spacecraft").addEventListener("click", () => setLabViewportMode("spacecraft"));
        }

        document.querySelectorAll(".nav-tab").forEach((btn) => {
            btn.addEventListener("click", () => switchTab(btn.dataset.tab));
        });
        $("header-engine-pill").addEventListener("click", () => switchTab("tab-settings"));
        $("header-stream-pill").addEventListener("click", () => switchTab("tab-live"));

        $("btn-export-report").addEventListener("click", exportScientificMissionReport);
        $("btn-export-csv").addEventListener("click", exportPredictiveCSV);
        $("btn-export-json").addEventListener("click", exportPredictiveJSON);
        $("btn-clear-chat").addEventListener("click", clearCopilotChat);

        $("sel-audience-mode").addEventListener("change", () => {
            state.audienceMode = $("sel-audience-mode").value;
            renderAudienceBanner();
        });
        $("chk-flight-overlay").addEventListener("change", () => {
            redrawActiveLabCharts();
        });
        $("sel-habitat-volume").addEventListener("change", () => {
            runSimulationUpdate("Habitat / Rover / Suit Switch");
        });
        $("sel-crew-response").addEventListener("change", () => {
            runSimulationUpdate("Crew Response Time");
        });

        $("inp-fuel").addEventListener("change", () => {
            syncCustomMaterialBox();
            runSimulationUpdate();
        });
        $("inp-diluent").addEventListener("change", () => runSimulationUpdate());
        ["inp-custom-mat-name", "inp-custom-rho", "inp-custom-lambda"].forEach((id) => {
            if ($(id)) {
                $(id).addEventListener("input", scheduleSimUpdate);
            }
        });
        if ($("btn-flow-opposed")) {
            $("btn-flow-opposed").addEventListener("click", () => {
                setFlowDirectionUI("opposed");
                runSimulationUpdate("Opposed Airflow");
            });
        }
        if ($("btn-flow-concurrent")) {
            $("btn-flow-concurrent").addEventListener("click", () => {
                setFlowDirectionUI("concurrent");
                runSimulationUpdate("Concurrent Airflow");
            });
        }
        syncCustomMaterialBox();
        setFlowDirectionUI(state.flowDirection);

        ["inp-gravity", "inp-oxygen", "inp-pressure", "inp-airflow", "inp-droplet"].forEach((id) => {
            $(id).addEventListener("input", scheduleSimUpdate);
        });

        $("inp-quick-lab-media").addEventListener("change", (e) => {
            if (e.target.files && e.target.files.length > 0) {
                ingestMediaBundle(e.target.files, true, "quick-lab-media-status");
            }
        });

        if ($("btn-reignite")) {
            $("btn-reignite").addEventListener("click", () => {
                if (state.chamber3D) state.chamber3D.reigniteDroplet();
                showToast("Hot-wire igniter triggered.");
            });
        }

        $("btn-audio-toggle").addEventListener("click", () => {
            const playing = state.sonifier.toggle();
            $("btn-audio-toggle").textContent = playing ? tStr("audio_stop") : tStr("audio_start");
            if (playing && state.currentSim) {
                state.sonifier.updateTelemetry(state.currentSim.telemetry);
            }
        });

        const triggerDeepSimAI = () => {
            switchTab("tab-copilot");
            sendChatMessage(
                "Evaluate my active 3D Combustion Chamber parameters, dimensionless numbers (K, B_oq, Sh, Re, Gr, Ra, Ri, Da, χ_r, MOC), ISS R² validation, and ECLSS survival timeline; rank matching NASA PSI experiments and provide spacecraft fire safety & Earth spinoff recommendations."
            );
        };
        $("btn-ai-interpret-sim").addEventListener("click", triggerDeepSimAI);
        $("btn-deep-ai-from-formula").addEventListener("click", triggerDeepSimAI);

        document.querySelectorAll(".hw-filter-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".hw-filter-btn").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                state.activeHardwareFilter = btn.dataset.hw || "ALL";
                refreshRankingTable();
            });
        });

        $("btn-run-rank").addEventListener("click", refreshRankingTable);
        $("inp-rank-query").addEventListener("keydown", (e) => {
            if (e.key === "Enter") refreshRankingTable();
        });
        $("btn-compare-selected").addEventListener("click", runComparisonUpdate);

        $("btn-stream-toggle").addEventListener("click", () => {
            configureContinuousStream(!state.streamEnabled, !state.streamEnabled);
        });
        $("btn-stream-poll-now").addEventListener("click", () => {
            configureContinuousStream(state.streamEnabled, true);
            showToast("Fetching live NASA data packet...");
        });
        $("sel-stream-source").addEventListener("change", () => {
            const v = $("sel-stream-source").value;
            const inp = $("inp-stream-target");
            if (v === "custom_url" && (inp.value === "auto" || !inp.value.startsWith("http"))) {
                inp.value = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69";
            } else if (v !== "custom_url" && inp.value.startsWith("http")) {
                inp.value = "auto";
            }
        });
        state.streamPollTimer = setInterval(() => {
            if (state.streamEnabled) {
                pollStreamStatusOnce();
            }
        }, 4000);

        $("btn-fetch-nasa-live").addEventListener("click", fetchLiveNasaData);
        $("inp-live-nasa-q").addEventListener("keydown", (e) => {
            if (e.key === "Enter") fetchLiveNasaData();
        });
        document.querySelectorAll(".quick-ntrs-btn").forEach((b) => {
            b.addEventListener("click", () => {
                $("inp-live-nasa-q").value = b.dataset.q;
                fetchLiveNasaData();
            });
        });

        $("btn-scrape-url").addEventListener("click", () => {
            executeUrlScrape($("inp-scrape-url").value);
        });
        $("inp-scrape-url").addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                executeUrlScrape($("inp-scrape-url").value);
            }
        });

        $("btn-upload-doc").addEventListener("click", () => {
            const fileInput = $("inp-doc-file");
            if (!fileInput.files || fileInput.files.length === 0) {
                showToast("Please select one or more flame photos or NASA PSI data files (.csv/.xlsx/.zip/.pdf/.json) first.");
                return;
            }
            ingestMediaBundle(fileInput.files, $("chk-media-autosync").checked, null);
        });

        if ($("btn-eval-custom-eq")) {
            $("btn-eval-custom-eq").addEventListener("click", evaluateCustomEquation);
        }
        if ($("inp-custom-eq")) {
            $("inp-custom-eq").addEventListener("keydown", (e) => {
                if (e.key === "Enter") evaluateCustomEquation();
            });
        }
        if ($("sel-custom-eq-target")) {
            $("sel-custom-eq-target").addEventListener("change", () => {
                if ($("inp-custom-eq") && $("inp-custom-eq").value.trim()) {
                    evaluateCustomEquation();
                }
            });
        }
        document.querySelectorAll(".custom-eq-preset-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                if ($("inp-custom-eq") && btn.dataset.eq) {
                    $("inp-custom-eq").value = btn.dataset.eq;
                }
                if ($("sel-custom-eq-target") && btn.dataset.target) {
                    $("sel-custom-eq-target").value = btn.dataset.target;
                }
                evaluateCustomEquation();
            });
        });

        $("btn-rag-search").addEventListener("click", async () => {
            const q = $("inp-rag-search").value.trim();
            if (!q) return;
            const res = await apiFetch(`/api/rag-search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            state.lastRagResults = data.results || [];
            renderRagSearchResults();
        });

        $("btn-send-chat").addEventListener("click", () => sendChatMessage());
        $("btn-cancel-chat").addEventListener("click", cancelActiveChatJob);
        $("inp-chat-msg").addEventListener("keydown", (e) => {
            if (e.key === "Enter") sendChatMessage();
        });
        document.querySelectorAll(".copilot-prompt-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                const p = btn.dataset.promptEn || btn.dataset.prompt || "";
                if (p) sendChatMessage(p);
            });
        });
        $("sel-copilot-provider").addEventListener("change", () => {
            $("cfg-active-provider").value = $("sel-copilot-provider").value;
            saveAllSettings(true);
        });
        $("inp-chat-image").addEventListener("change", (e) => {
            if (!e.target.files || e.target.files.length === 0) return;
            ingestMediaBundle(e.target.files, true, null);
        });
        $("chk-deep-6stage").addEventListener("change", () => saveAllSettings(true));

        $("btn-save-config").addEventListener("click", () => saveAllSettings(false));
        $("btn-save-directives").addEventListener("click", () => saveAllSettings(false));
        $("btn-refresh-ollama").addEventListener("click", async () => {
            showToast("Checking local model and system bridge...");
            const [resOll, resAgy] = await Promise.all([
                apiFetch("/api/ollama/status"),
                apiFetch("/api/antigravity/status"),
            ]);
            const stOll = await resOll.json();
            const stAgy = await resAgy.json();
            populateOllamaDropdown(stOll, $("cfg-ollama-model").value);
            const agyKeyCfg = Boolean(
                (state.lastConfigData && state.lastConfigData.antigravity_api_key_configured) ||
                ($("cfg-antigravity-key") && $("cfg-antigravity-key").value.trim())
            );
            populateLocalBridgeDropdown(stAgy, $("cfg-agy-model").value, agyKeyCfg);
            showToast(`Local Model: ${stOll.online ? "Online" : "Offline"} | System Bridge: ${stAgy.cli_ready ? "Ready" : "Inactive"}`);
        });

        $("btn-test-provider").addEventListener("click", async () => {
            const out = $("provider-test-output");
            const prov = $("cfg-active-provider").value;
            out.style.color = "#93c5fd";
            out.textContent = `Testing '${formatKernelDisplayName(prov)}'...`;
            await saveAllSettings(true);
            try {
                const res = await apiFetch("/api/providers/test", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ provider: prov }),
                });
                const d = await res.json();
                if (d.ok) {
                    out.style.color = "#6ee7b7";
                    out.innerHTML = `<strong>${escapeHtml(formatKernelDisplayName(d.provider))} (${escapeHtml(d.model)})</strong> — ${d.latency_s} s:<br/><em>"${escapeHtml(d.sample)}"</em>`;
                } else {
                    out.style.color = "#fca5a5";
                    out.textContent = `${d.error || d.note || "Failed"}`;
                }
            } catch (err) {
                out.style.color = "#fca5a5";
                out.textContent = formatFriendlyError(err);
            }
        });

        $("btn-ollama-pull").addEventListener("click", async () => {
            const m = $("inp-ollama-pull").value.trim();
            if (!m) return;
            showToast(`Downloading '${m}'...`);
            const res = await apiFetch("/api/ollama/pull", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ model: m }),
            });
            const data = await res.json();
            showToast(data.ok ? `'${m}' ready.` : `${data.error}`);
            if (data.ok) $("btn-refresh-ollama").click();
        });

        $("btn-ollama-unload").addEventListener("click", async () => {
            const res = await apiFetch("/api/ollama/unload", { method: "POST" });
            const d = await res.json();
            showToast(`${d.unloaded || 0} models cleared from memory.`);
        });

        window.addEventListener("resize", () => {
            redrawActiveLabCharts();
        });

        applyLanguageToDOM();
        renderAudienceBanner();
        loadSystemBootstrap();
    });
})();
