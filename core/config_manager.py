# -*- coding: utf-8 -*-
"""
ALTAR-NASA v6.3 Configuration Vault, API Key Store, and System TLS Adapter.
Uses portable runtime paths and system certificate validation without disabling TLS verification.
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import threading
from pathlib import Path
from typing import Any, Dict

import requests
from requests.adapters import HTTPAdapter

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


try:
    import certifi
except ImportError:
    certifi = None


def _build_resilient_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if certifi is not None:
        try:
            ca_file = certifi.where()
            if ca_file and os.path.isfile(ca_file):
                ctx.load_verify_locations(cafile=ca_file)
        except Exception:
            pass
    if hasattr(ssl, "VERIFY_X509_STRICT"):
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return ctx


class SystemSSLAdapter(HTTPAdapter):
    """
    HTTPS adapter compatible with Python 3.13+ and OpenSSL 3.x that combines the OS root trust store
    with certifi CA bundles, resolving intermediate certificate gaps without `verify=False`.
    """

    def init_poolmanager(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["ssl_context"] = _build_resilient_ssl_context()
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["ssl_context"] = _build_resilient_ssl_context()
        return super().proxy_manager_for(*args, **kwargs)


def create_secure_http_session() -> requests.Session:
    """Create a verified HTTPS session for NASA REST APIs and cloud AI providers."""
    session = requests.Session()
    session.mount("https://", SystemSSLAdapter())
    session.headers.update({
        "User-Agent": "ALTAR-NASA-FlameInFreefall/6.3 (NASA-SpaceApps-2026; Scientific-Dashboard)"
    })
    return session


def get_resource_base_dir() -> Path:
    """Return the PyInstaller bundle directory (`_MEIPASS`) or portable source root."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def get_app_host_dir() -> Path:
    """Return the directory containing the running executable or project source root."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_user_data_dir() -> Path:
    """Return portable `.runtime/userdata_en` if present, otherwise `%APPDATA%/AltarNasa_EN`."""
    host_dir = get_app_host_dir()
    for cand_rt in (host_dir / ".runtime", host_dir.parent / ".runtime"):
        if cand_rt.is_dir():
            portable_cfg = cand_rt / "userdata_en"
            try:
                portable_cfg.mkdir(parents=True, exist_ok=True)
                return portable_cfg
            except Exception:
                pass
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata) / "AltarNasa_EN"
    else:
        base = Path.home() / ".altar_nasa_en"
    base.mkdir(parents=True, exist_ok=True)
    return base


class ConfigManager:
    """Thread-safe configuration manager for API credentials, provider selection, and directives."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "active_provider": "auto",  # auto | ollama | antigravity | gemini | openrouter | custom
        "ollama_host": "http://127.0.0.1:11434",
        "ollama_model": "auto",
        "gemini_api_key": "",
        "gemini_model": "gemini-2.5-flash",
        "openrouter_api_key": "",
        "openrouter_model": "google/gemini-2.0-flash-exp:free",
        "antigravity_api_key": "",
        "antigravity_mode": "cli_sdk_or_api",
        "antigravity_model": "gemini-2.5-flash",
        "custom_base_url": "",
        "custom_api_key": "",
        "custom_model": "",
        "deep_verify_6stage": True,
        "auto_sync_media_to_3d": True,
        "language": "en",
        "custom_extra_directives": "",
    }

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.config_path = get_user_data_dir() / "config.json"
        self._load_optional_local_dotenv()
        self._data: Dict[str, Any] = dict(self.DEFAULT_CONFIG)
        self.load()

    def _load_optional_local_dotenv(self) -> None:
        """Load optional `.env` variables from the local working directory if present."""
        if load_dotenv is None:
            return
        candidates = [
            Path.cwd() / ".env",
            get_resource_base_dir() / ".env",
        ]
        for env_file in candidates:
            if env_file.is_file():
                try:
                    load_dotenv(dotenv_path=env_file, override=False)
                except Exception:
                    pass

    def load(self) -> Dict[str, Any]:
        with self._lock:
            merged = dict(self.DEFAULT_CONFIG)
            # Initialize defaults from optional environment variables
            if os.environ.get("OLLAMA_HOST"):
                merged["ollama_host"] = os.environ["OLLAMA_HOST"].strip()
            if os.environ.get("GEMINI_API_KEY"):
                merged["gemini_api_key"] = os.environ["GEMINI_API_KEY"].strip().strip('"')
            if os.environ.get("OPENROUTER_API_KEY"):
                merged["openrouter_api_key"] = os.environ["OPENROUTER_API_KEY"].strip().strip('"')
            if os.environ.get("ANTIGRAVITY_API_KEY"):
                merged["antigravity_api_key"] = os.environ["ANTIGRAVITY_API_KEY"].strip().strip('"')
            if os.environ.get("CUSTOM_OPENAI_BASE_URL"):
                merged["custom_base_url"] = os.environ["CUSTOM_OPENAI_BASE_URL"].strip()

            if self.config_path.is_file():
                try:
                    saved = json.loads(self.config_path.read_text(encoding="utf-8"))
                    if isinstance(saved, dict):
                        for k, v in saved.items():
                            if k in merged and v is not None:
                                if k.endswith("_api_key") and not str(v).strip() and merged.get(k):
                                    continue
                                merged[k] = v
                except Exception:
                    pass
            for model_key in ("antigravity_model", "gemini_model", "openrouter_model", "custom_model"):
                m_val = str(merged.get(model_key) or "").strip()
                if m_val.lower().startswith("gemini-3.8") or m_val.lower() in ("gemini-3.9", "gemini-4.0"):
                    merged[model_key] = "gemini-2.5-flash" if model_key != "custom_model" else ""
            # Enforce strict English-only locale lock
            merged["language"] = "en"
            self._data = merged
            return dict(self._data)

    load_config = load

    def save(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            for k, v in (updates or {}).items():
                if k == "language":
                    self._data["language"] = "en"
                    continue
                if k in self.DEFAULT_CONFIG and v is not None:
                    if isinstance(v, str):
                        v_clean = v.strip()
                        # Preserve existing secret key if masked placeholder was echoed back
                        if k.endswith("_api_key") and "•" in v_clean:
                            continue
                        if k.endswith("_model") and v_clean.lower().startswith("gemini-3.8"):
                            v_clean = "gemini-2.5-flash" if k != "custom_model" else ""
                        self._data[k] = v_clean
                    else:
                        self._data[k] = v
            self._data["language"] = "en"
            try:
                self.config_path.write_text(
                    json.dumps(self._data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass
            return dict(self._data)

    save_config = save

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            self._data["language"] = "en"
            return dict(self._data)

    def get_masked_public_view(self) -> Dict[str, Any]:
        """Return configuration view with API keys safely masked for client responses."""
        raw = self.get_all()
        out: Dict[str, Any] = {}
        for k, v in raw.items():
            if k.endswith("_api_key") and isinstance(v, str):
                if len(v) > 8:
                    out[k] = f"{v[:4]}{'•' * 12}{v[-4:]}"
                    out[f"{k}_configured"] = True
                elif len(v) > 0:
                    out[k] = "•" * 8
                    out[f"{k}_configured"] = True
                else:
                    out[k] = ""
                    out[f"{k}_configured"] = False
            else:
                out[k] = v
        out["language"] = "en"
        out["storage_path"] = str(self.config_path)
        return out


def load_config(mgr: ConfigManager | None = None) -> Dict[str, Any]:
    """Load persisted configuration dictionary with strict English-only locale lock."""
    target = mgr if mgr is not None else ConfigManager()
    cfg = target.load()
    cfg["language"] = "en"
    return cfg


def save_config(updates: Dict[str, Any], mgr: ConfigManager | None = None) -> Dict[str, Any]:
    """Save configuration updates with strict English-only locale lock."""
    target = mgr if mgr is not None else ConfigManager()
    normalized = dict(updates or {})
    normalized["language"] = "en"
    cfg = target.save(normalized)
    cfg["language"] = "en"
    return cfg
