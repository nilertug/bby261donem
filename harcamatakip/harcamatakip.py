import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import os

try:
    from PIL import Image, ImageTk
    PIL_KURULU = True
except ImportError:
    PIL_KURULU = False

KATEGORILER = [
    "Barınma", "Beslenme", "Ulaşım", "Giyim",
    "Kişisel Bakım", "Eğlence", "Diğer"
]

KATEGORI_RENKLERI = {
    "Barınma": "#FF5733",
    "Beslenme": "#33FF57",
    "Ulaşım": "#3357FF",
    "Giyim": "#FF33A1",
    "Kişisel Bakım": "#00CED1",
    "Eğlence": "#F3FF33",
    "Diğer": "#8E33FF",
    "Boş": "#E0E0E0"
}

KATEGORI_FOTOGRAFLARI = {
    "Barınma": "barinma.jpg", "Beslenme": "beslenme.jpg", "Ulaşım": "ulasim.jpg",
    "Giyim": "giyim.jpg", "Kişisel Bakım": "kisisel.jpg", "Eğlence": "eglence.jpg",
    "Diğer": "diger.jpg"
}
FOTO_KLASORU = "images"


class HarcamaUygulamasi(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Harcama Takip Uygulaması")
        self.geometry("450x800")
        self.resizable(False, False)

        # Tüm günlerin verileri burada toplanır
        self.genel_toplam_veriler = []
        self.aktif_gun = 1

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (AnaMenu, GirisEkrani, SonucEkrani):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(AnaMenu)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def takibi_baslat(self):
        self.genel_toplam_veriler = []
        self.aktif_gun = 1
        self.frames[GirisEkrani].ekrani_hazirla(self.aktif_gun)
        self.show_frame(GirisEkrani)

    def gunu_kaydet_ve_ilerle(self, gunluk_liste):
        self.genel_toplam_veriler.extend(gunluk_liste)
        self.aktif_gun += 1
        self.frames[GirisEkrani].ekrani_hazirla(self.aktif_gun)

    def takibi_bitir_ve_hesapla(self, son_gun_listesi):
        if son_gun_listesi:
            self.genel_toplam_veriler.extend(son_gun_listesi)
        
        self.frames[SonucEkrani].sonuclari_goster(self.genel_toplam_veriler, self.aktif_gun)
        self.show_frame(SonucEkrani)


class AnaMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Harcama Takip Uygulaması", font=("Arial", 18, "bold"))
        label.pack(pady=60, padx=10)
        
        aciklama = ttk.Label(self, text="Harcamalarınızı girmek için\nbaşla butonuna tıklayın.", 
                             font=("Arial", 12), justify="center")
        aciklama.pack(pady=20)

        btn = ttk.Button(self, text="Harcamaları Girmeye Başla",
                         command=lambda: controller.takibi_baslat())
        btn.pack(pady=20, ipady=15, fill='x', padx=50)


class GirisEkrani(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.gunluk_liste = []

        self.gun_etiketi = ttk.Label(self, text="1. GÜN", font=("Arial", 16, "bold"), foreground="#333")
        self.gun_etiketi.pack(pady=15)

        
        ust_frame = tk.Frame(self)
        ust_frame.pack(pady=10, padx=10, fill="x")
        tutar_label = ttk.Label(ust_frame, text="Tutar Girin (TL):", font=("Arial", 12))
        tutar_label.pack(side="left", padx=(0, 10))
        self.tutar_entry = ttk.Entry(ust_frame, width=15, font=("Arial", 12))
        self.tutar_entry.pack(side="left", fill="x", expand=True)

        
        kategori_frame = ttk.LabelFrame(self, text="Kategori Seçin")
        kategori_frame.pack(pady=10, padx=10, fill="both", expand=True)
        for kategori in KATEGORILER:
            btn = ttk.Button(kategori_frame, text=kategori,
                             command=lambda k=kategori: self.harcama_ekle(k))
            btn.pack(pady=4, padx=10, fill="x")

        
        self.harcama_listesi_text = ScrolledText(self, height=6, state="disabled", font=("Arial", 10))
        self.harcama_listesi_text.pack(pady=5, padx=10, fill="x")

        
        buton_frame = tk.Frame(self)
        buton_frame.pack(pady=10, padx=10, fill="x")

        
        self.bitir_btn = ttk.Button(buton_frame, text="Günü Bitir -> Sonraki Gün",
                                    command=self.gunu_bitir)
        self.bitir_btn.pack(side="top", fill="x", pady=5)

        
        self.hesapla_btn = ttk.Button(buton_frame, text="TAKİBİ BİTİR VE HESAPLA",
                                      command=self.hesapla)
        self.hesapla_btn.pack(side="top", fill="x", pady=10, ipady=5)

    def ekrani_hazirla(self, gun_no):
        self.gunluk_liste = []
        self.tutar_entry.delete(0, tk.END)
        self.gun_etiketi.config(text=f"{gun_no}. GÜN")
        self.harcama_listesi_text.config(state="normal")
        self.harcama_listesi_text.delete(1.0, tk.END)
        self.harcama_listesi_text.config(state="disabled")

    def harcama_ekle(self, kategori):
        tutar_str = self.tutar_entry.get()
        if not tutar_str:
            messagebox.showwarning("Hata", "Lütfen bir tutar girin.")
            return
        try:
            tutar = float(tutar_str)
            if tutar <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Hata", "Lütfen geçerli bir pozitif sayı girin.")
            self.tutar_entry.delete(0, tk.END)
            return

        self.gunluk_liste.append({"kategori": kategori, "tutar": tutar})
        self.harcama_listesi_text.config(state="normal")
        self.harcama_listesi_text.insert(tk.END, f"- {kategori}: {tutar:.2f} TL\n")
        self.harcama_listesi_text.see(tk.END)
        self.harcama_listesi_text.config(state="disabled")
        self.tutar_entry.delete(0, tk.END)

    def gunu_bitir(self):
        self.controller.gunu_kaydet_ve_ilerle(self.gunluk_liste)

    def hesapla(self):
        self.controller.takibi_bitir_ve_hesapla(self.gunluk_liste)


class SonucEkrani(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._photo_image = None

        main_canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = ttk.Frame(main_canvas)
        scrollable_window = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        def on_canvas_configure(event):
            main_canvas.itemconfig(scrollable_window, width=event.width)
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        main_canvas.bind("<Configure>", on_canvas_configure)

        self.label_baslik = ttk.Label(self.scrollable_frame, text="Harcama Raporu", font=("Arial", 18, "bold"))
        self.label_baslik.pack(pady=10, padx=10)

        self.label_bilgi = ttk.Label(self.scrollable_frame, text="", font=("Arial", 12))
        self.label_bilgi.pack(pady=5)

        self.canvas_width = 300
        self.canvas_height = 300
        canvas_frame = ttk.Frame(self.scrollable_frame)
        canvas_frame.pack(pady=10)
        self.pie_canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.pie_canvas.pack()

        ozet_frame = ttk.LabelFrame(self.scrollable_frame, text="Kategori Dağılımı")
        ozet_frame.pack(pady=10, padx=20, fill="x")
        self.ozet_text = ScrolledText(ozet_frame, height=7, font=("Arial", 11), wrap="word", state="disabled")
        self.ozet_text.pack(fill="x", expand=True, padx=5, pady=5)
        for k, r in KATEGORI_RENKLERI.items():
            self.ozet_text.tag_configure(k, foreground=r)

        self.foto_frame = tk.Frame(self.scrollable_frame, width=150, height=150, bg="lightgrey", relief="groove")
        self.foto_frame.pack(pady=10)
        self.foto_frame.pack_propagate(False)
        self.foto_label = ttk.Label(self.foto_frame, text="Fotoğraf Alanı", anchor="center")
        self.foto_label.pack(fill="both", expand=True)

        self.label_yorum = ttk.Label(self.scrollable_frame, text="", font=("Arial", 12, "italic"), wraplength=400)
        self.label_yorum.pack(pady=10)

        btn = ttk.Button(self.scrollable_frame, text="Ana Menüye Dön",
                         command=lambda: controller.show_frame(AnaMenu))
        btn.pack(pady=10, ipady=10, fill='x', padx=50)

    def sonuclari_goster(self, tum_veriler, toplam_gun):
        kategori_toplamlari = {k: 0 for k in KATEGORILER}
        genel_toplam = 0
        for h in tum_veriler:
            kategori_toplamlari[h["kategori"]] += h["tutar"]
            genel_toplam += h["tutar"]

        kategori_yuzdeleri = {}
        for k, t in kategori_toplamlari.items():
            if t > 0:
                kategori_yuzdeleri[k] = (t / genel_toplam) * 100

        en_cok = "Boş"
        if genel_toplam > 0:
            en_cok = max(kategori_toplamlari, key=kategori_toplamlari.get)

        gunluk_ort = genel_toplam / toplam_gun if toplam_gun > 0 else 0
        self.label_bilgi.config(text=f"Toplam Süre: {toplam_gun} Gün\nToplam: {genel_toplam:.2f} TL\nGünlük Ort: {gunluk_ort:.2f} TL")

        self.ozet_text.config(state="normal")
        self.ozet_text.delete(1.0, tk.END)
        sirali = sorted(kategori_yuzdeleri.items(), key=lambda x: x[1], reverse=True)
        
        if not sirali:
            self.ozet_text.insert(tk.END, "Veri yok.")
        else:
            for k, y in sirali:
                t = kategori_toplamlari[k]
                self.ozet_text.insert(tk.END, f"• {k}: {t:.2f} TL (%{y:.1f})\n", k)
        self.ozet_text.config(state="disabled")

        self.grafik_ciz(sirali)
        
        if en_cok == "Boş":
            self.label_yorum.config(text="Harcama yapılmadı.")
            self.goster_foto("diger.jpg")
        else:
            self.label_yorum.config(text=f"En çok '{en_cok}' kategorisine harcama yapıldı.")
            self.goster_foto(KATEGORI_FOTOGRAFLARI.get(en_cok, "diger.jpg"))

    def grafik_ciz(self, veri):
        self.pie_canvas.delete("all")
        if not veri:
            self.pie_canvas.create_oval(10, 10, 290, 290, fill="#E0E0E0")
            return
        start = 90
        for k, y in veri:
            extent = (y / 100) * 360
            self.pie_canvas.create_arc(10, 10, 290, 290, start=start, extent=extent, fill=KATEGORI_RENKLERI.get(k, "gray"))
            start += extent

    def goster_foto(self, dosya):
        if not PIL_KURULU:
            self.foto_label.config(text="PIL Modülü Yok")
            return
        try:
            path = os.path.join(FOTO_KLASORU, dosya)
            im = Image.open(path).resize((150, 150), Image.Resampling.LANCZOS)
            self._photo_image = ImageTk.PhotoImage(im)
            self.foto_label.config(image=self._photo_image, text="")
        except:
            self.foto_label.config(image=None, text="Resim Yok")

if __name__ == "__main__":
    app = HarcamaUygulamasi()
    app.mainloop()