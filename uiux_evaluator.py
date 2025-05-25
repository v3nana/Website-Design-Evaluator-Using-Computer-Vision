import base64
import requests
import json
import sys
import os
from PIL import Image
import io
import pytesseract
from datetime import datetime

# Configure Tesseract path (adjust based on your installation)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ollama Configuration
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
VISION_MODEL = "gemma3:4b"  # Using Gemma 3 4B model

# UI/UX Evaluation Rubric and Prompt
UIUX_EVALUATION_PROMPT = """You are an expert UI/UX evaluator for academic purposes. I will provide you with a detailed description of a website interface screenshot, and you need to analyze it based on established HCI and UI/UX principles.

Evaluate the design using these specific criteria:

1. **Layout Clarity and Information Structure** (0-2 points)
2. **Navigation Visibility and Usability** (0-2 points)
3. **Visual Consistency** (0-2 points)
4. **Readability and Accessibility** (0-2 points)
5. **Overall Design Quality** (0-2 points)

**Scoring Scale:**
- 9–10: Outstanding design, adheres to all major UI/UX principles
- 7–8: Solid design with minor usability or consistency issues
- 5–6: Functional but with notable UI/UX flaws
- 3–4: Poorly structured or hard-to-navigate interface
- 1–2: Lacks basic usability and design coherence

**Required Output Format:**
SCORE: [X/10]

STRENGTHS:
- [List strengths]

WEAKNESSES:
- [List weaknesses]

DETAILED FEEDBACK:
[Paragraph feedback]

RECOMMENDATIONS:
1. [Improvement 1]
2. [Improvement 2]
3. [Improvement 3]

Now analyze the website interface based on this description:"""

class UIUXEvaluator:
    def __init__(self, model_name=VISION_MODEL):
        self.model_name = model_name
        self.endpoint = OLLAMA_ENDPOINT
    
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            return f"[OCR Error: {str(e)}]"
    
    def describe_image_layout(self, image_path):
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                text_content = self.extract_text_from_image(image_path)

                description = f"""
Website Interface Analysis:
- Image dimensions: {width}x{height} pixels
- Aspect ratio: {"Landscape" if width > height else "Portrait" if height > width else "Square"}

Text Content Found:
{text_content[:1000] if text_content and not text_content.startswith("[OCR Error") else "No readable text detected"}

Visual Layout Analysis:
- Interface appears to be a {"mobile" if width < 768 else "tablet" if width < 1024 else "desktop"} layout
- Image quality: {"High resolution" if width > 1200 else "Medium resolution" if width > 600 else "Low resolution"}
"""
                return description.strip()
        except Exception as e:
            return f"[ERROR] Image analysis failed: {str(e)}"
    
    def evaluate_website_design(self, image_path):
        try:
            print("[INFO] Analyzing image layout and extracting text...")
            image_description = self.describe_image_layout(image_path)

            full_prompt = UIUX_EVALUATION_PROMPT + "\n\n" + image_description

            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 4096
                }
            }

            print("[INFO] Sending request to Ollama Gemma model...")
            response = requests.post(self.endpoint, json=payload, timeout=600)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No evaluation response received.")
        
        except requests.RequestException as e:
            return f"[ERROR] Ollama API request failed: {str(e)}"
        except Exception as e:
            return f"[ERROR] Evaluation failed: {str(e)}"
    
    def save_evaluation_report(self, evaluation_result, image_path, output_dir="evaluation_reports"):
        try:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            report_filename = f"{base_name}_evaluation_report.txt"
            report_path = os.path.join(output_dir, report_filename)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("UI/UX WEBSITE EVALUATION REPORT\n")
                f.write("=" * 60 + "\n")
                f.write(f"Image: {os.path.basename(image_path)}\n")
                f.write(f"Model: {self.model_name}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(evaluation_result)

            print(f"[INFO] Evaluation report saved to: {report_path}")
            return report_path
        
        except Exception as e:
            print(f"[WARNING] Failed to save report: {str(e)}")
            return None

def validate_image_file(image_path):
    if not os.path.exists(image_path):
        return False, "File does not exist"
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True, "Valid image file"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("=" * 60)
        print("UI/UX Website Evaluation System")
        print("=" * 60)
        print("Usage: python uiux_evaluator.py <image_path>")
        print("\nExample:")
        print("  python uiux_evaluator.py student_website.png")
        print("\nSupported formats: PNG, JPG, JPEG, BMP, GIF")
        print("\nMake sure Ollama is running with Gemma3 model installed:")
        print("  ollama pull gemma3:4b")
        print("  ollama serve")
        print("=" * 60)
        sys.exit(1)

    image_path = sys.argv[1]
    is_valid, message = validate_image_file(image_path)
    if not is_valid:
        print(f"[ERROR] {message}")
        sys.exit(1)

    print("=" * 60)
    print("UI/UX WEBSITE EVALUATION SYSTEM")
    print("=" * 60)
    print(f"Analyzing: {os.path.basename(image_path)}")
    print("=" * 60)

    evaluator = UIUXEvaluator()
    evaluation_result = evaluator.evaluate_website_design(image_path)

    if evaluation_result.startswith("[ERROR]"):
        print(evaluation_result)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(evaluation_result)

    evaluator.save_evaluation_report(evaluation_result, image_path)

if __name__ == "__main__":
    main()
