var dataset_search_result_federated = document.querySelectorAll('.dataset_search_result_federated')
var search_result_display_federated = document.querySelector('#search_result_display_federated')
var dts_full = document.querySelectorAll('.dts_full')
var dts_source = document.querySelectorAll('dts_source')
var table = document.querySelector('.result_table')
var pre_data = document.querySelector('#pre_data')


// check_source_text = dataset_search_result_federated[-1].innerText.split(" ")[0]

function prepare_table() {

    let tr = document.createElement('tr')
    let th_dataset_name = document.createElement('th')
    let dataset_name = document.createTextNode('Dataset Name')
    th_dataset_name.appendChild(dataset_name)
    let th_description = document.createElement('th')
    let description = document.createTextNode('Description')
    th_description.appendChild(description)
    let th_source = document.createElement('th')
    let source = document.createTextNode('Source')
    th_source.appendChild(source)
    let th_SN = document.createElement('th')
    let sn = document.createTextNode('S/N')
    th_SN.appendChild(sn)
    // tr.appendChild(th_SN)
    tr.appendChild(th_dataset_name)
    tr.appendChild(th_description)
    tr.appendChild(th_source)
    table.appendChild(tr)
}

prepare_table()

function process_kaggle(dataset_source, datset) {
    let first_space = datset.trim().search(/\s/)
    let first_num = datset.trim().search(/[0-9]/)
    let dataset_name = datset.slice(0, first_space)
    let dataset_description = datset.slice(first_space, first_num)

    let tr = document.createElement('tr')
    let td_dataset_name = document.createElement('td')
    let td_dataset_name_text = document.createTextNode(dataset_name)
    td_dataset_name.appendChild(td_dataset_name_text)
    let td_dataset_description = document.createElement('td')
    let td_dataset_description_text = document.createTextNode(dataset_description)
    td_dataset_description.appendChild(td_dataset_description_text)
    let td_datset_source = document.createElement('td')
    let td_datset_source_text = document.createTextNode(dataset_source)
    td_datset_source.appendChild(td_datset_source_text)
    tr.appendChild(td_dataset_name)
    tr.appendChild(td_dataset_description)
    tr.appendChild(td_datset_source)
    return tr


}

function process_uci(dataset_source, datset) {
    let start_index = datset.split('#')[0].split('=')[1].search('>')
    let stop_index = datset.split('#')[0].split('=')[1].search('<')
    let dataset_name = datset.split('#')[0].split('=')[1].slice(start_index + 1, stop_index)
    let dataset_description = datset.split('#')[1].replace(/[^\w\s]/ig, " ")
    let tr = document.createElement('tr')

    let td_dataset_name = document.createElement('td')
    let td_dataset_name_text = document.createTextNode(dataset_name)
    td_dataset_name.appendChild(td_dataset_name_text)

    let td_dataset_description = document.createElement('td')
    let td_dataset_description_text = document.createTextNode(dataset_description)
    td_dataset_description.appendChild(td_dataset_description_text)

    let td_source = document.createElement('td')
    let td_source_text = document.createTextNode(dataset_source)
    td_source.appendChild(td_source_text)

    tr.appendChild(td_dataset_name)
    tr.appendChild(td_dataset_description)
    tr.appendChild(td_source)

    return tr
    console.log(tr); //replaces all special xters
    // let first_space = datset.trim().search(/\s/)
    // let dataset_name = datset.slice(1,20)
    // console.log(dataset_name);
    // let dataset = ptag.innerText
    // return dataset
}


function check_source(fulldataset) {

    let results = {}
    counter = 0
    fulldataset.forEach((ele, index) => {

        let dataset_source_kaggle = ""
        let datset_kaggle = ""
        let dataset_source_uci = ""
        let datset_uci = ""

        if (ele.innerText.includes('Kaggle')) {
            dataset_source_kaggle += "Kaggle";
            datset_kaggle += ele.firstElementChild.innerText.trim();

            let tr = process_kaggle(dataset_source_kaggle, datset_kaggle)

            table.appendChild(tr)
        }
        else if (ele.innerText.includes('UCI')) {
            datset_uci += ele.firstElementChild.innerText
            dataset_source_uci += ele.lastElementChild.innerText.split('#')[1]
            let tr = process_uci(dataset_source_uci, datset_uci)
            table.appendChild(tr)
            //console.log(tr);
        }
    }

    )
    // source.forEach(span => {
    //     let splitter = span.innerText.split("#")[1] // selects the key of the returned dictionary
    //     if (splitter == "Kaggle") {
    //         dataset_source += splitter

    //     }
    //     else if (splitter == "UCI") {
    //         dataset_source += splitter
    //         let dataset_arr = process_uci(dataset_source, ptag)
    //         console.log("dataset uci", dataset_arr)
    //     }

    //     console.log(splitter);
    // });
    // dtsfull.forEach(span => {
    //     let dataset_arr = process_kaggle(dataset_source ,ptag)
    //         console.log("dataset kaggle", dataset_arr);
    // })
    // result = []
    // source.forEach(ptag => {
    //    let dataset = ptag.innerText
    //    return dataset
    // });
    // let splitter = source.split('#')
    // if (splitter[1] == "Kaggle"){
    //     let output = process_kaggle()
    //     result.append(output)
    // }
    // else if(splitter[1] == "UCI"){
    //     return "UCI"
    // }
}

check_source(dataset_search_result_federated)

pre_data.classList.add('display-none')

