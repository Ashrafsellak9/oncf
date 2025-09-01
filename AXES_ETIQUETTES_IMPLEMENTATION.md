# Implémentation des Axes Ferroviaires avec Étiquettes

## Vue d'ensemble

Cette implémentation permet d'afficher les axes ferroviaires du Maroc sur la carte interactive **sans utiliser leur géométrie**, mais plutôt avec des **étiquettes (labels)** et des **polygones simples** pour représenter les zones de chaque axe.

## Fonctionnalités Implémentées

### 1. Nouvelle API `/api/arcs-names`
- **Endpoint**: `GET /api/arcs-names`
- **Fonction**: Récupère tous les axes uniques avec leurs informations de base
- **Données retournées**:
  - Nom de l'axe
  - Type d'axe (Ligne à Grande Vitesse, Raccordement, Ligne Urbaine, Ligne Classique)
  - Nombre de segments
  - Points kilométriques (PK début/fin)
  - Points de localisation (PLOD/PLOF)

### 2. Affichage avec Étiquettes
- **Étiquettes colorées** avec le nom de chaque axe
- **Polygones simples** pour représenter les zones
- **Positions prédéfinies** pour les axes principaux
- **Positions aléatoires** dans les limites du Maroc pour les autres axes

### 3. Classification des Types d'Axes
- **Ligne à Grande Vitesse** (LGV): Rose (#e83e8c)
- **Raccordement**: Jaune (#ffc107)
- **Ligne Urbaine**: Bleu clair (#17a2b8)
- **Ligne Classique**: Bleu (#007bff)

### 4. Interactions
- **Popups informatifs** au clic sur les étiquettes ou polygones
- **Panneau d'information** détaillé
- **Hover effects** sur les étiquettes
- **Contrôle des couches** pour activer/désactiver l'affichage

## Structure des Données

### API Response
```json
{
  "success": true,
  "total": 45,
  "axes": [
    {
      "nom": "CASA VOYAGEURS/MARRAKECH",
      "type": "Ligne Urbaine",
      "segments": 1,
      "pk_debut": 8.34,
      "pk_fin": 8.5,
      "plod": "8",
      "plof": "340"
    }
  ]
}
```

### Positions Prédéfinies
Les axes principaux ont des positions géographiques prédéfinies :
- **CASA VOYAGEURS/MARRAKECH**: 31.6°N, 7.9°W
- **CASAVOYAGEURS/SKACEM**: 34.0°N, 6.8°W
- **BENGUERIR/SAFI U**: 32.3°N, 8.4°W
- **TANGER/FES**: 34.0°N, 5.3°W
- **LGV_V2**: 33.6°N, 6.8°W
- **OUJDA/FRONTIERE ALGERIENNE**: 34.7°N, 1.9°W

## Fichiers Modifiés

### 1. `app.py`
- Ajout de la route `/api/arcs-names`
- Import de `func` de SQLAlchemy
- Logique de classification des types d'axes

### 2. `static/js/carte.js`
- Nouvelle fonction `addAxesLabelsToMap()`
- Fonctions de support : `getAxeColor()`, `getAxeFillColor()`
- Fonctions d'interface : `createAxeLabelPopup()`, `showAxeLabelInfo()`
- Modification de l'initialisation pour utiliser les étiquettes

### 3. `static/css/style.css`
- Styles pour les étiquettes `.axe-label`
- Styles pour les popups `.axe-popup`
- Styles pour les polygones `.axe-polygon`
- Styles responsives pour mobile

## Statistiques des Axes

### Répartition par Type
- **Ligne Classique**: 18 axes
- **Ligne Urbaine**: 14 axes
- **Raccordement**: 8 axes
- **Ligne à Grande Vitesse**: 5 axes

### Total
- **45 axes uniques** dans la base de données
- **52 segments** au total (certains axes ont plusieurs segments)

## Utilisation

1. **Ouvrir la carte interactive** dans le navigateur
2. **Les étiquettes des axes** s'affichent automatiquement
3. **Cliquer sur une étiquette** pour voir les détails
4. **Utiliser le contrôle des couches** pour activer/désactiver l'affichage

## Avantages de cette Approche

1. **Pas de dépendance à la géométrie** - fonctionne même si les données géométriques sont incomplètes
2. **Affichage clair** - chaque axe est clairement identifié par son nom
3. **Performance optimisée** - pas de calculs géométriques complexes
4. **Interface intuitive** - étiquettes colorées et informatives
5. **Flexibilité** - facile d'ajouter de nouveaux axes ou de modifier les positions

## Prochaines Étapes Possibles

1. **Améliorer les positions** en utilisant des données géographiques réelles
2. **Ajouter des icônes spécifiques** pour chaque type d'axe
3. **Implémenter un clustering** pour éviter la surcharge visuelle
4. **Ajouter des filtres** par type d'axe
5. **Intégrer avec les incidents** pour montrer les axes affectés
