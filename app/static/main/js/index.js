// console.log("Hi there!")

"use strict"; // This ensures that insecure and incompatible code throws an error. This is ignored in older version of javascript https://www.w3schools.com/js/js_strict.asp
/* for automatically uploading  file without clicking */

const READYSTATE_DONE = 4; // This is returned when the XMLHTTPRequest is complete.
const HTTP_SUCCESS = 200; // 200 is returned when the http is successfully completed at the server.
let excelData = []; // global variable to store data obtained from excel file
// obtaining view port information
const viewPortWidth = document.getElementById('canvaswrapper').offsetWidth;
const viewPortHeight = document.getElementById('canvaswrapper').offsetHeight;
// getting canvas elements
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const xAxisResolution = canvas.width / viewPortWidth;
const yAxisResolution = canvas.height / viewPortHeight;

/**
 * this function sends the uploaded excel file to the server for processing
 *
 */
function submit_file(file) {
    if (file) {
        // generating http request to server for submitting the user uploaded excel file
        console.time("Rectangle Transmit Time: ")
        let fileUploadAjax = new XMLHttpRequest();
        fileUploadAjax.onreadystatechange = function () {
            if (this.readyState == READYSTATE_DONE && this.status == HTTP_SUCCESS) {
                // obtaining data parsed from excel at the backend
                excelData = JSON.parse(this.responseText).data;
                console.timeEnd("Rectangle Transmit Time: ")
            }
        }
        // opening a HTTP POST request at the upload_mdf endpoint
        fileUploadAjax.open("POST", '/upload_mdf', true); // asynchronously send request to update analysis view
        // creating form to carry the user chosen file to the server
        let excelFileFormData = new FormData();
        // adding the user selected file to the form
        excelFileFormData.append("mdfExcel", file.files[0]);
        // sending the form along with the HTTP request.
        fileUploadAjax.send(excelFileFormData);
    }
}


/**
 * some global variables to hold plotting data
 */
let zoomUsingPlotting = false // flag to turn on or off zooming using plotting
let zoomUsingCSS = true // flag to turn on or off zooming using CSS
let xZoomScale = 1; // global variable to hold zoom factor along xaxis
let yZoomScale = 1; // global variable to hold zoom factor along y axis
let xTranslation = 0; // global variable to hold translation along x axis in a zoom
let yTranslation = 0; // global variable to hold translation along y axis in a zoom

/**
 * resets the zoomed plot to its original plot
 */
function resetZoomedPlot() {

    // resetting global scaling and transformation variables
    zoomUsingPlotting = false;
    zoomUsingCSS = true;
    xZoomScale = 1;
    yZoomScale = 1;
    xTranslation = 0;
    yTranslation = 0;

    //setting the css transform matrix to identity
    document.getElementById('canvas').style.transform = "matrix(1,0,0,1,0,0)";

    //obtaining the canvas context and clearing all transformations
    // setTransform sets the tranformation matrix to identity
    document.getElementById('canvas').getContext('2d').setTransform();
    // plotting the data to the original scale
    plotExcelRectangles();

}

function scaleAndTranslateCanvas(xScale, yScale, xTranslation, yTranslation) {
    document.getElementById('canvas').style.transform = 'matrix(' +
        xScale + ',0,0,' +
        yScale + ',' +
        xTranslation + ',' +
        yTranslation +
        ')';
}

/**
 * plots rectangles inside area bounded by a rectangle (xMin,yMin) (xMax,yMax)
 */
function plotRectanglesInSelectedArea(xMin, xMax, yMin, yMax) {
    // starting http Post request to obtain indices of rectangles in selected area
    let getRectsInSelectedAreaAjax = new XMLHttpRequest();
    getRectsInSelectedAreaAjax.onreadystatechange = function () {
        if (this.readyState == READYSTATE_DONE && this.status == HTTP_SUCCESS) {
            // plot rectangles given by indexOfRectsInSelectedArea
            plotRectangles(JSON.parse(this.responseText).indexOfRectsInSelectedArea);
        }
    }
    getRectsInSelectedAreaAjax.open("POST", '/rects_in_selected_area', true);
    getRectsInSelectedAreaAjax.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    // sending bounding coordinates of the selected area to backend.
    getRectsInSelectedAreaAjax.send(JSON.stringify({
        "selected_area": [xMin, xMax, yMin, yMax]
    }));
}

