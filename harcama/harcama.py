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

        self.current_mode = "daily"
        self.gun_sayaci = 0
        self.haftalik_toplam_veriler = []

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (AnaMenu, GunlukGirisEkrani, SonucEkrani):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(AnaMenu)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def start_daily_mode(self):
        self.current_mode = "daily"
        self.gun_sayaci = 0
        self.frames[GunlukGirisEkrani].prepare_for_mode("daily")
        self.show_frame(GunlukGirisEkrani)

    def start_weekly_mode(self):
        self.current_mode = "weekly"
        self.gun_sayaci = 1
        self.haftalik_toplam_veriler = []
        self.frames[GunlukGirisEkrani].prepare_for_mode("weekly", self.gun_sayaci)
        self.show_frame(GunlukGirisEkrani)

    def show_sonuc_ekrani(self, hesaplanmis_sonuclar, mode="daily"):
        sonuc_frame = self.frames[SonucEkrani]
        sonuc_frame.sonuclari_guncelle(hesaplanmis_sonuclar, mode)
        self.show_frame(SonucEkrani)

    def reset_gunluk_ekran(self):
        self.gun_sayaci = 0
        self.haftalik_toplam_veriler = []
        self.current_mode = "daily"
        self.frames[GunlukGirisEkrani].resetle()
        self.frames[GunlukGirisEkrani].prepare_for_mode("daily")


class AnaMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = ttk.Label(self, text="Harcama Takip Uygulaması", font=("Arial", 18, "bold"))
        label.pack(pady=40, padx=10)
        gunluk_btn = ttk.Button(self, text="Günlük Harcamalar",
                                command=lambda: controller.start_daily_mode())
        gunluk_btn.pack(pady=15, ipady=10, fill='x', padx=50)
        haftalik_btn = ttk.Button(self, text="Haftalık Harcamalar",
                                  command=lambda: controller.start_weekly_mode(),
                                  state="normal")
        haftalik_btn.pack(pady=15, ipady=10, fill='x', padx=50)


