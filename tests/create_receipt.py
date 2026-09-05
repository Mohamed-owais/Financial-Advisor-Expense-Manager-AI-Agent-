from PIL import Image, ImageDraw, ImageFont

text = '''MCDONALD'S
Madurai Central Store

Date: 2024-09-05
Time: 14:30

Item Details:
Big Mac                    ₹250.00
Coca-Cola 500ml            ₹60.00
French Fries (Large)       ₹80.00

Subtotal:                  ₹390.00
Tax (GST 5%):              ₹19.50

Total Amount:              ₹409.50

Payment Method: Card'''

img = Image.new('RGB', (600, 500), color='white')
d = ImageDraw.Draw(img)
d.text((20, 20), text, fill='black')
img.save('test_receipt.jpg')
print('✅ test_receipt.jpg created')