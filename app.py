import os
os.environ["STREAMLIT_FILE_WATCHER_TYPE"] = "none"

import streamlit as st
from dotenv import load_dotenv
from file_loader import extract_text_from_pdf, extract_text_from_docx, extract_text_from_image
from deidentification import deidentify_patient_info
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_core.language_models.llms import LLM
from pydantic import Field
from typing import List
from google.generativeai import GenerativeModel, configure
import pickle
from summarizer import summarize_medical_report
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment
load_dotenv()
configure(api_key=os.getenv("GOOGLE_API_KEY")or st.secrets.get("GOOGLE_API_KEY"))

# LLM Wrapper
class GeminiLLMWrapper(LLM):
    client: object = Field(...)

    def _call(self, prompt: str, stop: List[str] = None) -> str:
        response = self.client.generate_content(prompt)
        return response.text

    @property
    def _llm_type(self) -> str:
        return "google-gemini"

# PDF Generator
def generate_pdf(practitioner_summary, patient_summary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    if practitioner_summary:
        elements.append(Paragraph("👨‍⚕️ Summary for Practitioner", styles['Heading2']))
        elements.append(Spacer(1, 12))
        for para in practitioner_summary.split('\n'):
            if para.strip():
                elements.append(Paragraph(para.strip(), styles['BodyText']))
                elements.append(Spacer(1, 6))

    if patient_summary:
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("👤 Summary for Patient", styles['Heading2']))
        elements.append(Spacer(1, 12))
        for para in patient_summary.split('\n'):
            if para.strip():
                elements.append(Paragraph(para.strip(), styles['BodyText']))
                elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# Streamlit UI setup
st.set_page_config(page_title="Medical Report Summarizer", layout="wide")
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 100%; }
        .stTextArea textarea { font-size: 1rem; line-height: 1.6; }
        @media (max-width: 768px) {
            .block-container { padding: 1rem; }
        }
    </style>
""", unsafe_allow_html=True)

st.title("🩺 Medical Report Analyzer & Summarizer")

# Intro
with st.expander("ℹ️ What does this app do?", expanded=True):
    st.markdown("""
    This app helps you analyze and summarize medical reports while protecting privacy.

    **How it works:**
    1. Upload your report (PDF, DOCX, or image)
    2. View and edit the extracted text
    3. De-identify sensitive data
    4. Generate summaries (for practitioners and patients)
    5. Ask questions or download results as a PDF
    """)

# Initialize state
defaults = {
    "deid_text": None, "final_text": None, "vector_index": None,
    "chunks": None, "wrapped_llm": None,
    "summary_practitioner": None, "summary_patient": None,
    "show_extracted": True, "show_deid": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Upload
uploaded_file = st.file_uploader("📤 Upload a medical report:", type=["pdf", "docx", "png", "jpg", "jpeg"])
if uploaded_file:
    ext = uploaded_file.name.lower()
    with st.spinner("🔍 Extracting text..."):
        if ext.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif ext.endswith(".docx"):
            extracted_text = extract_text_from_docx(uploaded_file)
        else:
            extracted_text = extract_text_from_image(uploaded_file)
    st.session_state.extracted_text = extracted_text
    st.session_state.show_extracted = True
    st.session_state.show_deid = False

# Step 1: Extracted Text
if "extracted_text" in st.session_state and st.session_state.extracted_text:
    with st.expander("📄 Review & Edit Extracted Text", expanded=st.session_state.show_extracted):
        edited_text = st.text_area("Edit extracted text:", value=st.session_state.extracted_text, height=400)

    if st.button("🔒 De-identify Text"):
        with st.spinner("De-identifying..."):
            st.session_state.deid_text = deidentify_patient_info(edited_text)
            st.session_state.final_text = st.session_state.deid_text
            st.session_state.vector_index = None
            st.session_state.chunks = None
            st.session_state.summary_practitioner = None
            st.session_state.summary_patient = None
            st.session_state.show_extracted = False
            st.session_state.show_deid = True

# Step 2: De-identified Text
if st.session_state.deid_text:
    with st.expander("🕵️ Review & Edit De-identified Text", expanded=st.session_state.show_deid):
        st.session_state.final_text = st.text_area(
            "De-identified (editable):", value=st.session_state.deid_text, height=400
        )

    if st.button("🧠 Summarize Report"):
        with st.spinner("Summarizing report..."):
            doc = Document(page_content=st.session_state.final_text)
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents([doc])
            for i, chunk in enumerate(chunks):
                chunk.metadata["source"] = f"chunk-{i+1}"

            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_index = FAISS.from_documents(chunks, embeddings)

            with open("vector_index.pkl", "wb") as f:
                pickle.dump(vector_index, f)

            gemini_model = GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config={"max_output_tokens": 512, "temperature": 0.5}
            )
            wrapped_llm = GeminiLLMWrapper(client=gemini_model)

            st.session_state.vector_index = vector_index
            st.session_state.chunks = chunks
            st.session_state.wrapped_llm = wrapped_llm

            try:
                st.session_state.summary_practitioner = summarize_medical_report("Medical Report", chunks, wrapped_llm, audience="practitioner")
            except Exception as e:
                st.session_state.summary_practitioner = f"❌ Practitioner summary failed: {e}"

            try:
                st.session_state.summary_patient = summarize_medical_report("Medical Report", chunks, wrapped_llm, audience="layman")
            except Exception as e:
                st.session_state.summary_patient = f"❌ Patient summary failed: {e}"

# Step 3: Summaries
if st.session_state.summary_practitioner or st.session_state.summary_patient:
    st.markdown("## 📋 Report Summaries")

    if st.session_state.summary_practitioner:
        with st.expander("👨‍⚕️ Summary for Practitioner"):
            st.write(st.session_state.summary_practitioner)

    if st.session_state.summary_patient:
        with st.expander("👤 Summary for Patient"):
            st.write(st.session_state.summary_patient)

    st.markdown("### 📥 Download Summary as PDF")
    options = []
    if st.session_state.summary_practitioner:
        options.append("Practitioner Summary")
    if st.session_state.summary_patient:
        options.append("Patient Summary")

    selected = st.multiselect("Choose summaries to include:", options, default=options)

    if selected:
        pdf_data = generate_pdf(
            st.session_state.summary_practitioner if "Practitioner Summary" in selected else "",
            st.session_state.summary_patient if "Patient Summary" in selected else ""
        )
        st.download_button("📄 Download Selected Summaries as PDF", data=pdf_data, file_name="medical_summary.pdf", mime="application/pdf")

# Step 4: Q&A
if st.session_state.vector_index and st.session_state.wrapped_llm:
    st.markdown("## 💬 Ask Questions")
    user_query = st.text_input("Type a question about the report:")
    if user_query:
        with st.spinner("Generating answer..."):
            try:
                chain = RetrievalQAWithSourcesChain.from_llm(
                    llm=st.session_state.wrapped_llm,
                    retriever=st.session_state.vector_index.as_retriever()
                )
                response = chain.invoke({"question": user_query})
                st.write(response["answer"])
            except Exception as e:
                st.error(f"❌ Failed to answer question: {e}")
