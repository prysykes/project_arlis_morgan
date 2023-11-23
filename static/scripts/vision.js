var view_uploaded_images = document.getElementById("view_uploaded_images")
var upload_images = document.getElementById('upload_images')
var upload_form = document.getElementById('upload_form')
var vision_main = document.getElementById('vision_main')
var disp_img = document.getElementById('img_disp')
var detections_yolo = document.getElementById('view_detections_yolo')


view_uploaded_images.addEventListener('click', () => {
    disp_img.classList.toggle('display-none')
})

upload_images.addEventListener('click', () => {
    upload_form.classList.toggle('display-none')
})

detections_yolo.addEventListener('click', () => {

})