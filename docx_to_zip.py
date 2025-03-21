import os
import zipfile
import shutil

def convert_and_extract_docx(docx_path, extract_folder):
    """Đổi file .docx thành .zip, rồi giải nén nội dung"""
    zip_path = docx_path.replace(".docx", ".zip")
    
    # Tạo bản sao file với định dạng .zip
    shutil.copy(docx_path, zip_path)
    
    # Giải nén nội dung
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_folder)
    
    print(f"File đã được giải nén vào thư mục: {extract_folder}")
    return extract_folder

# Chạy thử
extracted_folder = convert_and_extract_docx("sample.docx", "unzipped_content")
