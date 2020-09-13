var container = document.getElementById('map');
var options;
var map;
var hospitals;
var pageNum;
var currentPage;
var markers = []
var infowindows = []
options = {
    center: new kakao.maps.LatLng(0, 0),
    level: 6
};
map = new kakao.maps.Map(container, options);


function chage_center(lat,lng){
    map.setCenter(new kakao.maps.LatLng(lat, lng));
}

function addMarker(position, info, hid) {
    // 마커를 생성합니다
    var marker = new kakao.maps.Marker({
        position: position
    });

    // 마커가 지도 위에 표시되도록 설정합니다
    marker.setMap(map);
    markers.push(marker)
    
    var infowindow = new kakao.maps.InfoWindow({
        content : '<div style="padding:5px;">' + info + '</div>' // 인포윈도우에 표시할 내용
    });

    // 마커에 mouseover 이벤트를 등록한다
    kakao.maps.event.addListener(marker, 'mouseover', function() {
        // 인포윈도우를 지도에 표시한다
        infowindow.open(map, marker);
    });

    // 마커에 mouseout 이벤트 등록
    kakao.maps.event.addListener(marker, 'mouseout', function() {
        // 인포윈도우를 닫는다.
        infowindow.close()
    });

    kakao.maps.event.addListener(marker, 'click', function() {
        marker_appointment(hid)
    });
}

function printTable(page){
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }            
    markers = []
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
        <td style=" width: 150px;">${row['name']}</td>
        <td style=" width: 500px">${row['addr']}</td>
        <td>${row['working'] == 0 ? '진료 불가' 
            : row['working'] == 1 ? '진료 가능'
            : '정보 없음'}
        </td>
        <td>
        <form name = 'appo' method="POST" action = "/patient/make_appointment"> 
            <input type = 'hidden' name = 'hid' value = ${row['hid']} />
            <button type = 'submit' onclick = make_appointment(this) 
                    style = 'height : 25px; width :70px'> 예약하기 </button>
        </form>
        </td>
        </tr>
        `
        addMarker(new kakao.maps.LatLng(row['lat'], row['lng']), row['name'], row['hid'])
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

function getHospital(){
    var name = $("#search").val()
    var data = {name: name}
    $.ajax({
        type: "POST",
        url: '/patient/name_hospital/rest',
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
        options = {
            center: new kakao.maps.LatLng(input[1], input[2]),
            level: 7
        };
        map = new kakao.maps.Map(container, options);
        hospitals = input[0]
        var length= hospitals.length
        pageNum = length/10
        remain = length%10
        currentPage = 1
        printTable(1, hospitals)
        printPage()
    })
}

function marker_appointment(hid){
    var form = document.createElement("form")
    form.type = "submit"
    form.action = "/patient/make_appointment"
    form.method="POST" 
    var appo = document.createElement("input")
    appo.type = "hidden"
    appo.name = "hid"
    appo.value = hid

    form.appendChild(appo)
    form.submit()
}

function make_appointment(bttn){
    var form = $(bttn).parents("form")[0]
    form.submit()
}
