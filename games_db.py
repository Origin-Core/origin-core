"""
games_db.py
دیتابیس محلی و قابل‌گسترش بازی‌ها.
هر بازی شامل:
- process_names: نام(های) اجرایی که برای شناسایی پردازش در حال اجرا استفاده می‌شود
- min / recommended: مشخصات موردنیاز رسمی (تقریبی)
- baseline_score: امتیاز مرجع GPU (بر مبنای مقیاس داخلی GPU_SCORES) که بازی روی آن
  با کیفیت متوسط و رزولوشن 1080p حدود 60fps می‌دهد. برای پیش‌بینی FPS استفاده می‌شود.

این دیتابیس نمونه و قابل توسعه است — می‌تونی هر تعداد بازی دیگه به همین ساختار اضافه کنی.
"""

GAMES_DB = {
    "Valorant": {
        "process_names": ["VALORANT-Win64-Shipping.exe"],
        "min": {"cpu": "Intel i3-370M", "gpu": "Intel HD 3000", "ram_gb": 4},
        "recommended": {"cpu": "Intel i5-4460", "gpu": "GTX 1050 Ti", "ram_gb": 4},
        "baseline_score": 15,
    },
    "CS2": {
        "process_names": ["cs2.exe"],
        "min": {"cpu": "4 Core CPU", "gpu": "GTX 960 / R9 280", "ram_gb": 8},
        "recommended": {"cpu": "6 Core CPU", "gpu": "GTX 1060 / RX 580", "ram_gb": 16},
        "baseline_score": 35,
    },
    "GTA V": {
        "process_names": ["GTA5.exe", "PlayGTAV.exe"],
        "min": {"cpu": "Intel i5-3470", "gpu": "GTX 660", "ram_gb": 4},
        "recommended": {"cpu": "Intel i5-4460", "gpu": "GTX 1060", "ram_gb": 8},
        "baseline_score": 40,
    },
    "Cyberpunk 2077": {
        "process_names": ["Cyberpunk2077.exe"],
        "min": {"cpu": "Intel i7-6700", "gpu": "GTX 1060 6GB", "ram_gb": 12},
        "recommended": {"cpu": "Intel i7-12700", "gpu": "RTX 2060 Super", "ram_gb": 16},
        "baseline_score": 75,
    },
    "Fortnite": {
        "process_names": ["FortniteClient-Win64-Shipping.exe"],
        "min": {"cpu": "Intel i3-3225", "gpu": "Intel HD 4000", "ram_gb": 8},
        "recommended": {"cpu": "Intel i5-7300U", "gpu": "GTX 960", "ram_gb": 16},
        "baseline_score": 30,
    },
    "Red Dead Redemption 2": {
        "process_names": ["RDR2.exe"],
        "min": {"cpu": "Intel i5-2500K", "gpu": "GTX 770", "ram_gb": 8},
        "recommended": {"cpu": "Intel i7-4770K", "gpu": "GTX 1060 6GB", "ram_gb": 12},
        "baseline_score": 70,
    },
    "Elden Ring": {
        "process_names": ["eldenring.exe"],
        "min": {"cpu": "Intel i5-8400", "gpu": "GTX 1060 3GB", "ram_gb": 12},
        "recommended": {"cpu": "Intel i7-8700K", "gpu": "GTX 1070", "ram_gb": 16},
        "baseline_score": 60,
    },
    "Blender": {
        "process_names": ["blender.exe"],
        "min": {"cpu": "4 Core CPU", "gpu": "OpenGL 4.3 - 2GB VRAM", "ram_gb": 8},
        "recommended": {"cpu": "8 Core CPU", "gpu": "RTX 3060", "ram_gb": 32},
        "baseline_score": 50,
    },
}

# امتیاز نسبی تقریبی چند GPU برای تخمین (هرچه بزرگ‌تر، قوی‌تر).
# این‌ها اعداد تقریبی و قابل به‌روزرسانی هستند، نه بنچمارک رسمی.
GPU_SCORES = {
    "intel hd": 5, "intel uhd": 6, "intel iris xe": 12,
    "gtx 750": 10, "gtx 950": 14, "gtx 960": 16, "gtx 1050": 18, "gtx 1050 ti": 20,
    "gtx 1060": 28, "gtx 1070": 38, "gtx 1080": 46, "gtx 1080 ti": 55,
    "gtx 1650": 22, "gtx 1660": 30, "gtx 1660 ti": 33,
    "rtx 2060": 40, "rtx 2070": 48, "rtx 2080": 55, "rtx 2080 ti": 65,
    "rtx 3050": 30, "rtx 3060": 42, "rtx 3060 ti": 50, "rtx 3070": 58,
    "rtx 3080": 72, "rtx 3090": 82,
    "rtx 4060": 48, "rtx 4060 ti": 55, "rtx 4070": 68, "rtx 4070 ti": 78,
    "rtx 4080": 90, "rtx 4090": 110,
    "rx 570": 20, "rx 580": 22, "rx 5600": 34, "rx 5700": 40,
    "rx 6600": 38, "rx 6700": 50, "rx 6800": 62, "rx 7600": 45, "rx 7800": 65, "rx 7900": 90,
}


def match_gpu_score(gpu_name: str):
    """تخمین امتیاز GPU با تطبیق نام روی دیتابیس GPU_SCORES."""
    if not gpu_name:
        return 20  # امتیاز پیش‌فرض محافظه‌کارانه
    name = gpu_name.lower()
    best_match = None
    for key, score in GPU_SCORES.items():
        if key in name:
            if best_match is None or len(key) > len(best_match):
                best_match = key
                best_score = score
    if best_match:
        return best_score
    return 20


def detect_running_games(running_process_names):
    """running_process_names: set نام پردازش‌های در حال اجرا (lowercase)."""
    found = []
    for game, data in GAMES_DB.items():
        for proc in data["process_names"]:
            if proc.lower() in running_process_names:
                found.append(game)
                break
    return found
