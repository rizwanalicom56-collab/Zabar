# app.py - Salamum V4 - FINAL - Height Fix
import os
import uuid
import html as _html
import streamlit as st
import streamlit.components.v1 as components
from parser import process_fab_pdf

st.set_page_config(page_title="Salamum | FAB Statement to Excel", page_icon="📊", layout="centered")
os.makedirs("temp_files", exist_ok=True)

def H(s: str) -> str:
    return "\n".join(line.strip() for line in s.strip().splitlines())

def send_live_height():
    # FIX: window.parent -> window.top, taake message converting.html tak jaye
    components.html("""
    <script>
    (function(){
      function getHeight(){
        try{
          // Streamlit page ka asli height - parent document se lo
          var doc = window.parent.document;
          var body = doc.body;
          var app = doc.querySelector('[data-testid="stAppViewContainer"]');
          var h = 0;
          if(app){ h = Math.max(h, app.scrollHeight); }
          if(body){ h = Math.max(h, body.scrollHeight); }
          // Kam se kam 244, zyada se zyada 1400
          return Math.min(1400, Math.max(244, h + 20));
        }catch(e){
          return 244;
        }
      }
      var lastH = 0;
      function emit(force){
        var h = getHeight();
        if(force || Math.abs(h - lastH) >= 3){
          lastH = h;
          // TOP ko bhejo, PARENT ko nahi - yehi fix hai
          window.top.postMessage({type: "SALAMUM_HEIGHT", height: h}, "*");
          // Backup - parent ko bhi bhejo
          try{ window.parent.postMessage({type: "SALAMUM_HEIGHT", height: h}, "*"); }catch(e){}
        }
      }
      // Har 300ms me check karo, taake file select karte hi height badhe
      setInterval(function(){ emit(false); }, 300);
      window.addEventListener("load", function(){ emit(true); });
      setTimeout(function(){ emit(true); }, 500);
      setTimeout(function(){ emit(true); }, 1200);
    })();
    </script>
    """, height=0)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
:root{ --ink:#231812; --gold:#C9A86A; --gold2:#D4B483; --line:#F0E8DD; --muted:#7a6a5e; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, section.main, button, input{ font-family:'Poppins', sans-serif !important; }
.stApp{ background:#FFFEFB !important; color:var(--ink); }
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton, [data-testid="stViewerBadge"], [class*="viewerBadge"], [class*="stActionButton"], .stApp > footer, [data-testid="stBottom"], [data-testid="stBottomBlockContainer"]{ display:none !important; visibility:hidden !important; height:0 !important; overflow:hidden !important; }
.block-container{ max-width:100% !important; padding:0 !important; margin:0 !important; }
[data-testid="stVerticalBlock"], [data-testid="stElementContainer"], [data-testid="stFileUploader"]{ margin:0 !important; padding:0 !important; width:100% !important; }
[data-testid="stFileUploader"] > label{ display:none !important; }
[data-testid="stFileUploaderDropzone"]{ background:transparent !important; border:none !important; padding:16px 12px !important; min-height:225px !important; width:100% !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; gap:10px !important; text-align:center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > *{ display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{ width:100% !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; gap:6px !important; }
[data-testid="stFileUploaderDropzoneInstructions"]::before{ content:""; display:block; width:52px; height:52px; margin:0 auto; background-color:var(--ink); background-image:url("data:image/svg+xml;utf8,[STRIPPED]"); background-repeat:no-repeat; background-position:center; border-radius:14px; }
[data-testid="stFileUploaderDropzoneInstructions"]::after{ content:"Drop your FAB PDF here\\A or click to select from your device"; display:block; width:100%; text-align:center; white-space:pre-line; font-size:13px; color:#8a7a6e; line-height:1.55; }
[data-testid="stFileUploaderDropzone"] button{ background:var(--ink) !important; color:#fff !important; border:none !important; border-radius:100px !important; width:100%; max-width:240px; height:42px; margin:0 auto !important; display:flex !important; align-items:center !important; justify-content:center !important; font-size:0 !important; }
[data-testid="stFileUploaderDropzone"] button *{ display:none !important; }
[data-testid="stFileUploaderDropzone"] button::after{ content:"Select PDF"; font-size:13.5px; font-weight:600; color:#fff; }
[data-testid="stFileUploaderFile"]{ background:#F5EEE6 !important; border-radius:14px !important; padding:6px 10px !important; margin-top:8px !important; }
[data-testid="stFileUploaderFileName"]{ font-weight:500 !important; color:var(--ink) !important; }
.result-ok{ background:#EAF7F0; border:1px solid #C8E9D8; color:#14704F; border-radius:16px; padding:12px 16px; font-size:13.5px; font-weight:500; margin:14px 0 12px; line-height:1.5; }
.err-box{ background:#FDECEC; border:1px solid #F5C6C6; color:#B42318; border-radius:16px; padding:12px 16px; font-size:13.5px; font-weight:500; margin:14px 0 12px; line-height:1.5; }
.stats{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-bottom:14px; }
.stat{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:12px; box-shadow:0 6px 18px rgba(35,24,18,.04); }
.stat span{ display:block; font-size:11px; color:#8a7a6e; margin-bottom:4px; }
.stat b{ display:block; font-size:14.5px; color:var(--ink); word-break:break-word; }
.stat.credit{ background:#EAF7F0; border-color:#C8E9D8; } .stat.credit b{ color:#14704F; }
.stat.debit{ background:#FDECEC; border-color:#F5C6C6; } .stat.debit b{ color:#B42318; }
[data-testid="stDownloadButton"] button{ background:linear-gradient(135deg,var(--gold2),var(--gold)) !important; color:var(--ink) !important; border:none !important; border-radius:100px !important; height:48px; font-weight:600 !important; font-size:14px !important; box-shadow:0 10px 24px rgba(201,168,106,.35); }
.locked{ background:var(--ink); color:#fff; border-radius:18px; padding:18px 16px; margin-top:14px; display:flex; flex-direction:column; gap:12px; text-align:center; box-shadow:0 14px 28px rgba(35,24,18,.18); }
.locked h4{ font-size:15px; color:var(--gold); margin:0 0 4px; }
.locked p{ font-size:12.5px; color:#CBB8A3; line-height:1.5; margin:0; }
.locked .price{ background:linear-gradient(135deg,var(--gold2),var(--gold)); color:var(--ink); font-weight:700; font-size:12.5px; padding:10px 16px; border-radius:100px; }
[data-testid="stSpinner"] p{ color:var(--muted) !important; font-size:13px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

uploaded_pdf = st.file_uploader("Choose a FAB PDF file", type=["pdf"], label_visibility="collapsed")

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
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
    if result["status"] == "error":
        st.markdown(f'<div class="err-box">⚠️ {_html.escape(str(result["message"]))}</div>', unsafe_allow_html=True)
    else:
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
        st.download_button(label=f"📥 Download Clean Excel ({result['processed_pages']} Pages)", data=excel_bytes, file_name=f"FAB_Audit_{meta['Account Number']}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
        if result["locked_pages"] > 0:
            st.markdown(H(f"""
            <div class="locked"><div><h4>🔒 {result['locked_pages']} more pages are locked</h4><p>Free preview mein sirf pehle 3 pages hain. Pro se poora statement unlock karein.</p></div><div class="price">Go Pro — 19 AED</div></div>
            """), unsafe_allow_html=True)

send_live_height()
