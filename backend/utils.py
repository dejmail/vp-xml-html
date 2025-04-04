from flask import Flask, jsonify, request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64
import html
from pdb import set_trace


app = Flask(__name__)


def parse_xml(root):

    # Extract class information
    class_info = []
    class_names = []
    app.logger.info("Parsing the XML file for class information...")
    # Find all classes
    for cls in root.findall('.//Class'):
        
        class_name = cls.get('Name')
        class_id = cls.get('Id')

        # Skip unnamed classes
        if not class_name:
            continue

        app.logger.debug(f"Processing class: {cls.get('Name')}")

        # Check and print Documentation_plain for debugging
        class_description = cls.get('Documentation_plain', default=None)

        # Find all attributes within the class
        attributes = []
        for attr in cls.findall('.//Attribute'):
            attr_name = attr.get('Name', 'Unnamed Attribute')
            attr_type = attr.find('.//Type/DataType')
            attr_type_name = attr_type.get('Name', 'Unknown') if attr_type is not None else 'Unknown'
            attr_cardinality = attr.get('Multiplicity')
            attr_description = attr.get('Documentation', default='Ingen beskrivning tillgänglig')

            attributes.append({
                'Namn': attr_name,
                'Typ': attr_type_name,
                'Kardinalitet': attr_cardinality,
                'Beskrivning': attr_description
            })
        
        # Only add classes that have attributes
        if attributes:
            class_info.append({
                'Class Name': class_name,
                'Class Id' : class_id,
                'Class Description': class_description if class_description else 'Ingen beskrivning tillgänglig',
                'Attributes': attributes
                
            })
            class_names.append(class_name)
    return class_info, class_names

def extract_instance_inheritance(root):

    # Dictionary to store the extracted relationships
    instance_inheritance = {}

    # Find all InstanceSpecification elements
    for instance in root.findall(".//InstanceSpecification"):
        # Extract the MasterView element (child element)
        master_view = instance.find('MasterView/InstanceSpecification')
        master_view_name = master_view.get('Name', 'Unknown') if master_view is not None else 'Unknown'

        # Extract the Class element (parent element)
        classifier = instance.find('Classifiers/Class')
        classifier_name = classifier.get('Name', 'Unknown') if classifier is not None else 'Unknown'

        # Add the relationship in the format: "MasterView Name: Class Name"
        if (master_view_name != 'Unknown') and (classifier_name != 'Unknown'):
            instance_inheritance[classifier.get('Idref')] = f"{master_view_name}: {classifier_name}"
    #print(instance_inheritance)

    return instance_inheritance

def extract_diagram_shapes(root):

    def extract_shapes(shapes):
        diagram_shapes = []
        for shape in shapes:
            diagram_shapes.append({
                'id': shape.get('Name', 'No Name'),
                'name': shape.get('Name', 'No Name'),
                'x': shape.get('X', '0'),
                'y': shape.get('Y', '0'),
                'width': shape.get('Width', '50'),  # Default width if not specified
                'height': shape.get('Height', '50')  # Default height if not specified
            })
        return diagram_shapes

    # Extract InstanceSpecification elements under Diagrams
    diagram_shapes = extract_shapes(root.findall(".//Diagrams//Shapes//InstanceSpecification"))

    # If no shapes found, extract elements under ClassDiagram
    if not diagram_shapes:
        diagram_shapes = extract_shapes(root.findall(".//Diagrams//ClassDiagram//Shapes//Class"))
    
    return diagram_shapes

def extract_paragraphs(html_text, keep_tags=["p", "a"]):

    # Decode HTML entities first
    decoded_html = html.unescape(html_text)
    
    # Parse the decoded HTML content
    soup = BeautifulSoup(decoded_html, "html.parser")
    
    # Find all <p> tags and extract them with their content (including child elements)
    paragraphs = soup.find_all('p')
    
    # Extract the HTML content within <p> tags and return as string
    return ''.join([str(p) for p in paragraphs])

def create_link(header):
    
    if header == None:
        return None
    else:
        splits = header.split(':')
        if splits[0] == '':
            # print(f'empty string, returning second position - {splits[1]}')
            return splits[1].strip()
        else:
            # print(f'returning first position - {splits[0]}')
            return splits[0].strip()
        
