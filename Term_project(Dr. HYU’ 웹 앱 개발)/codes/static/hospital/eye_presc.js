
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

    data['l_eye'] = $('input[name ="l_eye"]').val()
    data['r_eye'] = $('input[name ="r_eye"]').val()
    var json_data = JSON.stringify(data)

    $.ajax({
        type : 'POST',
        url : '/hospital/prescribe/eye_presc/getpresc',
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