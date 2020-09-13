function cancle(ctl){
    var row = $(ctl).parents("tr")
    var cols = row.children("td")
    p_name = cols.eq(0).text()
    date = cols.eq(2).text()
    time = cols.eq(3).text()
    subject = cols.eq(4).text()
    hid = cols.eq(6).children("input").eq(0).val()
    pid = cols.eq(6).children("input").eq(1).val()
    
    

    // Pack form.
    var form = document.createElement("form")

    var pname_input = document.createElement("input")
    pname_input.type = "hidden"
    pname_input.name = "p_name"
    pname_input.value = p_name
    
    var date_input = document.createElement("input")
    date_input.type = "hidden"
    date_input.name = "date"
    date_input.value = date

    var time_input = document.createElement("input")
    time_input.type = "hidden"
    time_input.name = "time"
    time_input.value = time

    var subject_input = document.createElement("input")
    subject_input.type = "hidden"
    subject_input.name = "subject"
    subject_input.value = subject

    var hid_input = document.createElement("input")
    hid_input.type = "hidden"
    hid_input.name = "hid"
    hid_input.value = hid

    var pid_input = document.createElement("input")
    pid_input.type = "hidden"
    pid_input.name = "pid"
    pid_input.value = pid

    form.appendChild(pname_input)
    form.appendChild(date_input)
    form.appendChild(time_input)
    form.appendChild(subject_input)
    form.appendChild(hid_input)
    form.appendChild(pid_input)

    form.method = 'POST'
    form.action = '/patient/cancle_appointment'

    console.log(form)

    form.submit()
}