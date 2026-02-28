from flask import Flask, render_template, request, send_file, jsonify
import qrcode
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

TEMPLATES = {
    "classic": {
        "name": "Classic",       "desc": "Timeless black & white",  "icon": "◼",
        "fill": "#000000",       "back": "#ffffff",
        "card_bg": "linear-gradient(135deg,#1a1a1a,#3a3a3a)",
    },
    "neon": {
        "name": "Neon Pulse",    "desc": "Electric cyan on dark",   "icon": "⚡",
        "fill": "#00fff0",       "back": "#050518",
        "card_bg": "linear-gradient(135deg,#050518,#0a1628)",
    },
    "fire": {
        "name": "Inferno",       "desc": "Blazing orange & red",    "icon": "🔥",
        "fill": "#ff4500",       "back": "#1a0500",
        "card_bg": "linear-gradient(135deg,#1a0500,#3d0f00)",
    },
    "forest": {
        "name": "Forest",        "desc": "Fresh nature greens",     "icon": "🌿",
        "fill": "#1b5e20",       "back": "#f1f8f4",
        "card_bg": "linear-gradient(135deg,#e8f5e9,#a5d6a7)",
    },
    "galaxy": {
        "name": "Galaxy",        "desc": "Deep cosmic purple",      "icon": "🌌",
        "fill": "#b388ff",       "back": "#0d0221",
        "card_bg": "linear-gradient(135deg,#0d0221,#1a0533)",
    },
    "gold": {
        "name": "Gold Rush",     "desc": "Premium luxury gold",     "icon": "✦",
        "fill": "#d4a017",       "back": "#1c1200",
        "card_bg": "linear-gradient(135deg,#1c1200,#3d2b00)",
    },
    "ocean": {
        "name": "Ocean",         "desc": "Deep sea blues",          "icon": "🌊",
        "fill": "#00b4d8",       "back": "#03045e",
        "card_bg": "linear-gradient(135deg,#03045e,#0077b6)",
    },
    "rose": {
        "name": "Rose Gold",     "desc": "Elegant pink luxury",     "icon": "🌸",
        "fill": "#c2185b",       "back": "#fff0f5",
        "card_bg": "linear-gradient(135deg,#fce4ec,#f8bbd9)",
    },
    "midnight": {
        "name": "Midnight",      "desc": "Dark blue elegance",      "icon": "🌙",
        "fill": "#90caf9",       "back": "#0a0e1a",
        "card_bg": "linear-gradient(135deg,#0a0e1a,#0d1b2a)",
    },
}

TEMPLATE_BG = {k: v["card_bg"] for k, v in TEMPLATES.items()}

@app.template_global()
def tmpl_bg(key):
    return TEMPLATE_BG.get(key, "#111")

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def generate_qr_image(data, template_key):
    tmpl = TEMPLATES.get(template_key, TEMPLATES["classic"])
    fill_rgb = hex_to_rgb(tmpl["fill"])
    back_rgb = hex_to_rgb(tmpl["back"])

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_rgb, back_color=back_rgb)
    img = img.convert("RGB")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/generator")
def generator():
    return render_template("index.html", templates=TEMPLATES)

@app.route("/generate", methods=["POST"])
def generate_qr():
    data = request.form.get("data", "").strip()
    template_key = request.form.get("template", "classic")
    download = request.form.get("download", "false") == "true"

    if not data:
        return jsonify({"error": "Please enter text or a URL."}), 400

    try:
        img_bytes = generate_qr_image(data, template_key)

        if download:
            buf = BytesIO(img_bytes)
            return send_file(buf, mimetype="image/png", as_attachment=True,
                             download_name=f"justify_qr_{template_key}.png")

        b64 = base64.b64encode(img_bytes).decode("utf-8")
        return jsonify({"image": f"data:image/png;base64,{b64}", "ok": True})

    except Exception as e:
        app.logger.error(f"QR Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000,debug=true)
