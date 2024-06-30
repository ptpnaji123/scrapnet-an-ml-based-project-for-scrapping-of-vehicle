import os
import db
import bchain
from flask import *
from werkzeug.utils import secure_filename
# from model import ScrapnetModel
import time
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

app = Flask(__name__)
app.secret_key="12345"

@app.route('/')
def login():
    return render_template("index.html")

@app.route('/logincode', methods=['post'])
def logincode():
    username = request.form['UN']
    password = request.form['PWD']
    qry = "SELECT * from login where username=%s and password=%s"
    val=(username, password)
    res = db.selectone(qry,val)
    if res is not None:
        if res['type']=="rto":
            session['lid'] = res['id']
            return '''<script>alert("Welcome RTO");window.location='/indexrto'</script>'''
            # return redirect('/indexrto')
        elif res['type']=="User":
            session['lid']=res['id']
            return '''<script>alert("Welcome USER");window.location='/userhome'</script>'''
            # retur/n redirect('/userhome')
        elif res['type'] == "Scrapdealer":
            session['lid'] = res['id']
            return '''<script>alert("Welcome SCRAP DEALER");window.location='/scrapdealer_home'</script>'''
            # return redirect('/scrapdealer_home')
        else:
            return '''<script>alert("Invalid username or password");window.location="/"</script>'''
    else:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''


#============================================RTO===================================================

@app.route('/indexrto',methods=['get','post'])
def indexrto():
    return render_template("indexrto.html")

@app.route('/scrapdealerar',methods=['get','post'])
def scrapdealerar():
    q="SELECT `login`.*,`scrapdealer`.* FROM `login` JOIN `scrapdealer` ON `login`.`id`=`scrapdealer`.`loginid` WHERE `login`.`type`='pending'"
    res=db.selectall(q)
    return render_template("scrapdealerar.html", data=res)

@app.route('/acceptsd')
def acceptsd():
    id = request.args.get('id')
    qry = "update login set type='Scrapdealer' where id=%s"
    db.iud(qry, id)
    return '''<script>alert("Accepted");window.location="/scrapdealerar"</script>'''

@app.route('/rejectsd')
def rejectsd():
    id=request.args.get('id')
    qry = "update login set type='Rejected' where id=%s"
    db.iud(qry,id)
    return '''<script>alert("Rejected");window.location="/scrapdealerar"</script>'''



@app.route('/complaint', methods=['get', 'post'])
def complaint():
    q="SELECT `complaint`.*,`user`.* FROM `complaint` JOIN `user` ON `complaint`.`uid`=`user`.`loginid` "
    res=db.selectall(q)
    return render_template("complaint.html",data=res)

@app.route('/reply',methods=['get', 'post'])
def reply():
    cid = request.args.get('id')
    session['cid'] = cid
    return render_template("reply.html")

@app.route('/sendreply', methods=['post'])
def sendreply():
    msg = request.form['MSG']
    qry = "update complaint set reply=%s where cid=%s"
    val = (msg, str(session['cid']))
    db.iud(qry, val)
    return '''<script>alert("Submitted");window.location="/complaint"</script>'''

@app.route('/verifiedscrapdealer', methods=['get', 'post'])
def verifiedscrapdealer():
    q="SELECT `login`.*,`scrapdealer`.* FROM `login` JOIN `scrapdealer` ON `login`.`id`=`scrapdealer`.`loginid` WHERE `login`.`type`='Scrapdealer'"
    res=db.selectall(q)
    return render_template("verifiedscrapdealerar.html",data=res)

@app.route('/scraprequest',methods=['get','post'])
def scraprequest():
    qry = "SELECT `user`.`fname`,`lname`,`scrapdealer`.`sdname` ,`vehicle`.*,`userrequest`.status,`rid` FROM `userrequest` JOIN `vehicle` ON`vehicle`.`vid`=`userrequest`.`vid` JOIN `user` ON `user`.`loginid`=`vehicle`.`uid` JOIN `scrapdealer` ON `scrapdealer`.`loginid`=`userrequest`.`sdid`  WHERE `userrequest`.`status`='Forwarded' "
    res= db.selectall(qry)
    print(res)
    return render_template("scraprequest.html", data=res)

