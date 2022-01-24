// console.log("Hi there!")


let excel;


async function fetchText(file) {
    // console.log("Time begins")
    // console.time("Rectangle Transmit Time: ")

    let excelData = new FormData();
    // adding the user selected file to the form
    excelData.append("mdfExcel", file.files[0]);

    let response = await fetch('/getdata', {method: "POST",body: excelData});

    // console.log(response.status); // 200
    // console.log(response.statusText); // OK
    if (response.status === 200) {
         excel = await response.json();
        // excel = JSON.parse(data)
        // console.timeEnd("Rectangle Transmit Time for fetch: ")

    }
}

// async function fetchText(file) {
//     // console.log("Time begins")
//     // console.time("Rectangle Transmit Time: ")
//     let response = await fetch('/getdata');
//
//     // console.log(response.status); // 200
//     // console.log(response.statusText); // OK
//     if (response.status === 200) {
//          excel = await response.json();
//         // excel = JSON.parse(data)
//         // console.timeEnd("Rectangle Transmit Time for fetch: ")
//
//     }
// }
//
// const start = document.getElementById('fetch')
// start.addEventListener('click', fetchText);
