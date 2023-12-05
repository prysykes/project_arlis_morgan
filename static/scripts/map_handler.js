let lat_box = document.getElementById('elas_lat');
let long_box = document.getElementById('elas_long');
let map_h1 = document.getElementById('map_header');
let map_display = document.getElementById('map');
let radius_box = document.getElementById('elas_radius');

var submit_elas_form = document.querySelector('#submit_elas_form')


submit_elas_form.addEventListener('click', ()=>{
    let interval_counter = 0
    // poll_page_for_esimg()

    poll_img_interval = setInterval(()=>{
        if (interval_counter>=5){
            clearInterval(poll_img_interval)
        }
        poll_page_for_esimg(interval_counter++);
    }, 1000)

    
})

let timer, timeoutVal = 1000; // time it takes to wait on the user to begin typing again
var map = L.map('map')

function poll_page_for_esimg(interval_counter){
    var es_results = document.querySelectorAll('.es_results')
    es_results.forEach((elem)=>{
        elem.addEventListener('mouseover', ()=>{
            console.log("hiyoooo");
        })
    })
    // return es_results
}

// console.log('outer length', es_results.length)

// es_results.forEach((elem)=>{
//     elem.addEventListener("mouseover", ()=>{
//         console.log('hi');
//     })
// } )


function handleEventListenerLat(lat_box, long_box, radius_box){
    lat_box.addEventListener('keypress', handlekeyPress)
    lat_box.addEventListener('keyup', handlekeyUp)
   
}

function handleEventListenerLong(long_box, lat_box, radius_box){
    long_box.addEventListener('keypress', handlekeyPress)
    long_box.addEventListener('keyup', handlekeyUp)
    
}

function handleEventListenerRadius(radius_box, lat_box, long_box){
    radius_box.addEventListener('keypress', handlekeyPress)
    radius_box.addEventListener('keyup', handlekeyUp)
    
}

handleEventListenerLat(lat_box)
handleEventListenerLong(long_box)
handleEventListenerRadius(radius_box)


function handlekeyPress(element){
   
    window.clearTimeout(timer);
    console.log("started typing");
    // console.log(`inside ${element}: lat_val ${lat_box.value} \t radius_val:${radius_box.value} \t long_val: ${long_box.value}`);
}

function handlekeyUp(element){
    window.clearTimeout(timer);
    timer = window.setTimeout(()=>{
        lat_value = lat_box.value
        long_value = long_box.value
        if ((lat_value.length >= 2 && long_value.length) >= 2){
           
            handleMap(lat_value, long_value)
            // var es_results = document.querySelectorAll('.es_results')
            // console.log('inner length', es_results.length);
            // console.log(`inside ${element}: lat_val ${lat_value.length} \t radius_val:${radius_box.value} \t long_val: ${long_value.length}`);
            
        }
        else{
            console.log('You need the latitude and longitude values to draw the map');
        }
        
    }, timeoutVal)
}

function img_hover_to_map(lat, long, L, map){
   if (!map_display.classList.contains('display-none')) {
        var circle = L.circle([lat, long], {
            color: 'green',
            fillColor: '#f03',
            fillOpacity: 0.5,
            radius: 200
        }).addTo(map)
   }
}

function handleMap(lat, long){
    

    if (map_display.classList.contains('display-none')){
        map_h1.classList.remove('display-none')
        map_display.classList.remove('display-none') 
        map.setView([lat, long], 13);
        
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);
        var marker = L.marker([lat, long]).addTo(map);
        var circle = L.circle([lat, long], {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.5,
            radius: 450
        }).addTo(map);
        img_hover_to_map(lat, long, L, map);
        
        } else {
            
            map.remove()
            map_display.innerHTML == ""
            map.setView([lat, long], 13);
            
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }).addTo(map);
            marker = L.marker([lat, long]).addTo(map);
            circle = L.circle([lat, long], {
                color: 'red',
                fillColor: '#f03',
                fillOpacity: 0.5,
                radius: 400
            }).addTo(map);
        }

    
    
}


// console.log('outer length', es_results.length);
// es_results.forEach((elem)=>{
//     elem.addEventListener('mouseover', ()=> {
//         console.log("hiiii");
//     })
//     console.log(elem);
// })



// es_results.forEach((elem)=>{
//     console.log(elem);
// })
// console.log('es_results', typeof es_results);


// lat_box.addEventListener('click', ()=>{
//     console.log('lat box clicked');
//     if
// })

// lat_box.addEventListener('mouseover', ()=>{
//     console.log('lat box clicked');
// })

// long_box.addEventListener('mouseover', ()=>{
//     console.log('long box clicked');
// })

// map.addEventListener('click', ()=>{
//     console.log('hello');
// })

// function showmap(map){
//     var map = L.map('map').setView([51.505, -0.09], 13);
// }


//     console.log('yes');
// }

// // console.log(elas_lat);
let ismapdisplayed = false

// lat_box.addEventListener('click', ()=>{
//     console.log('lat box clicked');
//     if
// })

// lat_box.addEventListener('mouseover', ()=>{
//     console.log('lat box clicked');
// })

// long_box.addEventListener('mouseover', ()=>{
//     console.log('long box clicked');
// })

// map_elastic_search_form.addEventListener('submit', ()=>{
//     let lat_val = lat_box.value
//     let long_val = long_box.value
//     console.log("lat val",lat_val)
//     console.log("long val", long_val)
// })

