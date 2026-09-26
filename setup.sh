#!/usr/bin/env bash
# One-time setup per session (takes ~1 minute). Run from the repo root.
set -e
pip install --break-system-packages -q kokoro-onnx soundfile numpy pillow >/dev/null 2>&1 || pip install --break-system-packages kokoro-onnx soundfile numpy pillow
mkdir -p tts out
[ -f tts/kokoro-v1.0.onnx ] || curl -sSfL -o tts/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f tts/voices-v1.0.bin ] || curl -sSfL -o tts/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
which ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
echo "setup ok"
