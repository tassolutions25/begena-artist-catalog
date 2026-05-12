import docx
doc = docx.Document('የበገና መዝሙር ግጥሞች2.docx')
with open('scratch/indent_check.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(doc.paragraphs[:100]):
        # Check both left_indent and leading spaces
        left_indent = p.paragraph_format.left_indent
        leading_spaces = 0
        for char in p.text:
            if char == ' ': leading_spaces += 1
            else: break
        f.write(f"Para {i}: LeftIndent={left_indent}, LeadingSpaces={leading_spaces}, Text={p.text[:50]}\n")
