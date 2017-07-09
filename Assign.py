# Reference: https://docs.microsoft.com/en-us/azure/storage/storage-python-how-to-use-blob-storage

import os
from base64 import b64encode

import PIL
import datetime
from PIL import Image
import cStringIO
import pymysql
from flask import Flask
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from flask import render_template
from flask import request

hostname = 'us-cdbr-azure-east-c.cloudapp.net'
username = 'ba907652bd1452'
password = '73c4a790'
database = 'acsm_d663d3a7be9d1cc'
myConnection = pymysql.connect(host=hostname, user=username, passwd=password, db=database,
                               cursorclass=pymysql.cursors.DictCursor, local_infile=True)

print 'DB connected'

block_blob_service = BlockBlobService(account_name='mycloudassign',
                                      account_key='NFS0vruTCHJ7dV3rOl7VXBVIfV+JTphjyIhAXJqDxUrc+R17RE2mbCwSGDqbBuDoeA9H4phQPuZgACnEFK3Ygg==')
print ('Blob connected')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print(APP_ROOT)

app = Flask(__name__)


# generator = block_blob_service.list_blobs('saipriya')
# for blob in generator:
#     print(blob.name)

@app.route('/')
def index():
    print "Hello"
    return render_template('upload.html')


@app.route('/uploadImage', methods=['get', 'post'])
def upload1():
    f = request.files['upload_files']
    file_name = f.filename
    comm = request.form['comments']
    print (file_name)
    newfile = "D:/Cloud_Assignments/Assignment10_Azure/" + file_name
    print (newfile)
    block_blob_service.create_blob_from_path('saipriya', file_name, newfile,
                                             content_settings=ContentSettings(content_type='image/png'))
    imgUrl = 'https://mycloudassign.blob.core.windows.net/saipriya/' + file_name
    insertQuery = "insert into Photo (img) values ('%s')" % (imgUrl)
    print insertQuery
    cur = myConnection.cursor()
    cur.execute(insertQuery)
    query1 = 'select img from Photo'
    cur.execute(query1)
    res = cur.fetchall()
    myConnection.commit()
    return 'File uploaded successfully'


@app.route('/list', methods=['get', 'post'])
def list():
    # list=[]
    # generator = block_blob_service.list_blobs('saipriya')
    # for blob in generator:
    #     print(blob.name)
    #     list.append("https://mycloudassign.blob.core.windows.net/saipriya/" + blob.name)
    # print list[1]
    return render_template('display.html', img=list)


@app.route('/show', methods=["GET"])
def showUserData():
    imageList = []
    query = "SELECT * FROM Photo where photo_id=23"
    cur = myConnection.cursor()
    cur.execute(query)
    result = cur.fetchall()
    for row in result:
        image = b64encode(row[3])
        imageList.append(image)
    print datetime.now()
    return render_template("display.html", image=imageList)


if __name__ == '__main__':
    app.run()
