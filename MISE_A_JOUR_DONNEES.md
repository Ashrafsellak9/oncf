# Mise à Jour des Données ONCF EMS

## Résumé des Modifications

Cette mise à jour a permis d'importer et d'afficher toutes les données disponibles dans le dossier `sql_data` dans une nouvelle base de données `oncf_achraf`.

## Nouvelles Données Importées

### 1. Axes Ferroviaires (`axes.csv`)
- **Table**: `gpr.graphe_arc`
- **Données**: Informations sur les axes ferroviaires avec géométries
- **Colonnes principales**:
  - `axe`: Nom de l'axe
  - `cumuld`, `cumulf`: Points kilométriques début/fin
  - `plod`, `plof`: Points de localisation début/fin
  - `geometrie`: Géométrie WKT/WKB

### 2. Gares (`gares.csv`)
- **Table**: `gpr.gpd_gares_ref`
- **Données**: Informations détaillées sur toutes les gares
- **Colonnes principales**:
  - `nomgarefr`: Nom de la gare
  - `codegare`: Code de la gare
  - `typegare`: Type (STATION, Haltes, etc.)
  - `geometrie`: Coordonnées géographiques

### 3. Incidents (`incidents.csv`)
- **Table**: `gpr.ge_evenement`
- **Données**: Tous les incidents et événements
- **Colonnes principales**:
  - `date_avis`, `date_debut`, `date_fin`: Dates des événements
  - `resume`, `commentaire`: Descriptions
  - `etat`: Statut (Ouvert, Fermé)
  - `type_id`, `sous_type_id`: Types d'incidents

### 4. Localisations (`localisation.csv`)
- **Table**: `gpr.ge_localisation`
- **Données**: Localisations précises des événements
- **Colonnes principales**:
  - `type_localisation`: Type de localisation
  - `pk_debut`, `pk_fin`: Points kilométriques
  - `gare_debut_id`, `gare_fin_id`: Gares de référence

### 5. Données de Référence
- **Types** (`ref_types.csv`): Types d'événements
- **Sous-types** (`ref_sous_types.csv`): Sous-catégories
- **Systèmes** (`ref_systemes.csv`): Systèmes affectés
- **Sources** (`ref_sources.csv`): Sources d'information
- **Entités** (`ref_entites.csv`): Entités organisationnelles

## Nouvelles Fonctionnalités

### 1. Page Axes Ferroviaires (`/axes`)
- Affichage paginé de tous les axes
- Recherche par nom d'axe
- Informations détaillées sur chaque axe
- Indication de la disponibilité des géométries

### 2. Page Données de Référence (`/reference`)
- Interface à onglets pour toutes les données de référence
- Filtrage des sous-types par type
- Affichage des dates de mise à jour
- Navigation intuitive entre les différentes catégories

### 3. Dashboard Amélioré
- Statistiques globales mises à jour
- Compteurs pour toutes les entités :
  - Total gares
  - Total axes ferroviaires
  - Total incidents (ouverts/fermés)
  - Total localisations
  - Données de référence

### 4. Nouvelles APIs
- `/api/axes`: Récupération des axes avec pagination et recherche
- `/api/reference/types`: Types de référence
- `/api/reference/sous-types`: Sous-types avec filtrage
- `/api/reference/systemes`: Systèmes
- `/api/reference/sources`: Sources
- `/api/reference/entites`: Entités
- `/api/statistics`: Statistiques globales

## Configuration de la Base de Données

- **Nouvelle base**: `oncf_achraf`
- **Schéma**: `gpr` (pour toutes les tables métier)
- **Tables utilisateurs**: `users` (dans le schéma public)

## Script d'Importation

Le script `import_all_data.py` a été créé pour :
1. Créer automatiquement la base de données
2. Créer le schéma et toutes les tables
3. Importer toutes les données CSV
4. Gérer les erreurs de parsing
5. Convertir les géométries WKB en WKT

## Navigation Mise à Jour

Le menu de navigation inclut maintenant :
- **Axes**: Nouvelle page pour les axes ferroviaires
- **Référence**: Page pour les données de référence
- Toutes les pages existantes conservées

## Statistiques Disponibles

Le dashboard affiche maintenant :
- **157 gares** au total
- **Milliers d'axes** ferroviaires
- **1577 incidents** enregistrés
- **357 localisations** précises
- Données de référence complètes

## Prochaines Étapes Possibles

1. **Visualisation cartographique** des axes
2. **Analyse temporelle** des incidents
3. **Filtres avancés** par région/axe
4. **Export de données** en différents formats
5. **Alertes automatiques** basées sur les incidents
6. **Rapports personnalisés** par utilisateur

## Notes Techniques

- Toutes les données sont maintenant dans PostgreSQL
- Géométries stockées en format WKT pour compatibilité
- Pagination implémentée pour les gros volumes
- Recherche textuelle sur les axes
- Interface responsive pour tous les écrans

## Accès à l'Application

L'application est accessible sur `http://localhost:5000` avec :
- **Base de données**: `oncf_achraf`
- **Authentification**: Système utilisateur conservé
- **Toutes les données**: Importées et fonctionnelles
