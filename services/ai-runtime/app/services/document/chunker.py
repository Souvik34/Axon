
import re


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 40
) -> list[dict]:

    if not text or not text.strip():
        raise ValueError("Cannot chunk empty text.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid overlap.")

    page_pattern = r"\[PAGE (\d+)\]"
    sections = re.split(page_pattern, text)

    chunks = []
    step = chunk_size - overlap

    current_page = 1

    for index, section in enumerate(sections):
        if not section.strip():
            continue

        if index % 2 == 1:
            current_page = int(section)
            continue

        words = section.split()

        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]

            if not chunk_words:
                break

            chunks.append({
                "content": " ".join(chunk_words),
                "page_number": current_page
            })

            if start + chunk_size >= len(words):
                break

    return chunks
