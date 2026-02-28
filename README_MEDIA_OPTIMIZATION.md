# Media Optimization Workflow

Prosty workflow do optymalizacji zdjęć i wideo pod stronę internetową.

## 🚀 Szybki start

### 1. Wrzuć pliki do folderu input
```bash
cp twoje_zdjecie.jpg media_optimization/media_optimization_input/
cp twoje_wideo.mp4 media_optimization/media_optimization_input/
```

### 2. Uruchom optymalizację
```bash
./optimize.sh
```

### 3. Odbierz zoptymalizowane pliki z output
Gotowe! Twoje pliki są w `media_optimization/Media_optimization_output/`

---

## 📋 Co robi ten workflow?

### Dla zdjęć (JPG, PNG, etc.):
- ✅ Konwertuje do **WebP** (najlepszy format dla web - mniejsze pliki, lepsza jakość)
- ✅ Kompresja z jakością 85 (konfigurowalne)
- ✅ Zachowuje oryginalna rozdzielczość
- ✅ Opcjonalnie: responsive versions (wyłączone domyślnie)

### Dla wideo (MP4, MOV, etc.):
- ✅ Konwertuje do **MP4** z H.264 (uniwersalna kompatybilność)
- ✅ Optymalizuje ustawienia (CRF 23, AAC audio 128kbps)
- ✅ Skaluje do max 1920px szerokości
- ✅ Generuje **miniaturkę** (pierwszy frame jako WebP)
- ✅ Opcjonalnie: wersja **WebM** dla nowoczesnych przeglądarek

---

## 🎯 Opcje

### Podstawowe użycie
```bash
./optimize.sh
```

### Niestandardowa jakość (1-100, domyślnie 85)
```bash
./optimize.sh --quality 90
```

### Generuj responsive sizes dla obrazów
```bash
./optimize.sh --responsive
```

### Generuj WebM dla wideo
```bash
./optimize.sh --webm
```

---

## 📦 Wymagania

### Python packages (już zainstalowane)
- Pillow (obrazy)
- ffmpeg-python (wideo)

### FFmpeg (już zainstalowane w `.bin/`)
FFmpeg i ffprobe są już gotowe do użycia w folderze `.bin/`. Skrypt `optimize.sh` automatycznie ustawia ścieżkę.

---

## 📁 Struktura folderów

```
.
├── media_optimization/
│   ├── media_optimization_input/   # Wrzucaj tu pliki
│   └── Media_optimization_output/  # Zoptymalizowane pliki
├── .bin/
│   ├── ffmpeg                       # FFmpeg binary
│   └── ffprobe                      # FFprobe binary
├── optimize.sh                      # Główny skrypt (użyj tego!)
├── directives/
│   └── optimize_media.md            # Szczegółowa dokumentacja
└── execution/
    └── optimize_media.py            # Python skrypt (nie uruchamiaj bezpośrednio)
```

---

## 📊 Przykładowy output

```
============================================================
  MEDIA OPTIMIZATION
============================================================
Quality: 85
Responsive: False
WebM: False
============================================================

✓ photo.jpg
  Original: 1.61 MB
  Optimized: 73.64 KB (photo.webp)
  Saved: 1.54 MB (95.5%)

⏳ Processing video.mp4 (this may take a while)...
✓ video.mp4
  Original: 21.57 MB
  Optimized (MP4): 5.39 MB
  Saved: 16.18 MB (75.0%)
  Thumbnail: video_thumb.webp

============================================================
  SUMMARY
============================================================
Processed: 2 files
Skipped: 0 files
Total original size: 23.18 MB
Total optimized size: 5.46 MB
Total saved: 17.72 MB (76.4%)
Time: 14.6s

✓ Optimized files saved to 'media_optimization/Media_optimization_output/'
============================================================
```

---

## 🔥 Porady

### Dla stron internetowych:
1. **WebP z fallback**: Użyj elementu `<picture>` dla kompatybilności ze starymi przeglądarkami
   ```html
   <picture>
     <source srcset="image.webp" type="image/webp">
     <img src="image.jpg" alt="Description">
   </picture>
   ```

2. **Lazy loading**: Dodaj `loading="lazy"` dla lepszej wydajności
   ```html
   <img src="image.webp" loading="lazy" alt="Description">
   ```

### Dla wideo:
```html
<video controls poster="video_thumb.webp">
  <source src="video_optimized.webm" type="video/webm">
  <source src="video_optimized.mp4" type="video/mp4">
  Your browser doesn't support video.
</video>
```

---

## 🐛 Troubleshooting

**Problem**: Skrypt nie działa
**Rozwiązanie**: Upewnij się że uruchamiasz `./optimize.sh` a nie bezpośrednio python skrypt

**Problem**: Kolory wyglądają inaczej po optymalizacji
**Rozwiązanie**: Skrypt automatycznie zachowuje profile kolorów

**Problem**: Plik wideo nadal za duży
**Rozwiązanie**:
- Użyj niższego CRF (edytuj skrypt: zmień `crf=23` na np. `crf=28`)
- Zmniejsz rozdzielczość
- Skróć wideo

---

## 📖 Więcej informacji

Szczegółowa dokumentacja znajduje się w [directives/optimize_media.md](directives/optimize_media.md)

---

## 🎉 Gotowe!

Workflow jest gotowy do użycia:
1. Wrzuć pliki do `media_optimization/media_optimization_input/`
2. Uruchom `./optimize.sh`
3. Odbierz zoptymalizowane pliki z `media_optimization/Media_optimization_output/`

Proste! 🚀
