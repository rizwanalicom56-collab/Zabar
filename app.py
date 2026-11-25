# app.py - Salamum FINAL - Half Card + Hide Upload + 【entity-GoPro¦canonical_name=GoPro】 Message
import os, uuid, html as _html
import streamlit as st
import streamlit.components.v1 as components
from parser import process_fab_pdf

st.set_page_config(page_title="Salamum | FAB Statement to Excel", page_icon="📊", layout="centered")
os.makedirs("temp_files", exist_ok=True)

def H(s: str) -> str:
    return "\n".join(line.strip() for line in s.strip().splitlines())

def send_msg(msg_type, data=None):
    # HTML ko message bhejo - 【entity-GoPro¦canonical_name=GoPro】 card ke liye
    payload = f"""<script>
    (function(){{
      var msg = {{type: "{msg_type}", data: {data if data else "null"}}};
      try{{ window.top.postMessage(msg, "*"); }}catch(e){{}}
      try{{ window.parent.postMessage(msg, "*"); }}catch(e){{}}
    }})();
    </script>"""
    components.html(payload, height=0)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
:root{ --ink:#231812; --gold:#C9A86A; --gold2:#D4B483; --line:#F0E8DD; --muted:#7a6a5e; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, section.main, button, input{ font-family:'Poppins', sans-serif !important; }
.stApp{ background:#fff !important; color:var(--ink); }
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stViewerBadge"], [class*="viewerBadge"], [class*="stActionButton"], .stApp > footer, [data-testid="stBottom"], [data-testid="stBottomBlockContainer"]{ display:none !important; visibility:hidden !important; height:0 !important; overflow:hidden !important; }
.block-container{ max-width:100% !important; padding:12px !important; margin:0 !important; }
[data-testid="stVerticalBlock"], [data-testid="stElementContainer"]{ margin:0 !important; padding:0 !important; width:100% !important; }

/* UPLOAD BOX - Half Card ke andar */
[data-testid="stFileUploader"] > label{ display:none !important; }
[data-testid="stFileUploaderDropzone"]{ background:#FFFEFB !important; border:2px dashed #E8D5B5 !important; border-radius:16px !important; padding:20px 12px !important; min-height:280px !important; width:100% !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; gap:10px !important; text-align:center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{ width:100% !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; gap:6px !important; }
[data-testid="stFileUploaderDropzoneInstructions"]::before{ content:""; display:block; width:56px; height:56px; margin:0 auto; background-color:var(--ink); background-image:url("data:image/svg+xml;utf8,[STRIPPED]"); background-repeat:no-repeat; background-position:center; border-radius:14px; }
[data-testid="stFileUploaderDropzoneInstructions"]::after{ content:"Drop your FAB PDF here\\A or click to select from your device"; display:block; width:100%; text-align:center; white-space:pre-line; font-size:13px; color:#8a7a6e; line-height:1.55; }
[data-testid="stFileUploaderDropzone"] button{ background:var(--ink) !important; color:#fff !important; border:none !important; border-radius:100px !important; width:100%; max-width:240px; height:42px; margin:0 auto !important; display:flex !important; align-items:center !important; justify-content:center !important; font-size:0 !important; }
[data-testid="stFileUploaderDropzone"] button *{ display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after{ content:"Select PDF"; font-size:13.5px; font-weight:600; color:#fff; }
[data-testid="stFileUploaderFile"]{ display:none !important; }

/* RESULT */
.result-ok{ background:#EAF7F0; border:1px solid #C8E9D8; color:#14704F; border-radius:14px; padding:10px 14px; font-size:13px; font-weight:500; margin:0 0 12px; line-height:1.5; text-align:center; }
.err-box{ background:#FDECEC; border:1px solid #F5C6C6; color:#B42318; border-radius:14px; padding:10px 14px; font-size:13px; font-weight:500; margin:0 0 12px; line-height:1.5; text-align:center; }
.stats{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-bottom:12px; }
.stat{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:11px; box-shadow:0 6px 18px rgba(35,24,18,.04); text-align:left; }
.stat span{ display:block; font-size:11px; color:#8a7a6e; margin-bottom:4px; }
.stat b{ display:block; font-size:13.5px; color:var(--ink); word-break:break-word; }
.stat.credit{ background:#EAF7F0; border-color:#C8E9D8; } .stat.credit b{ color:#14704F; }
.stat.debit{ background:#FDECEC; border-color:#F5C6C6; } .stat.debit b{ color:#B42318; }
[data-testid="stDownloadButton"] button{ background:linear-gradient(135deg,var(--gold2),var(--gold)) !important; color:var(--ink) !important; border:none !important; border-radius:100px !important; height:48px; font-weight:600 !important; font-size:14px !important; box-shadow:0 10px 24px rgba(201,168,106,.35); }
[data-testid="stSpinner"] p{ color:var(--muted) !important; font-size:13px; text-align:center; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Agar file upload ho gayi hai to uploader mat dikhao - sirf result dikhao
# Streamlit rerun pe uploaded file session me rehti hai
uploaded_pdf = st.file_uploader("Choose a FAB PDF file", type=["pdf"], label_visibility="collapsed", key="salamum_uploader")

if uploaded_pdf is None:
    # STEP 1 - Sirf Upload Box dikhega - 440px card me fit
    # GoPro card chupao
    send_msg("SALAMUM_HIDE_GOPRO")
    st.markdown('<p style="text-align:center; font-size:11px; color:#8a7a6e; margin-top:10px;">🔒 File deleted after conversion • Nothing stored</p>', unsafe_allow_html=True)

else:
    # STEP 2 - Upload box gayab, ab Animation + Result
    file_id = str(uuid.uuid4())[:8]
    temp_pdf = os.path.join("temp_files", f"{file_id}_{uploaded_pdf.name}")
    out_xlsx = os.path.join("temp_files", f"FAB_Clean_{file_id}.xlsx")
    with open(temp_pdf, "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    try:
        with st.spinner("Uploading... Analyzing FAB statement..."):
            result = process_fab_pdf(temp_pdf, out_xlsx, is_pro=False)
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)

    if result["status"] == "error":
        st.markdown(f'<div class="err-box">⚠️ {_html.escape(str(result["message"]))}</div>', unsafe_allow_html=True)
        send_msg("SALAMUM_HIDE_GOPRO")
    else:
        with open(out_xlsx, "rb") as f_excel:
            excel_bytes = f_excel.read()
        if os.path.exists(out_xlsx):
            os.remove(out_xlsx)
        meta = result["metadata"]
        acc = _html.escape(str(meta["Account Number"]))
        cur = _html.escape(str(meta["Currency"]))
        # STEP 3 - Found text + 2x2 boxes + Download
        st.markdown(H(f"""
        <div class="result-ok">✅ Found <b>{result['tx_count']}</b> transactions in <b>{result['processed_pages']}</b> of <b>{result['total_pages']}</b> pages!</div>
        <div class="stats">
          <div class="stat"><span>Account Name / No</span><b>{acc}</b></div>
          <div class="stat"><span>Currency</span><b>{cur}</b></div>
          <div class="stat credit"><span>Total Credits</span><b>+ {result['total_credit']:,.2f}</b></div>
          <div class="stat debit"><span>Total Debits</span><b>- {result['total_debit']:,.2f}</b></div>
        </div>
        """), unsafe_allow_html=True)
        st.download_button(label=f"📥 Download Clean Excel", data=excel_bytes, file_name=f"FAB_Audit_{meta['Account Number']}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
        # STEP 4 - Free plan hai to HTML ko bolo GoPro card dikhao - ALAG card me
        if result["locked_pages"] > 0:
            send_msg("SALAMUM_SHOW_GOPRO", f'{{"locked": {result["locked_pages"]}}}')
        else:
            send_msg("SALAMUM_HIDE_GOPRO")
