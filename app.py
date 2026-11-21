# app.py - Zabar Backend for Render
# Frontend -> POST /convert (PDF) -> Backend -> JSON + Excel

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import tempfile
import traceback

# Tumhara purana parser - is file ka naam parser.py hona chahiye
from parser import process_fab_pdf

app = Flask(__name__)
CORS(app)  # Frontend (Netlify) ko allow karne ke liye

# Temp folder - Render par file store nahi hogi, sirf convert ke liye
UPLOAD_FOLDER = tempfile.gettempdir()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Download ke liye Excel ko thodi der rakhna hoga, phir delete
DOWNLOAD_CACHE = {}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "Zabar - FAB Parser Backend",
        "message": "Backend is live. Use POST /convert to convert PDF."
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/convert", methods=["POST"])
def convert():
    pdf_path = None
    excel_path = None
    try:
        # 1. File aayi ya nahi?
        if "file" not in request.files:
            return jsonify({"status": "error", "error_code": "NO_FILE", "message": "No file uploaded."}), 400

        file = request.files["file"]
        if file.filename == "" or not file.filename.lower().endswith(".pdf"):
            return jsonify({"status": "error", "error_code": "NOT_PDF", "message": "Please upload a PDF file only."}), 400

        # 2. Free ya Pro?
        is_pro_str = request.form.get("is_pro", "false").lower()
        is_pro = is_pro_str in ["true", "1", "yes", "pro"]

        # 3. Unique naam se temp me save karo
        token = str(uuid.uuid4())[:8]
        pdf_path = os.path.join(UPLOAD_FOLDER, f"input_{token}.pdf")
        excel_path = os.path.join(UPLOAD_FOLDER, f"output_{token}.xlsx")
        file.save(pdf_path)

        # 4. Tumhara asal parser chalao - YAHAN ASAL KAAM HOTA HAI
        result = process_fab_pdf(pdf_path, excel_path, is_pro=is_pro)

        # 5. Agar parser ne error diya - password / scanned / not FAB
        if "error" in result:
            err = result["error"]
            # Frontend ko saaf code bhejo taake wo sahi error dikhaye
            if "password" in err.lower():
                code = "PASSWORD_PROTECTED"
            elif "scanned" in err.lower() or "image" in err.lower():
                code = "SCANNED_PDF"
            elif "not a fab" in err.lower() or "fab" in err.lower():
                code = "NOT_FAB"
            else:
                code = "PARSE_ERROR"
            return jsonify({"status": "error", "error_code": code, "message": err}), 400

        # 6. Success - Excel ko cache me rakho, download ke liye
        download_id = str(uuid.uuid4())
        DOWNLOAD_CACHE[download_id] = excel_path
        # Input PDF turant delete - privacy
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # 7. Frontend ko JSON bhejo - Frontend yehi dikhayega, khud kuch nahi banayega
        return jsonify({
            "status": "success",
            "download_id": download_id,
            "download_url": f"/download/{download_id}",
            "metadata": result.get("metadata", {}),
            "tx_count": result.get("tx_count", 0),
            "total_credit": result.get("total_credit", 0),
            "total_debit": result.get("total_debit", 0),
            "total_pages": result.get("total_pages", 0),
            "processed_pages": result.get("processed_pages", 0),
            "locked_pages": result.get("locked_pages", 0),
            "is_pro": is_pro
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"status": "error", "error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        # Input PDF hamesha delete hogi
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass

@app.route("/download/<download_id>", methods=["GET"])
def download_excel(download_id):
    excel_path = DOWNLOAD_CACHE.get(download_id)
    if not excel_path or not os.path.exists(excel_path):
        return jsonify({"status": "error", "message": "File expired. Please convert again."}), 404

    # File bhejne ke baad cache se hata do
    DOWNLOAD_CACHE.pop(download_id, None)
    response = send_file(excel_path, as_attachment=True, download_name="Zabar_FAB_Statement_Converted.xlsx")
    @response.call_on_close
    def cleanup():
        try:
            if os.path.exists(excel_path):
                os.remove(excel_path)
        except:
            pass
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
