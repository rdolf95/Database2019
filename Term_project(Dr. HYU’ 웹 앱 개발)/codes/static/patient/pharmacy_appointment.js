function appointment(){
    var month = $('select[name ="month"]').val()
    var day = $('select[name ="day"]').val()

    // Check month and day is valid.
    if(day == 'default'){
        alert('예약일을 입력하세요.')
        return false;
    }
    switch(month){
        case 'default':
            alert('예약일을 선택하세요.')
            return false;
            break;
        case '4':
        case '6':
        case '9':
        case '11':
            if (day == '31'){
                alert(month + '월은 30일까지 있습니다.')
                return false;
            }
            break;
        case 2:
            if(day >= '30'){
                alert(month + '월은 28(29)일까지 있습니다.')
                return false;
            }
            break;
        default:
            break;
    }

    //check hour and minute is valid
    var hour = $('select[name ="hour"]').val()
    var minute = $('select[name ="minute"]').val()
    if(hour == 'default' || minute == 'default'){
        alert('예약 시간을 선택하세요.')
        return false;
    }

    var form = $("#appo")
    

    console.log(form)
    return true;
}