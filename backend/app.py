from flask import Flask, request, render_template, redirect, jsonify
from zipfile import ZipFile
import io
from pdb import set_trace
from utils import assemble_data

app = Flask(__name__)

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

    if 'file' not in request.files:
        return redirect(request.url)
    
    page_header = request.form.get('header', 'Extraherad Model  - Default Rubrik')  # Get header value from form
    file = request.files['file']
    # Ensure the file is a zip file
    if file and file.filename.endswith('.zip'):
        # Read the uploaded file into memory
        try:
            file_in_memory = io.BytesIO(file.read())
            
            # Process the zip file in memory
            with ZipFile(file_in_memory) as zip_file:
                xml_content = None
                image_content = None
                
                for name in zip_file.namelist():
                    if name.endswith('project.xml'):
                        with zip_file.open(name) as xml_file:
                            xml_content = name
                    elif name.endswith('.png'):
                        with zip_file.open(name) as png_file:
                            image_content = png_file.read()
                
                if xml_content and image_content:
                    # Generate HTML content using the header
                    html_content = assemble_data(xml_content, image_content,page_header)
                    return jsonify({"html": html_content})

        except Exception as e:
            return jsonify({"message": f"Fel omvandling fil: {str(e)}"}), 500
                    
    return "Ogiltig fil. Ladda upp en giltig ZIP fil med project.xml fil."

if __name__ == '__main__':
    app.run(debug=True)