// plot Rectangles stored in excelData given by indices in indexOfRectsInSelectedArea
function plotRectangles(indexOfRectsInSelectedArea) {
    //obtaining canvas to plot the rectangles
    let canvas = document.getElementById('canvas');
    // obtaining the context of the convas to plot the rectangles.
    let context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < indexOfRectsInSelectedArea.length; i++) {

        context.fillStyle = BAND_COLORS[indexOfRectsInSelectedArea[i] % COLOR_LENGTH]; // setting a random fill color for the rectangle
        // plotting filled rectangle on the canvas
        context.fillRect(
            excelData[indexOfRectsInSelectedArea[i]][0],
            excelData[indexOfRectsInSelectedArea[i]][2],
            excelData[indexOfRectsInSelectedArea[i]][1] - excelData[indexOfRectsInSelectedArea[i]][0],
            excelData[indexOfRectsInSelectedArea[i]][3] - excelData[indexOfRectsInSelectedArea[i]][2]
        );
        context.strokeStyle = EDGE_COLORS[indexOfRectsInSelectedArea[i] % COLOR_LENGTH]; // setting a random border color for the rectangle
        // plotting border of rectangle on the canvas
        context.strokeRect(
            excelData[indexOfRectsInSelectedArea[i]][0],
            excelData[indexOfRectsInSelectedArea[i]][2],
            excelData[indexOfRectsInSelectedArea[i]][1] - excelData[indexOfRectsInSelectedArea[i]][0],
            excelData[indexOfRectsInSelectedArea[i]][3] - excelData[indexOfRectsInSelectedArea[i]][2]
        );
    }
}

/**
 * plotting the rectangles obtained from the excel file
 */
function plotExcelRectangles() {
    plotRectangles(
        // The following generates an array starting containing the indices of all elements in excelData
        Array.from(Array(excelData.length), (e, i) => i)
    );
}

/**
 * This function obtains the coordinates with respect to the coordinates
 * of the bounding area of the element on which the cursor posiiton is sought
 */
function getCursorPos(event) {
    // obtaining the bounding area of the target element
    let elementBounds = event.currentTarget.getBoundingClientRect();
    // subtracting the absolute left coordinate of the target element
    // from the cursor position on the actual page
    let x = event.pageX - elementBounds.left,
        y = event.pageY - elementBounds.top;

    // taking care of any offsets due to scrolling on the web page.
    x -= window.pageXOffset;
    y -= window.pageYOffset;
    return [x, y];
}

// getting the ratio of the canvas width pixels to the css width of the canvas
function getXAxisResolution(canvas) {
    let canvasArea = canvas.getBoundingClientRect();
    return canvas.width / canvasArea.width;
}

// getting the ratio of the canvas height pixels to the css height of the canvas
function getYAxisResolution(canvas) {
    let canvasArea = canvas.getBoundingClientRect();
    return canvas.height / canvasArea.height;
}

/**
 * function is called when a user starts selecting the area to be zoomed
 */
function startZoom(event) {
    // obtaining position of the zoom start position
    let zoomStartPos = getCursorPos(event);
    // attaching function that will be called when the user completes
    // selecting the area to be zoomed
    event.currentTarget.addEventListener("mouseup", function endZoom(event) {
        // obtaining the coordinates where the user completed the zoom area selection
        let zoomEndPos = getCursorPos(event);
        // if the zoomed area diagonal is less than 5 pixels then don't zoom
        if (Math.sqrt((zoomEndPos[0] - zoomStartPos[0]) ** 2 + (zoomEndPos[1] - zoomStartPos[1]) ** 2) > 5) {

            // getting top right corner of selected area w.r.t view port.
            let xMin = (Math.min(zoomStartPos[0], zoomEndPos[0]) + xTranslation) / xZoomScale;
            let xMax = (Math.max(zoomStartPos[0], zoomEndPos[0]) + xTranslation) / xZoomScale;
            let yMin = (Math.min(zoomStartPos[1], zoomEndPos[1]) + yTranslation) / yZoomScale;
            let yMax = (Math.max(zoomStartPos[1], zoomEndPos[1]) + yTranslation) / yZoomScale;

            // getting the scaling factors along the x and y axes.
            xZoomScale = viewPortWidth / (xMax - xMin);
            yZoomScale = viewPortHeight / (yMax - yMin);

            // translations across the x and y axis to bring the zoomed area in to view
            // please note that the scaling and translation is done w.r.t to the origin
            // of the view. The origin is at the center of the view at (viewWidth/2,viewHeight/2)
            xTranslation = xMin * xZoomScale;
            yTranslation = yMin * yZoomScale;

            zoomUsingPlotting = (xMax - xMin) * xAxisResolution < viewPortWidth ||
                (yMax - yMin) * xAxisResolution < viewPortHeight;

            if (zoomUsingPlotting) {
                if (zoomUsingCSS) {
                    //setting the css transform matrix to identity
                    context.clearRect(0, 0, canvas.width, canvas.height);
                    document.getElementById('canvas').style.transform = "matrix(1,0,0,1,0,0)";
                    zoomUsingCSS = false;
                }
                // clearing and previous scaling or translation.
                context.setTransform();
                // applying scaling and translation corresponding to the
                // currently selected area
                context.transform(
                    xZoomScale, 0,
                    0, yZoomScale,
                    -xTranslation * xAxisResolution,
                    -yTranslation * yAxisResolution
                );
                // plotting rectangles inside the selected area
                plotRectanglesInSelectedArea(
                    xMin * xAxisResolution,
                    xMax * xAxisResolution,
                    yMin * yAxisResolution,
                    yMax * yAxisResolution
                );
            }

            if (!zoomUsingPlotting) {
                zoomUsingCSS = true;

                scaleAndTranslateCanvas(
                    xZoomScale,
                    yZoomScale,
                    -(1 / 2 * (1 - xZoomScale) * viewPortWidth + xTranslation),
                    -(1 / 2 * (1 - yZoomScale) * viewPortHeight + yTranslation)
                );

            }

        }
        // detach listener from mouseup to stop triggering zoom on any
        // future mouse up events.
        event.currentTarget.removeEventListener("mouseup", endZoom);
    });
}

