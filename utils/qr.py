import qrcode
import os

def generate_qr(data):
    # Make sure the directory exists
    qr_dir = 'static/qrcodes'
    os.makedirs(qr_dir, exist_ok=True)

    # Generate QR code
    img = qrcode.make(data)
    file_path = os.path.join(qr_dir, f"{data}.png")
    img.save(file_path)
    return file_path