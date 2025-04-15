from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import pytesseract
import os
import fitz  # PyMuPDF
from Generation import generate_summary
import json
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def format_invoice_output(invoices):
    formatted_output = ""
    total_value = 0.0

    for i, invoice in enumerate(invoices, start=1):
        formatted_output += f"<h3>Invoice {i}</h3>"
        formatted_output += "<pre>" + json.dumps(invoice, indent=4) + "</pre>"

        formatted_output += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
        for key, value in invoice.items():
            formatted_output += f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>"
        formatted_output += "</table><br>"

        try:
            total_value += float(invoice.get("Total Amount", 0))
        except:
            pass

    summary_html = (
        f"<h3>Summary</h3>"
        f"<p>Total Invoices: {len(invoices)}<br>"
        f"Total Amount: {total_value:.2f}</p>"
    )
    return formatted_output + summary_html

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    download_link = None

    if request.method == 'POST':
        try:
            if 'documents' not in request.files:
                error = "No files uploaded."
                return render_template('index.html', error=error)

            files = request.files.getlist('documents')
            responses = []

            for file in files:
                filename = file.filename
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img = Image.open(file_path)
                    extracted_text = pytesseract.image_to_string(img)

                elif filename.lower().endswith('.pdf'):
                    text_list = []
                    pdf = fitz.open(file_path)
                    for page in pdf:
                        text_list.append(page.get_text())
                    extracted_text = "\n".join(text_list)

                else:
                    os.remove(file_path)
                    continue  # skip unsupported file

                os.remove(file_path)

                summary_json = generate_summary(extracted_text)
                responses.append(summary_json)

            result = format_invoice_output(responses)

            # Save JSON file for download
            file_id = str(uuid.uuid4())
            json_filename = f"{file_id}.json"
            json_path = os.path.join(UPLOAD_FOLDER, json_filename)

            with open(json_path, "w") as f:
                json.dump(responses, f, indent=4)

            download_link = f"/download/{json_filename}"

        except Exception as e:
            error = f"An error occurred: {str(e)}"

    return render_template('index.html', result=result, error=error, download_link=download_link)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
