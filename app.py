from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask_migrate import Migrate
import pymysql
from utils.image_preprocessing import extract_text_from_image
from ai_processing import generate_test_cases
from utils.model_utils import load_custom_model
import os
from functools import wraps

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)

# Configuração do banco de dados
db_name = 'iatesting'
db_user = 'root'
db_password = 'root'
db_host = '192.168.15.35'

# Criar o banco de dados se ele não existir
connection = pymysql.connect(host=db_host, user=db_user, password=db_password)
cursor = connection.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
cursor.close()
connection.close()

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Corrigir caminho do checkpoint do modelo
model_path = 'checkpoints/checkpoint_batch_70.pth.tar'
num_classes = 2
model = load_custom_model(model_path, num_classes)

# Função para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Modelos
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

class TestSuite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(150), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref=db.backref('test_suites', lazy=True))

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)
    expected_result = db.Column(db.String(500), nullable=False)
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suite.id'), nullable=False)
    suite = db.relationship('TestSuite', backref=db.backref('test_cases', lazy=True))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    test_case = db.relationship('TestCase', backref=db.backref('images', lazy=True))


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
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/projects')
@login_required
def projects():
    user_id = session['user_id']
    projects = Project.query.filter_by(user_id=user_id).limit(10).all()
    return render_template('projects.html', projects=projects)

@app.route('/save_project', methods=['POST'])
@login_required
def save_project():
    project_name = request.form.get('name')
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    user_id = session['user_id']
    new_project = Project(name=project_name, user_id=user_id)
    db.session.add(new_project)
    db.session.commit()

    return redirect(url_for('projects'))  

@app.route('/view_suites')
@login_required
def view_suites():
    user_id = session['user_id']
    projects = Project.query.filter_by(user_id=user_id).all()
    if projects:
        project_id = projects[0].id
        suites = TestSuite.query.filter_by(project_id=project_id).all()
        suite_count = len(suites)
        max_suites = 9
        disable_create_suite = suite_count >= max_suites
        return render_template('view-suites.html', suites=suites, disable_create_suite=disable_create_suite)
    else:
        return render_template('view-suites.html', suites=[], disable_create_suite=True)




@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project is None or project.user_id != session['user_id']:
        return jsonify({"error": "Project not found or unauthorized access"}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully!'})

@app.route('/formtests')
@login_required
def formtests():
    return render_template('form-tests.html')

@app.route('/test_results')
@login_required
def test_results():
    feature = request.args.get('feature')
    test_cases = request.args.getlist('test_cases')
    return render_template('test-results.html', test_cases=test_cases, feature=feature)


def generate_test_cases(processed_image, description, quantity=1):
    description_str = str(description).title() if description else "Descrição inválida"
    processed_image_str = str(processed_image) if isinstance(processed_image, str) else "Texto não extraído corretamente."

    test_cases = []
    for i in range(1, int(quantity) + 1):
        test_case_1 = f"Test Case {i}: Validar que o campo '{description_str}' é exibido corretamente na interface."
        test_case_2 = f"Test Case {i}: Verificar que a imagem processada contém o texto: '{processed_image_str}'."
        test_cases.append({"case": test_case_1, "expected_result": test_case_2})

    return test_cases

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    if 'screenshot' not in request.files or 'description' not in request.form or 'feature' not in request.form:
        flash("Missing required fields", "danger")
        return redirect(url_for('formtests'))

    screenshot = request.files['screenshot']
    description = request.form['description']
    feature = request.form['feature']
    test_quantity = request.form.get('test_quantity', 1)

    # Recuperar o projeto do usuário logado (ajuste conforme sua lógica)
    project = Project.query.filter_by(user_id=session['user_id']).first()
    if not project:
        flash("No project found for this user.", "danger")
        return redirect(url_for('projects'))

    # Processar a imagem e gerar os testes
    image_path = save_image(screenshot)
    text = extract_text_from_image(image_path)
    processed_image = str(text) if isinstance(text, str) else "Texto não extraído corretamente."

    # Gerar os casos de teste
    test_cases = generate_test_cases(processed_image, description, test_quantity)

    # Criar uma nova suíte de teste e armazenar os casos
    new_suite = TestSuite(feature_name=feature, project_id=project.id)
    db.session.add(new_suite)
    db.session.commit()

    for case in test_cases:
        new_test_case = TestCase(description=case['case'], expected_result=case['expected_result'], suite_id=new_suite.id)
        db.session.add(new_test_case)
    
    db.session.commit()

    return redirect(url_for('view_suites'))

@app.route('/view_suite/<int:suite_id>')
@login_required
def view_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        flash("Suite not found", "danger")
        return redirect(url_for('view_suites'))

    test_cases = suite.test_cases
    return render_template('test-results.html', suite=suite, test_cases=test_cases)

@app.route('/delete_suite/<int:suite_id>', methods=['POST'])
@login_required
def delete_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        flash("Suite not found", "danger")
        return redirect(url_for('view_suites'))

    TestCase.query.filter_by(suite_id=suite.id).delete()
    db.session.delete(suite)
    db.session.commit()

    flash('Suite deleted successfully', 'success')
    return redirect(url_for('view_suites'))


# Ajustar o caminho para a pasta 'uploads'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_image(file):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(image_path)
    return image_path

if __name__ == '__main__':
    if model:
        print("Modelo carregado com sucesso!")
    else:
        print("Erro ao carregar o modelo.")

    app.run(host="0.0.0.0", port=5000, debug=True)
