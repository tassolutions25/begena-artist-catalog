import fitz
doc = fitz.open('የበገና መዝሙር ግጥሞች.pdf')
with open('scratch/pdf_first_pages.txt', 'wb') as f:
    for i in range(5):
        f.write(f"--- PAGE {i} ---\n".encode('utf-8'))
        f.write(doc[i].get_text().encode('utf-8'))
