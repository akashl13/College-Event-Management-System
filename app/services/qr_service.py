import os

import qrcode
from flask import current_app


def create_registration_qr(registration):
    payload = f"{current_app.config['APP_BASE_URL'].rstrip('/')}/verify/{registration.registration_code}"
    filename = f"{registration.registration_code}.png"
    relative_path = f"qr_codes/{filename}"
    absolute_path = os.path.join(current_app.static_folder, relative_path)
    qrcode.make(payload).save(absolute_path)
    registration.qr_code = relative_path
    return relative_path
