# Reference: https://docs.microsoft.com/en-us/azure/storage/storage-python-how-to-use-blob-storage
import glob
import os
import time
import datetime
from PIL import Image
import cStringIO
import pymysql
from azure.storage.blob import PublicAccess
from flask import Flask
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from flask import render_template
from flask import request

hostname = 'us-cdbr-azure-east-c.cloudapp.net'
username = 'ba907652bd1452'
password = '73c4a790'
database = 'acsm_d663d3a7be9d1cc'
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database, cursorclass=pymysql.cursors.DictCursor, local_infile=True)

print 'DB connected'

block_blob_service = BlockBlobService(account_name='mycloudassign', account_key='NFS0vruTCHJ7dV3rOl7VXBVIfV+JTphjyIhAXJqDxUrc+R17RE2mbCwSGDqbBuDoeA9H4phQPuZgACnEFK3Ygg==')
print ('Blob connected')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print(APP_ROOT)

app = Flask(__name__)

@app.route('/')
def index():
    print "Hello"
    return render_template('upload.html')

@app.route('/uploadImage',methods=['get','post'])
def upload1():
    f = request.files['upload_files']
    file_name = f.filename
    print (file_name)
    newfile = "C:/Users/Saipriya/Desktop/Cloud/Content/" + file_name
    print (newfile)
    block_blob_service.create_blob_from_path('saipriya',file_name,newfile,content_settings=ContentSettings(content_type='image/png'))
    imgUrl = 'https://mycloudassign.blob.core.windows.net/saipriya/'+ file_name
    csvf = file_name.split('.')[0]
    ext = "C:/Users/Saipriya/Desktop/Cloud/Content/" + csvf + ".csv"
    with open(ext, 'rb') as csvfile:
        content = csvfile.read().decode('utf-8')
        line0 = content.split('\r\n')[0]
        line1 = content.split('\r\n')[1]
        line2 = content.split('\r\n')[2]
        print (str(content))
    print "Hi"
    insertQuery = "insert into photo1 values ('" + file_name + "','" + imgUrl + "','" + line2 + "','" + content + "')"
    print (insertQuery)
    cur = myConnection.cursor()
    cur.execute(insertQuery)
    myConnection.commit()
    cur.close()
    inglist = []
    text = line1.replace(" ", "").split(',')
    for i in text:
        inglist.append(i)
        print (i)
    qtylist = []
    qty = line0.replace(" ", "").split(',')
    for i in qty:
        qtylist.append(i)
        print(i)
    j = 0
    for i in inglist:
        insertcsv = "insert into csvcontent1 values ('" + file_name + "','" + i + "','" + qtylist[j] + "')"
        cur = myConnection.cursor()
        cur.execute(insertcsv)
        myConnection.commit()
        j += 1
    for i in inglist:
        ingproc = "call ingredient_cnt1('" + i + "')"
        cur = myConnection.cursor()
        cur.execute(ingproc)
        myConnection.commit()
    return 'File uploaded successfully'