class GunlukGirisEkrani(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_mode = "daily"
        self.gunluk_harcamalar = []
        self.gun_etiketi = ttk.Label(self, text="", font=("Arial", 14, "bold"))
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
        self.gunu_bitir_btn = ttk.Button(buton_frame, text="Günü Bitir",
                                         command=self.gunu_bitir)
        self.gunu_bitir_btn.pack(side="right", padx=5)
        geri_btn = ttk.Button(buton_frame, text="Ana Menüye Dön",
                             command=lambda: [controller.show_frame(AnaMenu),
                                              controller.reset_gunluk_ekran()])
        geri_btn.pack(side="left", padx=5)

    def harcama_ekle(self, kategori):
        tutar_str = self.tutar_entry.get()
        if not tutar_str:
            messagebox.showwarning("Hata", "Lütfen bir tutar girin.")
            return
        try:
            tutar = float(tutar_str)
            if tutar <= 0:
                raise ValueError("Tutar pozitif olmalı")
        except ValueError:
            messagebox.showwarning("Hata", "Lütfen geçerli bir pozitif sayı girin.")
            self.tutar_entry.delete(0, tk.END)
            return
        self.gunluk_harcamalar.append({"kategori": kategori, "tutar": tutar})
        eklenen_yazi = f"- {kategori}: {tutar:.2f} TL eklendi.\n"
        self.harcama_listesi_text.config(state="normal")
        self.harcama_listesi_text.insert(tk.END, eklenen_yazi)
        self.harcama_listesi_text.see(tk.END)
        self.harcama_listesi_text.config(state="disabled")
        self.tutar_entry.delete(0, tk.END)

    def _hesapla(self, harcama_listesi):
        if not harcama_listesi:
            return None
        kategori_toplamlari = {kategori: 0 for kategori in KATEGORILER}
        toplam_harcama = 0
        for harcama in harcama_listesi:
            kategori_toplamlari[harcama["kategori"]] += harcama["tutar"]
            toplam_harcama += harcama["tutar"]
        kategori_yuzdeleri = {}
        for kategori, toplam in kategori_toplamlari.items():
            if toplam > 0:
                yuzde = (toplam / toplam_harcama) * 100
                kategori_yuzdeleri[kategori] = yuzde
        if toplam_harcama > 0:
            en_cok_harcanan_kategori = max(kategori_toplamlari, key=kategori_toplamlari.get)
        else:
            en_cok_harcanan_kategori = "Boş"
        return {
            "toplam_harcama": toplam_harcama,
            "kategori_toplamlari": kategori_toplamlari,
            "kategori_yuzdeleri": kategori_yuzdeleri,
            "en_cok_harcanan": en_cok_harcanan_kategori
        }

    def gunu_bitir(self):
        if not self.gunluk_harcamalar and \
           (self.current_mode == "daily" or self.controller.gun_sayaci < 7):
            messagebox.showwarning("Uyarı", "Bugün için hiç harcama girmediniz!")
            return
        if self.current_mode == "daily":
            sonuclar = self._hesapla(self.gunluk_harcamalar)
            if sonuclar:
                self.controller.show_sonuc_ekrani(sonuclar, "daily")
        else:
            self.controller.haftalik_toplam_veriler.extend(self.gunluk_harcamalar)
            if self.controller.gun_sayaci == 7:
                sonuclar = self._hesapla(self.controller.haftalik_toplam_veriler)
                if not sonuclar:
                    messagebox.showwarning("Uyarı", "Bütün hafta hiç harcama girmediniz!")
                    return
                self.controller.show_sonuc_ekrani(sonuclar, "weekly")
            else:
                self.resetle()
                self.controller.gun_sayaci += 1
                self.prepare_for_mode("weekly", self.controller.gun_sayaci)

    def resetle(self):
        self.gunluk_harcamalar = []
        self.tutar_entry.delete(0, tk.END)
        self.harcama_listesi_text.config(state="normal")
        self.harcama_listesi_text.delete(1.0, tk.END)
        self.harcama_listesi_text.config(state="disabled")

    def prepare_for_mode(self, mode, gun_no=0):
        self.current_mode = mode
        self.resetle()
        if mode == "daily":
            self.gun_etiketi.pack_forget()
            self.gunu_bitir_btn.config(text="Günü Bitir")
        else:
            self.gun_etiketi.config(text=f"Haftalık Mod: Gün {gun_no} / 7")
            self.gun_etiketi.pack(pady=(10,0))
            if gun_no == 7:
                self.gunu_bitir_btn.config(text="Haftayı Bitir")
            else:
                self.gunu_bitir_btn.config(text="Günü Bitir")


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
        
        # --- DEĞİŞİKLİK BURADA BAŞLIYOR ---
        
        # 'create_window' komutunu bir değişkene atıyoruz
        scrollable_window = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def on_frame_configure(event):
            # Bu fonksiyon kaydırma bölgesini ayarlar (bu doğruydu)
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # Bu YENİ fonksiyon, çerçevenin genişliğini canvas'a eşitler
            canvas_width = event.width
            main_canvas.itemconfig(scrollable_window, width=canvas_width)

        # Fonksiyonları ilgili bileşenlere bağlıyoruz
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        # Canvas'a YENİ bağlama (bind) ekliyoruz
        main_canvas.bind("<Configure>", on_canvas_configure)

        self.label_baslik = ttk.Label(self.scrollable_frame, text="", font=("Arial", 18, "bold"))
        self.label_baslik.pack(pady=10, padx=10)

        self.label_toplam = ttk.Label(self.scrollable_frame, text="", font=("Arial", 14))
        self.label_toplam.pack(pady=(0, 10))

        self.canvas_width = 300
        self.canvas_height = 300
        canvas_frame = ttk.Frame(self.scrollable_frame, width=self.canvas_width, height=self.canvas_height)
        canvas_frame.pack(pady=10)
        canvas_frame.pack_propagate(False)
        self.pie_canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.pie_canvas.pack()

        ozet_baslik_frame = ttk.LabelFrame(self.scrollable_frame, text="Kategori Dağılımı (Yüzdelik)")
        ozet_baslik_frame.pack(pady=10, padx=20, fill="x")

        self.ozet_text = ScrolledText(ozet_baslik_frame, height=7, font=("Arial", 11),
                                      wrap="word", state="disabled")
        self.ozet_text.pack(fill="x", expand=True, padx=5, pady=5)

        for kategori, renk in KATEGORI_RENKLERI.items():
            self.ozet_text.tag_configure(kategori, foreground=renk)

        self.foto_frame_width = 150
        self.foto_frame_height = 150
        self.foto_frame = tk.Frame(self.scrollable_frame, width=self.foto_frame_width, height=self.foto_frame_height, bg="lightgrey", relief="groove")
        self.foto_frame.pack(pady=10)
        self.foto_frame.pack_propagate(False)
        self.foto_label = ttk.Label(self.foto_frame, text="Fotoğraf Alanı", anchor="center")
        self.foto_label.pack(fill="both", expand=True)

        self.label_en_cok = ttk.Label(self.scrollable_frame, text="", font=("Arial", 12, "italic"), wraplength=400)
        self.label_en_cok.pack(pady=10)
        
        geri_btn = ttk.Button(self.scrollable_frame, text="Ana Menüye Dön",
                              command=lambda: [controller.show_frame(AnaMenu),
                                               controller.reset_gunluk_ekran()])
        geri_btn.pack(pady=10, ipady=10, fill='x', padx=50)

    def sonuclari_guncelle(self, sonuclar, mode="daily"):
        toplam_harcama = sonuclar["toplam_harcama"]
        kategori_yuzdeleri = sonuclar["kategori_yuzdeleri"]
        kategori_toplamlari = sonuclar["kategori_toplamlari"]
        en_cok_harcanan = sonuclar["en_cok_harcanan"]
        
        if mode == "daily":
            zaman_eki = "gün"
            baslik = "Günlük Harcama Özeti"
        else:
            zaman_eki = "hafta"
            baslik = "Haftalık Harcama Özeti"
            
        self.label_baslik.config(text=baslik)
        self.label_toplam.config(text=f"Toplam Harcama: {toplam_harcama:.2f} TL")

        sirali_yuzdeler = sorted(kategori_yuzdeleri.items(), key=lambda item: item[1], reverse=True)
        
        self.ozet_text.config(state="normal")
        self.ozet_text.delete(1.0, tk.END)
        
        if not sirali_yuzdeler:
            self.ozet_text.insert(tk.END, "Harcama bilgisi girilmedi.")
        else:
            for kategori, yuzde in sirali_yuzdeler:
                toplam = kategori_toplamlari[kategori]
                renk_tag = kategori
                yazi = f"• {kategori}: {toplam:.2f} TL (%{yuzde:.1f})\n"
                self.ozet_text.insert(tk.END, yazi, renk_tag)
        
        self.ozet_text.config(state="disabled")

        self.ciz_daire_grafik(sirali_yuzdeler)

        if en_cok_harcanan == "Boş":
            self.label_en_cok.config(text=f"Bu {zaman_eki} hiç harcama yapmadın.")
            self.goster_foto("diger.jpg")
        else:
            self.label_en_cok.config(text=f"Bu {zaman_eki} en çok '{en_cok_harcanan}' kategorisinde harcama yaptın.")
            foto_dosyasi = KATEGORI_FOTOGRAFLARI.get(en_cok_harcanan, "diger.jpg")
            self.goster_foto(foto_dosyasi)

    def ciz_daire_grafik(self, sirali_data_listesi):
        self.pie_canvas.delete("all")
        x0, y0 = 10, 10
        x1, y1 = self.canvas_width - 10, self.canvas_height - 10
        
        if not sirali_data_listesi:
            self.pie_canvas.create_oval(x0, y0, x1, y1, fill=KATEGORI_RENKLERI["Boş"], outline="black")
            return
            
        start_angle = 90
        
        for kategori, yuzde in sirali_data_listesi:
            extent = (yuzde / 100) * 360
            renk = KATEGORI_RENKLERI.get(kategori, KATEGORI_RENKLERI["Diğer"])
            self.pie_canvas.create_arc(x0, y0, x1, y1, start=start_angle, extent=extent, fill=renk, outline="black")
            start_angle += extent

    def goster_foto(self, dosya_adi):
        if not PIL_KURULU:
            self.foto_label.config(text="Pillow kütüphanesi yüklü değil.")
            return
        try:
            foto_yolu = os.path.join(FOTO_KLASORU, dosya_adi)
            image = Image.open(foto_yolu)
            image = image.resize((self.foto_frame_width, self.foto_frame_height), Image.Resampling.LANCZOS)
            self._photo_image = ImageTk.PhotoImage(image)
            self.foto_label.config(image=self._photo_image, text="")
        except FileNotFoundError:
            self.foto_label.config(image=None, text=f"{dosya_adi}\n bulunamadı!")
        except Exception as e:
            self.foto_label.config(image=None, text=f"Foto yüklenemedi:\n{e}")

if __name__ == "__main__":
    app = HarcamaUygulamasi()
    app.mainloop()