function add_row(){
    var tbd = $('#medicine_tbd')
    var row = "<tr>"
    row += "<td> <input type='text' placeholder='의약품 명칭' style='width:195px;'> </td>"
    row += "<td> <input type='text'  placeholder='1회 투약량' style='width:95px;'> </td>"
    row += "<td> <input type='number' placeholder='1일 투여횟수' style='width:95px;'> </td>"
    row += "<td> <input type='number' placeholder='총 투약일수' style='width95px;'> </td>"
    row += "</tr>"
    tbd.append(row)
}

function pack_forms(){
    console.log('hello')
    var data = {}
    data['year'] = $('input[name ="p_year"]').val()
    data['month'] = $('input[name ="p_month"]').val()
    data['day'] = $('input[name ="p_day"]').val()
    data['hour'] = $('input[name ="p_hour"]').val()
    data['minute'] = $('input[name ="p_minute"]').val()
    
    var name = $('input[name ="p_name"]').val()
    if(name == ''){
        alert('이름을 입력하세요.')
        return false
    }
    data['name'] = name
    var phone = $('input[name ="p_phone"]').val()

    if(!phone){
        alert('전화번호를 입력하세요.')
        return false
    }
    data['phone'] = phone

    var medicine = document.getElementById('medicine').getElementsByTagName('tr')
    var medicine = $('#medicine')

    medicine = medicine.children("tbody").children("tr")
    var medicines = Array()


    for(var i=0; i<medicine.length; i++){
        var row = medicine.eq(i)
        var cols = row.children("td")
        
        medi = {}
        medi['m_name'] = cols.eq(0).children().eq(0).val()
        medi['m_time'] = cols.eq(1).children().eq(0).val()
        medi['m_day'] = cols.eq(2).children().eq(0).val()
        medi['m_total'] = cols.eq(3).children().eq(0).val()
        medicines.push(medi)
    }
    if (medicines.length == 0){
        alert('약을 하나 이상 입력하세요.')
        return false
    }

    data['medicines'] = medicines
    var json_data = JSON.stringify(data)

    $.ajax({
        type : 'POST',
        url : '/hospital/prescribe/getpresc',
        cache: false,
        processData: false,
        data : json_data,
        dataType : 'json',
        success : res =>{
            location.href = '/hospital'
            //$("#work_hour").load(window.location.href + "#work_hour");
            //TODO: 새로고침 해야됨
        }
    })
}