@app.route('/bulkUpload', methods=['get','post'])
def bulkUpload():
    block_blob_service.set_container_acl('saipriya', public_access=PublicAccess.Container)
    print 'Connection successful'
    generator = block_blob_service.list_blobs('saipriya')
    for filename in glob.glob('C:/Users/Saipriya/Desktop/Cloud/Content/*.jpg'):
        im = Image.open(filename)
        F = filename.split('/')
        print F
        print F[5].split('\\')[1]
        block_blob_service.create_blob_from_path('saipriya',F[5].split('\\')[1],filename,content_settings=ContentSettings(content_type='image/jpg'))
        db_file = "https://mycloudassign.blob.core.windows.net/saipriya/" + F[5].split('\\')[1]
        csvf = F[5].split('\\')[1].split('.')[0]
        ext = "C:/Users/Saipriya/Desktop/Cloud/Content/" + csvf + ".csv"
        listdata = []
        with open(ext, 'rb') as csvfile:
            content = csvfile.read().decode('utf-8')
            line0 = content.split('\r\n')[0]
            line1 = content.split('\r\n')[1]
            line2 = content.split('\r\n')[2]
            print (str(content))
        insertQuery = "insert into photo1 values ('" + F[5].split('\\')[1] + "','" + db_file + "','" + line2 + "','" + content + "')"
        print (insertQuery)
        cur = myConnection.cursor()
        cur.execute(insertQuery)
        myConnection.commit()
        cur.close()
        inglist = []
        text = line1.replace(" ", "").split(',')
        for i in text:
            inglist.append(i)
            print (i)
        qtylist = []
        qty = line0.replace(" ", "").split(',')
        for i in qty:
            qtylist.append(i)
            print(i)
        j = 0
        for i in inglist:
            cur = myConnection.cursor()
            insertcsv = "insert into csvcontent1 values ('" + F[5].split('\\')[1] + "','" + i + "','" + qtylist[j] + "')"
            cur.execute(insertcsv)
            myConnection.commit()
            j += 1
        for i in inglist:
            ingproc = "call ingredient_cnt1('" + i + "')"
            cur = myConnection.cursor()
            cur.execute(ingproc)
            myConnection.commit()
    return "Uploaded Successfully"

@app.route('/list',methods=['get','post'])
def list():
    query="select distinct(path_url) from photo1 A,ingcount1 B,csvcontent1 C where A.imgname = C.imgname and B.ingredient=C.ingredients order by ingcnt desc limit 10"
    cur = myConnection.cursor()
    cur.execute(query)
    res=cur.fetchall()
    myConnection.commit()
    cur.close()
    return render_template('display.html', img = res)

@app.route('/ing',methods=['get','post'])
def ing():
    start = time.time()
    cur = myConnection.cursor()
    text = request.form['text']
    print text
    query2 = "SELECT path_url from photo1 WHERE description like '%%%s%%'" % text
    print query2
    cur.execute(query2)
    res = cur.fetchall()
    print res
    end= time.time()
    total=end-start
    return render_template('show.html',img=res,time=total)

@app.route('/query1',methods=['get','post'])
def query1():
    starttime = time.time()
    cur = myConnection.cursor()
    text = request.form['val1']
    print text
    print "select * from photo1 where imgname='%s'"% text
    query2="select * from photo1 where imgname='%s'"% text
    cur.execute(query2)
    res = cur.fetchall()
    c = 0
    str1 = " "
    for row in res:
        c = c + 1
        str1 += str(c) + ':' + str(row) + '\n\n'
    endtime = time.time()
    total=endtime-starttime
    return render_template('query.html', res=str1,totaltime=total)

@app.route('/query2',methods=['get','post'])
def query2():
    starttime = time.time()
    cur = myConnection.cursor()
    text1 = request.form['val1']
    text2 = request.form['val2']
    print text1
    #query2="SELECT imgname,path_url from photo1 WHERE description like '%%%s%%'" % text
    query2="select A.path_url,A.food_type,B.quantity from Photo1 A, csvcontent1 B where A.imgname=B.imgname and B.quantity between %s and %s order by B.quantity" %(text1,text2)
    cur.execute(query2)
    res = cur.fetchall()
    c = 0
    str1 = " "
    for row in res:
        c = c + 1
        str1 += str(c) + ':' + str(row) + '\n\n'
    endtime = time.time()
    total=endtime-starttime
    cur1 = myConnection.cursor()
    q5="select A.path_url,A.food_type,B.quantity from Photo1 A, csvcontent1 B where A.imgname=B.imgname and B.quantity between %s and %s order by B.quantity" %(text1,text2)
    cur1.execute(q5)
    res1 = cur1.fetchall()
    cur1.close()
    myConnection.commit()
    #return render_template('query.html', res=str1,totaltime=total)
    return render_template('query_img.html', res=str1, totaltime=total,img=res1)
    #return render_template('query_img.html', res=str1,totaltime=total,img=res1)

# query)

