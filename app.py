from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventaire.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
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
    camions_access = db.relationship('UserCamionAccess', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_access_to_camion(self, camion_id):
        if self.is_admin:
            return True
        return any(access.camion_id == camion_id for access in self.camions_access)

class Camion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon_path = db.Column(db.String(255))
    materiels = db.relationship('Materiel', backref='camion', lazy=True)
    user_access = db.relationship('UserCamionAccess', backref='camion', lazy=True)

class UserCamionAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    camion_id = db.Column(db.Integer, db.ForeignKey('camion.id'), nullable=False)

class Materiel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    numero_serie = db.Column(db.String(80), unique=True, nullable=False)
    date_peremption = db.Column(db.Date, nullable=False)
    camion_id = db.Column(db.Integer, db.ForeignKey('camion.id'), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
    if current_user.is_admin:
        camions = Camion.query.all()
    else:
        camions = [access.camion for access in current_user.camions_access]
    return render_template('liste_camions.html', camions=camions)

@app.route('/camion/<int:camion_id>')
@login_required
def detail_camion(camion_id):
    if not current_user.has_access_to_camion(camion_id):
        flash('Accès non autorisé')
        return redirect(url_for('liste_camions'))
    camion = Camion.query.get_or_404(camion_id)
    return render_template('detail_camion.html', camion=camion)

@app.route('/ajouter_camion', methods=['GET', 'POST'])
@login_required
def ajouter_camion():
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        description = request.form.get('description')
        icon = request.files.get('icon')
        
        try:
            # Vérification de l'existence du camion
            existing_camion = db.session.query(Camion).filter(Camion.nom == nom).first()
            if existing_camion:
                flash('Un camion avec ce nom existe déjà')
                return redirect(url_for('ajouter_camion'))
            
            camion = Camion(nom=nom, description=description)
            
            if icon and allowed_file(icon.filename):
                filename = secure_filename(icon.filename)
                icon_path = os.path.join('uploads', filename)
                icon.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                camion.icon_path = icon_path
            
            db.session.add(camion)
            db.session.commit()
            flash('Camion ajouté avec succès')
            return redirect(url_for('liste_camions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Une erreur est survenue : {str(e)}')
            return redirect(url_for('ajouter_camion'))
    
    return render_template('ajouter_camion.html')

@app.route('/modifier_camion/<int:camion_id>', methods=['GET', 'POST'])
@login_required
def modifier_camion(camion_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    camion = Camion.query.get_or_404(camion_id)
    
    if request.method == 'POST':
        camion.nom = request.form.get('nom')
        camion.description = request.form.get('description')
        icon = request.files.get('icon')
        
        if icon and allowed_file(icon.filename):
            if camion.icon_path:
                old_icon_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(camion.icon_path))
                if os.path.exists(old_icon_path):
                    os.remove(old_icon_path)
            filename = secure_filename(icon.filename)
            icon_path = os.path.join('uploads', filename)
            icon.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            camion.icon_path = icon_path
        
        db.session.commit()
        flash('Camion modifié avec succès')
        return redirect(url_for('liste_camions'))
    
    return render_template('modifier_camion.html', camion=camion)

@app.route('/supprimer_camion/<int:camion_id>')
@login_required
def supprimer_camion(camion_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    camion = Camion.query.get_or_404(camion_id)
    if camion.icon_path and os.path.exists(camion.icon_path):
        os.remove(camion.icon_path)
    
    db.session.delete(camion)
    db.session.commit()
    flash('Camion supprimé avec succès')
    return redirect(url_for('liste_camions'))

@app.route('/gestion_utilisateurs')
@login_required
def gestion_utilisateurs():
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    users = User.query.all()
    camions = Camion.query.all()
    return render_template('gestion_utilisateurs.html', users=users, camions=camions)

@app.route('/ajouter_utilisateur', methods=['POST'])
@login_required
def ajouter_utilisateur():
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = 'is_admin' in request.form
    
    if User.query.filter_by(username=username).first():
        flash('Ce nom d\'utilisateur existe déjà')
        return redirect(url_for('gestion_utilisateurs'))
    
    user = User(username=username, is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Gestion des accès aux camions
    for camion in Camion.query.all():
        if f'camion_{camion.id}' in request.form:
            access = UserCamionAccess(user_id=user.id, camion_id=camion.id)
            db.session.add(access)
    
    db.session.commit()
    flash('Utilisateur ajouté avec succès')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/modifier_utilisateur/<int:user_id>', methods=['POST'])
@login_required
def modifier_utilisateur(user_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = 'is_admin' in request.form
    
    # Mise à jour des accès aux camions
    UserCamionAccess.query.filter_by(user_id=user.id).delete()
    for camion in Camion.query.all():
        if f'camion_{camion.id}' in request.form:
            access = UserCamionAccess(user_id=user.id, camion_id=camion.id)
            db.session.add(access)
    
    db.session.commit()
    flash('Utilisateur modifié avec succès')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/supprimer_utilisateur/<int:user_id>')
@login_required
def supprimer_utilisateur(user_id):
    if not current_user.is_admin:
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte')
        return redirect(url_for('gestion_utilisateurs'))
    
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/ajouter_materiel/<int:camion_id>', methods=['POST'])
@login_required
def ajouter_materiel(camion_id):
    if not current_user.has_access_to_camion(camion_id):
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
    materiel = Materiel.query.get_or_404(materiel_id)
    if not current_user.has_access_to_camion(materiel.camion_id):
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    camion_id = materiel.camion_id
    db.session.delete(materiel)
    db.session.commit()
    
    return redirect(url_for('detail_camion', camion_id=camion_id))

@app.route('/modifier_materiel/<int:materiel_id>', methods=['POST'])
@login_required
def modifier_materiel(materiel_id):
    materiel = Materiel.query.get_or_404(materiel_id)
    if not current_user.has_access_to_camion(materiel.camion_id):
        flash('Permission refusée')
        return redirect(url_for('liste_camions'))
    
    materiel.nom = request.form.get('nom')
    materiel.numero_serie = request.form.get('numero_serie')
    materiel.date_peremption = datetime.strptime(request.form.get('date_peremption'), '%Y-%m-%d').date()
    
    db.session.commit()
    return redirect(url_for('detail_camion', camion_id=materiel.camion_id))

def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            # Création des utilisateurs par défaut
            admin_exists = db.session.query(User).filter(User.username == 'admin').first()
            if not admin_exists:
                admin = User(username='admin', is_admin=True)
                admin.set_password('admin')
                db.session.add(admin)
            
            test_exists = db.session.query(User).filter(User.username == 'test').first()
            if not test_exists:
                test = User(username='test', is_admin=False)
                test.set_password('test')
                db.session.add(test)
            
            # Création des camions par défaut
            vsav1_exists = db.session.query(Camion).filter(Camion.nom == 'VSAV1').first()
            if not vsav1_exists:
                vsav1 = Camion(nom='VSAV1', description='Véhicule de Secours et d\'Assistance aux Victimes 1')
                db.session.add(vsav1)
            
            vsav2_exists = db.session.query(Camion).filter(Camion.nom == 'VSAV2').first()
            if not vsav2_exists:
                vsav2 = Camion(nom='VSAV2', description='Véhicule de Secours et d\'Assistance aux Victimes 2')
                db.session.add(vsav2)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()
    app.run(debug=True) 