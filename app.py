import os
import uuid
import streamlit as st
from parser import process_fab_pdf

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="UAE Statement Pro | FAB to Excel",
    page_icon="📊",
    layout="centered"
)

# --- CUSTOM CSS (60-30-10 RULE + POPPINS + HIDE STREAMLIT BRANDING) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .top-banner {
        background-color: #3E2723;
        color: #FAF9F6;
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .top-banner h2 {
        color: #FAF9F6 !important;
        margin: 0;
        font-size: 1.35rem;
    }
    .gold-badge {
        background-color: #C87D32;
        color: #FFFFFF;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .back-link {
        text-decoration: none;
        color: #3E2723;
        font-weight: 600;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- STORAGE & SETTINGS ---
os.makedirs("temp_files", exist_ok=True)
NETLIFY_HOME_URL = "https://netlify.app"  # <-- Apna Netlify landing page link yahan dalein

# --- TOP NAVIGATION & HEADER ---
st.markdown(f'<a href="{NETLIFY_HOME_URL}" class="back-link">← Back to Home</a>', unsafe_allow_html=True)
st.write("")

st.markdown("""
    <div class="top-banner">
        <div>
            <h2>UAE Statement Pro</h2>
            <small>First Abu Dhabi Bank (FAB) PDF to Audited Excel</small>
        </div>
        <span class="gold-badge">FREE PREVIEW (3 PAGES)</span>
    </div>
""", unsafe_allow_html=True)

# --- UPLOAD SECTION ---
st.subheader("Upload Your Digital FAB Statement")
st.write("Convert your PDF statement into a clean, categorized, and math-audited Excel report in seconds.")

uploaded_pdf = st.file_uploader("Choose a FAB PDF file", type=["pdf"])

if uploaded_pdf is not None:
    file_id = str(uuid.uuid4())[:8]
    temp_pdf = os.path.join("temp_files", f"{file_id}_{uploaded_pdf.name}")
    out_xlsx = os.path.join("temp_files", f"FAB_Clean_{file_id}.xlsx")

    with open(temp_pdf, "wb") as f:
        f.write(uploaded_pdf.getbuffer())

    with st.spinner("Analyzing FAB statement & running balance audit..."):
        result = process_fab_pdf(temp_pdf, out_xlsx, is_pro=False)

    # Auto-delete uploaded PDF immediately for privacy
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)

    if result["status"] == "error":
        st.error(f"⚠️ {result['message']}")
    else:
        st.success(f"✅ Converted {result['processed_pages']} of {result['total_pages']} pages ({result['tx_count']} transactions found)!")

        # Summary Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Account No", result["metadata"]["Account Number"])
        c2.metric("Currency", result["metadata"]["Currency"])
        c3.metric("Total Credits", f"{result['total_credit']:,.2f}")
        c4.metric("Total Debits", f"{result['total_debit']:,.2f}")

        st.write("")

        # Download Excel Button
        with open(out_xlsx, "rb") as f_excel:
            st.download_button(
                label=f"📥 Download Clean Excel ({result['processed_pages']} Pages)",
                data=f_excel,
                file_name=f"FAB_Audit_{result['metadata']['Account Number']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

        # Locked Pages Hook
        if result["locked_pages"] > 0:
            st.warning(
                f"🔒 **{result['locked_pages']} more pages are locked in Free Preview.** "
                "Upgrade to Pro to unlock the complete statement."
            )
