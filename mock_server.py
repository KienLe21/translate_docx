import json
import asyncio
import websockets
from transformers import pipeline

translator = pipeline("translation_en_to_vi", model="VietAI/envit5-translation", max_length=1024)

async def handle_client(websocket):
    async for message in websocket:
        data = json.loads(message)
        sentence_lists = data.get("texts", [])  # Danh sách các đoạn văn (mỗi đoạn là danh sách câu)
        metadata = data.get("metadata", [])

        # Dịch từng câu
        translated_sentences = [
            [translator(sentence)[0]["translation_text"].replace("vi: ", "", 1) for sentence in sentences]
            for sentences in sentence_lists
        ]

        # Cập nhật metadata với văn bản dịch
        translated_metadata = []
        for meta_paragraph, translated_paragraph in zip(metadata, translated_sentences):
            new_meta_paragraph = []
            for meta, translated_text in zip(meta_paragraph, translated_paragraph):
                new_meta = meta.copy()  # Sao chép metadata gốc
                new_meta["text"] = translated_text  # Cập nhật văn bản dịch
                new_meta_paragraph.append(new_meta)
            translated_metadata.append(new_meta_paragraph)

        # Lưu metadata đã cập nhật vào file mới
        with open("translated_metadata.json", "w", encoding="utf-8") as f:
            json.dump(translated_metadata, f, ensure_ascii=False, indent=2)

        # Gửi lại kết quả qua WebSocket
        response = json.dumps({
            "translated_texts": translated_sentences,
            "metadata": translated_metadata
        })
        await websocket.send(response)

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server is running on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
