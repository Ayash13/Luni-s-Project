import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Precompiled regex patterns
patterns = {
    "date": re.compile(r'(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{2,4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}\s+\w{3}\s+\d{2,4})'),
    "time": re.compile(r'\b\d{1,2}:\d{2}(:\d{2})?\b'),
    "receipt_number": re.compile(r'\b(No|Nomor)\b'),
    "address": re.compile(r'\b(Jalan|Jl\.?|JL\.?|JUN\.?|JLN\.?|JK\.?)\b'),
    "quantity_product": re.compile(r'^\d+\s+[^\d]+\s+(\d{1,3}(,\d{3})*(\.\d{2})?)$'),
    "price": re.compile(r'\bRp\b|\d{1,3}(,\d{3})*(\.\d{2})?'),
}

non_product_terms = {"Subtotal", "Total", "Payment", "Cash", "Change", "Harga", "PPN", "Terima Kasih",
                    "Pembayaran", "Nomor", "Tax", "Discount", "Grand Total", "Dibayar", "Kembali", 
                    "Total Item", "Bill Num", "Order Id", "Telp.", "Tele.", "Tlp", "Telp", "Tlp.", "Tele"}

def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')
    img = ImageEnhance.Contrast(img).enhance(2)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return ImageOps.autocontrast(img)

def parse_receipt(lines):
    header, date_info, address_info, products = [], [], [], []
    receipt_number = None
    in_product_section = False

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Check if line is an address or receipt number
        if patterns["address"].search(line):
            address_info.append(line)
        elif patterns["receipt_number"].search(line):
            receipt_number = line
        elif patterns["date"].search(line):
            date_info.append(line)
            if i + 1 < len(lines) and patterns["time"].search(lines[i + 1].strip()):
                date_info.append(lines[i + 1].strip())
        
        # If line contains a non-product term, mark the end of the product section
        elif any(term.lower() in line.lower() for term in non_product_terms):
            in_product_section = False
            continue

        # If a price or quantity appears, assume we’re in the product section
        elif patterns["quantity_product"].match(line) or patterns["price"].search(line):
            in_product_section = True
            products.append(line)

        # Use the product section context to classify nearby lines
        elif in_product_section:
            products.append(line)
        else:
            # If not in the product section and no specific patterns match, classify as header
            header.append(line)

    return header, date_info, receipt_number, address_info, products

# Function to parse individual product lines for quantity, product name, and price
def parse_line(line):
    result = {"quantity": None, "product": None, "price": None}
    quantity_pattern = r'\b\d{1,2}\b'
    price_pattern = r'(\d{1,3}(,\d{3})*(\.\d{2})?)$'

    # Find quantity
    quantity_match = re.search(quantity_pattern, line)
    if quantity_match:
        result["quantity"] = int(quantity_match.group())

    # Find price
    price_match = re.search(price_pattern, line)
    if price_match:
        result["price"] = price_match.group().replace(",", "")

    # Extract product name
    product_text = re.sub(quantity_pattern, "", line)
    product_text = re.sub(price_pattern, "", product_text)
    result["product"] = product_text.strip()

    return result

def process_receipt(image_path):
    img = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)
    lines = text.splitlines()


    header, date_info, receipt_number, address_info, products = parse_receipt(lines)
    parsed_products = [parse_line(product) for product in products]  # Parse each product line

    print("Header Information:", header)
    print("\nDate Information:", date_info)
    print("\nReceipt Number:", receipt_number)
    print("\nAddress Information:", address_info)
    print("\nProducts Detected:")
    for product in parsed_products:
        print(f"  Quantity: {product['quantity']}, Product: '{product['product']}', Price: {product['price']}")

# Run the main function
# process_receipt('struk/6.-tampilan-dari-cetak-struk.jpg')
# process_receipt('struk\contoh-tampilkan-no-struk-kpandroid-1.jpg')
process_receipt('struk\Dfzj8LIU8AAki-Z.jpg')
# process_receipt('struk\IMG_9457.JPG')
# process_receipt('struk\IMG_9458.JPG')
# process_receipt('struk\img_20190511_084303.webp')
# process_receipt('struk\IMG-20201107-WA0013.jpg')
# process_receipt('struk\jasprint_struk_resto_indonesia_1671873431_4be5b5e0_progressive.jpg')
# process_receipt('struk\photo_2024-11-11_14-24-21.jpg')
# process_receipt('struk\struk1.jpg')
# process_receipt('struk\strukkk1.jpg')
# process_receipt('struk\strukkk2.jpg')
# process_receipt('struk\strukkk3.jpg')