@app.route('/acceptrq')
def acceptrq():
    id = request.args.get('id')
    qry = "UPDATE `userrequest` SET `status`='Accepted' WHERE `rid`=%s"
    db.iud(qry, id)
    return '''<script>alert("Accepted");window.location="/scraprequest"</script>'''

@app.route('/rejectrq')
def rejectrq():
    id = request.args.get('id')
    qry = "UPDATE `userrequest` SET `status`='Rejected' WHERE `rid`=%s"
    db.iud(qry, id)
    return '''<script>alert("Rejected");window.location="/scraprequest"</script>'''

@app.route('/certificate', methods=['get', 'post'])
def certificate():
    data = db.selectall("SELECT * FROM `certificate` JOIN `userrequest` ON `certificate`.`sdid`=`userrequest`.`rid` JOIN `scrapdealer` ON `userrequest`.`sdid`=`scrapdealer`.`loginid`")
    print(data)
    return render_template("certificate.html", data=data)

#==============================================SCRAP DEALER===========================================

@app.route('/sdsignup',methods=['get','post'])
def sdsignup():
    return render_template("sdsignup.html")

@app.route('/sdreg', methods=['post'])
def sdreg():
    name = request.form['NAME']
    place = request.form['PLACE']
    post = request.form['POST']
    pin = request.form['PIN']
    phone = request.form['PHONE']
    mail = request.form['MAIL']
    proof = request.files['PROOF']
    fn=secure_filename(proof.filename)
    proof.save(os.path.join('static/proof', fn))
    username = request.form['UN']
    password = request.form['PWD']
    qry1 = "insert into login values(null, %s, %s, 'Pending')"
    val = (username, password)
    id = db.iud(qry1, val)
    qry2 = "insert into scrapdealer values(null, %s, %s, %s, %s, %s, %s, %s, %s)"
    val2 = (id, name, place, post, pin, phone, mail, fn)
    db.iud(qry2, val2)
    return '''<script>alert("Registered Successfully");window.location="/"</script>'''

@app.route('/scrapdealer_home',methods=['get','post'])
def scrapdealer_home():
    return render_template("scrapdealer_index.html")

@app.route('/changepwd', methods=['get', 'post'])
def changepwd():
    return render_template("changepwd.html")

@app.route('/rating', methods=['get', 'post'])
def rating():
    qry="SELECT `rating`.*,`user`.`fname`,`lname` FROM `rating` JOIN `user` ON `rating`.`uid`=`user`.`loginid`  WHERE `rating`.`sdid`=%s"
    res=db.selectall2(qry,session['lid'])
    return render_template("rating.html",data=res)

@app.route('/userrequest', methods=['get', 'post'])
def userrequest():
    qry="SELECT `userrequest`.*, `vehicle`.* ,`user`.`fname`,`lname`FROM `userrequest` JOIN `vehicle` ON`vehicle`.`vid`=`userrequest`.`vid` JOIN `user` ON `user`.`loginid`=`vehicle`.`uid` WHERE `userrequest`.`sdid`=%s"
    res=db.selectall2(qry, session['lid'])
    return render_template("userrequest.html", data=res)

@app.route('/forwardrq')
def forwardrq():
    id = request.args.get('id')
    qry = "UPDATE `userrequest` SET `status`='Forwarded' WHERE `rid`=%s"
    db.iud(qry, id)
    return '''<script>alert("Forwarded");window.location="/userrequest"</script>'''

@app.route('/rjctrq')
def rjctrq():
    id = request.args.get('id')
    qry = "UPDATE `userrequest` SET `status`='Rejected' WHERE `rid`=%s"
    db.iud(qry, id)
    return '''<script>alert("Rejected");window.location="/userrequest"</script>'''

