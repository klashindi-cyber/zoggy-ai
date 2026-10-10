import os
import base64

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)

# Set FRONTEND_ORIGIN in the hosting provider's environment.
frontend_origin = os.environ.get("FRONTEND_ORIGIN", "")
allowed_origins = [frontend_origin] if frontend_origin else []

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}}
)

# Never place your API key directly in this file.
api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) if api_key else None


@app.get("/")
def home():
    return jsonify({
        "name": "ZOGGY AI Image API",
        "status": "running"
    })


@app.post("/api/generate-image")
def generate_image():
    if client is None:
        return jsonify({
            "error": "Server API key is not configured."
        }), 503

    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()

    if not prompt:
        return jsonify({
            "error": "Please enter an image description."
        }), 400

    if len(prompt) > 4000:
        return jsonify({
            "error": "Description is too long. Use 4000 characters or fewer."
        }), 400

    try:
        result = client.images.generate(
            model="gpt-image-2.5-sunburst",
            prompt=prompt,
            size="1024x1024",
            quality="medium"
        )

        image_base64 = result.data[0].b64_json

        if not image_base64:
            return jsonify({
                "error": "The image service returned no image."
            }), 502

        return jsonify({
            "image": "data:image/png;base64," + image_base64,
            "prompt": prompt
        })

    except Exception:
        app.logger.exception("Image generation failed")
        return jsonify({
            "error": "Image generation failed. Check server logs, API billing, model access and organization verification."
        }), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000"))
      )
