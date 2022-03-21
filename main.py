import sqlalchemy
from flask import *
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from PIL import Image
import glob

UPLOAD_FOLDER = 'static/clients_img/'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key='fmsl2022'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Creating an SQLAlchemy instance
db = SQLAlchemy(app)
# Models

class Profile(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    username = db.Column(db.String(20), unique=False, nullable=False)
    password=db.Column(db.String(20), unique=False, nullable=False)
    checkpassword=db.Column(db.String(20), unique=False, nullable=False)
    email=db.Column(db.String(20), unique=False, nullable=False)

    def __init__(self,firstname,lastname,username,password,checkpassword,email):
        self.email=email
        self.checkpassword=checkpassword
        self.password=password
        self.username=username
        self.firstname=firstname
        self.lastname=lastname
    # repr method represents how one object of this datatable
    # will look like
    @property
    def __repr__(self):
        return f"Name : {self.first_name}, Age: {self.age}"



@app.route("/")
def home():
    return render_template("about.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        find_user=Profile.query.filter_by(username=username, password=password).first()
        # find_pass=Profile.query.filter_by(password=password)
        if find_user:
            session["username"] = request.form.get("username")
            return redirect(url_for('PersonalArea'))
        else:
            return render_template("tryagain.html")
    else:
        return render_template("Login.html")

@app.route("/logout", methods=['GET', 'POST'])
def Logout():
    session["username"] = None
    return render_template("Logout.html")

@app.route("/foryou", methods=['GET','POST'])
def foryou():
    image_list = []
    for i in glob.glob(fr'static/clients_img/**/*.png'):
        image_list.append(i)
    return render_template("foryou.html", hists=image_list)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/personalarea", methods=['GET', 'POST'])
def PersonalArea():
    image_list = []
    username = session.get("username")
    for i in glob.glob(fr'static/clients_img/{username}/*.png'):
        image_list.append(i)
    if request.method == 'GET':
        return render_template('PersonalArea.html', hists=image_list, code=301)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER']+f'/{username}', filename))
        print('upload_image filename: ' + filename+'\n')
        flash('Image successfully uploaded and displayed below')
        image_list = []
        for i in glob.glob(fr'static/clients_img/{username}/*.png'):
            image_list.append(i)
        return render_template('PersonalArea.html', hists=image_list, code=301,note=f"<h1>its good to see you {username}!<h1>")

    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route("/register", methods=['POST','GET'])
def Register():
    if request.method == 'GET':
        return render_template("Register.html")
    # In this function we will input data from the
    # form page and store it in our database.
    # Remember that inside the get the name should
    # exactly be the same as that in the html
    # input fields
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    username = request.form.get("username")
    password = request.form.get("password")
    checkpassword = request.form.get("checkpassword")
    email = request.form.get("email")


    # create an object of the Profile class of models
    # and store data as a row in our datatable
    find_user_username = Profile.query.filter_by(username=username).first()
    find_user_email = Profile.query.filter_by(email=email).first()
    if find_user_username or find_user_email:
        flash("this email or username already in use")
        return render_template("Register.html")
    else:
        if firstname != '' and lastname != '' and username != '' and password != '' and checkpassword != '' and email != '':
            p = Profile(firstname=firstname, lastname=lastname, username=username,password=password,checkpassword=checkpassword,email=email)
            db.session.add(p)
            db.session.commit()
            newpath = fr'C:\Users\daryn\Lizard\static\clients_img\{username}'
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            session["username"] = request.form.get("username")
            session["password"] = request.form.get("password")
            return render_template("PersonalArea.html")


@app.route("/search", methods=['POST','GET'])
def Search():
    if request.method=='GET':
        return render_template("search.html")
    username = request.form.get("username")
    find_user_username = Profile.query.filter_by(username=username).first()
    if find_user_username:
        flash(f"{username} exists, do you want to talk with him/her?")
    else:
        flash(f"{username} doesnt exists, try again")
    return render_template("search.html")







if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)