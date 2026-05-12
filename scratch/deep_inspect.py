import docx
doc = docx.Document('የበገና መዝሙር ግጥሞች2.docx')
for i in range(2, 10):
    p = doc.paragraphs[i]
    li = p.paragraph_format.left_indent.pt if p.paragraph_format.left_indent else 0
    fi = p.paragraph_format.first_line_indent.pt if p.paragraph_format.first_line_indent else 0
    al = p.alignment
    print(f"P{i}: L={li} F={fi} A={al}")
