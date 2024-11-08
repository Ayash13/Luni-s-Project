import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Load and preprocess the image with additional enhancements
image_path = '/Users/ayash/Coding/Skirpsi Luni/struk/contoh-tampilkan-no-struk-kpandroid-1.jpg'
img = Image.open(image_path)
img = img.convert('L')  # Convert to grayscale
img = ImageEnhance.Contrast(img).enhance(2)  # Increase contrast
img = img.filter(ImageFilter.MedianFilter(size=3))  # Noise reduction
img = ImageOps.autocontrast(img)  # Automatic contrast adjustment

# Perform OCR with optimized config
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(img, config=custom_config)

# Split text into lines
lines = text.splitlines()

# Define enhanced patterns for detecting products, dates, times, receipt numbers, and addresses
patterns = {
    "date": r'(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{2,4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}\s+\w{3}\s+\d{2,4})',
    "time": r'\b\d{1,2}:\d{2}(:\d{2})?\b',  # Matches time formats hh:mm or hh:mm:ss
    "receipt_number": r'\b(No|Nomor)\b',
    "address": r'\b(Jalan|Jl\.?|JL\.?|JUN\.?|JLN\.?|JK\.?)\b',  # Matches variations of "Jalan", "Jl", "JL"
    "quantity_product": r'^\d+\s+[^\d]+\s+(\d{1,3}(,\d{3})*(\.\d{2})?)$',  # Refined to capture quantities and prices
    "price": r'\bRp\b|\d{1,3}(,\d{3})*(\.\d{2})?',  # Supports formats with Rp, comma, and period
}

# Terms to identify non-product sections, including new terms
non_product_terms = [
    "Subtotal", "Total", "Payment", "Cash", "Change", "Harga", "PPN", "Terima Kasih",
    "Pembayaran", "Nomor", "Tax", "Discount", "Grand Total", "Dibayar", "Kembali", "Total Item"
]

# Initialize lists for header, date, receipt number, address, and products
header = []
date_info = []
receipt_number = None
address_info = []
products = []
in_product_section = False

# Detect format (basic format detection based on keywords or structures)
def detect_format(lines):
    for line in lines:
        if re.search(r'\bSuper Indo\b', line, re.IGNORECASE):
            return "supermarket"
        elif re.search(r'\bAyam\b', line, re.IGNORECASE):
            return "restaurant"
    return "general"

# Determine which format we're working with
format_type = detect_format(lines)
print(f"Detected format: {format_type}")

# Process each line with additional logic for date, address, and receipt format adjustments
i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Skip empty lines
    if not line:
        i += 1
        continue

    # Check if the line contains an address
    if re.search(patterns["address"], line, re.IGNORECASE):
        address_info.append(line)
        i += 1
        continue

    # Check if the line contains a receipt number (e.g., starts with "No" or "Nomor")
    if re.search(patterns["receipt_number"], line):
        receipt_number = line
        i += 1
        continue
    
    # Check if the line contains a date format
    if re.search(patterns["date"], line):
        date_info.append(line)
        
        # Check the next line for a time pattern
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.search(patterns["time"], next_line):
                date_info.append(next_line)  # Add time to date information
                i += 2  # Skip to the line after the time
                continue
        
        # Move to the next line if no time pattern is found
        i += 1
        continue

    # Check if the line matches product patterns (quantity + product + price or "Rp" + price format)
    if re.match(patterns["quantity_product"], line) or re.search(patterns["price"], line):
        if any(term in line for term in non_product_terms):
            # Skip lines with non-product terms like "Total", "Subtotal", etc.
            i += 1
            continue
        in_product_section = True
        products.append(line)  # Add the product line
    elif in_product_section:
        # Once we are in the product section, keep adding lines until non-product line is found
        if any(term in line for term in non_product_terms):
            in_product_section = False  # End of product section
        else:
            products.append(line)
    else:
        # If not in the product section, and no date, receipt number, or address is found, consider it as header
        header.append(line)

    # Move to the next line
    i += 1

# Display extracted information
print("Header Information:", header)
print("\nDate Information:", date_info)
print("\nReceipt Number:", receipt_number)
print("\nAddress Information:", address_info)
print("\nProducts Detected:")
for product in products:
    print(product)
