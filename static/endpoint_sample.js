const upload = document.querySelector('#upload')

const upload_form = document.querySelector('#upload')


function get_request(){
    upload.addEventListener("click", (e) => {
        e.preventDefault()
        fetch('http://127.0.0.1:8000/object_detection_endpoint/')
        .then(response => response.json())
        .then(data => console.log(data))
        
    })
}




function post_request() {
    const images_upload_form = document.getElementsByName('images_upload_form')
    images_upload_form[0].addEventListener('submit', (e) => {
        e.preventDefault()
        const uploaded_images = document.querySelectorAll('.image_file')
       const formData = new FormData()
       formData.append("test_images_file_1", uploaded_images[0].files[0])
       formData.append("test_images_file_2", uploaded_images[2].files[0])
       formData.append("test_images_file_3", uploaded_images[3].files[0])
       formData.append("test_images_file_4", uploaded_images[4].files[0])
       formData.append("test_images_file_5", uploaded_images[5].files[0])
       formData.append("test_csv_file", uploaded_images[5].files[0])

       fetch('http://127.0.0.1:8000/object_detection_endpoint/', {
        method: "POST",
        body: formData,
       })
       .then(response => response.json())
       .then(data => console.log(data))
       .catch(error => console.log(error))
       
       
        
    })
  
post_request() 
//get_request()