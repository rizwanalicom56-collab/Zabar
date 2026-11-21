# app.py - Zabar V2 - Premium - Streamlit App

import streamlit as st
import os, tempfile, uuid
from parser import process_fab_pdf

st.set_page_config(
    page_title="Zabar - FAB to Excel",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- ZABAR PREMIUM CSS - Tati Fix ----------
st.markdown("""
<style>
  /* Streamlit ka sab kuch chhupao */
  #MainMenu {visibility: hidden !important;}
  footer {visibility: hidden !important;}
  header {visibility: hidden !important;}
  [data-testid="stToolbar"] {visibility: hidden !important;}
  [data-testid="stDecoration"] {display: none !important;}
  [data-testid="stStatusWidget"] {display: none !important;}
  .stAppDeployButton {display: none !important;}

  .block-container {padding-top: 12px !important; padding-bottom: 10px !important; max-width: 620px !important;}
  .stApp {background: #FFFEFB !important;}

  /* Zabar Logo */
  .zabar-logo {text-align: center; font-family: 'Poppins', sans-serif; font-size: 34px; font-weight: 800; color: #231812; letter-spacing: -0.5px; line-height: 1;}
  .zabar-logo span {color: #C9A86A;}
  .zabar-tag {text-align: center; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #C9A86A; font-weight: 700; margin-top: 4px; margin-bottom: 18px;}

  .zabar-card {background: #fff; border: 1px solid #F0E8DD; border-radius: 22px; padding: 22px 20px; box-shadow: 0 10px 30px rgba(35,24,18,0.06);}
  .zabar-title {font-size: 21px; font-weight: 700; color: #231812; text-align: center; line-height: 1.3;}
  .zabar-sub {font-size: 13px; color: #7a6a5e; text-align: center; margin-top: 6px; margin-bottom: 18px;}

  /* Radio - Free / Pro ko 2 card banao */
  div[data-testid="stRadio"] > div {display: flex; gap: 10px;}
  div[data-testid="stRadio"] label {
    flex: 1; background: #FBF6EF !important; border: 1.5px solid #F0E8DD !important;
    border-radius: 14px !important; padding: 12px 10px !important; text-align: center !important;
    font-size: 13px !important; font-weight: 600 !important; color: #231812 !important;
  }
  div[data-testid="stRadio"] label:has(input:checked) {
    border-color: #C9A86A !important; background: #FFF6E8 !important;
  }

  /* File Uploader */
  [data-testid="stFileUploader"] {background: #FBF6EF; border: 1.5px dashed #C9A86A; border-radius: 16px; padding: 10px;}
  [data-testid="stFileUploader"] button {border-radius: 100px !important; background: #231812 !important; color: #fff !important; border: none !important;}

  /* Main Button */
  .stButton > button {
    width: 100% !important; background: linear-gradient(135deg,#D4B483,#C9A86A) !important;
    color: #231812 !important; border: none !important; border-radius: 100px !important;
    padding: 15px !important; font-weight: 700 !important; font-size: 15px !important;
    box-shadow: 0 8px 20px rgba(201,168,106,0.35) !important;
  }
  /* Download Button */
  .stDownloadButton > button {
    width: 100% !important; background: #231812 !important; color: #fff !important;
    border-radius: 100px !important; padding: 15px !important; font-weight: 700 !important; border: none !important;
  }
  .stAlert {border-radius: 14px !important;}
</style>
""", unsafe_allow_html=True)

# ---------- LOGO + CARD ----------
st.markdown('<div class="zabar-logo">Za<span>bar</span></div>', unsafe_allow_html=True)
st.markdown('<div class="zabar-tag">FAB Statement • To • Excel</div>', unsafe_allow_html=True)

st.markdown('<div class="zabar-card">', unsafe_allow_html=True)
st.markdown('<div class="zabar-title">Convert Your FAB Statement</div>', unsafe_allow_html=True)
st.markdown('<div class="zabar-sub">Upload PDF • Get Excel in 30 Seconds • File never stored</div>', unsafe_allow_html=True)

plan = st.radio("Plan", ["Free - 3 Pages", "Pro - Full"], horizontal=True, label_visibility="collapsed")
is_pro = "Pro" in plan

uploaded = st.file_uploader("Upload your FAB Bank PDF", type=["pdf"])

if uploaded is not None:
    st.success(f"✅ {uploaded.name}")

    if st.button("Convert Now →"):
        with st.spinner("Reading your statement..."):
            try:
                token = str(uuid.uuid4())[:8]
                tmpdir = tempfile.gettempdir()
                pdf_path = os.path.join(tmpdir, f"zabar_in_{token}.pdf")
                excel_path = os.path.join(tmpdir, f"zabar_out_{token}.xlsx")
                with open(pdf_path, "wb") as f:
                    f.write(uploaded.getvalue())
                result = process_fab_pdf(pdf_path, excel_path, is_pro=is_pro)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

                if "error" in result:
                    err = result["error"]
                    if "password" in err.lower():
                        st.error("🔒 Password Protected PDF - Please remove password and upload again.")
                    elif "scanned" in err.lower():
                        st.error("📄 Scanned PDF Not Supported - Only digital FAB PDF works.")
                    elif "not a fab" in err.lower():
                        st.error("🏦 Not a FAB Statement - Only FAB Bank supported.")
                    else:
                        st.error(err)
                    st.stop()

                meta = result.get("metadata", {})
                st.success("✅ Converted Successfully!")
                c1, c2, c3 = st.columns(3)
                c1.metric("Transactions", result.get("tx_count", 0))
                c2.metric("Total Credit", f"{result.get('total_credit',0):,.0f}")
                c3.metric("Total Debit", f"{result.get('total_debit',0):,.0f}")
                st.caption(f"Account: {meta.get('Account Number','—')} • Currency: {meta.get('Currency','AED')} • Pages: {result.get('processed_pages',0)}/{result.get('total_pages',0)}")

                locked = result.get("locked_pages", 0)
                if not is_pro and locked > 0:
                    st.warning(f"🔒 {locked} Pages Locked - Unlock full statement with Pro.")

                if os.path.exists(excel_path):
                    with open(excel_path, "rb") as f:
                        excel_bytes = f.read()
                    st.download_button("⬇ Download Excel", data=excel_bytes, file_name="Zabar_FAB_Statement_Converted.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    if os.path.exists(excel_path):
                        os.remove(excel_path)
                    st.caption("File deleted from server. Nothing stored.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("👆 Upload your FAB PDF to start. Free = First 3 Pages, Pro = Full Statement.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:11px; color:#9a8a7c; margin-top:12px;">© 2026 Zabar • Made for FAB Bank Users in UAE</p>', unsafe_allow_html=True)
