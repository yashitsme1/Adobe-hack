import fitz  # PyMuPDF
import os
import json

# Common garbage fragments seen in broken PDFs
GARBAGE_WORDS = {"oposal", "r pr", "quest f", "r proposal", "quest foooor pr", "rfp: r", "reeeequest f"}

def extract_outline_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                y = round(line["bbox"][1], 1)
                merged_text = " ".join(span["text"].strip() for span in line["spans"])
                font_sizes = [span["size"] for span in line["spans"]]
                fonts = [span["font"] for span in line["spans"]]

                cleaned = merged_text.strip().lower()
                if (
                    len(cleaned) < 5
                    or cleaned in GARBAGE_WORDS
                    or not any(c.isalnum() for c in cleaned)
                ):
                    continue

                text_elements.append({
                    "text": merged_text,
                    "font_size": max(font_sizes),
                    "font": fonts[0],
                    "page": page_num + 1,
                    "y": y
                })

    # Sort by page and Y position
    text_elements.sort(key=lambda x: (x["page"], x["y"]))

    # Merge lines that are very close and same font size (less aggressive)
    merged_elements = []
    prev = None
    for el in text_elements:
        merge_threshold = 0.8  # stricter threshold for merging
        if (
            prev
            and el["page"] == prev["page"]
            and abs(el["y"] - prev["y"]) < merge_threshold
            and el["font_size"] == prev["font_size"]
        ):
            prev["text"] += " " + el["text"]
        else:
            if prev:
                merged_elements.append(prev)
            prev = el
    if prev:
        merged_elements.append(prev)

    # Deduplicate
    seen = set()
    unique_elements = []
    for el in merged_elements:
        key = (el["text"].strip().lower(), el["page"])
        if key not in seen:
            seen.add(key)
            unique_elements.append(el)

    # Assign heading levels dynamically for all unique font sizes
    font_sizes = sorted(set(el["font_size"] for el in unique_elements), reverse=True)
    levels = [f"H{i+1}" for i in range(len(font_sizes))]
    size_to_level = {size: level for size, level in zip(font_sizes, levels)}

    # Improved title extraction: concatenate all H1/H2 on page 1
    title_parts = [
        el["text"].strip()
        for el in unique_elements
        if el["page"] == 1 and size_to_level.get(el["font_size"]) in ("H1", "H2")
    ]
    title = " ".join(title_parts).strip()
    if not title and unique_elements:
        title = unique_elements[0]["text"]

    # Final outline: include all heading levels
    outline = []
    for el in unique_elements:
        level = size_to_level.get(el["font_size"])
        if not level:
            continue
        outline.append({
            "level": level,
            "text": el["text"].strip(),
            "page": el["page"]
        })

    return {
        "title": title,
        "outline": outline
    }

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            print(f"Processing {filename}")
            try:
                result = extract_outline_from_pdf(pdf_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    main()
