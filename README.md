<<<<<<< HEAD
# Adobe-hack
=======
# Adobe Hackathon 2025 – Round 1A

## Objective

Extract structured outlines from a PDF:
- Title (from largest font on page 1)
- Headings: H1, H2, H3 with page number

## Approach

- Used PyMuPDF to extract text spans from each PDF page
- Merged lines using spans, recorded font sizes, bold flags, and page numbers
- Assigned H1, H2, H3 based on top 3 font sizes
- Title was selected based on the largest font size on page 1
- Deduplicated repeated headings
- Output saved in required JSON format

## How to Build & Run

```bash
docker build --platform linux/amd64 -t dotreader:round1a .
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none dotreader:round1a
>>>>>>> dab9ecf (Initial commit)
