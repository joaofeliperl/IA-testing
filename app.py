from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask_migrate import Migrate

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar sessões
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/iatesting'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('projects', lazy=True))


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('projects'))
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('pass')
        confirm_pass = request.form.get('confirm_pass')

        if not all([name, email, role, password]):
            flash("Please fill in all fields.")
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for('signup'))

        if password != confirm_pass:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("User created successfully, please login.")
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('pass')
    
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        logging.debug(f'Login successful for user: {user.id}')
        return redirect(url_for('projects'))
    else:
        logging.warning(f'Invalid credentials for email: {email}')
        flash('Invalid credentials', 'danger')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Remove o ID do usuário da sessão
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    projects = Project.query.filter_by(user_id=user_id).limit(10).all()
    return render_template('projects.html', projects=projects)

@app.route('/save_project', methods=['POST'])
def save_project():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    project_name = request.form.get('name')
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    user_id = session['user_id']
    new_project = Project(name=project_name, user_id=user_id)
    db.session.add(new_project)
    db.session.commit()

    return redirect(url_for('projects'))


@app.route('/view_project/<int:project_id>')
def view_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))

    project = Project.query.get(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    return render_template('home.html', project=project)


@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))

    project = Project.query.get(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully!'})


@app.route('/formtests')
def formtests():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('form-tests.html')

def process_image(screenshot):
    # Dummy image processing
    return "processed_image"

def generate_test_cases(processed_image, description):
    # Dummy test case generation
    return ["test_case_1", "test_case_2"]

@app.route('/generate', methods=['POST'])
def generate():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if 'screenshot' not in request.files or 'description' not in request.form:
        return jsonify({"error": "Missing screenshot or description"}), 400

    screenshot = request.files['screenshot']
    description = request.form['description']

    # Process the screenshot and description
    processed_image = process_image(screenshot)
    test_cases = generate_test_cases(processed_image, description)

    return jsonify({"test_cases": test_cases})


@app.route('/create_tables')
def create_tables():
    db.create_all()
    return "Tables created!"

if __name__ == '__main__':
    app.run(debug=True)