# @app.route('/query4',methods=['get','post'])
# def query4():
#     starttime = time.time()
#     cur = myConnection.cursor()
#     text1 = request.form['val1']
#     text2 = request.form['val2']
#     print text1
#     query2="update csvcontent1 set ingredients='%s' where ingredients='%s'"%(text2,text1)
#     cur.execute(query2)
#     cur3 = myConnection.cursor()
#     q6="select * from csvcontent1"
#     cur3.execute(q6)
#     res = cur3.fetchall()
#     c = 0
#     str1 = " "
#     for row in res:
#         c = c + 1
#         str1 += str(c) + ':' + str(row) + '\n\n'
#     endtime = time.time()
#     total=endtime-starttime
#     cur.close()
#     cur3.close()
#     myConnection.commit()
#     #return render_template('query.html', res=str1,totaltime=total)
#     return render_template('query_img.html', res=str1, totaltime=total)
#     #return render_template('query_img.html', res=str1,totaltime=total,img=res1)


@app.route('/query4',methods=['get','post'])
def query4():
    starttime = time.time()
    cur = myConnection.cursor()
    text1 = request.form['val1']
    text2 = request.form['val2']
    print text1
    #query2="DELETE photo1, csvcontent FROM photo1 INNER JOIN csvcontent ON photo1.imgname = csvcontent.imgname WHERE quantity> 10 and quantity<20"
    #query2="DELETE photo1, csvcontent FROM photo1 INNER JOIN csvcontent ON photo1.imgname = csvcontent.imgname WHERE quantity<%s and quantity>%s"%(text1,text2)
    #cur.execute(query2)
    cur3 = myConnection.cursor()
    q6="select * from csvcontent1 where quantity>%s"%text2
    cur3.execute(q6)
    res = cur3.fetchall()
    c = 0
    str1 = " "
    for row in res:
        c = c + 1
        str1 += str(c) + ':' + str(row) + '\n\n'
    endtime = time.time()
    total=endtime-starttime
    cur.close()
    cur3.close()
    myConnection.commit()
    #return render_template('query.html', res=str1,totaltime=total)
    return render_template('query_img.html', res=str1, totaltime=total)
    #return render_template('query_img.html', res=str1,totaltime=total,img=res1)


@app.route('/query3',methods=['get','post'])
def query3():
    starttime = time.time()
    cur = myConnection.cursor()
    text1 = request.form['val1']
    # text2 = request.form['val2']
    print text1
    #query2="SELECT imgname,path_url from photo1 WHERE description like '%%%s%%'" % text
    query2="select * from csvcontent1 where quantity<%s"%text1
    cur.execute(query2)
    res = cur.fetchall()
    c = 0
    str1 = " "
    for row in res:
        c = c + 1
        str1 += str(c) + ':' + str(row) + '\n\n'
    endtime = time.time()
    total=endtime-starttime

    myConnection.commit()
    #return render_template('query.html', res=str1,totaltime=total)
    return render_template('query_img.html', res=str1, totaltime=total)
    #return render_template('query_img.html', res=str1,totaltime=total,img=res1)

@app.route('/repeatreq',methods=['get','post'])
def repeatreq():
    starttime = time.time()
    cur = myConnection.cursor()
    text = request.form['val1']
    print text
    query2="SELECT imgname,path_url from photo1 WHERE description like '%%%s%%'" % text
    cur.execute(query2)
    res = cur.fetchall()
    c = 0
    str1 = " "
    for row in res:
        c = c + 1
        str1 += str(c) + ':' + str(row) + '\n\n'
    endtime = time.time()
    total=endtime-starttime
    queryupdate = "update ingcount1 set request=request+1 where ingredient='%s'" % text
    cur1 = myConnection.cursor()
    cur1.execute(queryupdate)
    cur1.close()
    query3 = "SELECT path_url from photo1 WHERE description like '%%%s%%'" % text
    cur2 = myConnection.cursor()
    cur2.execute(query3)
    res1=cur2.fetchall()
    cur2.close()
    myConnection.commit()
    #return render_template('query.html', res=str1,totaltime=total)
    return render_template('query_img.html', res=str1,totaltime=total,img=res1)


if __name__ == '__main__':
    app.run(debug=True,port = 5001)
