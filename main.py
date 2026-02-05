import streamlit as st
import nltk

# Download NLTK data on first run
@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)

download_nltk_data()

from nltk.tokenize import sent_tokenize, word_tokenize

# Try PyPDF2 first, fallback to pypdf
try:
    import PyPDF2
except ImportError:
    import pypdf as PyPDF2

# ------------------ APP CONFIG ------------------
st.set_page_config(page_title="Offline Test Paper Evaluator", page_icon="📘")
st.title("📘 Offline Test Paper Evaluation System")
st.write("Upload a student answer PDF. Evaluation is done automatically (NO API key required).")

# ------------------ FUNCTIONS ------------------
def extract_text_from_pdf(pdf):
    reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.strip()

def evaluate_answer(answer, keywords, max_marks):
    tokens = word_tokenize(answer.lower())
    matched = [kw for kw in keywords if kw.lower() in tokens]

    score_ratio = len(matched) / len(keywords)
    marks = round(score_ratio * max_marks)

    if marks >= max_marks * 0.8:
        feedback = "Very good answer with strong conceptual clarity."
    elif marks >= max_marks * 0.5:
        feedback = "Good answer but lacks some important points."
    else:
        feedback = "Answer is weak and missing key concepts."

    return marks, feedback

# ------------------ KEYWORDS (RUBRIC) ------------------
rubric = {
    "Q1": {
        "keywords": ["artificial", "intelligence", "learning", "reasoning", "decision", "applications"],
        "marks": 10
    },
    "Q2": {
        "keywords": ["machine", "learning", "supervised", "unsupervised", "reinforcement", "data"],
        "marks": 10
    }
}

# ------------------ FILE UPLOAD ------------------
pdf_file = st.file_uploader("Upload Student Answer Sheet (PDF)", type=["pdf"])

# ------------------ EVALUATION ------------------
if st.button("Evaluate"):
    if not pdf_file:
        st.warning("Please upload a PDF file.")
    else:
        with st.spinner("Evaluating answers..."):
            text = extract_text_from_pdf(pdf_file)
            sentences = sent_tokenize(text)

            q1_answer = " ".join(sentences[:len(sentences)//2])
            q2_answer = " ".join(sentences[len(sentences)//2:])

            q1_marks, q1_feedback = evaluate_answer(
                q1_answer, rubric["Q1"]["keywords"], rubric["Q1"]["marks"]
            )
            q2_marks, q2_feedback = evaluate_answer(
                q2_answer, rubric["Q2"]["keywords"], rubric["Q2"]["marks"]
            )

            total = q1_marks + q2_marks

        st.subheader("📝 Evaluation Result")

        st.write(f"**Question 1:** {q1_marks} / 10")
        st.write(q1_feedback)

        st.write(f"**Question 2:** {q2_marks} / 10")
        st.write(q2_feedback)

        st.success(f"**Total Marks: {total} / 20**")
