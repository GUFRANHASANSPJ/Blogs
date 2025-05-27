from flask import Flask,render_template
from flask import Flask, render_template, request, flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from models import db ,User,Blog
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate



app= Flask(__name__)
app.secret_key = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
db.init_app(app)
migrate = Migrate(app, db)



with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # route name to redirect to if not logged in

# Where to save uploaded files
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['BLOGS_IMAGE_FOLDER'] = os.path.join('static', 'blogs_image')
app.config['PROFILE_IMAGE_FOLDER'] = os.path.join('static', 'profile_image')


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def home():
    page = request.args.get('page', 1, type=int)  # get ?page=2 or default to 1
    per_page = 4  # number of blogs per page

    blogs = Blog.query.paginate(page=page, per_page=per_page)

    return render_template("index.html", blogs=blogs)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method== "POST":
        username= request.form['username']
        password= request.form['password']
        email= request.form['email']
        phone= request.form['phone']
        image= request.files['image']
        hashed_pw= generate_password_hash(password)
        if image:
            filename= image.filename
            upload_path = app.config['PROFILE_IMAGE_FOLDER']
            os.makedirs(upload_path, exist_ok=True)

            # Save the file to static/profile_image/
            file_path = os.path.join(upload_path, filename)
            image.save(file_path)

        user= User(username=username,password=hashed_pw,email=email,phone=phone,image=filename)
        db.session.add(user)
        db.session.commit()
        flash("Resistratio  sucessful")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login',methods= ['GET',"POST"])
def login():
    if request.method== "POST":
        username= request.form['username']
        password= request.form['password']
        user= User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("login sucessful")
            return redirect(url_for('home'))
        else:
            return 'Invalid credental'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out!", "info")
    return redirect(url_for('login'))



@app.route('/add-blog', methods=['GET', 'POST'])
@login_required
def add_blog():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        file = request.files['image']
        
        if file :
            filename = file.filename
            upload_path = app.config['BLOGS_IMAGE_FOLDER']
            os.makedirs(upload_path, exist_ok=True)

            # Save the file to static/blogs_image/
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)

        blog = Blog(title=title, description=description, user_id=current_user.id, image=filename)
        db.session.add(blog)
        db.session.commit()
        flash("Blog created successfully")
        return redirect(url_for('home'))

    return render_template('add_blog.html')


@app.route('/view-blog/<int:id>')
def view_blog(id):
    blogs= Blog.query.get(id)
    if blogs:
        return render_template('blog.html',blogs=[blogs])
    else:
        return "Blog not found",404
    

@login_required
@app.route('/user-blogs')
def user_blogs():
    blogs= Blog.query.filter_by(user_id= current_user.id).all()
    return render_template('user_blogs.html',blogs=blogs)
    
@app.route('/update-blog/<int:id>',methods= ['GET','POST'])
def update_blog(id):
    blog= Blog.query.get(id)
    if request.method== "POST":
        blog.title= request.form['title']
        blog.description= request.form['description']
        db.session.commit()
        return render_template("update.html",blog=blog)
    else:
        if blog:
            return render_template('update.html',blog=blog)
        else:
            return "Blog not found",404
        
@app.route('/delete-blog/<int:id>',methods= ['GET','POST'])
def delete_blog(id):
    blog= Blog.query.get(id)
    if blog:
        db.session.delete(blog)
        db.session.commit()
        flash("Blog deleted!", "success")
        return redirect(url_for('home'))

@app.route('/profile')
def profile():
    user_profile= current_user
    return render_template("user_profile.html",user_profile=user_profile)

@app.route('/edit-profile',methods= ['GET','POST'])
def edit_profile():
    profile= db.session.get(User,current_user.id)
    if request.method== "POST":
        phone= request.form['phone']
        email= request.form['email']
        image= request.files['image']
        if phone:
            profile.phone= phone
        if email:
            profile.email= email

        if image:
            filename= image.filename
            upload_path = app.config['PROFILE_IMAGE_FOLDER']
            os.makedirs(upload_path, exist_ok=True)

            # Save the file to static/profile_image/
            file_path = os.path.join(upload_path, filename)
            image.save(file_path)
            profile.image = filename
        db.session.commit()
    return render_template("edit_profile.html",profile=profile)



if __name__== "__main__":
    app.run(debug=True)
