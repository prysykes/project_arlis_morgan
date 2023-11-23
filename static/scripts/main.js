var show_search = document.getElementById('show-search')
var search_dataset_div = document.getElementsByClassName('search-dataset')
var search_dset_div = document.getElementById('search-dataset')


show_search.addEventListener('click', function() {
    search_dset_div.classList.toggle('display-none');
})

// search_dset_div.addEventListener('click', ()=>{
//     console.log("hahahah");
// })