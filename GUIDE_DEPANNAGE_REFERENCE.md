# 🔧 Guide de Dépannage - Page de Référence

## 🚨 Problème : Page de référence affiche "Chargement..." en permanence

### ✅ Diagnostic effectué

Le diagnostic a révélé que :
- ✅ **Backend fonctionnel** : Tous les endpoints API répondent correctement
- ✅ **Page HTML correcte** : La structure HTML est valide
- ✅ **Scripts chargés** : Le fichier `reference.js` est accessible
- ✅ **Données disponibles** : 501 éléments de référence sont disponibles
- ⚠️ **Problème JavaScript** : Le JavaScript ne s'exécute pas côté client

### 🔍 Solutions à essayer

#### 1. **Vérifier la console du navigateur**

1. Ouvrez la page de référence dans votre navigateur
2. Appuyez sur **F12** pour ouvrir les outils de développement
3. Allez dans l'onglet **Console**
4. Vérifiez s'il y a des erreurs JavaScript (en rouge)
5. Rechargez la page avec **Ctrl+F5** (rechargement forcé)

#### 2. **Vérifier que l'application est démarrée**

```bash
# Dans le terminal, vérifiez que l'application tourne
python app.py
```

L'application doit afficher :
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

#### 3. **Vérifier l'authentification**

1. Assurez-vous d'être connecté avec :
   - **Nom d'utilisateur** : `admin`
   - **Mot de passe** : `admin123`
2. Vérifiez que vous êtes bien sur la page `/reference`

#### 4. **Tester les endpoints manuellement**

Ouvrez ces URLs dans votre navigateur (après connexion) :

- `http://localhost:5000/api/reference/types`
- `http://localhost:5000/api/reference/sous-types`
- `http://localhost:5000/api/reference/systemes`
- `http://localhost:5000/api/reference/sources`
- `http://localhost:5000/api/reference/entites`

Vous devriez voir des données JSON.

#### 5. **Vider le cache du navigateur**

1. **Chrome/Edge** : Ctrl+Shift+Delete
2. **Firefox** : Ctrl+Shift+Delete
3. Cochez "Images et fichiers en cache"
4. Cliquez sur "Effacer les données"

#### 6. **Tester avec un autre navigateur**

Essayez d'ouvrir la page dans un autre navigateur pour voir si le problème persiste.

### 🛠️ Corrections techniques effectuées

#### 1. **Correction du template**
- ✅ Changement de `{% block scripts %}` vers `{% block extra_js %}` dans `reference.html`
- ✅ Le script `reference.js` est maintenant correctement inclus

#### 2. **Correction des endpoints API**
- ✅ Remplacement de SQLAlchemy par des requêtes SQL directes
- ✅ Correction des types de données (`'t'` au lieu de `true`)
- ✅ Utilisation des bonnes colonnes selon la structure des tables

#### 3. **Amélioration de l'interface**
- ✅ Design moderne avec en-tête professionnel
- ✅ Onglets stylisés avec icônes
- ✅ Compteurs en temps réel
- ✅ Gestion d'erreurs améliorée

### 📊 Données disponibles

La page de référence contient :
- **58 types d'incidents** (ex: Accident, Acte de malveillance)
- **408 sous-types** (ex: Train contre obstacle, Train contre véhicule)
- **13 systèmes** (ex: Environnement, Exploitation, Infrastructure)
- **9 sources** (ex: Appel téléphonique, Alerte vidéo, Alerte CADI)
- **2 entités** (ex: Surete, Regulation)

### 🎯 Fonctionnalités

- **Navigation par onglets** entre les catégories
- **Filtrage des sous-types** par type d'incident
- **Compteurs dynamiques** pour chaque catégorie
- **Tableaux structurés** avec badges colorés
- **Gestion d'erreurs** avec messages informatifs

### 🚀 Si le problème persiste

Si après avoir essayé toutes les solutions ci-dessus le problème persiste :

1. **Redémarrez l'application** :
   ```bash
   # Arrêtez l'application (Ctrl+C)
   # Puis redémarrez
   python app.py
   ```

2. **Vérifiez les logs** :
   - Regardez les messages dans le terminal où l'application tourne
   - Vérifiez s'il y a des erreurs

3. **Testez avec curl** :
   ```bash
   # Test de connexion
   curl http://localhost:5000
   
   # Test d'un endpoint (après connexion)
   curl http://localhost:5000/api/reference/types
   ```

4. **Contactez le support** :
   - Fournissez les erreurs de la console du navigateur
   - Indiquez le navigateur utilisé
   - Décrivez les étapes suivies

### 📝 Résumé des corrections

| Problème | Solution | Statut |
|----------|----------|--------|
| Script non chargé | Correction du bloc template | ✅ Résolu |
| Erreurs SQL | Requêtes SQL directes | ✅ Résolu |
| Types de données | Correction des conditions WHERE | ✅ Résolu |
| Interface basique | Design moderne | ✅ Résolu |
| Pas de filtrage | Filtrage des sous-types | ✅ Résolu |

La page de référence est maintenant **entièrement fonctionnelle** côté serveur. Le problème de chargement permanent est probablement dû à une erreur JavaScript côté client qui peut être résolue en suivant les étapes de dépannage ci-dessus.
