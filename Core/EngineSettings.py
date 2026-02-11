# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ague Samuel Amen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
import os
from typing import Any, Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QSpinBox,
    QWidget,
)


def _engine_cfg_dir(workspace_dir: str) -> str:
    return os.path.join(os.path.abspath(workspace_dir), "arkenginecfg")


def _prefs_path(workspace_dir: str) -> str:
    return os.path.join(_engine_cfg_dir(workspace_dir), "_prefs.json")


def _engine_cfg_path(workspace_dir: str, engine_id: str) -> str:
    return os.path.join(_engine_cfg_dir(workspace_dir), f"{engine_id}.json")


def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass


def get_remember_pref(workspace_dir: str) -> bool:
    try:
        p = _prefs_path(workspace_dir)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                data = json.load(f) or {}
            return bool(data.get("remember_engine_settings", False))
    except Exception:
        pass
    return False


def set_remember_pref(workspace_dir: str, value: bool) -> None:
    try:
        _ensure_dir(_engine_cfg_dir(workspace_dir))
        p = _prefs_path(workspace_dir)
        data = {"remember_engine_settings": bool(value)}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def collect_widget_settings(root: QWidget) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for w in root.findChildren(QWidget):
        name = getattr(w, "objectName", lambda: "")()
        if not name:
            continue
        if isinstance(w, QCheckBox):
            data[name] = {"type": "QCheckBox", "value": bool(w.isChecked())}
        elif isinstance(w, QLineEdit):
            data[name] = {"type": "QLineEdit", "value": w.text()}
        elif isinstance(w, QComboBox):
            data[name] = {"type": "QComboBox", "value": w.currentText()}
        elif isinstance(w, QSpinBox):
            data[name] = {"type": "QSpinBox", "value": int(w.value())}
        elif isinstance(w, QDoubleSpinBox):
            data[name] = {"type": "QDoubleSpinBox", "value": float(w.value())}
    return data


def apply_widget_settings(root: QWidget, data: dict[str, dict[str, Any]]) -> None:
    for name, payload in data.items():
        try:
            w = root.findChild(QWidget, name)
            if w is None:
                continue
            t = payload.get("type")
            v = payload.get("value")
            if t == "QCheckBox" and isinstance(w, QCheckBox):
                w.setChecked(bool(v))
            elif t == "QLineEdit" and isinstance(w, QLineEdit):
                w.setText("" if v is None else str(v))
            elif t == "QComboBox" and isinstance(w, QComboBox):
                if isinstance(v, str):
                    idx = w.findText(v)
                    if idx >= 0:
                        w.setCurrentIndex(idx)
            elif t == "QSpinBox" and isinstance(w, QSpinBox):
                try:
                    w.setValue(int(v))
                except Exception:
                    pass
            elif t == "QDoubleSpinBox" and isinstance(w, QDoubleSpinBox):
                try:
                    w.setValue(float(v))
                except Exception:
                    pass
        except Exception:
            continue


def save_engine_settings(
    workspace_dir: str, engine_id: str, root: QWidget
) -> Optional[str]:
    try:
        _ensure_dir(_engine_cfg_dir(workspace_dir))
        path = _engine_cfg_path(workspace_dir, engine_id)
        payload = {
            "_meta": {"engine_id": engine_id},
            "widgets": collect_widget_settings(root),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return path
    except Exception:
        return None


def load_engine_settings(
    workspace_dir: str, engine_id: str
) -> Optional[dict[str, dict[str, Any]]]:
    try:
        path = _engine_cfg_path(workspace_dir, engine_id)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f) or {}
        widgets = data.get("widgets")
        return widgets if isinstance(widgets, dict) else None
    except Exception:
        return None


def engine_settings_path(workspace_dir: str, engine_id: str) -> str:
    return _engine_cfg_path(workspace_dir, engine_id)
