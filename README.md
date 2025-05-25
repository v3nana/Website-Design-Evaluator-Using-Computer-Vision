# Website-Design-Evaluator-Using-Computer-Vision

Features
•	Evaluates UI screenshots using OCR + Gemma 3:4B via Ollama
•	Gives score (1–10), strengths, weaknesses, and suggestions
•	Saves results to evaluation_reports/
Requirements
•	Python 3, Pillow, pytesseract, requests
•	Tesseract OCR installed (Windows default path supported)
•	Ollama with gemma3:4b pulled and running
Setup
•	1. Clone the repo
•	2. Install dependencies: pip install pillow pytesseract requests
•	3. Run Ollama: ollama pull gemma3:4b & ollama serve
Usage
•	Place image in test_images/
•	Run: python uiux_evaluator.py test_images/your_image.png
•	Check output in terminal and evaluation_reports/

Educational Purposes Only!!!
