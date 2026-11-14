from app.services.document.extractor import extract_text
from app.services.document.chunker import chunk_text

text = extract_text("storage/documents/test.txt")

# Repeat the sample to generate enough words for multiple chunks.
large_text = "\n\n".join([text] * 10)

chunks = chunk_text(large_text)

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    print(f"\nChunk {index}")
    print("Word count:", len(chunk.split()))
    print("Content:", chunk)
print("\n--- Overlap Verification ---")

chunk_0_words = chunks[0].split()
chunk_1_words = chunks[1].split()

print("Last 40 words of chunk 0:")
print(" ".join(chunk_0_words[-40:]))

print("\nFirst 40 words of chunk 1:")
print(" ".join(chunk_1_words[:40]))

print(
    "\nOverlap matches:",
    chunk_0_words[-40:] == chunk_1_words[:40]
)