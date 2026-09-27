"""Text-to-speech for the 'Hear this screen' feature."""
import io
from gtts import gTTS

_LANG_CODES = {"English": "en", "French": "fr", "Arabic": "ar"}


def script_to_speech(script_lines, language="English"):
    text = ". ".join(script_lines)
    lang = _LANG_CODES.get(language, "en")
    tts = gTTS(text=text, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf
