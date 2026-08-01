"""
ORIGIN-CORe
یک ابزار مانیتورینگ سخت‌افزار + شناسایی بازی + پیش‌بینی FPS
"""

import platform
import psutil
import customtkinter as ctk

import sensors
import games_db
import fps_predictor

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "ORIGIN-CORe"


class OriginCoreApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x640")
        self.minsize(860, 560)

        self.tabview = ctk.CTkTabview(self, width=960, height=620)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_dashboard = self.tabview.add("داشبورد سخت‌افزار")
        self.tab_processes = self.tabview.add("مصرف قطعات")
        self.tab_games = self.tabview.add("شناسایی بازی")
        self.tab_fps = self.tabview.add("پیش‌بینی FPS")

        self._build_dashboard_tab()
        self._build_processes_tab()
        self._build_games_tab()
        self._build_fps_tab()

        self.after(500, self._refresh_loop)

    # ------------------------------------------------------------------
    # تب داشبورد
    # ------------------------------------------------------------------
    def _build_dashboard_tab(self):
        f = self.tab_dashboard
        status = sensors.hardware_status_summary()

        warn = ""
        if not status["lhm_available"]:
            warn = ("⚠ سنسور دمای دقیق (LibreHardwareMonitorLib) پیدا نشد. "
                    "برای دمای دقیق CPU/GPU، فایل‌های DLL را طبق README در پوشه‌ی libs/ قرار بده "
                    "و برنامه را با دسترسی Administrator اجرا کن.")
        if warn:
            ctk.CTkLabel(f, text=warn, text_color="#e0a030", wraplength=880,
                         justify="right").pack(pady=(10, 0), padx=10, anchor="e")

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        grid.columnconfigure((0, 1), weight=1)

        # CPU card
        self.cpu_card = self._make_card(grid, "پردازنده (CPU)")
        self.cpu_card.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.lbl_cpu_name = self._add_row(self.cpu_card, "مدل:", platform.processor() or "نامشخص")
        self.lbl_cpu_usage = self._add_row(self.cpu_card, "میزان استفاده:", "...")
        self.lbl_cpu_temp = self._add_row(self.cpu_card, "دما:", "...")
        self.lbl_cpu_cores = self._add_row(self.cpu_card, "هسته‌ها:",
                                            f"{psutil.cpu_count(logical=False)} فیزیکی / "
                                            f"{psutil.cpu_count(logical=True)} منطقی")

        # GPU card
        self.gpu_card = self._make_card(grid, "کارت گرافیک (GPU)")
        self.gpu_card.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.lbl_gpu_name = self._add_row(self.gpu_card, "مدل:", "...")
        self.lbl_gpu_usage = self._add_row(self.gpu_card, "میزان استفاده:", "...")
        self.lbl_gpu_temp = self._add_row(self.gpu_card, "دما:", "...")
        self.lbl_gpu_mem = self._add_row(self.gpu_card, "حافظه:", "...")

        # RAM card
        self.ram_card = self._make_card(grid, "حافظه (RAM)")
        self.ram_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        self.lbl_ram_total = self._add_row(self.ram_card, "کل:", "...")
        self.lbl_ram_used = self._add_row(self.ram_card, "استفاده‌شده:", "...")
        self.ram_bar = ctk.CTkProgressBar(self.ram_card, width=400)
        self.ram_bar.pack(pady=(4, 10))
        self.ram_bar.set(0)

    def _make_card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=14)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(12, 6))
        return card

    def _add_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text=label, anchor="w").pack(side="right")
        val = ctk.CTkLabel(row, text=value, anchor="w", font=ctk.CTkFont(weight="bold"))
        val.pack(side="right", padx=(0, 10))
        return val

    # ------------------------------------------------------------------
    # تب مصرف قطعات (پردازش‌ها)
    # ------------------------------------------------------------------
    def _build_processes_tab(self):
        f = self.tab_processes
        ctk.CTkLabel(f, text="پرمصرف‌ترین پردازش‌ها (CPU)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.proc_box = ctk.CTkTextbox(f, width=900, height=480, font=ctk.CTkFont(family="Consolas", size=13))
        self.proc_box.pack(padx=10, pady=10, fill="both", expand=True)

    # ------------------------------------------------------------------
    # تب شناسایی بازی
    # ------------------------------------------------------------------
    def _build_games_tab(self):
        f = self.tab_games
        ctk.CTkLabel(f, text="بازی‌های در حال اجرا", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.games_box = ctk.CTkTextbox(f, width=900, height=480, font=ctk.CTkFont(size=13))
        self.games_box.pack(padx=10, pady=10, fill="both", expand=True)

    # ------------------------------------------------------------------
    # تب پیش‌بینی FPS
    # ------------------------------------------------------------------
    def _build_fps_tab(self):
        f = self.tab_fps
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(pady=16)

        ctk.CTkLabel(top, text="بازی:").grid(row=0, column=3, padx=6, pady=6)
        self.game_choice = ctk.CTkOptionMenu(top, values=list(games_db.GAMES_DB.keys()))
        self.game_choice.grid(row=0, column=2, padx=6, pady=6)

        ctk.CTkLabel(top, text="رزولوشن:").grid(row=1, column=3, padx=6, pady=6)
        self.res_choice = ctk.CTkOptionMenu(top, values=list(fps_predictor.RESOLUTION_FACTOR.keys()))
        self.res_choice.grid(row=1, column=2, padx=6, pady=6)

        ctk.CTkLabel(top, text="کیفیت:").grid(row=2, column=3, padx=6, pady=6)
        self.quality_choice = ctk.CTkOptionMenu(top, values=list(fps_predictor.QUALITY_FACTOR.keys()))
        self.quality_choice.grid(row=2, column=2, padx=6, pady=6)

        ctk.CTkButton(top, text="محاسبه‌ی تخمین FPS", command=self._on_predict_fps).grid(
            row=3, column=2, columnspan=2, pady=14)

        self.fps_result = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.fps_result.pack(pady=10)

        self.fps_note = ctk.CTkLabel(
            f, text="* این عدد یک تخمین آماری بر اساس مشخصات سخت‌افزار توست، نه اندازه‌گیری واقعی.",
            text_color="#999999")
        self.fps_note.pack()

    def _on_predict_fps(self):
        gpu = sensors.get_gpu_info()
        gpu_name = gpu["name"] if gpu else ""
        ram = sensors.get_ram_info()
        result = fps_predictor.predict_fps(
            game_name=self.game_choice.get(),
            gpu_name=gpu_name,
            cpu_core_count=psutil.cpu_count(logical=False) or 2,
            ram_gb=ram["total_mb"] / 1024,
            resolution=self.res_choice.get(),
            quality=self.quality_choice.get(),
        )
        if result:
            lo, hi = result["range"]
            self.fps_result.configure(
                text=f"تخمین FPS: {result['estimated_fps']}  (بازه‌ی تقریبی {lo}–{hi})"
            )
        else:
            self.fps_result.configure(text="بازی انتخاب نشد.")

    # ------------------------------------------------------------------
    # حلقه‌ی به‌روزرسانی زنده
    # ------------------------------------------------------------------
    def _refresh_loop(self):
        try:
            self._update_dashboard()
            self._update_processes()
            self._update_games()
        except Exception as e:
            print(f"[main] خطا در به‌روزرسانی: {e}")
        self.after(1500, self._refresh_loop)

    def _update_dashboard(self):
        cpu_usage = sensors.get_cpu_usage_percent()
        cpu_temp = sensors.get_cpu_temp()
        self.lbl_cpu_usage.configure(text=f"{cpu_usage:.1f}%")
        self.lbl_cpu_temp.configure(text=f"{cpu_temp}°C" if cpu_temp is not None else "در دسترس نیست")

        gpu = sensors.get_gpu_info()
        if gpu:
            self.lbl_gpu_name.configure(text=gpu["name"])
            self.lbl_gpu_usage.configure(
                text=f"{gpu['load_percent']}%" if gpu["load_percent"] is not None else "نامشخص")
            self.lbl_gpu_temp.configure(text=f"{gpu['temp']}°C" if gpu["temp"] is not None else "در دسترس نیست")
            if gpu["mem_total_mb"]:
                self.lbl_gpu_mem.configure(text=f"{gpu['mem_used_mb']} / {gpu['mem_total_mb']} MB")
            else:
                self.lbl_gpu_mem.configure(text="نامشخص")
        else:
            self.lbl_gpu_name.configure(text="کارت گرافیک شناسایی نشد")

        ram = sensors.get_ram_info()
        self.lbl_ram_total.configure(text=f"{ram['total_mb'] / 1024:.1f} GB")
        self.lbl_ram_used.configure(text=f"{ram['used_mb'] / 1024:.1f} GB ({ram['percent']}%)")
        self.ram_bar.set(ram["percent"] / 100)

    def _update_processes(self):
        procs = sensors.get_top_processes(limit=12)
        self.proc_box.delete("1.0", "end")
        header = f"{'PID':<8}{'نام پردازش':<32}{'CPU%':<10}{'RAM%':<10}\n" + "-" * 60 + "\n"
        self.proc_box.insert("end", header)
        for p in procs:
            self.proc_box.insert(
                "end",
                f"{p['pid']:<8}{(p['name'] or ''):<32}"
                f"{(p['cpu_percent'] or 0):<10.1f}{(p['memory_percent'] or 0):<10.2f}\n"
            )

    def _update_games(self):
        try:
            running = {p.info["name"].lower() for p in psutil.process_iter(["name"]) if p.info["name"]}
        except Exception:
            running = set()

        found = games_db.detect_running_games(running)
        self.games_box.delete("1.0", "end")
        if not found:
            self.games_box.insert("end", "در حال حاضر بازی شناخته‌شده‌ای در حال اجرا نیست.\n")
            return

        for g in found:
            data = games_db.GAMES_DB[g]
            self.games_box.insert("end", f"🎮 {g}\n")
            self.games_box.insert(
                "end",
                f"  حداقل سیستم: CPU={data['min']['cpu']} | GPU={data['min']['gpu']} | RAM={data['min']['ram_gb']}GB\n"
            )
            self.games_box.insert(
                "end",
                f"  پیشنهادی:   CPU={data['recommended']['cpu']} | GPU={data['recommended']['gpu']} | "
                f"RAM={data['recommended']['ram_gb']}GB\n\n"
            )


if __name__ == "__main__":
    app = OriginCoreApp()
    app.mainloop()
