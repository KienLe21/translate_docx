import json
from transformers import pipeline

# Khởi tạo pipeline dịch
translator = pipeline("translation_en_to_vi", model="VietAI/envit5-translation", max_length=1024)

def translate_texts(input_file, output_file):
    """Dịch các đoạn văn bản từ tiếng Anh sang tiếng Việt và giữ lại định dạng."""
    
    # Đọc dữ liệu từ file JSON
    with open(input_file, "r", encoding="utf-8") as f:
        paragraphs = json.load(f)  # [{text, bold, color}, ...]

    # Trích xuất nội dung văn bản để dịch
    texts_to_translate = [p["text"] for p in paragraphs]

    # Dịch từng đoạn văn bản
    translated_texts = translator(texts_to_translate)

    # Xử lý kết quả dịch để loại bỏ "vi:" nếu có
    translated_paragraphs = []
    for original, translated in zip(paragraphs, translated_texts):
        translated_text = translated["translation_text"].replace("vi: ", "").strip()
        translated_paragraphs.append({
            "text": translated_text,
            "bold": original["bold"],
            "color": original["color"]
        })

    # Lưu kết quả vào file JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated_paragraphs, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_json = "texts.json"  # File JSON từ module extract
    output_json = "translated_texts.json"  # File lưu kết quả dịch

    translate_texts(input_json, output_json)
    print(f"Hoàn thành! Đã lưu kết quả dịch vào {output_json}")
