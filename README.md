# Backup Repository — Telegram Automation & Tools Archive

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Telethon](https://img.shields.io/badge/Telethon-AsyncIO-2CA5E0?style=flat-square&logo=telegram)](https://github.com/LonamiWebs/Telethon)

This repository serves as a versioned backup archive for personal automation suites, scraping tools, and utilities, primarily focused on Telegram channel automation, link harvesting, and media downloading.

---

## 📦 Archive Contents

```
bakup/
├── TelegramToolsUnified/     # Consolidated Telegram CLI automation suite
│   ├── core/                 # Config, authentication & client wrappers
│   ├── modules/              # Video & link scanners and downloaders
│   ├── utils/                # Helpers, rate limiting & logging
│   ├── telegram_unified.py   # Main CLI entry point
│   ├── QUICKSTART.md         # Fast setup walkthrough
│   └── TROUBLESHOOTING.md    # Common errors & connection recovery
├── ResultSystem/             # Archive snapshot of academic results processing tools
├── Telegram Automate/        # Legacy automation scripts
└── new/                      # Working revisions & stage builds
```

---

## 🛠️ Spotlight: TelegramToolsUnified

`TelegramToolsUnified` is a modular Python CLI application built on top of **Telethon** and `asyncio`:
- **Video Scanner & Downloader**: Concurrently scans channel messages for media and streams downloads with progress tracking.
- **Link Harvester**: Intelligent categorization of links, drives, and external resources shared across channels.
- **Session Management**: Secure API ID and hash authentication persistence without requiring repeated logins.

### Quick Run
```bash
cd TelegramToolsUnified
pip install -r requirements.txt
cp config.json.example config.json # Enter API credentials
python telegram_unified.py --help
```

---

## ⚠️ Maintenance Notice
This is an archive repository. Active development for individual tools may be maintained in separate standalone repositories.
