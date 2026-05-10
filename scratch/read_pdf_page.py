import fitz
doc = fitz.open('የበገና መዝሙር ግጥሞች.pdf')
with open('scratch/pdf_page_4.txt', 'wb') as f:
    f.write(doc[4].get_text().encode('utf-8'))
