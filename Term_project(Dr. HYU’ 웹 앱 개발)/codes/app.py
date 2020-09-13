from flask import Flask, render_template, request, redirect, url_for, session
from apicall import hosp_list, pharm_list
from pypg import helper
from datetime import datetime, time, date
import json
import api_data as api_data

app = Flask(__name__)
app.secret_key = 'hard term project'


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def root():
    return render_template("login/login.html")

# When login sucess, redirect to home page or double seletion page.
@app.route('/login_success')
def login_success():
    result = request.args['messages']
    result = json.loads(result)
    kind = result[0]['kind']
    uid = result[0]['uid']

    user_data = {'uid':uid}
    user_data = json.dumps(user_data)
    session['uid'] = uid

    if (kind is None):
        return render_template("login/selection.html", name = result[0]['name'], uid = uid)
    elif kind == 1:
        return redirect(url_for('hospital', messages=user_data))
    elif kind == 2:
        return redirect(url_for('store', messages=user_data))
    elif kind == 4 or kind == 5:
        return render_template("login/double_user.html", 
                name = result[0]['name'] ,uid = uid, kind = kind)
    else :  # kind == 3
        return redirect(url_for('patient', messages=user_data))

# When login fails, try again.
@app.route('/login_fail')
def login_fail():
    return render_template("login/login_fail.html")