@app.route("/gencertificate", methods=["get", "post"])
def gen_certificate():
    qry="SELECT `userrequest`.*, `vehicle`.* ,`user`.`fname`,`lname`FROM `userrequest` JOIN `vehicle` ON`vehicle`.`vid`=`userrequest`.`vid` JOIN `user` ON `user`.`loginid`=`vehicle`.`uid` WHERE `userrequest`.`sdid`=%s and `userrequest`.`status`=%s"
    res=db.selectall2(qry, (session['lid'], "Accepted"))
    certificates = db.selectall("SELECT `sdid` FROM `certificate`")
    certificates = filter(lambda x: x["sdid"], certificates)
    certificates = list(map(lambda x: int(x["sdid"]), certificates))
    data = list(filter(lambda x: x["rid"] not in certificates, res))
    return render_template("gencertificate.html", data=data)

@app.route("/gencert_add")
def gencert_add():
    rid = request.args.get("rid")
    sdid = request.args.get("sdid")
    uid = request.args.get("uid")
    vehicle = request.args.get("vehicle")
    dealer = db.selectone("SELECT * FROM `scrapdealer` WHERE `loginid`=%s", (sdid))
    user = db.selectone("SELECT * FROM `user` WHERE `loginid`=%s", (uid))
    date = time.strftime("%B %d, %Y")
    output_file = "static/certificates/" + time.strftime("%Y%m%d_%H%M%S")+".pdf"
    bchain.generate_certificate(
        user_name=user["fname"] + " " + user["lname"],
        dealer_name=dealer["sdname"],
        vehicle_name=vehicle,
        date=date, 
        output_file=output_file,
    )
    cert = output_file.replace("static/certificates/", "")
    db.iud("INSERT INTO `certificate` (`sdid`, `cert`) VALUES (%s, %s)", (rid, cert))
    return '''<script>alert("Certificate Generated");window.location="/gencertificate"</script>'''



#=========================USER========================================

@app.route('/userhome',methods=['get','post'])
def userhome():
    return render_template("userhome.html")

@app.route('/usersignup',methods=['get','post'])
def usersignup():
    return render_template("usersignup.html")

@app.route('/userreg', methods=['post'])
def userreg():
    fname = request.form['FNAME']
    lname = request.form['LNAME']
    gender = request.form['GENDER']
    place = request.form['PLACE']
    post = request.form['POST']
    pin = request.form['PIN']
    phone = request.form['PHONE']
    mail = request.form['MAIL']
    username = request.form['UN']
    password = request.form['PWD']
    qry1 = "insert into login (username, password, type) values (%s, %s, 'User')"
    val = (username, password)
    id = db.iud(qry1, val)
    qry2 = "insert into user (loginid, fname, lname, gender, place, post, pin, email, phone) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val2 = (id, fname, lname, gender, place, post, pin, mail, phone)
    db.iud(qry2, val2)
    return '''<script>alert("Registered Successfully");window.location="/"</script>'''

@app.route('/viewvehicle',methods=['get','post'])
def viewvehicle():
    q="SELECT * FROM `vehicle` WHERE `uid`=%s"
    res=db.selectall2(q,session['lid'])
    return render_template("viewvehicle.html",data=res)

@app.route('/addvehicle',methods=['get','post'])
def addvehicle():
    return render_template("addvehicle.html")

@app.route('/vehicleadd_post',methods=['post'])
def vehicleadd_post():
    import time
    model=request.form['textfield']

    rc=request.files['file']
    rn=time.strftime("%Y%m%d_%H%M%S")+".jpg"
    rc.save("static/rc/"+rn)

    fitness=request.files['file2']
    fn=time.strftime("%Y%m%d_%H%M%S")+".jpg"
    fitness.save("static/fitness/"+fn)

    q="INSERT INTO `vehicle` VALUES(NULL, %s, %s, %s,%s)"
    val=(session['lid'],model,rn,fn)
    db.iud(q,val)
    return '''<script>alert("Added Successfully");window.location="/viewvehicle"</script>'''

