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
  display:flex !important; flex-direction:column !important; align-items:center !important;
  justify-content:center !important; gap:14px !important; text-align:center;
  box-shadow:0 24px 50px rgba(35,24,18,.08);
  transition:.25s;
}
[data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--gold) !important; background:#FFF9EF !important; }

/* Default icon aur text hide */
[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{
  display:flex !important; flex-direction:column; align-items:center; justify-content:center; gap:6px;
}

/* Custom icon aur text */
[data-testid="stFileUploaderDropzoneInstructions"]::before{
  content:"📄"; display:flex; align-items:center; justify-content:center;
  width:64px; height:64px; background:var(--ink); border-radius:18px; font-size:28px;
}
[data-testid="stFileUploaderDropzoneInstructions"]::after{
  content:"Drop your FAB PDF here\\A or click to select from your device";
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

/* Uploaded file chip */
[data-testid="stFileUploaderFile"]{
  background:#F5EEE6 !important; border-radius:14px !important; padding:6px 10px !important; margin-top:10px;
}
[data-testid="stFileUploaderFileName"]{ font-weight:500 !important; color:var(--ink) !important; }

/* Mobile */
@media(max-width:560px){
  .block-container{ padding:1rem .8rem !important; }
  [data-testid="stFileUploaderDropzone"]{ padding:26px 14px !important; border-radius:20px !important; }
  [data-testid="stFileUploaderDropzoneInstructions"]::before{ width:56px; height:56px; font-size:24px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

uploaded_pdf = st.file_uploader(
    "Choose a FAB PDF file",
    type=["pdf"],
    label_visibility="collapsed",
)
