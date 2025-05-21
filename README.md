# 🩺 Medical Report Analyzer & Summarizer

## [Try The App](https://olami2596-medical-summary-llm-app-8e7trw.streamlit.app/) 👈 Click here!

A privacy-focused application that helps healthcare professionals and patients analyze, de-identify, and summarize medical reports.

## 🌟 Features

- **Document Processing**: Upload and extract text from PDFs, Word documents, and images
- **Privacy Protection**: Automatically de-identify patient information (names, dates, locations, etc.)
- **Dual Summarization**: Generate separate summaries tailored for medical practitioners and patients
- **Interactive Q&A**: Ask questions about the report contents
- **Export Options**: Download summaries as formatted PDF documents

## 🛠️ How It Works

1. **Upload Report**: The app accepts PDFs, DOCXs, or images containing medical reports
2. **Review & Edit**: View and edit the extracted text if needed
3. **De-identify**: Remove sensitive patient information automatically
4. **Generate Summaries**: Create two versions - one for healthcare providers and one in layman's terms
5. **Ask Questions**: Use AI to answer specific questions about the report
6. **Download Results**: Export the summaries as a PDF document

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **NLP Processing**: spaCy, HuggingFace Embeddings
- **Text Extraction**: PyMuPDF, python-docx, Tesseract OCR
- **Vector Database**: FAISS
- **Language Model**: Google's Gemini API
- **PDF Generation**: ReportLab

## 🚀 Installation

### Prerequisites

- Python 3.9+
- A Google Gemini API key
- The Python packages from requirements.txt

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/medical-report-analyzer.git
   cd medical-report-analyzer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the spaCy model:
   ```bash
   python -m spacy download en_core_web_lg
   ```

4. Create a `.env` file in the project root with your API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📝 Usage

### For Healthcare Providers

- Upload patient reports for quick summarization
- Use de-identification to protect patient privacy when sharing or storing reports
- Generate concise summaries focusing on clinical relevance
- Ask specific questions to extract information quickly

### For Patients

- Upload medical reports to get easy-to-understand explanations
- Learn about medical findings without complex terminology
- Ask questions in natural language to better understand your health

## 🔐 Privacy

This application prioritizes privacy by:

- Performing all processing locally on your device
- Automatically removing personally identifiable information
- Not storing any uploaded documents or extracted text
- Using secure API calls for AI functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) - For the amazing web framework
- [spaCy](https://spacy.io/) - For powerful NLP capabilities
- [Google Generative AI](https://ai.google.dev/) - For the Gemini API
- [FAISS](https://github.com/facebookresearch/faiss) - For efficient similarity search
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - For PDF processing

---

> **Note:** This application is intended for informational purposes only and should not replace professional medical advice. Always consult with healthcare professionals regarding medical decisions.

