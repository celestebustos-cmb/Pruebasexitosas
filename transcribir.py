#!/usr/bin/env python3
"""
transcribir.py
--------------
Transcribe un audio descargado de WhatsApp Web usando la API de ElevenLabs (Scribe v2).
Optimizado para español latino / argentino.

Uso:
    python transcribir.py <archivo_de_audio>
    python transcribir.py audio.ogg
    python transcribir.py audio.mp3
    python transcribir.py               # busca automáticamente el primer audio en la carpeta

Requisitos:
    pip install elevenlabs python-dotenv

Variables de entorno (archivo .env en la misma carpeta):
    ELEVENLABS_API_KEY=tu_api_key_aqui
"""

import os
import sys
import glob
from pathlib import Path
from datetime import datetime

# ── Dependencias ──────────────────────────────────────────────────────────────
try:
    from elevenlabs import ElevenLabs
except ImportError:
    print("❌ Falta instalar dependencias. Ejecutá:")
    print("   pip install elevenlabs python-dotenv")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv es opcional si ya tenés la variable de entorno seteada


# ── Configuración ─────────────────────────────────────────────────────────────
AUDIO_EXTENSIONS = [".ogg", ".mp3", ".mp4", ".wav", ".m4a", ".opus", ".webm", ".mpeg"]
OUTPUT_DIR = "out"
LANGUAGE_CODE = "es"          # Español (detecta automáticamente variante latina/argentina)
MODEL_ID = "scribe_v2"        # Scribe v2: máxima precisión, 99 idiomas
DIARIZE = False               # Cambiar a True si el audio tiene múltiples oradores


# ── Funciones ─────────────────────────────────────────────────────────────────
def encontrar_audio(ruta_arg: str | None) -> Path:
    """Resuelve el archivo de audio a transcribir."""
    script_dir = Path(__file__).parent

    if ruta_arg:
        # El usuario pasó un archivo como argumento
        audio = Path(ruta_arg)
        if not audio.is_absolute():
            audio = script_dir / audio
        if not audio.exists():
            print(f"❌ No se encontró el archivo: {audio}")
            sys.exit(1)
        return audio

    # Sin argumento: buscar el primer audio soportado en la carpeta del script
    for ext in AUDIO_EXTENSIONS:
        matches = sorted(script_dir.glob(f"*{ext}"))
        if matches:
            return matches[0]

    print("❌ No se encontró ningún archivo de audio en la carpeta.")
    print(f"   Extensiones soportadas: {', '.join(AUDIO_EXTENSIONS)}")
    print("   Uso: python transcribir.py <archivo>")
    sys.exit(1)


def transcribir(audio_path: Path) -> str:
    """Llama a la API de ElevenLabs y devuelve el texto transcripto."""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ No se encontró la API key de ElevenLabs.")
        print("   Creá un archivo .env en esta carpeta con:")
        print("   ELEVENLABS_API_KEY=tu_api_key_aqui")
        print("   O seteá la variable de entorno ELEVENLABS_API_KEY.")
        sys.exit(1)

    client = ElevenLabs(api_key=api_key)

    print(f"🎙️  Transcribiendo: {audio_path.name}")
    print(f"    Modelo   : {MODEL_ID}")
    print(f"    Idioma   : {LANGUAGE_CODE} (español / Argentina)")
    print(f"    Diarizado: {'sí' if DIARIZE else 'no'}")
    print("    ⏳ Procesando...\n")

    with open(audio_path, "rb") as f:
        respuesta = client.speech_to_text.convert(
            file=f,
            model_id=MODEL_ID,
            language_code=LANGUAGE_CODE,
            diarize=DIARIZE,
            tag_audio_events=True,   # Detecta risas, silencios, etc.
            timestamps_granularity="word",
        )

    return respuesta.text


def guardar_transcripcion(texto: str, audio_path: Path) -> Path:
    """Guarda el texto en la carpeta out/ al lado del script."""
    script_dir = Path(__file__).parent
    out_dir = script_dir / OUTPUT_DIR
    out_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = audio_path.stem
    out_file = out_dir / f"{nombre_base}_{timestamp}.txt"

    out_file.write_text(texto, encoding="utf-8")
    return out_file


# ── Punto de entrada ──────────────────────────────────────────────────────────
def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    audio_path = encontrar_audio(arg)

    texto = transcribir(audio_path)

    out_file = guardar_transcripcion(texto, audio_path)

    print("✅ Transcripción completada.\n")
    print("─" * 60)
    print(texto)
    print("─" * 60)
    print(f"\n💾 Guardado en: {out_file}")


if __name__ == "__main__":
    main()
