from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

import pandas as pd
import numpy as np
import os
import json


### ORM for SQL agnostic syntax
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# App-level config vars
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db/content.sqlite"
app.config['UPLOAD_FOLDER'] = 'userData/'

# This variable only needs to exist because we're bypassing the upload screen for simplicity.
# In reality, this wouldn't exist and we'd default to asking users for a file.
temp_fileName = "File1.xlsx"


db = SQLAlchemy(app)

### Annotation denotes a python class that will create a db table to store the user-defined classification. 
class Annotation(db.Model):
    __tablename__ = 'annotations'

    id = db.Column(db.Integer, primary_key=True)
    annotation = db.Column(db.String(64))

    ### Not sure if this is necessary.
    # def __repr__(self):
    #     return '<xClass %r>' % (self.name)

### Inform the application to execute this setup function to create the database tables upon startup
@app.before_first_request
def setup():
    ### uncomment the line below if you'd like to start with a fresh db upon startup
    # db.drop_all()
    db.create_all()

###################################
##### ROUTES
###################################

### NOTE: Removed the upload screen
### Renders upload screen
@app.route("/")
def upload():
    if os.path.isfile(app.config['UPLOAD_FOLDER'] + temp_fileName):
        app.config['UPLOAD_FILE_PATH'] = os.path.join(app.config['UPLOAD_FOLDER'], temp_fileName)
        return render_template("annotate.html")
    else:
        return render_template("upload.html")

### Save file and redirect to training UI
@app.route("/saveFile", methods=['POST'])
def saveFile():
    f = request.files['filename']
    app.config['UPLOAD_FILE_PATH'] = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
    f.save(app.config['UPLOAD_FILE_PATH'])
    return redirect("/annotate", code=302)

### Render training UI
@app.route("/annotate")
def annotate():
    return render_template("annotate.html")

### Broadcast user's data via API for JavaScript to read
@app.route("/api/inputData")
def dataAPI():

    # read the user's input file
    input_df = pd.read_excel(app.config['UPLOAD_FILE_PATH'])

    # query the database for all IDs that have already been annotated
    anno_ids = np.ravel(db.session.query(Annotation.id).all())

    # Only continue with the records from input file that have not already been logged in the database.
    if len(anno_ids) > 0:
        untrained_df = input_df[~input_df['Service Request Number'].isin(anno_ids)]
    else:
        untrained_df = input_df

    # convert df to a list of dicts
    df_list = untrained_df.to_dict('records')

    return jsonify(df_list)


@app.route('/updateModel', methods = ['POST'])
def get_post_javascript_data():

    # receive the record ID and its annotation as a POST request from the AJAX request 
    rec_id = request.form['rec_id']
    classification = request.form['classification']

    # create an instance of our Annotation class and commit it ot the database
    anno = Annotation(id=rec_id, annotation=classification)
    db.session.add(anno)
    db.session.commit()

    return rec_id


if __name__ == "__main__":
    app.run(debug=True)