import streamlit as st
import requests
import json
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

API_BASE_URL = 'http://127.0.0.1:8000'

def get_documents():
    response = requests.get(f'{API_BASE_URL}/api/documents')
    return response.json()

def generate_pdf(session_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph(f"Research Session - {session_data['timestamp']}", styles['Title']))
    elements.append(Paragraph(f"Documents: {', '.join(session_data['documents'])}", styles['Normal']))
    
    for i, (q, a) in enumerate(zip(session_data['questions'], session_data['answers']), 1):
        elements.append(Paragraph(f"Q{i}: {q}", styles['Heading2']))
        elements.append(Paragraph(f"A{i}: {a}", styles['Normal']))
        elements.append(Paragraph(" ", styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

st.title("Research Agent")

# Document Selection
st.header("Select Document(s) for Research")
documents = get_documents()

if documents:
    doc_options = []
    doc_id_map = {}
    for namespace, docs in documents.items():
        for doc in docs:
            option = f"{doc['title']} (Namespace: {namespace}, ID: {doc['id']})"
            doc_options.append(option)
            doc_id_map[option] = doc['id']
    
    selected_docs = st.multiselect(
        "Available Documents",
        options=doc_options
    )
else:
    st.write("No documents available.")

if st.button("Start Research Session") and selected_docs:
    # Extract document IDs
    selected_doc_ids = [doc_id_map[doc] for doc in selected_docs]
    # Initialize session state
    if 'session_data' not in st.session_state:
        st.session_state.session_data = {
            'documents': selected_doc_ids,
            'questions': [],
            'answers': [],
            'timestamp': datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        }
    st.success("Research session started.")

if 'session_data' in st.session_state:
    st.header("Ask Questions")
    question = st.text_input("Enter your question:")
    
    if st.button("Submit Question") and question:
        # Prepare payload
        payload = {
            'question': question,
            'documents': st.session_state.session_data['documents']
        }
        # Send request to backend
        response = requests.post(f'{API_BASE_URL}/copilotkit/agents/researchAgent/invoke', json=payload)
        if response.status_code == 200:
            answer = response.json().get('answer', 'No answer received.')
        else:
            st.error(f"Error from backend: {response.status_code} - {response.text}")
            answer = 'No answer received.'
        
        # Store Q&A
        st.session_state.session_data['questions'].append(question)
        st.session_state.session_data['answers'].append(answer)
        
        st.write(f"**Question:** {question}")
        st.write(f"**Answer:** {answer}")
        
        # Limit to 6 questions
        if len(st.session_state.session_data['questions']) >= 6:
            st.warning("Maximum number of questions reached.")


    if st.button("Save Research Session"):
        # Implement saving logic here (e.g., database or file)
        st.success("Research session saved.")
    
    if st.button("Export Results to PDF"):
        pdf = generate_pdf(st.session_state.session_data)
        st.download_button(
            label="Download PDF",
            data=pdf,
            file_name=f"research_session_{st.session_state.session_data['timestamp']}.pdf",
            mime='application/pdf'
        )
