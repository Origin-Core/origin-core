"""
fps_predictor.py
یک مدل تخمینی ساده برای پیش‌بینی FPS.
مهم: این یک برآورد آماری بر اساس امتیاز نسبی سخت‌افزار است، نه اندازه‌گیری واقعی.
دقت واقعی نیازمند بنچمارک‌های رسمی هر بازی روی هر GPU/CPU است که در این ابزار سبک وجود ندارد.
"""

from games_db import GAMES_DB, match_gpu_score

RESOLUTION_FACTOR = {
    "1280x720": 1.6,
    "1920x1080": 1.0,
    "2560x1440": 0.62,
    "3840x2160": 0.32,
}

QUALITY_FACTOR = {
    "Low": 1.35,
    "Medium": 1.0,
    "High": 0.8,
    "Ultra": 0.6,
}


def predict_fps(game_name: str, gpu_name: str, cpu_core_count: int, ram_gb: float,
                 resolution="1920x1080", quality="Medium"):
    if game_name not in GAMES_DB:
        return None

    game = GAMES_DB[game_name]
    baseline = game["baseline_score"]  # امتیازی که تقریبا 60fps در 1080p/Medium میده
    gpu_score = match_gpu_score(gpu_name)

    # نسبت قدرت GPU کاربر به baseline بازی
    power_ratio = gpu_score / baseline if baseline else 1

    # جریمه‌ی سبک برای CPU ضعیف (کمتر از 4 هسته) و رم کم
    cpu_penalty = 1.0 if cpu_core_count >= 4 else 0.75
    ram_penalty = 1.0 if ram_gb >= game["min"]["ram_gb"] else 0.7

    res_factor = RESOLUTION_FACTOR.get(resolution, 1.0)
    q_factor = QUALITY_FACTOR.get(quality, 1.0)

    estimated_fps = 60 * power_ratio * cpu_penalty * ram_penalty * res_factor * q_factor
    estimated_fps = max(5, round(estimated_fps))

    # بازه‌ی اطمینان تقریبی (±20%)
    low = round(estimated_fps * 0.8)
    high = round(estimated_fps * 1.2)

    return {
        "estimated_fps": estimated_fps,
        "range": (low, high),
        "resolution": resolution,
        "quality": quality,
    }
