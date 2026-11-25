# app.py - Salamum FINAL - Sirf Upload + HTML ko Data Bhejo
import os, uuid, base64, json, html as _html
import streamlit as st
import streamlit.components.v1 as components
from parser import process_fab_pdf

st.set_page_config(page_title="Salamum", page_icon="📊", layout="centered")
os.makedirs("temp_files", exist_ok=True)

def send_to_html(msg_type, data=None):
    # HTML ko message bhejo - window.top pe
    js_data = json.dumps(data) if data is not None else "null"
    components.html(f"""
    <script>
    (function(){{
      var msg = {{type: "{msg_type}", data: {js_data}}};
      try{{ window.top.postMessage(msg, "*"); }}catch(e){{}}
      try{{ window.parent.postMessage(msg, "*"); }}catch(e){{}}
    }})();
    </script>
    """, height=0)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, section.main, button, input{ font-family:'Poppins', sans-serif !important; }
.stApp{ background:#fff !important; }
/* BUILT WITH STREAMLIT - PAKKA GAYAB */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stViewerBadge"], [class*="viewerBadge"], [class*="stActionButton"], [data-testid="stAppDeployButton"], [data-testid="stBottom"], [data-testid="stBottomBlockContainer"], .stApp > footer, iframe[title="streamlit_app"]{ display:none !important; visibility:hidden !important; height:0 !important; overflow:hidden !important; }
.block-container{ max-width:100% !important; padding:0 !important; margin:0 !important; }
[data-testid="stVerticalBlock"], [data-testid="stElementContainer"]{ margin:0 !important; padding:0 !important; width:100% !important; }
[data-testid="stFileUploader"] > label{ display:none !important; }
[data-testid="stFileUploaderDropzone"]{ background:#FFFEFB !important; border:2px dashed #E8D5B5 !important; border-radius:16px !important; padding:20px 12px !important; min-height:280px !important; width:100% !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; gap:10px !important; text-align:center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{ width:100% !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; gap:6px !important; }
[data-testid="stFileUploaderDropzoneInstructions"]::before{ content:""; display:block; width:56px; height:56px; margin:0 auto; background-color:#231812; background-image:url("data:image/svg+xml;utf8,[STRIPPED]"); background-repeat:no-repeat; background-position:center; border-radius:14px; }
[data-testid="stFileUploaderDropzoneInstructions"]::after{ content:"Drop your FAB PDF here\\A or click to select from your device"; display:block; width:100%; text-align:center; white-space:pre-line; font-size:13px; color:#8a7a6e; line-height:1.55; }
[data-testid="stFileUploaderDropzone"] button{ background:#231812 !important; color:#fff !important; border:none !important; border-radius:100px !important; width:100%; max-width:240px; height:42px; margin:0 auto !important; display:flex !important; align-items:center !important; justify-content:center !important; font-size:0 !important; }
[data-testid="stFileUploaderDropzone"] button *{ display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after{ content:"Select PDF"; font-size:13.5px; font-weight:600; color:#fff; }
[data-testid="stFileUploaderFile"]{ display:none !important; }
[data-testid="stSpinner"] p{ color:#7a6a5e !important; font-size:13px; text-align:center; }
</style>
<script>
// Built with Streamlit badge ko JS se bhi ura do
(function(){ setInterval(function(){ document.querySelectorAll('[data-testid="stViewerBadge"], [class*="viewerBadge"]').forEach(function(el){ el.style.display='none'; }); }, 500); })();
</script>
"""
st.markdown(CSS, unsafe_allow_html=True)

uploaded_pdf = st.file_uploader("Choose FAB PDF", type=["pdf"], label_visibility="collapsed", key="salamum_uploader")

if uploaded_pdf is None:
    send_to_html("SALAMUM_SHOW_UPLOAD")
else:
    # STEP 1 - HTML ko bolo Upload gayab karke Animation dikhao
    send_to_html("SALAMUM_UPLOADING", {"filename": uploaded_pdf.name})
    file_id = str(uuid.uuid4())[:8]
    temp_pdf = os.path.join("temp_files", f"{file_id}_{uploaded_pdf.name}")
    out_xlsx = os.path.join("temp_files", f"FAB_Clean_{file_id}.xlsx")
    with open(temp_pdf, "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    try:
        with st.spinner("Analyzing..."):
            result = process_fab_pdf(temp_pdf, out_xlsx, is_pro=False)
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
    if result["status"] == "error":
        send_to_html("SALAMUM_ERROR", {"message": str(result["message"])})
    else:
        with open(out_xlsx, "rb") as f_excel:
            excel_bytes = f_excel.read()
        if os.path.exists(out_xlsx):
            os.remove(out_xlsx)
        meta = result["metadata"]
        # Excel ko base64 me badal ke HTML ko bhejo - taake HTML ka Download btn kaam kare
        b64 = base64.b64encode(excel_bytes).decode()
        payload = {
            "tx_count": result["tx_count"],
            "processed_pages": result["processed_pages"],
            "total_pages": result["total_pages"],
            "account": str(meta["Account Number"]),
            "currency": str(meta["Currency"]),
            "total_credit": result["total_credit"],
            "total_debit": result["total_debit"],
            "locked_pages": result["locked_pages"],
            "excel_b64": b64,
            "filename": f"FAB_Audit_{meta['Account Number']}.xlsx"
        }
        # STEP 2 - HTML ko bolo ab baaki sab dikha do - Text, 4 Boxes, Download, 【entity-GoPro¦canonical_name=GoPro】
        send_to_html("SALAMUM_RESULT", payload)
        st.markdown('<p style="text-align:center; font-size:12px; color:#7a6a5e;">Done! Result is shown above.</p>', unsafe_allow_html=True)
