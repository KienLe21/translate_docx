import os
import zipfile
import shutil
import json
from docx_to_zip import convert_and_extract_docx
from extract import extract_paragraphs, save_to_json, get_text_from_json
from translate import translate_texts
from remap import update_document_xml, create_docx_from_zip

# Định nghĩa đường dẫn file
EXTRACTED_FOLDER = "unzipped_content"  # Thư mục chứa nội dung giải nén
TRANSLATED_JSON = "translated_texts.json"  # File JSON chứa nội dung dịch
OUTPUT_DOCX = "output.docx"  # File DOCX đầu ra

# Bước 1: Giải nén file DOCX
print("📂 Đang giải nén file DOCX...")
convert_and_extract_docx("sample.docx", EXTRACTED_FOLDER)
texts = extract_paragraphs(EXTRACTED_FOLDER)
save_to_json(texts, "texts.json")
print("✅ Hoàn thành! Đã lưu texts.json")

# Đọc và in nội dung từ file JSON
json_texts = get_text_from_json("texts.json")
output_txt_path = "texts.txt"
with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write(json_texts)

print(f"✅ Đã lưu nội dung vào {output_txt_path}")

# Bước 2: Dịch nội dung nếu chưa có file JSON
if not os.path.exists(TRANSLATED_JSON):
    print("🌍 Đang dịch nội dung văn bản...")
    translate_texts(EXTRACTED_FOLDER, TRANSLATED_JSON)
else:
    print("✅ File dịch đã có, bỏ qua bước dịch.")

# Bước 3: Cập nhật nội dung dịch vào document.xml
print("🔄 Đang cập nhật nội dung vào document.xml...")
update_document_xml(EXTRACTED_FOLDER, TRANSLATED_JSON)

# Bước 4: Đóng gói lại thành file DOCX
print("📦 Đang tạo file DOCX đầu ra...")
create_docx_from_zip(EXTRACTED_FOLDER, OUTPUT_DOCX)

print("🎉 Hoàn thành! File DOCX mới:", OUTPUT_DOCX)
