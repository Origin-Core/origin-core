# ORIGIN-CORe

ابزار مانیتورینگ سخت‌افزار + شناسایی بازی + پیش‌بینی FPS برای ویندوز.

## امکانات
- نمایش دمای CPU و GPU (از طریق LibreHardwareMonitor / NVML)
- درصد استفاده‌ی CPU و GPU
- میزان حافظه‌ی کل / استفاده‌شده
- لیست پرمصرف‌ترین پردازش‌ها (CPU/RAM)
- شناسایی خودکار بازی‌های در حال اجرا از روی دیتابیس محلی (`games_db.py`)
- نمایش حداقل و پیشنهادی سیستم موردنیاز بازی شناسایی‌شده
- تخمین FPS بر اساس مشخصات سیستم، رزولوشن و کیفیت گرافیکی

## اجرای محلی (برای تست قبل از بیلد)
```bash
pip install -r requirements.txt
python main.py
```

## گرفتن خروجی EXE از طریق GitHub Actions (خودکار)
1. یک ریپازیتوری جدید در گیت‌هاب بساز و کل این پوشه را push کن:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: ORIGIN-CORe"
   git branch -M main
   git remote add origin https://github.com/USERNAME/origin-core.git
   git push -u origin main
   ```
2. به محض push شدن روی شاخه‌ی `main`، ورک‌فلوی `.github/workflows/build.yml`
   به‌صورت خودکار روی یک ماشین ویندوزی اجرا می‌شود و با PyInstaller فایل
   `ORIGIN-CORe.exe` را می‌سازد.
3. برای دانلود فایل: به تب **Actions** ریپازیتوری برو → آخرین ران موفق را باز کن
   → پایین صفحه بخش **Artifacts** → `ORIGIN-CORe-windows` را دانلود کن.
4. اگر می‌خواهی یک **Release** رسمی با لینک دانلود مستقیم داشته باشی، یک تگ نسخه بزن:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   بعد از چند دقیقه فایل exe به‌صورت خودکار در بخش Releases ریپازیتوری قرار می‌گیرد.

## دمای دقیق سخت‌افزار (اختیاری ولی توصیه‌شده)
برای دمای دقیق، فایل‌های `LibreHardwareMonitorLib.dll` و `HidSharp.dll` را طبق
`libs/README.md` در پوشه‌ی `libs/` قرار بده و برنامه را با دسترسی **Run as Administrator**
اجرا کن. بدون این فایل‌ها، برنامه بدون خطا اجرا می‌شود ولی دمای CPU نمایش داده نمی‌شود
و دمای GPU فقط برای کارت‌های NVIDIA در دسترس است.

## توسعه‌ی دیتابیس بازی‌ها
هر بازی جدید را می‌توانی داخل `games_db.py` در دیکشنری `GAMES_DB` با همان ساختار نمونه‌ها
اضافه کنی: نام پردازش اجرایی (exe)، حداقل/پیشنهادی سیستم، و `baseline_score` برای مدل تخمین FPS.

## محدودیت‌های واقعی (صادقانه)
- تخمین FPS یک مدل آماری ساده است، نه یک بنچمارک واقعی — دقتش محدود است.
- شناسایی بازی فقط برای بازی‌هایی کار می‌کند که در `games_db.py` تعریف شده باشند.
- دمای دقیق سخت‌افزار وابسته به دسترسی Administrator و وجود DLLهای LibreHardwareMonitor است.

## ساختار پروژه
```
origin-core/
├── main.py               # رابط گرافیکی (customtkinter)
├── sensors.py             # خواندن سنسورهای واقعی سخت‌افزار
├── games_db.py             # دیتابیس بازی‌ها + شناسایی + امتیاز GPU
├── fps_predictor.py        # موتور تخمین FPS
├── requirements.txt
├── libs/                   # محل قرارگیری DLLهای اختیاری سنسور
└── .github/workflows/build.yml   # بیلد خودکار exe در GitHub Actions
```
