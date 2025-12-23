from __future__ import annotations

import hashlib
from typing import Dict, Tuple

# สีหลักสำหรับ Light theme (เลือกโทนอ่านง่ายบนพื้นขาว)
LIGHT_PALETTE = [
    "#2563EB", "#DC2626", "#16A34A", "#F59E0B", "#7C3AED",
    "#0EA5E9", "#F97316", "#10B981", "#DB2777", "#64748B",
]

# สีหลักสำหรับ Dark theme (สว่างขึ้น อ่านง่ายบนพื้นดำ)
DARK_PALETTE = [
    "#60A5FA", "#F87171", "#4ADE80", "#FBBF24", "#A78BFA",
    "#38BDF8", "#FB923C", "#34D399", "#F472B6", "#CBD5E1",
]

# ถ้าคุณมีชื่อโรคแน่นอน สามารถ fix แบบนี้ (optional)
# key ต้องตรงกับค่า disease ที่เก็บใน MongoDB
FIXED_LIGHT: Dict[str, str] = {
    # "Blast": "#DC2626",
    # "Brown Spot": "#A16207",
    # "Healthy": "#2563EB",
}
FIXED_DARK: Dict[str, str] = {
    # "Blast": "#F87171",
    # "Brown Spot": "#FBBF24",
    # "Healthy": "#60A5FA",
}

FALLBACK_LIGHT = "#94A3B8"
FALLBACK_DARK = "#CBD5E1"


def _pick_from_palette(name: str, palette: list[str]) -> str:
    if not name:
        return palette[0]
    h = hashlib.sha256(name.encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(palette)
    return palette[idx]


def disease_color_map(disease_names: list[str]) -> Dict[str, Dict[str, str]]:
    """
    return:
      {
        "light": {"Blast":"#...", ...},
        "dark": {"Blast":"#...", ...}
      }
    """
    light: Dict[str, str] = {}
    dark: Dict[str, str] = {}

    for d in disease_names:
        key = d or "Unknown"
        if key in FIXED_LIGHT:
            light[key] = FIXED_LIGHT[key]
        else:
            light[key] = _pick_from_palette(key, LIGHT_PALETTE) if key else FALLBACK_LIGHT

        if key in FIXED_DARK:
            dark[key] = FIXED_DARK[key]
        else:
            dark[key] = _pick_from_palette(key, DARK_PALETTE) if key else FALLBACK_DARK

    # เผื่อเจอ Unknown
    if "Unknown" not in light:
        light["Unknown"] = FALLBACK_LIGHT
    if "Unknown" not in dark:
        dark["Unknown"] = FALLBACK_DARK

    return {"light": light, "dark": dark}
