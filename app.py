from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
from langdetect import detect
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

# ===============================
# HOME ROUTE
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


# ===============================
# TRANSLATION API ROUTE
# ===============================
@app.route("/translate", methods=["POST"])
def translate_text():
    try:
        data = request.get_json()
        text = data.get("text", "")
        source_lang = data.get("source", "auto").lower()
        target_lang = data.get("target", "").lower()

        # detect source language if requested
        if source_lang == "auto":
            source_lang = detect(text).lower()

        # log the translation attempt
        app.logger.debug(f"Translating '{text}' from {source_lang} to {target_lang}")

        translated = GoogleTranslator(
            source=source_lang,
            target=target_lang
        ).translate(text)

        return jsonify({
            "success": True,
            "translated_text": translated,
            "detected_language": source_lang
        })

    except Exception as e:
        # log error for later debugging
        app.logger.error(f"translation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })


# ===============================
# TEXT TO SPEECH ROUTE
# ===============================
@app.route("/speak", methods=["POST"])
def speak_text():
    try:
        data = request.get_json()
        text = data["text"]
        lang = data["lang"]

        # make sure the static directory exists
        os.makedirs("static", exist_ok=True)
        filename = f"static/{uuid.uuid4()}.mp3"

        tts = gTTS(text=text, lang=lang)
        tts.save(filename)

        return jsonify({
            "success": True,
            "audio": filename
        })

    except Exception as e:
        app.logger.error(f"text-to-speech error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)