import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import shutil
import tempfile
import json
import ctypes
import webbrowser # Added to open web browser links
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

# Apply Windows display scaling (DPI) to prevent text/screen blurring
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Temporarily load Pretendard variable font from the folder into the system on startup (embedded font effect)
try:
    font_path = os.path.join(os.path.dirname(__file__), "PretendardVariable.ttf")
    FR_PRIVATE = 0x10
    ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
except Exception:
    pass

class LufsNormalizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LUFS Normalizer by SEMIDIGITAL")
        
        # 프로그램 종료 시 설정값 저장을 위한 이벤트 바인딩
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply window and taskbar icon
        try:
            self.app_icon = tk.PhotoImage(file="icon.png")
            self.root.iconphoto(True, self.app_icon)
        except Exception:
            pass
        
        # Set window size based on screen ratio (width 35%, height 60%)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_width = int(screen_width * 0.35)
        win_height = int(screen_height * 0.6)
        
        # Center the window on the screen
        x_pos = int((screen_width - win_width) / 2)
        y_pos = int((screen_height - win_height) / 2)
        self.root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
        
        # Fix window size
        self.root.resizable(False, False)
        
        # Dark mode color variables
        self.bg_color = "#1E1E1E"
        self.fg_color = "#FFFFFF"
        self.accent_color = "#4CAF50"
        self.element_bg = "#2D2D2D"
        self.element_active_bg = "#3D3D3D"
        self.list_highlight_bg = "#4A4A4A" # Light gray when selected
        self.gray_text = "#888888"
        
        self.root.configure(bg=self.bg_color)
        
        # Pretendard font settings (variable font based, size maintained and unified)
        self.font_main = ("Pretendard", 12)
        self.font_main_bold = ("Pretendard", 12, "bold")
        self.font_title = ("Pretendard", 16, "bold")
        self.font_sub = ("Pretendard", 10)
        self.font_footer = ("Pretendard", 9)
        self.font_button_start = ("Pretendard", 13, "bold")
        
        self.file_list = []

        # --- Load Saved LUFS Config ---
        self.config_file = "config.json"
        saved_lufs = "-14.0"
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    saved_lufs = config.get("target_lufs", "-14.0")
            except Exception:
                pass

        # --- UI Element Configuration (Left-aligned & Flat Design) ---
        
        # 1. Top Header (Logo and Text)
        header_frame = tk.Frame(root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(20, 10), anchor="w")
        
        try:
            # Shrink sd.png size (maintain subsample 5,5)
            self.logo_img = tk.PhotoImage(file="sd.png").subsample(5, 5)
            logo_lbl = tk.Label(header_frame, image=self.logo_img, bg=self.bg_color, bd=0, cursor="hand2")
            logo_lbl.pack(side="left", padx=(0, 15))
            logo_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://semidigital.co.kr"))
        except Exception:
            logo_lbl = tk.Label(header_frame, text="[IMG]", bg=self.element_bg, fg=self.fg_color, width=5, height=2, font=self.font_main, cursor="hand2")
            logo_lbl.pack(side="left", padx=(0, 15))
            logo_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://semidigital.co.kr"))
            
        text_frame = tk.Frame(header_frame, bg=self.bg_color)
        text_frame.pack(side="left", anchor="w")
        tk.Label(text_frame, text="LUFS Normalizer by SEMIDIGITAL", font=self.font_title, bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        tk.Label(text_frame, text="Version 0.0.2 (Build 20260518)", font=self.font_sub, bg=self.bg_color, fg=self.gray_text).pack(anchor="w", pady=(2, 0))

        # Divider line
        tk.Frame(root, bg=self.element_bg, height=1).pack(fill="x", padx=20, pady=10)

        # 2. LUFS Input Section
        input_frame = tk.Frame(root, bg=self.bg_color)
        input_frame.pack(fill="x", padx=20, pady=5, anchor="w")
        
        tk.Label(input_frame, text="Target Integrated LUFS:", font=self.font_main_bold, bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(0, 10))
        
        self.lufs_entry = tk.Entry(input_frame, width=10, font=self.font_main, bg=self.element_bg, fg=self.fg_color, relief="flat", insertbackground=self.fg_color)
        self.lufs_entry.insert(0, saved_lufs)
        self.lufs_entry.pack(side="left")

        # 3. Add File Button
        self.add_btn = tk.Button(root, text="Add Audio Files", command=self.add_files, width=15, bg=self.element_bg, fg=self.fg_color, font=self.font_main, relief="flat", activebackground=self.element_active_bg, activeforeground=self.fg_color)
        self.add_btn.pack(padx=20, pady=(15, 5), anchor="w")
        
        # 4. List Header (Supported Formats Label on left, Select All / Remove on right)
        list_header_frame = tk.Frame(root, bg=self.bg_color)
        list_header_frame.pack(fill="x", padx=20, pady=(0, 0))
        
        tk.Label(list_header_frame, text="Supported formats: .mp3, .wav", font=self.font_sub, bg=self.bg_color, fg=self.gray_text).pack(side="left", anchor="s")
        
        btn_frame = tk.Frame(list_header_frame, bg=self.bg_color)
        btn_frame.pack(side="right", anchor="s")
        
        self.select_all_btn = tk.Button(btn_frame, text="Select All", command=self.select_all, bg=self.element_bg, fg=self.fg_color, font=self.font_footer, relief="flat", activebackground=self.element_active_bg, activeforeground=self.fg_color, padx=10)
        self.select_all_btn.pack(side="left", padx=(0, 5))
        
        self.delete_btn = tk.Button(btn_frame, text="Remove", command=self.delete_selected, bg=self.element_bg, fg=self.fg_color, font=self.font_footer, relief="flat", activebackground=self.element_active_bg, activeforeground=self.fg_color, padx=10)
        self.delete_btn.pack(side="left")

        list_frame = tk.Frame(root, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Change selection background color to light gray (list_highlight_bg)
        self.listbox = tk.Listbox(list_frame, bg=self.element_bg, fg=self.fg_color, font=self.font_main, relief="flat", highlightthickness=0, selectbackground=self.list_highlight_bg, selectforeground=self.fg_color)
        self.listbox.pack(fill="both", expand=True)
        
        # Bind checkbox toggle function on click
        self.listbox.bind('<Button-1>', self.toggle_selection)

        # 5. Progress Bar - Not placed on screen at initial creation (hidden)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Flat.Horizontal.TProgressbar", troughcolor=self.element_bg, bordercolor=self.bg_color, background=self.accent_color, lightcolor=self.accent_color, darkcolor=self.accent_color, thickness=6)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", style="Flat.Horizontal.TProgressbar")
        # Do not call pack() normally to keep it hidden

        # 6. Start Conversion Button (Default green restored)
        self.start_btn = tk.Button(root, text="Start Conversion (Overwrite Original)", command=self.start_processing, bg=self.accent_color, fg="white", font=self.font_button_start, relief="flat", pady=8, activebackground="#45a049", activeforeground="white")
        self.start_btn.pack(fill="x", padx=20, pady=(5, 15))

        # 7. Bottom Copyright (Small gray text)
        tk.Label(root, text="Copyright © 2026 SEMIDIGITAL. All rights reserved.", font=self.font_footer, bg=self.bg_color, fg=self.gray_text).pack(side="bottom", pady=(0, 15), anchor="center")

        # 8. Social Links (Using PNG icon images in social/ folder)
        social_frame = tk.Frame(root, bg=self.bg_color)
        social_frame.pack(side="bottom", pady=(0, 5))
        
        self.social_icons = {} # Dictionary to prevent image garbage collection
        
        self.create_image_hyperlink(social_frame, os.path.join("social", "youtube.png"), "https://youtube.com/@SEMIDIGITAL")
        self.create_image_hyperlink(social_frame, os.path.join("social", "github.png"), "https://github.com/semidigital-kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "instagram.png"), "https://instagram.com/semidigital_kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "soundcloud.png"), "https://soundcloud.com/semidigital_kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "reddit.png"), "https://www.reddit.com/user/semidigital_kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "x.png"), "https://x.com/semidigital_kr")

    def on_closing(self):
        # Save target LUFS value when closing the app
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"target_lufs": self.lufs_entry.get()}, f)
        except Exception:
            pass
        self.root.destroy()

    def create_image_hyperlink(self, parent, image_path, url):
        try:
            # Adjust icon size (Smaller number = larger icon. Change to 15 or 20 to make it bigger)
            img = tk.PhotoImage(file=image_path).subsample(25, 25) 
            self.social_icons[image_path] = img # Keep reference to prevent garbage collection
            lbl = tk.Label(parent, image=img, bg=self.bg_color, cursor="hand2", bd=0)
            lbl.pack(side="left", padx=8)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
        except Exception:
            fallback_text = os.path.basename(image_path).replace(".png", "").upper()
            lbl = tk.Label(parent, text=fallback_text, font=self.font_footer, bg=self.bg_color, fg=self.gray_text, cursor="hand2")
            lbl.pack(side="left", padx=8)
            lbl.bind("<Enter>", lambda e: lbl.config(fg=self.fg_color))
            lbl.bind("<Leave>", lambda e: lbl.config(fg=self.gray_text))
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.file_list):
            checkbox = "■" if item.get('selected') else "□"
            lufs_str = f"{item['lufs']:+.1f} LUFS" if item['lufs'] is not None else "Analysis Failed"
            filename = os.path.basename(item['path'])
            display_text = f" {checkbox}   {filename}  |  Current: {lufs_str}"
            self.listbox.insert(tk.END, display_text)
            
            if item.get('selected'):
                self.listbox.selection_set(idx)

    def toggle_selection(self, event):
        idx = self.listbox.nearest(event.y)
        if idx >= 0:
            bbox = self.listbox.bbox(idx)
            if bbox and bbox[1] <= event.y <= bbox[1] + bbox[3]:
                self.file_list[idx]['selected'] = not self.file_list[idx].get('selected', False)
                self.refresh_listbox()
        return "break"

    def select_all(self):
        for item in self.file_list:
            item['selected'] = True
        self.refresh_listbox()

    def delete_selected(self):
        self.file_list = [item for item in self.file_list if not item.get('selected')]
        self.refresh_listbox()

    def get_current_lufs(self, filepath):
        command = [
            'ffmpeg', '-i', filepath,
            '-vn', # Ignore album art for speed
            '-af', 'loudnorm=print_format=json',
            '-f', 'null', '-'
        ]
        try:
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            out = result.stderr
            json_start = out.rfind('{')
            json_end = out.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                data = json.loads(out[json_start:json_end])
                return float(data['input_i'])
        except Exception:
            pass
        return None

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=(("Audio Files", "*.mp3 *.wav"), ("MP3 Files", "*.mp3"), ("WAV Files", "*.wav"), ("All Files", "*.*"))
        )
        
        new_files = [f for f in files if not any(item['path'] == f for item in self.file_list)]
        
        if not new_files:
            return

        popup = tk.Toplevel(self.root)
        popup.title("Analyzing...")
        popup.geometry("350x130")
        popup.configure(bg=self.bg_color)
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 65
        popup.geometry(f"+{x}+{y}")
        
        lbl = tk.Label(popup, text="Analyzing LUFS of added files...", font=self.font_main, bg=self.bg_color, fg=self.fg_color)
        lbl.pack(pady=(20, 10))
        
        prog = ttk.Progressbar(popup, orient="horizontal", mode="determinate", length=280, style="Flat.Horizontal.TProgressbar")
        prog.pack(pady=5)
        prog['maximum'] = len(new_files)
        
        for idx, f in enumerate(new_files):
            current_lufs = self.get_current_lufs(f)
            self.file_list.append({'path': f, 'lufs': current_lufs, 'selected': False})
            
            prog['value'] = idx + 1
            popup.update()
            
        popup.destroy()
        self.refresh_listbox()

    def process_file(self, filepath, target_lufs):
        ext = os.path.splitext(filepath)[1].lower()
        temp_file = tempfile.mktemp(suffix=ext)
        
        # 1. FFmpeg 1st Pass (정확한 LUFS 및 True Peak 측정)
        pass1_cmd = [
            'ffmpeg', '-i', filepath,
            '-vn', 
            '-af', 'loudnorm=print_format=json',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(pass1_cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
        out = result.stderr
        
        json_start = out.rfind('{')
        json_end = out.rfind('}') + 1
        
        gain_db = 0.0
        predicted_tp = -1.0
        
        if json_start != -1 and json_end != -1:
            try:
                data = json.loads(out[json_start:json_end])
                measured_i = float(data.get('input_i', '0'))
                measured_tp = float(data.get('input_tp', '0'))
                
                # 순수 선형 게인(Linear Gain) 계산
                gain_db = target_lufs - measured_i
                predicted_tp = measured_tp + gain_db
            except Exception:
                pass
        
        # 클리핑 감지 및 경고 로직 (내부 리미터 비활성화로 인한 안전장치)
        if predicted_tp > 0.0:
            filename = os.path.basename(filepath)
            msg = (f"[{filename}]\n\n"
                   f"Adjusting to {target_lufs} LUFS requires {gain_db:+.1f}dB of gain.\n"
                   f"This will cause Digital Clipping (Predicted Peak: +{predicted_tp:.1f}dB).\n\n"
                   f"The internal limiter is disabled to preserve mix dynamics.\n"
                   f"Do you want to proceed and allow clipping?")
            # FIX: parent=self.root 를 추가하여 경고창이 뒤로 숨는 현상 방지
            ans = messagebox.askyesno("Clipping Warning", msg, parent=self.root)
            if not ans:
                return False # 사용자가 취소를 누르면 해당 파일 변환 건너뜀
        
        # 2. FFmpeg 2nd Pass (다이나믹 스쿼싱을 100% 방지하기 위한 순수 volume 필터 적용)
        command = [
            'ffmpeg', '-y', '-i', filepath,
            '-af', f'volume={gain_db}dB'
        ]
        
        if ext == '.mp3':
            command.extend(['-map_metadata', '-1', '-c:a', 'libmp3lame', '-b:a', '320k'])
        elif ext == '.wav':
            command.extend(['-c:a', 'pcm_s16le'])
            
        command.append(temp_file)
        
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # 3. Extract metadata (MP3 Only)
        if ext == '.mp3':
            try:
                audio_orig = MP3(filepath, ID3=ID3)
                audio_temp = MP3(temp_file, ID3=ID3)
                
                if audio_orig.tags:
                    audio_temp.tags = audio_orig.tags
                    audio_temp.save()
            except Exception as e:
                print(f"Metadata copy error ({os.path.basename(filepath)}): {e}")

        # 4. Overwrite original file
        shutil.move(temp_file, filepath)
        return True

    def start_processing(self):
        if not self.file_list:
            messagebox.showwarning("Warning", "Please add files to process.", parent=self.root)
            return
            
        try:
            target_lufs = float(self.lufs_entry.get())
            with open(self.config_file, 'w') as f:
                json.dump({"target_lufs": self.lufs_entry.get()}, f)
        except ValueError:
            messagebox.showerror("Error", "LUFS value must be a number. (e.g., -14)", parent=self.root)
            return

        # FIX: parent=self.root 추가
        answer = messagebox.askyesno("Confirm", f"The volume of {len(self.file_list)} files in the list will be adjusted to {target_lufs} LUFS and overwritten.\n(Warning: Original files will be modified, please use test files!)\n\nDo you want to proceed?", parent=self.root)
        
        if answer:
            self.start_btn.config(state=tk.DISABLED, text="Processing...", bg=self.element_bg)
            self.progress.pack(fill="x", padx=20, pady=10, before=self.start_btn)
            self.progress['value'] = 0
            self.progress['maximum'] = len(self.file_list)
            self.root.update()

            success_count = 0
            for idx, item in enumerate(self.file_list):
                filepath = item['path']
                try:
                    # process_file이 True를 반환할 때만 성공 카운트 증가 (경고창에서 취소 시 무시됨)
                    processed = self.process_file(filepath, target_lufs)
                    if processed:
                        success_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"[{os.path.basename(filepath)}] Error occurred during processing:\n{str(e)}", parent=self.root)
                
                self.progress['value'] = idx + 1
                self.root.update()
            
            self.file_list.clear()
            self.refresh_listbox()
            self.start_btn.config(state=tk.NORMAL, text="Start Conversion (Overwrite Original)", bg=self.accent_color)
            self.progress['value'] = 0
            self.progress.pack_forget()
            messagebox.showinfo("Complete", f"A total of {success_count} files have been successfully converted!", parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = LufsNormalizerApp(root)
    root.mainloop()