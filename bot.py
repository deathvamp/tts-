import pygame
import requests
import io
from pynput import keyboard
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google TTS với Pygame")
        self.root.geometry("500x350")
        
        self.audio_data = None
        self.setup_ui()
        self.start_keyboard_listener()
    
    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Phần nhập văn bản
        ttk.Label(main_frame, text="Văn bản cần chuyển thành giọng nói:").pack(anchor=tk.W)
        self.text_input = tk.Text(main_frame, height=5, width=50)
        self.text_input.pack(fill=tk.X, pady=5)
        
        # Phần chọn ngôn ngữ
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        ttk.Label(lang_frame, text="Ngôn ngữ:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value="vi")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["vi", "en", "fr", "es", "ja"], width=5)
        lang_combo.pack(side=tk.LEFT, padx=5)
        
        # Các nút điều khiển
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Phát", command=self.play_tts).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Phát lại (F4)", command=self.play_tts).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Thoát", command=self.root.quit).pack(side=tk.RIGHT)
        
        # Thanh trạng thái
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_frame = ttk.Frame(main_frame, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, pady=5)
        ttk.Label(status_frame, text="Trạng thái:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X)
        self.progress.pack_forget()  # Ẩn thanh tiến trình ban đầu
    
    def google_tts(self, text, lang='vi'):
        """Lấy audio TTS từ Google Dịch"""
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={lang}&client=tw-ob"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy TTS: {e}")
            return None
    
    def play_audio(self, audio_data):
        """Phát audio bằng Pygame"""
        pygame.mixer.init()
        try:
            with io.BytesIO(audio_data) as audio_file:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                self.status_var.set("Đang phát...")
                
                while pygame.mixer.music.get_busy():
                    self.root.update()
                    pygame.time.Clock().tick(10)
                
                self.status_var.set("Sẵn sàng")
        except Exception as e:
            print(f"Lỗi khi phát audio: {e}")
            self.status_var.set(f"Lỗi: {str(e)}")
    
    def play_tts(self):
        """Xử lý phát TTS"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Lỗi", "Vui lòng nhập văn bản!")
            return
        
        lang = self.lang_var.get()
        self.status_var.set("Đang tải...")
        self.progress.pack(fill=tk.X)
        self.progress.start()
        
        def get_and_play():
            self.audio_data = self.google_tts(text, lang)
            if self.audio_data:
                self.play_audio(self.audio_data)
            else:
                self.status_var.set("Lỗi khi tải audio")
            self.progress.stop()
            self.progress.pack_forget()
        
        Thread(target=get_and_play, daemon=True).start()
    
    def replay(self):
        """Phát lại audio"""
        if self.audio_data:
            self.status_var.set("Đang phát lại...")
            Thread(target=self.play_audio, args=(self.audio_data,), daemon=True).start()
        else:
            messagebox.showerror("Lỗi", "Không có audio để phát lại!")
    
    def on_press(self, key):
        """Xử lý phím bấm"""
        if key == keyboard.Key.f4 and self.play_tts:
            self.root.after(0, self.play_tts)
    
    def start_keyboard_listener(self):
        """Bắt đầu lắng nghe phím bấm"""
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()

if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
    pygame.quit()
