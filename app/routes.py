import numpy as np
import pandas as pd
import time
from flask import render_template, request, jsonify, Response
from app import app
from app import cache
from sys import getsizeof


def data_gen():
    t1 = time.time()

    n_rectangles = 25_600_0
    canvas_width = 5000  # pixels
    canvas_height = 5000  # pixels
    rect_width = 150
    rect_height = canvas_height / 500

    x_min = np.random.randint(canvas_width - rect_width, size=(n_rectangles))
    x_max = x_min + rect_width
    y_min = np.random.randint(canvas_height - rect_height, size=(n_rectangles))
    y_max = y_min + rect_height

    excel_for_frontend = np.stack((x_min, x_max, y_min, y_max), axis=1)

    print(f'Time taken for data generation {time.time() - t1}')
    print("Memory size of numpy array in MBs:", round(getsizeof(excel_for_frontend) / 1024 / 1024, 2))
    set_data(excel_for_frontend)


# This route is called at the start of the application
@app.route('/', methods=['GET'])
def start_page():
    data_gen()
    return render_template(
        'index.html',
        title='Plotting from Backend'
    )


""" This route receives the excel file uploaded by user and return the rectangle information
    back to the user """


####### Data fetch ############
@app.route('/getdata', methods=['GET', 'POST'])
def data_get():
    # if request.method == 'POST':
    #     print(request.files['mdfExcel'])
    #     return {}

    if request.files:
        excelFileFromFrontEnd = pd.read_excel(request.files['mdfExcel']).values
        dataToList = excelFileFromFrontEnd.tolist()
        #     data_to_send = {'data': dataToList}
        #     # return jsonify(excelFileFromFrontEnd.tolist())
        return jsonify(dataToList)
    #     return data_to_send


# @app.route('/getdata', methods=['GET', 'POST'])
# def data_get():
#     if request.method == 'POST':  # POST request
#         print(request.get_text())  # parse as text
#         return 'OK', 200
#
#     else:  # GET request
#         excel_data = get_data()
#
#         return jsonify(excel_data.tolist())
#         # return {'data': excel_data.tolist()}
#         # return excel_data
#         # return Response(jsonify(excel_data.tolist()))


'''

          Xhttp                                                    fetch
10^3 => 292, 361, 268, 273, 286                            1.56, 1.74, 1.66, 2.93, 1.95
10^4 => 352, 351, 372, 352, 357                            12.65, 12.51, 14.24, 14.25, 13.83
10^5 => 1151, 1166, 1135, 1225, 1182                       119, 118, 123, 114, 124, 125
10^6 => 9419, 8959, 8903, 9022, 9046                        1012, 1024, 998, 1011, 939
10^7 =>


Xhttp                     fetch
10^3 => 296           1.968
10^4 => 356           13.496
10^5 => 1171          120
10^6 => 9069          996
'''


######## Data xhttp ############
@app.route("/upload_mdf", methods=['POST'])
def upload_mdf():
    if request.form:
        print('POST request!!')

    if request.files:
        excel_frontend = pd.read_excel(request.files['mdfExcel']).values

        return {'data': excel_frontend.tolist()}


""" This route return the indices of the rectangles in side the
    coordinates sent by the user from the front end """


#
# @app.route("/rects_in_selected_area", methods=['POST'])
# def get_rects_in_selected_area():
#     selectedArea = request.json['selected_area']
#     data = get_data()
#     # sliceMask = (data[:,1] >= selectedArea[0]) & (data[:,0] <= selectedArea[1]) & (data[:,3]
#     # >= selectedArea[2]) & (data[:,2] <= selectedArea[3])
#     sliceMask = np.where(np.logical_and.reduce(
#         [(data[:, 1] >= selectedArea[0]), (data[:, 0] <= selectedArea[1]), (data[:, 3] >= selectedArea[2]),
#          (data[:, 2] <= selectedArea[3])]))
#     return {'indexOfRectsInSelectedArea': sliceMask[0].tolist()}
#
#
# """ cache setters and getters to store and obtain data from the cache"""


def set_data(data):
    cache.set('data', data)


def get_data():
    return cache.get('data')
