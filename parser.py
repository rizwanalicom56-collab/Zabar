# parser.py - Zabar V3 - Manager + Bank Engines
# Manager ka kaam: Bank ka naam lo -> Us bank ka engine chalao
# FAB Engine ka kaam: Sirf data idhar se udhar karna, bank check nahi karna

import os
import re
from pypdf import PdfReader
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# ============================================================
# MANAGER - ROUTER
# ============================================================

def process_statement(pdf_path, output_excel, bank_code="FAB", is_pro=False):
    """
    Manager: Bank code ke hisab se us bank ka engine chalao
    bank_code: FAB, ADCB, NBD ...
    """
    bank_code = str(bank_code).upper().strip()

    if bank_code == "FAB":
        return fab_engine(pdf_path, output_excel, is_pro=is_pro)
    elif bank_code == "ADCB":
        return {"error": "ADCB is coming soon. Right now only FAB works."}
    elif bank_code == "NBD":
        return {"error": "【entity-Emirates NBD¦canonical_name=Emirates NBD】 is coming soon. Right now only FAB works."}
    else:
        # Default: FAB samjho, taake purani file bhi chale
        return fab_engine(pdf_path, output_excel, is_pro=is_pro)

# Purane naam ke liye bhi kaam kare - taake purana code na toote
def process_fab_pdf(pdf_path, output_excel, is_pro=False):
    return fab_engine(pdf_path, output_excel, is_pro=is_pro)

# ============================================================
# HELPERS - Category + Amount
# ============================================================

def get_category(desc):
    d = str(desc).upper()
    if any(x in d for x in ["SALARY", "PAYROLL", "WPS", "WAGES"]):
        return "Salary"
    if any(x in d for x in ["ATM", "CASH WITHDRAWAL"]):
        return "ATM"
    if any(x in d for x in ["POS", "CARD", "VISA", "MASTERCARD"]):
        return "Card"
    if any(x in d for x in ["FEE", "CHARGE", "COMMISSION", "VAT"]):
        return "Fees"
    if any(x in d for x in ["TRANSFER", "TRF", "REMITTANCE", "WIRE"]):
        return "Transfer"
    if any(x in d for x in ["INTEREST", "PROFIT"]):
        return "Interest"
    if any(x in d for x in ["LOAN", "EMI", "INSTALLMENT"]):
        return "Loan"
    if any(x in d for x in ["CHEQUE", "CHK"]):
        return "Cheque"
    return "Other"

def clean_amount(s):
    if s is None:
        return 0.0
    s = str(s).replace(",", "").replace("AED", "").replace("AED", "").strip()
    is_neg = False
    if "(" in s and ")" in s:
        is_neg = True
        s = s.replace("(", "").replace(")", "")
    # -1,234.00 ya 1,234.00-
    if s.startswith("-"):
        is_neg = True
        s = s.replace("-", "")
    if s.endswith("-"):
        is_neg = True
        s = s.replace("-", "")
    try:
        val = float(s)
        return -val if is_neg else val
    except:
        return 0.0

# ============================================================
# FAB ENGINE - Sirf Data Idhar Se Udhar
# Bank check NAHI karega - User ne pehle hi FAB bol diya hai
# ============================================================

