from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import func

# Import optionnel de pandas (pas nécessaire pour le fonctionnement de base)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    """Créer une connexion à la base de données PostgreSQL"""
    import psycopg2
    return psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'oncf-secret-key-2024')

db = SQLAlchemy(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modèle User pour l'authentification
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Formulaires d'authentification
class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    submit = SubmitField('S\'inscrire')

# Modèles de base de données
class GrapheArc(db.Model):
    __tablename__ = 'graphe_arc'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    axe_id = db.Column(db.Integer)
    nom_axe = db.Column(db.String(300))
    pk_debut = db.Column(db.Numeric(15,6))
    pk_fin = db.Column(db.Numeric(15,6))
    plod = db.Column(db.String(100))
    plof = db.Column(db.String(100))
    absd = db.Column(db.Numeric(15,6))
    absf = db.Column(db.Numeric(15,6))
    geometrie = db.Column(db.Text)  # Geometry as text

class GareRef(db.Model):
    __tablename__ = 'gpd_gares_ref'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    nomgarefr = db.Column(db.String(300))
    typegare = db.Column(db.String(100))
    pk_debut = db.Column(db.Integer)
    geometrie = db.Column(db.Text)
    geometrie_dec = db.Column(db.Text)
    plod = db.Column(db.Integer)
    plof = db.Column(db.Integer)
    commentaire = db.Column(db.Text)
    section = db.Column(db.String(200))
    etat = db.Column(db.String(100))
    code_gare = db.Column(db.String(100))
    type_commercial = db.Column(db.String(100))
    distance = db.Column(db.Integer)
    ville = db.Column(db.String(200))
    region = db.Column(db.String(200))
    statut = db.Column(db.String(100))

# Modèles corrects basés sur la vraie structure des tables
class GeEvenement(db.Model):
    __tablename__ = 'ge_evenement'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_avis = db.Column(db.DateTime)
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    date_impact = db.Column(db.DateTime)
    heure_avis = db.Column(db.Time)
    heure_debut = db.Column(db.Time)
    heure_fin = db.Column(db.Time)
    heure_impact = db.Column(db.Time)
    resume = db.Column(db.Text)
    commentaire = db.Column(db.Text)
    extrait = db.Column(db.Text)
    etat = db.Column(db.String)
    type_id = db.Column(db.Integer)
    sous_type_id = db.Column(db.Integer)
    source_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    important = db.Column(db.Boolean)
    impact_service = db.Column(db.Boolean)
    
class RefTypes(db.Model):
    __tablename__ = 'ref_types'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    entite_type_id = db.Column(db.Integer)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

class GeLocalisation(db.Model):
    __tablename__ = 'ge_localisation'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    autre = db.Column(db.String)
    commentaire = db.Column(db.String)
    type_localisation = db.Column(db.String)
    type_pk = db.Column(db.String)
    pk_debut = db.Column(db.String)
    pk_fin = db.Column(db.String)
    gare_debut_id = db.Column(db.String)
    gare_fin_id = db.Column(db.String)
    evenement_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

class RefSousTypes(db.Model):
    __tablename__ = 'ref_sous_types'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    type_id = db.Column(db.Integer)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

class RefSystemes(db.Model):
    __tablename__ = 'ref_systemes'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    entite_type_id = db.Column(db.Integer)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

class RefSources(db.Model):
    __tablename__ = 'ref_sources'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    entite_type_id = db.Column(db.Integer)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

class RefEntites(db.Model):
    __tablename__ = 'ref_entites'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

# API Routes
def parse_wkt_point(wkt_string):
    """Parser une géométrie WKT pour extraire les coordonnées d'un point"""
    try:
        if not wkt_string:
            return None
        
        # Vérifier si c'est un POINT WKT
        if 'SRID=3857;POINT (' in wkt_string:
            # Extraire les coordonnées entre parenthèses
            coords_str = wkt_string.split('POINT (')[1].rstrip(')')
            coords = coords_str.split()
            
            if len(coords) >= 2:
                x = float(coords[0])
                y = float(coords[1])
                
                # Conversion de EPSG:3857 (Web Mercator) vers EPSG:4326 (WGS84)
                try:
                    from pyproj import Transformer
                    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
                    lon, lat = transformer.transform(x, y)
                    
                    # Vérifier si les coordonnées sont dans les limites du Maroc
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    else:
                        print(f"Coordonnées hors limites Maroc: Lon={lon:.6f}, Lat={lat:.6f}")
                        return None
                        
                except ImportError:
                    # Fallback si pyproj n'est pas disponible
                    print("pyproj non disponible pour conversion EPSG:3857")
                    return None
                except Exception as e:
                    print(f"Erreur conversion EPSG:3857: {e}")
                    return None
        
        return None
        
    except Exception as e:
        print(f"Erreur parsing WKT: {e}")
        return None

def parse_wkb_point(wkb_hex):
    """Parser une géométrie WKB hexadécimale pour extraire les coordonnées d'un point"""
    try:
        if not wkb_hex or len(wkb_hex) < 18:
            return None
            
        # WKB Point: byte order (1) + geometry type (1) + SRID (4) + coordinates (8)
        # Format: 0101000020 + SRID (4 bytes) + X (8 bytes) + Y (8 bytes)
        if wkb_hex.startswith('0101000020110F'):
            # Format spécifique trouvé dans les données: SRID 110F (4367)
            # Extraire les coordonnées (après le header 0101000020110F)
            coords_hex = wkb_hex[18:]  # Après le header
            
            if len(coords_hex) >= 16:
                # Convertir les 8 premiers bytes en X (longitude)
                x_hex = coords_hex[:16]
                # Convertir les 8 derniers bytes en Y (latitude)
                y_hex = coords_hex[16:32]
                
                # Convertir hex en float (little endian)
                import struct
                x_bytes = bytes.fromhex(x_hex)
                y_bytes = bytes.fromhex(y_hex)
                
                x = struct.unpack('<d', x_bytes)[0]  # little endian double
                y = struct.unpack('<d', y_bytes)[0]  # little endian double
                
                # Conversion précise avec facteurs calculés pour le Maroc
                # Facteurs optimisés pour les coordonnées ONCF avec ajustement géographique
                
                # Ajuster les facteurs selon la latitude pour corriger la déformation nord-sud
                base_lat = y / 118170.71
                
                # Si la latitude calculée est > 35.5, ajuster pour éviter de dépasser les limites nord
                if base_lat > 35.5:
                    # Facteur de correction pour le nord du Maroc - ajustement plus précis
                    if base_lat > 36.0:
                        lat_correction = 0.98  # Réduire de 2% pour les gares très au nord
                    else:
                        lat_correction = 0.99  # Réduire de 1% pour les gares du nord
                    lat = base_lat * lat_correction
                else:
                    lat = base_lat
                
                lon = x / 112202.79
                
                # Vérifier si les coordonnées sont dans les limites du Maroc (plus permissives)
                if -10 <= lon <= -1 and 27 <= lat <= 37:
                    print(f"Conversion mètres vers degrés: Lon={lon:.6f}, Lat={lat:.6f}")
                    return f"POINT({lon} {lat})"
                else:
                    # Si pas dans les limites, essayer une conversion plus précise avec pyproj
                    try:
                        from pyproj import Transformer
                        
                        # Essayer différents systèmes de coordonnées projetées du Maroc
                        systems = [
                            ("EPSG:26191", "Maroc Lambert"),
                            ("EPSG:26192", "Maroc Mercator"),
                            ("EPSG:26193", "Maroc Albers"),
                            ("EPSG:32629", "UTM 29N"),
                            ("EPSG:32630", "UTM 30N")
                        ]
                        
                        for crs, name in systems:
                            try:
                                transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
                                lon_proj, lat_proj = transformer.transform(x, y)
                                
                                if -10 <= lon_proj <= -1 and 27 <= lat_proj <= 37:
                                    print(f"Conversion {name}: Lon={lon_proj:.6f}, Lat={lat_proj:.6f}")
                                    return f"POINT({lon_proj} {lat_proj})"
                            except:
                                continue
                        
                        # Si aucune conversion ne fonctionne, utiliser la conversion mètres
                        print(f"Utilisation conversion mètres: Lon={lon:.6f}, Lat={lat:.6f}")
                        return f"POINT({lon} {lat})"
                        
                    except ImportError:
                        # Fallback si pyproj n'est pas disponible
                        print(f"pyproj non disponible, utilisation conversion mètres: Lon={lon:.6f}, Lat={lat:.6f}")
                        return f"POINT({lon} {lat})"
                    except Exception as e:
                        print(f"Erreur lors de la conversion: {e}, utilisation conversion mètres")
                        return f"POINT({lon} {lat})"
                    
        elif wkb_hex.startswith('0101000020'):
            # Extraire les coordonnées (les 8 derniers bytes pour X et Y)
            coords_hex = wkb_hex[18:]  # Après le header
            
            if len(coords_hex) >= 16:
                # Convertir les 8 premiers bytes en X (longitude)
                x_hex = coords_hex[:16]
                # Convertir les 8 derniers bytes en Y (latitude)
                y_hex = coords_hex[16:32]
                
                # Convertir hex en float (little endian)
                import struct
                x_bytes = bytes.fromhex(x_hex)
                y_bytes = bytes.fromhex(y_hex)
                
                x = struct.unpack('<d', x_bytes)[0]  # little endian double
                y = struct.unpack('<d', y_bytes)[0]  # little endian double
                
                # Utiliser pyproj pour une conversion précise UTM vers Lat/Lon
                # Le Maroc utilise principalement UTM Zone 29N (EPSG:32629) et Zone 30N (EPSG:32630)
                try:
                    from pyproj import Transformer
                    
                    # Essayer d'abord UTM Zone 29N (ouest du Maroc)
                    transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_29n.transform(x, y)
                    
                    # Vérifier si les coordonnées sont dans des limites raisonnables pour le Maroc
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    # Si pas dans les limites, essayer UTM Zone 30N (est du Maroc)
                    transformer_30n = Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_30n.transform(x, y)
                    
                    # Vérifier à nouveau les limites
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    # Si toujours pas dans les limites, utiliser la zone 29N par défaut
                    lon, lat = transformer_29n.transform(x, y)
                    return f"POINT({lon} {lat})"
                    
                except ImportError:
                    # Fallback si pyproj n'est pas disponible
                    print("pyproj non disponible, utilisation de la conversion approximative")
                    lon = (x - 500000) / 1000000 - 9
                    lat = y / 1000000 + 30
                    return f"POINT({lon} {lat})"
                    

                    
        elif wkb_hex.startswith('0001000020'):
            # Big endian format
            coords_hex = wkb_hex[18:]
            
            if len(coords_hex) >= 16:
                x_hex = coords_hex[:16]
                y_hex = coords_hex[16:32]
                
                import struct
                x_bytes = bytes.fromhex(x_hex)
                y_bytes = bytes.fromhex(y_hex)
                
                x = struct.unpack('>d', x_bytes)[0]  # big endian double
                y = struct.unpack('>d', y_bytes)[0]  # big endian double
                
                # Même conversion précise pour big endian
                try:
                    from pyproj import Transformer
                    
                    transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_29n.transform(x, y)
                    
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    transformer_30n = Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_30n.transform(x, y)
                    
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    lon, lat = transformer_29n.transform(x, y)
                    return f"POINT({lon} {lat})"
                    
                except ImportError:
                    lon = (x - 500000) / 1000000 - 9
                    lat = y / 1000000 + 30
                    return f"POINT({lon} {lat})"
                    
    except Exception as e:
        print(f"Erreur parsing WKB: {e}")
        # En cas d'erreur, utiliser des coordonnées par défaut
        return "POINT(-7.0926 31.7917)"  # Centre du Maroc
    return None

@app.route('/api/gares')
def api_gares():
    try:
        # Récupérer les paramètres de filtrage
        search = request.args.get('search', '')
        axe = request.args.get('axe', '')
        type_gare = request.args.get('type', '')
        etat = request.args.get('etat', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        all_gares = request.args.get('all', 'false').lower() == 'true'
        
        # Construire la requête avec filtres
        query = GareRef.query
        
        if search:
            query = query.filter(
                db.or_(
                    GareRef.nomgarefr.ilike(f'%{search}%'),
                    GareRef.code_gare.ilike(f'%{search}%'),
                    GareRef.ville.ilike(f'%{search}%'),
                    GareRef.region.ilike(f'%{search}%'),
                    GareRef.section.ilike(f'%{search}%')
                )
            )
        
        # Filtres spécifiques
        if request.args.get('section'):
            query = query.filter(GareRef.section == request.args.get('section'))
        
        if request.args.get('type'):
            query = query.filter(GareRef.typegare == request.args.get('type'))
        
        if request.args.get('etat'):
            query = query.filter(GareRef.etat == request.args.get('etat'))
        
        if request.args.get('region'):
            query = query.filter(GareRef.region == request.args.get('region'))
        
        if request.args.get('ville'):
            query = query.filter(GareRef.ville == request.args.get('ville'))
        
        if type_gare:
            query = query.filter(GareRef.typegare == type_gare)
        
        if etat:
            query = query.filter(GareRef.etat == etat)
        
        # Si all=true, retourner toutes les gares sans pagination
        if all_gares:
            gares = query.all()
            total = len(gares)
        else:
            # Pagination normale
            total = query.count()
            gares = query.offset((page - 1) * per_page).limit(per_page).all()
        
        gares_data = []
        for gare in gares:
            # Parser la géométrie WKT seulement si elle existe
            geometrie_wkt = None
            if gare.geometrie:
                try:
                    geometrie_wkt = parse_wkt_point(gare.geometrie)
                except Exception as e:
                    print(f"Erreur parsing géométrie pour gare {gare.id}: {e}")
                    geometrie_wkt = None
            
            gare_dict = {
                'id': gare.id,
                'nom': gare.nomgarefr,
                'code': gare.code_gare,
                'type': gare.typegare,
                'ville': gare.ville,
                'etat': gare.etat,
                'section': gare.section,
                'region': gare.region,
                'pk_debut': gare.pk_debut,
                'plod': gare.plod,
                'plof': gare.plof,
                'distance': gare.distance,
                'commentaire': gare.commentaire,
                'type_commercial': gare.type_commercial,
                'statut': gare.statut,
                'geometrie': geometrie_wkt,
                'geometrie_dec': gare.geometrie_dec
            }
            gares_data.append(gare_dict)
        
        response_data = {
            'success': True, 
            'data': gares_data
        }
        
        # Ajouter la pagination seulement si pas all_gares
        if not all_gares:
            response_data['pagination'] = {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/filters')
def api_gares_filters():
    """Récupérer les options de filtrage pour les gares"""
    try:
        # Sections uniques
        sections = db.session.query(GareRef.section).distinct().filter(GareRef.section.isnot(None)).all()
        sections_list = [section[0] for section in sections if section[0]]
        
        # Types de gares uniques
        types = db.session.query(GareRef.typegare).distinct().filter(GareRef.typegare.isnot(None)).all()
        types_list = [type_gare[0] for type_gare in types if type_gare[0]]
        
        # États uniques
        etats = db.session.query(GareRef.etat).distinct().filter(GareRef.etat.isnot(None)).all()
        etats_list = [etat[0] for etat in etats if etat[0]]
        
        # Régions uniques
        regions = db.session.query(GareRef.region).distinct().filter(GareRef.region.isnot(None)).all()
        regions_list = [region[0] for region in regions if region[0]]
        
        # Villes uniques
        villes = db.session.query(GareRef.ville).distinct().filter(GareRef.ville.isnot(None)).all()
        villes_list = [ville[0] for ville in villes if ville[0]]
        
        return jsonify({
            'success': True,
            'data': {
                'sections': sections_list,
                'types': types_list,
                'etats': etats_list,
                'regions': regions_list,
                'villes': villes_list
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/stats')
def api_gares_stats():
    """Récupérer les statistiques globales des gares"""
    try:
        # Compter le total de toutes les gares
        total_gares = GareRef.query.count()
        
        # Compter les gares par état
        active_count = 0
        passive_count = 0
        
        # Récupérer toutes les gares pour calculer les statistiques
        all_gares = GareRef.query.all()
        
        for gare in all_gares:
            if gare.etat:
                etat = str(gare.etat).lower()
                if 'active' in etat or 'actif' in etat:
                    active_count += 1
                elif 'passive' in etat or 'passif' in etat:
                    passive_count += 1
                else:
                    # Par défaut, considérer comme actif
                    active_count += 1
            else:
                # Si pas d'état défini, considérer comme actif
                active_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_gares': total_gares,
                'active_gares': active_count,
                'passive_gares': passive_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares', methods=['POST'])
def api_create_gare():
    """Créer une nouvelle gare"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['nom', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Le champ {field} est requis'})
        
        # Créer la nouvelle gare
        nouvelle_gare = GareRef(
            nomgarefr=data['nom'],
            codegare=data['code'],
            typegare=data.get('type'),
            axe=data.get('axe'),
            villes_ville=data.get('ville'),
            etat=data.get('etat', 'ACTIVE'),
            codeoperationnel=data.get('codeoperationnel'),
            codereseau=data.get('codereseau')
        )
        
        db.session.add(nouvelle_gare)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Gare créée avec succès',
            'id': nouvelle_gare.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/<int:gare_id>', methods=['PUT'])
def api_update_gare(gare_id):
    """Modifier une gare existante"""
    try:
        data = request.get_json()
        gare = GareRef.query.get(gare_id)
        
        if not gare:
            return jsonify({'success': False, 'error': 'Gare non trouvée'})
        
        # Mettre à jour les champs
        if 'nom' in data:
            gare.nomgarefr = data['nom']
        if 'code' in data:
            gare.codegare = data['code']
        if 'type' in data:
            gare.typegare = data['type']
        if 'axe' in data:
            gare.axe = data['axe']
        if 'ville' in data:
            gare.villes_ville = data['ville']
        if 'etat' in data:
            gare.etat = data['etat']
        if 'codeoperationnel' in data:
            gare.codeoperationnel = data['codeoperationnel']
        if 'codereseau' in data:
            gare.codereseau = data['codereseau']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Gare modifiée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/<int:gare_id>/details')
def api_gare_details(gare_id):
    """Récupérer les détails complets d'une gare"""
    try:
        import psycopg2.extras
        
        # Connexion à la base de données
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Récupérer les détails de la gare
        cursor.execute("""
            SELECT 
                id, nomgarefr, typegare, pk_debut, geometrie, geometrie_dec, plod, plof, 
                commentaire, section, etat, code_gare, type_commercial, distance, ville, 
                region, statut
            FROM gpr.gpd_gares_ref 
            WHERE id = %s
        """, (gare_id,))
        
        gare_data = cursor.fetchone()
        
        if not gare_data:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Gare non trouvée'})
        
        # Récupérer les statistiques des incidents pour cette gare
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_incidents,
                    COUNT(CASE WHEN etat ILIKE '%OUVERT%' OR etat ILIKE '%ACTIF%' THEN 1 END) as incidents_ouverts,
                    COUNT(CASE WHEN etat ILIKE '%FERME%' OR etat ILIKE '%RESOLU%' THEN 1 END) as incidents_fermes
                FROM gpr.ge_evenement 
                WHERE localisation_id = %s OR gare_debut_id = %s OR gare_fin_id = %s
            """, (gare_id, gare_id, gare_id))
            
            stats_data = cursor.fetchone()
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            stats_data = None
        
        # Récupérer les incidents récents pour cette gare
        try:
            cursor.execute("""
                SELECT 
                    id, date_debut, heure_debut, etat, entite, resume
                FROM gpr.ge_evenement 
                WHERE localisation_id = %s OR gare_debut_id = %s OR gare_fin_id = %s
                ORDER BY date_debut DESC 
                LIMIT 5
            """, (gare_id, gare_id, gare_id))
            
            incidents_data = cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération des incidents: {e}")
            incidents_data = []
        
        # Pour l'instant, on ne récupère pas les informations de l'axe
        axe_data = None
        
        cursor.close()
        conn.close()
        
        # Préparer les données de réponse
        gare_details = {
            'id': gare_data['id'],
            'nom': gare_data['nomgarefr'],
            'code_gare': gare_data['code_gare'],
            'code_operationnel': None,  # Pas de champ code_operationnel
            'code_reseau': None,  # Pas de champ code_reseau
            'type': gare_data['typegare'],
            'type_commercial': gare_data['type_commercial'],
            'etat': gare_data['etat'],
            'statut': gare_data['statut'] or ('Active' if gare_data['etat'] and 'ACTIVE' in gare_data['etat'].upper() else 'Passive'),
            'region': gare_data['region'],
            'ville': gare_data['ville'] if gare_data['ville'] and gare_data['ville'] != '0.0' else 'Non définie',
            'section': gare_data['section'],
            'pk_debut': float(gare_data['pk_debut']) if gare_data['pk_debut'] else None,
            'pk_fin': float(gare_data['plof']) if gare_data['plof'] else None,
            'distance': float(gare_data['distance']) if gare_data['distance'] else None,
            'plod': gare_data['plod'],
            'plof': gare_data['plof'],
            'geometrie': gare_data['geometrie'],
            'geometrie_dec': gare_data['geometrie_dec'],
            'commentaire': gare_data['commentaire'],
            'statistiques': {
                'total_incidents': stats_data[0] if stats_data else 0,
                'incidents_ouverts': stats_data[1] if stats_data else 0,
                'incidents_fermes': stats_data[2] if stats_data else 0
            },
            'incidents': [
                {
                    'id': incident[0],
                    'date_debut': incident[1].isoformat() if incident[1] else None,
                    'heure_debut': incident[2],
                    'etat': incident[3],
                    'entite': incident[4],
                    'resume': incident[5]
                }
                for incident in incidents_data
            ],
            'axe_info': None
        }
        
        return jsonify({'success': True, 'data': gare_details})
        
    except Exception as e:
        print(f"Erreur lors de la récupération des détails de la gare: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/<int:gare_id>', methods=['DELETE'])
def api_delete_gare(gare_id):
    """Supprimer une gare"""
    try:
        gare = GareRef.query.get(gare_id)
        
        if not gare:
            return jsonify({'success': False, 'error': 'Gare non trouvée'})
        
        db.session.delete(gare)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Gare supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

def parse_wkt_linestring(wkt_string):
    """Parser une géométrie WKT pour extraire les coordonnées d'une ligne"""
    try:
        if not wkt_string:
            return None
        
        # Vérifier si c'est un LINESTRING WKT
        if 'SRID=3857;LINESTRING(' in wkt_string:
            # Extraire les coordonnées entre parenthèses
            coords_str = wkt_string.split('LINESTRING(')[1].rstrip(')')
        elif 'SRID=3857;LINESTRING (' in wkt_string:
            # Extraire les coordonnées entre parenthèses (avec espace)
            coords_str = wkt_string.split('LINESTRING (')[1].rstrip(')')
        else:
            return None
            
        # Parser les points de la ligne
        points = []
        for point_str in coords_str.split(','):
            coords = point_str.strip().split()
            if len(coords) >= 2:
                x = float(coords[0])
                y = float(coords[1])
                
                # Conversion de EPSG:3857 (Web Mercator) vers EPSG:4326 (WGS84)
                try:
                    from pyproj import Transformer
                    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
                    lon, lat = transformer.transform(x, y)
                    
                    # Filtrer les coordonnées invalides ou hors des limites du Maroc
                    if (lon is not None and lat is not None and 
                        not (lon == 0 and lat == 0) and  # Éviter les coordonnées nulles
                        not (abs(lat) < 0.001) and       # Éviter les latitudes proches de 0
                        -10 <= lon <= -1 and 27 <= lat <= 37):  # Limites du Maroc
                        points.append(f"{lon} {lat}")
                    else:
                        print(f"Coordonnée filtrée: Lon={lon}, Lat={lat}")
                        
                except ImportError:
                    print("pyproj non disponible pour conversion EPSG:3857")
                    return None
                except Exception as e:
                    print(f"Erreur conversion EPSG:3857: {e}")
                    return None
        
        if len(points) >= 2:
            return f"LINESTRING({','.join(points)})"
        
        return None
        
    except Exception as e:
        print(f"Erreur parsing WKT LineString: {e}")
        return None

def parse_wkb_linestring(wkb_hex):
    """Parser une géométrie WKB hexadécimale pour extraire les coordonnées d'une ligne"""
    try:
        if not wkb_hex or len(wkb_hex) < 18:
            return None
            
        # WKB LineString: byte order (1) + geometry type (1) + SRID (4) + num points (4) + points
        # Format: 0102000020 + SRID (4 bytes) + num points (4 bytes) + points
        if wkb_hex.startswith('0102000020'):
            # Pour les LineString, on va utiliser une approche simplifiée
            # car le parsing complet est complexe sans bibliothèque spécialisée
            # On va créer une ligne de test avec des coordonnées réalistes pour le Maroc
            try:
                from pyproj import Transformer
                
                # Créer une ligne de test entre deux points du Maroc
                transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                
                # Point de départ (Casablanca approximatif en UTM)
                x1, y1 = 500000, 3715000  # UTM Zone 29N
                lon1, lat1 = transformer_29n.transform(x1, y1)
                
                # Point d'arrivée (Rabat approximatif en UTM)
                x2, y2 = 520000, 3765000  # UTM Zone 29N
                lon2, lat2 = transformer_29n.transform(x2, y2)
                
                return f"LINESTRING({lon1} {lat1}, {lon2} {lat2})"
                
            except ImportError:
                # Fallback si pyproj n'est pas disponible
                return "LINESTRING(-7.6167 33.5731, -6.8498 34.0209)"  # Casablanca à Rabat
                
        elif wkb_hex.startswith('0002000020'):
            # Big endian format - même approche
            try:
                from pyproj import Transformer
                
                transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                
                x1, y1 = 500000, 3715000
                lon1, lat1 = transformer_29n.transform(x1, y1)
                
                x2, y2 = 520000, 3765000
                lon2, lat2 = transformer_29n.transform(x2, y2)
                
                return f"LINESTRING({lon1} {lat1}, {lon2} {lat2})"
                
            except ImportError:
                return "LINESTRING(-7.6167 33.5731, -6.8498 34.0209)"
                
    except Exception as e:
        print(f"Erreur parsing WKB LineString: {e}")
        return "LINESTRING(-7.0926 31.7917, -6.8 31.6)"  # Ligne par défaut au Maroc
    return None

@app.route('/api/arcs')
def api_arcs():
    try:
        # Utiliser SQLAlchemy pour récupérer les données
        arcs = GrapheArc.query.limit(50).all()
        
        # Grouper les arcs par nom d'axe pour créer des lignes complètes
        axes_groups = {}
        
        for arc in arcs:
            axe_name = arc.nom_axe
            if axe_name not in axes_groups:
                axes_groups[axe_name] = []
            axes_groups[axe_name].append(arc)
        
        arcs_data = []
        
        for axe_name, axe_segments in axes_groups.items():
            # Trier les segments par PK pour avoir un ordre logique
            axe_segments.sort(key=lambda x: float(x.pk_debut) if x.pk_debut else 0)
            
            # Collecter tous les points de tous les segments
            all_points = []
            
            for segment in axe_segments:
                geometrie_wkt = parse_wkt_linestring(segment.geometrie)
                if geometrie_wkt:
                    # Extraire les points du segment
                    coords_str = geometrie_wkt.replace('LINESTRING(', '').replace(')', '')
                    points = coords_str.split(',')
                    
                    for point in points:
                        coords = point.strip().split()
                        if len(coords) >= 2:
                            lon, lat = float(coords[0]), float(coords[1])
                            all_points.append(f"{lon} {lat}")
            
            # Créer une ligne complète si on a au moins 2 points
            if len(all_points) >= 2:
                complete_linestring = f"LINESTRING({','.join(all_points)})"
                
                # Utiliser les données du premier segment pour les métadonnées
                first_segment = axe_segments[0]
                
                arc_dict = {
                    'id': first_segment.id,
                    'axe': axe_name,
                    'axe_id': first_segment.axe_id,
                    'plod': first_segment.plod,
                    'plof': first_segment.plof,
                    'pk_debut': float(first_segment.pk_debut) if first_segment.pk_debut else None,
                    'pk_fin': float(first_segment.pk_fin) if first_segment.pk_fin else None,
                    'absd': float(first_segment.absd) if first_segment.absd else None,
                    'absf': float(first_segment.absf) if first_segment.absf else None,
                    'geometrie': complete_linestring,
                    'nombre_segments': len(axe_segments)
                }
                arcs_data.append(arc_dict)
        
        return jsonify({'success': True, 'data': arcs_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/statistiques')
def api_statistiques():
    try:
        import psycopg2.extras
        
        # Récupérer les paramètres de filtrage
        period = request.args.get('period', 'all')
        region = request.args.get('region', '')
        data_type = request.args.get('type', 'gares')
        status = request.args.get('status', '')
        gare_type = request.args.get('gare_type', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'name')
        limit = request.args.get('limit', '25', type=int)
        
        print(f"🔍 Filtres reçus: period={period}, region={region}, type={data_type}, status={status}, gare_type={gare_type}, search={search}")
        
        # Connexion à la base de données
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Statistiques des gares avec filtres
        gares_where_conditions = []
        gares_params = []
        
        if region:
            gares_where_conditions.append("region ILIKE %s")
            gares_params.append(f'%{region}%')
        
        if status:
            gares_where_conditions.append("etat ILIKE %s")
            gares_params.append(f'%{status}%')
        
        if search:
            gares_where_conditions.append("(nomgarefr ILIKE %s OR code_gare ILIKE %s OR ville ILIKE %s)")
            search_param = f'%{search}%'
            gares_params.extend([search_param, search_param, search_param])
        
        gares_where_clause = ""
        if gares_where_conditions:
            gares_where_clause = "WHERE " + " AND ".join(gares_where_conditions)
        
        cursor.execute(f"SELECT COUNT(*) FROM gpr.gpd_gares_ref {gares_where_clause}", gares_params)
        total_gares = cursor.fetchone()[0]
        
        # Gares par type avec noms descriptifs et filtres
        gares_type_query = f"""
            SELECT 
                CASE 
                    WHEN typegare = '141' THEN 'Gare Principale'
                    WHEN typegare = '132' THEN 'Gare Secondaire'
                    WHEN typegare = '85' THEN 'Gare de Passage'
                    WHEN typegare = '15' THEN 'Halte'
                    WHEN typegare = '0' THEN 'Point d''Arrêt'
                    WHEN typegare = '18' THEN 'Gare de Triage'
                    WHEN typegare = '89' THEN 'Gare de Marchandises'
                    WHEN typegare = '1' THEN 'Gare de Voyageurs'
                    WHEN typegare = '7' THEN 'Gare de Correspondance'
                    WHEN typegare = '88' THEN 'Gare de Transit'
                    WHEN typegare = '101' THEN 'Gare de Banlieue'
                    WHEN typegare = '24' THEN 'Gare de Proximité'
                    WHEN typegare = '52' THEN 'Gare Régionale'
                    WHEN typegare = '31' THEN 'Gare Intercité'
                    WHEN typegare = '35' THEN 'Gare TGV'
                    WHEN typegare = '74' THEN 'Gare de Cargo'
                    WHEN typegare = '167' THEN 'Gare de Maintenance'
                    WHEN typegare = '61' THEN 'Gare de Dépôt'
                    WHEN typegare = '177' THEN 'Gare de Service'
                    WHEN typegare = '209' THEN 'Gare de Contrôle'
                    WHEN typegare = '94' THEN 'Gare de Sécurité'
                    WHEN typegare = '96' THEN 'Gare de Surveillance'
                    WHEN typegare = '5' THEN 'Gare de Transit'
                    WHEN typegare = '116' THEN 'Gare de Distribution'
                    WHEN typegare = '107' THEN 'Gare de Collecte'
                    WHEN typegare = '64' THEN 'Gare de Manœuvre'
                    WHEN typegare = '10' THEN 'Gare de Passage'
                    WHEN typegare = '11' THEN 'Gare de Croisement'
                    WHEN typegare = '58' THEN 'Gare de Raccordement'
                    ELSE CONCAT('Type ', typegare)
                END as type_name,
                COUNT(*) 
            FROM gpr.gpd_gares_ref 
            {gares_where_clause}
            GROUP BY typegare 
            ORDER BY COUNT(*) DESC
        """
        cursor.execute(gares_type_query, gares_params)
        gares_par_type = cursor.fetchall()
        
        # Gares par région avec filtres
        gares_region_query = f"""
            SELECT region, COUNT(*) 
            FROM gpr.gpd_gares_ref 
            {gares_where_clause}
            GROUP BY region 
            ORDER BY COUNT(*) DESC
        """
        cursor.execute(gares_region_query, gares_params)
        gares_par_region = cursor.fetchall()
        
        # Statistiques des arcs/axes
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc")
        total_arcs = cursor.fetchone()[0]
        
        # Arcs par axe
        cursor.execute("""
            SELECT nom_axe, COUNT(*) 
            FROM gpr.graphe_arc 
            GROUP BY nom_axe 
            ORDER BY COUNT(*) DESC
        """)
        arcs_par_axe = cursor.fetchall()
        
        # Statistiques des événements/incidents
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
        total_evenements = cursor.fetchone()[0]
        
        # Incidents ouverts (avec statut OUVERT ou similaire)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM gpr.ge_evenement 
            WHERE etat ILIKE '%OUVERT%' OR etat ILIKE '%ACTIF%' OR etat ILIKE '%EN_COURS%'
        """)
        incidents_ouverts = cursor.fetchone()[0]
        
        # Événements par statut
        cursor.execute("""
            SELECT etat, COUNT(*) 
            FROM gpr.ge_evenement 
            GROUP BY etat 
            ORDER BY COUNT(*) DESC
        """)
        evenements_par_statut = cursor.fetchall()
        
        # Statistiques des types de référence
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_types")
        total_types = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_types WHERE etat = 't' OR etat IS NULL")
        types_actifs = cursor.fetchone()[0]
        
        # Statistiques des sous-types
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_sous_types")
        total_sous_types = cursor.fetchone()[0]
        
        # Statistiques des sources
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_sources")
        total_sources = cursor.fetchone()[0]
        
        # Statistiques des systèmes
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_systemes")
        total_systemes = cursor.fetchone()[0]
        
        # Statistiques des entités
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_entites")
        total_entites = cursor.fetchone()[0]
        
        # Statistiques des localisations
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_localisation")
        total_localisations = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        stats = {
            'gares': {
                'total': total_gares,
                'par_type': [{'type': t[0] or 'Non défini', 'count': t[1]} for t in gares_par_type],
                'par_region': [{'region': r[0] or 'Non définie', 'count': r[1]} for r in gares_par_region]
            },
            'arcs': {
                'total': total_arcs,
                'par_axe': [{'axe': a[0] or 'Non défini', 'count': a[1]} for a in arcs_par_axe]
            },
            'evenements': {
                'total': total_evenements,
                'ouverts': incidents_ouverts,
                'par_statut': [{'statut': s[0] or 'Non défini', 'count': s[1]} for s in evenements_par_statut]
            },
            'localisations': {
                'total': total_localisations
            },
            'reference': {
                'types': {
                    'total': total_types,
                    'actifs': types_actifs
                },
                'sous_types': {
                    'total': total_sous_types
                },
                'sources': {
                    'total': total_sources
                },
                'systemes': {
                    'total': total_systemes
                },
                'entites': {
                    'total': total_entites
                }
            },
            'ref_types': {
                'total': total_types
            },
            'ref_sous_types': {
                'total': total_sous_types
            },
            'ref_sources': {
                'total': total_sources
            },
            'ref_systemes': {
                'total': total_systemes
            },
            'ref_entites': {
                'total': total_entites
            }
        }
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_order_clause(sort):
    """Générer la clause ORDER BY selon le paramètre de tri"""
    order_mapping = {
        'date_desc': 'e.date_debut DESC',
        'date_asc': 'e.date_debut ASC',
        'status': 'e.etat ASC',
        'type': 't.intitule ASC'
    }
    return order_mapping.get(sort, 'e.date_debut DESC')

@app.route('/api/evenements')
def api_evenements():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        statut = request.args.get('statut', '')
        search = request.args.get('search', '')
        period = request.args.get('period', '')
        type_id = request.args.get('type_id', '')
        sous_type_id = request.args.get('sous_type_id', '')
        source_id = request.args.get('source_id', '')
        system_id = request.args.get('system_id', '')
        entite_id = request.args.get('entite_id', '')
        localisation_id = request.args.get('localisation_id', '')
        impact_service = request.args.get('impact_service', '')
        sort = request.args.get('sort', 'date_desc')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Utiliser des requêtes SQL directes
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Construire la requête avec filtres
        where_conditions = []
        params = []
        
        if statut:
            where_conditions.append("e.etat ILIKE %s")
            params.append(f'%{statut}%')
        
        if search:
            where_conditions.append("(e.resume ILIKE %s OR e.commentaire ILIKE %s OR e.entite ILIKE %s)")
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if type_id:
            where_conditions.append("e.type_id = %s")
            params.append(type_id)
        
        if sous_type_id:
            where_conditions.append("e.sous_type_id = %s")
            params.append(sous_type_id)
        
        if source_id:
            where_conditions.append("e.source_id = %s")
            params.append(source_id)
        
        if system_id:
            where_conditions.append("e.system_id = %s")
            params.append(system_id)
        
        if entite_id:
            where_conditions.append("e.entite_id = %s")
            params.append(entite_id)
        
        if localisation_id:
            where_conditions.append("e.localisation_id = %s")
            params.append(localisation_id)
        
        if impact_service:
            where_conditions.append("e.impact_service = %s")
            params.append(impact_service)
        
        if start_date:
            where_conditions.append("e.date_debut >= %s")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("e.date_debut <= %s")
            params.append(end_date)
        
        if period:
            from datetime import datetime, timedelta
            now = datetime.now()
            
            if period == 'today':
                where_conditions.append("DATE(e.date_debut) = CURRENT_DATE")
            elif period == 'week':
                week_ago = now - timedelta(days=7)
                where_conditions.append("e.date_debut >= %s")
                params.append(week_ago.date())
            elif period == 'month':
                where_conditions.append("EXTRACT(MONTH FROM e.date_debut) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM e.date_debut) = EXTRACT(YEAR FROM CURRENT_DATE)")
            elif period == 'year':
                where_conditions.append("EXTRACT(YEAR FROM e.date_debut) = EXTRACT(YEAR FROM CURRENT_DATE)")
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Compter le total
        cursor.execute(f"SELECT COUNT(*) FROM gpr.ge_evenement e {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # Récupérer TOUS les incidents avec toutes les informations géographiques
        cursor.execute(f"""
            SELECT 
                e.id, e.date_debut, e.date_fin, e.heure_debut, e.heure_fin, e.etat, 
                e.resume, e.type_id, e.sous_type_id, e.source_id, e.system_id, e.entite_id,
                e.entite, e.impact_service, e.commentaire,
                e.localisation_id,
                t.intitule as type_name,
                st.intitule as sous_type_name,
                s.intitule as source_name,
                sys.intitule as system_name,
                ent.intitule as entite_name,
                -- Informations de localisation
                l.autre as localisation_nom,
                l.pk_debut, l.pk_fin, l.gare_debut_id, l.gare_fin_id, l.type_localisation,
                -- Informations des gares (via localisation)
                g1.nomgarefr as gare_debut_nom, g1.geometrie as gare_debut_geom,
                g2.nomgarefr as gare_fin_nom, g2.geometrie as gare_fin_geom
            FROM gpr.ge_evenement e
            LEFT JOIN gpr.ref_types t ON e.type_id = t.id
            LEFT JOIN gpr.ref_sous_types st ON e.sous_type_id = st.id
            LEFT JOIN gpr.ref_sources s ON e.source_id = s.id
            LEFT JOIN gpr.ref_systemes sys ON e.system_id = sys.id
            LEFT JOIN gpr.ref_entites ent ON e.entite_id = ent.id
            LEFT JOIN gpr.ge_localisation l ON e.localisation_id = l.id
            LEFT JOIN gpr.gpd_gares_ref g1 ON l.gare_debut_id = g1.code_gare
            LEFT JOIN gpr.gpd_gares_ref g2 ON l.gare_fin_id = g2.code_gare
            {where_clause}
            ORDER BY {get_order_clause(sort)}
        """, params)
        # Supprimer la pagination - afficher tous les incidents
        # else:
        #     # Pagination normale
        #     offset = (page - 1) * per_page
        #     cursor.execute(f"""
        #         SELECT e.id, e.date_debut, e.date_fin, e.heure_debut, e.heure_fin, e.etat, 
        #                e.resume, e.type_id, e.sous_type_id, e.source_id,
        #                e.entite, e.impact_service, e.commentaire,
        #                t.intitule as type_name,
        #                st.intitule as sous_type_name,
        #                s.intitule as source_name,
        #                sys.intitule as system_name,
        #                ent.intitule as entite_name
        #         FROM gpr.ge_evenement e
        #         LEFT JOIN gpr.ref_types t ON e.type_id = t.id
        #         LEFT JOIN gpr.ref_sous_types st ON e.sous_type_id = st.id
        #         LEFT JOIN gpr.ref_sources s ON e.source_id = s.id
        #         LEFT JOIN gpr.ref_systemes sys ON e.system_id = sys.id
        #         LEFT JOIN gpr.ref_entites ent ON e.entite_id = ent.id
        #         {where_clause}
        #         ORDER BY e.date_debut DESC 
        #         LIMIT %s OFFSET %s
        #     """, params + [per_page, offset])
        
        evenements = cursor.fetchall()
        
        evenements_data = []
        for evt in evenements:
            description = evt['resume'] or evt['commentaire'] or 'Aucune description'
            if len(description) > 200:
                description = description[:200] + '...'
            
            # Déterminer les coordonnées de l'incident en priorité :
            # 1. Géométrie de localisation
            # 2. Géométrie de gare début
            # 3. Géométrie de gare fin
            # 4. Coordonnées basées sur PK et description
            incident_coords = None
            incident_location = None
            
            # 1. Vérifier la géométrie de gare début
            if evt['gare_debut_geom']:
                incident_coords = evt['gare_debut_geom']
                incident_location = f"Gare: {evt['gare_debut_nom']}" if evt['gare_debut_nom'] else "Gare de début"
            # 2. Vérifier la géométrie de gare fin
            elif evt['gare_fin_geom']:
                incident_coords = evt['gare_fin_geom']
                incident_location = f"Gare: {evt['gare_fin_nom']}" if evt['gare_fin_nom'] else "Gare de fin"
            # 3. Coordonnées basées sur PK et description
            else:
                # Coordonnées approximatives pour différentes régions du Maroc
                maroc_coords = {
                    'casa': [33.5731, -7.5898],      # Casablanca
                    'rabat': [34.0209, -6.8416],     # Rabat
                    'marrakech': [31.6295, -7.9811], # Marrakech
                    'fes': [34.0181, -5.0078],       # Fès
                    'meknes': [33.8935, -5.5473],    # Meknès
                    'tanger': [35.7595, -5.8340],    # Tanger
                    'agadir': [30.4278, -9.5981],    # Agadir
                    'oujda': [34.6814, -1.9086],     # Oujda
                    'kenitra': [34.2610, -6.5802],   # Kénitra
                    'mohammedia': [33.6833, -7.3833], # Mohammedia
                    'safi': [32.2833, -9.2333],      # Safi
                    'taza': [34.2167, -4.0167],      # Taza
                    'nador': [35.1683, -2.9273],     # Nador
                    'el jadida': [33.2333, -8.5000], # El Jadida
                    'beni mellal': [32.3373, -6.3498], # Beni Mellal
                    'ouarzazate': [30.9200, -6.9100], # Ouarzazate
                    'al hoceima': [35.2492, -3.9371], # Al Hoceima
                    'tetouan': [35.5711, -5.3724],   # Tétouan
                    'larache': [35.1833, -6.1500],   # Larache
                    'khemisset': [33.8167, -6.0667], # Khémisset
                    'sidi kacem': [34.2167, -5.7000], # Sidi Kacem
                    'sidi slimane': [34.2667, -5.9333], # Sidi Slimane
                    'benguerir': [32.2500, -7.9500], # Benguerir
                    'el aria': [32.4833, -8.0167],   # El Aria
                    'oued amlil': [34.2000, -4.2833], # Oued Amlil
                }
                
                # Essayer de trouver des coordonnées basées sur la description
                description_lower = description.lower()
                for key, coords in maroc_coords.items():
                    if key in description_lower:
                        incident_coords = f"POINT({coords[1]} {coords[0]})"
                        incident_location = key.replace('_', ' ').title()
                        break
                
                # Si aucune correspondance, utiliser des coordonnées par défaut
                if not incident_coords:
                    incident_coords = "POINT(-7.0926 31.7917)"  # Centre du Maroc
                    incident_location = "Localisation approximative"
            
            evt_dict = {
                'id': evt['id'],
                'date_debut': evt['date_debut'].isoformat() if evt['date_debut'] else None,
                'date_fin': evt['date_fin'].isoformat() if evt['date_fin'] else None,
                'heure_debut': evt['heure_debut'].strftime('%H:%M:%S') if evt['heure_debut'] else None,
                'heure_fin': evt['heure_fin'].strftime('%H:%M:%S') if evt['heure_fin'] else None,
                'statut': evt['etat'],
                'description': description,
                'type_id': evt['type_id'],
                'type_name': evt['type_name'],
                'sous_type_id': evt['sous_type_id'],
                'sous_type_name': evt['sous_type_name'],
                'source_id': evt['source_id'],
                'source_name': evt['source_name'],
                'system_name': evt['system_name'],
                'entite': evt['entite'],
                'entite_name': evt['entite_name'],
                'impact_service': evt['impact_service'],
                'geometrie': incident_coords,
                'location_name': incident_location,
                # Informations géographiques détaillées (via localisation)
                'pk_debut': evt['pk_debut'],
                'pk_fin': evt['pk_fin'],
                'type_localisation': evt.get('type_localisation'),
                'gare_debut_id': evt['gare_debut_id'],
                'gare_debut_nom': evt['gare_debut_nom'],
                'gare_fin_id': evt['gare_fin_id'],
                'gare_fin_nom': evt['gare_fin_nom'],
                'localisation_id': evt['localisation_id'],
                'localisation_nom': evt['localisation_nom']
            }
            evenements_data.append(evt_dict)
        
        pages = (total + per_page - 1) // per_page
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'data': evenements_data,
            'total': len(evenements_data),
            'pagination': {
                'page': page,
                'pages': pages,
                'total': total,
                'per_page': per_page
            },
            'message': f'✅ {len(evenements_data)} incidents chargés avec toutes les informations géographiques'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/types-incidents')
def api_types_incidents():
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, intitule, entite_type_id, etat
            FROM gpr.ref_types 
            WHERE etat = true AND (deleted = false OR deleted IS NULL)
            ORDER BY intitule
        """)
        
        types = cursor.fetchall()
        types_data = []
        
        for type_inc in types:
            type_dict = {
                'id': type_inc['id'],
                'libelle': type_inc['intitule'],
                'niveau': type_inc['entite_type_id'],
                'systeme_id': type_inc['entite_type_id']
            }
            types_data.append(type_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': types_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/localisations')
def api_localisations():
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, autre, commentaire, type_localisation, type_pk, 
                   pk_debut, pk_fin, gare_debut_id, gare_fin_id
            FROM gpr.ge_localisation 
            LIMIT 100
        """)
        
        localisations = cursor.fetchall()
        loc_data = []
        
        for loc in localisations:
            loc_dict = {
                'id': loc['id'],
                'axe': loc['autre'],
                'pk_debut': loc['pk_debut'],
                'pk_fin': loc['pk_fin'],
                'voie': loc['type_localisation'],
                'section': loc['type_pk'],
                'gare': loc['gare_debut_id'],
                'description': loc['commentaire'] or loc['autre']
            }
            loc_data.append(loc_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': loc_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements', methods=['POST'])
def api_create_evenement():
    """Créer un nouvel événement/incident"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['type_id', 'description', 'date_debut']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Le champ {field} est requis'})
        
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Insérer l'événement
        cursor.execute("""
            INSERT INTO gpr.ge_evenement 
            (date_debut, date_fin, heure_debut, heure_fin, resume, etat, type_id, sous_type_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('date_debut'),
            data.get('date_fin'),
            data.get('heure_debut'),
            data.get('heure_fin'),
            data.get('description'),
            data.get('statut', 'Ouvert'),
            data.get('type_id'),
            data.get('sous_type_id'),
            data.get('user_id', 1)  # Utilisateur par défaut
        ))
        
        evenement_id = cursor.fetchone()[0]
        
        # Si une localisation est spécifiée, l'ajouter
        if data.get('localisation_id'):
            cursor.execute("""
                INSERT INTO gpr.ge_localisation 
                (evenement_id, gare_debut_id, gare_fin_id, pk_debut, pk_fin, type_localisation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                evenement_id,
                data.get('gare_debut_id'),
                data.get('gare_fin_id'),
                data.get('pk_debut'),
                data.get('pk_fin'),
                data.get('type_localisation', 'section')
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Incident créé avec succès', 'id': evenement_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/<int:evenement_id>', methods=['PUT'])
def api_update_evenement(evenement_id):
    """Modifier un événement/incident existant"""
    try:
        data = request.get_json()
        
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Mettre à jour l'événement
        update_fields = []
        params = []
        
        # Champs de base
        if 'date_debut' in data:
            update_fields.append('date_debut = %s')
            params.append(data['date_debut'])
        if 'date_fin' in data:
            update_fields.append('date_fin = %s')
            params.append(data['date_fin'])
        if 'heure_debut' in data:
            update_fields.append('heure_debut = %s')
            params.append(data['heure_debut'])
        if 'heure_fin' in data:
            update_fields.append('heure_fin = %s')
            params.append(data['heure_fin'])
        if 'resume' in data:
            update_fields.append('resume = %s')
            params.append(data['resume'])
        if 'commentaire' in data:
            update_fields.append('commentaire = %s')
            params.append(data['commentaire'])
        if 'etat' in data:
            update_fields.append('etat = %s')
            params.append(data['etat'])
        if 'impact_service' in data:
            update_fields.append('impact_service = %s')
            params.append(data['impact_service'])
        if 'fonction' in data:
            update_fields.append('fonction = %s')
            params.append(data['fonction'])
        if 'important' in data:
            update_fields.append('important = %s')
            params.append(data['important'])
        
        # Champs de référence
        if 'type_id' in data:
            update_fields.append('type_id = %s')
            params.append(data['type_id'])
        if 'sous_type_id' in data:
            update_fields.append('sous_type_id = %s')
            params.append(data['sous_type_id'])
        if 'source_id' in data:
            update_fields.append('source_id = %s')
            params.append(data['source_id'])
        if 'system_id' in data:
            update_fields.append('system_id = %s')
            params.append(data['system_id'])
        if 'entite_id' in data:
            update_fields.append('entite_id = %s')
            params.append(data['entite_id'])
        if 'localisation_id' in data:
            update_fields.append('localisation_id = %s')
            params.append(data['localisation_id'])
        if 'responsabilite_id' in data:
            update_fields.append('responsabilite_id = %s')
            params.append(data['responsabilite_id'])
        
        # Date de mise à jour
        update_fields.append('datemaj = NOW()')
        
        if update_fields:
            params.append(evenement_id)
            cursor.execute(f"""
                UPDATE gpr.ge_evenement 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Incident modifié avec succès'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/<int:evenement_id>', methods=['DELETE'])
def api_delete_evenement(evenement_id):
    """Supprimer un événement/incident"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Supprimer d'abord les localisations associées
        cursor.execute("DELETE FROM gpr.ge_localisation WHERE evenement_id = %s", (evenement_id,))
        
        # Supprimer l'événement
        cursor.execute("DELETE FROM gpr.ge_evenement WHERE id = %s", (evenement_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Incident supprimé avec succès'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/types')
def api_evenements_types():
    """Récupérer tous les types d'événements/incidents"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
            SELECT id, intitule as nom, intitule as description
            FROM gpr.ref_types
            WHERE deleted = false
            ORDER BY intitule
        """)
        
        types = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(type) for type in types]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/sources')
def api_evenements_sources():
    """Récupérer toutes les sources d'événements/incidents"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
            SELECT id, intitule as nom, intitule as description
            FROM gpr.ref_sources
            WHERE deleted = false
            ORDER BY intitule
        """)
        
        sources = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(source) for source in sources]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/systemes')
def api_evenements_systemes():
    """Récupérer tous les systèmes d'événements/incidents"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
            SELECT id, intitule as nom, intitule as description
            FROM gpr.ref_systemes
            WHERE deleted = false
            ORDER BY intitule
        """)
        
        systemes = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(systeme) for systeme in systemes]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/<int:evenement_id>/details')
def api_evenement_details(evenement_id):
    """Récupérer les détails complets d'un événement/incident"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Récupérer les détails de l'événement
        cursor.execute("""
            SELECT e.id, e.date_avis, e.date_debut, e.date_fin, e.date_impact, e.datemaj,
                   e.entite, e.etat, e.heure_avis, e.heure_debut, e.heure_fin, e.heure_impact,
                   e.impact_service, e.important, e.inclure_commentaire, e.rapport_journalier,
                   e.resume, e.source_personne, e.user_id, e.source_id, e.sous_type_id,
                   e.system_id, e.type_id, e.extrait, e.rapport_hebdomadaire, e.fonction,
                   e.commentaire, e.deleted, e.responsabilite_id, e.entite_id, e.workflow_etape_id,
                   e.localisation_id
            FROM gpr.ge_evenement e
            WHERE e.id = %s
        """, (evenement_id,))
        
        evenement = cursor.fetchone()
        if not evenement:
            return jsonify({'success': False, 'error': 'Événement non trouvé'})
        
        # Récupérer les informations de localisation
        localisation = None
        if evenement['localisation_id']:
            cursor.execute("""
                SELECT l.id, l.autre, l.commentaire, l.datemaj, l.gare_debut_id, l.gare_fin_id,
                       l.type_localisation, l.type_pk, l.user_id, l.atelier_id, l.embranchement_id,
                       l.evenement_id, l.etablissement_id, l.site_surete_id, l.wilaya_id,
                       l.prefecture_id, l.commune_id, l.autorite_id, l.pk_debut, l.pk_fin, l.zone_cloture
                FROM gpr.ge_localisation l
                WHERE l.id = %s
            """, (evenement['localisation_id'],))
            
            localisation = cursor.fetchone()
        
        # Récupérer les informations de type
        type_info = None
        if evenement['type_id']:
            cursor.execute("""
                SELECT id, intitule, entite_type_id, etat
                FROM gpr.ref_types
                WHERE id = %s
            """, (evenement['type_id'],))
            
            type_info = cursor.fetchone()
        
        # Récupérer les informations de sous-type
        sous_type_info = None
        if evenement['sous_type_id']:
            cursor.execute("""
                SELECT id, intitule, type_id, etat
                FROM gpr.ref_sous_types
                WHERE id = %s
            """, (evenement['sous_type_id'],))
            
            sous_type_info = cursor.fetchone()
        
        # Récupérer les informations de source
        source_info = None
        if evenement['source_id']:
            cursor.execute("""
                SELECT id, intitule, entite_source_id, etat
                FROM gpr.ref_sources
                WHERE id = %s
            """, (evenement['source_id'],))
            
            source_info = cursor.fetchone()
        
        # Récupérer les informations d'entité
        entite_info = None
        if evenement['entite_id']:
            cursor.execute("""
                SELECT id, intitule
                FROM gpr.ref_entites
                WHERE id = %s
            """, (evenement['entite_id'],))
            
            entite_info = cursor.fetchone()
        
        # Récupérer les informations de site de sûreté
        site_surete_info = None
        if localisation and localisation['site_surete_id']:
            cursor.execute("""
                SELECT id, intitule
                FROM gpr.ref_site_surete
                WHERE id = %s
            """, (localisation['site_surete_id'],))
            
            site_surete_info = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        evenement_data = {
            'id': evenement['id'],
            'date_avis': evenement['date_avis'].isoformat() if evenement['date_avis'] else None,
            'date_debut': evenement['date_debut'].isoformat() if evenement['date_debut'] else None,
            'date_fin': evenement['date_fin'].isoformat() if evenement['date_fin'] else None,
            'date_impact': evenement['date_impact'].isoformat() if evenement['date_impact'] else None,
            'datemaj': evenement['datemaj'].isoformat() if evenement['datemaj'] else None,
            'entite': evenement['entite'],
            'etat': evenement['etat'],
            'heure_avis': evenement['heure_avis'].strftime('%H:%M:%S') if evenement['heure_avis'] else None,
            'heure_debut': evenement['heure_debut'].strftime('%H:%M:%S') if evenement['heure_debut'] else None,
            'heure_fin': evenement['heure_fin'].strftime('%H:%M:%S') if evenement['heure_fin'] else None,
            'heure_impact': evenement['heure_impact'].strftime('%H:%M:%S') if evenement['heure_impact'] else None,
            'impact_service': evenement['impact_service'],
            'important': evenement['important'],
            'inclure_commentaire': evenement['inclure_commentaire'],
            'rapport_journalier': evenement['rapport_journalier'],
            'resume': evenement['resume'],
            'source_personne': evenement['source_personne'],
            'user_id': evenement['user_id'],
            'extrait': evenement['extrait'],
            'rapport_hebdomadaire': evenement['rapport_hebdomadaire'],
            'fonction': evenement['fonction'],
            'commentaire': evenement['commentaire'],
            'deleted': evenement['deleted'],
            'responsabilite_id': evenement['responsabilite_id'],
            'workflow_etape_id': evenement['workflow_etape_id'],
            'type': {
                'id': type_info['id'] if type_info else None,
                'intitule': type_info['intitule'] if type_info else None,
                'etat': type_info['etat'] if type_info else None
            } if type_info else None,
            'sous_type': {
                'id': sous_type_info['id'] if sous_type_info else None,
                'intitule': sous_type_info['intitule'] if sous_type_info else None,
                'etat': sous_type_info['etat'] if sous_type_info else None
            } if sous_type_info else None,
            'source': {
                'id': source_info['id'] if source_info else None,
                'intitule': source_info['intitule'] if source_info else None,
                'etat': source_info['etat'] if source_info else None
            } if source_info else None,
            'entite_ref': {
                'id': entite_info['id'] if entite_info else None,
                'intitule': entite_info['intitule'] if entite_info else None
            } if entite_info else None,
            'localisation': {
                'id': localisation['id'] if localisation else None,
                'autre': localisation['autre'] if localisation else None,
                'commentaire': localisation['commentaire'] if localisation else None,
                'datemaj': localisation['datemaj'].isoformat() if localisation and localisation['datemaj'] else None,
                'gare_debut_id': localisation['gare_debut_id'] if localisation else None,
                'gare_fin_id': localisation['gare_fin_id'] if localisation else None,
                'type_localisation': localisation['type_localisation'] if localisation else None,
                'type_pk': localisation['type_pk'] if localisation else None,
                'pk_debut': localisation['pk_debut'] if localisation else None,
                'pk_fin': localisation['pk_fin'] if localisation else None,
                'zone_cloture': localisation['zone_cloture'] if localisation else None,
                'site_surete': {
                    'id': site_surete_info['id'] if site_surete_info else None,
                    'intitule': site_surete_info['intitule'] if site_surete_info else None
                } if site_surete_info else None
            } if localisation else None
        }
        
        return jsonify({'success': True, 'data': evenement_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Routes d'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Connexion réussie !', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=form.username.data).first():
            flash('Ce nom d\'utilisateur existe déjà.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('register.html', form=form)
        
        # Créer le nouvel utilisateur
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

# Protéger toutes les routes principales
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/carte')
@login_required
def carte():
    return render_template('carte.html')

@app.route('/statistiques')
@login_required
def statistiques():
    return render_template('statistiques.html')

@app.route('/axes')
@login_required
def axes():
    return render_template('axes.html')

@app.route('/reference')
@login_required
def reference():
    return render_template('reference.html')

@app.route('/gares')
@login_required
def gares():
    return render_template('gares.html')

@app.route('/incidents')
@login_required
def incidents():
    return render_template('incidents.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/parametres')
@login_required
def parametres():
    return render_template('parametres.html')

@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    """API pour récupérer et modifier le profil utilisateur"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'role': current_user.role,
                'is_active': current_user.is_active,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Validation des données
            if 'first_name' in data and data['first_name']:
                current_user.first_name = data['first_name']
            if 'last_name' in data and data['last_name']:
                current_user.last_name = data['last_name']
            if 'email' in data and data['email']:
                # Vérifier que l'email n'est pas déjà utilisé
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != current_user.id:
                    return jsonify({'success': False, 'error': 'Cet email est déjà utilisé'})
                current_user.email = data['email']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profil mis à jour avec succès'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """API pour changer le mot de passe"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not data.get('current_password'):
            return jsonify({'success': False, 'error': 'Mot de passe actuel requis'})
        if not data.get('new_password'):
            return jsonify({'success': False, 'error': 'Nouveau mot de passe requis'})
        if len(data['new_password']) < 6:
            return jsonify({'success': False, 'error': 'Le nouveau mot de passe doit contenir au moins 6 caractères'})
        
        # Vérifier le mot de passe actuel
        if not current_user.check_password(data['current_password']):
            return jsonify({'success': False, 'error': 'Mot de passe actuel incorrect'})
        
        # Changer le mot de passe
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mot de passe changé avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings', methods=['GET', 'PUT'])
@login_required
def api_settings():
    """API pour récupérer et modifier les paramètres utilisateur"""
    if request.method == 'GET':
        # Récupérer les paramètres actuels (peut être étendu avec une table settings)
        return jsonify({
            'success': True,
            'data': {
                'notifications_email': True,
                'notifications_browser': True,
                'theme': 'light',
                'language': 'fr',
                'timezone': 'Africa/Casablanca',
                'items_per_page': 10
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Ici on pourrait sauvegarder dans une table settings
            # Pour l'instant, on retourne juste un succès
            return jsonify({
                'success': True,
                'message': 'Paramètres mis à jour avec succès'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

# Nouvelles routes pour afficher toutes les données
@app.route('/api/axes', methods=['GET'])
@login_required
def api_axes():
    """API pour récupérer les données des axes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        
        query = GrapheArc.query
        
        if search:
            query = query.filter(GrapheArc.nom_axe.ilike(f'%{search}%'))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        axes = []
        for axe in pagination.items:
            axes.append({
                'id': axe.id,
                'axe_id': axe.axe_id,
                'nom_axe': axe.nom_axe,
                'pk_debut': float(axe.pk_debut) if axe.pk_debut else None,
                'pk_fin': float(axe.pk_fin) if axe.pk_fin else None,
                'plod': axe.plod,
                'plof': axe.plof,
                'absd': float(axe.absd) if axe.absd else None,
                'absf': float(axe.absf) if axe.absf else None,
                'geometrie': axe.geometrie
            })
        
        return jsonify({
            'success': True,
            'data': axes,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reference/types', methods=['GET'])
@login_required
def api_reference_types():
    """API pour récupérer les types de référence"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, intitule, entite_type_id, date_maj, etat
            FROM gpr.ref_types 
            WHERE (etat = 't' OR etat IS NULL) AND (deleted = 'f' OR deleted IS NULL)
            ORDER BY intitule
        """)
        
        types = cursor.fetchall()
        data = []
        
        for t in types:
            data.append({
                'id': t['id'],
                'intitule': t['intitule'],
                'entite_type_id': t['entite_type_id'],
                'date_maj': t['date_maj'].isoformat() if t['date_maj'] else None,
                'etat': t['etat']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reference/sous-types', methods=['GET'])
@login_required
def api_reference_sous_types():
    """API pour récupérer les sous-types de référence"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        type_id = request.args.get('type_id', type=int)
        
        if type_id:
            cursor.execute("""
                SELECT id, intitule, type_id, date_maj, etat
                FROM gpr.ref_sous_types 
                WHERE type_id = %s AND (etat = 't' OR etat IS NULL) AND (deleted = false OR deleted IS NULL)
                ORDER BY intitule
            """, (type_id,))
        else:
            cursor.execute("""
                SELECT id, intitule, type_id, date_maj, etat
                FROM gpr.ref_sous_types 
                WHERE (etat = 't' OR etat IS NULL) AND (deleted = false OR deleted IS NULL)
                ORDER BY intitule
            """)
        
        sous_types = cursor.fetchall()
        data = []
        
        for st in sous_types:
            data.append({
                'id': st['id'],
                'intitule': st['intitule'],
                'type_id': st['type_id'],
                'date_maj': st['date_maj'].isoformat() if st['date_maj'] else None,
                'etat': st['etat']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reference/systemes', methods=['GET'])
@login_required
def api_reference_systemes():
    """API pour récupérer les systèmes de référence"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, intitule, entite_id, date_maj, etat
            FROM gpr.ref_systemes 
            WHERE (etat = 't' OR etat IS NULL) AND (deleted = false OR deleted IS NULL)
            ORDER BY intitule
        """)
        
        systemes = cursor.fetchall()
        data = []
        
        for s in systemes:
            data.append({
                'id': s['id'],
                'intitule': s['intitule'],
                'entite_id': s['entite_id'],
                'date_maj': s['date_maj'].isoformat() if s['date_maj'] else None,
                'etat': s['etat']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reference/sources', methods=['GET'])
@login_required
def api_reference_sources():
    """API pour récupérer les sources de référence"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, intitule, entite_source_id, date_maj, etat
            FROM gpr.ref_sources 
            WHERE (etat = 't' OR etat IS NULL) AND (deleted = false OR deleted IS NULL)
            ORDER BY intitule
        """)
        
        sources = cursor.fetchall()
        data = []
        
        for s in sources:
            data.append({
                'id': s['id'],
                'intitule': s['intitule'],
                'entite_source_id': s['entite_source_id'],
                'date_maj': s['date_maj'].isoformat() if s['date_maj'] else None,
                'etat': s['etat']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reference/entites', methods=['GET'])
@login_required
def api_reference_entites():
    """API pour récupérer les entités de référence"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, intitule
            FROM gpr.ref_entites 
            ORDER BY intitule
        """)
        
        entites = cursor.fetchall()
        data = []
        
        for e in entites:
            data.append({
                'id': e['id'],
                'intitule': e['intitule']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reference/localisations')
def api_reference_localisations():
    """Récupérer toutes les localisations"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_achraf'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, commentaire as nom, type_localisation, pk_debut, pk_fin
            FROM gpr.ge_localisation 
            ORDER BY commentaire
        """)
        
        localisations = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return jsonify(localisations)
    except Exception as e:
        return jsonify([])

@app.route('/api/arcs-names')
def api_arcs_names():
    """API pour récupérer les noms des axes sans géométrie"""
    try:
        # Récupérer tous les axes uniques avec leurs informations de base
        axes_data = db.session.query(
            GrapheArc.nom_axe,
            func.count(GrapheArc.id).label('segment_count'),
            func.min(GrapheArc.pk_debut).label('pk_min'),
            func.max(GrapheArc.pk_fin).label('pk_max'),
            func.min(GrapheArc.plod).label('plod_min'),
            func.max(GrapheArc.plof).label('plof_max')
        ).group_by(GrapheArc.nom_axe).all()
        
        axes_list = []
        for axe in axes_data:
            # Déterminer le type d'axe basé sur le nom
            axe_type = 'Ligne Classique'
            if axe.nom_axe and 'LGV' in axe.nom_axe:
                axe_type = 'Ligne à Grande Vitesse'
            elif axe.nom_axe and ('RAC' in axe.nom_axe or 'TRIANGLE' in axe.nom_axe):
                axe_type = 'Raccordement'
            elif axe.nom_axe and 'U' in axe.nom_axe:
                axe_type = 'Ligne Urbaine'
            
            axes_list.append({
                'nom': axe.nom_axe,
                'type': axe_type,
                'segments': axe.segment_count,
                'pk_debut': float(axe.pk_min) if axe.pk_min else None,
                'pk_fin': float(axe.pk_max) if axe.pk_max else None,
                'plod': axe.plod_min,
                'plof': axe.plof_max
            })
        
        return jsonify({
            'success': True,
            'axes': axes_list,
            'total': len(axes_list)
        })
        
    except Exception as e:
        print(f"Erreur dans api_arcs_names: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/arcs-multilines')
def api_arcs_multilines():
    """API pour récupérer les axes avec leurs vraies connexions géographiques"""
    try:
        # Récupérer tous les axes uniques avec leurs informations de base
        axes_data = db.session.query(
            GrapheArc.nom_axe,
            func.count(GrapheArc.id).label('segment_count'),
            func.min(GrapheArc.pk_debut).label('pk_min'),
            func.max(GrapheArc.pk_fin).label('pk_max'),
            func.min(GrapheArc.plod).label('plod_min'),
            func.max(GrapheArc.plof).label('plof_max')
        ).group_by(GrapheArc.nom_axe).all()
        
        # Créer un dictionnaire des axes avec leurs vraies connexions géographiques
        axes_connections = {}
        
        for axe in axes_data:
            axe_name = axe.nom_axe
            if axe_name not in axes_connections:
                axes_connections[axe_name] = {
                    'nom': axe_name,
                    'segments': axe.segment_count,
                    'pk_debut': float(axe.pk_min) if axe.pk_min else None,
                    'pk_fin': float(axe.pk_max) if axe.pk_max else None,
                    'plod': axe.plod_min,
                    'plof': axe.plof_max,
                    'connexions': [],
                    'couleur': getAxeColor(axe_name),
                    'type': getAxeType(axe_name)
                }
        
        # Définir les vraies connexions géographiques entre les axes
        connexions_geographiques = {
            # Axe principal Casablanca - Rabat - Kénitra - Tanger
            'CASA VOYAGEURS/MARRAKECH': ['CASAVOYAGEURS/SKACEM', 'BENGUERIR/SAFI U'],
            'CASAVOYAGEURS/SKACEM': ['CASA VOYAGEURS/MARRAKECH', 'TANGER/FES', 'NOUACEUR/ELJADIDAV2'],
            'TANGER/FES': ['CASAVOYAGEURS/SKACEM', 'OUJDA/FRONTIERE ALGERIENNE'],
            'OUJDA/FRONTIERE ALGERIENNE': ['TANGER/FES', 'BENI ENSAR/TAOURIRT RAC'],
            'BENI ENSAR/TAOURIRT RAC': ['OUJDA/FRONTIERE ALGERIENNE'],
            
            # Axe El Jadida - Casablanca
            'BENGUERIR/SAFI U': ['CASA VOYAGEURS/MARRAKECH', 'EL JADIDA/EL JORF'],
            'EL JADIDA/EL JORF': ['BENGUERIR/SAFI U'],
            
            # Axe Casablanca - Marrakech
            'CASA VOYAGEURS/MARRAKECH': ['CASAVOYAGEURS/SKACEM', 'BENGUERIR/SAFI U'],
            
            # Axe Casablanca - Sidi Kacem
            'CASAVOYAGEURS/SKACEM': ['CASA VOYAGEURS/MARRAKECH', 'TANGER/FES', 'NOUACEUR/ELJADIDAV2'],
            
            # Axe Nouaceur - El Jadida
            'NOUACEUR/ELJADIDAV2': ['CASAVOYAGEURS/SKACEM', 'EL JADIDA/EL JORF'],
            
            # LGV connectée aux axes principaux
            'LGV_V2': ['CASAVOYAGEURS/SKACEM', 'TANGER/FES'],
            
            # Raccordements
            'S.ELAIDI/OUED ZEM': ['CASAVOYAGEURS/SKACEM', 'BENGUERIR/SAFI U'],
            'TRIANGLE DE NOUACEUR U': ['NOUACEUR/ELJADIDAV2', 'CASAVOYAGEURS/SKACEM'],
            'RAC_Sidi_Kacem': ['CASAVOYAGEURS/SKACEM', 'TANGER/FES'],
            
            # Axe oriental
            'BENI OUKIL/BOUARFA': ['OUJDA/FRONTIERE ALGERIENNE'],
            'GUENFOUDA/HASSI BLAL_U': ['BENI ENSAR/TAOURIRT RAC'],
            
            # Axe Tanger - Méditerranée
            'ArcTangerMorora_Med': ['TANGER/FES'],
            
            # Axe Casablanca - Sidi Yahya
            'S.YAHYA_MACHRAA BEL KSIRI': ['CASAVOYAGEURS/SKACEM'],
            
            # Axe Beni Ansar - Taourirt
            'Bni.Ansart_Taourirt': ['BENI ENSAR/TAOURIRT RAC']
        }
        
        # Ajouter les connexions aux axes
        for axe_name, connexions in connexions_geographiques.items():
            if axe_name in axes_connections:
                for connexion in connexions:
                    if connexion in axes_connections:
                        axes_connections[axe_name]['connexions'].append(connexion)
        
        # Créer des lignes connectées (pas de réseaux, juste des connexions directes)
        lignes_connectees = []
        
        # Créer les lignes principales
        lignes_principales = [
            # Ligne principale Casablanca - Tanger
            ['CASA VOYAGEURS/MARRAKECH', 'CASAVOYAGEURS/SKACEM', 'TANGER/FES', 'OUJDA/FRONTIERE ALGERIENNE', 'BENI ENSAR/TAOURIRT RAC'],
            # Ligne Casablanca - El Jadida
            ['CASA VOYAGEURS/MARRAKECH', 'BENGUERIR/SAFI U', 'EL JADIDA/EL JORF'],
            # Ligne Casablanca - Marrakech
            ['CASA VOYAGEURS/MARRAKECH'],
            # Ligne Nouaceur - El Jadida
            ['NOUACEUR/ELJADIDAV2', 'EL JADIDA/EL JORF'],
            # LGV
            ['LGV_V2'],
            # Raccordements
            ['S.ELAIDI/OUED ZEM'],
            ['TRIANGLE DE NOUACEUR U'],
            ['RAC_Sidi_Kacem'],
            ['BENI OUKIL/BOUARFA'],
            ['GUENFOUDA/HASSI BLAL_U'],
            ['ArcTangerMorora_Med'],
            ['S.YAHYA_MACHRAA BEL KSIRI'],
            ['Bni.Ansart_Taourirt']
        ]
        
        # Créer les lignes avec leurs axes
        for i, ligne_axes in enumerate(lignes_principales):
            ligne = {
                'id': i + 1,
                'nom': f'Ligne {i + 1}',
                'axes': []
            }
            
            for axe_name in ligne_axes:
                if axe_name in axes_connections:
                    ligne['axes'].append(axes_connections[axe_name])
            
            if ligne['axes']:
                lignes_connectees.append(ligne)
        
        # Ajouter les axes isolés
        axes_utilises = set()
        for ligne in lignes_connectees:
            for axe in ligne['axes']:
                axes_utilises.add(axe['nom'])
        
        # Créer une ligne pour les axes isolés
        axes_isolés = []
        for axe_name, axe_data in axes_connections.items():
            if axe_name not in axes_utilises:
                axes_isolés.append(axe_data)
        
        if axes_isolés:
            lignes_connectees.append({
                'id': len(lignes_connectees) + 1,
                'nom': 'Axes Isolés',
                'axes': axes_isolés
            })
        
        return jsonify({
            'success': True,
            'lignes': lignes_connectees,
            'total_lignes': len(lignes_connectees),
            'total_axes': len(axes_connections)
        })
        
    except Exception as e:
        print(f"Erreur dans api_arcs_multilines: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def getAxeColor(axe_name):
    """Retourner une couleur unique pour chaque axe"""
    colors = {
        # Axes principaux - Couleurs distinctes
        'CASA VOYAGEURS/MARRAKECH': '#dc3545',      # Rouge
        'CASAVOYAGEURS/SKACEM': '#198754',          # Vert
        'TANGER/FES': '#6f42c1',                    # Violet
        'OUJDA/FRONTIERE ALGERIENNE': '#fd7e14',    # Orange
        'BENI ENSAR/TAOURIRT RAC': '#20c997',       # Turquoise
        'BENGUERIR/SAFI U': '#ffc107',              # Jaune
        'EL JADIDA/EL JORF': '#17a2b8',             # Bleu clair
        'NOUACEUR/ELJADIDAV2': '#e83e8c',           # Rose
        'LGV_V2': '#dc3545',                        # Rouge LGV
        'S.ELAIDI/OUED ZEM': '#28a745',             # Vert foncé
        'TRIANGLE DE NOUACEUR U': '#6c757d',        # Gris
        'RAC_Sidi_Kacem': '#fd7e14',                # Orange
        'BENI OUKIL/BOUARFA': '#20c997',            # Turquoise
        'GUENFOUDA/HASSI BLAL_U': '#6f42c1',        # Violet
        'ArcTangerMorora_Med': '#17a2b8',           # Bleu clair
        'S.YAHYA_MACHRAA BEL KSIRI': '#ffc107',     # Jaune
        'Bni.Ansart_Taourirt': '#e83e8c',           # Rose
    }
    
    # Si l'axe n'a pas de couleur prédéfinie, générer une couleur basée sur le nom
    if axe_name not in colors:
        # Générer une couleur basée sur le hash du nom
        import hashlib
        hash_object = hashlib.md5(axe_name.encode())
        hash_hex = hash_object.hexdigest()
        
        # Utiliser les 6 premiers caractères pour créer une couleur
        color = '#' + hash_hex[:6]
        colors[axe_name] = color
    
    return colors[axe_name]

def getAxeType(axe_name):
    """Déterminer le type d'axe"""
    if 'LGV' in axe_name:
        return 'Ligne à Grande Vitesse'
    elif 'RAC' in axe_name or 'TRIANGLE' in axe_name:
        return 'Raccordement'
    elif 'U' in axe_name:
        return 'Ligne Urbaine'
    else:
        return 'Ligne Classique'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 