// Colors and symbols to be used in the plotly plots.
const BAND_COLORS = [
    "rgba(0,255,255,0.5)", //aqua
    "rgba(0,0,255,0.5)", //"blue"
    "rgba(0,188,212,0.5)", //"cyan"
    "rgba(165,42,42,0.5)", //"brown"
    "rgba(0,0,139,0.5)", //"darkblue"
    "rgba(0,139,139,0.5)", //"darkcyan"
    "rgba(189,183,107,0.5)", //"darkkhaki"
    "rgba(139,0,139,0.5)", //"darkmagenta"
    "rgba(85,107,47,0.5)", //"darkolivegreen"
    "rgba(255,140,0,0.5)", //"darkorange"
    "rgba(153,107,47,0.5)", //"darkorchid"
    "rgba(245,245,220,0.5)", //"beige"
    "rgba(139,0,0,0.5)", //"darkred"
    "rgba(233,150,122,0.5)", //"darksalmon"
    "rgba(148,0,211,0.5)", //"darkviolet"
    "rgba(255,0,255,0.5)", //"fuchsia"
    "rgba(255,215,0,0.5)", //"gold"
    "rgba(0,128,0,0.5)", //"green"
    "rgba(75,0,130,0.5)", //"indigo"
    "rgba(240,230,140,0.5)",//"#f0e68c" "khaki"
    "rgba(173,216,230,0.5)",//"#add8e6" "lightblue"
    "rgba(224,255,255,0.5)",//"#e0ffff", "lightcyan"
    "rgba(144,238,144,0.5)",//"#90ee90", "lightgreen"
    "rgba(211,211,211,0.5)",//"#d3d3d3" "lightgrey"
    "rgba(255,182,193,0.5)",//"#ffb6c1" "lightpink"
    "rgba(255,255,224,0.5)",//"#ffffe0" //"lightyellow"
    "rgba(0,255,0,0.5)",//"#00ff00", //"lime"
    "rgba(255,0,255,0.5)",//"#ff00ff", //"magenta"
    "rgba(128,0,0,0.5)",//"#800000", //"maroon"
    "rgba(0,0,128,0.5)",//"#000080", //"navy"
    "rgba(128,128,0,0.5)",//"#808000", //"olive"
    "rgba(255,165,0,0.5)",//"#ffa500", //"o#bdb76biolet"
    "rgba(192,192,192,0.5)",//"#c0c0c0", //"silver"
    "rgba(255,255,0,0.5)",//"#ffff00"  //"yellow"
];
// edge colors used to assign to a mode
const EDGE_COLORS = [
    "#00ffff", //aqua
    "#0000ff", //"blue"
    "#00bcd4", //"cyan"
    "#a52a2a", //"brown"
    "#00008b", //"darkblue"
    "#008b8b", //"darkcyan"
    "#bdb76b", //"darkkhaki"
    "#8b008b", //"darkmagenta"
    "#556b2f", //"darkolivegreen"
    "#ff8c00", //"darkorange"
    "#9932cc", //"darkorchid"
    "#f5f5dc", //"beige"
    "#8b0000", //"darkred"
    "#e9967a", //"darksalmon"
    "#9400d3", //"darkviolet"
    "#ff00ff", //"fuchsia"
    "#ffd700", //"gold"
    "#008000", //"green"
    "#4b0082", //"indigo"
    "#f0e68c", //"khaki"
    "#add8e6", //"lightblue"
    "#e0ffff", //"lightcyan"
    "#90ee90", //"lightgreen"
    "#d3d3d3", //"lightgrey"
    "#ffb6c1", //"lightpink"
    "#ffffe0", //"lightyellow"
    "#00ff00", //"lime"
    "#ff00ff", //"magenta"
    "#800000", //"maroon"
    "#000080", //"navy"
    "#808000", //"olive"
    "#ffa500", //"orange"
    "#ffc0cb", //"pink"
    "#800080", //"violet"
    "#c0c0c0", //"silver"
    "#ffff00"  //"yellow"
];
const COLOR_LENGTH = BAND_COLORS.length;
