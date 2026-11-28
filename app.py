import os
import json
import uuid
import base64
import streamlit as st
import streamlit.components.v1 as components
from parser import process_fab_pdf

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Salamum | FAB Statement to Excel",
    page_icon="📊",
    layout="centered",
)

os.makedirs("temp_files", exist_ok=True)


def send_to_parent(msg_type: str, payload: dict):
    safe_json = json.dumps({"type": msg_type, "payload": payload}, ensure_ascii=False)
    safe_json_js = safe_json.replace("</", "<\\/")
    components.html(
        f"""
        <script>
        (function() {{
          const data = {safe_json_js};
          function hideBadges() {{
            try {{
              const doc = window.parent && window.parent.document ? window.parent.document : document;
              const selectors = [
                '[data-testid="stViewerBadge"]',
                '[class*="viewerBadge"]',
                '[class*="stActionButton"]',
                'footer',
                '[data-testid="stBottom"]'
              ];
              for (const sel of selectors) {{
                doc.querySelectorAll(sel).forEach((el) => {{
                  el.style.setProperty("display", "none", "important");
                  el.style.setProperty("visibility", "hidden", "important");
                  el.style.setProperty("height", "0px", "important");
                }});
              }}
            }} catch (e) {{}}
          }}
          hideBadges();
          setTimeout(hideBadges, 120);
          setTimeout(hideBadges, 500);
          if (window.parent && window.parent !== window) {{
            window.parent.postMessage(data, "*");
          }}
        }})();
        </script>
        """,
        height=0,
    )


def notify_file_selected(filename: str):
    send_to_parent(
        "SALAMUM_FILE_SELECTED",
        {
            "filename": filename,
        },
    )


# ============ CSS ============
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

:root{
  --ink:#231812;
  --line:#F0E8DD;
  --muted:#7a6a5e;
}

html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, section.main, [class*="css"], button, input{
  font-family:'Poppins', sans-serif !important;
}

.stApp{
  background:transparent !important;
  color:var(--ink);
}

/* Streamlit branding, footer aur viewer/built-with badges hide */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton,
[data-testid="stViewerBadge"],
[class*="viewerBadge"],
[class*="stActionButton"],
.stApp > footer,
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"]{
  display:none !important;
  visibility:hidden !important;
  opacity:0 !important;
  pointer-events:none !important;
  height:0 !important;
  min-height:0 !important;
  max-height:0 !important;
  overflow:hidden !important;
}

.block-container{
  max-width:100% !important;
  padding:0 !important;
  margin:0 !important;
}

[data-testid="stVerticalBlock"],
[data-testid="stElementContainer"],
[data-testid="stFileUploader"]{
  margin:0 !important;
  padding:0 !important;
  width:100% !important;
}
[data-testid="stFileUploader"] > label{ display:none !important; }

[data-testid="stFileUploaderDropzone"]{
  background:transparent !important;
  border:none !important;
  padding:20px 14px !important;
  min-height:240px !important;
  width:100% !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  gap:12px !important;
  text-align:center !important;
  box-sizing:border-box !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{
  width:100% !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  text-align:center !important;
  gap:8px !important;
  margin:0 auto !important;
}

[data-testid="stFileUploaderDropzoneInstructions"]::before{
  content:"";
  display:block;
  width:52px;
  height:52px;
  margin:0 auto;
  background-color:var(--ink);
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/><line x1='16' y1='13' x2='8' y2='13'/><line x1='16' y1='17' x2='8' y2='17'/></svg>");
  background-repeat:no-repeat;
  background-position:center;
  border-radius:14px;
}

[data-testid="stFileUploaderDropzoneInstructions"]::after{
  content:"Drop your FAB PDF here\\A or click to select from your device";
  display:block;
  width:100%;
  text-align:center;
  white-space:pre-line;
  font-size:13px;
  color:#8a7a6e;
  line-height:1.55;
  font-weight:400;
}

[data-testid="stFileUploaderDropzone"] button{
  background:var(--ink) !important;
  color:#fff !important;
  border:none !important;
  border-radius:100px !important;
  padding:0 !important;
  width:100%;
  max-width:240px;
  height:42px;
  margin:0 auto !important;
  display:flex !important;
  align-items:center !important;
  justify-content:center !important;
  font-size:0 !important;
  position:relative;
  transition:.25s;
}
[data-testid="stFileUploaderDropzone"] button *{ display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after{
  content:"Select PDF";
  font-size:13.5px;
  font-weight:600;
  color:#fff;
  letter-spacing:.2px;
  text-align:center;
}
[data-testid="stFileUploaderDropzone"] button:hover{
  background:#3a2a20 !important;
}

/* File select hone ke baad andar ke Streamlit default file list / spinner ko chhupa kar kaam HTML card par */
[data-testid="stFileUploaderFile"],
[data-testid="stSpinner"]{
  display:none !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

IS_PRO = False

# ============ UPLOAD ============
uploaded_pdf = st.file_uploader(
    "Choose a FAB PDF file",
    type=["pdf"],
    label_visibility="collapsed",
)

# ============ PROCESS & SEND JSON ============
if uploaded_pdf is not None:
    notify_file_selected(uploaded_pdf.name)

    file_id = str(uuid.uuid4())[:8]
    temp_pdf = os.path.join("temp_files", f"{file_id}_{uploaded_pdf.name}")
    out_xlsx = os.path.join("temp_files", f"FAB_Clean_{file_id}.xlsx")

    with open(temp_pdf, "wb") as f:
        f.write(uploaded_pdf.getbuffer())

    try:
        result = process_fab_pdf(temp_pdf, out_xlsx, is_pro=IS_PRO)
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)

    if result.get("status") == "error":
        if os.path.exists(out_xlsx):
            os.remove(out_xlsx)

        send_to_parent(
            "SALAMUM_RESULT",
            {
                "status": "error",
                "message": str(result.get("message", "Could not process PDF.")),
                "is_pro": IS_PRO,
                "locked_pages": 0,
            },
        )
    else:
        excel_b64 = ""
        if os.path.exists(out_xlsx):
            with open(out_xlsx, "rb") as f_excel:
                excel_b64 = base64.b64encode(f_excel.read()).decode("utf-8")
            os.remove(out_xlsx)

        meta = result.get("metadata") or {}
        account_no = str(meta.get("Account Number", "N/A"))
        currency = str(meta.get("Currency", "AED"))
        processed_pages = int(result.get("processed_pages", 0))
        total_pages = int(result.get("total_pages", 0))
        tx_count = int(result.get("tx_count", 0))
        total_credit = float(result.get("total_credit", 0.0))
        total_debit = float(result.get("total_debit", 0.0))
        locked_pages = int(result.get("locked_pages", 0))

        send_to_parent(
            "SALAMUM_RESULT",
            {
                "status": "ok",
                "filename": f"FAB_Audit_{account_no}.xlsx",
                "excel_base64": excel_b64,
                "account_no": account_no,
                "currency": currency,
                "processed_pages": processed_pages,
                "total_pages": total_pages,
                "tx_count": tx_count,
                "total_credit": total_credit,
                "total_debit": total_debit,
                "locked_pages": locked_pages,
                "is_pro": IS_PRO,
                "show_pro_button": (not IS_PRO) or (locked_pages > 0),
            },
        )
