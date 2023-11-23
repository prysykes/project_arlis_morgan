const search_input = document.querySelectorAll('.search_input');
const kaggle_filter = document.querySelector('#kaggle_filter');
const result_filter_id = document.querySelector('#result_filter')

kaggle_filter.addEventListener('click', () => {
    result_filter_id.classList.toggle('display-none')
})

search_input.forEach(ele => {
    
    ele.addEventListener('keyup', (event) => {
       
        let current_id = ele.id
        if (current_id == "in_ref") {
            let tr_all = document.querySelectorAll('.result_table tr')
            //get all tr elements from table with class name  result_table
            tr_all.forEach(tr => {
                let index = 0
                let td_inref = tr.childNodes[index ].innerText
                let current_input = document.getElementById(current_id).value.toLowerCase()
                hide_show_rows(tr_all, current_input, index ) 
                
                
            })



        }

        else if (current_id == "in_title") {
            
            let tr_all = document.querySelectorAll('.result_table tr')
            tr_all.forEach(tr => {
                let index = 1
                let td_in_title = tr.childNodes[index ].innerText
                let current_input = document.getElementById(current_id).value.toLowerCase()
                hide_show_rows(tr_all, current_input,index ) 
                
                
            })
        }

        else if (current_id == "in_lastUpdated") {
            let tr_all = document.querySelectorAll('.result_table tr')
            tr_all.forEach(tr => {
                let index  = 3
                let td_in_lastUpdated = tr.childNodes[index ].innerText
                let current_input = document.getElementById(current_id).value.toLowerCase()
                hide_show_rows(tr_all, current_input, index) 
                 
                
            })
            
        };
    })
})


function hide_show_rows(rows, current_input, index) {
    
    for (let i=0; i < rows.length; i++){
        let full_inner_text = rows[i].childNodes[index].innerText.toLowerCase()
        if (full_inner_text.indexOf(current_input) != -1){
            // indexOf returns false if the substring is not part of the main string
            continue
        }else {
            rows[i].classList.add("display-none")
        }
    }
    

   
}