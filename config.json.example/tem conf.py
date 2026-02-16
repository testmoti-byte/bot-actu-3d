{
  "studio": {
    "name": "JT 3D PRINTING NEWS",
    "version": "1.0.0",
    "resolution": "1080x1920",
    "fps": 30,
    "format": "vertical"
  },
  "characters": {
    "kara": {
      "name": "Kara",
      "age": 26,
      "blend_file": "blender/STUDIO2.blend",
      "skeleton_name": "Armature",
      "height_cm": 170
    }
  },
  "blender": {
    "headless": true,
    "project_file": "blender/STUDIO2.blend",
    "output_dir": "renders/",
    "fps": 30
  },
  "scraper": {
    "enabled": true,
    "min_relevance_score": 5
  },
  "ollama": {
    "enabled": true,
    "host": "http://localhost:11434",
    "model": "llama2"
  },
  "gemini": {
    "enabled": true,
    "model": "gemini-pro"
  },
  "tts": {
    "service": "google",
    "enabled": true,
    "language_code": "fr-FR"
  },
  "telegram": {
    "enabled": false
  }
}
```

**Sauvegarde et relance:**
```
python scripts/main.py --test
