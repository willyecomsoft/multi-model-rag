import pypdfium2
import base64
import pypdfium2.raw as pdfium_c

#path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\TT_AXM_CFC_250305 明基健康生活_發票底稿出貨應收作業_v00.pdf"
path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\605385_112Q4_合併_完稿財報-電子書.pdf"
#path = "/Users/willy/Desktop/project/Couchbase/TechmanRobot/OneDrive_1_2025-3-28/605385_112Q4_合併_完稿財報-電子書.pdf"
#path = "/Users/willy/Desktop/project/Couchbase/multi-model-rag/doc/ai_workshop_with_couchbase.pdf"

pdf_reader = pypdfium2.PdfDocument(path)
# bookmarks = [
#   bookmark
#   for bookmark in pdf.get_toc()
# ]

# print(bookmarks)

for page_number, page in enumerate(pdf_reader):
    if page_number == 52:
        #print(page)
        
        text_page = page.get_textpage()
        content = text_page.get_text_range()
        print(content)

        images = page.get_objects(
            filter = (pdfium_c.FPDF_PAGEOBJ_IMAGE, )
        )
        images = list(images)

        for j, image in enumerate(images):
            image.extract(f"./{j}" , fb_format="png")
            print(image.get_size())

    