# پوشه‌ی libs

برای گرفتن دمای **دقیق** CPU و GPU (به‌خصوص روی AMD/Intel که NVML پشتیبانی نمی‌کند)، فایل‌های زیر را
از ریلیزهای رسمی LibreHardwareMonitor دانلود و در همین پوشه قرار بده:

- LibreHardwareMonitorLib.dll
- HidSharp.dll

لینک: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases

بدون این فایل‌ها، برنامه همچنان اجرا می‌شود اما:
- دمای CPU نمایش داده نمی‌شود (پیام "در دسترس نیست")
- دمای GPU فقط برای کارت‌های NVIDIA (از طریق NVML) نمایش داده می‌شود

⚠️ برنامه برای خواندن این سنسورها باید با دسترسی **Run as Administrator** اجرا شود.
