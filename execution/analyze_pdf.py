
import fitz  # PyMuPDF
import sys
import json

def analyze_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        print(f"Number of pages: {len(doc)}")
        
        analysis = []
        
        for i, page in enumerate(doc):
            page_data = {
                "page_number": i + 1,
                "text": page.get_text(),
                "blocks": page.get_text("blocks"),
                # "colors": get_colors(page) # Advanced: extracting colors might be harder but let's try basic text first
            }
            analysis.append(page_data)
            
        print(json.dumps(analysis, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pdf.py <pdf_path>")
        sys.exit(1)
    
    analyze_pdf(sys.argv[1])
