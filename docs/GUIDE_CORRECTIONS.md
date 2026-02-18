# 🔧 Guide de Correction - Kara ne s'affiche pas

## 📋 Problèmes identifiés

Après analyse de tes images, j'ai trouvé ces problèmes :

1. **Nom de fichier Kara incorrect** : Tes fichiers montrent `KARA_Standing Idle_base.rig` mais le script cherchait `KARA_Standing Idle_base_rig.fbx`
2. **Le personnage n'apparaît pas dans le rendu** - le mesh n'était pas correctement attaché à l'armature après le scaling
3. **Textures manquantes (rose)** - les matériaux FBX Mixamo n'étaient pas gérés
4. **Le montage ffmpeg n'était pas automatique**

---

## ✅ Solutions apportées

### blender_script.py (NOUVEAU)
- ✅ Recherche **flexible** du fichier Kara (trouve automatiquement le bon nom)
- ✅ Scaling correct de **l'armature ET du mesh**
- ✅ Gestion des **matériaux manquants** (évite le rose!)
- ✅ Création de matériaux par défaut si nécessaire

### blender_oracle.py (NOUVEAU)
- ✅ Recherche automatique de Blender et FFmpeg
- ✅ Assemblage **automatique** des frames PNG en vidéo MP4
- ✅ Noms de fichiers **uniques** avec date/heure
- ✅ Nettoyage automatique des frames après assemblage

---

## 🚀 Instructions d'installation

### Étape 1 : Télécharger les nouveaux scripts

Télécharge ces 2 fichiers depuis le serveur :
- `/home/z/my-project/download/blender_script.py`
- `/home/z/my-project/download/blender_oracle.py`

Et copie-les dans ton dossier :
```
C:\Users\david\bot-actu-3d\scripts\
```

**Pour remplacer les anciens fichiers.**

### Étape 2 : Vérifier que FFmpeg est installé

FFmpeg est nécessaire pour assembler la vidéo finale.

1. Ouvre PowerShell
2. Tape : `ffmpeg -version`
3. Si tu vois une erreur "commande introuvable" :

**Installer FFmpeg sur Windows :**
```
# Option 1: Avec winget (Windows 11)
winget install ffmpeg

# Option 2: Avec Chocolatey
choco install ffmpeg

# Option 3: Télécharger manuellement
# https://www.gyan.dev/ffmpeg/builds/
# Télécharger "ffmpeg-release-essentials.zip"
# Extraire dans C:\ffmpeg
# Ajouter C:\ffmpeg\bin au PATH Windows
```

### Étape 3 : Vérifier la structure des dossiers

```
C:\Users\david\bot-actu-3d\
├── mkdir - p blender\
│   ├── jt_test.blend          ← Ton projet Blender
│   └── animations\
│       ├── KARA_Standing Idle_base.rig  ← Kara avec rig
│       ├── Sitting Drinking.fbx
│       ├── Sitting Talking.fbx
│       ├── Stand To Sit.fbx
│       ├── Stand Up.fbx
│       └── Walking Arc Left.fbx
├── data\
│   └── audio.mp3              ← Audio généré
├── renders\                   ← Dossier de sortie (créé automatiquement)
└── scripts\
    ├── blender_oracle.py      ← NOUVEAU
    └── blender_script.py      ← NOUVEAU
```

### Étape 4 : Tester le rendu

```powershell
cd C:\Users\david\bot-actu-3d
python scripts\blender_oracle.py
```

Si tu as un fichier audio :
```powershell
python scripts\blender_oracle.py --audio data\audio.mp3
```

### Étape 5 : Vérifier le résultat

Le script va :
1. Chercher automatiquement le fichier Kara (même si le nom est différent)
2. Importer Kara et appliquer le scale 6.5
3. Créer l'animation (marche, s'assoit, tourne chaise)
4. Rendre en frames PNG
5. **Assembler automatiquement** en MP4 avec ffmpeg
6. Sauvegarder dans `renders\` avec un nom unique (ex: `jt_output_20250218_191234.mp4`)

---

## 🔍 Dépannage

### Si le personnage est toujours invisible

1. Ouvre ton fichier `jt_test.blend` dans Blender
2. Vérifie que la chaise est nommée avec "chaise" ou "chair" dans son nom
3. Vérifie que le studio est à l'échelle millimètres (scale 0.001)

### Si tu vois encore du rose

Le nouveau script crée automatiquement des matériaux de base.
Mais pour un meilleur résultat :
1. Dans Blender, ouvre le fichier Kara
2. Va dans Shading
3. Vérifie que les textures sont bien connectées
4. Réexporte en FBX si nécessaire

### Si ffmpeg ne fonctionne pas

Ajoute le chemin complet dans le script :
```python
# Dans blender_oracle.py, ligne 51, ajoute ton chemin :
windows_paths = [
    "C:\\TON_CHEMIN\\ffmpeg\\bin\\ffmpeg.exe",
    ...
]
```

---

## 📞 Commandes utiles

```powershell
# Voir les logs Blender
python scripts\blender_oracle.py 2>&1 | Tee-Object -FilePath logs\render.log

# Chercher Blender
where blender

# Chercher ffmpeg
where ffmpeg

# Vérifier le nom du fichier Kara
dir "C:\Users\david\bot-actu-3d\mkdir - p blender\animations\"
```

---

## ✨ Prochaines étapes (Phase 2)

Une fois que ça fonctionne :
- Ajouter plusieurs personnages qui alternent
- Lip-sync automatique
- Objets sur le bureau (figurines, écran hologramme)
- Effets spéciaux (zoom sur figurines)

---

**Télécharge les 2 nouveaux scripts et teste!** 🚀
