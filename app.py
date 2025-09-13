import streamlit as st
import pytesseract
from PIL import Image
import sqlite3
import hashlib
import io

# ---------------- Mock Database ----------------
def init_db():
    conn = sqlite3.connect("certificates.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS certificates
                 (cert_id TEXT, name TEXT, degree TEXT, year INT, hash TEXT)''')
    # Insert some sample records (only if empty)
    c.execute("SELECT COUNT(*) FROM certificates")
    if c.fetchone()[0] == 0:
        data = [
            ("CERT001", "Radha Sharma", "B.Tech CSE", 2025, "hash123"),
            ("CERT002", "Arun Kumar", "M.Sc Math", 2024, "hash456")
        ]
        c.executemany("INSERT INTO certificates VALUES (?,?,?,?,?)", data)
    conn.commit()
    return conn

# ---------------- Certificate Check ----------------
def check_certificate(extracted_text, file_bytes):
    conn = init_db()
    c = conn.cursor()
    
    # Simple search by name or ID
    c.execute("SELECT * FROM certificates WHERE name LIKE ? OR cert_id LIKE ?",
              (f"%{extracted_text}%", f"%{extracted_text}%"))
    result = c.fetchone()
    
    if result:
        return "✅ VALID Certificate", result
    else:
        # Run simple AI/Tamper check = file hash comparison
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        if file_hash.endswith("0"):  # just a toy rule
            return "⚠️ SUSPICIOUS - Possible Tampering", None
        else:
            return "❌ FAKE Certificate", None

# ---------------- Streamlit UI ----------------
st.title("🎓 Academic Certificate Verification Prototype")

uploaded_file = st.file_uploader("Upload a certificate (Image)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Show uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Certificate", use_column_width=True)

    # Extract text using OCR
    extracted_text = pytesseract.image_to_string(img)
    st.subheader("🔎 Extracted Text:")
    st.write(extracted_text)

    # Run verification
    file_bytes = uploaded_file.getvalue()
    status, record = check_certificate(extracted_text, file_bytes)

    st.subheader("📌 Verification Result:")
    st.success(status) if "VALID" in status else st.error(status) if "FAKE" in status else st.warning(status)

    if record:
        st.write("**Matched Record:**")
        st.json({
            "Certificate ID": record[0],
            "Name": record[1],
            "Degree": record[2],
            "Year": record[3]
        })
