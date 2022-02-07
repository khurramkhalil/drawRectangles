// console.log("Hi there!")

"use strict"; // This ensures that insecure and incompatible code throws an error. This is ignored in older version of javascript https://www.w3schools.com/js/js_strict.asp
/* for automatically uploading  file without clicking */

const READYSTATE_DONE = 4; // This is returned when the XMLHTTPRequest is complete.
const HTTP_SUCCESS = 200; // 200 is returned when the http is successfully completed at the server.
let excelData = []; // global variable to store data obtained from excel file


function submit_file(file) {
    if (file) {
        // generating http request to server for submitting the user uploaded excel file
        console.time("Rectangle Transmit Time: ")
        let fileUploadAjax = new XMLHttpRequest();
        fileUploadAjax.onreadystatechange = function () {
            if (this.readyState === READYSTATE_DONE && this.status === HTTP_SUCCESS) {
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
