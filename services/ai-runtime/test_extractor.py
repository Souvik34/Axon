from app.services.document.extractor import extract_text

text = extract_text("storage/documents/test.txt")

print("Extracted text:")
print(text)

print("\nCharacter count:", len(text))