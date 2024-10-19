from flask import Flask, jsonify, request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64

app = Flask(__name__)


def parse_xml(root):
    # Load and parse the XML file
    # tree = ET.parse(file_path)
    # root = tree.getroot()

    # Extract class information
    class_info = []
    
    # Find all classes
    for cls in root.findall('.//Class'):
        class_name = cls.get('Name')
        class_id = cls.get('Id')

        # Skip unnamed classes
        if not class_name:
            continue

        # Check and print Documentation_plain for debugging
        class_description = cls.get('Documentation_plain', default=None)

        # Find all attributes within the class
        attributes = []
        for attr in cls.findall('.//Attribute'):
            #if class_name == "VGR_Adress": set_trace()
            attr_name = attr.get('Name', 'Unnamed Attribute')
            attr_type = attr.find('.//Type/DataType')
            attr_type_name = attr_type.get('Name', 'Unknown') if attr_type is not None else 'Unknown'
            attr_cardinality = attr.get('Multiplicity')#find('.//MultiplicityDetail/Multiplicity')
            #attr_cardinality_value = attr_cardinality.get('Name', 'Unknown') if attr_cardinality is not None else 'Unknown'
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
    return class_info

def extract_instance_inheritance(root):
    # Parse the XML file
    # tree = ET.parse(xml_file)
    # root = tree.getroot()

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
    # tree = ET.parse(xml_file)
    # root = tree.getroot()

    diagram_shapes = []

    # Find all InstanceSpecification elements under the Shapes tag within Diagrams
    for shape in root.findall(".//Diagrams//Shapes//InstanceSpecification"):
        element_id = shape.get('Id', 'No ID')
        element_name = shape.get('Name', 'No Name')
        x = shape.get('X', '0')
        y = shape.get('Y', '0')
        width = shape.get('Width', '50')  # Default width if not specified
        height = shape.get('Height', '50')  # Default height if not specified
        # Store the shape details
        diagram_shapes.append({
            'id': element_name,
            'name': element_name,
            'x': x,
            'y': y,
            'width': width,
            'height': height
        })
    
    return diagram_shapes

import html

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
    <img src="data:image/png;base64,{base64.b64encode(model_diagram).decode('utf-8')}" alt="Beskrivning av modellen" usemap="#modelmap" class="border shadow">
    </div>
    
    <map name="modelmap">
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
        map_area = f'<area shape="rect" coords="{x},{y},{float(x)+float(width)},{float(y)+float(height)}" href="#{idref}" alt="{idref}" name="{name}">'
        html_output += map_area
        
    html_output += "</map>"
    
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
    </div>
    </body>
    </html>
    """

    return html_output

def assemble_data(xml_root, model_diagram, page_header):
    # Parse the XML and extract classes

    
    class_info = parse_xml(xml_root)

    diagram_elements = extract_diagram_shapes(xml_root)

    inheritance = extract_instance_inheritance(xml_root)

    # Generate HTML content with Bootstrap styling
    html_content = generate_html_data(diagram_elements, class_info, inheritance, model_diagram, page_header)
    
    return html_content 