@app.route('/delete_vehicle')
def delete_vehicle():
    id=request.args.get('id')
    q="DELETE FROM `vehicle` WHERE `vid`=%s"
    db.iud(q,id)
    return '''<script>alert("Deleted Successfully");window.location="/viewvehicle"</script>'''

@app.route('/userstatus',methods=['get','post'])
def userstatus():
    q="SELECT `userrequest`.*, `vehicle`.* FROM `userrequest` JOIN `vehicle` ON `vehicle`.`vid`=`userrequest`.`vid` WHERE `vehicle`.`uid`=%s"
    res=db.selectall2(q,session['lid'])
    return render_template("userstatus.html", data=res)

@app.route('/dealerlist',methods=['get','post'])
def dealerlist():
    qry="SELECT `login`.*,`scrapdealer`.* FROM `login` JOIN `scrapdealer` ON `login`.`id`=`scrapdealer`.`loginid` WHERE `login`.`type`='Scrapdealer'"
    res=db.selectall(qry)
    return render_template("dealerlist.html", data=res)

@app.route('/sendrequest',methods=['get','post'])
def sendrequest():
    id=request.args.get('id')
    session['sid']=id
    q = "SELECT * FROM `vehicle` WHERE `uid`=%s"
    res=db.selectall2(q,session['lid'])
    return render_template("sendrequest.html", data=res)

@app.route('/snd_request',methods=['get','post'])
def snd_request():
    id=session['sid']
    vid=request.form['select']
    q = "INSERT INTO `userrequest` VALUES (NULL,%s,%s,CURDATE(),'pending')"
    val=(id,vid)
    db.iud(q,val)
    return '''<script>alert("Send Successfully");window.location="/dealerlist"</script>'''


@app.route('/usercomplaint',methods=['get','post'])
def usercomplaint():
    q="SELECT `complaint`.*,`scrapdealer`.`sdname` FROM `complaint` JOIN `scrapdealer` ON `complaint`.`dealer_id`=`scrapdealer`.`loginid`"
    res=db.selectall(q)
    return render_template("usercomplaint.html",data=res)

@app.route('/sendcomplaint', methods=['post'])
def sendcomplaint():
    q="SELECT * FROM `scrapdealer`"
    res=db.selectall(q)
    return render_template('send_complaint.html',data=res)

@app.route('/snd_complaint',methods=['post'])
def snd_complaint():
    s=request.form['select']
    complaint=request.form['textfield']
    q1="INSERT INTO `complaint` VALUES (NULL,%s,%s,%s,CURDATE(),'pending')"
    val = (session['lid'],s,complaint)
    db.iud(q1, val)
    return '''<script>alert("Send successfully");window.location='usercomplaint'</script>'''

@app.route('/userrating',methods=['get','post'])
def userrating():
    q = "SELECT * FROM `scrapdealer`"
    res = db.selectall(q)
    return render_template("userrating.html", data=res)

@app.route('/setrating', methods=['post'])
def setrating():
    dealer = request.form['select']
    rating = request.form['select1']
    qry = "INSERT INTO `rating` VALUES (NULL,%s,%s,%s)"
    val = (str(session['lid']),dealer,rating)
    db.iud(qry, val)
    return '''<script>alert("Done");window.location="/userrating"</script>'''

@app.route('/pre')
def pre():
    return render_template('predict_value.html')

@app.route('/predict',methods=['post'])
def predict():
    image=request.files['file']
    image.save("static/upload.jpg")
    model = load_model("model/keras_model.h5")
    with open("model/labels.txt", "r") as file:
        class_names = file.readlines()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open("static/upload.jpg").convert("RGB")
    image = ImageOps.fit(image=image, size=(224, 224), method=Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    result = int(class_name)
    print(prediction, index, result)
    # model = ScrapnetModel.from_pretrained("checkpoints/model-v2.pt")
    # result = model.predict("static/upload.jpg")
    # res = int(result)
    return render_template('result.html',re=result)

app.run(debug=True, host="0.0.0.0", port=5000)