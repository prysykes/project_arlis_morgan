const elas_object = document.getElementById("elas_object")

const elas_long = document.getElementById("elas_long")
const elas_lat = document.getElementById("elas_lat")
const elas_radius = document.getElementById("elas_radius")
const elas_det = document.getElementById("elas_det")
const elas_area = document.getElementById("elas_area")
const elas_start_date = document.getElementById("elas_start_date")
const elas_end_date = document.getElementById("elas_end_date")
const date_error = document.getElementById("date_error")
const elastic_search_form = document.getElementById("elastic_search_form")
const elastic_search_results = document.getElementById("elastic_search_results")
const elastic_search_div = document.getElementById("elastic_search_div")
const elastic_search = document.getElementById('elastic_search')

elastic_search_div.addEventListener('click', ()=>{
    elastic_search.classList.toggle('display-none')
} )

function check_startdate_lt_enddate(start_val, end_val){
    if(start_val > end_val){
        throw new Error('start date must be less than end date')
    }
}

function check_long_lat(value){
    let regex = /^\d*\.?\d*$/ //longitude/ latitude format validator
    value = value.replace('-', '')
    chk_outcome = regex.test(value)
    if (chk_outcome == false){
        throw new Error("Longitude and Latitude must be a float")
   }
}

async function fetch_search_endpoint(url, search_values){
    const csrftoken = getCookie('csrftoken');
    // console.log("csrftokeneee", csrftoken);
    // console.log('datafg oo', search_values);
    const form_data = new FormData();
    form_data.append('csrfmiddlewaretoken', csrftoken)
    const keys = Object.getOwnPropertyNames(search_values)
    // console.log('keevvvveey', search_values);
    keys.forEach((key) =>{
        current_key = String(key)
        current_val = String(search_values[key])
        // instantiates a form data using the data object
        form_data.append(key, search_values[key])
    })
    

    form_data_entries = form_data.entries()
    
    try {
        
        const response = await fetch(url, {
            method: 'POST',
            body: form_data,
        });
        
        if (!response.ok){
            throw new Error("Search response not valid")
        }else{
            return response.json()
        }
         // if response is OK, work on these
    } catch (error) {
        // console.error(error)
    } 

}

function getCookie(name){
    //tried to use this function to set CSRF token 
    // for django forms
    let cookieValue = null;

    if (document.cookie && document.cookie != ''){
        const cookies = document.cookie.split(';');
        for (i=0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length +1));
                break;
            }
        }
    }
    // console.log('cookie', cookieValue);
    return cookieValue;
}

function check_long_lag(longitude, latitude, data){
    if(longitude != "" && latitude != ""){
        try {
            check_long_lat(longitude)
            check_long_lat(latitude)
            Object.defineProperties(data, {
                'longitude':{
                    value: longitude,
                    writable: true
                },
                'latitude':{
                    value: latitude,
                    writable: true
                }
            })
            // data['longitude'] = longitude
            // data['latitude'] = latitude
        } catch (error) {
            console.log(error);
            date_error.classList.remove('display-none')
            date_error.textContent = error.toString().replace('Error:', '')
            // date_error is a div to send error messages to the user
        }
        
        
    }
}

function check_date(start_date, end_date, data){
    if (start_date && end_date){
        let seconds_equiv_start_date = new Date(start_date)
        let seconds_equiv_end_date = new Date(end_date)
        try {
            check_startdate_lt_enddate(seconds_equiv_start_date, seconds_equiv_end_date)
            // sets the value of a key in an object if the key does not exist
            Object.defineProperties(data, {
                'start_date': {
                    value: start_date,
                    writable: true,
                },

                'end_date': {
                    value: end_date,
                    writable: true,
                }
            })
            // data['start_date'] = seconds_equiv_start_date
            // data['end_date'] = seconds_equiv_end_date
        } catch (error) {
            date_error.classList.remove('display-none')
            date_error.textContent = error.toString().replace('Error:', '')
        }

    }
}

function check_num_det(detections, data){
    if (detections != ""){
        Object.defineProperties(data, {
            'detections': {
                value: detections,
                writable: true,
            }
        })
        // data['detection'] = detections
    }
}

function check_radius(radius, data){
    if (radius != ""){
        Object.defineProperties(data, {
            'radius': {
                value: radius,
                writable: true,
            }
        })
    }
}

function check_object_area(area, data){
    //picks the onject class to query on
    if (area != ""){
        Object.defineProperties(data, {
            'object_area': {
                value: area,
                writable: true,
            }
        })
    }
}

function object(object, data){
    
    if (object != ""){
        // console.log("object", object);
        Object.defineProperties(data, {
            'object': {
                value: object,
                writable: true,
            }
        })
        // console.log(object);
        // data['object'] = object
    }
}

// console.log("elastic_search_results", elastic_search_results);

