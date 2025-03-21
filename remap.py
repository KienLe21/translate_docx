import os
import json
import zipfile
import shutil
from lxml import etree

# Khai báo namespace đầy đủ
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
}

def update_document_xml(extracted_folder, translated_file):
    """Map nội dung đã dịch vào file document.xml, thay thế bằng 1 <w:t> duy nhất mỗi đoạn."""
    
    document_xml_path = os.path.join(extracted_folder, "word/document.xml")
    if not os.path.exists(document_xml_path):
        raise FileNotFoundError("Không tìm thấy document.xml!")

    # Đọc nội dung file XML
    with open(document_xml_path, "r", encoding="utf-8") as f:
        xml_data = f.read()

    # Parse XML với lxml (tự động nhận namespace)
    root = etree.fromstring(xml_data.encode("utf-8"))

    # Đọc nội dung dịch
    with open(translated_file, "r", encoding="utf-8") as f:
        translated_paragraphs = json.load(f)

    paragraphs = root.findall(".//w:p", NAMESPACES)

    num_translated = len(translated_paragraphs)
    num_paragraphs = len(paragraphs)

    print(f"📄 Số đoạn văn bản gốc: {num_paragraphs}")
    print(f"🌍 Số đoạn dịch: {num_translated}")

    # Chỉ map nội dung vào số đoạn tương ứng
    for i in range(min(num_translated, num_paragraphs)):
        p = paragraphs[i]
        translated = translated_paragraphs[i]

        # Xóa tất cả <w:r> cũ trong đoạn văn
        for r in p.findall(".//w:r", NAMESPACES):
            p.remove(r)

        # Tạo mới một <w:r> và <w:t> duy nhất
        new_r = etree.SubElement(p, f"{{{NAMESPACES['w']}}}r")
        rPr = etree.SubElement(new_r, f"{{{NAMESPACES['w']}}}rPr")
        new_t = etree.SubElement(new_r, f"{{{NAMESPACES['w']}}}t")
        new_t.text = translated["text"]
        new_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")  # Giữ khoảng trắng

        # Áp dụng định dạng của đoạn dịch
        if translated.get("bold", False):
            etree.SubElement(rPr, f"{{{NAMESPACES['w']}}}b")  # Đánh dấu in đậm
        
        if translated.get("color"):
            color_elem = etree.SubElement(rPr, f"{{{NAMESPACES['w']}}}color")
            color_elem.set(f"{{{NAMESPACES['w']}}}val", translated["color"])

    # Chuyển ns0: về w:
    xml_str = etree.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
    xml_str = xml_str.replace("ns0:", "w:")

    # Ghi file document.xml mới
    with open(document_xml_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

def create_docx_from_zip(extracted_folder, output_docx):
    """Nén lại thư mục thành file .docx"""
    zip_filename = output_docx.replace(".docx", ".zip")

    # Nén thư mục thành file .zip
    shutil.make_archive(zip_filename.replace(".zip", ""), 'zip', extracted_folder)

    # Đổi tên file .zip thành .docx
    os.rename(zip_filename, output_docx)
    print(f"✅ File {output_docx} đã được tạo thành công!")

if __name__ == "__main__":
    extracted_folder = "unzipped_content"  # Thư mục chứa XML đã giải nén
    translated_json = "translated_texts.json"  # File JSON chứa nội dung dịch
    output_docx = "output.docx"  # File đầu ra

    print("🔄 Đang cập nhật nội dung dịch vào document.xml...")
    update_document_xml(extracted_folder, translated_json)

    print("📦 Đang đóng gói thành file .docx...")
    create_docx_from_zip(extracted_folder, output_docx)

    print("🎉 Hoàn thành! File đầu ra:", output_docx)