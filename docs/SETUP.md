# 🎬 JT 3D PRINTING NEWS - Studio d'Animation Automatisé

**Un journal télévisé 100% automatisé pour couvrir l'actualité mondiale de l'impression 3D.**

![Status](https://img.shields.io/badge/Status-Development-yellow)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Vision

Un studio de production d'animation 3D qui crée automatiquement des contenus vidéo sur l'impression 3D :
- ✅ **Scrape** 40+ sources (RSS, LinkedIn, Instagram, Twitter, YouTube, Google News)
- ✅ **Analyse** avec Ollama Llama 3.1 8B local
- ✅ **Génère** des scripts avec Gemini
- ✅ **Crée** l'audio avec Google TTS
- ✅ **Rend** les vidéos avec Blender automatiquement
- ✅ **Publie** sur YouTube, TikTok, Instagram

**Tout fonctionne automatiquement via GitHub Actions - Zéro intervention manuelle!**

---

## 🚀 Fonctionnalités

### Core Pipeline
- **Scraper Global** : 40+ sources 3D printing (RSS, APIs, web scraping)
- **News Extraction** : Ollama Llama 3.1 8B analyse les articles localement
- **Script Generation** : Gemini crée dialogues dynamiques
- **TTS** : Google Cloud génère les voix (Léa & Kate)
- **Blender Oracle** : Bot Blender rend vidéos automatiquement
- **Upload** : Telegram, YouTube, TikTok, GitHub

### Formats Supportés
- **JT Court** : 5 minutes (3000 caractères)
- **Mini-Série** : 10-30 minutes (6000-15000 caractères)
- **Film** : 60-120 minutes (60000+ caractères)

### Résolution & Specs
- **Résolution** : 1080×1920 (vertical, pour TikTok/YouTube Shorts)
- **FPS** : 30
- **Codec** : H.264 MP4
- **Audio** : MP3 24kHz

---

## 📋 Prérequis

```
- Python 3.9+
- Blender 3.x+ (headless mode)
- Ollama avec Llama 3.1 8B
- API Keys:
  - Google Gemini
  - Google Cloud TTS
  - Optional: Twitter, Reddit, YouTube
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/bot-actu-3d.git
cd bot-actu-3d

# Python venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install deps
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Créer .env local (NE PAS push sur GitHub!)
cp .env.example .env

# Éditer .env avec tes API keys
nano .env
```

### 3. Blender Setup
```bash
# Prépare ton projet Blender
# - Ajoute animatie personnages (walk, sit_down, idle_sitting)
# - Place-les dans blender/animations/
# - Sauvegarde en blender/jt_test.blend
```

### 4. Test du Pipeline
```bash
# Test scraper seul
python scripts/scraper_complete.py

# Test Ollama
python scripts/ollama_extractor.py

# Test Gemini
python scripts/script_generator.py

# Test TTS
python scripts/tts_generator.py

# Test Blender rendering
python scripts/blender_oracle.py

# Pipeline complète
python scripts/main.py --test
```

### 5. Production
```bash
# Lancer le pipeline complet
python scripts/main.py

# Via GitHub Actions (cron job quotidien)
# Voir .github/workflows/daily_jt.yml
```

---

## 📁 Structure du Projet

```
bot-actu-3d/
├── scripts/
│   ├── main.py                    # Orchestrateur principal
│   ├── scraper_complete.py        # Scraper 40+ sources
│   ├── ollama_extractor.py        # Extraction Ollama Llama 3.1
│   ├── script_generator.py        # Gemini script generation
│   ├── tts_generator.py           # Google TTS
│   ├── blender_oracle.py          # ⭐ MAGIC BOT Blender
│   └── telegram_sender.py         # Upload Telegram
│
├── blender/
│   ├── jt_test.blend             # TON PROJECT BLENDER
│   └── animations/               # Tes animations FBX
│       ├── walk.fbx
│       ├── sit_down.fbx
│       └── idle_sitting.fbx
│
├── data/
│   ├── news_today.json           # News du jour
│   ├── jt_script.json            # Script généré
│   └── audio.mp3                 # Audio TTS généré
│
├── renders/
│   └── jt_output.mp4             # Vidéo finale rendue
│
├── config/
│   ├── sources.json              # Sources RSS/APIs
│   └── studio_settings.json      # Paramètres studio
│
├── docs/
│   ├── SETUP.md
│   ├── BLENDER_GUIDE.md
│   └── API_KEYS.md
│
├── .github/workflows/
│   └── daily_jt.yml              # GitHub Actions automation
│
├── .env.example                  # Template variables
├── config.json.example           # Template config
├── requirements.txt              # Dépendances Python
└── README.md
```

---

## 🔄 Workflow Complet

```
[RSS Feeds]  [LinkedIn]  [Instagram]  [Twitter]  [Reddit]  [YouTube]
      ↓            ↓            ↓          ↓         ↓         ↓
      └────────────────[SCRAPER]────────────────────┘
                        ↓
              [SCORED NEWS (top 3-5)]
                        ↓
              [OLLAMA EXTRACTION (local)]
              (Infos + 3 angles + keywords)
                        ↓
              [GEMINI SCRIPT GENERATION]
              (Dialogue Léa & Kate)
                        ↓
              [GOOGLE TTS]
              (Voix + Audio MP3)
                        ↓
              [BLENDER ORACLE] ⭐
              (Animations + Éclairage + Rendu)
                        ↓
              [VIDEO OUTPUT]
              (1080×1920 MP4)
                        ↓
    [Telegram] [YouTube] [TikTok] [GitHub] [Drive]
```

---

## 🤖 Blender Oracle - Le Magic Bot

**Blender Oracle** est le cœur du système. Il orchestre automatiquement Blender pour :

- ✅ Charger animations Mixamo
- ✅ Appliquer animations au personnage
- ✅ Gérer lip-sync automatique
- ✅ Configurer l'éclairage (cyan + orange + white)
- ✅ Ajouter écran bleu hologramme
- ✅ Ajouter effets glow/bloom
- ✅ Rendre la vidéo finale en MP4

**Voir scripts/blender_oracle.py pour détails!**

---

## 🔐 Sécurité API Keys

**IMPORTANT :** 
- `.env` est dans `.gitignore` - **JAMAIS push sur GitHub**
- `.env.example` est un template public avec des placeholders
- Stocke les vraies clés dans un fichier local `.env`
- GitHub Secrets pour GitHub Actions (voir `.github/workflows/daily_jt.yml`)

---

## 📊 Temps d'Exécution (Estimé)

```
Scraper          : 5-10 min  (dépend des sources)
Ollama Extract   : 1-2 min   (local, rapide)
Gemini Script    : 2-3 min   (API cloud)
Google TTS       : 3-5 min   (génère audio)
Blender Render   : 15-20 min (rendu 1080×1920 @ 30fps)
Upload           : 1-2 min   (Telegram/YouTube)
───────────────────────────────
TOTAL            : 30-45 min (AUTOMATIQUE!) ✅
```

---

## 🐛 Troubleshooting

### Blender not found
```bash
# Set BLENDER_PATH in .env
BLENDER_PATH=/path/to/blender
# Or: which blender  (Linux/Mac)
```

### Ollama connection error
```bash
# Vérifie qu'Ollama est lancé
ollama serve

# Vérifie http://localhost:11434
curl http://localhost:11434/api/generate
```

### API Key errors
- Vérifie .env contient les bonnes clés
- Revoke et crée une nouvelle clé si compromis
- Ne commit JAMAIS ton .env sur GitHub

---

## 📖 Documentation Complète

- [SETUP.md](docs/SETUP.md) - Configuration initiale détaillée
- [BLENDER_GUIDE.md](docs/BLENDER_GUIDE.md) - Guide Blender personnalisé
- [API_KEYS.md](docs/API_KEYS.md) - Obtenir et configurer les clés
- [WORKFLOW.md](docs/WORKFLOW.md) - Détails techniques du pipeline

---

## 🤝 Contributing

Les améliorations sont bienvenues!

```bash
git checkout -b feature/ma-feature
# Fais tes changes
git commit -m "feat: description"
git push origin feature/ma-feature
# Crée une Pull Request
```

---

## 📄 Licence

MIT License - Voir LICENSE pour détails

---

## 👥 Auteur

Créé par **testmoti-byte** - 2026

## 🚀 Status

- ✅ Architecture complète
- ✅ Tous les scripts
- ✅ Documentation
- ⏳ Test initial demain

---

## 📞 Support

Pour les problèmes :
1. Voir [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Check les logs : `logs/jt3d.log`
3. Ouvre une issue sur GitHub

---

**Made with ❤️ for 3D Printing Enthusiasts**
