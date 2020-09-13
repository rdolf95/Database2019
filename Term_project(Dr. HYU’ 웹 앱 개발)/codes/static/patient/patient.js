

function add_frequent(){
    var name = prompt('추가할 병원 이름을 입력하세요');
    if(name == null){
        alert('병원 이름을 입력하세요.')
        return false;
    }
    getHospital(name)
}

function printTable(page){
    currentPage = page
    var tBodyHtml = ''
    var last = 0
    if(page < pageNum){
        last = page*10
        
    }
    else{
        last = (page-1)*10 + remain
        console.log(last)
    }
    
    for (var i = (page-1)*10; i<last; i++){
        row = hospitals[i]
        tBodyHtml +=  `<tr>
        <td>${row['name']}</td>
        <td>${row['addr']}</td>

        <td>
        <form name = 'appo' method="POST" action = "/patient/frequent_hospital">
            <input type = 'hidden' name = 'hid' value = ${row['hid']} />
            <button type = 'submit' onclick = frequent(this) 
                    style = 'height : 25px; width :70px'> 추가하기 </button>
        </form>
        </td>
        </tr>
        `
    }
    $("table#search-result tbody").html(tBodyHtml)
    printPage()
}

function printPage(){
    var tBodyHtml = ''
    if (currentPage <3)
        var first = 1
    else
        var first = currentPage-2
    
    if (currentPage +10 > pageNum)
        var last = pageNum+1
    else
        var last = currentPage+10
    
    for(var i = first; i<last ; i++){
        tBodyHtml +=  `<button onclick = "printTable(${i})"> ${i} </button>`
    }
    tBodyHtml += `<b> page </b>`
    $("div#hospital-list p").html(tBodyHtml)
}

function getHospital(name){
    var data = {name: name}
    $.ajax({
        type: "POST",
        url: '/patient/name_hospital/rest',
        cache: false,
        processData: false,
        contentType: false,
        data: JSON.stringify(data),
        success: res => {
        }
    }).done(data => {
        //console.log(data)
        input = JSON.parse(data)
        hospitals = input[0]
        var length= hospitals.length
        pageNum = length/10
        remain = length%10
        currentPage = 1
        printTable(1, hospitals)
        printPage()
    })
}