# 🧼 MediaCleaner — Video va Rasmlardan Yozuv, Raqam va Logolarni Tozalash Ilovasi

Python, OpenCV va FastAPI asosida yaratilgan zamonaviy, yengil va tezkor media tozalash ilovasi. 

Ushbu ilova yordamida foydalanuvchi video yoki rasm yuklaydi, kerakmas suv belgisi (watermark), subtitr, logotip, raqam yoki matnni belgilaydi va ilova fonni sun'iy intellekt / inpainting algoritmlari yordamida tabiiy tiklab, tayyor faylni qaytaradi.

---

## 🌟 Asosiy Imkoniyatlar

1. **Barcha formatlarni qo'llab-quvvatlaydi**:
   - **Rasmlar**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`
   - **Videolar**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.mpg`, `.mpeg`, `.webm`, `.flv`, `.m4v`, `.ts`, `.3gp`
2. **Yengil va Tezkor (Lightweight & Resource-Friendly)**:
   - Og'ir 10GB+ neyron tarmoqlar o'rniga yuqori optimallashgan OpenCV Telea va Navier-Stokes algoritmlari ishlatiladi.
   - Mac va oddiy arzon VPS serverlarda ham CPU orqali tezkor va qotmasdan ishlaydi.
3. **Interaktiv Canvas UI**:
   - Yuklangan video yoki rasm ekranda ochiladi.
   - Sichqoncha bilan xohlagan joydagi yozuv yoki logoni to'rtburchak (Bounding Box) qilib belgilash mumkin.
4. **Tezkor Presetlar**:
   - Pastki o'ng burchak (TikTok, CapCut, Reels logolari)
   - Yuqori o'ng burchak (TV kanallar logolari)
   - Pastki chap / Yuqori chap burchaklar
   - Pastki subtitr qatori (kino va seriallar taglavhalari)
5. **Videolarda Ovozni (Audio) Saqlash**:
   - Videodagi audio oqimi yo'qotilmaydi, avtomatik ajratib olinib, tozalangan video bilan qayta birlashtiriladi.
6. **Xatoliklarni Oldini Olish & Chiroyli UI Error Display**:
   - Noto'g'ri format, shikastlangan fayl, o'lcham chegarasi yoki serverdagi xatoliklar foydalanuvchiga tushunarli tilda qizil ogohlantirish paneli orqali ko'rsatiladi.
7. **Clean Code & DRY (Don't Repeat Yourself)**:
   - Modulli arxitektura: Maska generatsiyasi, Inpainting va Audio birlashtirish funksiyalari ajratilgan va rasm hamda video protsessorlarda qayta ishlatiladi.

---

## 📁 Loyiha Tuzilmasi

```text
media_cleaner/
├── core/
│   ├── __init__.py           # Paket eksportlari
│   ├── exceptions.py         # Maxsus istisnolar (CleanerError, CorruptedFileError)
│   ├── detector.py           # Matn, raqam, belgi va ROI maskasi generatori
│   ├── inpainter.py          # Telea va Navier-Stokes inpainting algoritmlari
│   ├── image_processor.py    # Rasmlarni tozalash moduli
│   └── video_processor.py    # Videolarni kadrma-kadr tozalash va audio muxing
├── web/
│   ├── __init__.py
│   ├── app.py                # FastAPI REST API (upload, process, status, download)
│   ├── config.py             # Sozlamalar (formatlar, hajmlar, portlar)
│   ├── static/
│   │   ├── css/style.css     # Zamonaviy Dark UI, Glassmorphism
│   │   └── js/app.js         # Interaktiv canvas, drag-and-drop, real-time polling
│   └── templates/
│       └── index.html        # Veb-interfeys sahifasi
├── tests/
│   └── test_cleaner.py       # Avtomatlashtirilgan birlik va integratsiya testlari
├── Dockerfile                # Server uchun Docker tasviri
├── docker-compose.yml        # Serverda 1 buyruq bilan ishga tushirish
├── requirements.txt          # Python bog'liqliklari
├── run.py                    # Mahalliy ishga tushirish skripti
└── README.md                 # Hujjatlar
```

---

## 💻 1. Mac Kompyuteringizda Ishlatish va Test Qilish

### 1-qadam: Virtual muhitni faollashtirish
Loyiha papkasida:
```bash
cd "/Users/fds/python project"
source .venv/bin/activate
```

### 2-qadam: Kutubxonalarni tekshirish / o'rnatish
```bash
pip install -r media_cleaner/requirements.txt
```

### 3-qadam: Testlarni yurgazish
```bash
python -m unittest media_cleaner/tests/test_cleaner.py
```
*(Barcha 6 ta test `OK` deb chiqishi kerak)*

### 4-qadam: Ilovani ishga tushirish
```bash
python run_cleaner.py
```
yoki:
```bash
python media_cleaner/run.py
```
Server ishga tushadi va brauzeringizda avtomatik ravishda `http://localhost:8000` manzili ochiladi!

---

## 🚀 2. Serverga (Linux / Ubuntu / VPS) Joylashtirish

Serverga qo'yish uchun 2 xil qulay usul mavjud:

### Variant A: Docker va Docker Compose orqali (Eng oson va tavsiya etiladigan usul)

Serverda Docker va Docker Compose o'rnatilgan bo'lsa:

```bash
# 1. Loyihani serverga nusxalang
cd media_cleaner

# 2. Konteynerni ishga tushiring
docker compose up -d --build
```
Ilova `http://SERVER_IP:8000` portida doimiy ishlaydi. 

### Variant B: To'g'ridan-to'g'ri Linux (Ubuntu/Debian) Serverda

```bash
# 1. Tizim paketlarini o'rnatish (OpenCV va FFmpeg uchun)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libgl1 libglib2.0-0 ffmpeg

# 2. Virtual muhit yaratish
python3 -m venv venv
source venv/bin/activate

# 3. Paketlarni o'rnatish
pip install -r requirements.txt

# 4. Doimiy ishlashi uchun Systemd servisi yaratish:
sudo nano /etc/systemd/system/mediacleaner.service
```

Fayl ichiga quyidagilarni yozing:
```ini
[Unit]
Description=Media Cleaner Web Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/media_cleaner
ExecStart=/var/www/media_cleaner/venv/bin/python run.py --no-browser
Restart=always

[Install]
WantedBy=multi-user.target
```

Servisni yoqing:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mediacleaner
sudo systemctl start mediacleaner
```

---

## 🔒 Xavfsizlik va Resurslarni Boshqarish
- Fayl yuklash hajmi maksimal 500 MB qilib sozlangan (`media_cleaner/web/config.py`).
- Yuklangan va tozalangan fayllar `uploads/` va `outputs/` papkalarida saqlanadi.
- Kadrlar xotirani to'ldirmasligi uchun stream rejimida birma-bir o'qiladi va tozalanadi.
