
import streamlit as st

st.set_page_config(
    page_title="Salamum | FAB Statement to Excel",
    page_icon="📊",
    layout="centered",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

:root{
  --ink:#231812;
  --gold:#C9A86A;
}

html, body, [class*="css"], .stApp, button, input{
  font-family:'Poppins', sans-serif !important;
}
.stApp{ background:linear-gradient(180deg,#FFFEFB 0%,#FBF6EF 100%); color:var(--ink); }

/* Streamlit branding hide */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton{ display:none !important; visibility:hidden; }

.block-container{ max-width:980px !important; padding:2rem 1.2rem !important; }

/* ---------- UPLOADER ---------- */
[data-testid="stFileUploader"]{ margin-top:4px; }
[data-testid="stFileUploader"] > label{ display:none !important; }

[data-testid="stFileUploaderDropzone"]{
  background:rgba(255,255,255,.85) !important;
  border:2px dashed #E8D5B5 !important;
  border-radius:24px !important;
  padding:34px 18px !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  gap:14px !important;
  text-align:center !important;
  box-shadow:0 24px 50px rgba(35,24,18,.08);
  transition:.25s;
}
[data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--gold) !important; background:#FFF9EF !important; }

/* Default icon aur text completely hide */
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

/* Custom sharp SVG icon bilkul center */
[data-testid="stFileUploaderDropzoneInstructions"]::before{
  content:"";
  display:block;
  width:64px;
  height:64px;
  margin:0 auto;
  background-color:var(--ink);
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/><line x1='16' y1='13' x2='8' y2='13'/><line x1='16' y1='17' x2='8' y2='17'/></svg>");
  background-repeat:no-repeat;
  background-position:center;
  border-radius:18px;
}

/* Text bilkul center */
[data-testid="stFileUploaderDropzoneInstructions"]::after{
  content:"Drop your FAB PDF here\\A or click to select from your device";
  display:block;
  width:100%;
  text-align:center;
  white-space:pre-line;
  font-size:13.5px;
  color:#8a7a6e;
  line-height:1.7;
  font-weight:400;
}

/* Browse button -> "Select PDF" bilkul center */
[data-testid="stFileUploaderDropzone"] button{
  background:var(--ink) !important;
  color:#fff !important;
  border:none !important;
  border-radius:100px !important;
  padding:0 !important;
  width:100%;
  max-width:260px;
  height:46px;
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
  font-size:14px;
  font-weight:600;
  color:#fff;
  letter-spacing:.2px;
  text-align:center;
}
[data-testid="stFileUploaderDropzone"] button:hover{ background:#3a2a20 !important; transform:translateY(-1px); }

/* Uploaded file chip */
[data-testid="stFileUploaderFile"]{
  background:#F5EEE6 !important; border-radius:14px !important; padding:6px 10px !important; margin-top:10px;
}
[data-testid="stFileUploaderFileName"]{ font-weight:500 !important; color:var(--ink) !important; }

/* Mobile */
@media(max-width:560px){
  .block-container{ padding:1rem .8rem !important; }
  [data-testid="stFileUploaderDropzone"]{ padding:26px 14px !important; border-radius:20px !important; }
  [data-testid="stFileUploaderDropzoneInstructions"]::before{ width:56px; height:56px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

uploaded_pdf = st.file_uploader(
    "Choose a FAB PDF file",
    type=["pdf"],
    label_visibility="collapsed",
)
