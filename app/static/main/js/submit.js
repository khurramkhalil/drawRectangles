// console.log("Hi there!")


let excel;

async function fetchText() {
    let response = await fetch('/getdata');

    // console.log(response.status); // 200
    // console.log(response.statusText); // OK

    if (response.status === 200) {
        console.log("Time begins")
        console.time("Rectangle Transmit Time: ")
        let data = await response.text();
        excel = JSON.parse(data)
        console.timeEnd("Rectangle Transmit Time: ")

    }
}

const start = document.getElementById('fetch')
start.addEventListener('click', fetchText);
