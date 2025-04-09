# Système de Gestion d'Inventaire pour Camions de Pompiers

Ce projet est une application web Flask permettant de gérer l'inventaire des équipements des camions de pompiers. Il inclut un système de gestion des utilisateurs avec différents niveaux d'accès et une interface intuitive pour gérer les équipements.

## Fonctionnalités

- Gestion des utilisateurs avec deux niveaux d'accès (administrateur et utilisateur standard)
- Gestion des camions (ajout, modification, suppression)
- Gestion des équipements par camion
- Interface responsive avec Bootstrap
- Système de permissions par camion
- Gestion des icônes pour les camions

## Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Un navigateur web moderne

## Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_REPO]
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
- Windows :
```bash
venv\Scripts\activate
```
- Linux/Mac :
```bash
source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

5. Créez le dossier pour les uploads :
```bash
mkdir -p static/uploads
```

## Configuration

1. Le fichier `config.py` contient les configurations principales :
   - `SECRET_KEY` : Clé secrète pour la sécurité de l'application
   - `UPLOAD_FOLDER` : Dossier pour stocker les icônes des camions
   - `MAX_CONTENT_LENGTH` : Taille maximale des fichiers uploadés

2. La base de données SQLite est initialisée automatiquement au premier lancement.

## Utilisation

1. Lancez l'application :
```bash
python app.py
```

2. Accédez à l'application dans votre navigateur :
```
http://localhost:5000
```

### Comptes par défaut

Deux comptes sont créés automatiquement au premier lancement :

1. Administrateur :
   - Nom d'utilisateur : `admin`
   - Mot de passe : `admin123`

2. Utilisateur test :
   - Nom d'utilisateur : `test`
   - Mot de passe : `test123`

**Important :** Changez ces mots de passe immédiatement après la première connexion !

## Déploiement en production

Pour déployer l'application en production, suivez ces étapes :

1. Modifiez la configuration de production dans `config.py` :
   - Changez `SECRET_KEY` pour une valeur sécurisée
   - Activez le mode debug à `False`
   - Configurez une base de données plus robuste (PostgreSQL recommandé)

2. Utilisez un serveur WSGI comme Gunicorn :
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

3. Configurez un serveur web (Nginx recommandé) comme proxy inverse.

4. Sécurisez l'application :
   - Utilisez HTTPS
   - Configurez des règles de pare-feu
   - Mettez à jour régulièrement les dépendances

## Dépendances principales

- Flask : Framework web
- Flask-SQLAlchemy : ORM pour la base de données
- Flask-Login : Gestion de l'authentification
- Flask-WTF : Gestion des formulaires
- Werkzeug : Utilitaires WSGI
- Bootstrap : Framework CSS
- DataTables : Plugin jQuery pour les tableaux

## Structure du projet

```
.
├── app.py                 # Application principale
├── config.py             # Configuration
├── models.py             # Modèles de données
├── requirements.txt      # Dépendances
├── static/              # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── uploads/         # Dossier pour les icônes
└── templates/           # Templates HTML
    ├── base.html
    ├── login.html
    └── ...
```

## Sécurité

- Tous les mots de passe sont hachés avant d'être stockés
- Protection contre les attaques CSRF
- Validation des entrées utilisateur
- Gestion des permissions par camion
- Protection des routes sensibles

## Maintenance

- Sauvegardez régulièrement la base de données
- Mettez à jour les dépendances
- Surveillez les logs d'erreur
- Effectuez des tests de sécurité réguliers

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt GitHub. 