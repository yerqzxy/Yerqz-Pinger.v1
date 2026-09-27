import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import subprocess, threading, time, os, re, csv, datetime

try:
    from PIL import Image, ImageTk, ImageSequence, ImageDraw, ImageFont
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False


class YerqzPinger:
    def __init__(self, root):
        self.root = root
        self.root.title("Yerqz Pinger")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)

        self.running = False
        self.sent = 0
        self.received = 0
        self.timeout = 0
        self.ping_times = []
        self.history = []
        self.bg_frames = []
        self.bg_label = None
        self.current_frame = 0

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.gif_path = os.path.join(self.script_dir, "fondo.gif")

        self.titulo_img = self.crear_imagen_titulo()

        self.bg_label = tk.Label(self.root, bg="#000000")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_widgets()
        self.root.after(200, self.iniciar_gif)

    def cargar_fuente(self, size):
        for nombre in ["C:/Windows/Fonts/consola.ttf", "consola.ttf", "C:/Windows/Fonts/arial.ttf"]:
            try:
                return ImageFont.truetype(nombre, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def crear_imagen_titulo(self):
        if not PILLOW_DISPONIBLE:
            return None

        lineas_ascii = [
            "╦ ╦ ╔═╗ ╦═╗ ╔═╗  ╔═╗  ╔═╗ ╦ ╔╗╔ ╔═╗ ╔═╗ ╦═╗",
            "╚╦╝ ║╣  ╠╦╝ ║═╬╗ ╔═╝  ╠═╝ ║ ║║║ ║ ╦ ║╣  ╠╦╝",
            " ╩  ╚═╝ ╩╚═ ╚═╝╚ ╚═╝  ╩   ╩ ╝╚╝ ╚═╝ ╚═╝ ╩╚═"
        ]

        font_ascii = self.cargar_fuente(16)
        dummy = Image.new("L", (1, 1))
        d = ImageDraw.Draw(dummy)
        bboxes = [d.textbbox((0, 0), l, font=font_ascii) for l in lineas_ascii]
        widths = [b[2] - b[0] for b in bboxes]
        heights = [b[3] - b[1] for b in bboxes]

        pad_a = 10
        W_ascii = max(widths) + pad_a * 2
        H_ascii = sum(heights) + pad_a * 2 + 2

        mask_ascii = Image.new("L", (W_ascii, H_ascii), 0)
        md = ImageDraw.Draw(mask_ascii)
        y = pad_a
        for i, linea in enumerate(lineas_ascii):
            md.text((pad_a, y), linea, font=font_ascii, fill=255)
            y += heights[i] + 1

        sw, sh = 200, 40
        small = Image.new("RGB", (sw, sh))
        for yy in range(sh):
            for xx in range(sw):
                t_v = yy / (sh - 1) if sh > 1 else 0
                t_h = xx / (sw - 1) if sw > 1 else 0
                t = t_h * 0.65 + t_v * 0.35
                if t < 0.5:
                    t2 = t / 0.5
                    r = int(60 + (200 - 60) * t2)
                else:
                    t2 = (t - 0.5) / 0.5
                    r = int(200 + (255 - 200) * t2)
                small.putpixel((xx, yy), (r, 0, 0))

        gradient = small.resize((W_ascii, H_ascii), Image.BICUBIC)
        ascii_img = Image.new("RGBA", (W_ascii, H_ascii), (0, 0, 0, 0))
        ascii_img.paste(gradient, (0, 0), mask_ascii)

        font_info = self.cargar_fuente(15)
        font_big = self.cargar_fuente(17)

        box_W = 640
        box_H = 175
        box = Image.new("RGBA", (box_W, box_H), (0, 0, 0, 170))
        bd = ImageDraw.Draw(box)

        bd.rectangle([0, 0, box_W - 1, box_H - 1], outline=(255, 0, 0), width=2)
        bd.rectangle([5, 5, box_W - 6, box_H - 6], outline=(255, 0, 0), width=1)

        header_text = "[ IP PINGER ]"
        hb = bd.textbbox((0, 0), header_text, font=font_big)
        hw = hb[2] - hb[0]
        hh = hb[3] - hb[1]
        hx = (box_W - hw) // 2
        hy = 14

        line_y = hy + hh // 2 + 3
        bd.line([(25, line_y), (hx - 12, line_y)], fill=(255, 0, 0), width=2)
        bd.line([(hx + hw + 12, line_y), (box_W - 25, line_y)], fill=(255, 0, 0), width=2)
        bd.text((hx, hy), header_text, font=font_big, fill=(255, 255, 255))

        label1 = "[Tiktok]"
        label2 = "[Discord]"
        lb1 = bd.textbbox((0, 0), label1, font=font_info)
        lb2 = bd.textbbox((0, 0), label2, font=font_info)
        lw1 = lb1[2] - lb1[0]
        lw2 = lb2[2] - lb2[0]
        max_lw = max(lw1, lw2)

        handle1 = "@yerqz0"
        handle2 = "91yx."
        hb1 = bd.textbbox((0, 0), handle1, font=font_info)
        hb2 = bd.textbbox((0, 0), handle2, font=font_info)
        hw1 = hb1[2] - hb1[0]
        hw2 = hb2[2] - hb2[0]

        box_pad = 14
        total_w1 = max_lw + 12 + hw1 + box_pad
        total_w2 = max_lw + 12 + hw2 + box_pad
        max_total = max(total_w1, total_w2)

        start_x = (box_W - max_total) // 2

        y1 = hy + hh + 18
        bd.text((start_x, y1), label1, font=font_info, fill=(255, 60, 60))
        box_x1 = start_x + max_lw + 12
        bd.rectangle([box_x1, y1 - 3, box_x1 + hw1 + box_pad, y1 + 21], fill=(0, 100, 200))
        bd.text((box_x1 + box_pad // 2, y1), handle1, font=font_info, fill=(255, 255, 255))

        y2 = y1 + 30
        bd.text((start_x, y2), label2, font=font_info, fill=(255, 60, 60))
        box_x2 = start_x + max_lw + 12
        bd.rectangle([box_x2, y2 - 3, box_x2 + hw2 + box_pad, y2 + 21], fill=(200, 0, 0))
        bd.text((box_x2 + box_pad // 2, y2), handle2, font=font_info, fill=(255, 255, 255))

        y3 = y2 + 36
        please = "Please "
        provide = "PROVIDE"
        the_ip = " The IP"
        pb = bd.textbbox((0, 0), please, font=font_info)
        prb = bd.textbbox((0, 0), provide, font=font_info)
        tib = bd.textbbox((0, 0), the_ip, font=font_info)
        w_p = pb[2] - pb[0]
        w_pr = prb[2] - prb[0]
        w_t = tib[2] - tib[0]
        total_w = w_p + w_pr + w_t + 22
        start_x3 = (box_W - total_w) // 2

        bd.text((start_x3, y3), please, font=font_info, fill=(255, 255, 255))
        px = start_x3 + w_p
        bd.rectangle([px - 3, y3 - 3, px + w_pr + 5, y3 + 21], fill=(220, 0, 0))
        bd.text((px, y3), provide, font=font_info, fill=(255, 255, 255))
        bd.text((px + w_pr, y3), the_ip, font=font_info, fill=(255, 255, 255))

        total_W = max(W_ascii, box_W)
        total_H = H_ascii + box_H + 10

        combined = Image.new("RGBA", (total_W, total_H), (0, 0, 0, 0))
        combined.paste(ascii_img, ((total_W - W_ascii) // 2, 0), ascii_img)
        combined.paste(box, ((total_W - box_W) // 2, H_ascii + 6), box)

        if combined.width > 1150:
            ratio = 1150 / combined.width
            combined = combined.resize((1150, int(combined.height * ratio)), Image.LANCZOS)

        return combined

    def iniciar_gif(self):
        if PILLOW_DISPONIBLE:
            self.cargar_gif(self.gif_path)
        else:
            self.log("[!] Falta Pillow. Ejecuta: pip install pillow")
        self.bg_label.lower()

    def create_widgets(self):
        bg_widget = "#0d0000"
        bg_frame = "#0a0000"
        fg = "#ff2222"
        accent = "#550000"
        entry_bg = "#150000"
        font_main = ("Consolas", 10, "bold")
        font_stats = ("Consolas", 10)

        top = tk.Frame(self.root, bg=bg_widget)
        top.place(x=20, y=270, width=1160, height=38)

        tk.Label(top, text="HOST / IP:", bg=bg_widget, fg=fg, font=font_main).pack(side=tk.LEFT, padx=(8, 0))
        self.host_entry = tk.Entry(top, bg=entry_bg, fg=fg, insertbackground=fg, font=font_main, width=22)
        self.host_entry.pack(side=tk.LEFT, padx=8, pady=6)
        self.host_entry.insert(0, "8.8.8.8")

        self.ping_btn = tk.Button(top, text="PING", bg="#330000", fg=fg, activebackground=accent,
                                  font=font_main, command=self.start_ping, width=6)
        self.ping_btn.pack(side=tk.LEFT, padx=2, pady=6)
        self.stop_btn = tk.Button(top, text="STOP", bg="#330000", fg=fg, activebackground=accent,
                                  font=font_main, command=self.stop_ping, state=tk.DISABLED, width=6)
        self.stop_btn.pack(side=tk.LEFT, padx=2, pady=6)
        self.clear_btn = tk.Button(top, text="CLEAR", bg="#330000", fg=fg, activebackground=accent,
                                   font=font_main, command=self.clear_output, width=6)
        self.clear_btn.pack(side=tk.LEFT, padx=2, pady=6)
        self.export_btn = tk.Button(top, text="CSV", bg="#330000", fg=fg, activebackground=accent,
                                    font=font_main, command=self.export_csv, width=6)
        self.export_btn.pack(side=tk.LEFT, padx=2, pady=6)

        stats_frame = tk.Frame(self.root, bg=bg_frame, bd=1, relief=tk.SUNKEN)
        stats_frame.place(x=20, y=313, width=1160, height=26)

        self.lbl_sent = tk.Label(stats_frame, text="Enviados: 0", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_sent.pack(side=tk.LEFT, padx=4)
        self.lbl_recv = tk.Label(stats_frame, text="Online: 0", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_recv.pack(side=tk.LEFT, padx=4)
        self.lbl_timeout = tk.Label(stats_frame, text="Offline: 0", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_timeout.pack(side=tk.LEFT, padx=4)
        self.lbl_loss = tk.Label(stats_frame, text="Pérdida: 0%", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_loss.pack(side=tk.LEFT, padx=4)
        self.lbl_min = tk.Label(stats_frame, text="Min: 0ms", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_min.pack(side=tk.LEFT, padx=4)
        self.lbl_max = tk.Label(stats_frame, text="Max: 0ms", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_max.pack(side=tk.LEFT, padx=4)
        self.lbl_avg = tk.Label(stats_frame, text="Avg: 0ms", bg=bg_frame, fg=fg, font=font_stats)
        self.lbl_avg.pack(side=tk.LEFT, padx=4)

        self.text_area = scrolledtext.ScrolledText(self.root, bg="#0d0000", fg=fg, insertbackground=fg,
                                                   font=("Consolas", 12), wrap=tk.WORD)
        self.text_area.place(x=20, y=345, width=1160, height=410)
        self.text_area.config(state=tk.DISABLED)

        self.text_area.tag_config("normal", foreground="#ff2222")
        self.text_area.tag_config("tag_time", foreground="#ffffff")
        self.text_area.tag_config("tag_host", foreground="#ff4444")
        self.text_area.tag_config("connected", background="#00cc00", foreground="#ffffff",
                                  font=("Consolas", 12, "bold"))
        self.text_area.tag_config("downed", background="#cc0000", foreground="#ffffff",
                                  font=("Consolas", 12, "bold"))

        bottom = tk.Frame(self.root, bg=bg_widget)
        bottom.place(x=20, y=762, width=1160, height=24)
        self.status_label = tk.Label(bottom, text="STATUS: IDLE", bg=bg_widget, fg=fg, font=font_main)
        self.status_label.pack(side=tk.LEFT)
        self.ip_label = tk.Label(bottom, text="TARGET: 0.0.0.0", bg=bg_widget, fg=fg, font=font_main)
        self.ip_label.pack(side=tk.RIGHT)

    def cargar_gif(self, ruta):
        if not os.path.exists(ruta):
            self.log(f"[!] No existe el archivo: {ruta}")
            return
        try:
            ancho = 1200
            alto = 800

            self.bg_frames = []
            img = Image.open(ruta)
            print(f"[DEBUG] Formato: {img.format}, Modo: {img.mode}, Tamaño: {img.size}")

            for frame in ImageSequence.Iterator(img):
                frame_rgba = frame.convert("RGBA")
                frame_resized = frame_rgba.resize((ancho, alto), Image.LANCZOS)

                if self.titulo_img is not None:
                    tx = (ancho - self.titulo_img.width) // 2
                    ty = 12
                    frame_resized.paste(self.titulo_img, (tx, ty), self.titulo_img)

                photo = ImageTk.PhotoImage(frame_resized)
                self.bg_frames.append(photo)

            print(f"[DEBUG] Frames cargados: {len(self.bg_frames)}")

            if not self.bg_frames:
                return

            self.current_frame = 0
            self.bg_label.config(image=self.bg_frames[0])
            self.bg_label.image = self.bg_frames[0]
            self.bg_label.lower()

            if len(self.bg_frames) > 1:
                self.animar_gif()

            self.log(f"[*] Fondo cargado: {os.path.basename(ruta)} ({len(self.bg_frames)} frames)")
        except Exception as e:
            print(f"[DEBUG] Error: {e}")
            self.log(f"[!] Error al cargar GIF: {e}")

    def animar_gif(self):
        if self.bg_frames and self.bg_label and len(self.bg_frames) > 1:
            self.current_frame = (self.current_frame + 1) % len(self.bg_frames)
            self.bg_label.config(image=self.bg_frames[self.current_frame])
            self.bg_label.image = self.bg_frames[self.current_frame]
            self.root.after(80, self.animar_gif)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"[{timestamp}] ", "tag_time")
        self.text_area.insert(tk.END, f"{message}\n", "normal")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def log_ping(self, host, ok, ping_time=None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        simbolo = "[+]" if ok else "[-]"
        status = "CONNECTED" if ok else "DOWNED"
        tag_status = "connected" if ok else "downed"

        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"[{timestamp}] ", "tag_time")
        self.text_area.insert(tk.END, f"{simbolo} to ", "normal")
        self.text_area.insert(tk.END, f"[ {host} ]", "tag_host")
        self.text_area.insert(tk.END, " Status : ", "normal")
        self.text_area.insert(tk.END, f" {status} ", tag_status)
        if ok and ping_time is not None:
            self.text_area.insert(tk.END, f"  {ping_time:.0f}ms", "normal")
        self.text_area.insert(tk.END, "\n", "normal")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def update_stats(self):
        self.lbl_sent.config(text=f"Enviados: {self.sent}")
        self.lbl_recv.config(text=f"Online: {self.received}")
        self.lbl_timeout.config(text=f"OFF BY CN-: {self.timeout}")
        loss = (self.timeout / self.sent * 100) if self.sent > 0 else 0
        self.lbl_loss.config(text=f"Pérdida: {loss:.1f}%")
        if self.ping_times:
            self.lbl_min.config(text=f"Min: {min(self.ping_times):.0f}ms")
            self.lbl_max.config(text=f"Max: {max(self.ping_times):.0f}ms")
            self.lbl_avg.config(text=f"Avg: {sum(self.ping_times)/len(self.ping_times):.0f}ms")

    def start_ping(self):
        host = self.host_entry.get().strip()
        if not host:
            self.log("[!] Ingresa una IP o dominio.")
            return
        if self.running:
            return
        self.running = True
        self.sent = self.received = self.timeout = 0
        self.ping_times = []
        self.history = []
        self.update_stats()
        self.ip_label.config(text=f"TARGET: {host}")
        self.ping_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="STATUS: PINGING...")
        self.log(f"[*] Iniciando ping a {host}...")
        threading.Thread(target=self.ping_loop, args=(host,), daemon=True).start()

    def ping_loop(self, host):
        is_windows = os.name == 'nt'
        while self.running:
            try:
                if is_windows:
                    cmd = ["ping", "-n", "1", "-w", "2000", host]
                    creationflags = subprocess.CREATE_NO_WINDOW
                else:
                    cmd = ["ping", "-c", "1", "-W", "2", host]
                    creationflags = 0
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3, creationflags=creationflags)
                output = result.stdout + result.stderr
                self.sent += 1
                if result.returncode == 0:
                    self.received += 1
                    ping_time = 1.0
                    match = re.search(r'(?:time|tiempo)[=<]([\d\.]+)ms', output, re.IGNORECASE)
                    if match:
                        ping_time = float(match.group(1))
                    elif "time<1ms" in output.lower() or "tiempo<1ms" in output.lower():
                        ping_time = 0.5
                    self.ping_times.append(ping_time)
                    self.root.after(0, self.log_ping, host, True, ping_time)
                    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.history.append({"timestamp": ts, "host": host, "status": "OK", "time_ms": ping_time})
                else:
                    self.timeout += 1
                    self.root.after(0, self.log_ping, host, False, None)
                    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.history.append({"timestamp": ts, "host": host, "status": "TIMEOUT", "time_ms": ""})
                self.root.after(0, self.update_stats)
            except subprocess.TimeoutExpired:
                self.timeout += 1
                self.sent += 1
                self.root.after(0, self.log_ping, host, False, None)
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.history.append({"timestamp": ts, "host": host, "status": "TIMEOUT", "time_ms": ""})
                self.root.after(0, self.update_stats)
            except Exception as e:
                self.log(f"[!] Error: {e}")
                self.running = False
                break
            time.sleep(1)
        self.root.after(0, self.ping_finished)

    def stop_ping(self):
        if self.running:
            self.running = False
            self.log("[*] Deteniendo ping...")
            self.status_label.config(text="STATUS: STOPPED")
            self.ping_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def ping_finished(self):
        self.running = False
        self.status_label.config(text="STATUS: IDLE")
        self.ping_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def clear_output(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.sent = self.received = self.timeout = 0
        self.ping_times = []
        self.history = []
        self.update_stats()
        self.status_label.config(text="STATUS: IDLE")
        self.ip_label.config(text="TARGET: 0.0.0.0")

    def export_csv(self):
        if not self.history:
            messagebox.showwarning("Sin datos", "No hay datos para exportar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=["timestamp", "host", "status", "time_ms"])
                    writer.writeheader()
                    writer.writerows(self.history)
                self.log(f"[*] Datos exportados a {file_path}")
                messagebox.showinfo("Éxito", "Datos exportados correctamente.")
            except Exception as e:
                self.log(f"[!] Error al exportar: {e}")
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YerqzPinger(root)
    root.mainloop()