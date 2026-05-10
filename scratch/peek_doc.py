import docx

doc = docx.Document('የበገና መዝሙር ግጥሞች.docx')
with open('scratch/peek_output.txt', 'w', encoding='utf-8') as f:
    for i, para in enumerate(doc.paragraphs[:500]):
        indent = para.paragraph_format.left_indent
        if indent:
            indent_val = indent.pt
        else:
            indent_val = 0
        f.write(f"Para {i}: Indent={indent_val}, Text='{para.text}'\n")
