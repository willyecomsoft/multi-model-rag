import pdfplumber

path = r"C:\Users\w1232_rxxlb\OneDrive\桌面\Couchbase_PoC_materials_TechmanRobot\TT_AXM_CFC_250305 明基健康生活_發票底稿出貨應收作業_v00.pdf"

with pdfplumber.open(path) as pdf:
    for page in pdf.pages:
        print("///////////////////")
        tables = page.extract_tables()
        for table in tables:
            print("------------------------")
            for row in table:
                print(row)
