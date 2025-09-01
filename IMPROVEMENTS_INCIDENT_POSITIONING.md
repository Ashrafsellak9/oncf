# Améliorations du Positionnement des Incidents - Suivant les Gares

## Objectif
Assurer que tous les incidents sont localisés "suivant les gares" pour un meilleur affichage de la carte, éviter que les incidents apparaissent "ailleurs", et garantir qu'ils sont sur la "même ligne" que les gares.

## Problèmes Identifiés
1. **Priorité aux coordonnées réelles** : Le système utilisait en priorité les coordonnées de la base de données, même si elles étaient hors des lignes ferroviaires
2. **Positionnement non aligné avec les gares** : Les incidents pouvaient apparaître loin des gares et des lignes ferroviaires
3. **Manque de validation géographique** : Pas de vérification si les coordonnées étaient sur des lignes ferroviaires

## Solutions Implémentées

### 1. Nouvelle Logique de Priorité dans `createIncidentMarker`

**Avant :**
```javascript
// PRIORITÉ 1: Utiliser les coordonnées réelles de la base de données
if (incident.geometrie && incident.geometrie !== 'None') {
    coords = parseGeometry(incident.geometrie);
    // ...
}
```

**Après :**
```javascript
// NOUVELLE LOGIQUE: Prioriser le positionnement suivant les gares et sur les lignes ferroviaires
// PRIORITÉ 1: Positionnement logique basé sur les gares et lignes ferroviaires
coords = generateLogicalIncidentPosition(incident);

// PRIORITÉ 2: Vérifier si les coordonnées réelles sont sur une ligne ferroviaire
if (incident.geometrie && incident.geometrie !== 'None') {
    const realCoords = parseGeometry(incident.geometrie);
    if (realCoords && validateCoordinates(realCoords[0], realCoords[1])) {
        const isOnRailwayLine = checkIfOnRailwayLine(realCoords[0], realCoords[1]);
        if (isOnRailwayLine) {
            coords = realCoords;
        }
    }
}
```

### 2. Nouvelle Fonction `checkIfOnRailwayLine`

Cette fonction vérifie si des coordonnées sont sur ou proches d'une ligne ferroviaire :

```javascript
function checkIfOnRailwayLine(lat, lng) {
    const garePositions = getGarePositions();
    const axePositions = getAxePositions();
    
    const maxDistance = 0.02; // ~2km
    
    // Vérifier si le point est proche d'une gare
    for (const [gareName, gareCoords] of Object.entries(garePositions)) {
        const distance = calculateDistance([lat, lng], gareCoords);
        if (distance <= maxDistance) {
            return true;
        }
    }
    
    // Vérifier si le point est proche d'un axe ferroviaire
    for (const [axeName, axePoints] of Object.entries(axePositions)) {
        for (let i = 0; i < axePoints.length - 1; i++) {
            const point1 = axePoints[i];
            const point2 = axePoints[i + 1];
            
            const distance = distanceToLine([lat, lng], point1, point2);
            if (distance <= maxDistance) {
                return true;
            }
        }
    }
    
    return false;
}
```

### 3. Amélioration du Positionnement en Gare

**Avant :**
```javascript
// INCIDENT EN GARE : Positionner sur la gare spécifiée
if (gareDebutName && garePositions[gareDebutName]) {
    coords = garePositions[gareDebutName];
}
```

**Après :**
```javascript
// INCIDENT EN GARE : Positionner sur la gare spécifiée avec variation pour éviter la superposition
if (gareDebutName && garePositions[gareDebutName]) {
    const baseCoords = garePositions[gareDebutName];
    const variation = 0.001; // ~100m
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
    coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
}
```

### 4. Amélioration du Positionnement en Ligne

**Avant :**
```javascript
// Position au milieu entre les deux gares
return [
    (gareDebut[0] + gareFin[0]) / 2,
    (gareDebut[1] + gareFin[1]) / 2
];
```

**Après :**
```javascript
// Position au milieu entre les deux gares avec variation basée sur l'ID pour éviter la superposition
const baseLat = (gareDebut[0] + gareFin[0]) / 2;
const baseLng = (gareDebut[1] + gareFin[1]) / 2;

const variation = 0.001; // ~100m
const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);

return [baseLat + offsetLat, baseLng + offsetLng];
```

### 5. Amélioration du Fallback Final

**Avant :**
```javascript
console.log(`❓ Incident ${incident.id}: Aucune donnée de localisation, positionnement sur réseau principal`);
```

**Après :**
```javascript
console.log(`❓ Incident ${incident.id}: Aucune donnée de localisation, positionnement suivant les gares principales`);

// Positionner sur les gares principales avec distribution intelligente suivant les lignes ferroviaires
const mainStations = [
    [33.5970, -7.6186], // Casablanca Voyageurs - Hub principal
    [34.0209, -6.8417], // Rabat Ville - Axe Nord
    [31.6295, -7.9811], // Marrakech - Axe Sud
    [34.0334, -4.9998], // Fès - Axe Est
    [35.7595, -5.8340], // Tanger - Axe Nord
    [34.6867, -1.9114], // Oujda - Axe Est
    [32.2372, -7.9549], // Benguerir - Axe Phosphates
    [33.2316, -8.5007]  // El Jadida - Axe Atlantique
];
```

## Fonction `distanceToLine`

Nouvelle fonction pour calculer la distance d'un point à une ligne :

```javascript
function distanceToLine(point, lineStart, lineEnd) {
    const A = point[0] - lineStart[0];
    const B = point[1] - lineStart[1];
    const C = lineEnd[0] - lineStart[0];
    const D = lineEnd[1] - lineStart[1];
    
    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    
    if (lenSq === 0) {
        return calculateDistance(point, lineStart);
    }
    
    const param = dot / lenSq;
    
    let xx, yy;
    if (param < 0) {
        xx = lineStart[0];
        yy = lineStart[1];
    } else if (param > 1) {
        xx = lineEnd[0];
        yy = lineEnd[1];
    } else {
        xx = lineStart[0] + param * C;
        yy = lineStart[1] + param * D;
    }
    
    const dx = point[0] - xx;
    const dy = point[1] - yy;
    
    return Math.sqrt(dx * dx + dy * dy);
}
```

## Résultats Attendus

1. **Positionnement cohérent** : Tous les incidents seront positionnés suivant les gares et sur les lignes ferroviaires
2. **Évitement des superpositions** : Chaque incident aura une position unique grâce aux variations basées sur l'ID
3. **Validation géographique** : Les coordonnées réelles ne seront utilisées que si elles sont sur des lignes ferroviaires
4. **Meilleur affichage** : Les incidents apparaîtront toujours proches des gares et sur les mêmes lignes

## Avantages

- **Cohérence visuelle** : Les incidents suivent la même logique de positionnement que les gares
- **Précision géographique** : Tous les incidents sont garantis d'être sur des lignes ferroviaires
- **Distribution intelligente** : Évite la concentration d'incidents au même endroit
- **Robustesse** : Fallback intelligent pour les incidents sans données de localisation

## Tests Recommandés

1. Vérifier que les incidents apparaissent toujours proches des gares
2. Confirmer qu'aucun incident n'apparaît en mer ou hors des lignes ferroviaires
3. Tester avec des incidents ayant des coordonnées réelles hors ligne
4. Vérifier la distribution des incidents sur les différentes lignes
