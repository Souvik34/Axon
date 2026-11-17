
from docx import Document
from app.services.document.extractor import extract_text

# Create a test DOCX containing a paragraph and a table.
doc = Document()
doc.add_paragraph("Axon is an agentic RAG platform.")

table = doc.add_table(rows=2, cols=2)
table.cell(0, 0).text = "Provider"
table.cell(0, 1).text = "Role"
table.cell(1, 0).text = "Groq"
table.cell(1, 1).text = "Primary LLM"

doc.save("test_document.docx")

# Extract the content.
text = extract_text("test_document.docx")

print("--- EXTRACTED CONTENT ---")
print(text)

assert "Axon is an agentic RAG platform." in text
assert "Provider | Role" in text
assert "Groq | Primary LLM" in text

print("\nDOCX extraction test PASSED.")
