import docx
doc = docx.Document('የበገና መዝሙር ግጥሞች2.docx')
with open('scratch/check_indented_text.txt', 'w', encoding='utf-8') as f:
    for i in [177, 178, 214]:
        p = doc.paragraphs[i]
        f.write(f"Para {i}: Indent={p.paragraph_format.left_indent.pt if p.paragraph_format.left_indent else 'None'}, Text={p.text}\n")
