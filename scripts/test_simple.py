#!/usr/bin/env python3
import json
import sys

print("🎬 TEST SIMPLE - JT 3D")

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("✅ Config loaded!")
    print(f"   Studio: {config['studio']['name']}")
    print(f"   Resolution: {config['studio']['resolution']}")
    print("✅ ALL GOOD! 🚀")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)