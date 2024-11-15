import streamlit as st
import pdfkit

# Update with the correct path to wkhtmltopdf
path_to_wkhtmltopdf = "/usr/local/bin/wkhtmltopdf"  # Replace this with the correct path if different
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

# Function to generate markdown content
def generate_markdown(qa_pairs):
    markdown_content = "# Research Session Results\n\n"
    for idx, qa in enumerate(qa_pairs):
        markdown_content += f"## Question {idx + 1}\n"
        markdown_content += f"**Q:** {qa['question']}\n\n"
        markdown_content += f"**A:** {qa['answer']}\n\n"
    return markdown_content

# Function to generate PDF from markdown content with custom styles and margins
def generate_pdf_from_markdown(markdown_content):
    # Custom CSS for better PDF layout
    css = """
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        padding: 0;
        margin: 0;
    }
    h1, h2 {
        color: #2e3a59;
        margin-bottom: 1em;
    }
    p {
        margin-bottom: 1em;
    }
    .qa-container {
        margin-bottom: 2em;
    }
    .question {
        font-weight: bold;
        font-size: 1.2em;
    }
    .answer {
        margin-top: 10px;
        font-size: 1.1em;
    }
    """
    
    # Create an HTML string that includes the markdown content with styling
    html_content = f"""
    <html>
        <head>
            <style>
                {css}
                body {{
                    margin: 2cm;
                }}
            </style>
        </head>
        <body>
            <h1>Research Session Results</h1>
            {markdown_content}
        </body>
    </html>
    """
    
    # Use pdfkit to convert the HTML content into a PDF
    pdfkit.from_string(html_content, "research_report.pdf", configuration=config)
    st.success("PDF report generated successfully!")

# Setup Streamlit interface
def main():
    st.title("Research Interface & Q/A Interaction")

    # Document selection
    document_ids = ["doc1", "doc2"]  # Replace with actual document IDs if available
    selected_doc = st.selectbox("Select a document to research", document_ids)
    st.write(f"You selected {selected_doc}")

    # Initialize session state variables if they don't exist
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []

    # Collect Q/A results: Allow users to ask any number of questions dynamically
    question = st.text_input("Ask your question:")
    
    if question and question not in [qa['question'] for qa in st.session_state.qa_history]:  # Avoid duplicate questions
        # Simulate an answer (you can replace with actual logic to get answers)
        answer = f"This is a dummy answer to the question: {question}"
        st.write(f"**Answer:** {answer}")

        # Add the Q/A pair to session history
        st.session_state.qa_history.append({"question": question, "answer": answer})

    # Optionally, provide an option to continue asking more questions
    if st.button("Ask another question"):
        pass

    # Export and save options after at least one question is asked
    if st.session_state.qa_history:
        if st.button("Export Results to PDF"):
            markdown_content = generate_markdown(st.session_state.qa_history)
            generate_pdf_from_markdown(markdown_content)

        if st.button("Save Results as Markdown"):
            markdown_content = generate_markdown(st.session_state.qa_history)
            with open("research_results.md", "w") as f:
                f.write(markdown_content)
            st.success("Markdown file saved successfully!")

if __name__ == "__main__":
    main()
