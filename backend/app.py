from flask import Flask, request, render_template, redirect, jsonify
from zipfile import ZipFile
import io
from pdb import set_trace
from utils import assemble_data
from flask_cors import CORS

import xml.etree.ElementTree as ET

import logging


logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()  # You can add FileHandler here too
    ]
)


app = Flask(__name__)
CORS(app)

# Configure upload folder and allowed extensions
ALLOWED_EXTENSIONS = {'xml', 'zip'}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the upload page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():

    if len(request.files) < 2:
        return jsonify({"message": "Behöver project.xml och en modell i SVG format"}), 400
    elif len(request.files) == 2:
        page_header = request.form.get('header', 'Extraherad Model')
    
        for file in request.files:
            
            if file == 'xml':
                try:
                    file_in_memory = io.BytesIO(request.files.get(file).read())        
                
                    tree = ET.ElementTree(ET.fromstring(file_in_memory.read().decode('utf-8')))
                    xml_content = tree.getroot()
                except Exception as e:        
                    print(f"Error occurred: {e}")  # Log the error for debugging
                    return jsonify({"message": f"Fel omvandling av fil: {str(e)}"}), 500
            
            elif file == 'svg':
                image_extension = 'svg'
                image_content = request.files.get(file).read()
                    
        if (xml_content is not None) and (image_content is not None):
                        # Generate HTML content using the header
            html_content, class_names = assemble_data(xml_content, 
                                        image_content, 
                                        image_extension, 
                                        page_header)
            return jsonify({"html": html_content,
                            "classes" : class_names})
                    
    return "Ogiltig fil. Ladda upp en giltig ZIP fil med project.xml fil."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