def fab_engine(pdf_path, output_excel, is_pro=False):
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        if "password" in str(e).lower() or "encrypted" in str(e).lower():
            return {"error": "This PDF is password-protected. Please remove password and try again."}
        return {"error": f"Could not read PDF: {str(e)}"}

    if reader.is_encrypted:
        return {"error": "This PDF is password-protected. Please remove password and try again."}

    total_pages = len(reader.pages)
    if total_pages == 0:
        return {"error": "PDF is empty."}

    processed_pages = total_pages if is_pro else min(3, total_pages)
    locked_pages = total_pages - processed_pages

    # ---------- PAGE 1 - Metadata (Narm wala, FAB check nahi) ----------
    first_text = ""
    try:
        first_text = reader.pages[0].extract_text() or ""
    except:
        first_text = ""

    # Scanned check - agar text hi nahi hai to scanned hai
    if len(first_text.strip()) < 50:
        return {"error": "This looks like a scanned PDF. Only digital PDF works, the one you download from bank."}

    # FAB check HATA DIYA - User ne pehle hi FAB select kiya hai
    # Ab sirf metadata nikalenge, agar mile to, warna khali chhor denge

    metadata = {}
    def find_field(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    metadata["Account Number"] = find_field(r"Account\s*(?:Number|No\.?)\s*[:\-]?\s*([0-9Xx\*\- ]+)", first_text)
    metadata["IBAN"] = find_field(r"IBAN\s*[:\-]?\s*([A-Z0-9 ]+)", first_text)
    metadata["Currency"] = find_field(r"Currency\s*[:\-]?\s*([A-Z]{3})", first_text) or "AED"
    metadata["Period"] = find_field(r"(?:Statement\s*Period|Period)\s*[:\-]?\s*([^\n\r]+)", first_text)
    metadata["Customer Name"] = find_field(r"(?:Customer\s*Name|Account\s*Holder|Name)\s*[:\-]?\s*([^\n\r]+)", first_text)
    metadata["Bank"] = "FAB"

    # ---------- TRANSACTIONS - Narm Wala Pattern ----------
    transactions = []
    # Date: 01/01/2024, 01-01-2024, 01.01.2024, 01 Jan 2024, 01-Jan-2024
    date_pattern = re.compile(r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})", re.IGNORECASE)

    for p_idx in range(processed_pages):
        try:
            text = reader.pages[p_idx].extract_text() or ""
        except:
            continue
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if len(line) < 10:
                continue
            dm = date_pattern.search(line)
            if not dm:
                continue
            date_str = dm.group(1)

            # Numbers - 1,234.56, (1,234.56), 1234.56, -1,234.56
            nums = re.findall(r"\(?\-?[\d,]+\.\d{2}\)?\-?", line)
            if len(nums) < 1:
                continue

            # Description - Date hatado, Numbers hatado, baki bacha Description
            desc_part = line.replace(date_str, "", 1)
            for n in nums:
                desc_part = desc_part.replace(n, "", 1)
            desc = re.sub(r"\s+", " ", desc_part).strip()
            # Choti si safai
            desc = desc.replace("|", " ").strip()
            if len(desc) < 3:
                continue
            # Header / Footer wali lines skip karo
            if any(x in desc.upper() for x in ["BALANCE BROUGHT", "OPENING BALANCE", "TOTAL", "PAGE", "STATEMENT OF", "ACCOUNT STATEMENT"]):
                continue

            balance = clean_amount(nums[-1])
            debit = 0.0
            credit = 0.0

            if len(nums) >= 3:
                debit = clean_amount(nums[-3])
                credit = clean_amount(nums[-2])
            elif len(nums) == 2:
                amt = clean_amount(nums[0])
                if len(transactions) == 0:
                    # Pehli row - positive to credit, negative to debit
                    if amt >= 0:
                        credit = abs(amt)
                    else:
                        debit = abs(amt)
                else:
                    prev_bal = transactions[-1]["Balance"]
                    if balance > prev_bal:
                        credit = abs(amt)
                    elif balance < prev_bal:
                        debit = abs(amt)
                    else:
                        credit = abs(amt)
            else:
                # Sirf 1 number hai, wo Balance hai, transaction nahi
                continue

            # Agar Debit aur Credit dono 0 hain to skip
            if debit == 0 and credit == 0:
                continue

            # Audit - Balance se verify
            audit = "OK"
            if len(transactions) > 0:
                prev_bal = transactions[-1]["Balance"]
                expected = round(prev_bal - debit + credit, 2)
                if abs(expected - balance) > 1.5:
                    audit = "MISMATCH"

            transactions.append({
                "Date": date_str,
                "Value Date": date_str,
                "Description": desc[:120],
                "Debit": round(debit, 2),
                "Credit": round(credit, 2),
                "Balance": round(balance, 2),
                "Category": get_category(desc),
                "Audit Check": audit
            })

    if len(transactions) == 0:
        return {"error": "No transactions found. Please upload a valid digital FAB statement."}

    total_credit = round(sum(t["Credit"] for t in transactions), 2)
    total_debit = round(sum(t["Debit"] for t in transactions), 2)

    # ---------- EXCEL ----------
    df = pd.DataFrame(transactions)
    cat_summary = df.groupby("Category").agg(
        Count=("Category", "count"),
        Total_Debit=("Debit", "sum"),
        Total_Credit=("Credit", "sum")
    ).reset_index()
    mismatch_count = len(df[df["Audit Check"] == "MISMATCH"])

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Transactions", index=False)
        summary_data = [
            ["Zabar - FAB Statement Summary", ""],
            ["", ""],
            ["Bank", "FAB"],
            ["Account Number", metadata.get("Account Number", "")],
            ["Customer Name", metadata.get("Customer Name", "")],
            ["Currency", metadata.get("Currency", "AED")],
            ["Period", metadata.get("Period", "")],
            ["Total Pages", total_pages],
            ["Processed Pages", processed_pages],
            ["Locked Pages", locked_pages],
            ["", ""],
            ["Total Transactions", len(transactions)],
            ["Total Credit", total_credit],
            ["Total Debit", total_debit],
            ["Mismatch Rows", mismatch_count],
            ["", ""],
            ["Category", "Count"],
        ]
        for _, r in cat_summary.iterrows():
            summary_data.append([r["Category"], int(r["Count"])])
        sum_df = pd.DataFrame(summary_data, columns=["Field", "Value"])
        sum_df.to_excel(writer, sheet_name="Summary & Audit", index=False, header=False)

        ws = writer.sheets["Transactions"]
        header_fill = PatternFill(start_color="231812", end_color="231812", fill_type="solid")
        header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        widths = [14, 14, 55, 14, 14, 15, 14, 13]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        red_fill = PatternFill(start_color="FDE8E8", end_color="FDE8E8", fill_type="solid")
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            if row[7].value == "MISMATCH":
                for c in row:
                    c.fill = red_fill

        ws2 = writer.sheets["Summary & Audit"]
        ws2.column_dimensions["A"].width = 28
        ws2.column_dimensions["B"].width = 28
        ws2["A1"].font = Font(name="Calibri", bold=True, size=14, color="231812")

    return {
        "metadata": metadata,
        "tx_count": len(transactions),
        "total_credit": total_credit,
        "total_debit": total_debit,
        "total_pages": total_pages,
        "processed_pages": processed_pages,
        "locked_pages": locked_pages
    }
