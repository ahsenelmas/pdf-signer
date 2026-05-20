import fitz

doc = fitz.open()

page = doc.new_page()

page.insert_text((100, 500), "Student Name: Ayse Selma")
page.insert_text((100, 550), "Signature: __________________")

doc.save("sample.pdf")

doc.close()

print("sample.pdf created successfully")