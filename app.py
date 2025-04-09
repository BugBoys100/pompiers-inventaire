from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventaire.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèles de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Camion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), unique=True, nullable=False)
    materiels = db.relationship('Materiel', backref='camion', lazy=True)

class Materiel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    numero_serie = db.Column(db.String(80), unique=True, nullable=False)
    date_peremption = db.Column(db.Date, nullable=False)
    camion_id = db.Column(db.Integer, db.ForeignKey('camion.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('liste_camions'))
        flash('Identifiants invalides')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/camions')
@login_required
def liste_camions():
    camions = Camion.query.all()
    return render_template('liste_camions.html', camions=camions)

@app.route('/camion/<int:camion_id>')
@login_required
def detail_camion(camion_id):
    camion = Camion.query.get_or_404(camion_id)
    return render_template('detail_camion.html', camion=camion)

@app.route('/ajouter_materiel/<int:camion_id>', methods=['POST'])
@login_required
def ajouter_materiel(camion_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('detail_camion', camion_id=camion_id))
    
    nom = request.form.get('nom')
    numero_serie = request.form.get('numero_serie')
    date_peremption = datetime.strptime(request.form.get('date_peremption'), '%Y-%m-%d').date()
    
    materiel = Materiel(nom=nom, numero_serie=numero_serie, 
                       date_peremption=date_peremption, camion_id=camion_id)
    db.session.add(materiel)
    db.session.commit()
    
    return redirect(url_for('detail_camion', camion_id=camion_id))

@app.route('/supprimer_materiel/<int:materiel_id>')
@login_required
def supprimer_materiel(materiel_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    materiel = Materiel.query.get_or_404(materiel_id)
    camion_id = materiel.camion_id
    db.session.delete(materiel)
    db.session.commit()
    
    return redirect(url_for('detail_camion', camion_id=camion_id))

@app.route('/modifier_materiel/<int:materiel_id>', methods=['POST'])
@login_required
def modifier_materiel(materiel_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    materiel = Materiel.query.get_or_404(materiel_id)
    materiel.nom = request.form.get('nom')
    materiel.numero_serie = request.form.get('numero_serie')
    materiel.date_peremption = datetime.strptime(request.form.get('date_peremption'), '%Y-%m-%d').date()
    
    db.session.commit()
    return redirect(url_for('detail_camion', camion_id=materiel.camion_id))

def init_db():
    with app.app_context():
        db.create_all()
        
        # Création des utilisateurs par défaut
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
        
        if not User.query.filter_by(username='test').first():
            test = User(username='test', is_admin=False)
            test.set_password('test')
            db.session.add(test)
        
        # Création des camions par défaut
        if not Camion.query.filter_by(nom='VSAV1').first():
            vsav1 = Camion(nom='VSAV1')
            db.session.add(vsav1)
        
        if not Camion.query.filter_by(nom='VSAV2').first():
            vsav2 = Camion(nom='VSAV2')
            db.session.add(vsav2)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 