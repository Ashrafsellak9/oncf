# 🔐 Informations de Connexion - Application ONCF EMS

## 📋 Comptes Utilisateurs Disponibles

### 👨‍💼 Administrateur Principal
- **Nom d'utilisateur:** `admin`
- **Mot de passe:** `admin123`
- **Email:** `admin@oncf.ma`
- **Rôle:** Administrateur
- **Permissions:** Accès complet à toutes les fonctionnalités

## 🌐 Accès à l'Application

### URL de Connexion
```
http://localhost:5000/login
```

### URL de l'Application
```
http://localhost:5000
```

## 🚀 Démarrage de l'Application

1. **Démarrer l'application:**
   ```bash
   python app.py
   ```

2. **Ouvrir votre navigateur et aller à:**
   ```
   http://localhost:5000
   ```

3. **Se connecter avec les identifiants:**
   - Nom d'utilisateur: `admin`
   - Mot de passe: `admin123`

## 📊 Fonctionnalités Disponibles

Une fois connecté, vous aurez accès à :

- **📈 Dashboard:** Vue d'ensemble avec statistiques
- **🗺️ Carte Interactive:** Visualisation géographique des données
- **📊 Statistiques:** Analyses détaillées
- **🚉 Gares:** Gestion des gares ferroviaires
- **⚠️ Incidents:** Suivi des incidents
- **🛤️ Axes:** Gestion des axes ferroviaires
- **📚 Référence:** Données de référence (types, sous-types, systèmes, etc.)

## 🔧 Configuration de la Base de Données

- **Base de données:** PostgreSQL
- **Nom de la base:** `oncf_achraf`
- **Schéma:** `gpr`
- **URL de connexion:** `postgresql://postgres:postgres@localhost:5432/oncf_achraf`

## ⚠️ Notes Importantes

1. **Sécurité:** Changez le mot de passe par défaut après la première connexion
2. **Base de données:** Assurez-vous que PostgreSQL est en cours d'exécution
3. **Port:** L'application utilise le port 5000 par défaut
4. **Données:** Toutes les données sont importées dans le schéma `gpr`

## 🆘 Support

En cas de problème de connexion :
1. Vérifiez que l'application Flask est démarrée
2. Vérifiez que PostgreSQL est en cours d'exécution
3. Vérifiez que la base de données `oncf_achraf` existe
4. Vérifiez que les tables ont été créées dans le schéma `gpr`

---
*Document généré automatiquement - ONCF EMS System*
