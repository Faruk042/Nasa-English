# -*- coding: utf-8 -*-
"""
ALTAR-NASA Intelligent Scope Guard, Physical Misconception Detector, and Action Recommender (`scope_guard.py`).
- Standard-library only (`< 1 ms` runtime per query).
- Mixed-clause casual small-talk stripping plus character 3-gram + Damerau-Levenshtein typo tolerance.
- History-poisoning-resistant follow-up resolution.
- Concise, natural aerospace engineering English across all badges, notes, and suggested actions.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

_SUBSCRIPT_ASCII_TABLE = str.maketrans(
    {
        "₂": "2",
        "²": "2",
        "₀": "0",
        "₁": "1",
        "₃": "3",
        "µ": "u",
    }
)

# Canonical domain vocabulary for typo tolerance (canonical_term, mapped_term)
_CANONICAL_DOMAIN_VOCAB: Tuple[Tuple[str, str], ...] = (
    ("saffire", "saffire"),
    ("sofie", "sofie"),
    ("spalding", "spalding"),
    ("sherwood", "sherwood"),
    ("reynolds", "reynolds"),
    ("grashof", "grashof"),
    ("rayleigh", "rayleigh"),
    ("richardson", "richardson"),
    ("damkohler", "damkohler"),
    ("schumann", "schumann"),
    ("semenov", "semenov"),
    ("kamenetskii", "kamenetskii"),
    ("microgravity", "microgravity"),
    ("gravity", "gravity"),
    ("oxygen", "oxygen"),
    ("methanol", "methanol"),
    ("heptane", "heptane"),
    ("ethanol", "ethanol"),
    ("hydrogen", "hydrogen"),
    ("propane", "propane"),
    ("toluene", "toluene"),
    ("nomex", "nomex"),
    ("sibal", "sibal"),
    ("kapton", "kapton"),
    ("teflon", "teflon"),
    ("halon", "halon"),
    ("combustion", "combustion"),
    ("flammability", "flammability"),
    ("ignition", "ignition"),
    ("extinguish", "extinguish"),
    ("suppression", "suppression"),
    ("ventilation", "ventilation"),
    ("airflow", "airflow"),
    ("radiometer", "radiometer"),
    ("thermocouple", "thermocouple"),
    ("detector", "detector"),
    ("pyrolysis", "pyrolysis"),
    ("convection", "convection"),
    ("diffusion", "diffusion"),
    ("radiative", "radiative"),
    ("spherical", "spherical"),
    ("buoyancy", "buoyancy"),
    ("spacesuit", "spacesuit"),
    ("spacecraft", "spacecraft"),
    ("orion", "orion"),
    ("gateway", "gateway"),
    ("cygnus", "cygnus"),
    ("artemis", "artemis"),
    ("camras", "camras"),
    ("eclss", "eclss"),
)

# Direct in-scope phrases searched against normalized ASCII text
_DIRECT_DOMAIN_PHRASES: Tuple[str, ...] = (
    "combustion",
    "flammability",
    "water mist",
    "fine mist",
    "cool flame",
    "spherical flame",
    "candle flame",
    "zero gravity",
    "zero-g",
    "flame in vacuum",
    "fire in vacuum",
    "burn in vacuum",
    "in space",
    "spacecraft",
    "microgravity",
    "freefall",
    "free-fall",
    "partial gravity",
    "lunar gravity",
    "mars gravity",
    "0g",
    "0.0g",
    "0.16g",
    "0.38g",
    "1g",
    "oxygen",
    "pressure",
    "psia",
    "kpa",
    "cm/s",
    "mm2/s",
    "kw/m2",
    "carbon monoxide",
    "co ppm",
    "formaldehyde",
    "smac",
    "eclss",
    "camras",
    "fdir",
    "spalding",
    "b_oq",
    "boq",
    "sherwood",
    "reynolds",
    "grashof",
    "rayleigh",
    "richardson",
    "damkohler",
    "d2-law",
    "d2 law",
    "de ris",
    "burke-schumann",
    "burke schumann",
    "chi_r",
    "radiative",
    "convection",
    "diffusion",
    "pyrolysis",
    "soot",
    "standoff",
    "rf/rd",
    "r_f",
    "hrrpua",
    "semenov",
    "kamenetskii",
    "heptane",
    "methanol",
    "ethanol",
    "propane",
    "hydrogen",
    "toluene",
    "pmma",
    "nomex",
    "sibal",
    "kapton",
    "teflon",
    "ptfe",
    "peek",
    "xlpe",
    "halon",
    "saffire",
    "sofie",
    "flex-2",
    "bass-ii",
    "spice",
    "slice",
    "daft",
    "cfi-g",
    "cfig",
    "luci",
    "fm2",
    "ntrs",
    "osdr",
    "nasa psi",
    "psi-",
    "6001b",
    "20584",
    "eva suit",
    "spacesuit",
    "lunar rover",
    "pressurized rover",
    "lunar habitat",
    "mars habitat",
    "orion",
    "gateway",
    "cygnus",
    "space station",
    "station cabin",
    "cabin",
    "hatch",
    "return duct",
    "ventilation duct",
    "airflow",
    "thermal camera",
    "optical camera",
    "smoke",
    "regolith",
    "lunar dust",
    "re-ignition",
    "reignition",
    "uncertainty",
    "custom equation",
    "custom material",
    "firefighter",
    "scba",
)

_RE_DOMAIN_SHORT_TOKENS = re.compile(
    r"\b(?:flex|bass|acme|same|cfi|moc|iss|eva|mie|fed|ntc|psd|cir|msg|mdca|halo|ihab|ppe|o2|co2|n2|r2|rmse)\b"
)

_RE_NATURAL_COMBUSTION_TOKENS = re.compile(
    r"\b(?:flame|flames|fire|fires|burn|burns|burning|burned|candle|candles|"
    r"ignite|ignites|ignited|ignition|extinguish|extinguisher|extinguishing|"
    r"quench|quenches|quenching|smolder|smoldering|buoyancy|convective|"
    r"spherical|weightless|weightlessness)\b"
)

_RE_STRONG_SPACE_ANCHORS = re.compile(
    r"(?:^|\b)(?:0g|0\.0g|0\.16g|0\.38g|microgravity|freefall|saffire|sofie|"
    r"flex|bass|moc|spalding|sherwood|damkohler|orion|iss|nasa|cabin)(?:\b|$)"
)

_STRONG_SPACE_ANCHOR_PHRASES: Tuple[str, ...] = (
    "spacecraft",
    "space station",
    "water mist",
    "fine water mist",
)

_SHORT_GREETINGS: Tuple[str, ...] = (
    "hello",
    "hi",
    "hey",
    "greetings",
    "good morning",
    "good afternoon",
    "good evening",
)

_RE_CASUAL_GREETING_TOKENS = re.compile(r"\b(?:hello|hi|hey)\b")

# Platform capability / overview questions (treated as in-scope meta queries)
_PLATFORM_INTRO_PHRASES: Tuple[str, ...] = (
    "what can you do",
    "what can this platform do",
    "how to use",
    "how do i use",
    "platform features",
    "features of this platform",
    "what are the features",
    "capabilities",
    "your capabilities",
    "who are you",
    "introduce yourself",
    "what is this app",
    "what is this platform",
    "this platform",
    "this console",
    "this application",
    "altar-nasa",
    "flame in freefall",
)

# Explicit off-topic and polysemy/idiom phrases (also blocks follow-up inheritance)
_EXPLICIT_OFF_TOPIC_PHRASES: Tuple[str, ...] = (
    "lentil",
    "soup",
    "recipe",
    "pasta recipe",
    "bake a cake",
    "cookie recipe",
    "cooking recipe",
    "dinner recipe",
    "match score",
    "football",
    "soccer",
    "soccer match",
    "world cup",
    "champions league",
    "basketball",
    "stock price",
    "stock market",
    "crypto",
    "crypto market",
    "bitcoin",
    "ethereum",
    "forex",
    "horoscope",
    "astrology",
    "gossip",
    "celebrity",
    "movie recommendation",
    "tv show",
    "song lyrics",
    "write a poem",
    "tell a joke",
    "bedtime story",
    "snake game",
    "flappy bird",
    "tetris",
    "write a game",
    "game code",
    "free fire",
    "build a website",
    "shopping cart",
    "election result",
    "politics",
    "dating advice",
    "weather forecast",
    "burn calories",
    "calorie",
    "heartburn",
    "acid reflux",
    "what medicine",
    "sunburn",
    "burnout",
    "burn out",
    "burn out at work",
    "fire an employee",
    "fire someone",
    "got fired",
    "fired from work",
    "ceasefire",
    "open fire",
    "high fever",
    "fever medicine",
)

# Casual small-talk / weather clauses stripped from mixed domain questions
_CASUAL_CLAUSE_PHRASES: Tuple[str, ...] = (
    "nice weather today",
    "nice weather",
    "lovely weather",
    "great weather",
    "weather forecast",
    "weather is nice",
    "weather is rainy",
    "weather is cold",
    "weather is warm",
    "it is raining today",
    "it is sunny today",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "hope you are well",
    "hope you are doing well",
)

# Follow-up patterns allowed only immediately after a valid in-scope turn
_FOLLOWUP_PATTERNS: Tuple[str, ...] = (
    "summarize",
    "summarize this",
    "make it shorter",
    "shorter",
    "simpler",
    "simplify",
    "in a table",
    "put in a table",
    "as a table",
    "show as bullets",
    "bullet points",
    "explain row",
    "first row",
    "second row",
    "third row",
    "last row",
    "what if i increase",
    "what if i decrease",
    "what if we double",
    "what if we halve",
    "why does that",
    "how did you calculate",
    "compare them",
    "elaborate",
    "explain this result",
    "explain this value",
)

_MEDIA_FOLLOWUP_PATTERNS: Tuple[str, ...] = (
    "uploaded",
    "attached",
    "this file",
    "this image",
    "this photo",
    "this dataset",
    "this table",
    "analyze this",
    "inspect this",
    "evaluate this",
)

# Role-override and safety-bypass patterns
_ROLE_OVERRIDE_PHRASES: Tuple[str, ...] = (
    "ignore previous instructions",
    "ignore previous rules",
    "ignore all instructions",
    "ignore all rules",
    "ignore safety rules",
    "forget previous rules",
    "forget all rules",
    "forget your instructions",
    "disregard previous",
    "disregard safety",
    "bypass safety",
    "override safety",
    "remove restrictions",
    "you are now a",
    "act as a chef",
    "act as a poet",
    "act as a playwright",
)

_HALON_ENDORSE_VERBS: Tuple[str, ...] = (
    "recommend halon",
    "endorse halon",
    "approve halon",
    "use halon 1301",
    "allow halon",
    "say halon 1301 is safe",
    "say halon is safe",
    "say using halon is right",
    "tell me to use halon",
)

# Assistant markers indicating the previous turn was declined as off-topic or rule-locked
_REJECTED_ASSISTANT_MARKERS: Tuple[str, ...] = (
    "focuses exclusively on spacecraft fire safety",
    "only covers spacecraft fire safety",
    "flight safety rules are fixed",
    "flight and fire safety rules are fixed",
)

# Unverified / fabricated experiment index sanitizers (valid catalog: Saffire I-VI / 1-6, FLEX / FLEX-2 / FLEX-2J, BASS / BASS-II / BASS-M, SoFIE, SPICE, SLICE, DAFT / DAFT-2)
_RE_FAKE_SAFFIRE_ROMAN = re.compile(r"\bSaffire[-\s]+(?:VII|VIII|IX|X|XI|XII|XIII|XIV|XV)\b", flags=re.IGNORECASE)
_RE_FAKE_SAFFIRE_NUM = re.compile(r"\bSaffire[-\s]+(?:[789]|\d{2,})\b", flags=re.IGNORECASE)
_RE_FAKE_FLEX = re.compile(r"\bFLEX[-\s]+(?:[3-9]|\d{2,}|III|IV|V|VI|VII|VIII|IX|X)\b", flags=re.IGNORECASE)
_RE_FAKE_BASS = re.compile(r"\bBASS[-\s]+(?:[3-9]|\d{2,}|III|IV|V|VI|VII|VIII|IX|X)\b", flags=re.IGNORECASE)
_RE_FAKE_SOFIE = re.compile(r"\bSoFIE[-\s]+(?:[2-9]|\d{2,}|II|III|IV|V|VI|VII|VIII|IX|X)\b", flags=re.IGNORECASE)
_RE_FAKE_SPICE_SLICE = re.compile(r"\b(SPICE|SLICE|ACME)[-\s]+(?:[2-9]|\d{2,}|II|III|IV|V|VI|VII|VIII|IX|X)\b", flags=re.IGNORECASE)


def normalize_scope_text(raw: str) -> str:
    txt = str(raw or "").translate(_SUBSCRIPT_ASCII_TABLE)
    decomposed = unicodedata.normalize("NFKD", txt)
    ascii_folded = "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", ascii_folded).strip()


def _char_trigrams(word: str) -> Set[str]:
    padded = f"^{word}$"
    if len(padded) < 3:
        return {padded}
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


def _trigram_dice(a: str, b: str) -> float:
    ga = _char_trigrams(a)
    gb = _char_trigrams(b)
    if not ga or not gb:
        return 0.0
    return (2.0 * len(ga & gb)) / float(len(ga) + len(gb))


def _damerau_levenshtein(a: str, b: str) -> int:
    la, lb = len(a), len(b)
    if a == b:
        return 0
    if la == 0:
        return lb
    if lb == 0:
        return la
    d = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        d[i][0] = i
    for j in range(lb + 1):
        d[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            val = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                val = min(val, d[i - 2][j - 2] + 1)
            d[i][j] = val
    return d[la][lb]


_PRECOMPUTED_VOCAB = tuple((term, canon, _char_trigrams(term)) for term, canon in _CANONICAL_DOMAIN_VOCAB)
_EXACT_VOCAB_MAP = {term: canon for term, canon in _CANONICAL_DOMAIN_VOCAB}


def _match_fuzzy_domain_tokens(norm_text: str) -> Tuple[List[Tuple[str, str]], str]:
    """
    Match domain typos such as 'sfafire', 'spaldng', 'microgravty', 'haln', 'methnol', 'nomx', 'oxygn'
    using character 3-grams combined with Damerau-Levenshtein edit similarity.
    """
    tokens = re.findall(r"[a-z0-9_]+", norm_text)
    matched: List[Tuple[str, str]] = []
    repaired_words: Dict[str, str] = {}

    for tok in tokens:
        if len(tok) < 4 or tok.isdigit():
            continue
        if tok in _EXACT_VOCAB_MAP:
            matched.append((tok, _EXACT_VOCAB_MAP[tok]))
            continue

        phonetic_tok = tok.replace("ks", "x")
        tok_grams = _char_trigrams(tok)
        best_canon = ""
        best_score = 0.0

        for term, canon, term_grams in _PRECOMPUTED_VOCAB:
            if abs(len(tok) - len(term)) > 2 and abs(len(phonetic_tok) - len(term)) > 2:
                continue
            shared_grams = len(tok_grams & term_grams)
            if shared_grams == 0 and phonetic_tok == tok:
                continue
            dice_raw = (2.0 * shared_grams) / float(len(tok_grams) + len(term_grams))
            max_len = float(max(len(tok), len(term)))
            if max_len <= 5 and tok[0] != term[0]:
                continue
            if dice_raw < 0.22 and tok[0] != term[0] and phonetic_tok == tok:
                continue
            dist = _damerau_levenshtein(tok, term)
            if phonetic_tok != tok and dist > 1:
                dist = min(dist, _damerau_levenshtein(phonetic_tok, term))
            edit_sim = 1.0 - (dist / max_len)
            combined = 0.45 * dice_raw + 0.55 * edit_sim

            if max_len <= 5:
                is_hit = dist <= 1 and tok[0] == term[0]
            else:
                is_hit = (dist <= 1 and edit_sim >= 0.78) or (
                    dist <= 2 and dice_raw >= 0.42 and combined >= 0.64 and tok[0] == term[0]
                )

            if is_hit and combined > best_score:
                best_score = combined
                best_canon = canon

        if best_canon:
            matched.append((tok, best_canon))
            repaired_words[tok] = best_canon

    if not repaired_words:
        return matched, norm_text

    repaired_norm = norm_text
    for wrong_w, right_w in repaired_words.items():
        repaired_norm = re.sub(rf"\b{re.escape(wrong_w)}\b", right_w, repaired_norm)
    return matched, repaired_norm


def _has_any(text: str, phrases: Sequence[str]) -> bool:
    return any(p in text for p in phrases)


def _has_strong_space_anchor(norm_text: str) -> bool:
    if _RE_STRONG_SPACE_ANCHORS.search(norm_text):
        return True
    return _has_any(norm_text, _STRONG_SPACE_ANCHOR_PHRASES)


def _clause_has_domain_signal(clause_norm: str) -> bool:
    if _has_any(clause_norm, _EXPLICIT_OFF_TOPIC_PHRASES) and not _has_strong_space_anchor(clause_norm):
        return False
    if _has_any(clause_norm, _DIRECT_DOMAIN_PHRASES):
        return True
    if _RE_DOMAIN_SHORT_TOKENS.search(clause_norm):
        return True
    if _RE_NATURAL_COMBUSTION_TOKENS.search(clause_norm):
        return True
    fuzzy_hits, _ = _match_fuzzy_domain_tokens(clause_norm)
    return len(fuzzy_hits) > 0


def _strip_casual_clauses(raw_message: str) -> Tuple[str, bool]:
    """
    Strip casual opening clauses (e.g., 'Nice weather today, why does methanol transition to a cool flame in 0G?')
    while preserving the core combustion question intact.
    """
    parts = re.split(
        r"(?:[.!?;]+|,\s*(?=(?:by the way|anyway|also|however|so\b))|\b(?:by the way|anyway)\b|,)",
        raw_message,
        flags=re.IGNORECASE,
    )
    if len(parts) <= 1:
        return raw_message.strip(), False

    kept_parts: List[str] = []
    dropped_any = False
    for raw_p in parts:
        p_clean = raw_p.strip(" ,;:-")
        if not p_clean:
            continue
        p_norm = normalize_scope_text(p_clean)
        has_dom = _clause_has_domain_signal(p_norm)
        is_casual = _has_any(p_norm, _CASUAL_CLAUSE_PHRASES) or bool(_RE_CASUAL_GREETING_TOKENS.search(p_norm))
        if is_casual and not has_dom:
            dropped_any = True
            continue
        kept_parts.append(p_clean)

    if dropped_any and kept_parts:
        joined = ", ".join(kept_parts).strip()
        joined = re.sub(r"^(?:by the way|anyway|also|however|so|and|but)\s+", "", joined, flags=re.IGNORECASE).strip()
        if _clause_has_domain_signal(normalize_scope_text(joined)):
            return joined, True
    return raw_message.strip(), False


def detect_physical_misconception(norm_text: str) -> Optional[Dict[str, str]]:
    """
    Detect 4 common physical misconceptions in in-scope spacecraft combustion questions and return
    a concise one-sentence engineering correction.
    """
    # 1) Rising smoke / ceiling smoke accumulation in 0G microgravity or space stations
    has_zero_g_ctx = _has_any(
        norm_text,
        (
            "0g",
            "0.0g",
            "zero gravity",
            "zero-g",
            "weightless",
            "microgravity",
            "freefall",
            "free-fall",
            "space station",
            "station cabin",
            "iss",
        ),
    )
    has_ceiling_rise = _has_any(
        norm_text,
        (
            "ceiling smoke",
            "ceiling smoke detector",
            "ceiling smoke detectors",
            "ceiling detector",
            "ceiling detectors",
            "smoke on the ceiling",
            "smoke rising",
            "rising smoke",
            "rising hot air",
            "rise to the ceiling",
            "rises to the ceiling",
            "collects on the ceiling",
            "accumulates at the ceiling",
        ),
    ) or bool(
        re.search(
            r"\b(?:smoke|hot\s+air|heat|fumes)\b.{0,28}\b(?:rise|rises|rising|collect|collects|accumulate|accumulates)\b",
            norm_text,
        )
    )
    if has_zero_g_ctx and has_ceiling_rise:
        corr = (
            "In 0G microgravity, buoyancy vanishes so smoke and hot gas do not rise or collect at the ceiling; "
            "they drift with cabin airflow toward return ducts, which is where smoke sensors are mounted."
        )
        return {
            "code": "zero_g_ceiling_smoke",
            "correction_tr": corr,
            "correction_en": corr,
        }

    # 2) Sustaining a gas-phase flame or candle in 0% oxygen or vacuum without an oxidizer
    has_zero_o2 = bool(
        re.search(r"(?:%\s*0\s*(?:o2|oxygen)|0\s*%\s*(?:o2|oxygen)|zero\s+oxygen)", norm_text)
        or (
            (
                _has_any(
                    norm_text,
                    (
                        "flame in vacuum",
                        "burn in vacuum",
                        "fire in vacuum",
                        "candle in vacuum",
                    ),
                )
                or bool(
                    re.search(
                        r"\b(?:flame|fire|candle)\b.{0,32}\b(?:in\s+(?:space\s+)?vacuum|zero\s+oxygen|0\s*%\s*oxygen)",
                        norm_text,
                    )
                )
            )
            and not _has_any(norm_text, ("rocket", "thruster", "oxidizer"))
        )
    )
    if has_zero_o2 and not _has_any(norm_text, ("quench", "cannot burn", "extinguish")):
        corr = (
            "Below the minimum oxygen concentration (`O₂ < MOC`) or in vacuum without a supplied oxidizer, "
            "a gas-phase flame cannot sustain combustion and quenches."
        )
        return {
            "code": "vacuum_or_zero_o2_flame",
            "correction_tr": corr,
            "correction_en": corr,
        }

    # 3) Opening a sealed compartment hatch to ventilate before the hot core cools
    has_hot_premature_open = _has_any(
        norm_text, ("hatch", "ventilat", "unseal", "open the bay", "open compartment")
    ) and (
        _has_any(
            norm_text,
            (
                "before cooling",
                "while still hot",
                "open immediately",
                "right after extinguishing",
            ),
        )
        or bool(re.search(r"\b(?:open|unseal)\b.{0,25}\b(?:immediately|right\s+away|instantly|before\s+cooling)\b", norm_text))
        or bool(re.search(r"\b(?:immediately|right\s+away|instantly)\b.{0,20}\b(?:open|unseal|ventilate)\b", norm_text))
    )
    if has_hot_premature_open:
        corr = (
            "Opening the compartment hatch to admit fresh oxygen before the hot core cools below `525 K` "
            "triggers flash re-ignition; keep the bay sealed until cooling and air scrubbing finish."
        )
        return {
            "code": "premature_hatch_reignition",
            "correction_tr": corr,
            "correction_en": corr,
        }

    # 4) Pouring bulk liquid water from a bucket/cup onto a 0G cabin fire
    has_space_cabin_ctx = _has_any(
        norm_text,
        (
            "0g",
            "0.0g",
            "zero gravity",
            "zero-g",
            "weightless",
            "microgravity",
            "freefall",
            "free-fall",
            "in space",
            "spacecraft",
            "space station",
            "iss",
            "orion",
            "cabin",
        ),
    )
    has_bulk_water = (
        _has_any(
            norm_text,
            (
                "pour water",
                "pouring water",
                "bucket of water",
                "splash water",
                "throw water",
            ),
        )
        or bool(re.search(r"\b(?:pour|pouring|splash|splashing|throw|throwing|dump|dumping)\b.{0,22}\bwater\b", norm_text))
    )
    if (
        has_space_cabin_ctx
        and has_bulk_water
        and not _has_any(norm_text, ("oil", "grease", "kitchen"))
        and not _has_any(norm_text, ("water mist", "fine mist", "sofie-mist"))
    ):
        corr = (
            "In 0G microgravity, poured bulk water forms floating spheres under surface tension that miss the "
            "flame sheet and risk shorting cabin electronics, so crews deploy 25–40 µm fine water mist (`SoFIE-MIST`) instead."
        )
        return {
            "code": "zero_g_bulk_water",
            "correction_tr": corr,
            "correction_en": corr,
        }

    return None


def _detect_boundary_category(norm_text: str) -> Optional[str]:
    """
    Boundary categories bridged directly to spacecraft fire safety:
    - 'rocket_engine': High-velocity rocket propulsion / external thruster combustion (CON-08)
    - 'space_equipment': Routine ISS crew equipment (food warmers, sleeping bags, solar arrays)
    - 'terrestrial_fire': Household grease/kitchen fires, home smoke detectors, building fires
    """
    if _has_any(
        norm_text,
        (
            "rocket engine",
            "rocket motor",
            "rocket thruster",
            "rocket combustion",
            "rocket nozzle",
            "liquid rocket",
            "solid rocket",
            "thruster plume",
            "propellant engine",
        ),
    ) or (
        _has_any(norm_text, ("rocket", "thruster"))
        and _has_any(norm_text, ("combustion", "flame", "nozzle", "propellant", "engine"))
    ):
        return "rocket_engine"

    if _has_any(
        norm_text,
        (
            "food warmer",
            "galley oven",
            "sleeping bag",
            "solar panel",
            "solar array",
            "microwave oven",
            "coffee machine",
            "crew laptop",
        ),
    ):
        return "space_equipment"

    has_space_ctx_for_water = _has_any(
        norm_text,
        (
            "0g",
            "0.0g",
            "zero gravity",
            "zero-g",
            "weightless",
            "microgravity",
            "freefall",
            "space",
            "iss",
            "orion",
            "cabin",
        ),
    )

    if _has_any(
        norm_text,
        (
            "grease fire",
            "cooking oil fire",
            "kitchen fire",
            "house fire",
            "apartment fire",
            "forest fire",
            "wildfire",
            "pour water on oil",
            "home smoke detector",
        ),
    ) or (_has_any(norm_text, ("pour water on grease",)) and not has_space_ctx_for_water):
        return "terrestrial_fire"

    if _has_any(norm_text, ("how does a smoke detector work", "how do smoke detectors work")) and not _has_any(
        norm_text, ("0g", "iss", "space", "daft", "same")
    ):
        return "terrestrial_fire"

    return None


def build_boundary_response(
    boundary_kind: str,
    norm_text: str,
    active_sim: Optional[Dict[str, Any]] = None,
    lang: str = "en",
) -> str:
    """
    State the domain boundary concisely in the opening sentence and immediately connect the topic
    to spacecraft cabin fire safety physics.
    """
    _ = lang
    inp = (active_sim or {}).get("inputs") or {}
    tel = (active_sim or {}).get("telemetry") or {}
    u_cms = inp.get("airflow_cms", 2.0)
    re_val = tel.get("reynolds_number", 18.0)
    ri_val = tel.get("richardson_number", 0.0)

    if boundary_kind == "rocket_engine":
        return (
            "High-velocity rocket engines and external thrusters sit outside cabin combustion testing, "
            "yet they link to spacecraft fire safety through flow-regime scaling and pressurized oxidizer line protection.\n\n"
            f"- **High-Speed Jet vs. Cabin Airflow (`Ri = Gr / Re²`):** Rocket chambers inject propellants at `100–3000 m/s` (`Re > 10⁵`, `Ri < 10⁻⁶`), so momentum dominates and gravity has negligible effect on the flame. Inside crew cabins (`U = {u_cms} cm/s`, `Re = {re_val}`, `Ri = {ri_val}`), gentle ventilation means removing buoyancy turns flames spherical, increases radiative loss (`χ_r`), and shifts `MOC`.\n"
            "- **Cabin Leak Hazard:** Service-module and docking oxidizer/fuel lines are isolated by sealed bulkheads and continuous pressure/gas sensors so a line leak cannot enrich cabin `P_O₂` or lower minimum ignition energy (`MIE`)."
        )

    if boundary_kind == "space_equipment":
        if _has_any(norm_text, ("sleeping bag",)):
            return (
                "Crew sleeping-bag comfort design belongs to general cabin outfitting, but in spacecraft fire safety "
                "it is evaluated as a large textile surface exposed to low-velocity cabin ventilation.\n\n"
                "- **Material Behavior (`Nomex / SIBAL`):** Gentle `0G` airflow (`3–8 cm/s`) feeds fresh oxygen to thin fabric edges and can lower `MOC` below `1G` Earth limits (`BASS` and `Saffire` findings), so crew sleep stations use flame-resistant `Nomex` weaves certified under `NASA-STD-6001B`.\n"
                "- **Early Smoldering Protection:** Sleep bays monitor `CO` accumulation continuously; if overheating or smoldering starts, closing ventilation ducts starves the reaction zone of oxygen."
            )

        if _has_any(norm_text, ("solar panel", "solar array")):
            return (
                "External solar arrays operate in hard vacuum where gas-phase flames cannot burn, yet they connect directly "
                "to cabin fire safety through high-power `120V DC` electrical distribution.\n\n"
                "- **Internal Bus Overheating & Arc Risk:** Power generated by the arrays enters pressurized modules through switching units (`PCDU / SSPC`), where overloaded harnesses in stagnant `0G` air (`Ra = 0`) can overheat and pyrolyze `Kapton / PTFE` wire insulation.\n"
                "- **Preventive Isolation:** When thermal or ultrasonic arc sensors detect pre-ignition heating, cutting bay `120V DC` power and cabin airflow stops ignition before open flame develops."
            )

        return (
            "Everyday crew appliances such as cabin food warmers sit outside combustion experiments as routine hardware, "
            "but in spacecraft fire safety they are treated as localized thermal overheating and ignition sources.\n\n"
            "- **`0G` Stagnant-Heat Buildup (`Ra = 0`):** Without buoyancy to carry warm air upward, heat concentrates around heating elements and wiring harnesses (`Semenov` thermal runaway risk).\n"
            "- **Containment & Response:** Enclosures use flame-retardant `Nomex` and metallic barriers (`NASA-STD-6001B`); if temperature or `CO` rises, bay `120V DC` power and ventilation fans are shut off immediately."
        )

    if _has_any(norm_text, ("smoke detector",)) and not _has_any(norm_text, ("oil", "grease")):
        return (
            "Household smoke detectors belong to everyday building safety, yet their light-scattering physics directly "
            "connects to spacecraft fire detection and NASA's terrestrial technology transfers.\n\n"
            "- **Earth vs. `0G` Soot & Cool Flames:** Standard photoelectric detectors sense visible soot particles, but in `0G` flames can transition into soot-free `550–780 K` cool flames that optical sensors miss, requiring `CO` gas analyzers and `UV/IR` radiometers.\n"
            "- **Space-to-Earth Transfer (`SAME / DAFT`):** Multi-angle laser scattering developed for ISS and Lunar dust rejection now reduces false alarms from dust and steam in terrestrial buildings, mines, and aircraft cargo bays."
        )

    return (
        "Household kitchen and grease fires belong to terrestrial safety rather than orbital testing, yet water droplet "
        "size physics directly explains both why bulk water fails on hot oil and how spacecraft water-mist extinguishers work.\n\n"
        "- **Bulk Water vs. `25–40 µm` Fine Water Mist:** Pouring bulk liquid water onto burning oil sinks and flashes into steam (`~1700x` expansion), splattering burning fuel—so kitchen grease fires must be smothered by cutting oxygen with a lid. Crewed spacecraft never spray bulk water; they deploy **`25–40 µm` fine water mist (`SoFIE-MIST / ISS PFE`)**, whose micro-droplets evaporate directly in the flame front to absorb heat and dilute oxygen without splashing or damaging electronics.\n"
        "- **Space-to-Earth Transfer:** NASA micro-mist nozzle designs (`SoFIE-MIST`) and `Nomex / PBI` protective fabrics are now widely used in terrestrial cleanrooms, battery rooms, and firefighting gear."
    )


def _is_previous_turn_valid_in_scope(history: Optional[Sequence[Dict[str, str]]]) -> bool:
    """
    History-poisoning guard: allow follow-up resolution only when the immediately preceding user message
    was genuinely `in_scope` or `boundary_context` AND the preceding assistant message was not a refusal.
    """
    if not history:
        return False

    last_user_msg = ""
    last_assistant_msg = ""
    for item in reversed(list(history)):
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").lower()
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        if role == "assistant" and not last_assistant_msg:
            last_assistant_msg = content
        elif role == "user" and not last_user_msg:
            last_user_msg = content
            break

    if not last_user_msg:
        return False

    if last_assistant_msg:
        norm_asst = normalize_scope_text(last_assistant_msg)
        if _has_any(norm_asst, _REJECTED_ASSISTANT_MARKERS):
            return False

    prev_eval = evaluate_query_scope(
        user_message=last_user_msg,
        history=None,
        sim_params=None,
        media_context="",
        image_base64=None,
        lang="en",
        _allow_followup=False,
    )
    return prev_eval.get("status") in ("in_scope", "boundary_context")


def evaluate_query_scope(
    user_message: str,
    history: Optional[Sequence[Dict[str, str]]] = None,
    sim_params: Optional[Dict[str, Any]] = None,
    media_context: str = "",
    image_base64: Optional[str] = None,
    lang: str = "en",
    _allow_followup: bool = True,
) -> Dict[str, Any]:
    """
    Classify a user query in `< 1 ms`:
    - `status`: `'in_scope'` | `'boundary_context'` | `'rule_locked'` | `'off_topic'`
    - `cleaned_query`: small-talk stripped and typo-repaired query text
    - `misconception`: physical misconception dictionary if detected
    - `physics_note`: bool flag plus `physics_note_tr` / `physics_note_en` correction strings
    - `reply_tr` / `reply_en` / `reply`: pure English early-exit or boundary-bridge response
    """
    _ = lang
    raw_msg = str(user_message or "").strip()
    full_norm = normalize_scope_text(raw_msg)
    fuzzy_full, repaired_full_norm = _match_fuzzy_domain_tokens(full_norm)

    # 1) Flight & Fire Safety Rule Lock ('rule_locked') — evaluated first on full normalized text
    has_role_override = _has_any(repaired_full_norm, _ROLE_OVERRIDE_PHRASES)
    has_halon_endorse = ("halon" in repaired_full_norm) and _has_any(repaired_full_norm, _HALON_ENDORSE_VERBS)
    if has_role_override or has_halon_endorse:
        mentions_halon = "halon" in repaired_full_norm
        if mentions_halon:
            rep_en = (
                "Flight safety rules are fixed and cannot be overridden. "
                "Under `NASA-STD-6001B`, Halon 1301 is prohibited in enclosed spacecraft cabins because it decomposes into toxic `HF` and `HBr` "
                "gases at flame temperatures; crews shut off cabin HVAC airflow and apply `25–40 µm` fine water mist instead."
            )
        else:
            rep_en = (
                "Flight and fire safety rules are fixed; this console operates strictly for spacecraft fire safety and combustion "
                "physics analysis. You can ask a technical question based on the active 3D chamber or Orion compartments."
            )
        return {
            "status": "rule_locked",
            "badge_tr": "Off-Topic",
            "badge_en": "Off-Topic",
            "physics_note": False,
            "physics_note_tr": "",
            "physics_note_en": "",
            "is_followup": False,
            "mixed_stripped": False,
            "cleaned_query": raw_msg,
            "typo_corrections": [c for _, c in fuzzy_full],
            "misconception": None,
            "boundary_kind": None,
            "reply_tr": rep_en,
            "reply_en": rep_en,
            "reply": rep_en,
            "actions": [],
        }

    # 2) Casual clause stripping and domain typo repair
    stripped_msg, mixed_stripped = _strip_casual_clauses(raw_msg)
    clause_norm = normalize_scope_text(stripped_msg)
    if clause_norm == full_norm:
        fuzzy_hits, repaired_norm = fuzzy_full, repaired_full_norm
    else:
        fuzzy_hits, repaired_norm = _match_fuzzy_domain_tokens(clause_norm)

    cleaned_query = stripped_msg
    if fuzzy_hits:
        missing_canon = [canon for orig, canon in fuzzy_hits if orig != canon and canon not in clause_norm]
        if missing_canon:
            cleaned_query = f"{stripped_msg} ({' '.join(dict.fromkeys(missing_canon))})"

    # 3) Boundary context ('boundary_context') — ISS equipment, household grease fire, rocket engines
    boundary_kind = _detect_boundary_category(repaired_norm)
    if boundary_kind:
        miscon = detect_physical_misconception(repaired_norm)
        note_str = str(miscon["correction_en"]) if miscon else ""
        return {
            "status": "boundary_context",
            "badge_tr": "Fire Safety Context",
            "badge_en": "Fire Safety Context",
            "physics_note": bool(miscon),
            "physics_note_tr": note_str,
            "physics_note_en": note_str,
            "is_followup": False,
            "mixed_stripped": mixed_stripped,
            "cleaned_query": cleaned_query,
            "typo_corrections": [c for _, c in fuzzy_hits],
            "misconception": miscon,
            "boundary_kind": boundary_kind,
            "reply_tr": "",
            "reply_en": "",
            "reply": "",
            "actions": [],
        }

    # 4) Direct in-scope ('in_scope') check
    has_explicit_off_topic = _has_any(repaired_norm, _EXPLICIT_OFF_TOPIC_PHRASES)
    has_strong_space_anchor = _has_strong_space_anchor(repaired_norm)
    blocked_by_off_topic = has_explicit_off_topic and not has_strong_space_anchor

    has_direct_domain = (
        _has_any(repaired_norm, _DIRECT_DOMAIN_PHRASES)
        or bool(_RE_DOMAIN_SHORT_TOKENS.search(repaired_norm))
        or bool(_RE_NATURAL_COMBUSTION_TOKENS.search(repaired_norm))
        or len(fuzzy_hits) > 0
    )
    clean_greeting_norm = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", repaired_norm)).strip()
    has_intro_intent = (
        _has_any(repaired_norm, _PLATFORM_INTRO_PHRASES)
        or clean_greeting_norm == "help"
        or clean_greeting_norm in _SHORT_GREETINGS
    )

    if not blocked_by_off_topic and (has_direct_domain or has_intro_intent):
        miscon = detect_physical_misconception(repaired_norm)
        note_str = str(miscon["correction_en"]) if miscon else ""
        return {
            "status": "in_scope",
            "badge_tr": "Direct Analysis",
            "badge_en": "Direct Analysis",
            "physics_note": bool(miscon),
            "physics_note_tr": note_str,
            "physics_note_en": note_str,
            "is_followup": False,
            "mixed_stripped": mixed_stripped,
            "cleaned_query": cleaned_query,
            "typo_corrections": [c for _, c in fuzzy_hits],
            "misconception": miscon,
            "boundary_kind": None,
            "reply_tr": "",
            "reply_en": "",
            "reply": "",
            "actions": [],
        }

    # 5) Safe follow-up and attached dataset/image context (history-poisoning protected)
    has_media = bool((media_context and str(media_context).strip()) or (image_base64 and str(image_base64).strip()))
    if not has_explicit_off_topic:
        if has_media and (
            _has_any(repaired_norm, _MEDIA_FOLLOWUP_PATTERNS)
            or _has_any(repaired_norm, _FOLLOWUP_PATTERNS)
            or len(repaired_norm.split()) <= 6
        ):
            return {
                "status": "in_scope",
                "badge_tr": "Direct Analysis",
                "badge_en": "Direct Analysis",
                "physics_note": False,
                "physics_note_tr": "",
                "physics_note_en": "",
                "is_followup": True,
                "mixed_stripped": mixed_stripped,
                "cleaned_query": cleaned_query,
                "typo_corrections": [],
                "misconception": None,
                "boundary_kind": None,
                "reply_tr": "",
                "reply_en": "",
                "reply": "",
                "actions": [],
            }

        if _allow_followup and _has_any(repaired_norm, _FOLLOWUP_PATTERNS) and _is_previous_turn_valid_in_scope(history):
            return {
                "status": "in_scope",
                "badge_tr": "Direct Analysis",
                "badge_en": "Direct Analysis",
                "physics_note": False,
                "physics_note_tr": "",
                "physics_note_en": "",
                "is_followup": True,
                "mixed_stripped": mixed_stripped,
                "cleaned_query": cleaned_query,
                "typo_corrections": [],
                "misconception": None,
                "boundary_kind": None,
                "reply_tr": "",
                "reply_en": "",
                "reply": "",
                "actions": [],
            }

    # 6) Off-topic ('off_topic') — early exit (< 1 ms, zero external calls)
    fuel_id = str((sim_params or {}).get("fuel_id") or "n_heptane")
    fuel_labels_en = {
        "n_heptane": "n-Heptane",
        "methanol": "Methanol",
        "ethanol": "Ethanol",
        "pmma": "PMMA",
        "nomex": "Nomex",
        "sibal": "SIBAL fabric",
        "propane_cfig": "Propane",
        "hydrogen": "Hydrogen",
        "custom_material": "custom material",
    }
    f_en = fuel_labels_en.get(fuel_id, "combustion chamber")

    off_en = (
        "This console focuses exclusively on spacecraft fire safety, cabin response, and microgravity combustion physics. "
        f"You can pick one of the quick actions below for the active `{f_en}` scene or type a technical question."
    )

    return {
        "status": "off_topic",
        "badge_tr": "Off-Topic",
        "badge_en": "Off-Topic",
        "physics_note": False,
        "physics_note_tr": "",
        "physics_note_en": "",
        "is_followup": False,
        "mixed_stripped": False,
        "cleaned_query": raw_msg,
        "typo_corrections": [],
        "misconception": None,
        "boundary_kind": None,
        "reply_tr": off_en,
        "reply_en": off_en,
        "reply": off_en,
        "actions": [],
    }


def prepend_misconception_correction(reply_text: str, misconception: Optional[Dict[str, str]], lang: str = "en") -> str:
    """
    Prepend a concise `**Physics Note:**` correction at the top of the reply whenever a physical misconception is detected.
    """
    _ = lang
    if not misconception:
        return reply_text
    corr = str(misconception.get("correction_en") or misconception.get("correction_tr") or "").strip()
    if not corr:
        return reply_text
    norm_rep = normalize_scope_text(reply_text[:320])
    norm_corr_head = normalize_scope_text(corr[:60])
    if norm_corr_head and norm_corr_head in norm_rep:
        return reply_text
    return f"**Physics Note:** {corr}\n\n{reply_text.lstrip()}"


def sanitize_unverified_experiment_names(reply_text: str, lang: str = "en") -> Tuple[str, bool]:
    """
    Replace unverified / out-of-catalog experiment indices (e.g., Saffire-IX, Saffire-7, FLEX-9, BASS-4, SoFIE-9)
    with verified NASA mission designations.
    """
    _ = lang
    if not reply_text:
        return reply_text, False

    cleaned = reply_text
    changed = False

    for pat, repl in (
        (_RE_FAKE_SAFFIRE_ROMAN, "Saffire (I–VI)"),
        (_RE_FAKE_SAFFIRE_NUM, "Saffire (I–VI)"),
        (_RE_FAKE_FLEX, "FLEX / FLEX-2"),
        (_RE_FAKE_BASS, "BASS / BASS-II"),
        (_RE_FAKE_SOFIE, "SoFIE"),
        (_RE_FAKE_SPICE_SLICE, r"\1"),
    ):
        new_txt = pat.sub(repl, cleaned)
        if new_txt != cleaned:
            cleaned = new_txt
            changed = True

    return cleaned, changed


def build_suggested_actions(
    scope_result: Dict[str, Any],
    active_sim: Optional[Dict[str, Any]] = None,
    lang: str = "en",
) -> List[Dict[str, Any]]:
    """
    Build clickable English action chips displayed beneath assistant replies:
    - `apply_3d_sim` (`'Load in 3D'`)
    - `run_orion_sequence` (`'Start Fire Response'`)
    - `ask_prompt` (concise 4-7 word technical questions tailored to the active 3D scene)
    """
    _ = lang
    inp = (active_sim or {}).get("inputs") or {}
    comp_net = (active_sim or {}).get("compartment_network") or {}
    norm_q = normalize_scope_text(str(scope_result.get("cleaned_query") or ""))

    cur_fuel = str(inp.get("fuel_id") or "n_heptane")
    cur_g = float(inp.get("gravity_g") if inp.get("gravity_g") is not None else 0.0)
    cur_o2 = float(inp.get("oxygen_pct") if inp.get("oxygen_pct") is not None else 21.0)
    cur_p = float(inp.get("pressure_psia") if inp.get("pressure_psia") is not None else 14.7)
    cur_u = float(inp.get("airflow_cms") if inp.get("airflow_cms") is not None else 2.0)
    fire_comp = str(comp_net.get("fire_compartment_id") or "ORION_CM").upper()
    if fire_comp not in ("ORION_CM", "IHAB", "HALO", "AIRLOCK", "PPE"):
        fire_comp = "ORION_CM"

    if "methanol" in norm_q:
        target_sim: Dict[str, Any] = {
            "fuel_id": "methanol",
            "gravity_g": 0.0,
            "oxygen_pct": 16.0,
            "pressure_psia": 14.7,
            "airflow_cms": 0.4,
            "droplet_d0_mm": 3.8,
            "diluent": "N2",
        }
    elif "cool flame" in norm_q:
        target_sim = {
            "fuel_id": "n_heptane",
            "gravity_g": 0.0,
            "oxygen_pct": 15.5,
            "pressure_psia": 14.7,
            "airflow_cms": 0.2,
            "droplet_d0_mm": 4.2,
            "diluent": "N2",
        }
    elif "spacesuit" in norm_q or "eva" in norm_q:
        target_sim = {
            "fuel_id": "nomex",
            "gravity_g": 0.16,
            "oxygen_pct": 100.0,
            "pressure_psia": 4.3,
            "airflow_cms": 4.0,
            "droplet_d0_mm": 3.2,
            "diluent": "N2",
            "habitat_id": "eva_suit",
        }
    elif "pmma" in norm_q or "saffire" in norm_q or "bass" in norm_q:
        target_sim = {
            "fuel_id": "pmma",
            "gravity_g": 0.0,
            "oxygen_pct": 21.0,
            "pressure_psia": 14.7,
            "airflow_cms": 5.5,
            "droplet_d0_mm": 3.5,
            "diluent": "N2",
        }
    else:
        target_sim = {
            "fuel_id": cur_fuel,
            "gravity_g": cur_g,
            "oxygen_pct": cur_o2,
            "pressure_psia": cur_p,
            "airflow_cms": max(0.2, cur_u) if cur_u != 0 else 4.5,
            "droplet_d0_mm": float(inp.get("droplet_d0_mm") or 3.2),
            "diluent": str(inp.get("diluent") or "N2"),
        }

    actions: List[Dict[str, Any]] = [
        {
            "type": "apply_3d_sim",
            "label_tr": "Load in 3D",
            "label_en": "Load in 3D",
            "sim_params": target_sim,
        },
        {
            "type": "run_orion_sequence",
            "label_tr": "Start Fire Response",
            "label_en": "Start Fire Response",
            "compartment_id": fire_comp,
        },
    ]

    prompt_candidates: List[str] = []
    if cur_fuel == "methanol" or "methanol" in norm_q:
        prompt_candidates.append("How does methanol burn in 0G?")
    elif cur_g == 0.16:
        prompt_candidates.append("How does lunar gravity shift flammability?")
    elif cur_o2 >= 50.0:
        prompt_candidates.append("Why do spacesuits use pure oxygen?")
    else:
        prompt_candidates.append("How does methanol burn in 0G?")

    prompt_candidates.append("How does water mist quench fire?")
    prompt_candidates.append("When is hatch opening safe?")

    for p_en in prompt_candidates[:2]:
        actions.append(
            {
                "type": "ask_prompt",
                "label_tr": p_en,
                "label_en": p_en,
                "prompt_tr": p_en,
                "prompt_en": p_en,
            }
        )

    return actions
