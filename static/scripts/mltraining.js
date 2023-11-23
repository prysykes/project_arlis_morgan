// id="delete_instance" class="alis-pane-button"> Delete Sagemaker Instance </button> <i class="botton-dot"> <button></button></i></li>
// {% else %}
// <li> <button id="launch_instance" class="alis-pane-button"> Launch Sagemaker Instance </button> <i class="botton-dot"> <button></button></i></li>
// {% endif %}

// <li> <button id="upload_notebook" class="alis-pane-button"> Upload Jupyter Notebook</button> <i class="botton-dot"> <button></button></i></li>
// <li><button id="upload_images" class="alis-pane-button"> Upload Images</button> <i class="botton-dot"> <button></button></i> </li>
// <li> <button id="Select_classifier" class="alis-pane-button"> Select Classifier/Model</button> <i class="botton-dot"> <button></button></i></li>
// <li><button id="uploaded_dataset"

var delete_instance = document.querySelector("#delete_instance")
var launch_instance = document.querySelector("#launch_instance")
var upload_notebook = document.querySelector("#upload_notebook")
var upload_images = document.querySelector("#upload_images")
var select_classifier = document.querySelector("#select_classifier")
var uploaded_dataset = document.querySelector("#uploaded_dataset")

var upload_notebook_form = document.querySelector('#upload_notebook_form')
var choose_classifier_form = document.querySelector('#choose_classifier_form')
var upload_dataset_form = document.querySelector('#upload_dataset_form')

upload_notebook.addEventListener('click', () => {
    upload_notebook_form.classList.toggle('display-none') 
});

select_classifier.addEventListener('click', () => {
    choose_classifier_form.classList.toggle('display-none') 
});

uploaded_dataset.addEventListener('click', () => {
    upload_dataset_form.classList.toggle('display-none') 
});

// launch_instance.addEventListener('click', () => {
//     console.log("hahah");
// });

// upload_notebook.addEventListener('click', () => {
//     console.log("hahah");
// });

// upload_images.addEventListener('click', () => {
//     console.log("hahah");
// });

// select_classifier.addEventListener('click', () => {
//     console.log("hahah");
// });

// uploaded_dataset.addEventListener('click', () => {
//     console.log("hahah");
// })