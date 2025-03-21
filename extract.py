import os
import json
import xml.etree.ElementTree as ET

def extract_paragraphs(extracted_folder):
    """Trích xuất nội dung từng đoạn văn (<w:p>), gộp các phần tử trong đoạn văn và chọn định dạng của đoạn dài nhất."""
    
    document_xml_path = os.path.join(extracted_folder, "word/document.xml")
    if not os.path.exists(document_xml_path):
        raise FileNotFoundError("Không tìm thấy document.xml trong thư mục giải nén!")

    # Parse XML
    tree = ET.parse(document_xml_path)
    root = tree.getroot()

    # Namespace của Word XML
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    paragraphs = []  # Mảng chứa văn bản hoàn chỉnh của từng đoạn <w:p>

    for p in root.findall(".//w:p", namespaces):
        paragraph_text = ""
        max_bold = False
        max_color = None

        for r in p.findall(".//w:r", namespaces):
            rPr = r.find("w:rPr", namespaces)  # Định dạng chữ
            t = r.find("w:t", namespaces)  # Nội dung chữ
            if t is not None and t.text:
                text_part = t.text.strip()
                paragraph_text += text_part + " "
                
                # Kiểm tra định dạng
                is_bold = rPr is not None and rPr.find("w:b", namespaces) is not None
                color_elem = rPr.find("w:color", namespaces) if rPr is not None else None
                color = color_elem.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val") if color_elem is not None else None
                
                # Chọn định dạng của đoạn dài nhất
                if len(text_part) > len(paragraph_text) / 2:
                    max_bold = is_bold
                    max_color = color

        # Lưu đoạn văn đã gộp
        if paragraph_text.strip():
            paragraphs.append({
                "text": paragraph_text.strip(),
                "bold": max_bold,
                "color": max_color
            })
    
    return paragraphs

def get_text_from_json(json_path):
    """Trích xuất phần text từ file JSON và trả về chuỗi format: "'text1', 'text2', ..." bọc trong dấu ""."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Không tìm thấy file {json_path}!")

    with open(json_path, "r", encoding="utf-8") as f:
        translated_data = json.load(f)

    # Trích xuất danh sách các đoạn văn bản và format đúng yêu cầu
    text_list = [f"'{entry['text']}'" for entry in translated_data if 'text' in entry]

    # Kết hợp thành một chuỗi và bọc trong dấu ""
    formatted_text = f'"{", ".join(text_list)}"'
    
    return formatted_text

def save_to_json(data, filename):
    """Lưu dữ liệu vào file JSON"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    extracted_folder = "unzipped_content"  # Thư mục chứa XML đã giải nén
    texts = extract_paragraphs(extracted_folder)
    
    # Lưu vào file JSON
    save_to_json(texts, "texts.json")
    print("Hoàn thành! Đã lưu texts.json")
