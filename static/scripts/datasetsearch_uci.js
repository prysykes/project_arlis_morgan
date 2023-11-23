var dataset_search_result_uci = document.querySelectorAll('.dataset_search_result_uci') 
var search_result_display_uci = document.querySelector('#search_result_display_uci')


function extract_dataset_name(tag_text){
    let start_point = tag_text.search("\/")
    let end_point = tag_text.search('\">')
    name_of_dtset = tag_text.slice(start_point+1, end_point)
    name_of_dtset_clean = name_of_dtset.replace(/[^a-zA-Z0-9-.]/ig, " ")
    // [^a-zA-Z0-9-] search all special characters except -
    //console.log("extract_dataset_name",tag_text);

    return name_of_dtset_clean
}
function extract_dataset_description(tag_text){
    let start_point = tag_text.search('\">')
    let end_point = tag_text.search('<\/')
    description_of_dtset = tag_text.slice(start_point+1, end_point)
    description_of_dtset_clean = description_of_dtset.replace(/[^a-zA-Z0-9-]/ig, " ")
    // [^a-zA-Z0-9-] search all special characters except -
    // console.log("extract_dataset_description",tag_text);
    return description_of_dtset_clean
}

function prepare_header(){
    let table = document.createElement('table')
    let tr = document.createElement('tr')
    let th_dataset_name = document.createElement('th')
    let dataset_name = document.createTextNode('Dataset Name')
    let th_dataset_description = document.createElement('th')
    let th_count = document.createElement('th')
    let th_count_text = document.createTextNode('S/N')
    tr.appendChild(th_count).appendChild(th_count_text)
    let dataset_description = document.createTextNode('Dataset Description')
    tr.appendChild(th_dataset_name).appendChild(dataset_name)
    tr.appendChild(th_dataset_description).appendChild(dataset_description)
    
    table.appendChild(tr)
    return table

}

function prepare_rows(){
    table = prepare_header()
    let count = 1
    dataset_search_result_uci.forEach(p_tag => {
        //console.log("p_tag.innerText", p_tag.innerText);
        let p_tag_text = p_tag.innerText.split('#') // reason we added the hash at the backend
        let dataset_name = extract_dataset_name(p_tag_text[0])
        let dataset_description = extract_dataset_description(p_tag_text[1])
        let tr = document.createElement('tr')
        let td_count = document.createElement('td')
        let td_count_text = document.createTextNode(count.toString())
        let td_dataset_name = document.createElement('td')
        td_dataset_name.classList.add('download_text')
        let td_description = document.createElement('td')
        let dataset_name_text = document.createTextNode(dataset_name)
        let dataset_description_text = document.createTextNode(dataset_description)
        td_count.appendChild(td_count_text)
        tr.appendChild(td_count)
        td_dataset_name.appendChild(dataset_name_text)
        tr.appendChild(td_dataset_name)
        td_description.appendChild(dataset_description_text)
        tr.appendChild(td_description)
        table.appendChild(tr)
        count +=1
        
        
    })
    search_result_display_uci.appendChild(table)
}

prepare_rows()

dataset_search_result_uci.forEach(element => {
    element.classList.add('display-none')
})