def generate_html_data(diagram_elements, 
                       classes, 
                       inheritance,
                       model_diagram,
                       image_extension,
                       page_header):

    html_output = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Extracted Classes</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
    <div class="container">

    <div class="row my-4">
    <h1>{page_header}</h1>
    </div>

    <div class="row my-4">

    """

    if image_extension == 'svg':
        html_output += f"""<img src="data:image/{image_extension}+xml;base64,{base64.b64encode(model_diagram).decode('utf-8')}" alt="Beskrivning av modellen" style="width: 100%; height: auto; position: relative;" usemap="#modelmap" id="modelImage" class="border shadow">"""
    else:
        html_output += f"""<img src="data:image/svg+xml;base64,{base64.b64encode(model_diagram).decode('utf-8')}" alt="Beskrivning av modellen" usemap="#modelmap" class="border shadow">"""
    
    html_output += """</div> 
    

    <svg id="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
        
    """

    # Define the clickable areas based on diagram elements
    for element in diagram_elements:
        idref = element['id']
        x = element['x']
        y = element['y']
        width = element['width']
        height = element['height']
        name = element['name']

        # Use the idref to create a clickable area
        
        map_area = f'''
        <a href="#{idref}"> <rect x="{x}" y="{y}" height="{float(height)}" width="{float(width)}" fill="transparent" alt="{idref}" name="{name}" style="pointer-events: all;">
            </rect>
        </a>'''
        html_output += map_area
        
    html_output += "</svg>"
    
    # Iterate over each class and create HTML tables
    for cls in classes:

        header = inheritance.get(cls['Class Id'])

        first_class = create_link(header)
        if header is not None:        
            html_output += f"<h2 class='my-2' id='{first_class}'>{header}</h2>"
        else:
            html_output += f"<h2 class='my-2' id='{cls['Class Name']}'>{cls['Class Name']}</h2>"
        html_output += f"<p>{cls['Class Description']}</p>"
        html_output += "<h4>Attribut</h4>"  # Adding "Attribut" as a header above the table
        html_output += "<table class='table table-striped'>"
        html_output += "<thead><tr><th>Namn</th><th>Typ</th><th>Kardinalitet</th><th>Beskrivning</th></tr></thead>"
        html_output += "<tbody>"
        
        for attr in cls['Attributes']:
            sanitised_paragraph = extract_paragraphs(attr['Beskrivning'])
            html_output += (
                f"<tr>"
                f"<td>{attr['Namn']}</td>"
                f"<td>{attr['Typ']}</td>"
                f"<td>{attr['Kardinalitet']}</td>"
                f"<td>{sanitised_paragraph}</td>"
                f"</tr>\n"
            )
        
        html_output += "</tbody></table><br><br>"
    
    html_output += """
    <script>
    document.addEventListener("DOMContentLoaded", () => {
    // Step 1: Get reference to the SVG overlay
    const overlay = document.getElementById("overlay");

    // Step 2: Find all rect elements within the overlay SVG
    const rectElements = overlay.querySelectorAll("rect");

    // Step 3: Iterate through each rect and extract its attributes
    const const_areas = [];
    rectElements.forEach((rect) => {
        const x = parseFloat(rect.getAttribute("x"));
        const y = parseFloat(rect.getAttribute("y"));
        const width = parseFloat(rect.getAttribute("width"));
        const height = parseFloat(rect.getAttribute("height"));
        const name = rect.getAttribute("name");  // Assuming you have 'name' attribute

        const_areas.push({ x, y, width, height, name });
    });

    console.log("Initial areas from overlay:", const_areas);

    // References to the image and SVG overlay
    const img = document.getElementById('modelImage');
    const svg = document.getElementById('overlay');

    // Function to create the visual overlay and clickable SVG shapes
    function drawSvgOverlay() {
        if (img && svg) {
            // Get the bounding box of the image
            const imgRect = img.getBoundingClientRect();

            // Set SVG overlay dimensions to match the image
            svg.setAttribute('width', imgRect.width);
            svg.setAttribute('height', imgRect.height);
            svg.style.width = imgRect.width + "px";
            svg.style.height = imgRect.height + "px";
            svg.style.left = imgRect.left + "px";
            svg.style.top = imgRect.top + "px";

            // Calculate scaling factors based on the current image size vs original size
            const scaleX = imgRect.width / img.naturalWidth;
            const scaleY = imgRect.height / img.naturalHeight;

            // Clear the existing SVG elements
            svg.innerHTML = '';

            // Iterate over each area and add corresponding SVG elements
            const_areas.forEach(area => {
                const scaledX = area.x * scaleX;
                const scaledY = area.y * scaleY;
                const scaledWidth = area.width * scaleX;
                const scaledHeight = area.height * scaleY;

                const rectElement = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                rectElement.setAttribute("x", scaledX);
                rectElement.setAttribute("y", scaledY);
                rectElement.setAttribute("width", scaledWidth);
                rectElement.setAttribute("height", scaledHeight);
                rectElement.setAttribute("fill", "transparent");
                // rectElement.setAttribute("stroke", "red");
                // rectElement.setAttribute("stroke-width", "2");

                // Create a hyperlink element if needed
                const linkElement = document.createElementNS("http://www.w3.org/2000/svg", "a");
                linkElement.setAttribute("href", area.href || `#${area.name}`);
                linkElement.appendChild(rectElement);

                svg.appendChild(linkElement);
            });
        }
    }

    // Ensure overlay is drawn after image has loaded
    img.addEventListener('load', drawSvgOverlay);
    
    // Recalculate and redraw the overlay on window resize
    window.addEventListener('resize', drawSvgOverlay);

    // Draw the overlay after the DOM content is fully loaded and image is available
    if (img.complete) {
        drawSvgOverlay(); // Draw immediately if the image is already loaded
    }
});
</script>
"""

    html_output += """
    </div>
    </body>
    </html>
    """

    return html_output

def assemble_data(xml_root, model_diagram, image_extension, page_header):
    # Parse the XML and extract classes

    
    class_info, class_names = parse_xml(xml_root)

    diagram_elements = extract_diagram_shapes(xml_root)

    inheritance = extract_instance_inheritance(xml_root)

    # Generate HTML content with Bootstrap styling
    html_content = generate_html_data(diagram_elements, class_info, inheritance, model_diagram, image_extension, page_header)
    
    return html_content, class_names

