
import fitz
import sys
import os

def extract_images(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc = fitz.open(pdf_path)
    
    for i in range(len(doc)):
        page = doc[i]
        image_list = page.get_images()
        
        print(f"Page {i+1}: Found {len(image_list)} images")
        
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"page_{i+1}_img_{image_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
                
            print(f"Saved {image_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_assets.py <pdf_path> <output_dir>")
        sys.exit(1)
        
    extract_images(sys.argv[1], sys.argv[2])
