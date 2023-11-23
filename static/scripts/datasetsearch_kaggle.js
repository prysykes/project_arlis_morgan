
var dataset_search_result = document.querySelectorAll('.dataset_search_result_kaggle');
var search_result_display = document.getElementById('search_result_display_kaggle');


function prepare_header() {
    let tr = document.createElement('tr')
    let result_column = dataset_search_result[0].innerText.split(' ')
    result_column.forEach(ele => {
        let th = document.createElement('th')
        let text = document.createTextNode(ele)
        th.appendChild(text);
        tr.appendChild(th)
    })


    return tr;

}
function rest_of_it_populate(rest_of_it_split) {
    let tdArray = []
    let tdSize = document.createElement('td')
    let tdLastUpdated = document.createElement('td')
    let tdDownloadCount = document.createElement('td')
    let tdVoteCount = document.createElement('td')
    let tdUsabilityRating = document.createElement('td')
    let tdSizeText = document.createTextNode(rest_of_it_split[0])
    let tdLastUpdatedText = document.createTextNode(rest_of_it_split[1].concat(rest_of_it_split[2]))
    let tdDownloadCountText = document.createTextNode(rest_of_it_split[3])
    let tdVoteCountText = document.createTextNode(rest_of_it_split[4])
    let tdUsabilityRatingText = document.createTextNode(rest_of_it_split[5])
    tdSize.appendChild(tdSizeText)
    tdLastUpdated.appendChild(tdLastUpdatedText)
    tdDownloadCount.appendChild(tdDownloadCountText)
    tdVoteCount.appendChild(tdVoteCountText)
    tdUsabilityRating.appendChild(tdUsabilityRatingText)
    //use spread operator to create an array from the variables above
    tdArray = [...tdArray, tdSize, tdLastUpdated, tdDownloadCount, tdVoteCount, tdUsabilityRating]
    return tdArray;
}

function prepare_rows() {

    var tr_arr = []

    for (let i = 1; i < dataset_search_result.length; i++) {
        let tr = document.createElement('tr');
        let result_row = dataset_search_result[i].innerText;
        let result_row_split = result_row.split(" ")
        let download_link_text = result_row_split[0];
        let download_link = result_row.search(download_link_text);
        //returns index of where the download link text starts
        let index_to_search_space = download_link + result_row_split[0].length
        let first_num = result_row.slice(index_to_search_space,).search(/[0-9]/)
        let full_index_to_num = index_to_search_space + first_num
        let dataset_name = result_row.slice(index_to_search_space, full_index_to_num)
        let rest_of_it = result_row.slice(full_index_to_num,)
        let td_download_link = document.createElement('td')
        let td_dataset_name = document.createElement('td')
        let text_download_link = document.createTextNode(download_link_text)
        let text_dataset_name = document.createTextNode(dataset_name)
        td_download_link.appendChild(text_download_link)
        td_dataset_name.appendChild(text_dataset_name)
        // adition
        td_download_link.classList.add('download_text')
        tr.appendChild(td_download_link)
        tr.appendChild(td_dataset_name)
        rest_of_it_split = rest_of_it.split(' ')
        let tdSize = document.createElement('td')
        let tdLastUpdated = document.createElement('td')
        let tdDownloadCount = document.createElement('td')
        let tdVoteCount = document.createElement('td')
        let tdUsabilityRating = document.createElement('td')
        let tdSizeText = document.createTextNode(rest_of_it_split[0])
        let tdLastUpdatedText = document.createTextNode(rest_of_it_split[1] + " ".concat(rest_of_it_split[2]))
        let tdDownloadCountText = document.createTextNode(rest_of_it_split[3])
        let tdVoteCountText = document.createTextNode(rest_of_it_split[4])
        let tdUsabilityRatingText = document.createTextNode(rest_of_it_split[5])
        tdSize.appendChild(tdSizeText)
        tdLastUpdated.appendChild(tdLastUpdatedText)
        tdDownloadCount.appendChild(tdDownloadCountText)
        tdVoteCount.appendChild(tdVoteCountText)
        tdUsabilityRating.appendChild(tdUsabilityRatingText)
        tr.appendChild(tdSize)
        tr.appendChild(tdLastUpdated)
        tr.appendChild(tdDownloadCount)
        tr.appendChild(tdVoteCount)
        tr.appendChild(tdUsabilityRating)

        tr_arr.push(tr)


    }
    return tr_arr;


}


function dashboard_kaggle() {
    let tr_head = prepare_header()
    let tr_row = prepare_rows()
    tr_row.forEach(tr => {
        tr.classList.add('kaggle_dataset')
    });

    let table = document.createElement('table')
    table.classList.add('result_table')
    table.appendChild(tr_head)
    tr_row.forEach(tr => {
        table.appendChild(tr)
    })

    search_result_display.appendChild(table)


}

dashboard_kaggle()


dataset_search_result.forEach(element => {
    element.classList.add('display-none')

});

// implementing download kaggle


// go into the table rows and obtain the innerText of the first child of the row