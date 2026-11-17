
from app.services.document.extractor import extract_text
from app.services.document.chunker import chunk_text

text = extract_text("test.pdf")
chunks = chunk_text(text)

print("--- PAGE-AWARE CHUNKS ---")

for chunk in chunks:
    print("Page:", chunk["page_number"])
    print("Content:", chunk["content"])
    print()
