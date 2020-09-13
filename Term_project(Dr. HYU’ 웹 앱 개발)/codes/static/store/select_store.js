

var pageNum;
var currentPage;



function printTable(page){
    currentPage = page
    var tBodyHtml = ''
    var last = 0
    if(page < pageNum){
        last = page*10
        
    }
    else{
        last = (page-1)*10 + remain
    }
    
    for (var i = (page-1)*10; i<last; i++){
        row = pharmacy[i]
        tBodyHtml +=  `<tr>
            <td style=" width: 150px;">${row['name']}</td>
            <td style=" width: 500px">${row['addr']}</td>
            <td>
                <form name = 'appo' method="POST" action = "/store/select_store"> 
                    <input type = 'hidden' name = 'sid' value = ${row['sid']} />
                    <button type = 'submit' style = 'height : 25px; width :70px'> 선택하기 </button>
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
    $("div#pharmacy-list p").html(tBodyHtml)
}

function getStore(){
    var kind = $("#kind").val()
    var name = $("#search").val()
    var data = {name: name,
                kind: kind}
    $.ajax({
        type: "POST",
        url: '/patient/name_store/rest',
        cache: false,
        processData: false,
        contentType: false,
        data: JSON.stringify(data),
        success: res => {
            //console.log(res)
        }
    }).done(data => {
        //console.log(data)
        input = JSON.parse(data)
        pharmacy = input
        var length= pharmacy.length
        pageNum = length/10
        remain = length%10
        currentPage = 1
        printTable(1, pharmacy)
        printPage()
    })
}

function marker_appointment(sid){
    var form = document.createElement("form")
    form.type = "submit"
    form.action = "/patient/pharmacy_appointment"
    form.method="POST" 
    var appo = document.createElement("input")
    appo.type = "hidden"
    appo.name = "sid"
    appo.value = sid

    form.appendChild(appo)
    form.submit()
}