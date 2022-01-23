import numpy as np
import pandas as pd
from flask import render_template, request
from app import app
from app import cache
from sys import getsizeof


# This route is called at the start of the application
@app.route('/', methods=['GET'])
def start_page():
    return render_template(
        'index.html',
        title='Plotting from Backend'
    )


""" This route receives the excel file uploaded by user and return the rectangle information
    back to the user """


######## Data fetch ############
@app.route('/getdata', methods=['GET', 'POST'])
def data_get():
    if request.method == 'POST':  # POST request
        print(request.get_text())  # parse as text
        return 'OK', 200

    else:  # GET request
        n_rectangles = 10_000_00
        canvasWidth = 5000  # pixels
        canvasHeight = 5000  # pixels
        rectWidth = 150
        rectHeight = canvasHeight / 500

        xMin = np.random.randint(canvasWidth - rectWidth, size=(n_rectangles))
        xMax = xMin + rectWidth
        yMin = np.random.randint(canvasHeight - rectHeight, size=(n_rectangles))
        yMax = yMin + rectHeight

        excelFileFromFrontEnd = np.stack((xMin, xMax, yMin, yMax), axis=1)
        print("Memory size of numpy array in MBs:", round(getsizeof(excelFileFromFrontEnd) / 1024 / 1024, 2))
        return {'data': excelFileFromFrontEnd.tolist()}


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
    # if request.files:
    #     excelFileFromFrontEnd = pd.read_excel(request.files['mdfExcel']).values

    n_rectangles = 10_00000
    canvasWidth = 5000  # pixels
    canvasHeight = 5000  # pixels

    rectWidth = 150
    rectHeight = canvasHeight / 500

    xMin = np.random.randint(canvasWidth - rectWidth, size=(n_rectangles))
    xMax = xMin + rectWidth
    yMin = np.random.randint(canvasHeight - rectHeight, size=(n_rectangles))
    yMax = yMin + rectHeight

    excelFileFromFrontEnd = np.stack((xMin, xMax, yMin, yMax), axis=1)

    # memory size of numpy array in bytes
    print("Memory size of numpy array in MBs:", round(getsizeof(excelFileFromFrontEnd) / 1024 / 1024, 2))

    set_data(excelFileFromFrontEnd)

    return {'data': excelFileFromFrontEnd.tolist()}


""" This route return the indices of the rectangles in side the
    coordinates sent by the user from the front end """


@app.route("/rects_in_selected_area", methods=['POST'])
def get_rects_in_selected_area():
    selectedArea = request.json['selected_area']
    data = get_data()
    # sliceMask = (data[:,1] >= selectedArea[0]) & (data[:,0] <= selectedArea[1]) & (data[:,3]
    # >= selectedArea[2]) & (data[:,2] <= selectedArea[3])
    sliceMask = np.where(np.logical_and.reduce(
        [(data[:, 1] >= selectedArea[0]), (data[:, 0] <= selectedArea[1]), (data[:, 3] >= selectedArea[2]),
         (data[:, 2] <= selectedArea[3])]))
    return {'indexOfRectsInSelectedArea': sliceMask[0].tolist()}


""" cache setters and getters to store and obtain data from the cache"""


def set_data(data):
    cache.set('data', data)


def get_data():
    return cache.get('data')
