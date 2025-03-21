import json
import websocket
import subprocess
import nltk
from extract import extract_paragraphs_with_metadata

#nltk.download("punkt_tab")
from nltk.tokenize import sent_tokenize

def split_text_into_sentences(texts):
    """Tách từng đoạn văn thành danh sách câu."""
    return [sent_tokenize(text) for text in texts]

def on_message(ws, message):
    """Nhận phản hồi từ server, lưu và chạy ánh xạ lại XML"""
    response = json.loads(message)

    with open("translated_output.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, ensure_ascii=False)
    
    print("Saved translated output to translated_output.json")

    # Gọi script remap.py để ánh xạ vào file XML
    subprocess.run(["python3", "remap.py"], check=True)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed.")

def on_open(ws):
    """Gửi dữ liệu khi mở kết nối"""
    texts, metadata = extract_paragraphs_with_metadata("unzipped_content")
    
    if not texts:
        print("No message to send.")
        ws.close()
        return
    
    # Chia nhỏ đoạn văn thành các câu
    sentence_lists = split_text_into_sentences(texts)

    # Gửi danh sách câu cần dịch thay vì đoạn văn bản gốc
    data = json.dumps({
        "texts": sentence_lists,
        "metadata": metadata
    })
    ws.send(data)
    print("Sent:", data)

# Khởi tạo kết nối WebSocket
ws = websocket.WebSocketApp("ws://localhost:8765",
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()
