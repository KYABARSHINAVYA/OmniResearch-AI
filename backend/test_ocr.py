from multimodal.ocr_agent import extract_text
import os

path = "uploads/test.png"

print("Exists:", os.path.exists(path))
print("Absolute path:", os.path.abspath(path))

text = extract_text(path)

text = extract_text(
    r"C:\Users\ADMIN\Documents\OmniResearch-AI\backend\uploads\test.png"
)

print(text)