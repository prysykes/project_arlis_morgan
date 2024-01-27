let lat_box = document.getElementById('elas_lat');
let long_box = document.getElementById('elas_long');
let map_h1 = document.getElementById('map_header');
let map_display = document.getElementById('map');
let radius_box = document.getElementById('elas_radius');
window.es_results = []
var submit_elas_form = document.querySelector('#submit_elas_form')


submit_elas_form.addEventListener('click', ()=>{
    let interval_counter = 0
    
    // var len_esresults = es_results.length
    // poll_page_for_esimg()
    // the poll process should be run just 5 times 
    // afterwards, the interval will be removed
    poll_img_interval = setInterval(()=>{
        es_results = document.querySelectorAll('.es_results')
        // checks to see if a search result has been returned from server
        if (es_results.length > 1){
            poll_page_for_esimg(es_results);
            clearInterval(poll_img_interval)
        }
        console.log('len esresults', es_results.length);
        
    }, 1000)

    
})

let timer, timeoutVal = 1000; // time it takes to wait on the user to begin typing again
// var map = L.map(map_display)

//an object to hold the markers for subsequent removal 

let added = false
function poll_page_for_esimg(es_results){
    // adds mouse over event to each image on the page
    // after it has been returned from the server
    
    
    color_change = 100
    es_results = document.querySelectorAll('.es_results')
    // let esCounter = 0
    es_results.forEach((elem)=>{
        
        // console.log('esCounter', esCounter);
        elem.addEventListener('mouseover', (e)=>{
            //select the lat and long val of the current image
            let cur_metrics_div = elem.nextElementSibling.children
            cur_metrics_div = cur_metrics_div[2]
            cur_metrics_div = cur_metrics_div.children
            let cur_lat = Number(cur_metrics_div[2].innerText.split(" ")[1])
            
            let cur_long = Number(cur_metrics_div[3].innerText.split(" ")[1])
            // cur_long = cur_long.innerText
            
            
            color_change = locate_img_onmap(color_change, cur_lat, cur_long);
            let cur_img = e.srcElement
                      
            cur_img.classList.add("img_border")
        })

        elem.addEventListener('mouseout', (e)=>{
            
            //select the lat and long val of the current image
            let cur_metrics_div = elem.nextElementSibling.children
            cur_metrics_div = cur_metrics_div[2]
            cur_metrics_div = cur_metrics_div.children
            let cur_lat = Number(cur_metrics_div[2].innerText.split(" ")[1])
           
            let cur_long = Number(cur_metrics_div[3].innerText.split(" ")[1])

            let cur_img = e.srcElement
            
            cur_img.classList.remove("img_border")
            // console.log('makeout', markers);
            
            locate_img_onmap(color_change, cur_lat, cur_long, mouse_out=true)
            
        })
        esCounter += 1
    })
    return es_results
}

// locates an image on map when user hovers over it
function locate_img_onmap(color_change, cur_lat, cur_long, mouse_out=false){
   
    if (!mouse_out){
        
        loc_circle = L.circle([cur_lat, cur_long], {
            color: `#${color_change}c0e`,
            fillColor: `#4c${color_change}f`,
            fillOpacity: 1,
            radius: 100
        }).addTo(map);
        color_change ++
        // console.log(color_change);
        return color_change
    } else {
        
        map.removeLayer(loc_circle)
        
        
    }
    
    
    
}

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


function handleMap(lat, long){
    

    if (map_display.classList.contains('display-none')){
        map_h1.classList.remove('display-none')
        map_display.classList.remove('display-none')
        // initializing map 
        window.map = L.map(map_display)
        // var map = L.map(map_display)
        map.setView([lat, long], 13);
        
        // osm layer
        let osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);

        // add street view on map
        var googleStreets = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{
            maxZoom: 20,
            subdomains:['mt0','mt1','mt2','mt3']
        }).addTo(map);

       
        var main_marker = L.marker([lat, long],
        );
         // setting marker icon size
        var icon = main_marker.options.icon;
        icon.options.iconSize = [40, 60]
        main_marker.setIcon(icon)
        
        var aux_icon = new L.Icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [40, 50]
          });
          
        
        // diplays the lat and long cordinates above the main marker
        var popup = main_marker.bindPopup(`Lat: ${lat} Lng: ${long}`); 
        popup.addTo(map);
        popup.openPopup();
        // var img1_marker = L.marker([lat, -76.6399],
        //     {icon: aux_icon}).addTo(map);
        // var img2_marker = L.marker([lat, -76.6299],
        //     {icon: aux_icon}).addTo(map);

        // var img3_marker = L.marker([lat, -76.6199],
        //     {icon: aux_icon}).addTo(map);
        
        // var image_locations = L.layerGroup([img1_marker, img2_marker, img3_marker]);

        var circle = L.circle([lat, long], {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.2,
            radius: 4500
        }).addTo(map);

        map.on('mouseover', function () {
            console.log('heeeeeee');
        })
        

        
        // var map = L.map(map_display, {
        //     center: [lat, long],
        //     zoom: 10,
        //     layers: [osm, googlestreet]
        // });
        // map.options.layers = [osm, main_marker];

        // var baseMaps = {
        //     "OSM": osm,
        //     "Google Street": googleStreets,
            
        // };
        
        // var overlayMaps = {
        //     'main_marker': main_marker,
        //     'im1': img1_marker,
        //     'img2': img2_marker,
        //     'img3': img3_marker,
        //     'circle': circle 
           
        // };

        // L.control.layers(baseMaps, overlayMaps, {collapsed: false}).addTo(map)
        
        } 

        // var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);
        // layerControl.addOverlay(image_locations, 'imageLocations')
        

        // layer controls


    
    
}


let ismapdisplayed = false
