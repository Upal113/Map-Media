from os import name
import firebase_admin
from flask import *
from firebase_admin import credentials, initialize_app, storage, db
import tempfile
import requests
import urllib3
import json
import fsspec
import folium


# Init firebase with your credentials
cred = credentials.Certificate('map-media-firebase-adminsdk-n2drj-c5da9f1d62.json')


db_app = initialize_app(credential=cred)
ref = db.reference("/", url='https://map-media-default-rtdb.firebaseio.com/')

product_dict  = ref.get()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'superb'

@app.route('/join',  methods=['GET', 'POST'])
def upload():
        if request.method=='POST':
            
            name = request.form['product-name']
            description = request.form['product-des']
            fb_link = request.form['fb-link']
            location = request.form['location']
            image = request.files['product-image']
            temp = tempfile.NamedTemporaryFile(delete=False)
            image.save(temp.name)
            bucket = storage.bucket(name='map-media.appspot.com', app=db_app)
            blob = bucket.blob(temp.name)
            blob.upload_from_filename(temp.name)
            # Opt : if you want to make public access from the URL
            blob.make_public()
            image = blob.public_url
            ref.push(
                {
                    'Name' : name,
                    'Description' : description,
                    'Image Url' : image,
                    'Facebook Link' : fb_link,
                    'Lat' : float(location.split(',')[0]),
                    'Lon' : float(location.split(',')[1])
                }
            )
            return redirect('/join')
        else:    
            return render_template('add_item.html') 
    
@app.route('/')
def home():
    dicty  = ref.get()
    m = folium.Map(zoom_start=10,
		   min_zoom=5,
		   max_bounds=True,
		   location=[23.767048598910577, 90.35805513296512]
    )
    
    for key in dicty.keys():
        iframe = folium.IFrame(html=
	'''
        <!DOCTYPE html>
        <html lang="en">
	<head>
	</head>
	<body>
	<div class="main">

	<ul class="cards">
	<li class="cards_item">
	<div class="card">
	<div class="card_image"><img height="200px" width="200px" src="{}" alt={}></div>
	<div class="card_content">
	<h2 class="card_title">{}</h2>
	<p class="card_text">{}</p>
	    <a target="new" href="{}" style="text-decoration: none;">
	<button class="btn card_btn">Follow On Facebook</button></a>
	</div>
	</div>
	</li>
	</ul>
	</div>
   
        
        </body>
        </html>'''.format(dicty[key]['Image Url'],dicty[key]['Name'],dicty[key]['Name'],dicty[key]['Description'],dicty[key]['Facebook Link']))
        folium.Marker(location=(dicty[key]['Lat'], dicty[key]['Lon']),
		    icon=folium.features.CustomIcon(dicty[key]['Image Url'], icon_size=(40, 40)), 
                    popup=folium.Popup(iframe,  min_width=500,max_width=500)).add_to(m)
        map = m._repr_html_()            
    return render_template('index.html', map=map)

if __name__ == '__main__':
    app.run(debug=True)    
