
import json
import gradio as gr

# Load memory from JSONL
def load_memory(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

# Search memory by keyword in topic, user_input, or deeja_response
def search_memory(keyword, filepath="memory_chat2025.jsonl"):
    keyword = keyword.lower()
    memory = load_memory(filepath)
    results = [
        f"🧠 {item['memory_id']} | {item['topic']}\n"
        f"👤 {item['user_input']}\n"
        f"🤖 {item['deeja_response']}\n"
        f"🎯 Intent: {item['intent']} | ❤️ Sentiment: {item['sentiment']}\n"
        "--------------------------------------------------"
        for item in memory
        if keyword in item['user_input'].lower() or
           keyword in item['deeja_response'].lower() or
           keyword in item['topic'].lower()
    ]
    return "\n\n".join(results) if results else "No memory found."

# Gradio GUI
def launch_memory_viewer():
    iface = gr.Interface(
        fn=search_memory,
        inputs=gr.Textbox(label="🔍 ค้นหาในความทรงจำของ Deeja", placeholder="พิมพ์คำ เช่น AGI, Archive, export..."),
        outputs=gr.Textbox(label="📚 ผลลัพธ์จาก Deeja Memory", lines=20),
        title="🧠 Deeja Memory Viewer",
        description="สำรวจความทรงจำที่ดีจ้าจำไว้จากบทสนทนา"
    )
    iface.launch()

if __name__ == "__main__":
    launch_memory_viewer()
