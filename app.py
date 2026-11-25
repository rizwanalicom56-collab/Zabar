import os
import uuid
import html as _html
import streamlit as st
from parser import process_fab_pdf

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Salamum | FAB Statement to Excel",
    page_icon="📊",
    layout="centered",
)

# ============ SETTINGS ============
NETLIFY_HOME_URL = "https://netlify.app"  # <-- Apna Netlify landing page link yahan dalein
os.makedirs("temp_files", exist_ok=True)


def H(s: str) -> str:
    """Markdown code-block bug se bachne ke liye leading spaces hata deta hai."""
    return "\n".join(line.strip() for line in s.strip().splitlines())


# ============ CSS ============
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');

:root{
  --ink:#231812; --gold:#C9A86A; --gold2:#D4B483; --cream:#FFFEFB;
  --sand:#FBF6EF; --line:#F0E8DD; --muted:#7a6a5e;
}

html, body, [class*="css"], .stApp, button, input{
  font-family:'Poppins', sans-serif !important;
}
.stApp{ background:linear-gradient(180deg,#FFFEFB 0%,#FBF6EF 100%); color:var(--ink); }

/* Streamlit branding hide */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton{ display:none !important; visibility:hidden; }

.block-container{ max-width:980px !important; padding:1.1rem 1.2rem 2rem !important; }

/* ---------- TOP BAR ---------- */
.topbar{
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  padding:6px 2px 18px;
}
.brand{ line-height:1; }
.brand-name{ font-family:'Playfair Display',serif !important; font-size:30px; font-weight:700; color:var(--gold); letter-spacing:-.5px; }
.brand-tag{ font-size:9.5px; letter-spacing:3px; text-transform:uppercase; color:#9a8a7c; font-weight:500; margin-top:5px; }
.back-pill{
  text-decoration:none !important; color:var(--ink) !important; font-weight:600; font-size:13px;
  background:#fff; border:1px solid rgba(35,24,18,.12); padding:10px 18px; border-radius:100px;
  white-space:nowrap; transition:.25s;
}
.back-pill:hover{ background:var(--ink); color:#fff !important; }

/* ---------- HERO ---------- */
.hero-badge{
  display:inline-flex; align-items:center; gap:8px; background:#fff; border:1px solid var(--line);
  padding:7px 14px; border-radius:100px; font-size:12.5px; font-weight:500; color:#5a4a3e;
}
.badge-dot{ width:7px; height:7px; background:#1FA47A; border-radius:50%; box-shadow:0 0 0 4px rgba(31,164,122,.15); }
.hero-title{
  font-family:'Playfair Display',serif !important; font-size:46px; line-height:1.1; letter-spacing:-.5px;
  color:var(--ink); margin:18px 0 12px; font-weight:700;
}
.hero-title span{ color:var(--gold); font-style:italic; }
.hero-sub{ font-size:15.5px; line-height:1.65; color:#6f6157; max-width:560px; margin-bottom:18px; }
.trust-row{ display:flex; flex-wrap:wrap; gap:8px 16px; font-size:13px; color:var(--muted); margin-bottom:22px; }
.trust-row b{ color:#1FA47A; }

/* ---------- UPLOADER (200MB wala box replace) ---------- */
[data-testid="stFileUploader"]{ margin-top:4px; }
[data-testid="stFileUploader"] > label{ display:none !important; }

[data-testid="stFileUploaderDropzone"]{
  background:rgba(255,255,255,.85) !important;
  border:2px dashed #E8D5B5 !important;
  border-radius:24px !important;
  padding:34px 18px !important;
  display:flex !important; flex-direction:column !important; align-items:center !important;
  justify-content:center !important; gap:14px !important; text-align:center;
  box-shadow:0 24px 50px rgba(35,24,18,.08);
  transition:.25s;
}
[data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--gold) !important; background:#FFF9EF !important; }

/* default icon + "Drag and drop" + "Limit 200MB" sab chupao */
[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{
  display:flex !important; flex-direction:column; align-items:center; justify-content:center; gap:6px;
}
/* apna design */
[data-testid="stFileUploaderDropzoneInstructions"]::before{
  content:"📄"; display:flex; align-items:center; justify-content:center;
  width:64px; height:64px; background:var(--ink); border-radius:18px; font-size:28px;
}
[data-testid="stFileUploaderDropzoneInstructions"]::after{
  content:"Drop your FAB PDF here\A or click to select from your device";
  white-space:pre-wrap; font-size:13.5px; color:#8a7a6e; line-height:1.7; font-weight:400;
}

/* Browse button -> "Select PDF" */
[data-testid="stFileUploaderDropzone"] button{
  background:var(--ink) !important; color:#fff !important; border:none !important;
  border-radius:100px !important; padding:0 !important; width:100%; max-width:260px; height:46px;
  font-size:0 !important; position:relative; transition:.25s;
}
[data-testid="stFileUploaderDropzone"] button *{ display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after{
  content:"Select PDF"; font-size:14px; font-weight:600; color:#fff; letter-spacing:.2px;
}
[data-testid="stFileUploaderDropzone"] button:hover{ background:#3a2a20 !important; transform:translateY(-1px); }

/* uploaded file chip */
[data-testid="stFileUploaderFile"]{
  background:#F5EEE6 !important; border-radius:14px !important; padding:6px 10px !important; margin-top:10px;
}
[data-testid="stFileUploaderFileName"]{ font-weight:500 !important; color:var(--ink) !important; }

.privacy-note{
  display:flex; justify-content:center; flex-wrap:wrap; gap:6px 12px; margin:14px 0 4px;
  font-size:11.5px; color:#9a8a7c; text-align:center; line-height:1.5;
}
.dot{ width:4px; height:4px; background:var(--gold); border-radius:50%; align-self:center; }

/* ---------- RESULT ---------- */
.result-ok{
  background:#EAF7F0; border:1px solid #C8E9D8; color:#14704F; border-radius:16px;
  padding:14px 18px; font-size:14px; font-weight:500; margin:22px 0 14px; line-height:1.5;
}
.err-box{
  background:#FDECEC; border:1px solid #F5C6C6; color:#B42318; border-radius:16px;
  padding:14px 18px; font-size:14px; font-weight:500; margin:22px 0 14px; line-height:1.5;
}
.stats{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }
.stat{
  background:#fff; border:1px solid var(--line); border-radius:18px; padding:16px 14px;
  box-shadow:0 6px 18px rgba(35,24,18,.04); min-width:0;
}
.stat span{ display:block; font-size:11.5px; color:#8a7a6e; margin-bottom:6px; }
.stat b{ display:block; font-size:16px; color:var(--ink); word-break:break-word; line-height:1.3; }
.stat.credit{ background:#EAF7F0; border-color:#C8E9D8; }
.stat.credit b{ color:#14704F; }
.stat.debit{ background:#FDECEC; border-color:#F5C6C6; }
.stat.debit b{ color:#B42318; }

/* Download button */
[data-testid="stDownloadButton"] button{
  background:linear-gradient(135deg,var(--gold2),var(--gold)) !important;
  color:var(--ink) !important; border:none !important; border-radius:100px !important;
  height:54px; font-weight:600 !important; font-size:15px !important;
  box-shadow:0 10px 24px rgba(201,168,106,.35); transition:.25s;
}
[data-testid="stDownloadButton"] button:hover{ transform:translateY(-2px); box-shadow:0 14px 28px rgba(201,168,106,.45); }
[data-testid="stDownloadButton"] button p{ font-weight:600 !important; font-size:15px !important; }

/* Locked pages */
.locked{
  background:var(--ink); color:#fff; border-radius:22px; padding:24px 22px; margin-top:18px;
  display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
  box-shadow:0 20px 40px rgba(35,24,18,.22);
}
.locked h4{ font-size:16px; color:var(--gold); margin-bottom:4px; font-weight:600; }
.locked p{ font-size:13.5px; color:#CBB8A3; line-height:1.55; margin:0; }
.locked .price{
  background:linear-gradient(135deg,var(--gold2),var(--gold)); color:var(--ink); font-weight:700;
  font-size:13px; padding:11px 20px; border-radius:100px; white-space:nowrap;
}

/* Footer */
.foot{ text-align:center; margin-top:34px; padding-top:18px; border-top:1px solid var(--line); font-size:12px; color:#9a8a7c; line-height:1.7; }
.foot b{ font-family:'Playfair Display',serif !important; font-size:18px; color:var(--gold); }

/* Spinner / alerts */
[data-testid="stSpinner"] p{ color:var(--muted) !important; font-size:13.5px; }

/* ---------- TABLET ---------- */
@media(max-width:820px){
  .hero-title{ font-size:38px; }
  .stats{ grid-template-columns:repeat(2,1fr); }
}

/* ---------- MOBILE ---------- */
@media(max-width:560px){
  .block-container{ padding:.8rem .8rem 1.6rem !important; }
  .brand-name{ font-size:24px; }
  .brand-tag{ font-size:8px; letter-spacing:2.2px; }
  .back-pill{ padding:9px 14px; font-size:12px; }
  .hero-title{ font-size:30px; line-height:1.2; margin:14px 0 10px; }
  .hero-sub{ font-size:14px; }
  .trust-row{ font-size:12px; gap:6px 12px; }
  [data-testid="stFileUploaderDropzone"]{ padding:26px 14px !important; border-radius:20px !important; }
  [data-testid="stFileUploaderDropzoneInstructions"]::before{ width:56px; height:56px; font-size:24px; }
  .stats{ gap:10px; }
  .stat{ padding:14px 12px; }
  .stat b{ font-size:14px; }
  .locked{ flex-direction:column; text-align:center; padding:22px 16px; }
  .locked .price{ width:100%; text-align:center; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============ HEADER ============
st.markdown(H(f"""
<div class="topbar">
  <div class="brand">
    <div class="brand-name">Salamum</div>
    <div class="brand-tag">FAB • Statement • Excel</div>
  </div>
  <a href="{NETLIFY_HOME_URL}" class="back-pill">← Back to Home</a>
</div>

<div class="hero-badge"><span class="badge-dot"></span>Free Preview • First 3 Pages</div>
<div class="hero-title">Upload Your FAB Statement, Get <span>Excel</span></div>
<div class="hero-sub">Clean, categorized and balance-audited Excel report from your digital FAB PDF. No signup, no manual typing.</div>
<div class="trust-row">
  <span><b>✓</b> 30 Sec Result</span>
  <span><b>✓</b> Debit / Credit Auto</span>
  <span><b>✓</b> File Never Stored</span>
</div>
"""), unsafe_allow_html=True)

# ============ UPLOAD ============
uploaded_pdf = st.file_uploader(
    "Choose a FAB PDF file",
    type=["pdf"],
    label_visibility="collapsed",
)

st.markdown(H("""
<div class="privacy-note">
  <span>Password-protected & scanned PDF not supported</span>
  <span class="dot"></span>
  <span>100% Private</span>
</div>
"""), unsafe_allow_html=True)

# ============ PROCESS ============
if uploaded_pdf is not None:
    file_id = str(uuid.uuid4())[:8]
    temp_pdf = os.path.join("temp_files", f"{file_id}_{uploaded_pdf.name}")
    out_xlsx = os.path.join("temp_files", f"FAB_Clean_{file_id}.xlsx")

    with open(temp_pdf, "wb") as f:
        f.write(uploaded_pdf.getbuffer())

    try:
        with st.spinner("Analyzing FAB statement & running balance audit..."):
            result = process_fab_pdf(temp_pdf, out_xlsx, is_pro=False)
    finally:
        # Privacy: uploaded PDF foran delete
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)

    if result["status"] == "error":
        st.markdown(
            f'<div class="err-box">⚠️ {_html.escape(str(result["message"]))}</div>',
            unsafe_allow_html=True,
        )
    else:
        # Excel ko memory mein le lo, phir server se delete
        with open(out_xlsx, "rb") as f_excel:
            excel_bytes = f_excel.read()
        if os.path.exists(out_xlsx):
            os.remove(out_xlsx)

        meta = result["metadata"]
        acc = _html.escape(str(meta["Account Number"]))
        cur = _html.escape(str(meta["Currency"]))

        st.markdown(H(f"""
        <div class="result-ok">✅ Converted <b>{result['processed_pages']}</b> of <b>{result['total_pages']}</b> pages — <b>{result['tx_count']}</b> transactions found!</div>
        <div class="stats">
          <div class="stat"><span>Account No</span><b>{acc}</b></div>
          <div class="stat"><span>Currency</span><b>{cur}</b></div>
          <div class="stat credit"><span>Total Credits</span><b>+ {result['total_credit']:,.2f}</b></div>
          <div class="stat debit"><span>Total Debits</span><b>- {result['total_debit']:,.2f}</b></div>
        </div>
        """), unsafe_allow_html=True)

        st.download_button(
            label=f"📥 Download Clean Excel ({result['processed_pages']} Pages)",
            data=excel_bytes,
            file_name=f"FAB_Audit_{meta['Account Number']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

        if result["locked_pages"] > 0:
            st.markdown(H(f"""
            <div class="locked">
              <div>
                <h4>🔒 {result['locked_pages']} more pages are locked</h4>
                <p>Free preview mein sirf pehle 3 pages hain. Pro se poora statement unlock karein.</p>
              </div>
              <div class="price">Go Pro — 19 AED</div>
            </div>
            """), unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown(H("""
<div class="foot">
  <b>Salamum</b><br>
  Private by design. Your file is never stored.<br>
  Made for FAB Bank users in UAE • © 2026 Salamum
</div>
"""), unsafe_allow_html=True)
