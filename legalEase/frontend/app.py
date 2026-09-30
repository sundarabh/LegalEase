import streamlit as st
st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

h1 {
    color: #1f3c88;
    text-align: center;
}

h3 {
    color: #2c3e50;
}

.stButton > button {
    border-radius: 10px;
    background-color: #1f3c88;
    color: white;
    font-weight: bold;
    width: 100%;
}

.stDownloadButton > button {
    border-radius: 10px;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)
import requests
from pypdf import PdfReader
from docx import Document
from io import BytesIO
import os
from dotenv import load_dotenv
from google import genai


# ---------------- SETUP ----------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered"
)


# ---------------- TITLE ----------------

st.title("⚖️ LegalEase")
st.markdown("### Your Simple Legal Assistant")
st.write("Upload a legal document and explore its content easily.")


# ---------------- BACKEND STATUS ----------------

st.divider()
st.subheader("🔗 Backend Status")

try:
    response = requests.get(
        "http://127.0.0.1:8000",
        timeout=3
    )

    if response.status_code == 200:
        st.success("🟢 Backend Connected Successfully")
    else:
        st.warning("🟡 Backend returned an unexpected response.")

except Exception:
    st.error(
        "🔴 Backend is not connected. "
        "Please start the FastAPI server."
    )


# ---------------- PDF UPLOAD ----------------

st.divider()

uploaded_file = st.file_uploader(
    "📄 Upload your legal document",
    type=["pdf"]
)


