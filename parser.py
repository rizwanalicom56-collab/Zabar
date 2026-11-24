import os
import re
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
import pandas as pd
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def process_fab_pdf(pdf_path, output_excel, is_pro=False):
    """FAB Bank Statement Parser - Fully Optimized & Bulletproofed."""
    try:
        # 1. File & Encryption Check
        if not os.path.exists(pdf_path):
            return {"status": "error", "message": "PDF file not found on server."}

        try:
            reader = PdfReader(pdf_path)
        except PdfReadError:
            return {"status": "error", "message": "Corrupted or invalid PDF file."}

        if reader.is_encrypted:
            return {
                "status": "error",
                "message": "This PDF is password-protected. Please remove the password and upload again."
            }

        total_pages = len(reader.pages)
        if total_pages == 0:
            return {"status": "error", "message": "The uploaded PDF has 0 pages."}

        # 2. Extract First Page & Verify Bank Identity
        first_page_text = reader.pages[0].extract_text() or ""
        if len(first_page_text.strip()) < 30:
            return {
                "status": "error",
                "message": "Scanned/Image PDF detected. Only digital bank PDFs are supported."
            }

        if "First Abu Dhabi Bank" not in first_page_text and "bankfab.com" not in first_page_text:
            return {
                "status": "error",
                "message": "Unsupported Bank! Currently only First Abu Dhabi Bank (FAB) statements are supported."
            }

        # 3. Extract Account Metadata
        iban_match = re.search(r"IBAN:\s*([A-Z0-9]+)", first_page_text)
        acc_match = re.search(r"Account number:\s*(\d+)", first_page_text)
        curr_match = re.search(r"Currency:\s*([A-Z]{3})", first_page_text)
        period_match = re.search(r"Account statement:\s*(.+)", first_page_text)

        metadata = {
            "Bank": "First Abu Dhabi Bank (FAB)",
            "Account Number": acc_match.group(1) if acc_match else "N/A",
            "IBAN": iban_match.group(1) if iban_match else "N/A",
            "Currency": curr_match.group(1) if curr_match else "AED",
            "Period": period_match.group(1).strip() if period_match else "N/A",
        }

        # 4. Free vs Pro Page Limit
        pages_to_process = total_pages if is_pro else min(3, total_pages)
        full_text = ""

        for i in range(pages_to_process):
            page_text = reader.pages[i].extract_text() or ""
            header_match = re.search(
                r"(?:Posting\s+)?Date\s+Value\s+Date.*?Balance", page_text, re.DOTALL
            )
            if header_match:
                table_part = page_text[header_match.end():]
            else:
                table_part = page_text
            table_part = table_part.split("This is a system generated document")[0]
            full_text += "\n" + table_part.strip()

        if not full_text.strip():
            return {
                "status": "error",
                "message": "Could not locate transaction table in this FAB PDF."
            }

        # 5. Split Transactions
        tx_pattern = re.compile(
            r"(?=\b\d{2}-[A-Za-z]{3}-\d{4}\s+\d{2}-[A-Za-z]{3}-\d{4}\b)"
        )
        raw_blocks = [b.strip() for b in tx_pattern.split(full_text) if b.strip()]

        row_regex = re.compile(
            r"^(?P<date>\d{2}-[A-Za-z]{3}-\d{4})\s+"
            r"(?P<val_date>\d{2}-[A-Za-z]{3}-\d{4})\s+"
            r"(?P<desc>.*?)\s+"
            r"(?P<amount>[\d,]+\.\d{2})\s+"
            r"(?P<balance>[\d,]+\.\d{2})$",
            re.DOTALL,
        )

        transactions = []
        for block in raw_blocks:
            clean_block = " ".join(block.split())
            match = row_regex.match(clean_block)
            if match:
                try:
                    data = match.groupdict()
                    amt_str = data["amount"].replace(",", "")
                    bal_str = data["balance"]
                    if bal_str.count(",") > 1:
                        parts = bal_str.split(",")
                        bal_str = "".join(parts[:-1]).replace(",", "") + "." + parts[-1]
                    else:
                        bal_str = bal_str.replace(",", "")

                    amt = float(amt_str)
                    bal = float(bal_str)

                    transactions.append({
                        "Date": data["date"],
                        "Value Date": data["val_date"],
                        "Description": data["desc"],
                        "Amount": amt,
                        "Balance": bal,
                    })
                except ValueError:
                    continue

        if not transactions:
            return {
                "status": "error",
                "message": "No valid transaction rows could be parsed."
            }

        df = pd.DataFrame(transactions)

        # 6. Debit vs Credit via balance math + keyword fallback
        debits = []
        credits = []
        audit_status = []
        credit_keywords = [
            "inward", "salary", "deposit", "reverse charges", "credit", "refund"
        ]

        for i in range(len(df)):
            curr_bal = df.loc[i, "Balance"]
            amt = df.loc[i, "Amount"]
            desc_lower = df.loc[i, "Description"].lower()

            if i == 0:
                if any(k in desc_lower for k in credit_keywords):
                    credits.append(amt)
                    debits.append(0.0)
                else:
                    debits.append(amt)
                    credits.append(0.0)
                audit_status.append("Opening Row")
            else:
                prev_bal = df.loc[i - 1, "Balance"]
                if round(prev_bal + amt, 2) == round(curr_bal, 2):
                    credits.append(amt)
                    debits.append(0.0)
                    audit_status.append("OK")
                elif round(prev_bal - amt, 2) == round(curr_bal, 2):
                    debits.append(amt)
                    credits.append(0.0)
                    audit_status.append("OK")
                else:
                    if any(k in desc_lower for k in credit_keywords):
                        credits.append(amt)
                        debits.append(0.0)
                    else:
                        debits.append(amt)
                        credits.append(0.0)
                    audit_status.append("MISMATCH / CHECK")

        df["Debit"] = debits
        df["Credit"] = credits
        df["Audit Check"] = audit_status
        df = df[["Date", "Value Date", "Description", "Debit", "Credit", "Balance", "Audit Check"]]

        # 7. Auto-Categorization
        def categorize(desc):
            d = desc.lower()
            if "vat" in d or "charge" in d or "chgs" in d:
                return "Bank Fees & VAT"
            elif "salary" in d:
                return "Salary / Payroll"
            elif "utility" in d:
                return "Utility Bills"
            elif "debit card" in d:
                return "Card / POS Expense"
            elif "atm" in d:
                return "ATM Cash"
            elif "transfer" in d:
                return "Fund Transfer"
            return "Other"

        df["Category"] = df["Description"].apply(categorize)

        # 8. Export Multi-Sheet Excel
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Transactions", index=False)
            cat_summary = df.groupby("Category")[["Debit", "Credit"]].sum().reset_index()
            cat_summary.to_excel(writer, sheet_name="Summary & Audit", index=False, startrow=7)

        # 9. Styling (Matches Espresso Brown Theme)
        wb = load_workbook(output_excel)
        ws_tx = wb["Transactions"]
        header_fill = PatternFill(start_color="3E2723", end_color="3E2723", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        warn_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        for cell in ws_tx[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for row in ws_tx.iter_rows(min_row=2, max_row=ws_tx.max_row):
            if row[6].value == "MISMATCH / CHECK":
                for c in row:
                    c.fill = warn_fill

        ws_sum = wb["Summary & Audit"]
        ws_sum["A1"] = "FAB STATEMENT AUDIT REPORT"
        ws_sum["A1"].font = Font(size=14, bold=True, color="3E2723")

        ws_sum["A2"] = f"Account No: {metadata['Account Number']}"
        ws_sum["B2"] = f"IBAN: {metadata['IBAN']}"
        ws_sum["A3"] = f"Period: {metadata['Period']}"
        ws_sum["B3"] = f"Currency: {metadata['Currency']}"

        ws_sum["A5"] = "Total Credits (Inflow):"
        ws_sum["B5"] = round(df["Credit"].sum(), 2)
        ws_sum["A6"] = "Total Debits (Outflow):"
        ws_sum["B6"] = round(df["Debit"].sum(), 2)

        for cell in ws_sum[8]:
            cell.fill = header_fill
            cell.font = header_font

        for sheet in [ws_tx, ws_sum]:
            for col in sheet.columns:
                max_len = max((len(str(cell.value or "")) for cell in col), default=10)
                sheet.column_dimensions[col[0].column_letter].width = min(max_len + 4, 45)

        wb.save(output_excel)

        return {
            "status": "success",
            "message": "FAB statement parsed successfully!",
            "metadata": metadata,
            "total_pages": total_pages,
            "processed_pages": pages_to_process,
            "locked_pages": total_pages - pages_to_process,
            "tx_count": len(df),
            "total_credit": round(df["Credit"].sum(), 2),
            "total_debit": round(df["Debit"].sum(), 2),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred while processing the FAB statement: {str(e)}"
        }


# Example Usage (Testing ke liye)
if __name__ == "__main__":
    sample_pdf = "fab_statement.pdf"
    output_file = "fab_parsed_report.xlsx"

    result = process_fab_pdf(sample_pdf, output_file, is_pro=True)
    print(result)
