import pymupdf4llm
import json


pdf_path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\TT_AXM_CFC_250305 明基健康生活_發票底稿出貨應收作業_v00.pdf"

# md_text = pymupdf4llm.to_markdown(path)

# print(md_text)

# md_text_images = pymupdf4llm.to_markdown(
#     doc=pdf_path,
#     pages=[4, 4],
#     page_chunks=True,
#     embed_images=True,
#     image_format="jpg",
#     show_progress=True,
# )

md_text_images = pymupdf4llm.to_markdown(
    doc=pdf_path,
    pages=[4, 4],
    page_chunks=True,
    write_images=False,
    image_format="jpg",
    show_progress=True
)

#print(json.dumps(md_text_images))

with open("output.txt", "w", encoding="utf-8") as file:
    # 重定向 print 输出到文件
    print(md_text_images, file=file)
