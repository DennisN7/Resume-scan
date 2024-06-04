# app.py
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import spacy
import docx2txt
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

nlp = spacy.load('en_core_web_sm')

job_descriptions = {
    "Software Engineer": "Develop and maintain software applications...",
    "Data Scientist": "Analyze data to extract insights...",
    "Project Manager": "Manage projects and coordinate team projects..."
}

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extract_text()
    return text

def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return ' '.join(tokens)

@app.route('/scan-resume', methods=['POST'])
def scan_resume():
    file = request.files['resume']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    if filename.endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_path)
    elif filename.endswith('.docx'):
        resume_text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file type"}), 400
    
    processed_resume = preprocess_text(resume_text)
    
    vectorizer = CountVectorizer().fit_transform([processed_resume] + list(job_descriptions.values()))
    vectors = vectorizer.toarray()
    cosine_matrix = cosine_similarity(vectors)
    
    job_match_index = cosine_matrix[0][1:].argmax()
    job_match = list(job_descriptions.keys())[job_match_index]
    
    resume_quality = int((len(resume_text) / 2000) * 100)
    resume_quality = min(100, resume_quality)
    
    return jsonify({
        "jobMatch": job_match,
        "resumeQuality": resume_quality
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

