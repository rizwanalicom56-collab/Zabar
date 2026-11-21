# app.py - Zabar V3 - Premium - Bank Engine System
# Bank Dropdown -> Manager -> FAB Engine

import streamlit as st
import os, tempfile, uuid
from parser import process_statement

st.set_page_config(
    page_title="Zabar - FAB to Excel",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- ZABAR PREMIUM CSS - STREAMLIT KA LAL BAND ----------
st.markdown("""
<style>
  /* Streamlit ka sab kuch band - Menu, Footer, Toolbar, Red */
  #MainMenu {visibility: hidden !important; display: none !important;}
  footer {visibility: hidden !important; display: none !important;}
  header {visibility: hidden !important; display: none !important;}
  [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
  [data-testid="stDecoration"] {display: none !important;}
  [data-testid="stStatusWidget"] {display: none !important;}
  .stAppDeployButton {display: none !important;}
  [data-testid="stAppViewContainer"] > div:first-child {padding-top: 0 !important;}

  /* App background */
  .stApp {background: #FFFEFB !important;}
  .block-container {padding-top: 14px !important; padding-bottom: 10px !important; max-width: 640px !important;}

  /* Sab red / blue ko khatam karo - Zabar colors hi chalenge */
  :root {--primary-color: #C9A86A !important;}

  /* Logo */
  .zabar-logo {text-align: center; font-size: 36px; font-weight: 800; color: #231812; line-height: 1; letter-spacing: -0.5px;}
  .zabar-logo span {color: #C9A86A;}
  .zabar-tag {text-align: center; font-size: 11px; letter-spacing: 2.5px; text-transform: uppercase; color: #C9A86A; font-weight: 700; margin-top: 5px; margin-bottom: 18px;}

  /* Card */
  .zabar-card {background: #fff; border: 1px solid #F0E8DD; border-radius: 22px; padding: 22px 20px; box-shadow: 0 12px 32px rgba(35,24,18,0.07);}
  .zabar-title {font-size: 21px; font-weight: 700; color: #231812; text-align: center; line-height: 1.3;}
  .zabar-sub {font-size: 13px; color: #7a6a5e; text-align: center; margin-top: 6px; margin-bottom: 16px;}
  .zabar-label {font-size: 12px; font-weight: 700; color: #231812; letter-spacing: 0.5px; text-transform: uppercase; margin: 14px 0 6px;}

  /* Selectbox - Bank Dropdown - Premium */
  [data-testid="stSelectbox"] > div > div {
    background: #FBF6EF !important; border: 1.5px solid #E8D5B5 !important;
    border-radius: 14px !important; color: #231812 !important;
  }
  [data-testid="stSelectbox"] label {color: #231812 !important; font-weight: 700 !important;}

  /* File Uploader - Premium */
  [data-testid="stFileUploader"] {background: #FBF6EF !important; border: 1.5px dashed #C9A86A !important; border-radius: 16px !important; padding: 8px !important;}
  [data-testid="stFileUploader"] button {
    background: #231812 !important; color: #fff !important; border: none !important;
    border-radius: 100px !important; padding: 8px 20px !important; font-weight: 600 !important;
  }
  [data-testid="stFileUploader"] button:hover {background: #231812 !important; color: #fff !important;}

  /* Buttons - Gold, No Red */
  .stButton > button {
    width: 100% !important; background: linear-gradient(135deg,#D4B483,#C9A86A) !important;
    color: #231812 !important; border: none !important; border-radius: 100px !important;
    padding: 15px !important; font-weight: 700 !important; font-size: 15px !important;
    box-shadow: 0 8px 20px rgba(201,168,106,0.35) !important;
  }
  .stButton > button:hover {background: linear-gradient(135deg,#D4B483,#C9A86A) !important; color: #231812 !important; opacity: 0.92 !important;}
  .stButton > button:active {background: linear-gradient(135deg,#D4B483,#C9A86A) !important; color: #231812 !important;}

  /* Download Button - Brown */
  .stDownloadButton > button {
    width: 100% !important; background: #231812 !important; color: #fff !important;
    border: none !important; border-radius: 100px !important; padding: 15px !important; font-weight: 700 !important;
  }
  .stDownloadButton > button:hover {background: #231812 !important; color: #fff !important;}

  /* Plan Buttons - 2 Columns */
  .plan-btn-active > button {background: #FFF6E8 !important; color: #231812 !important; border: 1.5px solid #C9A86A !important; border-radius: 14px !important; padding: 12px !important; font-weight: 700 !important; width: 100% !important;}
  .plan-btn > button {background: #FBF6EF !important; color: #7a6a5e !important; border: 1.5px solid #F0E8DD !important; border-radius: 14px !important; padding: 12px !important; font-weight: 600 !important; width: 100% !important;}

  /* Success / Error / Info - Premium, No Red */
  [data-testid="stAlert"] {border-radius: 14px !important; border: 1px solid #F0E8DD !important;}
  .stSuccess {background: #EDF7ED !important;}
  .stError {background: #FFF6E8 !important; border-color: #E8D5B5 !important; color: #231812 !important;}
  .stInfo {background: #FBF6EF !important;}
  .stWarning {background: #FFF6E8 !important;}

  /* Metric */
  [data-testid="stMetric"] {background: #FBF6EF; border: 1px solid #F0E8DD; border-radius: 14px; padding: 10px;}
  [data-testid="stMetricLabel"] {color: #7a6a5e !important;}
  [data-testid="stMetricValue"] {color: #231812 !important;}

  /* Spinner - Gold */
  .stSpinner > div > div {border-top-color: #C9A86A !important;}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "plan" not in st.session_state:
    st.session_state.plan = "Free"

# ---------- LOGO ----------
st.markdown('<div class="zabar-logo">Za<span>bar</span></div>', unsafe_allow_html=True)
st.markdown('<div class="zabar-tag">Bank Statement • To • Excel</div>', unsafe_allow_html=True)

st.markdown('<div class="zabar-card">', unsafe_allow_html=True)
st.markdown('<div class="zabar-title">Convert Your Bank Statement</div>', unsafe_allow_html=True)
st.markdown('<div class="zabar-sub">Upload PDF • Select Bank • Get Excel in 30 Seconds</div>', unsafe_allow_html=True)

# ---------- 1. BANK DROPDOWN - ENGINE SELECT ----------
st.markdown('<div class="zabar-label">1. Select Your Bank</div>', unsafe_allow_html=True)
bank_name = st.selectbox(
    "Bank",
    ["FAB - First Abu Dhabi Bank", "ADCB - Abu Dhabi Commercial Bank (Coming Soon)", "【entity-Emirates NBD¦canonical_name=Emirates NBD】 (Coming Soon)"],
    label_visibility="collapsed"
)
# Manager ko sirf code chahiye: FAB / ADCB / NBD
bank_code = bank_name.split(" - ")[0].strip()
if "Coming Soon" in bank_name:
    st.info("⚠️ This bank is coming soon. Right now only FAB works.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------- 2. PLAN - BUTTONS, RADIO NAHI (Red se bachne ke liye) ----------
st.markdown('<div class="zabar-label">2. Select Plan</div>', unsafe_allow_html=True)
col_free, col_pro = st.columns(2)
with col_free:
    # Active wale ko alag class
    st.markdown('<div class="plan-btn-active">' if st.session_state.plan == "Free" else '<div class="plan-btn">', unsafe_allow_html=True)
    if st.button("Free - 3 Pages", key="btn_free"):
        st.session_state.plan = "Free"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col_pro:
    st.markdown('<div class="plan-btn-active">' if st.session_state.plan == "Pro" else '<div class="plan-btn">', unsafe_allow_html=True)
    if st.button("Pro - Full", key="btn_pro"):
        st.session_state.plan = "Pro"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

is_pro = (st.session_state.plan == "Pro")

# ---------- 3. UPLOAD ----------
st.markdown('<div class="zabar-label">3. Upload PDF</div>', unsafe_allow_html=True)
uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

if uploaded is not None:
    st.success(f"✅ {uploaded.name} • {(len(uploaded.getvalue())/1024):.1f} KB")

    if st.button("Convert Now →"):
        with st.spinner("Reading your statement... Please wait..."):
            try:
                token = str(uuid.uuid4())[:8]
                tmpdir = tempfile.gettempdir()
                pdf_path = os.path.join(tmpdir, f"zabar_in_{token}.pdf")
                excel_path = os.path.join(tmpdir, f"zabar_out_{token}.xlsx")
                with open(pdf_path, "wb") as f:
                    f.write(uploaded.getvalue())

                # MANAGER ko bank ka naam bhejo - wo us bank ka engine chalayega
                result = process_statement(pdf_path, excel_path, bank_code=bank_code, is_pro=is_pro)

                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

                if "error" in result:
                    err = result["error"]
                    if "password" in err.lower():
                        st.error("🔒 Password Protected - Please remove password and upload again.")
                    elif "scanned" in err.lower():
                        st.error("📄 Scanned PDF - Only digital PDF works, the one you download from bank.")
                    else:
                        st.error(err)
                    st.stop()

                meta = result.get("metadata", {})
                st.success("✅ Converted Successfully!")
                c1, c2, c3 = st.columns(3)
                c1.metric("Transactions", result.get("tx_count", 0))
                c2.metric("Credit", f"{result.get('total_credit',0):,.0f}")
                c3.metric("Debit", f"{result.get('total_debit',0):,.0f}")
                st.caption(f"Bank: {bank_code} • Account: {meta.get('Account Number','—')} • Pages: {result.get('processed_pages',0)}/{result.get('total_pages',0)}")

                locked = result.get("locked_pages", 0)
                if not is_pro and locked > 0:
                    st.warning(f"🔒 {locked} Pages Locked - Unlock full statement with Pro.")

                if os.path.exists(excel_path):
                    with open(excel_path, "rb") as f:
                        excel_bytes = f.read()
                    st.download_button("⬇ Download Excel", data=excel_bytes, file_name=f"Zabar_{bank_code}_Statement_Converted.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    if os.path.exists(excel_path):
                        os.remove(excel_path)
                    st.caption("File deleted from server. Nothing stored.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("👆 Upload your PDF to start. Free = First 3 Pages, Pro = Full Statement.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:11px; color:#9a8a7c; margin-top:12px;">© 2026 Zabar • Made for Bank Users in UAE</p>', unsafe_allow_html=True)
