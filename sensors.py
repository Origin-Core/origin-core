"""
sensors.py
ماژول جمع‌آوری اطلاعات سخت‌افزاری واقعی سیستم:
- دمای CPU (از طریق LibreHardwareMonitorLib در صورت وجود، وگرنه WMI)
- دمای GPU (از طریق NVML برای NVIDIA، وگرنه LibreHardwareMonitorLib)
- درصد استفاده‌ی CPU / هسته‌ها
- رم کل / استفاده‌شده / آزاد
- استفاده‌ی GPU و VRAM

نکته‌ی مهم:
دمای دقیق سخت‌افزار روی ویندوز بدون یک لایه‌ی سنسور واقعی (LibreHardwareMonitorLib.dll)
در دسترس نیست. این فایل تلاش می‌کند آن را از طریق pythonnet بارگذاری کند. اگر DLL کنار
اجرایی برنامه نباشد، مقدار دما None برمی‌گردد و در UI پیام مناسب نشان داده می‌شود.

نحوه‌ی آماده‌سازی DLL:
1) از https://github.com/LibreHardwareMonitor/LibreHardwareMonitor ریلیزهای Library را دانلود کن.
2) فایل‌های LibreHardwareMonitorLib.dll و HidSharp.dll را در پوشه‌ی libs/ این پروژه بگذار.
3) برنامه باید با دسترسی Administrator اجرا شود تا سنسورها در دسترس باشند.
"""

import os
import sys
import platform
import psutil

IS_WINDOWS = platform.system() == "Windows"
LIBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")

_lhm_computer = None
_lhm_available = False
_nvml_available = False

# ---------------------------------------------------------------------------
# راه‌اندازی LibreHardwareMonitorLib (اختیاری، فقط ویندوز)
# ---------------------------------------------------------------------------
def _init_lhm():
    global _lhm_computer, _lhm_available
    if not IS_WINDOWS:
        return
    dll_path = os.path.join(LIBS_DIR, "LibreHardwareMonitorLib.dll")
    if not os.path.exists(dll_path):
        _lhm_available = False
        return
    try:
        import clr  # pythonnet
        sys.path.append(LIBS_DIR)
        clr.AddReference(dll_path.replace(".dll", ""))
        from LibreHardwareMonitor import Hardware

        computer = Hardware.Computer()
        computer.IsCpuEnabled = True
        computer.IsGpuEnabled = True
        computer.IsMemoryEnabled = True
        computer.Open()
        _lhm_computer = computer
        _lhm_available = True
    except Exception as e:
        print(f"[sensors] LibreHardwareMonitor در دسترس نیست: {e}")
        _lhm_available = False


def _init_nvml():
    global _nvml_available
    try:
        import pynvml
        pynvml.nvmlInit()
        _nvml_available = True
    except Exception:
        _nvml_available = False


_init_lhm()
_init_nvml()


# ---------------------------------------------------------------------------
# CPU
# ---------------------------------------------------------------------------
def get_cpu_usage_percent(per_core=False):
    return psutil.cpu_percent(percpu=per_core)


def get_cpu_temp():
    """برمی‌گرداند دمای CPU به سانتی‌گراد یا None اگر در دسترس نباشد."""
    if _lhm_available and _lhm_computer is not None:
        try:
            for hw in _lhm_computer.Hardware:
                if str(hw.HardwareType) == "Cpu":
                    hw.Update()
                    temps = [
                        s.Value for s in hw.Sensors
                        if str(s.SensorType) == "Temperature" and s.Value is not None
                    ]
                    if temps:
                        # میانگین حسگرهای هسته + بیشینه برای دمای "Package/Core Max"
                        return round(max(temps), 1)
        except Exception as e:
            print(f"[sensors] خطا در خواندن دمای CPU: {e}")
    return None


# ---------------------------------------------------------------------------
# GPU
# ---------------------------------------------------------------------------
def get_gpu_info():
    """
    خروجی: dict {name, temp, load_percent, mem_total_mb, mem_used_mb} یا None
    ابتدا NVML (NVIDIA) تست می‌شود، سپس LibreHardwareMonitor برای سایر برندها.
    """
    if _nvml_available:
        try:
            import pynvml
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode()
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return {
                "name": name,
                "temp": temp,
                "load_percent": util.gpu,
                "mem_total_mb": round(mem.total / 1024 / 1024),
                "mem_used_mb": round(mem.used / 1024 / 1024),
            }
        except Exception as e:
            print(f"[sensors] خطا در NVML: {e}")

    if _lhm_available and _lhm_computer is not None:
        try:
            for hw in _lhm_computer.Hardware:
                if "Gpu" in str(hw.HardwareType):
                    hw.Update()
                    temp = load = mem_used = mem_total = None
                    for s in hw.Sensors:
                        st = str(s.SensorType)
                        if st == "Temperature" and temp is None:
                            temp = s.Value
                        elif st == "Load" and "Core" in s.Name and load is None:
                            load = s.Value
                        elif st == "SmallData" and "Memory Used" in s.Name:
                            mem_used = s.Value
                        elif st == "SmallData" and "Memory Total" in s.Name:
                            mem_total = s.Value
                    return {
                        "name": hw.Name,
                        "temp": round(temp, 1) if temp else None,
                        "load_percent": round(load, 1) if load else None,
                        "mem_total_mb": round(mem_total) if mem_total else None,
                        "mem_used_mb": round(mem_used) if mem_used else None,
                    }
        except Exception as e:
            print(f"[sensors] خطا در خواندن GPU از LHM: {e}")

    return None


# ---------------------------------------------------------------------------
# RAM
# ---------------------------------------------------------------------------
def get_ram_info():
    vm = psutil.virtual_memory()
    return {
        "total_mb": round(vm.total / 1024 / 1024),
        "used_mb": round(vm.used / 1024 / 1024),
        "available_mb": round(vm.available / 1024 / 1024),
        "percent": vm.percent,
    }


# ---------------------------------------------------------------------------
# مصرف در حال اجرا به تفکیک پردازش (برای بخش "میزان استفاده هر قطعه")
# ---------------------------------------------------------------------------
def get_top_processes(limit=8):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: (x["cpu_percent"] or 0), reverse=True)
    return procs[:limit]


def hardware_status_summary():
    """برای نمایش هشدار به کاربر که کدام سنسورها فعال هستند."""
    return {
        "lhm_available": _lhm_available,
        "nvml_available": _nvml_available,
        "is_windows": IS_WINDOWS,
    }
