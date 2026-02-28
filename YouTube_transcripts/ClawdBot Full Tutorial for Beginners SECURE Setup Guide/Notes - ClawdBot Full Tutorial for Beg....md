# Notatki: ClawdBot Full Tutorial for Beginners: SECURE Setup Guide

## 🚀 Główna Koncepcja (Core Concept)
Video to przewodnik po bezpiecznej konfiguracji "ClawdBot" (OpenClaw) - otwartoźródłowego oprogramowania orkiestrującego modele LLM. Głównym celem jest uruchomienie bota na wirtualnym serwerze prywatnym (VPS) zamiast na komputerze domowym, aby chronić dane i sieć lokalną, oraz zastosowanie zaawansowanych zabezpieczeń (VPN, firewall, osobne konta).

## 🛠️ Praktyczne Metody i Przepływy Pracy (Actionable Methods & Workflows)

### 1. Konfiguracja VPS (Virtual Private Server)
- **Wybór serwera**: Zalecany jest VPS w chmurze (np. Hostinger, plan KVM2) zamiast domowego komputera (Mac Mini itp.), co zapewnia lepsze bezpieczeństwo fizyczne, backupy i stabilność łącza.
- **System**: Debian 13 (lub Ubuntu).
- **Inicjalizacja**: Ustaw silne, losowe hasło dla użytkownika `root`.

### 2. Zabezpieczenie Sieci za pomocą Tailscale (VPN)
Aby serwer nie był dostępny publicznie z całego internetu:
- Zainstaluj Tailscale na VPS: `curl -fsSL https://tailscale.com/install.sh | sh`.
- Uruchom usługę SSH w Tailscale: `tailscale up --ssh`.
- Uwierzytelnij serwer w sieci Tailscale (logowanie przez przeglądarkę).
- Zainstaluj Tailscale na swoim komputerze lokalnym i połącz się z tą samą siecią.

### 3. Konfiguracja SSH i Nowego Użytkownika
- Edytuj plik konfiguracyjny SSH (`nano /etc/ssh/sshd_config`):
    - Odkomentuj i ustaw `ListenAddress` na adres IP z Tailscale (zaczynający się np. od 100.x.x.x).
    - Ustaw `PasswordAuthentication` na `no` (wymusza klucze/Tailscale).
    - Ustaw `PermitRootLogin` na `no` (blokuje logowanie na roota).
- Utwórz nowego użytkownika (nie-root): `adduser [nazwa]`.
- Dodaj użytkownika do grupy sudo: `usermod -aG sudo [nazwa]`.
- Zrestartuj usługę SSH: `systemctl restart ssh`.
- **Efekt**: Logowanie jest możliwe tylko przez sieć VPN i tylko na stworzonego użytkownika.

### 4. Firewall
- Skonfiguruj firewall u dostawcy VPS (np. w panelu Hostinger).
- Zablokuj cały ruch przychodzący (Deny All).
- Dodaj wyjątek tylko dla UDP port `41641` (dla Tailscale).
- Nie otwieraj portów 22 (SSH), 80 ani 443, chyba że planujesz hostować publiczną stronę www.

### 5. Instalacja i Konfiguracja OpenClaw
- Zaloguj się jako nowy użytkownik: `ssh [użytkownik]@[tailscale-ip]`.
- Zainstaluj OpenClaw (jedną komendą ze strony projektu).
- **Modele LLM**:
    - Można użyć kluczy API, ale jest to drogie.
    - **Zalecana metoda**: Użycie "Codex" (OpenAI) lub tokena sesji (Anthropic) z istniejącej subskrypcji (np. ChatGPT Plus / Claude Pro). Pozwala to na korzystanie z modeli w ramach stałej opłaty miesięcznej (np. 20$).
- **Kanał komunikacji**: Telegram. Utwórz bota przez @BotFather, skopiuj token i podłącz w konfiguracji OpenClaw.

### 6. Dostęp do Panelu (UI)
- Interfejs OpenClaw działa na porcie `18789`, który nie jest wystawiony publicznie.
- Aby się do niego dostać, użyj tunelowania SSH (Port Forwarding):
  ```bash
  ssh -N -L 18789:127.0.0.1:18789 [użytkownik]@[tailscale-ip]
  ```
- Otwórz w przeglądarce: `http://127.0.0.1:18789`.

### 7. Ochrona przed Prompt Injection (Sandboxing)
- **Zasada izolacji**: Nie podłączaj do bota swoich głównych, prywatnych kont (Gmail, Google Drive,  portfele krypto).
- Utwórz dedykowane, "puste" konta Google/Email dla bota.
- Jeśli chcesz, aby bot przetworzył maila, przekaż go (forward) ręcznie na adres bota ze swojego zaufanego konta.
- To chroni przed atakami, gdzie złośliwy mail mógłby zmusić bota do wykadnięcia danych lub wykonania niebezpiecznych akcji.

## 💡 Kluczowe Spostrzeżenia (Key Insights)
- **OpenClaw to nie model AI**: To oprogramowanie "orkiestrujące", które zarządza rozmową i narzędziami, ale "mózgiem" są zewnętrzne modele (GPT-4, Claude 3.5).
- **Bezpieczeństwo przez ukrycie**: Dzięki Tailscale i konfiguracji `ListenAddress`, serwer jest technicznie "niewidzialny" dla skanerów portów i botów w publicznym internecie.
- **Ekonomia tokenów**: Wykorzystanie tokenów sesji z subskrypcji konsumenckich (Pro/Plus) jest drastycznie tańsze niż płacenie za tokeny przez API przy intensywnym użytkowaniu agenta.

## 🔗 Narzędzia i Zasoby (Tools & Resources)
- **Hostinger**: Platforma VPS (polecana w wideo).
- **Tailscale**: Sieć VPN typu Mesh do bezpiecznego łączenia urządzeń bez publicznych adresów IP.
- **OpenClaw**: Otwartoźródłowy agent/bot AI.
- **Telegram**: Aplikacja do bezpiecznej komunikacji z botem.