if uploaded_file:

    st.success(
        f"✅ {uploaded_file.name} uploaded successfully!"
    )

    # ---------------- PDF TEXT EXTRACTION ----------------

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""


    # ---------------- DOCUMENT CONTENT ----------------

    st.divider()
    st.subheader("📖 Document Content")

    st.text_area(
        "Extracted Text",
        text,
        height=300,
        key="extracted_text"
    )


    # ---------------- AI SUMMARY ----------------

    st.divider()
    st.subheader("🤖 AI Summary")

    if st.button(
        "🤖 Generate AI Summary",
        key="ai_summary"
    ):

        if not text.strip():
            st.warning("No text was found in the PDF.")

        elif gemini_client is None:
            st.error(
                "Gemini API key was not found. "
                "Please check your .env file."
            )

        else:

            with st.spinner("🤖 Gemini is analyzing the document..."):

                try:

                    prompt = f"""
You are a legal document education assistant.

Summarize the following legal document in simple language.

Give:
1. Document type
2. Main parties
3. Important dates
4. Payment information
5. Important obligations
6. Termination conditions
7. Other important points

Use simple bullet points.

Do not provide legal advice.

DOCUMENT:
{text}
"""

                    result = gemini_client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )

                    st.success("✅ AI Summary Generated!")

                    st.write(result.text)

                except Exception:
                    st.error(
                        "⚠️ Gemini is temporarily unavailable. "
                        "Please try again later."
                    )


    # ---------------- SIMPLE SEARCH ----------------

    st.divider()
    st.subheader("❓ Ask About Document")

    question = st.text_input(
        "Enter a keyword",
        key="document_question"
    )

    if st.button(
        "🔍 Search",
        key="document_search"
    ):

        if question:

            sentences = (
                text.replace("\n", " ")
                .split(".")
            )

            found = False

            for sentence in sentences:

                if question.lower() in sentence.lower():

                    st.success("Relevant information found:")
                    st.write(sentence.strip())

                    found = True

            if not found:
                st.info(
                    "No relevant information was found."
                )

        else:
            st.warning("Please enter a keyword.")


    # ---------------- DOCUMENT ANALYSIS ----------------

    st.divider()
    st.subheader("⚖️ Analyze Document")

    if st.button(
        "🔎 Analyze Document",
        key="analyze_document"
    ):

        text_lower = text.lower()

        st.write("### 📋 Document Analysis")

        if "contract" in text_lower:
            st.write("📄 Document Type: Contract")

        elif "agreement" in text_lower:
            st.write("📄 Document Type: Agreement")

        elif "lease" in text_lower:
            st.write("📄 Document Type: Lease Agreement")

        else:
            st.write(
                "📄 Document Type: General Legal Document"
            )

        if "payment" in text_lower:
            st.write("💰 Payment information found.")
        else:
            st.write(
                "💰 No payment information found."
            )

        if "termination" in text_lower:
            st.write(
                "⚠️ Termination condition found."
            )
        else:
            st.write(
                "⚠️ No termination condition found."
            )

        if "date" in text_lower:
            st.write(
                "📅 Date-related information found."
            )
        else:
            st.write(
                "📅 No date-related information found."
            )


    # ---------------- IMPORTANT CLAUSES ----------------

    st.divider()
    st.subheader("⚠️ Important Clauses")

    if st.button(
        "📌 Find Important Clauses",
        key="important_clauses"
    ):

        clause_words = [
            "payment",
            "termination",
            "confidential",
            "obligation",
            "liability",
            "penalty",
            "notice",
            "condition"
        ]

        found_clauses = []

        sentences = (
            text.replace("\n", " ")
            .split(".")
        )

        for sentence in sentences:

            for word in clause_words:

                if word in sentence.lower():

                    found_clauses.append(
                        sentence.strip()
                    )

                    break

        if found_clauses:

            for clause in found_clauses[:10]:

                st.warning(
                    "⚠️ " + clause
                )

        else:

            st.info(
                "No important clauses found."
            )


    # ---------------- DOCUMENT GENERATOR ----------------

    st.divider()
    st.subheader("📝 Document Generator")

    document_type = st.selectbox(
        "📄 Select Document Type",
        [
            "Employment Contract",
            "Lease Agreement",
            "NDA",
            "Freelance Work Contract"
        ],
        key="document_type"
    )

    first_party = st.text_input(
        "👤 First Party Name",
        key="first_party"
    )

    second_party = st.text_input(
        "👤 Second Party Name",
        key="second_party"
    )

    effective_date = st.date_input(
        "📅 Effective Date",
        key="effective_date"
    )

    terms = st.text_area(
        "📝 Terms and Conditions",
        key="terms"
    )

    if st.button(
        "📄 Generate Draft",
        key="generate_draft"
    ):

        if first_party and second_party and terms:

            st.success(
                "✅ Draft generated successfully!"
            )

            st.subheader(
                "📋 Generated Document"
            )

            st.write(
                f"**Document Type:** {document_type}"
            )

            st.write(
                f"**First Party:** {first_party}"
            )

            st.write(
                f"**Second Party:** {second_party}"
            )

            st.write(
                f"**Effective Date:** {effective_date}"
            )

            st.write("### Terms and Conditions")

            st.write(terms)


            # ---------------- TXT FILE ----------------

            draft_text = (
                "LEGAL DOCUMENT DRAFT\n\n"
                f"Document Type: {document_type}\n\n"
                f"First Party: {first_party}\n\n"
                f"Second Party: {second_party}\n\n"
                f"Effective Date: {effective_date}\n\n"
                "TERMS AND CONDITIONS\n\n"
                f"{terms}\n\n"
                "DISCLAIMER:\n"
                "This is a basic educational draft and "
                "should be reviewed by a qualified "
                "legal professional before use."
            )

            st.download_button(
                "⬇️ Download TXT",
                draft_text,
                "LegalEase_Draft.txt",
                "text/plain",
                key="download_txt"
            )


            # ---------------- WORD FILE ----------------

            document = Document()

            document.add_heading(
                "LEGAL DOCUMENT DRAFT",
                0
            )

            document.add_paragraph(
                f"Document Type: {document_type}"
            )

            document.add_paragraph(
                f"First Party: {first_party}"
            )

            document.add_paragraph(
                f"Second Party: {second_party}"
            )

            document.add_paragraph(
                f"Effective Date: {effective_date}"
            )

            document.add_heading(
                "Terms and Conditions",
                level=1
            )

            document.add_paragraph(terms)

            document.add_heading(
                "Disclaimer",
                level=1
            )

            document.add_paragraph(
                "This is a basic educational draft and "
                "should be reviewed by a qualified "
                "legal professional before use."
            )

            word_file = BytesIO()

            document.save(word_file)

            word_file.seek(0)

            st.download_button(
                "📘 Download Word Document",
                word_file,
                "LegalEase_Draft.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="download_docx"
            )

        else:

            st.warning(
                "Please fill in First Party Name, "
                "Second Party Name and Terms and Conditions."
            )


# ---------------- DISCLAIMER ----------------

st.divider()

st.warning(
    "⚠️ LegalEase provides general educational "
    "information only. It is not a substitute "
    "for professional legal advice."
)