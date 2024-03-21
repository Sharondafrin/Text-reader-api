import os
import base64
import numpy as np
import time
import shutil
from io import BytesIO 
from PIL import Image
import pytesseract
import warnings
from flask import Flask, jsonify, request
from flask_cors import CORS
from scripts.utils import *

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
logger_path = r'./logs/text-reader.log'

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
warnings.filterwarnings("ignore")

# Archive Log Files

if os.path.exists(logger_path):
    time_now = time.time()
    if time_now - os.path.getctime(logger_path) > 6*30*24*3600:
        archive_dir = os.path.join(os.path.dirname(logger_path), 'archive')
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        shutil.move(logger_path, os.path.join(archive_dir, 'text-reader-' + str(int(time_now))))


logging.basicConfig(
    format='%(levelname)s: %(asctime)s - %(message)s',
    filename=logger_path,
    level=logging.INFO
)

application = Flask(__name__)
CORS(application)
logging.info('Service Restarted!')


@application.route('/', methods=['GET', 'POST'])
def test():
    return 'Service is Up and Running. Please Use /transcript'


@application.route('/transcript', methods=['GET', 'POST'])
def get_transcript():

    if request.method == 'POST':
        try:
            arguments = request.json

            encoded_image = arguments.get('image')
            bounding_boxes = arguments.get('bbox')
            class_name = arguments.get('class')
            language = arguments.get('language').lower() if 'language' in arguments else 'eng'
            language = 'eng' if not language else language

            image_bytes = base64.b64decode(encoded_image)

            image_buffer = Image.open(BytesIO(image_bytes))

            image = np.array(image_buffer)

            img_height, img_width, _ = image.shape

            response = {}

            for bbox in bounding_boxes:
                key, xmin, ymin, xmax, ymax = bbox
                xmin = int(xmin * img_width)
                xmax = min(int(xmax * img_width), img_width)
                ymin = int(ymin * img_height)
                ymax = min(int(ymax * img_height), img_height)

                text = pytesseract.image_to_string(image[ymin: ymax, xmin: xmax, :],
                                                   lang=language, config='--psm 10').replace('\n', ' ')
                text = text.strip()

                if class_name in ['netAmount', 'vatAmount', 'grossAmount'] and key == 'value':
                    response[key] = amount_extraction(text)
                elif class_name in ['invoiceDate', 'invoiceDueDate'] and key == 'value':
                    response[key] = date_extraction(text)
                elif class_name == 'paymentReference' and key == 'value':
                    response[key] = text.upper()
                elif class_name == 'swift' and key == 'value':
                    text = validate_transcript(text)
                    response[key] = text.upper()
                elif class_name in ('bankBranchCode', 'bankAccountNumber', 'vendorVat', 'iban') and key == 'value':
                    response[key] = validate_transcript(text)
                else:
                    response[key] = text

            logging.info('Transcript generated: {}'.format(response))

        except Exception as err:
            logging.error('Error occurred: %s' % err)
            response = {
                'label-text': '', 'value': ''
            }
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=3034, debug=True)
