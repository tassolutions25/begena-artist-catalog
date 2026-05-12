import docx
doc = docx.Document('የበገና መዝሙር ግጥሞች2.docx')
found = False
for i, p in enumerate(doc.paragraphs):
    li = p.paragraph_format.left_indent
    ls = len(p.text) - len(p.text.lstrip(' '))
    if (li is not None and li.pt > 5) or ls > 2:
        print(f"Para {i}: LeftIndent={li.pt if li else 'None'}, Spaces={ls}, Text={p.text[:30]}")
        found = True
if not found:
    print("No indented paragraphs found.")
