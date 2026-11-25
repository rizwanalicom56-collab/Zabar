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

html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, section.main, [class*="css"], button, input{
  font-family:'Poppins', sans-serif !important;
  overflow:hidden !important;
}

.stApp{
  background:#FFFEFB !important;
  color:var(--ink);
}

#MainMenu, footer, header,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton,
[data-testid="stViewerBadge"], [class*="viewerBadge"],
.stApp > footer, [data-testid="stBottom"]{
  display:none !important;
  visibility:hidden !important;
  height:0 !important;
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
  background:#FFFEFB !important;
  border:2px dashed #E8D5B5 !important;
  border-radius:20px !important;
  padding:18px 14px !important;
  height:242px !important;
  width:100% !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  gap:10px !important;
  text-align:center !important;
  box-sizing:border-box !important;
  transition:.25s;
}
[data-testid="stFileUploaderDropzone"]:hover{
  border-color:var(--gold) !important;
  background:#FFF9EF !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{
  width:100% !important;
  display:flex !important;
  flex-direction:column !important;
  align-items:center !important;
  justify-content:center !important;
  text-align:center !important;
  gap:6px !important;
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
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

uploaded_pdf = st.file_uploader(
    "Choose a FAB PDF file",
    type=["pdf"],
    label_visibility="collapsed",
)
