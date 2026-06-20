from reportlab.pdfgen import canvas

c = canvas.Canvas("documents/sample.pdf")

c.drawString(100, 750, "Artificial Intelligence is transforming industries.")
c.drawString(100, 730, "Machine learning enables computers to learn from data.")
c.drawString(100, 710, "Retrieval-Augmented Generation combines vector databases with language models.")

c.save()

print("sample.pdf created successfully!")