function unpack_cur_metrics(cur_metrics){
    // function to unpack current metrics for an image
    let metric_div = document.createElement('div')
    metric_div.classList.add('metrics_div')
    let metrics_heading = document.createElement('h3')
    metrics_heading.innerText = 'Summary'
    metric_div.appendChild(metrics_heading)

    let metadata_div = document.createElement('div')
    metadata_div.classList.add('metadata_div')
    let metadata_heading = document.createElement('h4')
    metadata_heading.innerText = 'Image Metadata'
    metadata_div.appendChild(metadata_heading)
    

    let detections_div = document.createElement('div')
    detections_div.classList.add('detections_div')
    let detections_heading = document.createElement('h4')
    detections_heading.innerText = 'Detections'
    detections_div.appendChild(detections_heading)

    for(const key in cur_metrics) {
        console.log(`key: ${key} \n values: ${cur_metrics[key]}`);
        if (key == 'detections'){
            let detections = cur_metrics['detections']
            
            for (const detection in detections) {
                console.log(` DetectionIs: ${detection} frequency: ${detections[detection]}`);
                let p_detection = document.createElement('p')
                p_detection.innerText = `${detection}:${detections[detection]}`
                detections_div.appendChild(p_detection)
            }
            metric_div.appendChild(detections_div)
            
        }
        else if (key == 'metadata'){
            let metadata = cur_metrics['metadata']
            
            for (const mdata in metadata){
                if (mdata == 'GPSInfo'){
                    let GPSInfo = metadata['GPSInfo']
                    // console.log(`GPSInfo ${GPSInfo}`);
                    let latitude = null
                    let longitude = null
                    for (const lat_long in GPSInfo){
                        if (lat_long == 'latitude'){
                            latitude = GPSInfo['latitude']
                            let p_lat = document.createElement('p')
                            p_lat.innerText = `Latitude: ${latitude}`
                            metadata_div.appendChild(p_lat)
                        } 
                        else if (lat_long == 'longitude'){
                            longitude = GPSInfo['longitude']
                            let p_long = document.createElement('p')
                            p_long.innerText = `Longitude: ${longitude}`
                            metadata_div.appendChild(p_long)
                        }
                        
                    }
                    
                    
                    console.log(`latitude: ${latitude} longitude: ${longitude}`);
                    
                }else if (mdata == 'DateTime'){
                    let datetime = metadata['DateTime']
                    let p_date = document.createElement('p')
                    p_date.innerText = `Date Captured: ${datetime}`
                    metadata_div.appendChild(p_date)
                    console.log(`datetime: ${datetime}`);
                }else if (mdata == 'img_dimensions'){
                    let img_dimensions = metadata['img_dimensions']
                    // console.log(`img_dimensions ${img_dimensions}`);
                    let img_width = null
                    let img_height = null
                    for (const wt_ht in img_dimensions){
                        if (wt_ht == 'width'){
                            img_width  = img_dimensions['width']
                            let p_img_width = document.createElement('p')
                            p_img_width.innerText = `Image Width: ${img_width}`
                            metadata_div.appendChild(p_img_width)
                        }
                        else if (wt_ht == 'height'){
                            img_height = img_dimensions['height']
                            let p_img_height= document.createElement('p')
                            p_img_height.innerText = `Image Height: ${img_height}`
                            metadata_div.appendChild(p_img_height)
                        }
                      
                        
                    }
                    console.log(`img_width: ${img_width}  img_height: ${img_height}`);
                    
                }
            }
        }
        metric_div.append(metadata_div)
    }
    return metric_div
}

function create_img_containier(cur_img, cur_metrics){
    // console.log("preee", cur_img);
    
    metrics_div = unpack_cur_metrics(cur_metrics)
    
    let div = document.createElement('div')
    

    let img = document.createElement('img')
    img.src = `/media/temp_imgs_s3/${cur_img}.jpg`
    console.log("img.src", img.src);
    img.width = '300'
    img.height = '300'
    img.classList.add('es_results')
    //  console.log(`div: ${div} \n img ${img}`);
    div.appendChild(img)
    div.appendChild(metrics_div)
    return div
}

// create_img_containier()

elastic_search_form.addEventListener("submit", (e)=>{
    e.preventDefault()
    // let elas_object = elas_object.value
    let search_values = {}
    let longitude = elas_long.value
    let latitude = elas_lat.value
    let radius = elas_radius.value
    let num_detections = elas_det.value
    let object_area = elas_area.value
    let start_date = elas_start_date.value
    let end_date = elas_end_date.value
    let selected_class = elas_object.options[elas_object.selectedIndex].value;


    // helper functions to check that
    // the variables above and are empty then 
    // append then to the search_values_object

    // check selected object
    object(selected_class, search_values)

    // check longitude
    check_long_lag(longitude, latitude, search_values)
    
    // check radius
    check_radius(radius, search_values)
    
    // check that date values were supplied
    
    check_date(start_date, end_date, search_values)

    // check detections
    check_num_det(num_detections, search_values)

    // check that date values were supplied    
    check_date(start_date, end_date, search_values)
    // check that object area was supplied
    check_object_area(object_area, search_values)

    // console.log("search_valueers", search_values);
    
     if(elas_object == "" && longitude == "" && radius == "" && latitude == "" && num_detections == "" && object_area == "" ){
        preventDefault()
        alert("You must enter a value"); //checks if all valies are empty
        
    }
    let base_url = window.location.origin // retrieves the base url
    // console.log(base_url);
    const url = base_url+'/elastic_search'
    // console.log("url", url);
    

    fetch_search_endpoint(url, search_values)
    .then((data) =>{
        let img_id_metrics = null
        console.log("gigig",data)
        img_id_metrics = data['img_id_metrics']

        for (const imgg in img_id_metrics) {
            let cur_img = imgg
            let cur_metrics = img_id_metrics[cur_img]
            img_div = create_img_containier(cur_img, cur_metrics)
            elastic_search_results.appendChild(img_div)
            
        }
        // img_id_metrics.forEach((cur_url) => {
        //     img_div = create_img_containier(cur_url)
        //     elastic_search_results.appendChild(img_div)
        // })
        
    }
   
        
    )
}) 