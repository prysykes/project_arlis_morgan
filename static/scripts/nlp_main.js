let hide_df = document.querySelector('#hide_df')
let df_view = document.querySelector('.df_view')
let current_paginated_row = document.querySelectorAll('.df_row')
let df_row_table = document.querySelector('#df_row_table')

hide_df.addEventListener('click', () => {
    df_view.classList.toggle('display-none')
    
})

// current_paginated_row.forEach((row) => {
//     console.log(row.innerText);
// })

function create_table_head() {
    //prepares the table with associated headers from the dataset
    let table = document.createElement('table')
    let tr = document.createElement('tr')
    let th_id = document.createElement('th')
    let id = document.createTextNode('ID')
    th_id.appendChild(id)
    tr.appendChild(th_id)
    let th_text = document.createElement('th')
    let text = document.createTextNode('Text')
    th_text.appendChild(text)
    tr.appendChild(th_text)
    let th_polarity = document.createElement('th')
    let polarity = document.createTextNode('Polarity')
    th_polarity.appendChild(polarity)
    tr.appendChild(th_polarity)
    let th_target = document.createElement('th')
    let target = document.createTextNode('Target')
    th_target.appendChild(target)
    tr.appendChild(th_target)
    table.appendChild(tr)

    return table
}



function process_hidden_paginated_rows(hidden_paginated_rows){
    
    table_with_header = create_table_head()
    hidden_paginated_rows.forEach((e) => {
        let tr = document.createElement('tr')
        column_value = e.innerText.replace(/[^a-zA-Z0-9,\s.]/ig, "")
        //regular expression to replace anything that is not an alphabet, digit space , and .
        column_values_splitted = column_value.split(',')
        let c_id = column_values_splitted[0]
        let c_text = column_values_splitted[1]
        let c_polarity = column_values_splitted[2]
        let c_target = column_values_splitted[3]
        let id_td = document.createElement('td')
        let id_val = document.createTextNode(c_id)
        id_td.appendChild(id_val)
        tr.appendChild(id_td)
        let text_td = document.createElement('td')
        let text_val = document.createTextNode(c_text)
        text_td.appendChild(text_val)
        tr.appendChild(text_td)
        let polarity_td = document.createElement('td')
        let polarity_val = document.createTextNode(c_polarity)
        polarity_td.appendChild(polarity_val)
        tr.appendChild(polarity_td)
        let target_td = document.createElement('td')
        let target_val = document.createTextNode(c_target)
        target_td.appendChild(target_val)
        tr.appendChild(target_td)

        table_with_header.appendChild(tr)

        console.log(typeof c_id, typeof c_text, typeof c_polarity, typeof c_target);
    })
    return table_with_header

}

let table = process_hidden_paginated_rows(current_paginated_row)



function append_table_to_dom(table){
    df_row_table.appendChild(table)
}

append_table_to_dom(table)