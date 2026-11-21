# app.py - Zabar - Streamlit App
# Ye iframe me chalegi - Frontend ke Converting Page ke andar

import streamlit as st
import os
import tempfile
import uuid

from parser import process_fab_pdf

# ---------- PAGE SETUP - Embed ke liye menu chhupao ----------
st.set_page_config(
    page_title="Zabar - FAB Statement to Excel",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- ZABAR COLORS - Brown + Gold ----------
st.markdown("""
<style>
  /* Streamlit ka uper wala menu / footer chhupao - iframe me saaf lage */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  .block-container {padding-top: 10px !important; padding-bottom: 10px !important; max-width: 700px;}

  /* Background white */
  .stApp {background: #FFFFFF;}

  /* Heading */
  .zabar-title {font-family: 'Poppins', sans-serif; font-size: 28px; font-weight: 700; color: #231812; text-align: center; margin-bottom: 4px;}
  .zabar-sub {font-size: 14px; color: #7a6a5e; text-align: center; margin-bottom: 20px;}

  /* Upload box */
  .stFileUploader {background: #FBF6EF; border: 1.5px dashed #C9A86A; border-radius: 16px; padding: 16px;}

  /* Button - Gold */
  .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #D4B483, #C9A86A) !important;
    color: #231812 !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 14px 20px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
  }
  .stButton > button:hover {opacity: 0.9;}

  /* Download button */
  .stDownloadButton > button {
    width: 100%;
    background: #231812 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 14px 20px !important;
    font-weight: 700 !important;
  }

  /* Info boxes */
  .zabar-card {background: #FFFEFB; border: 1px solid #F0E8DD; border-radius: 16px; padding: 16px; margin-top: 12px;}
  .zabar-lock {background: #FFF6E8; border: 1px solid #E8D5B5; border-radius: 16px; padding: 16px; margin-top: 12px; text-align: center;}
  .zabar-error {background: #FDE8E8; border: 1px solid #F5C6C6; border-radius: 16px; padding: 16px; margin-top: 12px; text-align: center; color: #9B1C1C;}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE - Iframe ke andar ----------
st.markdown('<div class="zabar-title">Convert Your FAB Statement</div>', unsafe_allow_html=True)
st.markdown('<div class="zabar-sub">Upload PDF • Get Excel in 30 Seconds • File never stored</div>', unsafe_allow_html=True)

# ---------- FREE / PRO SELECT ----------
plan = st.radio(
    "Choose Plan:",
    ["Free - First 3 Pages", "Pro - Full Statement"],
    horizontal=True,
    label_visibility="collapsed"
)
is_pro = "Pro" in plan

# ---------- UPLOAD ----------
uploaded = st.file_uploader(
    "Upload your FAB Bank PDF",
    type=["pdf"],
    help="Only digital FAB PDF. Password & scanned PDF not supported."
)

if uploaded is not None:
    st.success(f"File uploaded: {uploaded.name} • {(len(uploaded.getvalue())/1024):.1f} KB")

    if st.button("Convert Now →"):
        with st.spinner("Reading your statement... Please wait..."):
            try:
                token = str(uuid.uuid4())[:8]
                tmpdir = tempfile.gettempdir()
                pdf_path = os.path.join(tmpdir, f"zabar_in_{token}.pdf")
                excel_path = os.path.join(tmpdir, f"zabar_out_{token}.xlsx")

                # PDF save karo
                with open(pdf_path, "wb") as f:
                    f.write(uploaded.getvalue())

                # Asal parser chalao - YAHAN ASAL KAAM HOTA HAI
                result = process_fab_pdf(pdf_path, excel_path, is_pro=is_pro)

                # Input PDF turant delete - privacy
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

                # ---------- ERROR ----------
                if "error" in result:
                    err = result["error"]
                    if "password" in err.lower():
                        st.markdown(f'<div class="zabar-error"><b>Password Protected PDF</b><br>Please remove password and upload again.<br><br>{err}</div>', unsafe_allow_html=True)
                    elif "scanned" in err.lower():
                        st.markdown(f'<div class="zabar-error"><b>Scanned PDF Not Supported</b><br>Only digital FAB PDF works, the one you download from bank.<br><br>{err}</div>', unsafe_allow_html=True)
                    elif "not a fab" in err.lower() or "not a fab" in err.lower():
                        st.markdown(f'<div class="zabar-error"><b>Not a FAB Statement</b><br>Only FAB Bank statements are supported.<br><br>{err}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="zabar-error"><b>Could not convert</b><br>{err}</div>', unsafe_allow_html=True)
                    st.stop()

                # ---------- SUCCESS ----------
                meta = result.get("metadata", {})
                st.markdown(f"""
                <div class="zabar-card">
                  <b>✅ Converted Successfully</b><br><br>
                  <b>Account:</b> {meta.get("Account Number", "—")}<br>
                  <b>Currency:</b> {meta.get("Currency", "AED")}<br>
                  <b>Period:</b> {meta.get("Period", "—")}<br><br>
                  <b>Total Transactions:</b> {result.get("tx_count", 0)}<br>
                  <b>Total Credit:</b> {result.get("total_credit", 0):,.2f} AED<br>
                  <b>Total Debit:</b> {result.get("total_debit", 0):,.2f} AED<br>
                  <b>Pages:</b> {result.get("processed_pages", 0)} / {result.get("total_pages", 0)} processed
                </div>
                """, unsafe_allow_html=True)

                # ---------- FREE WALA LOCK ----------
                locked = result.get("locked_pages", 0)
                if not is_pro and locked > 0:
                    st.markdown(f"""
                    <div class="zabar-lock">
                      <b>🔒 {locked} Pages Locked</b><br>
                      You converted {result.get("processed_pages", 0)} / {result.get("total_pages", 0)} pages.<br>
                      Unlock full statement with Pro.<br>
                      <b>Go Pro - Unlock Full Statement →</b>
                    </div>
                    """, unsafe_allow_html=True)

                # ---------- DOWNLOAD ----------
                if os.path.exists(excel_path):
                    with open(excel_path, "rb") as f:
                        excel_bytes = f.read()
                    st.download_button(
                        label="⬇ Download Excel",
                        data=excel_bytes,
                        file_name="Zabar_FAB_Statement_Converted.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    # Excel bhi delete - privacy
                    if os.path.exists(excel_path):
                        os.remove(excel_path)
                    st.caption("File deleted from server after download. Nothing stored.")

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

else:
    st.info("👆 Upload your FAB PDF to start. Free = First 3 Pages, Pro = Full Statement.")
