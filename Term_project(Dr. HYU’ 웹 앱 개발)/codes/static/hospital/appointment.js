function confirm(bttn){
    console.log('confirm')
    var row = $(bttn).parents("tr")
    var cols = row.children("td")
    var data = {}
    data['name'] = cols.eq(0).text()
    data['phone'] = cols.eq(1).text()
    data['date'] = cols.eq(3).text()
    data['time'] = cols.eq(4).text()

    var json_data = JSON.stringify(data)
    $.ajax({
        type : 'POST',
        url : '/hospital/appointment/confirm',
        cache: false,
        processData: false,
        data : json_data,
        dataType : 'json',
        success : res =>{
            location.reload()
            //$("#appointment").load(window.location.href + "#appointment");
            //TODO: 새로고침 해야됨
        }
    })
}

function decline(bttn){
    var row = $(bttn).parents("tr")
    var cols = row.children("td")
    var data = {}
    data['name'] = cols.eq(0).text()
    data['phone'] = cols.eq(1).text()
    data['date'] = cols.eq(3).text()
    data['time'] = cols.eq(4).text()

    var json_data = JSON.stringify(data)
    $.ajax({
        type : 'POST',
        url : '/hospital/appointment/decline',
        cache: false,
        processData: false,
        data : json_data,
        dataType : 'json',
        success : res =>{
            location.reload()
            //$("#appointment").load(window.location.href + "#appointment");
            //TODO: 새로고침 해야됨
        }
    })
}