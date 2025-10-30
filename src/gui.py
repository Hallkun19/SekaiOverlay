# src/gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.generator import Generator

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sekai Overlay Generator v3.0")
        self.geometry("500x680")
        self.resizable(False, False)
        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        try:
            from ttkthemes import ThemedTk
            # ThemedTkに自分自身をアップグレード
            ThemedTk(self, theme="arc")
        except ImportError:
            pass # ttkthemesがなくても動作する
        
        style = ttk.Style(self)
        style.configure("Accent.TButton", font=("", 10, "bold"))

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)

        # --- 譜面情報 ---
        id_frame = ttk.LabelFrame(main_frame, text="譜面情報", padding="10")
        id_frame.grid(row=0, column=0, sticky="ew")
        id_frame.columnconfigure(0, weight=1)
        ttk.Label(id_frame, text="譜面ID (例: UnCh-XXXX):").pack(anchor="w")
        self.full_level_id_var = tk.StringVar()
        ttk.Entry(id_frame, textvariable=self.full_level_id_var).pack(fill="x", pady=(2, 5))

        # --- メタデータ ---
        meta_frame = ttk.LabelFrame(main_frame, text="楽曲・譜面情報 (空白でlevel.jsonの値を使用)", padding="10")
        meta_frame.grid(row=1, column=0, sticky="ew", pady=10)
        meta_frame.columnconfigure(1, weight=1)
        self.meta_vars = self._create_meta_fields(meta_frame)

        # --- 生成設定 ---
        settings_frame = ttk.LabelFrame(main_frame, text="生成設定", padding="10")
        settings_frame.grid(row=2, column=0, sticky="ew")
        settings_frame.columnconfigure(1, weight=1)
        self._create_settings_fields(settings_frame)

        # --- 実行 ---
        self.run_button = ttk.Button(main_frame, text="生成開始", command=self._start_generation, style="Accent.TButton")
        self.run_button.grid(row=3, column=0, pady=20, ipady=5, sticky="ew")
        self.status_var = tk.StringVar(value="待機中...")
        ttk.Label(main_frame, textvariable=self.status_var, relief="sunken", anchor="center").grid(row=4, column=0, sticky="ew", ipady=3)

    def _create_meta_fields(self, parent):
        meta_vars = {}
        fields = ["タイトル (title)", "譜面制作 (author)", "作詞 (words)", "作曲 (music)", "編曲 (arrange)", "ボーカル (vocal)"]
        for i, field_text in enumerate(fields):
            key = field_text.split('(')[1][:-1]
            ttk.Label(parent, text=f"{field_text}:").grid(row=i, column=0, sticky="w", pady=2, padx=5)
            var = tk.StringVar()
            ttk.Entry(parent, textvariable=var).grid(row=i, column=1, sticky="ew", pady=2)
            meta_vars[key] = var
        return meta_vars

    def _create_settings_fields(self, parent):
        ttk.Label(parent, text="難易度:").grid(row=0, column=0, sticky="w", pady=5)
        self.difficulty_var = tk.StringVar()
        diff_combo = ttk.Combobox(parent, textvariable=self.difficulty_var, values=["easy", "normal", "hard", "expert", "master", "append", "custom"])
        diff_combo.grid(row=0, column=1, sticky="ew", pady=5)
        diff_combo.set("master")
        
        custom_diff_entry = ttk.Entry(parent, textvariable=self.difficulty_var, state="disabled")
        custom_diff_entry.grid(row=1, column=1, sticky="ew", pady=(0, 5))
        diff_combo.bind("<<ComboboxSelected>>", lambda e: custom_diff_entry.config(state="normal" if self.difficulty_var.get() == "custom" else "disabled"))

        ttk.Label(parent, text="チーム総合力:").grid(row=2, column=0, sticky="w", pady=5)
        self.team_power_var = tk.StringVar(value="250000")
        ttk.Entry(parent, textvariable=self.team_power_var).grid(row=2, column=1, sticky="ew", pady=5)
        
        ttk.Label(parent, text="背景バージョン:").grid(row=3, column=0, sticky="w", pady=5)
        self.bg_version_var = tk.StringVar(value="3")
        bg_radio_frame = ttk.Frame(parent)
        bg_radio_frame.grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(bg_radio_frame, text="v3", variable=self.bg_version_var, value="3").pack(side="left", padx=5)
        ttk.Radiobutton(bg_radio_frame, text="v1", variable=self.bg_version_var, value="1").pack(side="left", padx=5)

    def _start_generation(self):
        self.run_button.config(state="disabled")
        
        config = {
            "full_level_id": self.full_level_id_var.get().strip(),
            "bg_version": self.bg_version_var.get(),
            "team_power": float(self.team_power_var.get()),
            "extra_data": {key: var.get() for key, var in self.meta_vars.items()}
        }
        config["extra_data"]["difficulty"] = self.difficulty_var.get()
        
        thread = threading.Thread(target=self._run_generator, args=(config,), daemon=True)
        thread.start()

    def _run_generator(self, config):
        generator = Generator(config, lambda msg: self.status_var.set(msg))
        success, message = generator.run()
        
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("エラー", message)
            
        self.run_button.config(state="normal")