from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from svglib.svglib import svg2rlg  # Import to handle SVG files
from reportlab.graphics import renderPDF  # To render SVG on the PDF
import pandas as pd
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics
from io import BytesIO



def draw_svg(c, svg_path, x, y, width, height):
    """Helper function to draw and resize an SVG."""
    # Load the SVG drawing
    drawing = svg2rlg(svg_path)
    
    # Get original dimensions
    original_width = drawing.width
    original_height = drawing.height

    # Calculate scaling factors
    scale_x = width / float(original_width)
    scale_y = height / float(original_height)
    
    # Use the smaller scale to preserve aspect ratio
    scale = min(scale_x, scale_y)

    # Apply the scaling to the drawing
    drawing.width = original_width * scale
    drawing.height = original_height * scale
    drawing.scale(scale, scale)

    # Render the scaled SVG at the specified position
    renderPDF.draw(drawing, c, x, y)
    
    
# Image paths
signature_image = "C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/assets/img/pdf_elements/sig.png"  # Load the signature image
watermark_path = "C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/assets/img/pdf_elements/datos_watermark.png"  # Path to watermark image
svg_logo_path = "C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/assets/img/pdf_elements/datosbb.svg"  # Path to the SVG logo

def generate_quote(buffer, svg_logo_path, company_details, client_details, receipt_info, items, totals, watermark_path):
    # Create a canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    spartan_regular = ttfonts.TTFont('Spartan', "C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/fonts/League_Spartan/static/LeagueSpartan-Light.ttf")
    pdfmetrics.registerFont(spartan_regular)

    spartan_bold = ttfonts.TTFont('Spartan-Bold', "C:/Users/Timothy/Desktop/Datos/DatosWorld/static/datos/fonts/League_Spartan/static/LeagueSpartan-ExtraBold.ttf")
    pdfmetrics.registerFont(spartan_bold)

    # Set transparency (alpha value) for the watermark
    c.saveState()  # Save the current graphics state
    c.setFillAlpha(0.6)  # Set transparency level (1.0 is opaque, 0.0 is fully transparent)

    # Add watermark image at the center of the page
    watermark_width = width  # Adjust the size of the watermark image (width)
    watermark_height = height  # Adjust the size of the watermark image (height)
    
    # Calculate position for centering
    x_position = (width - watermark_width) / 2
    y_position = (height - watermark_height) / 2

    # Draw the watermark (optional transparency can be set using c.setFillAlpha if needed)
    c.drawImage(watermark_path, x_position, y_position, width=watermark_width, height=watermark_height, mask='auto')

    # Add SVG Logo (resized with aspect ratio)
    draw_svg(c, svg_logo_path, 20, height - 115, 180, 90)

    # Company Details (left side under logo)
    c.setFillColor(colors.black)
    c.setFont("Spartan-Bold", 10)
    c.drawString(40, height - 220, "From")
    c.setFont("Spartan-Bold", 14)
    c.drawString(40, height - 240, company_details['name'])
    c.setFont("Spartan", 10)
    c.drawString(40, height - 270, company_details['email'])
    c.drawString(40, height - 285, company_details['phone'])
    c.drawString(40, height - 300, company_details['address'])

    # Receipt Title and Info (right-aligned with 40 units margin)
    c.setFillColor(colors.navy)
    c.setFont("Spartan-Bold", 28)
    c.drawRightString(width - 40, height - 60, "Quotation")  # Right-align the title with 40-unit margin


    c.setFillColor(colors.black)
    c.setFont("Spartan", 10)
    
    # Invoice no.
    c.drawString(width - 215, height - 100, "Invoice no: ")
    c.drawRightString(width - 40, height - 100, f"{receipt_info['number']}")  # Right-align invoice number
    
    # Invoice date
    c.drawString(width - 215, height - 115, "Invoice date: ")
    c.drawRightString(width - 40, height - 115, f"{receipt_info['date']}")  # Right-align invoice date
    
    # Due date
    c.drawString(width - 215, height - 130, "Due: ")
    c.drawRightString(width - 40, height - 130, f"{receipt_info['due_date']}")  # Right-align due date


    # Client Details (right side under receipt title, aligned right starting from 40 width)
    x_position = width - 40  # Set the x position so text aligns to the right but leaves 40 units of space on the right side
    
    c.setFont("Spartan-Bold", 10)
    c.drawRightString(x_position, height - 220, "Bill to")
    c.setFont("Spartan-Bold", 14)
    c.drawRightString(x_position, height - 240, client_details['name'])
    c.setFont("Spartan", 10)
    c.drawRightString(x_position, height - 270, client_details['email'])
    c.drawRightString(x_position, height - 285, client_details['phone'])
    c.drawRightString(x_position, height - 300, client_details['address'])


    # Itemized Table (center)
    table_data = [["DESCRIPTION", "RATE (K)", "QTY", "TAX", "DISC", "AMOUNT (K)"]]
    
    # Add the rows from the items list
    for item in items:
        table_data.append([item['description'], f"{item['rate']}", str(item['qty']), f"{item['tax']} %", f"{item['discount']} %", f"{item['amount']}"])
    
    # Define the table style with specific alignments
    table_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Spartan-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    
        # Align the headers
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),     # Description header aligned left
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),   # Rate, Qty, Tax, Disc, Amount headers aligned right
    
        # Align the rows (Description: left, others: right)
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Description column aligned left
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Rate, Qty, Tax, Disc, Amount columns aligned right
    
        # Row styling (remove borders and alternate row colors)
        ('FONTNAME', (0, 1), (-1, -1), 'Spartan'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ])
    
    # Add alternating row colors (white and very light grey)
    for row in range(1, len(table_data)):
        bg_color = colors.whitesmoke if row % 2 == 0 else colors.white
        table_style.add('BACKGROUND', (0, row), (-1, row), bg_color)
    
    # Set the total table width and colWidths to ensure 40 units on both sides
    total_table_width = width - 80  # Total width is page width minus 80 (40 units on both sides)
    colWidths = [total_table_width * 0.35, total_table_width * 0.13, total_table_width * 0.13, total_table_width * 0.13, total_table_width * 0.13, total_table_width * 0.13]  # Adjust each column width
    
    # Create the table with the new column widths
    table = Table(table_data, colWidths=colWidths)
    table.setStyle(table_style)
    
    # Calculate x_position for equal left and right margins
    x_position = 40
    
    # Render the table
    table.wrapOn(c, width, height)
    table.drawOn(c, x_position, height - 420)



    # Payment instructions (left)
    c.setFont("Spartan-Bold", 11)
    c.drawString(40, height - 535, "Payment instruction")
    c.setFont("Spartan", 10)
    c.drawString(40, height - 555, company_details['payment_info'])

    # Notes section
    c.setFont("Spartan-Bold", 11)
    c.drawString(40, height - 610, "Notes")
    c.setFont("Spartan", 10)
    c.drawString(40, height - 630, company_details['notes'])

    c.setFont("Spartan", 8)
    c.drawString(40, 40, f"Issued on {receipt_info['created_on'].strftime('%Y/%m/%d %H:%M:%S')}")

    # Total breakdown (right-aligned only for ZMW values)
    c.setFont("Spartan-Bold", 11)
    c.drawString(width - 210, height - 535, "Subtotal: ")
    c.drawRightString(width - 40, height - 535, f"{totals['subtotal']}")  # Right-align subtotal
    
    c.setFont("Spartan", 10)
    c.drawString(width - 210, height - 555, "Discount: ")
    c.drawRightString(width - 40, height - 555, f"{totals['discount']}")  # Right-align discount
    
    c.drawString(width - 210, height - 570, "Shipping Cost: ")
    c.drawRightString(width - 40, height - 570, f"{totals['shipping']}")  # Right-align shipping cost
    
    c.drawString(width - 210, height - 585, "Sales Tax: ")
    c.drawRightString(width - 40, height - 585, f"{totals['tax']}")  # Right-align sales tax
    
    c.setFont("Spartan-Bold", 11)
    c.drawString(width - 210, height - 610, "Total: ")
    c.drawRightString(width - 40, height - 610, f"{totals['total']}")  # Right-align total
    
    c.setFont("Spartan", 10)
    c.drawString(width - 210, height - 630, "Amount paid: ")
    c.drawRightString(width - 40, height - 630, f"{totals['paid']}")  # Right-align amount paid
    
    c.setFont("Spartan-Bold", 12)
    c.drawString(width - 210, height - 650, "Balance Due: ")
    c.drawRightString(width - 40, height - 650, f"{totals['balance_due']}")  # Right-align balance due


    c.drawImage(signature_image, width - 210, 80, width=100, height=30, mask='auto')  # Adjust the position and size

    # Save the PDF
    c.showPage()
    c.save()