# Check the login data.
@app.route('/login', methods = ["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    email = email.split('@')

    
    result = helper.search('client', ['name','kind','uid'], 
                    [('local', '\'' + email[0] + '\''),
                    ('domain', '\'' + email[1] + '\''),
                    ('passwd', '\'' + password + '\'')], 1)
    if(result == []):
        return redirect('/login_fail')
    else:
        result = json.dumps(result)
        return redirect(url_for('login_success', messages=result))

# Select user's type when first login.
@app.route('/selection', methods = ["POST"])
def selection():
    kind = request.form.get("kind")
    uid = request.form.get("uid")

    helper.modify('client', [('uid',uid)], [('kind', kind)], 'uid')

    user_data = {'uid':uid}
    user_data = json.dumps(user_data)
    
    if kind == 1:
        return redirect(url_for('hospital', messages=user_data))
    elif kind == 2:
        return redirect(url_for('store', messages=user_data))
    elif kind == 4 or kind == 5:
        return render_template("login/double_user.html", uid = uid, kind = kind)
    else :  # kind == 3
        return redirect(url_for('patient', messages=user_data))

# Select double type user's type every time when the users login.
@app.route('/dselect', methods = ['POST'])
def double_user_selection():
    kind = request.form.get("kind")
    uid = request.form.get("uid")

    user_data = {'uid':uid}
    user_data = json.dumps(user_data)

    kind = int(kind)
    if kind == 1:
         return redirect(url_for('hospital', messages=user_data))
    elif kind == 2:
        return redirect(url_for('store', messages=user_data))
    else :  # kind == 3
        return redirect(url_for('patient', messages=user_data))

@app.route('/register')
def register():
    return render_template("login/register.html")

@app.route('/register_check', methods = ['POST'])
def register_check():
    email = request.form.get("email")
    password = request.form.get("password")
    email = email.split('@')
    
    result = helper.search('client', ['name','kind','uid'], 
                    [('local', '\'' + email[0] + '\''),
                    ('domain', '\'' + email[1] + '\'')], 1)
    if result != []:
        check = 'fail'
        return render_template("login/register.html",check = check)
    else:
        name = str(request.form.get("name"))
        phone = str(request.form.get("phone"))
        lat = float(request.form.get("lat"))
        lng = float(request.form.get("lng"))
        kind = int(request.form.get('kind'))
        helper.insert('client', [('name', '\'' + name + '\''),
                                 ('local', '\'' + email[0] + '\''),
                                 ('domain', '\'' + email[1] + '\''),
                                 ('passwd', '\'' + password + '\''),
                                 ('phone', '\'' + phone + '\''),
                                 ('lat', lat),
                                 ('lng', lng),
                                 ('kind', kind)])
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('pid', None)
    session.pop('sid', None)
    session.pop('hid', None)
    return redirect('/')

@app.route('/change_profil')
def change_profil():
    uid = session['uid']
    user = helper.search('client', ['local', 'domain', 'name', 'phone', 'passwd', 'kind', 'lat', 'lng'], 
                        [('uid', uid)], 1)[0]

    email = user['local'] + '@' + user['domain']
    return render_template('login/change_profil.html', user = user, email = email)

@app.route('/check_change_profil', methods = ['POST'])
def check_change_profil():
    uid = session['uid']
    email = request.form.get("email")
    password = request.form.get("changed_password")
    email = email.split('@')
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    phone = request.form.get("phone")
    name = request.form.get("name")

    helper.modify('client', [('uid', uid)], 
                  [('local', '\'' + email[0] + '\''), 
                   ('domain', '\'' + email[1] + '\''), 
                   ('lat', lat), 
                   ('lng', lng),
                   ('name', '\'' + name + '\''),
                   ('phone', '\'' + phone + '\''),
                   ('passwd', password)], 'uid')

    return redirect('/')

@app.route('/hospital')
def hospital():
    uid = session['uid']
    uid = int(uid)

    hid = helper.search('h_client', ['hid'], [('uid', uid)],1)

    user = helper.search('client', ['lat', 'lng',], [('uid', uid)], 1)[0]

    if hid == []:
        return render_template("hospital/select_hospital.html", uid = uid)
    session['hid'] = hid[0]['hid']

    startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
    endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']

    ###### get hospital information. ######
    hid = hid[0]['hid']
    target = ['name', 'dnum', 'lat', 'lng', 'addr']
    for i in range(7):
        target.append(startTimes[i])
        target.append(endTimes[i])
    
    hospital = helper.search('hospital', target, [('hid', hid)], 1)
    name = hospital[0]['name']
    dnum = hospital[0]['dnum']
    lat = hospital[0]['lat']
    lng = hospital[0]['lng']
    addr = hospital[0]['addr']
    
    distance = api_data.distance(lat,lng, user['lat'], user['lng'])
    distance = round(distance, 2)

    startTime = []
    endTime = []
    for i in range(7):
        startTime.append(hospital[0][startTimes[i]])
        endTime.append(hospital[0][endTimes[i]])

    ###### get hospital's subject information. #######
    subject = helper.search('h_subject', ['subject'], [('hid', hid)], 100)

    return render_template("hospital/hospital.html", \
        hospital = hospital[0], subjects = subject, startTimes = startTime, endTimes = endTime, distance=distance)

@app.route('/hospital/add_subject', methods = ['POST'])
def hospital_add_subject():
    hid = session['hid']
    subject = '\'' + request.form.get("subject") + '\''
    check = helper.search('h_subject', ['hsid'], [('hid', hid), ('subject', subject)], 1)
    if check == []:
        helper.insert('h_subject', [('hid', hid), ('subject', subject)])
    
    return redirect('/hospital')

@app.route('/hospital/delete_subject', methods = ['POST'])
def hospital_delete_subject():
    hid = session['hid']
    subject = '\'' + request.form.get("subject") + '\''
    check = helper.search('h_subject', ['hsid'], [('hid', hid), ('subject', subject)], 1)
    if check != []:
        helper.delete('h_subject', [('hid', hid), ('subject', subject)], 'hsid')
    
    return redirect('/hospital')

@app.route('/hospital/select_hospital', methods=['POST'])
def select_hospital():
    hospital = request.form.get("name")
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    uid = session['uid']

    user_data = {'uid':uid}
    user_data = json.dumps(user_data)

    hid = helper.search('hospital', ['hid'], [('name', '\'' + hospital + '\''), ('lat', lat), ('lng', lng)], 1)
    if hid == []:
        return redirect(url_for('hospital', messages=user_data))
    hid = hid[0]['hid']
    helper.insert('h_client',[('hid', hid), ('uid', uid)])

    
    return redirect(url_for('hospital', messages=user_data))

@app.route('/hospital/appointment')
def appointment_hospital():
    ###### get appointment information. ########
    uid = session['uid']
    uid = int(uid)
    hid = session['hid']
    hid = int(hid)
    patients = []
    appointments = helper.search('appointment', ['pid', 'time', 'date', 'subject', 'confirm'], [('hid', hid)], 1000)
    
    remove = []
    for appo in appointments:
        if appo['confirm'] != 1 and appo['confirm'] != 0:
            remove.append(appo)
            #appointments.remove(appo)
        else:
            pid = appo['pid']
            pati = helper.search('patient', ['name', 'phone'], [('pid', pid)], 1)
            patients.append(pati[0])

    for rm in remove:
        appointments.remove(rm)
    
    return render_template('/hospital/appointment.html', appointment = appointments, patients = patients)

@app.route('/hospital/appointment/confirm', methods = ['POST'])
def appointment_confirm():
    input = request.get_json(force=True)
    name = input['name'].strip()
    phone = input['phone'].strip()
    date = input['date'].strip()
    time = input['time'].strip()

    pid = helper.search('patient',['pid'], [('name', '\'' + name + '\''), ('phone', '\'' + phone + '\'')], 1)
    pid = pid[0]['pid']
    appointment = helper.modify('appointment', [('pid', pid), ('time', '\'' + time + '\''), ('date', '\'' + date + '\'')], [('confirm', 1)], 'aid')

    return json.dumps({'success':True})

@app.route('/hospital/appointment/decline', methods = ['POST'])
def appointment_decline():
    input = request.get_json(force=True)
    name = input['name'].strip()
    phone = input['phone'].strip()
    date = input['date'].strip()
    time = input['time'].strip()

    pid = helper.search('patient',['pid'], [('name', '\'' + name + '\''), ('phone', '\'' + phone + '\'')], 1)
    pid = pid[0]['pid']
    appointment = helper.modify('appointment', [('pid', pid), ('time', '\'' + time + '\''), ('date', '\'' + date + '\'')], [('confirm', 2)], 'aid')

    return json.dumps({'success':True})

@app.route('/hospital/prescribe')
def prescribe():
    hid = int(session['hid'])
    hospital = helper.search('hospital', ['name'], [('hid', hid)], 1)
    hospital = hospital[0]['name']
    now = datetime.now() 

    return render_template("hospital/prescription.html", hospital = hospital, 
            year = now.year, month = str(now.month).zfill(2), day = str(now.day).zfill(2), hour = str(now.hour).zfill(2), minute = str(now.minute).zfill(2))

# 안과 처방하기
@app.route('/hospital/prescribe/eye_presc')
def eye_presc():
    hid = int(session['hid'])
    hospital = helper.search('hospital', ['name'], [('hid', hid)], 1)
    hospital = hospital[0]['name']
    now = datetime.now() 

    return render_template('hospital/eye_presc.html', hospital = hospital, 
            year = now.year, month = str(now.month).zfill(2), day = str(now.day).zfill(2), hour = str(now.hour).zfill(2), minute = str(now.minute).zfill(2))

@app.route('/hospital/prescribe/eye_presc/getpresc', methods = ['POST'])
def get_eye_presc():
    input = request.get_json(force=True)
    name = '\'' + input['name'] + '\''
    phone = '\'' + input['phone'] + '\''
    year = input['year']
    month = input['month']
    day = input['day']
    hour = input['hour']
    minute = input['minute']
    l_eye = '\'' + input['l_eye'] + '\''
    r_eye = '\'' + input['r_eye'] + '\''

    patient = helper.search('patient', ['pid'], [('name', name), ('phone', phone)], 1)
    if patient == []:
        helper.insert('patient', [('name', name), ('phone', phone)])
        patient = helper.search('patient', ['pid'], [('name', name), ('phone', phone)], 1)
    
    pid = patient[0]['pid']
    hid = session['hid']
    date = '\'' + year + month + day + '\''
    time = '\'' + hour + minute + '\''

    uid = 0
    # Delete appointment if exist.
    appointments = helper.search('appointment', 
                    ['aid', 'time', 'uid'], [('hid', hid), ('pid', pid), ('date', date), ('confirm', 1)], 100)
    if appointments != []:
        # Find oldest one.
        oldest = appointments[0]
        for appo in appointments:
            if appo['time'] < oldest['time']:
                oldest = appo
        # Save appointment's user id.
        uid = oldest['uid']
        # Delete oldest one.
        helper.delete('appointment', [('aid', oldest['aid'])], 'aid')

    # Make prescription.
    if uid == 0:
        target = [('hid', hid), ('pid', pid), ('presc_date', date), ('presc_time', time), ('presc_done', 0), ('etc','\'' + '안경처방전' + '\'')]
    else:
        target =  [('hid', hid), ('pid', pid), ('presc_date', date), 
                   ('presc_time', time), ('presc_done', 0), ('uid', uid), ('etc', '\'' +'안경처방전' + '\'')]
    helper.insert('prescription', target)
    prid = helper.search('prescription', ['prid'], 
        [('hid', hid), ('pid', pid), ('presc_date', date), ('presc_time', time), ('presc_done', 0)], 1)[0]['prid']

    # insert eye prescription.
    helper.insert('p_eye', [('prid', prid), ('l_eye', l_eye), ('r_eye', r_eye)])
    
    return json.dumps({'success':True})


@app.route('/hospital/prescribe/getpresc', methods = ['POST'])
def getpresc():
    input = request.get_json(force=True)
    name = '\'' + input['name'] + '\''
    phone = '\'' + input['phone'] + '\''
    year = input['year']
    month = input['month']
    day = input['day']
    hour = input['hour']
    minute = input['minute']

    patient = helper.search('patient', ['pid'], [('name', name), ('phone', phone)], 1)
    if patient == []:
        helper.insert('patient', [('name', name), ('phone', phone)])
        patient = helper.search('patient', ['pid'], [('name', name), ('phone', phone)], 1)
    
    pid = patient[0]['pid']
    hid = session['hid']
    date = '\'' + year + month + day + '\''
    time = '\'' + hour + minute + '\''

    uid = 0
    # Delete appointment if exist.
    appointments = helper.search('appointment', 
                    ['aid', 'time', 'uid'], [('hid', hid), ('pid', pid), ('date', date), ('confirm', 1)], 100)
    if appointments != []:
        # Find oldest one.
        oldest = appointments[0]
        for appo in appointments:
            if appo['time'] < oldest['time']:
                oldest = appo
        # Save appointment's user id.
        uid = oldest['uid']
        # Delete oldest one.
        helper.delete('appointment', [('aid', oldest['aid'])], 'aid')

    # Make prescription.
    if uid == 0:
        target = [('hid', hid), ('pid', pid), ('presc_date', date), ('presc_time', time), ('presc_done', 0)]
    else:
        target =  [('hid', hid), ('pid', pid), ('presc_date', date), 
                   ('presc_time', time), ('presc_done', 0), ('uid', uid)]
    helper.insert('prescription', target)

    # Make prescription - medicine relation. 
    prid = helper.search('prescription', ['prid'], 
        [('hid', hid), ('pid', pid), ('presc_date', date), ('presc_time', time), ('presc_done', 0)], 1)[0]['prid']

    medicines = input['medicines']
    for medi in medicines:
        helper.insert('p_medicine', [('prid', prid), ('name', '\'' + medi['m_name'] + '\''), \
            ('total', medi['m_total']), ('day', medi['m_day']), ('amount', '\'' + medi['m_time'] + '\'')])

    return json.dumps({'success':True})

@app.route('/hospital/work_hour', methods = ['POST'])
def work_hour():
    input = request.get_json(force=True)
    week = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart',
                 'monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']


    newData = []

    for i in range(14):
        if input[week[i]]['hour'] != 'false' and input[week[i]]['minute'] != 'false':
            hour = input[week[i]]['hour'] 
            minute = input[week[i]]['minute']

            if(int(hour) < 10):
                hour = '0' + hour
            if(int(minute) < 10):
                minute = '0' + minute
            time = '\'' + hour + minute + '\''
            newData.append((week[i], time))

    hid = session['hid']

    if newData != []:
        helper.modify('hospital', [('hid', hid)], newData, 'hid')

    return json.dumps({'success':True})

@app.route('/hospital/record')
def patient_record():
    hid = session['hid']
    patients = helper.search('prescription', ['pid','presc_date', 'presc_time', 'prid'], [('hid', hid)], 10000)
    for patient in patients:
        pati = helper.search('patient', ['name', 'phone'], [('pid', patient['pid'])], 1)
        patient['name'] = pati[0]['name']
        patient['phone'] = pati[0]['phone']
    
    return render_template('/hospital/record.html', patients = patients)

@app.route('/hospital/record/showpresc', methods = ['POST'])
def show_presc():
    # TODO : 처음부터 다시하기
    prid = request.form.get("prid")
    #prid = prid['prid']
    hid = session['hid']
    
    hospital = helper.search('hospital', ['name'], [('hid', hid)],1)
    prescription = helper.search('prescription', ['pid', 'presc_time', 'presc_date'], [('prid', prid)], 1)
    pid = prescription[0]['pid']
    patient = helper.search('patient', ['name', 'phone'], [('pid', pid)],1)
    medicines = helper.search('p_medicine', ['name', 'total', 'day', 'amount'], [('prid', prid)], 1000)
    eye = helper.search('p_eye', ['l_eye', 'r_eye'], [('prid', prid)], 1)



    return render_template('/hospital/record_prescription.html', 
            patient = patient[0], prescription = prescription[0], 
            medicines = medicines, hospital = hospital[0]['name'], eye = eye)

@app.route('/hospital/record/rest', methods = ['POST'])
def search_record():
    # Get searching distance from input.
    input = request.get_json(force=True)
    name = input['name']
    phone = input['phone']
    month = int(input['month'])
    day = int(input['day'])

    # Get appointmnet date.
    today = datetime.today()
    year = today.year

    record_date = date(year, month, day)
    record_date = '\'' + record_date.strftime('%Y-%m-%d') + '\''

    pid = helper.search('patient', ['pid'], [('name', '\'' + name + '\''), ('phone', '\'' + phone + '\'')], 1)
    if pid == []:
        return 'no'
    
    else:
        pid = pid[0]['pid']

    prescription = helper.search('prescription', ['presc_date','presc_time'], 
        [('pid', pid), ('presc_date', record_date)], 100)

    for presc in prescription:
        presc['p_name'] = name
        presc['p_phone'] = phone
        presc['presc_date'] = presc['presc_date'].strftime('%Y-%m-%d')
        presc['presc_time'] = presc['presc_time'].strftime('%H:%M:%S')

    return_val = json.dumps((prescription))
    
    return return_val

@app.route('/patient')
def patient():
    # get uid from session
    uid = session['uid']
    # get user data from DB
    user = helper.search('client', ['name', 'phone'], [('uid', uid)], 1)
    name = '\'' + user[0]['name'] + '\''
    phone = '\'' +  user[0]['phone'] + '\''
    # get user's pid from DB
    pid = helper.search('patient', ['pid'], [('name', name), ('phone', phone)], 1)

    # if user's pid doesn't exist, insert user as patient.
    if pid == []:
        helper.insert('patient', [('name', name), ('phone', phone)])
        pid = helper.search('patient', ['pid'], [('name', name), ('phone', phone)], 1)

    # set session's pid.
    pid = int(pid[0]['pid'])
    session['pid'] = pid

    # search recently visted hospital in prescription table.
    sql = f'''SELECT *
              FROM (SELECT DISTINCT hid, pid
                    FROM prescription pr
                    WHERE pr.uid = {uid}) AS presc
              LIMIT 5
           '''
    r_hospital = helper.special_sql(sql)

    # search frequently visiting hospital in f_hospital table.
    f_hospital = helper.search('f_hospital', ['hid'], [('uid', uid)], 5)

    # get each hospital's name
    recent_hos = []
    frequent_hos = []

    for recent in r_hospital:
        h_name = helper.search('hospital', ['name'], [('hid', recent['hid'])], 1)
        recent_hos.append({'name':h_name[0]['name'], 'hid':recent['hid']})
    
    for frequent in f_hospital:
        h_name = helper.search('hospital', ['name'], [('hid', frequent['hid'])], 1)
        frequent_hos.append({'name':h_name[0]['name'], 'hid':frequent['hid']})

    return render_template("patient/patient.html", recent_hos = recent_hos, frequent_hos = frequent_hos)

@app.route('/patient/close_hospital')
def close_hospital():
    return render_template("patient/close_hospital.html")

@app.route('/patient/close_hospital/rest', methods = ['POST'])
def search_close_hospital():
    # Get searching distance from input.
    input = request.get_json(force=True)
    distance = (input['distance'] * 0.621371)/1000

    # Get uid from session.
    uid = session['uid']

    # Get user's location from DB
    user = helper.search('client', ['lat', 'lng'], [('uid', uid)], 1)
    lat = user[0]['lat']
    lng = user[0]['lng']

    # Save data with respect to standard point.
    api_data.get_hospital_data(lat, lng)

    # Get today data.
    startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
    endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']
    today = datetime.today()
    weekday = today.weekday()
    startTime = startTimes[weekday]
    endTime = endTimes[weekday]

    # Search hospitals closer than input distance.
    sql = f'''
            SELECT h.hid, h.name, h.addr, h.{startTime}, h.{endTime}, h.lat, h.lng
            FROM hospital h
            WHERE {distance} >= (SELECT (POINT({lat},{lng}) <@> POINT(h.lat,h.lng)) AS distance);
           '''
    close_hospitals = helper.special_sql(sql)
    
    # Check hospital is working now.
    # 0 -> not working, 1 -> working now, 2 -> No info.
    for close_hos in close_hospitals:
        close_hos['working'] = 1
        # Check start time.
        
        if close_hos[startTime] is not None:
            if today.time() < close_hos[startTime]:
                close_hos['working'] = 0
        else:
             close_hos['working'] = 2
        # Check end time.
        if close_hos[endTime] is not None:
            if today.time() > close_hos[endTime]:
                close_hos['working'] = 0
        else:
             close_hos['working'] = 2

        # Delete time field.
        close_hos.pop(startTime, None)
        close_hos.pop(endTime, None)

    return_val = json.dumps((close_hospitals, lat, lng))
    
    #close_hospitals = json.dumps(close_hospitals)

    return return_val

@app.route('/patient/subject_hospital')
def subject_hospital():
    uid = session['uid']
    user = helper.search('client', ['lat', 'lng'], [('uid', uid)], 1)[0]

    subject = ["일반의", "내과", "신경과", "정신건강의학과" ,"외과","정형외과","신경외과","흉부외과","성형외과",
            "마취통증의학과","산부인과","소아청소년과","안과","이비인후과","피부과","비뇨의학과","영상의학과",
            "방사선종양학과","병리과","진단검사의학과","결핵과","재활의학과","핵의학과","가정의학과","응급의학과",
            "직업환경의학과","예방의학과","치과","한방","약국","보건","보건기관의과","보건기관치과","보건기관한방",
            "치과","구강악안면외과","치과보철과","치과교정과","소아치과","치주과","치과보존과","구강내과","영상치의학과",
            "구강병리과","예방치과","치과소계","통합치의학과","한방내과","한방부인과","한방소아과","한방안·이비인후·피부과",
            "한방신경정신과","침구과","한방재활의학과","사상체질과","한방응급","한방응급","한방소계"]

    return render_template("patient/subject_hospital.html", 
                            subjects = subject, lat = user['lat'], lng = user['lng'])

@app.route('/patient/subject_hospital/rest', methods = ['POST'])
def search_subject_hospital():
    # Get searching distance from input.
    input = request.get_json(force=True)
    name = input['name']

    # Get uid from session.
    uid = session['uid']

    # Get user's location from DB
    user = helper.search('client', ['lat', 'lng'], [('uid', uid)], 1)
    lat = user[0]['lat']
    lng = user[0]['lng']

    # Get today data.
    startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
    endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']
    today = datetime.today()
    weekday = today.weekday()
    startTime = startTimes[weekday]
    endTime = endTimes[weekday]

    # Search hospitals closer than input distance.
    sql = f'''
            SELECT h.hid, h.name, h.addr, h.{startTime}, h.{endTime}, h.lat, h.lng
            FROM hospital h
            WHERE h.name LIKE '%{name}%';
           '''
    close_hospitals = helper.special_sql(sql)
    
    # Check hospital is working now.
    # 0 -> not working, 1 -> working now, 2 -> No info.
    for close_hos in close_hospitals:
        close_hos['working'] = 1
        # Check start time.
        
        if close_hos[startTime] is not None:
            if today.time() < close_hos[startTime]:
                close_hos['working'] = 0
        else:
             close_hos['working'] = 2
        # Check end time.
        if close_hos[endTime] is not None:
            if today.time() > close_hos[endTime]:
                close_hos['working'] = 0
        else:
             close_hos['working'] = 2

        # Delete time field.
        close_hos.pop(startTime, None)
        close_hos.pop(endTime, None)

    return_val = json.dumps((close_hospitals, lat, lng))
    
    return return_val

@app.route('/patient/name_hospital')
def name_hospital():
    uid = session['uid']
    user = helper.search('client', ['lat', 'lng'], [('uid', uid)], 1)[0]
    return render_template("patient/name_hospital.html", lat = user['lat'], lng = user['lng'])

@app.route('/patient/name_hospital/rest', methods = ['POST'])
def search_name_hospital():
    # Get searching distance from input.
    input = request.get_json(force=True)
    name = input['name']

    # Get uid from session.
    uid = session['uid']

    # Get user's location from DB
    user = helper.search('client', ['lat', 'lng'], [('uid', uid)], 1)
    lat = user[0]['lat']
    lng = user[0]['lng']

    # Get today data.
    startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
    endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']
    today = datetime.today()
    weekday = today.weekday()
    startTime = startTimes[weekday]
    endTime = endTimes[weekday]

    # Search hospitals closer than input distance.
    sql = f'''
            SELECT h.hid, h.name, h.addr, h.{startTime}, h.{endTime}, h.lat, h.lng
            FROM hospital h
            WHERE h.name LIKE '%{name}%';
           '''
    close_hospitals = helper.special_sql(sql)
    
    # Check hospital is working now.
    # 0 -> not working, 1 -> working now, 2 -> No info.
    for close_hos in close_hospitals:
        close_hos['working'] = 1
        # Check start time.
        
        if close_hos[startTime] is not None:
            if today.time() < close_hos[startTime]:
                close_hos['working'] = 0
        else:
             close_hos['working'] = 2
        # Check end time.
        if close_hos[endTime] is not None:
            if today.time() > close_hos[endTime]:
                close_hos['working'] = 0
        else:
             close_hos['working'] = 2

        # Delete time field.
        close_hos.pop(startTime, None)
        close_hos.pop(endTime, None)

    return_val = json.dumps((close_hospitals, lat, lng))
    
    return return_val

@app.route('/patient/make_appointment', methods = ['POST'])
def make_appointment():
    # get hospital's name parameter.
    hid = request.form.get('hid')
    startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
    endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']
    # search hospital data with name.
    target = ['hid', 'name', 'dnum','addr']
    target = target + startTimes + endTimes
    hospital = helper.search('hospital', target, [('hid', hid)], 1)[0]

    # seperate general data, start time and end time.
    startTime = []
    endTime = []
    for i in range(7):
        startTime.append(hospital[startTimes[i]])
        endTime.append(hospital[endTimes[i]])
    # get hid.
    hid = hospital['hid']

    # Seperate general data
    hos = {}
    hos['name'] = hospital['name']
    hos['dnum'] = hospital['dnum']
    hos['addr'] = hospital['addr']

    # Get subject data.
    subjects = helper.search('h_subject', ['subject'], [('hid', hid)], 100)

    return render_template("patient/make_appointment.html", 
        hid = hid, hospital = hos, startTimes = startTime, endTimes = endTime, subjects = subjects)

@app.route('/patient/check_appointment')
def appointment_check():
    uid = session['uid']
    
    # Search appointment.
    appointments = helper.search('appointment', ['pid','hid', 'time', 'date', 'subject', 'confirm'], 
                                                [('uid', uid)], 100)
    # Search hospital.
    for appo in appointments:
        hid = appo['hid']
        hospital = helper.search('hospital', ['name'], [('hid', hid)], 1)
        appo['h_name'] = hospital[0]['name']
        appo['time'] = str(appo['time'])
        appo['date'] = str(appo['date'])

    # search patient.
    for appo in appointments:
        pid = appo['pid']
        patient = helper.search('patient', ['name'], [('pid', pid)], 1)
        appo['p_name'] = patient[0]['name']


    return render_template("patient/check_appointment.html", appointments = appointments)

@app.route('/patient/appointment', methods = ['POST'])
def patient_appointment():
    # Get data from submitted form.
    hid = int(request.form.get('hid'))
    month = int(request.form.get('month'))
    day = int(request.form.get('day'))
    hour = int(request.form.get('hour'))
    minute = int(request.form.get('minute'))
    name = '\'' + request.form.get('name') + '\''
    phone = '\'' + request.form.get('phone') + '\''
    subject = '\'' + request.form.get('subject') + '\''
    uid = session['uid']

    # get patient id
    pid = helper.search('patient',['pid'], [('name', name), ('phone', phone)], 1)

    if pid == []:
        helper.insert('patient', [('name', name), ('phone', phone)])
        pid = helper.search('patient',['pid'], [('name', name), ('phone', phone)], 1)
    
    pid = pid[0]['pid']

    startTimes = ['monstart', 'tuestart', 'wedstart', 'thustart', 'fristart', 'satstart', 'sunstart']
    endTimes = ['monend', 'tueend', 'wedend', 'thuend', 'friend', 'satend', 'sunend']
    # Get appointmnet date.
    today = datetime.today()
    year = today.year
    appo_date = date(year, month, day)
    appo_time = time(hour, minute)
    weekday = appo_date.weekday()

    # Check the appointment are aleady made.
    check_appo = helper.search('appointment', ['aid'], 
        [('date', '\'' + appo_date.strftime('%Y-%m-%d') + '\''), 
         ('time', '\'' + appo_time.strftime('%H:%M:%S') + '\''), 
         ('hid', hid), ('pid', pid)], 1)

    if check_appo != []:
        return redirect('/patient/check_appointment')

    # Check will be updated when can't make appointmnet
    check = 0

    # Check hospital is working on that time.
    work_hour = helper.search('hospital', [startTimes[weekday], endTimes[weekday]], [('hid', hid)], 1)
    
    start = work_hour[0][startTimes[weekday]]
    end = work_hour[0][endTimes[weekday]]
    if start is not None:
        if start > appo_time:
            check = 3
    if end is not None:
        if end < appo_time:
            check = 3

    # Check appointment is already exist in that time.
    check_appo = helper.special_sql(f'''
                                    SELECT aid 
                                    FROM appointment
                                    WHERE time = '{appo_time.strftime('%H:%M:%S')}' AND subject = {subject}
                                    LIMIT 1;
                                    ''')
    if check_appo != []:
        check = 4

    # Create new appointment.
    helper.insert('appointment', [('pid', pid), ('hid', hid), ('subject', subject), ('confirm', check), ('uid', uid),
                                  ('date', '\'' + appo_date.strftime('%Y-%m-%d') + '\''), 
                                  ('time', '\'' + appo_time.strftime('%H:%M:%S') + '\'')])


    return redirect('/patient/check_appointment')

@app.route('/patient/cancle_appointment', methods = ['POST'])
def cancle_appointment():
    # Get data form the submited form.
    date = '\'' + request.form.get('date') + '\''
    time = '\'' + request.form.get('time') + '\''
    subject = '\'' + request.form.get('subject') + '\''
    hid = request.form.get('hid')
    pid = request.form.get('pid')

    # Delete appointment.
    helper.delete('appointment', 
        [('hid', hid), ('pid', pid), ('date', date), ('time', time), ('subject', subject)], 'aid')

    return redirect('/patient/check_appointment')

@app.route('/patient/frequent_hospital', methods = ['POST'])
def frequent_hospital():
    hid = request.form.get('hid')

    # Get pid from session.
    uid = session['uid']

    # Check input hospital aleady exist in frequently visiting hospital table.
    fid = helper.search('f_hospital', ['fid'], [('uid', uid), ('hid', hid)], 1)
    if fid != []:
        return redirect('/patient')

    # Check the number of frequently visiting hospital is over 5.
    # IF it is, delete oldest one.
    fids = helper.search('f_hospital', ['fid'], [('uid', uid)], 10)
    if len(fids) >= 5:
        # Get oldest fid
        min = fids[0]['fid']
        for fid in fids:
            if min > fid['fid']:
                min = fid['fid']
        # Delete oldest one.
        helper.delete('f_hospital', [('fid', min)], 'fid')

    # insert new one.
    helper.insert('f_hospital', [('uid', uid), ('hid', hid)])
    return redirect('/patient')

@app.route('/patient/close_pharmacy')
def close_pharmacy():
    return render_template("patient/close_pharmacy.html")

@app.route('/patient/close_pharmacy/rest', methods = ['POST'])
def search_close_pharmacy():
    # Get searching distance from input.
    input = request.get_json(force=True)
    distance = input['distance']/1000
    kind = input['kind']

    # Get uid from session.
    uid = session['uid']

    # Get user's location from DB
    user = helper.search('client', ['lat', 'lng'], [('uid', uid)], 1)
    lat = user[0]['lat']
    lng = user[0]['lng']

    # Save data with respect to standard point.
    api_data.get_pharmacy_data(lat, lng)

    # Search pharmacy closer than input distance.
    if kind == '0':
        sql = f'''
                SELECT p.sid, p.name, p.addr, p.lat, p.lng
                FROM store p
                WHERE {distance} >= (SELECT (POINT({lat},{lng}) <@> POINT(p.lat,p.lng)) AS distance);
            '''
    else:
         sql = f'''
                SELECT p.sid, p.name, p.addr, p.lat, p.lng
                FROM store p
                WHERE {distance} >= (SELECT (POINT({lat},{lng}) <@> POINT(p.lat,p.lng)) AS distance)
                AND p.kind = {kind};
            '''

    close_pharmacy = helper.special_sql(sql)

    return_val = json.dumps((close_pharmacy, lat, lng))
    return return_val

@app.route('/patient/name_store')
def name_store():
    return render_template('/patient/name_store.html')

@app.route('/patient/name_store/rest', methods = ['POST'])
def search_name_store():
    # Get searching distance from input.
    input = request.get_json(force=True)
    name = input['name']
    kind = input['kind']

    print(kind)

    if kind != '1':
        # Search hospitals closer than input distance.
        sql = f'''
                SELECT s.sid, s.name, s.addr
                FROM store s
                WHERE s.name LIKE '%{name}%';
            '''
        name_store = helper.special_sql(sql)
    else:
        # Search hospitals closer than input distance.
        sql = f'''
                SELECT s.sid, s.name, s.addr
                FROM store s
                WHERE s.name LIKE '%{name}%' AND s.kind = 1;
            '''
        name_store = helper.special_sql(sql)

    return_val = json.dumps((name_store))
    
    return return_val

@app.route('/patient/pharmacy_appointment', methods = ['POST'])
def appoint_pharmacy():
    # Get sid from submitted form.
    sid = request.form.get('sid')
    # Get pharmacy data from DB.
    store = helper.search('store', ['sid', 'name', 'addr', 'kind'], [('sid', sid)], 1)[0]
    
    # Get uid from session.
    uid = session['uid']
    # Get prescriptions with uid.
    presc = helper.search('prescription', ['prid', 'pid', 'hid', 'presc_date', 'presc_time', 'etc'], [('uid', uid), ('presc_done', 0)], 100)

    # Get hospital and patient name.
    for prescription in presc:
        hos = helper.search('hospital', ['name'], [('hid', prescription['hid'])], 1)
        pat = helper.search('patient', ['name'], [('pid', prescription['pid'])], 1)
        prescription['h_name'] = hos[0]['name']
        prescription['p_name'] = pat[0]['name']

    return render_template('patient/pharmacy_appointment.html', store = store, prescriptions = presc)

@app.route('/patient/make_store_appointment', methods = ['POST'])
def make_store_appointment():
    sid = request.form.get('sid')
    prid = request.form.get('prid')

    helper.modify('prescription', [('prid', prid)], [('sid', sid), ('presc_done', 0)], 'prid')
    return redirect('/patient')

@app.route('/patient/check_store_appointment')
def check_store_appointment():
    uid = session['uid']
    
    
    # Search appointment.
    appointments = helper.search('prescription', 
                    ['prid', 'pid','hid', 'sid', 'presc_time', 'presc_date', 'presc_done'], 
                    [('uid', uid)], 100)
    f_appo = []
    # Search hospital, patient, store.
    for appo in appointments:
        if appo['presc_done'] == 1: #done
            continue
        if appo['sid'] is None:
            continue
        
        hid = appo['hid']
        hospital = helper.search('hospital', ['name'], [('hid', hid)], 1)
        appo['h_name'] = hospital[0]['name']

        pid = appo['pid']
        patient = helper.search('patient', ['name'], [('pid', pid)], 1)
        appo['p_name'] = patient[0]['name']

        sid = appo['sid']
        store = helper.search('store', ['name'], [('sid', sid)], 1)
        appo['s_name'] = store[0]['name']

        # Change date, time to string.
        appo['presc_date'] = str(appo['presc_date'])
        appo['presc_time'] = str(appo['presc_time'])
        f_appo.append(appo)

    
    return render_template("patient/check_store_appointment.html", appointments = f_appo)

@app.route('/patient/cancle_store_appointment', methods = ['POST'])
def cancle_store_appointment():
    prid = request.form.get('prid')
    state = request.form.get('state')

    helper.modify('prescription', [('prid', prid)], [('sid', 'NULL'), ('presc_done', 0)], 'prid')
    return redirect('/patient/check_store_appointment')

@app.route('/patient/show_prescription')
def patient_show_prescription():
    # Get uid from session.
    uid = session['uid']
    # Get prescriptions with uid.
    presc = helper.search('prescription', ['prid', 'pid', 'hid', 'presc_date', 'presc_time'], [('uid', uid)], 100)

    # Get hospital and patient name.
    for prescription in presc:
        hos = helper.search('hospital', ['name'], [('hid', prescription['hid'])], 1)
        pat = helper.search('patient', ['name'], [('pid', prescription['pid'])], 1)
        prescription['h_name'] = hos[0]['name']
        prescription['p_name'] = pat[0]['name']

    return render_template('patient/show_prescription.html', prescriptions = presc)

@app.route('/patient/show_prescription/show_detail', methods = ['POST'])
def patient_show_prescription_detail():
    prid = request.form.get('prid')

    prescription = helper.search('prescription', 
        ['pid', 'hid', 'sid', 'presc_time', 'presc_date', 'prepare_date', 'prepare_time', 'etc','presc_done'], [('prid', prid)], 1)[0]
    
    hospital = helper.search('hospital', ['name'], [('hid', prescription['hid'])],1)[0]
    pid = prescription['pid']
    patient = helper.search('patient', ['name', 'phone'], [('pid', pid)],1)[0]
    prescription['s_name'] = 0
    if prescription['sid'] is not None:
        store = helper.search('store', ['name'], [('sid', prescription['sid'])], 1)[0]
        prescription['s_name'] = store['name']

    prescription['h_name'] = hospital['name']
    prescription['p_name'] = patient['name']
    prescription['p_phone'] = patient['phone']
    prescription['etc'] = prescription['etc'].replace(" ", "")

    medicines = helper.search('p_medicine', ['name', 'total', 'day', 'amount'], [('prid', prid)], 1000)
    eye = helper.search('p_eye', ['l_eye', 'r_eye'], [('prid', prid)], 1)
    
    return render_template('patient/show_prescription_detail.html', 
                            prescription = prescription, medicines = medicines, eye = eye)

@app.route('/store')
def store():
    uid = session['uid']
    uid = int(uid)

    sid = helper.search('s_client', ['sid'], [('uid', uid)],1)
    
    if sid == []:
        return render_template("store/select_store.html")

    sid = sid[0]['sid']
    session['sid'] = sid
    target = ['name', 'kind', 'lat', 'lng', 'addr']
    
    store = helper.search('store', target, [('sid', sid)], 1)
    
    return render_template("store/store.html", store = store[0])

@app.route('/store/select_store', methods=['POST'])
def select_store():

    sid = request.form.get("sid")
    uid = session['uid']

    helper.insert('s_client',[('sid', sid), ('uid', uid)])
    return redirect('/store')

@app.route('/store/appointment')
def store_appointment():
    sid = session['sid']
    prescriptions = helper.search('prescription', ['prid', 'hid', 'pid', 'presc_date', 'presc_time', 'presc_done'],
                          [('sid', sid)], 10000)
    
    remove = []
    for presc in prescriptions:
        if presc['presc_done'] != 0:
            remove.append(presc)
            #prescriptions.remove(presc)
            continue
        hospital = helper.search('hospital', ['name'], [('hid', presc['hid'])], 1)[0]
        presc['h_name'] = hospital['name']
        patient = helper.search('patient', ['name', 'phone'], [('pid', presc['pid'])], 1)[0]
        presc['p_name'] = patient['name']
        presc['p_phone'] = patient['phone']
    
    for rm in remove:
        prescriptions.remove(rm)

    print(prescriptions)

    return render_template('store/appointment.html', appointment = prescriptions)

@app.route('/store/show_prescription', methods = ['POST'])
def store_show_prescription():
    # Get prid and sid from form and session.
    prid = request.form.get('prid')

    prescription = helper.search('prescription', 
                   ['prid', 'hid', 'pid', 'presc_time', 'presc_date'], [('prid', prid)], 1)[0]
    
    hospital = helper.search('hospital', ['name'], [('hid', prescription['hid'])], 1)[0]
    patient = helper.search('patient', ['name', 'phone'], [('pid', prescription['pid'])], 1)[0]

    medicines = helper.search('p_medicine', ['name', 'total', 'day', 'amount'], [('prid', prid)], 100)
    eye = helper.search('p_eye', ['l_eye', 'r_eye'], [('prid', prid)], 1)

    return render_template('/store/show_prescription.html', 
                    prescription = prescription, hospital = hospital, patient = patient, medicines = medicines, eye = eye)

@app.route('/store/prescribe', methods = ['POST'])
def store_prescribe():
    prid = request.form.get('prid')
    etc = '\'' + request.form.get('etc') + '\''

    now = datetime.today()
    time = '\'' + now.strftime('%H:%M') + '\''
    date = '\'' + now.strftime('%Y-%m-%d') + '\''

    helper.modify('prescription', [('prid', prid)], 
                  [('prepare_time', time), ('prepare_date', date), ('etc', etc), ('presc_done', 1)], 'prid')

    return redirect('/store/record')

@app.route('/store/cancle_appointment', methods = ['POST'])
def store_cancle_appointment():
    prid = request.form.get('prid')
    helper.modify('prescription', [('prid', prid)], [('presc_done', 2)], 'prid')
    return redirect('/store/appointment')

@app.route('/store/record')
def store_record():
    sid = session['sid']
    prescriptions = helper.search('prescription', 
                          ['prid', 'hid', 'pid', 'prepare_date', 'prepare_time', 'presc_done'],
                          [('sid', sid)], 10000)

    for presc in prescriptions:
        if presc['presc_done'] != 1:
            prescriptions.remove(presc)
            continue
        hospital = helper.search('hospital', ['name'], [('hid', presc['hid'])], 1)[0]
        presc['h_name'] = hospital['name']
        patient = helper.search('patient', ['name', 'phone'], [('pid', presc['pid'])], 1)[0]
        presc['p_name'] = patient['name']
        presc['p_phone'] = patient['phone']

    

    return render_template('store/record.html', prescription = prescriptions)

@app.route('/store/record/presc_detail', methods = ['POST'])
def store_presc_detail():
    prid = request.form.get('prid')
    sid = session['sid']
    print(prid)

    presc = helper.search('prescription', 
                          ['prid', 'hid', 'pid', 'prepare_date', 'prepare_time', 
                          'presc_done', 'presc_time', 'presc_date', 'etc'],
                          [('prid', prid)], 1)[0]

    hospital = helper.search('hospital', ['name'], [('hid', presc['hid'])], 1)[0]
    presc['h_name'] = hospital['name']
    patient = helper.search('patient', ['name', 'phone'], [('pid', presc['pid'])], 1)[0]
    presc['p_name'] = patient['name']
    presc['p_phone'] = patient['phone']
    store = helper.search('store', ['name'], [('sid', sid)], 1)[0]
    presc['s_name'] = store['name']
    presc['etc'] = presc['etc'].replace(" ","")
    if presc['etc'] == "":
        presc['etc'] = "정보없음"


    medicines = helper.search('p_medicine', ['name', 'total', 'day', 'amount'], [('prid', prid)], 100)

    return render_template('store/presc_detail.html', prescription = presc, medicines = medicines)

if __name__ == ("__main__"):
    app.run(debug=True)
