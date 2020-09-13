function timeSelect(text){
    var tr = document.createElement('tr')
    var td = document.createElement('td')
    td.appendChild(document.createTextNode(text))
    tr.appendChild(td)
    
    for(var i = 0; i<7; i++){
        var td = document.createElement('td')
        // make hour selection
        var selec = document.createElement('select')
        // make default option = false
        var defal = document.createElement('option')
        defal.setAttribute('value', false)
        defal.setAttribute('selected', 'selected')
        defal.appendChild(document.createTextNode('시'))
        selec.appendChild(defal)
        // add hour option.
        for(var j=0; j<24; j++){
            var opt = document.createElement('option')
            opt.setAttribute('value', j)
            opt.appendChild(document.createTextNode(parseInt(j)))
            selec.appendChild(opt)
        }
        // append hour selection to td
        td.appendChild(selec)

        // make minute selection.
        var selec = document.createElement('select')
        // make default option = false
        var defal = document.createElement('option')
        defal.setAttribute('value', false)
        defal.setAttribute('selected', 'selected')
        defal.appendChild(document.createTextNode('분'))
        selec.appendChild(defal)
        //add minute option
        for(var j=0; j<60; j++){
            var opt = document.createElement('option')
            opt.setAttribute('value', j)
            opt.appendChild(document.createTextNode(parseInt(j)))
            selec.appendChild(opt)
        }
        // append minute selection to td
        td.appendChild(selec)
        tr.appendChild(td)
    }
    return tr
}

function tableCreate() {
    var divi = document.getElementById('modify_time')
    var tbl = document.createElement('table')
    tbl.setAttribute('id', 'modify_tbl')
    var tbdy = document.createElement('tbody')
    var thed = document.createElement('thead')

    var weekday = new Array()
    weekday = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    var tr = document.createElement('tr')
    // blank head
    var th = document.createElement('th')
    tr.appendChild(th)
    // make head
    for (var i = 0; i < 7; i++){
        var th = document.createElement('th')
        th.appendChild(document.createTextNode(weekday[i]))
        tr.appendChild(th)
    }
    thed.appendChild(tr)

    // make body
    
    tbdy.appendChild(timeSelect('시작시간'))
    tbdy.appendChild(timeSelect('종료시간'))

    var bttn = document.createElement('button')
    //bttn.setAttribute('type', 'submit')
    //bttn.setAttribute('method','POST')
    //bttn.setAttribute('action', '/hospital/work_hour')
    bttn.setAttribute('onclick', 'packForm(this)')
    bttn.appendChild(document.createTextNode('수정하기'))
    
    tbdy.appendChild(bttn)

    tbl.appendChild(thed)
    tbl.appendChild(tbdy)

    divi.appendChild(tbl)
    //body.appendChild(frm)     

    var button = document.getElementById('modify')
    button.disabled = true;
}

function packForm(bttn){
    var tbl = bttn.parentNode
    
	var start = tbl.childNodes[0]
	var end = tbl.childNodes[1]
	// tbl.childNodes[1] = tbody
	var s_tds = start.childNodes
	var e_tds = end.childNodes
	
	var weekstart = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart'] 
	
	var result = {}
	for(var i = 0; i<7; i++){
        var temps ={}
        var hour = s_tds[i+1].childNodes[0]
        var minute = s_tds[i+1].childNodes[1]
        hour = hour.options[hour.selectedIndex].value;
        minute = minute.options[minute.selectedIndex].value;
		temps['hour'] = hour
		temps['minute'] = minute
		
		result[weekstart[i]] = temps
	}
	
	var weekend = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend'] 
	
	for(var i = 0; i<7; i++){
		var temps ={}
        var hour = e_tds[i+1].childNodes[0]
        var minute = e_tds[i+1].childNodes[1]
        hour = hour.options[hour.selectedIndex].value;
        minute = minute.options[minute.selectedIndex].value;
		temps['hour'] = hour
		temps['minute'] = minute
        
		
		result[weekend[i]] = temps
    }
    var json_data = JSON.stringify(result)
    $.ajax({
        type : 'POST',
        url : '/hospital/work_hour',
        cache: false,
        processData: false,
        data : json_data,
        dataType : 'json',
        success : res =>{
            location.reload()
            //$("#work_hour").load(window.location.href + "#work_hour");
            //TODO: 새로고침 해야됨
        }
    })
}