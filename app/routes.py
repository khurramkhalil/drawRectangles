import numpy as np
import pandas as pd
import time
import os
from flask import render_template, request, jsonify
from werkzeug.utils import secure_filename
from app import app
from app import cache
from app.checksum import checksum
from sys import getsizeof


######## Data xhttp ############
@app.route("/change_mdf")
def change_mdf():
    t1 = time.time()

    filename = os.path.join(app.config['DOWNLOAD_FOLDER'], 'example') + '.xlsx'
    # filename = os.path.join(app.config['DOWNLOAD_FOLDER'], 'excel_for_frontend') + '.xlsx'
    # excel.to_excel(filename)
    hash_parent = get_hash()
    hash_parent = checksum(filename, hash_parent)

    print(f'Time taken for data generation {time.time() - t1}')

    return render_template('index.html', title='Plotting from Backend')


# This route is called at the start of the application
@app.route('/', methods=['GET'])
def start_page():
    # change_mdf()
    return render_template('index.html', title='Plotting from Backend')


""" This route receives the excel file uploaded by user and return the rectangle information
    back to the user """


######## Data xhttp ############
@app.route("/upload_mdf", methods=['POST'])
def upload_mdf():
    if request.form:
        print('POST request!!')

    if request.files:
        file = request.files['mdfExcel']
        filename = secure_filename(file.filename)
        f_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(f_name)
        hash_parent = checksum(f_name)
        set_hash(hash_parent)

        print('POST request!!')
        excel_frontend = pd.read_excel(request.files['mdfExcel']).values
        return {'data': excel_frontend.tolist()}


""" This route return the indices of the rectangles in side the
    coordinates sent by the user from the front end """


# ####### Data fetch ############
# @app.route('/getdata', methods=['GET', 'POST'])
# def data_get():
#     if request.files:
#         excelFileFromFrontEnd = pd.read_excel(request.files['mdfExcel']).values
#         dataToList = excelFileFromFrontEnd.tolist()
#         #     data_to_send = {'data': dataToList}
#         #     # return jsonify(excelFileFromFrontEnd.tolist())
#         return jsonify(dataToList)
#     #     return data_to_send
#

# """ cache setters and getters to store and obtain data from the cache"""


def set_hash(hash):
    cache.set('hash', hash)


def get_hash():
    return cache.get('hash')

# def set_data(data):
#     cache.set('data', data)
#
#
# def get_data():
#     return cache.get('data')
#
