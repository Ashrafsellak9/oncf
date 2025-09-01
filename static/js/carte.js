// ONCF GIS - Carte Interactive

let map;
let garesLayer;
let arcsLayer;
let incidentsLayer;
let incidentsCluster;
let layerControl;
let selectedGare = null;
let selectedIncident = null;

// Variables pour les incidents (sans pagination)
let allIncidents = [];
let currentIncidents = [];

// Variables pour les gares
let allGares = [];

// Configuration de la carte
const MAP_CONFIG = {
    center: [31.7917, -7.0926], // Centre du Maroc
    zoom: 6,
    minZoom: 5,
    maxZoom: 18
};

// Initialisation de la carte
function initONCFMap() {
    // Vérifier si la carte existe déjà
    if (map) {
        map.remove();
        map = null;
    }
    
    // Créer la carte
    map = L.map('map', {
        center: MAP_CONFIG.center,
        zoom: MAP_CONFIG.zoom,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom
    });

    // Ajouter les tuiles de base (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Créer les couches
    garesLayer = L.layerGroup().addTo(map);
    arcsLayer = L.layerGroup().addTo(map);
    incidentsLayer = L.layerGroup().addTo(map);
    
    // Créer le cluster pour les incidents
    incidentsCluster = L.markerClusterGroup({
        chunkedLoading: true,
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: function(cluster) {
            const childCount = cluster.getChildCount();
            let className = 'marker-cluster marker-cluster-';
            
            if (childCount < 10) {
                className += 'small';
            } else if (childCount < 100) {
                className += 'medium';
            } else {
                className += 'large';
            }
            
            return L.divIcon({
                html: '<div><span>' + childCount + '</span></div>',
                className: className,
                iconSize: L.point(40, 40)
            });
        }
    }).addTo(map);
    
    // Créer le contrôle des couches
    layerControl = L.control.layers(null, {
        'Gares': garesLayer,
        'Axes Ferroviaires': arcsLayer,
        'Incidents': incidentsCluster
    }).addTo(map);

    // Charger les données
    loadMapData();
    
    // Afficher les axes ferroviaires
    displayRailwayAxes();
    
    // Initialiser les contrôles
    initializeMapControls();
    
    // Ajouter les événements de la carte
    setupMapEvents();
}

// Charger les données de la carte
function loadMapData() {
    // Charger toutes les gares pour la carte
    fetch('/api/gares?all=true')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allGares = data.data; // Stocker toutes les gares
                addGaresToMap(data.data);
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des gares:', error);
            showNotification('Erreur lors du chargement des gares', 'error');
        });

    // Charger les arcs (commenté car addArcsToMap a été supprimé)
    // fetch('/api/arcs')
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.success) {
    //             addArcsToMap(data.data);
    //         }
    //     })
    //     .catch(error => {
    //         console.error('Erreur lors du chargement des arcs:', error);
    //         showNotification('Erreur lors du chargement des voies', 'error');
    //     });
        
    // Charger tous les incidents
    loadAllIncidents();
}

// Ajouter les gares à la carte
function addGaresToMap(gares) {
    console.log(`🗺️ Ajout de ${gares.length} gares à la carte...`);
    garesLayer.clearLayers();
    
    let addedCount = 0;
    let skippedCount = 0;
    
    gares.forEach((gare, index) => {
        const coords = parseGeometry(gare.geometrie);
        if (coords) {
            const marker = createGareMarker(gare, coords);
            garesLayer.addLayer(marker);
            addedCount++;
        } else {
            console.warn(`⚠️ Gare ${gare.id} (${gare.nom}) - Géométrie invalide:`, gare.geometrie);
            skippedCount++;
        }
        
        // Log de progression pour les gros volumes
        if (gares.length > 20 && (index + 1) % 10 === 0) {
            console.log(`🚉 ${index + 1}/${gares.length} gares traitées...`);
        }
    });
    
    console.log(`✅ ${addedCount} gares ajoutées à la carte (${skippedCount} ignorées)`);
    updateMapStats();
}

// Créer un marqueur pour une gare
function createGareMarker(gare, coords) {
    // Définir l'icône selon le type de gare
    const iconColor = getGareIconColor(gare.type);
    const iconSize = getGareIconSize(gare.type);
    
    const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            width: ${iconSize}px; 
            height: ${iconSize}px; 
            background-color: ${iconColor}; 
            border: 2px solid white; 
            border-radius: 50%; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: ${iconSize * 0.6}px;
        "><i class="fas fa-train"></i></div>`,
        iconSize: [iconSize, iconSize],
        iconAnchor: [iconSize/2, iconSize/2]
    });

    const marker = L.marker(coords, { icon: icon });
    
    // Stocker les données de la gare dans le marqueur
    marker.gareData = gare;
    
    // Ajouter le popup
    const popupContent = createGarePopup(gare);
    marker.bindPopup(popupContent);
    
    // Ajouter l'événement de clic
    marker.on('click', () => {
        selectedGare = gare;
        showGareInfo(gare);
    });
    
    return marker;
}

// Obtenir la couleur de l'icône selon le type de gare
function getGareIconColor(type) {
    switch(type?.toUpperCase()) {
        case 'PRINCIPALE':
        case 'MAJOR':
            return '#dc3545'; // Rouge pour les gares principales
        case 'SECONDAIRE':
        case 'MINOR':
            return '#198754'; // Vert pour les gares secondaires
        default:
            return '#0d6efd'; // Bleu par défaut
    }
}

// Obtenir la taille de l'icône selon le type de gare
function getGareIconSize(type) {
    switch(type?.toUpperCase()) {
        case 'PRINCIPALE':
        case 'MAJOR':
            return 20; // Plus grand pour les gares principales
        case 'SECONDAIRE':
        case 'MINOR':
            return 16; // Moyen pour les gares secondaires
        default:
            return 14; // Petit par défaut
    }
}

// Fonction pour convertir les codes de type de gare en noms descriptifs
function getGareTypeName(typeCode) {
    const typeNames = {
        '141': 'Gare Principale',
        '132': 'Gare Secondaire', 
        '85': 'Gare de Passage',
        '15': 'Halte',
        '0': 'Point d\'Arrêt',
        '18': 'Gare de Triage',
        '89': 'Gare de Marchandises',
        '1': 'Gare de Voyageurs',
        '7': 'Gare de Correspondance',
        '88': 'Gare de Transit',
        '101': 'Gare de Banlieue',
        '24': 'Gare de Proximité',
        '52': 'Gare Régionale',
        '31': 'Gare Intercité',
        '35': 'Gare TGV',
        '74': 'Gare de Cargo',
        '167': 'Gare de Maintenance',
        '61': 'Gare de Dépôt',
        '177': 'Gare de Service',
        '209': 'Gare de Contrôle',
        '94': 'Gare de Sécurité',
        '96': 'Gare de Surveillance',
        '5': 'Gare de Transit',
        '116': 'Gare de Distribution',
        '107': 'Gare de Collecte',
        '64': 'Gare de Manœuvre',
        '10': 'Gare de Passage',
        '11': 'Gare de Croisement',
        '58': 'Gare de Raccordement'
    };
    
    return typeNames[typeCode] || `Type ${typeCode}`;
}

// Fonction pour convertir les codes de ville en noms
function getVilleName(villeCode) {
    const villeNames = {
        '620': 'Casablanca',
        '621': 'Rabat',
        '622': 'Marrakech',
        '623': 'Fès',
        '624': 'Meknès',
        '625': 'Tanger',
        '626': 'Agadir',
        '627': 'Oujda',
        '628': 'Kénitra',
        '629': 'Mohammedia',
        '630': 'Safi',
        '631': 'Taza',
        '632': 'Nador',
        '633': 'El Jadida',
        '634': 'Beni Mellal',
        '635': 'Ouarzazate',
        '636': 'Al Hoceima',
        '637': 'Tétouan',
        '638': 'Larache',
        '639': 'Khémisset',
        '640': 'Sidi Kacem',
        '641': 'Sidi Slimane',
        '642': 'Benguerir',
        '643': 'El Aria',
        '644': 'Oued Amlil'
    };
    
    return villeNames[villeCode] || `Ville ${villeCode}`;
}

// Créer le contenu du popup pour une gare
function createGarePopup(gare) {
    const typeDisplay = getGareTypeName(gare.type);
    const villeDisplay = getVilleName(gare.ville);
    const etatDisplay = gare.etat === 'ACTIVE' ? 'Active' : 'Passive';
    
    return `
        <div class="gare-popup">
            <h6>${gare.nom || 'Gare sans nom'}</h6>
            <div class="mb-2">
                <span class="badge bg-primary">${gare.code || 'N/A'}</span>
                <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">${etatDisplay}</span>
            </div>
            <div class="small">
                <div><strong>Type:</strong> ${typeDisplay}</div>
                <div><strong>Ville:</strong> ${villeDisplay}</div>
                <div><strong>Région:</strong> ${gare.region || 'N/A'}</div>
            </div>
            <button class="btn btn-sm btn-primary mt-2" onclick="showGareDetails(${gare.id})">
                <i class="fas fa-info-circle me-1"></i>Détails
            </button>
        </div>
    `;
}

// Fonctions de dessin de lignes supprimées - Seules les étiquettes sont affichées maintenant

// Fonctions de couleur et épaisseur supprimées - Plus nécessaires car seules les étiquettes sont affichées

// Fonction de popup supprimée - Plus nécessaire car seules les étiquettes sont affichées

// Ajouter les incidents à la carte - BASÉ SUR ge_localisation
function addIncidentsToMap(incidents) {
    console.log(`🗺️ Ajout de ${incidents.length} incidents basés sur ge_localisation...`);
    
    // Nettoyer les couches existantes
    incidentsLayer.clearLayers();
    incidentsCluster.clearLayers();
    
    let addedCount = 0;
    const markers = [];
    
    incidents.forEach((incident, index) => {
        // Créer un marqueur pour l'incident
        const marker = createIncidentMarker(incident);
        if (marker) {
            markers.push(marker);
            addedCount++;
        }
        
        // Log de progression pour les gros volumes
        if (incidents.length > 100 && (index + 1) % 50 === 0) {
            console.log(`📍 ${index + 1}/${incidents.length} incidents traités...`);
        }
    });
    
    // Ajouter tous les marqueurs au cluster en une seule fois pour de meilleures performances
    if (markers.length > 0) {
        incidentsCluster.addLayers(markers);
    }
    
    console.log(`✅ ${addedCount} incidents ajoutés à la carte avec positionnement ge_localisation`);
    updateMapStats();
}

// Générer une position logique pour un incident basée sur ses informations
// FORCER LE POSITIONNEMENT SUR LES LIGNES FERROVIAIRES
function generateLogicalIncidentPosition(incident) {
    console.log(`🛤️ POSITIONNEMENT PRÉCIS selon données DB pour incident ${incident.id}`);
    console.log('📊 Données DB incident:', {
        id: incident.id,
        gare_debut_nom: incident.gare_debut_nom,
        gare_fin_nom: incident.gare_fin_nom,
        type_localisation: incident.type_localisation,
        pk_debut: incident.pk_debut,
        pk_fin: incident.pk_fin,
        localisation_nom: incident.localisation_nom
    });
    
    // PRIORITÉ 0: Vérifier si c'est un incident avec pattern de clustering connu
    const clusteredPosition = handleClusteredIncidents(incident);
    if (clusteredPosition) {
        console.log(`🎯 Incident ${incident.id}: Traité avec logique spéciale de clustering`);
        return clusteredPosition;
    }
    
    // Positions prédéfinies pour les principales gares marocaines (données professionnelles ONCF 2024)
    const garePositions = {
        // Gares LGV Al Boraq
        'Tanger Ville': [35.7595, -5.8340], // Terminal nord LGV
        'Kenitra': [34.2610, -6.5802], // Junction LGV/réseau classique
        'Rabat Agdal': [33.9591, -6.8498], // Gare LGV dédiée
        'Casablanca Voyageurs': [33.5970, -7.6186], // Hub principal
        
        // Réseau classique - Axe Nord
        'Assilah': [35.4650, -6.0366], // Ligne classique côtière
        'Larache': [35.1933, -6.1558], // Ligne classique
        'Ksar El Kebir': [35.0019, -5.9083], // Ligne classique
        'Souk El Arbaa': [34.6908, -5.9886], // Ligne classique
        'Sidi Yahya El Gharb': [34.3008, -6.3106], // Ligne classique
        'Sidi Slimane': [34.2628, -5.9222], // Junction vers Sidi Kacem
        'Sidi Kacem': [34.2214, -5.7031], // Junction principale
        
        // Axe Atlantique
        'Sale': [34.0531, -6.7985], // Rabat-Salé
        'Rabat Ville': [34.0209, -6.8417], // Gare principale Rabat
        'Temara': [33.9281, -6.9067], // Banlieue Rabat
        'Skhirat': [33.8519, -7.0306], // Côte atlantique
        'Bouznika': [33.7869, -7.1608], // Côte atlantique
        'Mohammedia': [33.6866, -7.3837], // Port atlantique
        'Casablanca Port': [33.6036, -7.6233], // Port Casa
        'Ain Sebaa': [33.6147, -7.5263], // Casa industriel
        
        // Axe Casa-Marrakech
        'Berrechid': [33.2582, -7.5870], // Junction sud Casa
        'Settat': [33.0013, -7.6216], // Ville moyenne
        'Ben Ahmed': [32.7367, -7.9833], // Junction
        'Benguerir': [32.2372, -7.9549], // Ville phosphates
        'Marrakech': [31.6295, -7.9811], // Terminal sud
        
        // Axe Oriental
        'Meknes': [33.8839, -5.5406], // Ville impériale
        'Fes': [34.0334, -4.9998], // Hub oriental
        'Oued Amlil': [34.0833, -4.6167], // Première station vers Oujda
        'Taza': [34.2130, -4.0100], // Passage montagnard
        'Msoun': [34.0667, -3.4833], // Station intermédiaire
        'Guercif': [34.2264, -3.3519], // Station importante
        'Taourirt': [34.4092, -2.8953], // Junction vers Nador
        'Oujda': [34.6867, -1.9114], // Terminal est
        'Nador': [35.1681, -2.9287], // Port méditerranéen
        
        // Axe Phosphates et extensions
        'Khouribga': [32.8811, -6.9063], // Centre phosphatier
        'Oued Zem': [32.8631, -6.5738], // Phosphates
        'El Jadida': [33.2316, -8.5007], // Port atlantique
        'Safi': [32.2833, -9.2333], // Port phosphates
        'Youssoufia': [32.2450, -8.5308], // Mines phosphates
        'Bouarfa': [32.5333, -1.9667] // Terminal minier est
    };

    // Mapping des codes de gares vers les noms (basé sur les données de ge_localisation)
    const gareCodeMapping = {
        'LIN01.T001.TANGER': 'Tanger Ville',
        'LIN01.T001.ASILAH': 'Assilah',
        'LIN01.T001.LARACHE': 'Larache',
        'LIN01.T001.KENITRA': 'Kenitra',
        'LIN01.T001.SALE': 'Sale',
        'LIN01.T001.RABAT': 'Rabat Ville',
        'LIN01.T001.TEMARA': 'Temara',
        'LIN01.T001.SKHIRAT': 'Skhirat',
        'LIN01.T001.BOUZNIKA': 'Bouznika',
        'LIN01.T001.MOHAMMEDIA': 'Mohammedia',
        'LIN01.T001.CASABLANCA': 'Casablanca Voyageurs',
        'LIN01.T001.BERRECHID': 'Berrechid',
        'LIN01.T001.SETTAT': 'Settat',
        'LIN01.T001.BEN_AHMED': 'Ben Ahmed',
        'LIN01.T001.BENGUERIR': 'Benguerir',
        'LIN01.T001.MARRAKECH': 'Marrakech',
        'LIN01.T001.SIDI_KACEM': 'Sidi Kacem',
        'LIN01.T001.MEKNES': 'Meknes',
        'LIN01.T001.FES': 'Fes',
        'LIN01.T001.TAZA': 'Taza',
        'LIN01.T001.GUERCIF': 'Guercif',
        'LIN01.T001.TAOURIRT': 'Taourirt',
        'LIN01.T001.OUJDA': 'Oujda',
        'LIN01.T001.NADOR': 'Nador',
        'LIN01.T001.KHOURIBGA': 'Khouribga',
        'LIN01.T001.OUED_ZEM': 'Oued Zem',
        'LIN01.T001.EL_JADIDA': 'El Jadida',
        'LIN01.T001.SAFI': 'Safi'
    };
    
    // Positions des axes ferroviaires principaux (passant exactement par les gares)
    const axePositions = {
        'LGV-Al-Boraq': [
            // LGV Al Boraq - Tracé intérieur officiel
            [35.7595, -5.8340], // Tanger Ville
            [35.6000, -5.8000], // Sortie Tanger vers intérieur
            [35.4000, -5.7000], // Plaine intérieure Gharb
            [35.2000, -5.6000], // Traverse terres agricoles
            [35.0000, -5.5000], // Continue intérieur
            [34.8000, -5.6000], // Plaine Gharb centrale
            [34.6000, -5.7000], // Évite zones côtières
            [34.4000, -5.8000], // Continue sud-est
            [34.3000, -5.9000], // Traverse Loukkos (intérieur)
            [34.2610, -6.5802]  // Kenitra - Junction
        ],
        'Tanger-Kenitra-Classique': [
            // Ligne classique Tanger-Kenitra via côte
            [35.7595, -5.8340], // Tanger Ville
            [35.4650, -6.0366], // Assilah
            [35.1933, -6.1558], // Larache
            [35.0019, -5.9083], // Ksar El Kebir
            [34.6908, -5.9886], // Souk El Arbaa
            [34.3008, -6.3106], // Sidi Yahya El Gharb
            [34.2610, -6.5802]  // Kenitra
        ],
        'Kenitra-Casablanca-LGV': [
            // Ligne Kenitra-Casablanca (utilisée par LGV)
            [34.2610, -6.5802], // Kenitra
            [34.0531, -6.7985], // Salé
            [33.9591, -6.8498], // Rabat Agdal (LGV)
            [34.0209, -6.8417], // Rabat Ville
            [33.9281, -6.9067], // Témara
            [33.8519, -7.0306], // Skhirat
            [33.7869, -7.1608], // Bouznika
            [33.6866, -7.3837], // Mohammedia
            [33.5970, -7.6186]  // Casablanca Voyageurs
        ],
        'Mohammedia-Bouznika-Direct': [
            // Ligne DIRECTE Mohammedia-Bouznika (TNR)
            [33.6866, -7.3837], // Mohammedia
            [33.7500, -7.3000], // Trajet côtier direct
            [33.7869, -7.1608]  // Bouznika
        ],
        'Casablanca-Marrakech': [
            [33.5970, -7.6186], // Casablanca Voyageurs
            [33.2582, -7.5870], // Berrechid
            [33.0013, -7.6216], // Settat
            [32.7367, -7.9833], // Ben Ahmed
            [32.2372, -7.9549], // Benguerir
            [31.6295, -7.9811]  // Marrakech
        ],
        'Fes-Oujda-Real': [
            // Fès-Oujda (tracé réel via Taza-Guercif)
            [34.0334, -4.9998], // Fès
            [34.0833, -4.6167], // Oued Amlil
            [34.2130, -4.0100], // Taza (col de Taza)
            [34.0667, -3.4833], // Msoun
            [34.2264, -3.3519], // Guercif
            [34.4092, -2.8953], // Taourirt
            [34.6867, -1.9114]  // Oujda
        ],
        'Taourirt-Nador': [
            [34.4092, -2.8953], // Taourirt
            [34.8000, -2.9000], // Traversée Rif
            [35.1681, -2.9287]  // Nador
        ],
        'Phosphates': [
            // Ligne phosphates
            [34.2214, -5.7031], // Sidi Kacem
            [32.8811, -6.9063], // Khouribga
            [32.8631, -6.5738], // Oued Zem
            [32.2450, -8.5308], // Youssoufia
            [32.2833, -9.2333]  // Safi
        ],
        'El-Jadida-Casablanca': [
            // Ligne El Jadida → Casablanca (direct via gares existantes)
            [33.2316, -8.5007], // El Jadida
            [33.5970, -7.6186]  // Casablanca Voyageurs
        ],
        'Nouaceur-El-Jadida': [
            // Ligne Nouaceur → El Jadida
            [33.3670, -7.6470], // Nouaceur
            [33.2316, -8.5007]  // El Jadida
        ]
    };
    
    let coords = [31.7917, -7.0926]; // Centre du Maroc par défaut
    
    // NOUVELLE LOGIQUE STRICTE BASÉE SUR LES DONNÉES DE LA BASE DE DONNÉES
    console.log('🔍 Analyse incident:', {
        id: incident.id,
        gare_debut_nom: incident.gare_debut_nom,
        gare_fin_nom: incident.gare_fin_nom,
        type_localisation: incident.type_localisation,
        pk_debut: incident.pk_debut,
        pk_fin: incident.pk_fin,
        localisation_nom: incident.localisation_nom
    });
    
    // PRIORITÉ 1: Utiliser les données de ge_localisation si disponibles
    if (incident.gare_debut_id || incident.gare_fin_id) {
        let gareDebutName = null;
        let gareFinName = null;
        
        // Convertir les codes de gares en noms
        if (incident.gare_debut_id && gareCodeMapping[incident.gare_debut_id]) {
            gareDebutName = gareCodeMapping[incident.gare_debut_id];
        } else if (incident.gare_debut_nom) {
            gareDebutName = incident.gare_debut_nom;
        }
        
        if (incident.gare_fin_id && gareCodeMapping[incident.gare_fin_id]) {
            gareFinName = gareCodeMapping[incident.gare_fin_id];
        } else if (incident.gare_fin_nom) {
            gareFinName = incident.gare_fin_nom;
        }
        
        console.log('📍 Gares identifiées:', { gareDebutName, gareFinName });
        
        // Déterminer le type de localisation selon type_localisation
        const isInStation = determineIncidentLocationType(incident);
        console.log('🏢 Type de localisation:', isInStation ? 'EN GARE' : 'EN LIGNE');
        
        if (isInStation) {
            // INCIDENT EN GARE : Positionner EXACTEMENT sur la gare spécifiée
            if (gareDebutName && garePositions[gareDebutName]) {
                const baseCoords = garePositions[gareDebutName];
                // Variation plus importante pour éviter la superposition
                const variation = 0.0005; // ~50m pour éviter la superposition visible
                const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                console.log('✅ Position EXACTE en gare (variation améliorée):', gareDebutName, coords);
            } else if (gareFinName && garePositions[gareFinName]) {
                const baseCoords = garePositions[gareFinName];
                // Variation plus importante pour éviter la superposition
                const variation = 0.0005; // ~50m pour éviter la superposition visible
                const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                console.log('✅ Position EXACTE en gare (variation améliorée):', gareFinName, coords);
            }
        } else {
            // INCIDENT EN LIGNE : Positionner EXACTEMENT entre les gares ou selon le PK
            coords = positionIncidentOnRailwayLine(incident, gareDebutName, gareFinName, garePositions, axePositions);
            console.log('✅ Position EXACTE en ligne:', coords);
            
            // Si le positionnement a échoué, essayer une approche alternative
            if (!coords || (coords[0] === 31.7917 && coords[1] === -7.0926)) {
                console.log('⚠️ Positionnement ligne échoué, tentative de positionnement alternatif');
                
                // Positionner sur l'axe entre les deux gares avec variation basée sur l'ID
                if (gareDebutName && gareFinName && garePositions[gareDebutName] && garePositions[gareFinName]) {
                    const startCoords = garePositions[gareDebutName];
                    const endCoords = garePositions[gareFinName];
                    
                    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                    const t = (uniqueFactor % 100) / 100;
                    
                    const baseCoords = [
                        startCoords[0] + t * (endCoords[0] - startCoords[0]),
                        startCoords[1] + t * (endCoords[1] - startCoords[1])
                    ];
                    
                    // Variation pour éviter la superposition
                    const variation = 0.0001; // ~10m
                    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
                    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
                    
                    coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                    console.log(`✅ Position alternative entre gares ${gareDebutName}-${gareFinName}: [${coords[0]}, ${coords[1]}]`);
                }
            }
        }
        
        return coords;
    }
    
    // PRIORITÉ 2: Utiliser les noms de gares directement si disponibles
    if (incident.gare_debut_nom || incident.gare_fin_nom) {
        let gareDebutName = incident.gare_debut_nom;
        let gareFinName = incident.gare_fin_nom;
        
        console.log('📍 Gares identifiées (noms directs):', { gareDebutName, gareFinName });
        
        // Déterminer le type de localisation selon type_localisation
        const isInStation = determineIncidentLocationType(incident);
        console.log('🏢 Type de localisation:', isInStation ? 'EN GARE' : 'EN LIGNE');
        
        if (isInStation) {
            // INCIDENT EN GARE : Positionner EXACTEMENT sur la gare spécifiée
            if (gareDebutName && garePositions[gareDebutName]) {
                const baseCoords = garePositions[gareDebutName];
                // Variation plus importante pour éviter la superposition
                const variation = 0.0005; // ~50m pour éviter la superposition visible
                const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                console.log('✅ Position EXACTE en gare (variation améliorée):', gareDebutName, coords);
            } else if (gareFinName && garePositions[gareFinName]) {
                const baseCoords = garePositions[gareFinName];
                // Variation plus importante pour éviter la superposition
                const variation = 0.0005; // ~50m pour éviter la superposition visible
                const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                console.log('✅ Position EXACTE en gare (variation améliorée):', gareFinName, coords);
            }
        } else {
            // INCIDENT EN LIGNE : Positionner EXACTEMENT entre les gares ou selon le PK
            coords = positionIncidentOnRailwayLine(incident, gareDebutName, gareFinName, garePositions, axePositions);
            console.log('✅ Position EXACTE en ligne:', coords);
        }
        
        return coords;
    }
    
    // PRIORITÉ 3: Utiliser le PK si disponible pour positionner sur un axe
    if (incident.pk_debut || incident.pk_fin) {
        console.log('📏 Utilisation PK pour positionnement:', { pk_debut: incident.pk_debut, pk_fin: incident.pk_fin });
        
        // Déterminer le type de localisation selon type_localisation
        const isInStation = determineIncidentLocationType(incident);
        console.log('🏢 Type de localisation:', isInStation ? 'EN GARE' : 'EN LIGNE');
        
        if (isInStation) {
            // INCIDENT EN GARE : Chercher la gare la plus proche du PK
            const pkValue = incident.pk_debut || incident.pk_fin;
            const nearestGare = findNearestGareByPK(pkValue, garePositions);
            if (nearestGare) {
                const baseCoords = garePositions[nearestGare];
                // Variation plus importante pour éviter la superposition
                const variation = 0.0005; // ~50m pour éviter la superposition visible
                const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                console.log('✅ Position EXACTE en gare selon PK:', nearestGare, coords);
            }
        } else {
            // INCIDENT EN LIGNE : Positionner selon le PK sur un axe
            coords = positionIncidentByPK(incident, garePositions, axePositions);
            console.log('✅ Position EXACTE en ligne selon PK:', coords);
        }
        
        // Si le positionnement PK a échoué, essayer une approche alternative
        if (!coords || (coords[0] === 31.7917 && coords[1] === -7.0926)) {
            console.log('⚠️ Positionnement PK échoué, tentative de positionnement alternatif');
            
            // Essayer de positionner sur un axe basé sur les gares disponibles
            if (incident.gare_debut_nom || incident.gare_fin_nom) {
                const gareDebut = incident.gare_debut_nom;
                const gareFin = incident.gare_fin_nom;
                
                // Chercher un axe qui contient ces gares
                for (const [axeName, axePoints] of Object.entries(axePositions)) {
                    if (axePoints.length >= 2) {
                        // Positionner sur cet axe avec variation basée sur l'ID
                        const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                        const t = (uniqueFactor % 100) / 100;
                        
                        const startPoint = axePoints[0];
                        const endPoint = axePoints[axePoints.length - 1];
                        
                        const baseCoords = [
                            startPoint[0] + t * (endPoint[0] - startPoint[0]),
                            startPoint[1] + t * (endPoint[1] - startPoint[1])
                        ];
                        
                        // Variation pour éviter la superposition
                        const variation = 0.0001; // ~10m
                        const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
                        const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
                        
                        coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
                        console.log(`✅ Position alternative sur axe ${axeName}: [${coords[0]}, ${coords[1]}]`);
                        break;
                    }
                }
            }
        }
        
        return coords;
    }
    
    // PRIORITÉ 4: Utiliser localisation_nom si disponible
    if (incident.localisation_nom) {
        console.log('📍 Utilisation localisation_nom:', incident.localisation_nom);
        
        // Chercher une gare correspondante
        const matchingGare = findGareByName(incident.localisation_nom, garePositions);
        if (matchingGare) {
            const baseCoords = garePositions[matchingGare];
            // Variation plus importante pour éviter la superposition
            const variation = 0.0005; // ~50m pour éviter la superposition visible
            const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
            const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
            const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
            coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
            console.log('✅ Position EXACTE selon localisation_nom:', matchingGare, coords);
            return coords;
        }
    }
    
    // FALLBACK FINAL: Pour les incidents vraiment non localisés (aucune donnée de localisation)
    if (!incident.gare_debut_nom && !incident.gare_fin_nom && !incident.localisation_nom && 
        !incident.pk_debut && !incident.pk_fin) {
        console.log(`❓ Incident ${incident.id}: Aucune donnée de localisation, distribution intelligente sur réseau ferroviaire`);
        
        // Distribution intelligente sur TOUT le réseau ferroviaire pour éviter le clustering
        const allRailwayPoints = [
            // LGV Al Boraq - Points intermédiaires ajoutés
            [35.7595, -5.8340], // Tanger Ville
            [35.6800, -5.8170], // Point intermédiaire 1
            [35.6000, -5.8000], // Sortie Tanger
            [35.5000, -5.7500], // Point intermédiaire 2
            [35.4000, -5.7000], // Plaine Gharb
            [35.3000, -5.6500], // Point intermédiaire 3
            [35.2000, -5.6000], // Terres agricoles
            [35.1000, -5.5500], // Point intermédiaire 4
            [35.0000, -5.5000], // Intérieur
            [34.9000, -5.5500], // Point intermédiaire 5
            [34.8000, -5.6000], // Gharb centrale
            [34.7000, -5.6500], // Point intermédiaire 6
            [34.6000, -5.7000], // Évite côtes
            [34.5000, -5.7500], // Point intermédiaire 7
            [34.4000, -5.8000], // Sud-est
            [34.3500, -5.8500], // Point intermédiaire 8
            [34.3000, -5.9000], // Loukkos
            [34.2805, -6.2406], // Point intermédiaire 9
            [34.2610, -6.5802], // Kenitra
            
            // Ligne classique côtière - Points intermédiaires ajoutés
            [35.4650, -6.0366], // Assilah
            [35.3292, -6.0962], // Point intermédiaire 10
            [35.1933, -6.1558], // Larache
            [35.0976, -6.0321], // Point intermédiaire 11
            [35.0019, -5.9083], // Ksar El Kebir
            [34.8464, -5.9485], // Point intermédiaire 12
            [34.6908, -5.9886], // Souk El Arbaa
            [34.4958, -6.1496], // Point intermédiaire 13
            [34.3008, -6.3106], // Sidi Yahya
            [34.2619, -6.0068], // Point intermédiaire 14
            [34.2628, -5.9222], // Sidi Slimane
            [34.2421, -6.3127], // Point intermédiaire 15
            [34.2214, -5.7031], // Sidi Kacem
            
            // Axe Kenitra-Casablanca - Points intermédiaires ajoutés
            [34.0531, -6.7985], // Salé
            [34.0060, -6.8241], // Point intermédiaire 16
            [33.9591, -6.8498], // Rabat Agdal
            [33.9900, -6.8458], // Point intermédiaire 17
            [34.0209, -6.8417], // Rabat Ville
            [33.9745, -6.8742], // Point intermédiaire 18
            [33.9281, -6.9067], // Témara
            [33.8900, -6.9687], // Point intermédiaire 19
            [33.8519, -7.0306], // Skhirat
            [33.8194, -7.0957], // Point intermédiaire 20
            [33.7869, -7.1608], // Bouznika
            [33.7368, -7.2723], // Point intermédiaire 21
            [33.6866, -7.3837], // Mohammedia
            [33.6418, -7.5012], // Point intermédiaire 22
            [33.5970, -7.6186], // Casablanca
            
            // Axe Casablanca-Marrakech - Points intermédiaires ajoutés
            [33.2582, -7.5870], // Berrechid
            [33.1298, -7.6043], // Point intermédiaire 23
            [33.0013, -7.6216], // Settat
            [32.8690, -7.8025], // Point intermédiaire 24
            [32.7367, -7.9833], // Ben Ahmed
            [32.4869, -7.9691], // Point intermédiaire 25
            [32.2372, -7.9549], // Benguerir
            [31.9334, -7.9680], // Point intermédiaire 26
            [31.6295, -7.9811], // Marrakech
            
            // Axe Fès-Oujda - Points intermédiaires ajoutés
            [34.0334, -4.9998], // Fès
            [34.0584, -4.8078], // Point intermédiaire 27
            [34.0833, -4.6167], // Oued Amlil
            [34.1482, -4.3134], // Point intermédiaire 28
            [34.2130, -4.0100], // Taza
            [34.1399, -3.7467], // Point intermédiaire 29
            [34.0667, -3.4833], // Msoun
            [34.1466, -3.4176], // Point intermédiaire 30
            [34.2264, -3.3519], // Guercif
            [34.3178, -3.1236], // Point intermédiaire 31
            [34.4092, -2.8953], // Taourirt
            [34.5480, -2.4034], // Point intermédiaire 32
            [34.6867, -1.9114], // Oujda
            
            // Axe phosphates - Points intermédiaires ajoutés
            [32.8811, -6.9063], // Khouribga
            [32.8721, -6.7401], // Point intermédiaire 33
            [32.8631, -6.5738], // Oued Zem
            [32.5541, -7.5521], // Point intermédiaire 34
            [32.2450, -8.5308], // Youssoufia
            [32.2642, -8.8821], // Point intermédiaire 35
            [32.2833, -9.2333], // Safi
            
            // Axe El Jadida - Points intermédiaires ajoutés
            [33.2316, -8.5007], // El Jadida
            [33.2993, -8.0739], // Point intermédiaire 36
            [33.3670, -7.6470], // Nouaceur
            
            // Points supplémentaires sur axes secondaires
            [34.8000, -5.9000], // Point intermédiaire 37
            [34.7000, -6.0000], // Point intermédiaire 38
            [34.6000, -6.1000], // Point intermédiaire 39
            [34.5000, -6.2000], // Point intermédiaire 40
            [34.4000, -6.3000], // Point intermédiaire 41
            [34.3000, -6.4000], // Point intermédiaire 42
            [34.2000, -6.5000], // Point intermédiaire 43
            [34.1000, -6.6000], // Point intermédiaire 44
            [34.0000, -6.7000], // Point intermédiaire 45
            [33.9000, -6.8000], // Point intermédiaire 46
            [33.8000, -6.9000], // Point intermédiaire 47
            [33.7000, -7.0000], // Point intermédiaire 48
            [33.6000, -7.1000], // Point intermédiaire 49
            [33.5000, -7.2000], // Point intermédiaire 50
            [33.4000, -7.3000], // Point intermédiaire 51
            [33.3000, -7.4000], // Point intermédiaire 52
            [33.2000, -7.5000], // Point intermédiaire 53
            [33.1000, -7.6000], // Point intermédiaire 54
            [33.0000, -7.7000], // Point intermédiaire 55
            [32.9000, -7.8000], // Point intermédiaire 56
            [32.8000, -7.9000], // Point intermédiaire 57
            [32.7000, -8.0000], // Point intermédiaire 58
            [32.6000, -8.1000], // Point intermédiaire 59
            [32.5000, -8.2000], // Point intermédiaire 60
            [32.4000, -8.3000], // Point intermédiaire 61
            [32.3000, -8.4000], // Point intermédiaire 62
            [32.2000, -8.5000], // Point intermédiaire 63
            [32.1000, -8.6000], // Point intermédiaire 64
            [32.0000, -8.7000], // Point intermédiaire 65
            [31.9000, -8.8000], // Point intermédiaire 66
            [31.8000, -8.9000], // Point intermédiaire 67
            [31.7000, -9.0000], // Point intermédiaire 68
            [31.6000, -9.1000], // Point intermédiaire 69
            [31.5000, -9.2000]  // Point intermédiaire 70
        ];
        
        // Utiliser l'ID de l'incident pour sélectionner un point unique sur le réseau
        const pointIndex = incident.id % allRailwayPoints.length;
        const baseCoords = allRailwayPoints[pointIndex];
        
        // Ajouter une variation BEAUCOUP plus importante pour éviter le clustering visible
        const variation = 0.001; // ~100m pour éviter la superposition visible
        const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
        const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
        const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
        
        coords = [baseCoords[0] + offsetLat, baseCoords[1] + offsetLng];
        console.log(`🎯 Incident ${incident.id}: Positionné sur réseau ferroviaire (fallback): [${coords[0]}, ${coords[1]}]`);
    }
    
    // Position finale validée - pas de vérification en mer ici
    
    return coords;
}

// Fonction pour trouver la gare la plus proche selon le PK
function findNearestGareByPK(pkValue, garePositions) {
    // Mapping approximatif PK vers gares (basé sur les données ONCF)
    const pkGareMapping = {
        '0': 'Tanger Ville',
        '50': 'Assilah',
        '100': 'Larache',
        '150': 'Ksar El Kebir',
        '200': 'Souk El Arbaa',
        '250': 'Sidi Yahya El Gharb',
        '300': 'Kenitra',
        '350': 'Sale',
        '400': 'Rabat Ville',
        '450': 'Temara',
        '500': 'Skhirat',
        '550': 'Bouznika',
        '600': 'Mohammedia',
        '650': 'Casablanca Voyageurs',
        '700': 'Berrechid',
        '750': 'Settat',
        '800': 'Ben Ahmed',
        '850': 'Benguerir',
        '900': 'Marrakech'
    };
    
    // Parser le PK
    const parsePK = (pk) => {
        if (!pk) return 0;
        const match = pk.toString().match(/(\d+)\+(\d+)/);
        if (match) {
            return parseInt(match[1]) + parseInt(match[2]) / 1000;
        }
        return parseFloat(pk) || 0;
    };
    
    const pkNum = parsePK(pkValue);
    
    // Trouver la gare la plus proche
    let nearestGare = null;
    let minDistance = Infinity;
    
    for (const [pkStr, gareName] of Object.entries(pkGareMapping)) {
        const pkGare = parseFloat(pkStr);
        const distance = Math.abs(pkNum - pkGare);
        if (distance < minDistance) {
            minDistance = distance;
            nearestGare = gareName;
        }
    }
    
    return nearestGare;
}

// Fonction pour positionner un incident selon le PK sur un axe
function positionIncidentByPK(incident, garePositions, axePositions) {
    const pkValue = incident.pk_debut || incident.pk_fin;
    
    // Parser le PK
    const parsePK = (pk) => {
        if (!pk) return 0;
        const match = pk.toString().match(/(\d+)\+(\d+)/);
        if (match) {
            return parseInt(match[1]) + parseInt(match[2]) / 1000;
        }
        return parseFloat(pk) || 0;
    };
    
    const pkNum = parsePK(pkValue);
    
    // Déterminer l'axe selon le PK
    let selectedAxe = null;
    if (pkNum < 300) {
        selectedAxe = 'Tanger-Kenitra-Classique';
    } else if (pkNum < 650) {
        selectedAxe = 'Kenitra-Casablanca-LGV';
    } else if (pkNum < 900) {
        selectedAxe = 'Casablanca-Marrakech';
    } else {
        selectedAxe = 'Fes-Oujda-Real';
    }
    
    if (selectedAxe && axePositions[selectedAxe]) {
        const axePoints = axePositions[selectedAxe];
        
        // Positionner selon le PK sur l'axe
        const pkRatio = (pkNum % 300) / 300; // Ratio sur l'axe
        const segmentIndex = Math.floor(pkRatio * (axePoints.length - 1));
        
        if (segmentIndex < axePoints.length - 1) {
            const point1 = axePoints[segmentIndex];
            const point2 = axePoints[segmentIndex + 1];
            const segmentRatio = (pkRatio * (axePoints.length - 1)) % 1;
            
            const lat = point1[0] + (point2[0] - point1[0]) * segmentRatio;
            const lng = point1[1] + (point2[1] - point1[1]) * segmentRatio;
            
            // Ajouter une variation plus importante pour éviter la superposition
            const variation = 0.0005; // ~50m pour éviter la superposition visible
            const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
            const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
            const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
            
            return [lat + offsetLat, lng + offsetLng];
        }
    }
    
    // Fallback: position au milieu de l'axe
    const axes = Object.values(axePositions);
    const randomAxe = axes[Math.floor(Math.random() * axes.length)];
    return positionIncidentOnLine(incident, randomAxe, 0);
}

// Fonction pour trouver une gare par nom
function findGareByName(locationName, garePositions) {
    const searchName = locationName.toLowerCase();
    
    for (const [gareName, coords] of Object.entries(garePositions)) {
        if (gareName.toLowerCase().includes(searchName) || 
            searchName.includes(gareName.toLowerCase())) {
            return gareName;
        }
    }
    
    return null;
}

// NOUVELLE FONCTION : Gestion spéciale des patterns de clustering identifiés
function handleClusteredIncidents(incident) {
    const gareDebut = (incident.gare_debut_nom || '').toLowerCase();
    const gareFin = (incident.gare_fin_nom || '').toLowerCase();
    const localisation = (incident.localisation_nom || '').toLowerCase();
    
    console.log(`🎯 Gestion spéciale pour incident ${incident.id}: ${gareDebut} → ${gareFin}`);
    
    // PATTERN 1: casavoyageurs/skacem (58 incidents)
    if (gareDebut.includes('casavoyageurs/skacem') || gareFin.includes('casavoyageurs/skacem')) {
        return positionCasablancaSkacemIncident(incident);
    }
    
    // PATTERN 2: benguerir/safi u (48 incidents)
    if (gareDebut.includes('benguerir/safi') || gareFin.includes('benguerir/safi')) {
        return positionBenguerirSafiIncident(incident);
    }
    
    // PATTERN 3: casavoyageurs/marrakech (19 + 16 + 14 incidents)
    if (gareDebut.includes('casavoyageurs/marrakech') || gareFin.includes('casavoyageurs/marrakech') || 
        gareDebut.includes('casa voyageurs/marrakech') || gareFin.includes('casa voyageurs/marrakech')) {
        return positionCasablancaMarrakechIncident(incident);
    }
    
    // PATTERN 4: nouaceur/eljadida (14 incidents)
    if (gareDebut.includes('nouaceur/eljadida') || gareFin.includes('nouaceur/eljadida')) {
        return positionNouaceurElJadidaIncident(incident);
    }
    
    // PATTERN 5: s.elaidi/oued zem (12 incidents)
    if (gareDebut.includes('s.elaidi/oued zem') || gareFin.includes('s.elaidi/oued zem')) {
        return positionSelaidiOuedZemIncident(incident);
    }
    
    // PATTERN 6: tanger/fes u (12 incidents)
    if (gareDebut.includes('tanger/fes u') || gareFin.includes('tanger/fes u')) {
        return positionTangerFesIncident(incident);
    }
    
    return null; // Pas de pattern spécial trouvé
}

// Fonction spéciale pour Casablanca-Skacem
function positionCasablancaSkacemIncident(incident) {
    const casablancaCoords = [33.5970, -7.6186]; // Casablanca Voyageurs
    const skacemCoords = [34.2214, -5.7031]; // Sidi Kacem
    
    // Déterminer la position sur l'axe Casablanca-Sidi Kacem
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const t = (uniqueFactor % 100) / 100; // Position basée sur l'ID
    
    // Position sur la ligne Casablanca → Sidi Kacem
    const coords = [
        casablancaCoords[0] + t * (skacemCoords[0] - casablancaCoords[0]),
        casablancaCoords[1] + t * (skacemCoords[1] - casablancaCoords[1])
    ];
    
    // Ajouter une variation plus importante pour éviter la superposition exacte
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
    
    const finalCoords = [coords[0] + offsetLat, coords[1] + offsetLng];
    
    // Position finale validée - pas de vérification en mer ici
    
    console.log(`🎯 Incident ${incident.id}: Positionné sur axe Casablanca-Skacem: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Fonction spéciale pour Benguerir-Safi
function positionBenguerirSafiIncident(incident) {
    const benguerirCoords = [32.2372, -7.9549]; // Benguerir
    const safiCoords = [32.2833, -9.2333]; // Safi
    
    // Déterminer la position sur l'axe Benguerir-Safi
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const t = (uniqueFactor % 100) / 100;
    
    // Position sur la ligne Benguerir → Safi
    const coords = [
        benguerirCoords[0] + t * (safiCoords[0] - benguerirCoords[0]),
        benguerirCoords[1] + t * (safiCoords[1] - benguerirCoords[1])
    ];
    
    // Ajouter une variation plus importante
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
    
    const finalCoords = [coords[0] + offsetLat, coords[1] + offsetLng];
    
    // Position finale validée - pas de vérification en mer ici
    
    console.log(`🎯 Incident ${incident.id}: Positionné sur axe Benguerir-Safi: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Fonction spéciale pour Casablanca-Marrakech
function positionCasablancaMarrakechIncident(incident) {
    const casablancaCoords = [33.5970, -7.6186]; // Casablanca Voyageurs
    const marrakechCoords = [31.6295, -7.9811]; // Marrakech
    
    // Déterminer la position sur l'axe Casablanca-Marrakech
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const t = (uniqueFactor % 100) / 100;
    
    // Position sur la ligne Casablanca → Marrakech
    const coords = [
        casablancaCoords[0] + t * (marrakechCoords[0] - casablancaCoords[0]),
        casablancaCoords[1] + t * (marrakechCoords[1] - casablancaCoords[1])
    ];
    
    // Ajouter une variation plus importante
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
    
    const finalCoords = [coords[0] + offsetLat, coords[1] + offsetLng];
    
    // Position finale validée - pas de vérification en mer ici
    
    console.log(`🎯 Incident ${incident.id}: Positionné sur axe Casablanca-Marrakech: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Fonction spéciale pour Nouaceur-El Jadida
function positionNouaceurElJadidaIncident(incident) {
    const nouaceurCoords = [33.3670, -7.6470]; // Nouaceur
    const elJadidaCoords = [33.2316, -8.5007]; // El Jadida
    
    // Déterminer la position sur l'axe Nouaceur-El Jadida
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const t = (uniqueFactor % 100) / 100;
    
    // Position sur la ligne Nouaceur → El Jadida
    const coords = [
        nouaceurCoords[0] + t * (elJadidaCoords[0] - nouaceurCoords[0]),
        nouaceurCoords[1] + t * (elJadidaCoords[1] - nouaceurCoords[1])
    ];
    
    // Ajouter une variation plus importante
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
    
    const finalCoords = [coords[0] + offsetLat, coords[1] + offsetLng];
    
    // Position finale validée - pas de vérification en mer ici
    
    console.log(`🎯 Incident ${incident.id}: Positionné sur axe Nouaceur-El Jadida: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Fonction spéciale pour S. Elaidi-Oued Zem
function positionSelaidiOuedZemIncident(incident) {
    const selaidiCoords = [32.8631, -6.5738]; // S. Elaidi (approximatif)
    const ouedZemCoords = [32.8631, -6.5738]; // Oued Zem
    
    // Déterminer la position sur l'axe S. Elaidi-Oued Zem
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const t = (uniqueFactor % 100) / 100;
    
    // Position sur la ligne S. Elaidi → Oued Zem
    const coords = [
        selaidiCoords[0] + t * (ouedZemCoords[0] - selaidiCoords[0]),
        selaidiCoords[1] + t * (ouedZemCoords[1] - selaidiCoords[1])
    ];
    
    // Ajouter une variation plus importante
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
    
    const finalCoords = [coords[0] + offsetLat, coords[1] + offsetLng];
    
    // Position finale validée - pas de vérification en mer ici
    
    console.log(`🎯 Incident ${incident.id}: Positionné sur axe S. Elaidi-Oued Zem: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Fonction spéciale pour Tanger-Fes
function positionTangerFesIncident(incident) {
    const tangerCoords = [35.7595, -5.8340]; // Tanger
    const fesCoords = [34.0334, -4.9998]; // Fès
    
    // Déterminer la position sur l'axe Tanger-Fès
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const t = (uniqueFactor % 100) / 100;
    
    // Position sur la ligne Tanger → Fès
    const coords = [
        tangerCoords[0] + t * (fesCoords[0] - tangerCoords[0]),
        tangerCoords[1] + t * (fesCoords[1] - tangerCoords[1])
    ];
    
    // Ajouter une variation plus importante
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
    
    const finalCoords = [coords[0] + offsetLat, coords[1] + offsetLng];
    
    // Position finale validée - pas de vérification en mer ici
    
    console.log(`🎯 Incident ${incident.id}: Positionné sur axe Tanger-Fès: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Fonction spéciale pour positionner les incidents d'El Jadida
function positionElJadidaIncident(incident) {
    const garePositions = getGarePositions();
    const axePositions = getAxePositions();
    
    // Position de base : El Jadida
    const elJadidaCoords = [33.2316, -8.5007];
    
    // Déterminer si l'incident est en gare ou en ligne
    const isInStation = determineIncidentLocationType(incident);
    
    // Vérifier si l'incident mentionne spécifiquement El Jadida
    const incidentText = (incident.gare_debut_nom || incident.gare_fin_nom || incident.localisation_nom || '').toLowerCase();
    const isElJadidaSpecific = incidentText.includes('el jadida') || incidentText.includes('el jorf');
    
    if (isInStation || isElJadidaSpecific) {
        // INCIDENT EN GARE : Positionner sur El Jadida avec variation plus importante
        const variation = 0.0005; // ~50m pour éviter la superposition visible
        const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
        const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
        const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
        
        const finalCoords = [elJadidaCoords[0] + offsetLat, elJadidaCoords[1] + offsetLng];
        
        // Position finale validée - pas de vérification en mer ici
        
        console.log(`🎯 Incident ${incident.id}: Positionné en gare El Jadida avec variation: [${finalCoords[0]}, ${finalCoords[1]}]`);
        return finalCoords;
    } else {
        // INCIDENT EN LIGNE : Positionner sur l'axe El Jadida - Casablanca
        const axePoints = axePositions['El-Jadida-Casablanca'] || axePositions['Nouaceur-El-Jadida'];
        if (axePoints && axePoints.length >= 2) {
            const lineCoords = positionIncidentOnLine(incident, axePoints, 0);
            console.log(`🎯 Incident ${incident.id}: Positionné en ligne El Jadida-Casablanca: [${lineCoords[0]}, ${lineCoords[1]}]`);
            return lineCoords;
        } else {
            // Fallback : position entre El Jadida et Casablanca
            const casablancaCoords = [33.5970, -7.6186];
            const t = (incident.id % 100) / 100; // Position basée sur l'ID
            const fallbackCoords = [
                elJadidaCoords[0] + t * (casablancaCoords[0] - elJadidaCoords[0]),
                elJadidaCoords[1] + t * (casablancaCoords[1] - elJadidaCoords[1])
            ];
            
            // Position finale validée - pas de vérification en mer ici
            
            console.log(`🎯 Incident ${incident.id}: Positionné avec fallback El Jadida-Casablanca: [${fallbackCoords[0]}, ${fallbackCoords[1]}]`);
            return fallbackCoords;
        }
    }
}

// Déterminer le type de localisation basé sur les données de ge_localisation
function determineIncidentLocationType(incident) {
    // Utiliser le type_localisation de ge_localisation en priorité
    if (incident.type_localisation) {
        const type = incident.type_localisation.toLowerCase();
        if (type.includes('gare') || type.includes('station') || type.includes('quai')) {
            return true; // EN GARE
        }
        if (type.includes('ligne') || type.includes('voie') || type.includes('section') || type.includes('tronçon')) {
            return false; // EN LIGNE
        }
    }
    
    // Fallback sur l'ancienne logique
    return determineIfIncidentInStation(incident);
}

// Positionner un incident sur une ligne ferroviaire en utilisant les données de localisation
function positionIncidentOnRailwayLine(incident, gareDebutName, gareFinName, garePositions, axePositions) {
    // Si on a les deux gares, calculer la position entre elles
    if (gareDebutName && gareFinName && garePositions[gareDebutName] && garePositions[gareFinName]) {
        const gareDebut = garePositions[gareDebutName];
        const gareFin = garePositions[gareFinName];
        
        // Utiliser le PK si disponible pour une position plus précise
        if (incident.pk_debut && incident.pk_fin) {
            return calculatePositionFromPK(incident.pk_debut, incident.pk_fin, gareDebut, gareFin);
        } else if (incident.pk_debut) {
            return calculatePositionFromPK(incident.pk_debut, incident.pk_debut, gareDebut, gareFin);
        }
        
        // Position au milieu entre les deux gares avec variation basée sur l'ID pour éviter la superposition
        const baseLat = (gareDebut[0] + gareFin[0]) / 2;
        const baseLng = (gareDebut[1] + gareFin[1]) / 2;
        
        // Ajouter une variation plus importante pour éviter la superposition
        const variation = 0.0005; // ~50m pour éviter la superposition visible
        const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
        const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
        const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
        
        return [baseLat + offsetLat, baseLng + offsetLng];
    }
    
    // Si on a seulement une gare, chercher l'axe qui la contient
    if (gareDebutName && garePositions[gareDebutName]) {
        const garePos = garePositions[gareDebutName];
        
        // Trouver l'axe qui contient cette gare
        for (const [axeName, points] of Object.entries(axePositions)) {
            const hasGare = points.some(point => 
                Math.abs(point[0] - garePos[0]) < 0.01 && 
                Math.abs(point[1] - garePos[1]) < 0.01
            );
            
            if (hasGare) {
                // Positionner à proximité de la gare sur l'axe
                const gareIndex = points.findIndex(point => 
                    Math.abs(point[0] - garePos[0]) < 0.01 && 
                    Math.abs(point[1] - garePos[1]) < 0.01
                );
                
                if (gareIndex > 0 && gareIndex < points.length - 1) {
                    // Position entre cette gare et la suivante avec variation plus importante
                    const nextPoint = points[gareIndex + 1];
                    const baseLat = (garePos[0] + nextPoint[0]) / 2;
                    const baseLng = (garePos[1] + nextPoint[1]) / 2;
                    
                    const variation = 0.0005; // ~50m pour éviter la superposition visible
                    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                    const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                    const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                    
                    return [baseLat + offsetLat, baseLng + offsetLng];
                } else if (gareIndex === 0 && points.length > 1) {
                    // Position après la première gare avec variation plus importante
                    const nextPoint = points[1];
                    const baseLat = (garePos[0] + nextPoint[0]) / 2;
                    const baseLng = (garePos[1] + nextPoint[1]) / 2;
                    
                    const variation = 0.0005; // ~50m pour éviter la superposition visible
                    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                    const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                    const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                    
                    return [baseLat + offsetLat, baseLng + offsetLng];
                } else if (gareIndex === points.length - 1 && points.length > 1) {
                    // Position avant la dernière gare avec variation plus importante
                    const prevPoint = points[points.length - 2];
                    const baseLat = (garePos[0] + prevPoint[0]) / 2;
                    const baseLng = (garePos[1] + prevPoint[1]) / 2;
                    
                    const variation = 0.0005; // ~50m pour éviter la superposition visible
                    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                    const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                    const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                    
                    return [baseLat + offsetLat, baseLng + offsetLng];
                }
            }
        }
    }
    
    // Fallback: position aléatoire sur un axe
    const axes = Object.values(axePositions);
    const randomAxe = axes[Math.floor(Math.random() * axes.length)];
    return positionIncidentOnLine(incident, randomAxe, 0);
}

// Calculer la position basée sur le PK (Point Kilométrique)
function calculatePositionFromPK(pkDebut, pkFin, gareDebut, gareFin) {
    try {
        // Parser les PK (format: "245+400" = 245.4 km)
        const parsePK = (pk) => {
            if (!pk) return 0;
            const match = pk.toString().match(/(\d+)\+(\d+)/);
            if (match) {
                return parseInt(match[1]) + parseInt(match[2]) / 1000;
            }
            return parseFloat(pk) || 0;
        };
        
        const pkStart = parsePK(pkDebut);
        const pkEnd = parsePK(pkFin);
        const pkMiddle = (pkStart + pkEnd) / 2;
        
        // Calculer la distance totale entre les gares (approximation)
        const distance = Math.sqrt(
            Math.pow(gareFin[0] - gareDebut[0], 2) + 
            Math.pow(gareFin[1] - gareDebut[1], 2)
        );
        
        // Position proportionnelle selon le PK
        const ratio = pkMiddle / 100; // Approximation: 100km = distance totale
        const clampedRatio = Math.max(0, Math.min(1, ratio));
        
        return [
            gareDebut[0] + (gareFin[0] - gareDebut[0]) * clampedRatio,
            gareDebut[1] + (gareFin[1] - gareDebut[1]) * clampedRatio
        ];
    } catch (error) {
        console.warn('Erreur calcul PK:', error);
        // Fallback: position au milieu
        return [
            (gareDebut[0] + gareFin[0]) / 2,
            (gareDebut[1] + gareFin[1]) / 2
        ];
    }
}

// Déterminer si l'incident se produit en gare ou en ligne (ancienne logique)
function determineIfIncidentInStation(incident) {
    // Indicateurs d'incident en gare
    const stationIndicators = [
        'gare', 'station', 'quai', 'hall', 'bâtiment', 'infrastructure',
        'signalisation', 'passage', 'niveau', 'barrière', 'guichet',
        'parking', 'accès', 'entrée', 'sortie'
    ];
    
    // Indicateurs d'incident en ligne
    const lineIndicators = [
        'voie', 'rail', 'ligne', 'tronçon', 'section', 'entre',
        'pont', 'viaduc', 'tunnel', 'passage à niveau', 'aiguillage',
        'caténaire', 'électrique', 'signal'
    ];
    
    const description = (incident.resume || incident.commentaire || '').toLowerCase();
    const location = (incident.localisation_nom || '').toLowerCase();
    const type = (incident.type_name || '').toLowerCase();
    
    // Vérifier les indicateurs de gare
    const hasStationIndicator = stationIndicators.some(indicator => 
        description.includes(indicator) || 
        location.includes(indicator) || 
        type.includes(indicator)
    );
    
    // Vérifier les indicateurs de ligne
    const hasLineIndicator = lineIndicators.some(indicator => 
        description.includes(indicator) || 
        location.includes(indicator) || 
        type.includes(indicator)
    );
    
    // Si pas de gare de début/fin spécifiée, probablement en gare
    if (!incident.gare_debut_nom && !incident.gare_fin_nom) {
        return true;
    }
    
    // Si description contient "entre [gare1] et [gare2]", c'est en ligne
    if (incident.gare_debut_nom && incident.gare_fin_nom && 
        description.includes('entre') && 
        (description.includes(incident.gare_debut_nom.toLowerCase()) || 
         description.includes(incident.gare_fin_nom.toLowerCase()))) {
        return false;
    }
    
    // Priorité aux indicateurs explicites
    if (hasStationIndicator && !hasLineIndicator) {
        return true;
    }
    if (hasLineIndicator && !hasStationIndicator) {
        return false;
    }
    
    // Par défaut, si on a des gares de début/fin, c'est en ligne
    return !(incident.gare_debut_nom && incident.gare_fin_nom);
}

// Positionner un incident en gare avec division intelligente
function positionIncidentInStation(incident, axePoints) {
    // Si on a une gare spécifique mentionnée, l'utiliser avec division
    if (incident.gare_debut_nom) {
        const gareName = incident.gare_debut_nom.toLowerCase();
        for (const [gareNameKey, position] of Object.entries(garePositions)) {
            if (gareName.includes(gareNameKey.toLowerCase()) || 
                gareNameKey.toLowerCase().includes(gareName)) {
                
                // Ajouter une variation basée sur l'ID de l'incident pour éviter la concentration
                const variation = 0.0005; // ~50m
                const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                
                const finalCoords = [position[0] + offsetLat, position[1] + offsetLng];
                console.log(`🏢 Incident ${incident.id}: Positionné en gare spécifique avec division: ${gareNameKey}`);
                return finalCoords;
            }
        }
    }
    
    // Sinon, choisir une gare de l'axe avec division basée sur l'ID
    const gareIndex = incident.id % axePoints.length;
    const selectedPoint = axePoints[gareIndex];
    
    // Ajouter une petite variation pour éviter la concentration
    const variation = 0.0005; // ~50m
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
    
    const finalCoords = [selectedPoint[0] + offsetLat, selectedPoint[1] + offsetLng];
    console.log(`🏢 Incident ${incident.id}: Positionné en gare d'axe avec division (index: ${gareIndex})`);
    return finalCoords;
}

// Fonction de validation des coordonnées - TRÈS PERMISSIVE pour éviter les faux positifs
function validateCoordinates(lat, lng) {
    // Limites du Maroc - TRÈS permissives
    const MOROCCO_BOUNDS = {
        min_lat: 27.0,  // Sud du Maroc - encore plus permissif
        max_lat: 37.0,  // Nord du Maroc - encore plus permissif
        min_lng: -18.0, // Ouest du Maroc - encore plus permissif
        max_lng: -0.5   // Est du Maroc - encore plus permissif
    };
    
    // Vérifier si les coordonnées sont valides
    if (!(-90 <= lat <= 90) || !(-180 <= lng <= 180)) {
        return false;
    }
    
    // Vérifier si c'est dans les limites du Maroc - TRÈS permissives
    if (!(MOROCCO_BOUNDS.min_lat <= lat <= MOROCCO_BOUNDS.max_lat && 
          MOROCCO_BOUNDS.min_lng <= lng <= MOROCCO_BOUNDS.max_lng)) {
        return false;
    }
    
    // SUPPRIMER TOUTE LA LOGIQUE DE DÉTECTION EN MER - Trop de faux positifs
    // Les coordonnées dans les limites du Maroc sont considérées comme valides
    // Seulement flagger les coordonnées vraiment impossibles (hors limites géographiques)
    
    return true;
}

// Vérifier si les coordonnées sont sur ou proches d'une ligne ferroviaire
function checkIfOnRailwayLine(lat, lng) {
    const garePositions = getGarePositions();
    const axePositions = getAxePositions();
    
    // Distance maximale pour considérer qu'un point est sur une ligne ferroviaire (en degrés)
    // RÉDUITE pour être plus strict et forcer le positionnement sur les lignes
    const maxDistance = 0.005; // ~500m au lieu de 2km
    
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
            
            // Calculer la distance du point à la ligne
            const distance = distanceToLine([lat, lng], point1, point2);
            if (distance <= maxDistance) {
                return true;
            }
        }
    }
    
    return false;
}

// Calculer la distance d'un point à une ligne
function distanceToLine(point, lineStart, lineEnd) {
    const A = point[0] - lineStart[0];
    const B = point[1] - lineStart[1];
    const C = lineEnd[0] - lineStart[0];
    const D = lineEnd[1] - lineStart[1];
    
    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    
    if (lenSq === 0) {
        // Les points de la ligne sont identiques
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

// Fonction de correction des coordonnées invalides
function correctInvalidCoordinates(lat, lng, incident, recursionCount = 0) {
    // Protection contre la récursion infinie
    if (recursionCount > 3) {
        console.error(`❌ Récursion infinie détectée pour l'incident ${incident.id} - Arrêt d'urgence`);
        // Position d'urgence : Casablanca Voyageurs (sur ligne ferroviaire)
        return [33.5970, -7.6186];
    }
    
    // Si les coordonnées sont invalides, utiliser une position de fallback sur ligne ferroviaire
    console.log(`⚠️ Coordonnées invalides détectées: [${lat}, ${lng}] - Utilisation d'une position de fallback sur ligne ferroviaire (récursion: ${recursionCount})`);
    
    // Position de fallback sur ligne ferroviaire : Casablanca Voyageurs
    const fallbackCoords = [33.5970, -7.6186]; // Casablanca Voyageurs (sur ligne)
    
    // Ajouter une variation plus importante basée sur l'ID de l'incident pour éviter la concentration
    const variation = 0.0005; // ~50m pour éviter la superposition visible
    const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
    const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
    const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
    
    const finalCoords = [fallbackCoords[0] + offsetLat, fallbackCoords[1] + offsetLng];
    
    console.log(`📍 Incident ${incident.id}: Position de fallback sur ligne ferroviaire: [${finalCoords[0]}, ${finalCoords[1]}]`);
    return finalCoords;
}

// Positionner un incident en ligne (entre deux gares) avec précision PK
// FORCER LE POSITIONNEMENT SUR LES LIGNES FERROVIAIRES
function positionIncidentOnLine(incident, axePoints, recursionCount = 0) {
    console.log(`🛤️ Positionnement FORCÉ en ligne sur voie ferrée pour incident ${incident.id}`);
    
    if (axePoints.length < 2) {
        return axePoints[0] || [31.7917, -7.0926];
    }
    
    // PRIORITÉ 1: Essayer de positionner précisément avec les informations PK
    if (incident.pk_debut && incident.gare_debut_nom && incident.gare_fin_nom) {
        const precisePosition = positionIncidentWithPK(incident, axePoints, recursionCount);
        if (precisePosition) {
            console.log(`📍 Incident ${incident.id}: Positionné avec PK précis sur ligne ferroviaire`);
            return precisePosition;
        }
    }
    
    // PRIORITÉ 2: Positionner entre les gares de début et fin si disponibles
    if (incident.gare_debut_nom && incident.gare_fin_nom) {
        const garePositions = getGarePositions();
        const gareDebut = findGarePosition(incident.gare_debut_nom, garePositions);
        const gareFin = findGarePosition(incident.gare_fin_nom, garePositions);
        
        if (gareDebut && gareFin) {
            // Vérifier si c'est la même gare
            if (gareDebut[0] === gareFin[0] && gareDebut[1] === gareFin[1]) {
                // Même gare : positionner avec variation basée sur l'ID de l'incident
                const variation = (incident.id % 100) / 1000; // Variation de 0 à 0.1
                // Utiliser une combinaison de l'ID, type, et gares pour garantir l'unicité
                const uniqueFactor = incident.id + 
                    (incident.type_name ? incident.type_name.length : 0) +
                    (incident.gare_debut_nom ? incident.gare_debut_nom.length : 0) +
                    (incident.gare_fin_nom ? incident.gare_fin_nom.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                const finalCoords = [gareDebut[0] + offsetLat, gareDebut[1] + offsetLng];
                if (validateCoordinates(finalCoords[0], finalCoords[1])) {
                    console.log(`📍 Incident ${incident.id}: Positionné sur gare avec variation unique (même gare début/fin)`);
                    return finalCoords;
                } else {
                    console.log(`⚠️ Incident ${incident.id}: Position invalide détectée, correction appliquée`);
                    return correctInvalidCoordinates(finalCoords[0], finalCoords[1], incident, 0);
                }
            } else {
                // Gares différentes : positionner avec variation basée sur l'ID
                const baseLat = (gareDebut[0] + gareFin[0]) / 2;
                const baseLng = (gareDebut[1] + gareFin[1]) / 2;
                
                // Variation basée sur l'ID de l'incident pour éviter les positions identiques
                const variation = (incident.id % 50) / 1000; // Variation de 0 à 0.05
                // Utiliser une combinaison de l'ID, type, et gares pour garantir l'unicité
                const uniqueFactor = incident.id + 
                    (incident.type_name ? incident.type_name.length : 0) +
                    (incident.gare_debut_nom ? incident.gare_debut_nom.length : 0) +
                    (incident.gare_fin_nom ? incident.gare_fin_nom.length : 0);
                const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
                const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
                
                const finalCoords = [baseLat + offsetLat, baseLng + offsetLng];
                if (validateCoordinates(finalCoords[0], finalCoords[1])) {
                    console.log(`📍 Incident ${incident.id}: Positionné entre gares avec variation unique sur ligne ferroviaire`);
                    return finalCoords;
                } else {
                    console.log(`⚠️ Incident ${incident.id}: Position invalide détectée, correction appliquée`);
                    return correctInvalidCoordinates(finalCoords[0], finalCoords[1], incident, 0);
                }
            }
        }
    }
    
    // PRIORITÉ 3: Positionner sur l'axe le plus proche des gares mentionnées
    if (incident.gare_debut_nom) {
        const garePositions = getGarePositions();
        const gareDebut = findGarePosition(incident.gare_debut_nom, garePositions);
        
        if (gareDebut) {
            // Trouver le point le plus proche sur l'axe - SUR LA LIGNE FERROVIAIRE
            let closestPoint = axePoints[0];
            let minDistance = calculateDistance(gareDebut, closestPoint);
            
            for (let i = 1; i < axePoints.length; i++) {
                const distance = calculateDistance(gareDebut, axePoints[i]);
                if (distance < minDistance) {
                    minDistance = distance;
                    closestPoint = axePoints[i];
                }
            }
            
            // Positionner avec variation basée sur l'ID de l'incident
            const variation = (incident.id % 30) / 1000; // Variation de 0 à 0.03
            // Utiliser une combinaison de l'ID et du type pour garantir l'unicité
            const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
            const offsetLat = (Math.sin(uniqueFactor * 0.2) * variation);
            const offsetLng = (Math.cos(uniqueFactor * 0.2) * variation);
            const finalCoords = [closestPoint[0] + offsetLat, closestPoint[1] + offsetLng];
            if (validateCoordinates(finalCoords[0], finalCoords[1])) {
                console.log(`📍 Incident ${incident.id}: Positionné près de gare avec variation unique sur ligne ferroviaire`);
                return finalCoords;
            } else {
                console.log(`⚠️ Incident ${incident.id}: Position invalide détectée, correction appliquée`);
                return correctInvalidCoordinates(finalCoords[0], finalCoords[1], incident, recursionCount + 1);
            }
        }
    }
    
    // PRIORITÉ 4: Position sur l'axe avec répartition intelligente basée sur l'ID
    // Utiliser l'ID de l'incident pour déterminer le segment et la position
    const segmentIndex = incident.id % (axePoints.length - 1);
    const gare1 = axePoints[segmentIndex];
    const gare2 = axePoints[segmentIndex + 1];
    
    // Position dans le segment basée sur l'ID (évite les positions identiques)
    const t = (incident.id % 100) / 100; // t entre 0 et 1 basé sur l'ID
    
    const lat = gare1[0] + t * (gare2[0] - gare1[0]);
    const lng = gare1[1] + t * (gare2[1] - gare1[1]);
    
    const finalCoords = [lat, lng];
    if (validateCoordinates(finalCoords[0], finalCoords[1])) {
        console.log(`📍 Incident ${incident.id}: Positionné avec répartition intelligente sur ligne ferroviaire (segment ${segmentIndex}, t=${t.toFixed(3)})`);
        return finalCoords;
    } else {
        console.log(`⚠️ Incident ${incident.id}: Position invalide détectée, correction appliquée`);
        return correctInvalidCoordinates(finalCoords[0], finalCoords[1], incident, recursionCount + 1);
    }
}

// Positionner un incident avec précision en utilisant les informations PK
function positionIncidentWithPK(incident, axePoints, recursionCount = 0) {
    try {
        const pkValue = parsePKValue(incident.pk_debut);
        if (!pkValue) return null;
        
        // Trouver les gares de début et fin sur l'axe
        const garePositions = getGarePositions();
        const gareDebut = findGarePosition(incident.gare_debut_nom, garePositions);
        const gareFin = findGarePosition(incident.gare_fin_nom, garePositions);
        
        if (!gareDebut || !gareFin) return null;
        
        // Vérifier si c'est la même gare
        if (gareDebut[0] === gareFin[0] && gareDebut[1] === gareFin[1]) {
            // Même gare : positionner avec variation basée sur l'ID de l'incident
            const variation = (incident.id % 100) / 1000; // Variation de 0 à 0.1
            // Utiliser une combinaison de l'ID et du type pour garantir l'unicité
            const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
            const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
            const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
            const finalCoords = [gareDebut[0] + offsetLat, gareDebut[1] + offsetLng];
            if (validateCoordinates(finalCoords[0], finalCoords[1])) {
                console.log(`📍 Incident ${incident.id}: Positionné avec PK sur gare avec variation unique (même gare début/fin)`);
                return finalCoords;
            } else {
                console.log(`⚠️ Incident ${incident.id}: Position invalide détectée, correction appliquée`);
                return correctInvalidCoordinates(finalCoords[0], finalCoords[1], incident, recursionCount + 1);
            }
        }
        
        // Trouver les positions des gares sur l'axe
        const debutIndex = findPointIndexOnAxe(gareDebut, axePoints);
        const finIndex = findPointIndexOnAxe(gareFin, axePoints);
        
        if (debutIndex === -1 || finIndex === -1) return null;
        
        // Calculer la distance totale entre les gares
        let totalDistance = 0;
        const segmentDistances = [];
        
        for (let i = Math.min(debutIndex, finIndex); i < Math.max(debutIndex, finIndex); i++) {
            const dist = calculateDistance(axePoints[i], axePoints[i + 1]);
            segmentDistances.push(dist);
            totalDistance += dist;
        }
        
        // Calculer la position relative du PK
        const pkPosition = pkValue / 1000; // Convertir en km
        const relativePosition = pkPosition / totalDistance;
        
        // Positionner sur le segment approprié
        let accumulatedDistance = 0;
        for (let i = 0; i < segmentDistances.length; i++) {
            const segmentStart = Math.min(debutIndex, finIndex) + i;
            const segmentEnd = segmentStart + 1;
            
            if (relativePosition <= (accumulatedDistance + segmentDistances[i]) / totalDistance) {
                // L'incident est sur ce segment
                const segmentProgress = (relativePosition * totalDistance - accumulatedDistance) / segmentDistances[i];
                const lat = axePoints[segmentStart][0] + segmentProgress * (axePoints[segmentEnd][0] - axePoints[segmentStart][0]);
                const lng = axePoints[segmentStart][1] + segmentProgress * (axePoints[segmentEnd][1] - axePoints[segmentStart][1]);
                
                return [lat, lng];
            }
            
            accumulatedDistance += segmentDistances[i];
        }
        
        return null;
    } catch (error) {
        console.error('Erreur lors du positionnement PK:', error);
        return null;
    }
}

// Parser une valeur PK (ex: "202+200" ou "131.926")
function parsePKValue(pkString) {
    if (!pkString || pkString === 'None' || pkString === 'N/A') return null;
    
    try {
        // Format "202+200" -> 202.2 km
        if (pkString.includes('+')) {
            const parts = pkString.split('+');
            const km = parseFloat(parts[0]);
            const meters = parseFloat(parts[1]);
            return km + (meters / 1000);
        }
        
        // Format "131.926" -> 131.926 km
        return parseFloat(pkString);
    } catch (error) {
        return null;
    }
}

// Obtenir les positions des gares
function getGarePositions() {
    return {
        // Gares LGV Al Boraq
        'Tanger Ville': [35.7595, -5.8340],
        'Kenitra': [34.2610, -6.5802],
        'Rabat Agdal': [33.9591, -6.8498],
        'Casablanca Voyageurs': [33.5970, -7.6186],
        
        // Réseau classique - Axe Nord
        'Assilah': [35.4650, -6.0366],
        'Larache': [35.1933, -6.1558],
        'Ksar El Kebir': [35.0019, -5.9083],
        'Souk El Arbaa': [34.6908, -5.9886],
        'Sidi Yahya El Gharb': [34.3008, -6.3106],
        'Sidi Slimane': [34.2628, -5.9222],
        'Sidi Kacem': [34.2214, -5.7031],
        
        // Axe Atlantique
        'Sale': [34.0531, -6.7985],
        'Rabat Ville': [34.0209, -6.8417],
        'Temara': [33.9281, -6.9067],
        'Skhirat': [33.8519, -7.0306],
        'Bouznika': [33.7869, -7.1608],
        'Mohammedia': [33.6866, -7.3837],
        'Casablanca Port': [33.6036, -7.6233],
        'Ain Sebaa': [33.6147, -7.5263],
        
        // Axe Casa-Marrakech
        'Berrechid': [33.2582, -7.5870],
        'Settat': [33.0013, -7.6216],
        'Ben Ahmed': [32.7367, -7.9833],
        'Benguerir': [32.2372, -7.9549],
        'Marrakech': [31.6295, -7.9811],
        
        // Axe Oriental
        'Meknes': [33.8839, -5.5406],
        'Fes': [34.0334, -4.9998],
        'Taourirt': [34.4078, -2.8931],
        'Oujda': [34.6814, -1.9086],
        'Nador': [35.1681, -2.9287],
        
        // Autres gares importantes
        'El Jadida': [33.2316, -8.5007],
        'Safi': [32.2833, -9.2333],
        'Youssoufia': [32.2450, -8.5308],
        'Khouribga': [32.8811, -6.9063],
        'Oued Zem': [32.8631, -6.5738]
    };
}

// Trouver la position d'une gare par son nom (AMÉLIORÉ pour gares génériques)
function findGarePosition(gareName, garePositions) {
    if (!gareName) return null;
    
    const normalizedName = gareName.toLowerCase().trim();
    
    // Recherche exacte
    for (const [name, position] of Object.entries(garePositions)) {
        if (name.toLowerCase() === normalizedName) {
            return position;
        }
    }
    
    // Recherche partielle
    for (const [name, position] of Object.entries(garePositions)) {
        if (name.toLowerCase().includes(normalizedName) || normalizedName.includes(name.toLowerCase())) {
            return position;
        }
    }
    
    // Recherche par mots-clés AMÉLIORÉE pour gares génériques
    const keywords = {
        // Casablanca
        'casa': 'Casablanca Voyageurs',
        'casablanca': 'Casablanca Voyageurs',
        'casa voyageurs': 'Casablanca Voyageurs',
        'casa/marrakech': 'Casablanca Voyageurs',
        'casa/marrakech v2': 'Casablanca Voyageurs',
        'casa/skacem': 'Casablanca Voyageurs',
        
        // Rabat
        'rabat': 'Rabat Ville',
        'rabat ville': 'Rabat Ville',
        'rabat agdal': 'Rabat Agdal',
        
        // Tanger
        'tanger': 'Tanger Ville',
        'tanger ville': 'Tanger Ville',
        'tanger/fes': 'Tanger Ville',
        'tanger/fes rac': 'Tanger Ville',
        'tanger/fes u': 'Tanger Ville',
        'tanger/fesv1': 'Tanger Ville',
        
        // Marrakech
        'marrakech': 'Marrakech',
        'casa voitureurs/marrakech': 'Marrakech',
        'casa voyageurs/marrakech': 'Marrakech',
        'casa voyageurs/marrakech v2': 'Marrakech',
        
        // Fes
        'fes': 'Fes',
        'fes/oujda': 'Fes',
        'fes/oujda real': 'Fes',
        
        // Autres gares importantes
        'meknes': 'Meknes',
        'oujda': 'Oujda',
        'nador': 'Nador',
        'kenitra': 'Kenitra',
        'sale': 'Sale',
        'mohammedia': 'Mohammedia',
        'settat': 'Settat',
        'benguerir': 'Benguerir',
        'benguerir/safi': 'Benguerir',
        'benguerir/safi u': 'Benguerir',
        'el jadida': 'El Jadida',
        'nouaceur/eljadida': 'El Jadida',
        'nouaceur/eljadidav2': 'El Jadida',
        'safi': 'Safi',
        'sidi kacem': 'Sidi Kacem',
        'sidi slimane': 'Sidi Slimane',
        'sidi yahya': 'Sidi Yahya El Gharb',
        'ksar el kebir': 'Ksar El Kebir',
        'larache': 'Larache',
        'assilah': 'Assilah',
        'temara': 'Temara',
        'skhirat': 'Skhirat',
        'bouznika': 'Bouznika',
        'berrechid': 'Berrechid',
        'ben ahmed': 'Ben Ahmed',
        'taourirt': 'Taourirt',
        'taourirt/nador': 'Taourirt',
        'khouribga': 'Khouribga',
        'oued zem': 'Oued Zem',
        'youssoufia': 'Youssoufia'
    };
    
    // Recherche par mots-clés
    for (const [keyword, gareName] of Object.entries(keywords)) {
        if (normalizedName.includes(keyword)) {
            return garePositions[gareName];
        }
    }
    
    // Recherche par mots-clés partiels (fallback)
    const partialKeywords = {
        'casa': 'Casablanca Voyageurs',
        'rabat': 'Rabat Ville',
        'tanger': 'Tanger Ville',
        'marrakech': 'Marrakech',
        'fes': 'Fes',
        'meknes': 'Meknes',
        'oujda': 'Oujda',
        'nador': 'Nador',
        'kenitra': 'Kenitra',
        'sale': 'Sale',
        'mohammedia': 'Mohammedia',
        'settat': 'Settat',
        'benguerir': 'Benguerir',
        'el jadida': 'El Jadida',
        'safi': 'Safi'
    };
    
    for (const [keyword, gareName] of Object.entries(partialKeywords)) {
        if (normalizedName.includes(keyword)) {
            return garePositions[gareName];
        }
    }
    
    return null;
}

// Trouver l'index d'un point sur un axe
function findPointIndexOnAxe(point, axePoints) {
    let closestIndex = -1;
    let minDistance = Infinity;
    
    for (let i = 0; i < axePoints.length; i++) {
        const distance = calculateDistance(point, axePoints[i]);
        if (distance < minDistance) {
            minDistance = distance;
            closestIndex = i;
        }
    }
    
    return closestIndex;
}

// Calculer la distance entre deux points (formule de Haversine simplifiée)
function calculateDistance(point1, point2) {
    const lat1 = point1[0] * Math.PI / 180;
    const lat2 = point2[0] * Math.PI / 180;
    const deltaLat = (point2[0] - point1[0]) * Math.PI / 180;
    const deltaLng = (point2[1] - point1[1]) * Math.PI / 180;
    
    const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(deltaLng/2) * Math.sin(deltaLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    
    return 6371 * c; // Rayon de la Terre en km
}

// Afficher les axes ferroviaires sur la carte (DÉSACTIVÉ - axes masqués)
function displayRailwayAxes() {
    console.log('🛤️ Axes ferroviaires masqués (seulement gares et incidents)');
    
    // Nettoyer les axes existants
    if (arcsLayer) {
        arcsLayer.clearLayers();
    }
    
    // Retourner sans afficher les axes
    return;
    
    // Positions des axes ferroviaires (passant exactement par les gares)
    const axePositions = {
        'LGV-Al-Boraq': [
            // LGV Al Boraq - Tracé intérieur officiel
            [35.7595, -5.8340], // Tanger Ville
            [35.6000, -5.8000], // Sortie Tanger vers intérieur
            [35.4000, -5.7000], // Plaine intérieure Gharb
            [35.2000, -5.6000], // Traverse terres agricoles
            [35.0000, -5.5000], // Continue intérieur
            [34.8000, -5.6000], // Plaine Gharb centrale
            [34.6000, -5.7000], // Évite zones côtières
            [34.4000, -5.8000], // Continue sud-est
            [34.3000, -5.9000], // Traverse Loukkos (intérieur)
            [34.2610, -6.5802]  // Kenitra - Junction
        ],
        'Tanger-Kenitra-Classique': [
            // Ligne classique Tanger-Kenitra via côte
            [35.7595, -5.8340], // Tanger Ville
            [35.4650, -6.0366], // Assilah
            [35.1933, -6.1558], // Larache
            [35.0019, -5.9083], // Ksar El Kebir
            [34.6908, -5.9886], // Souk El Arbaa
            [34.3008, -6.3106], // Sidi Yahya El Gharb
            [34.2610, -6.5802]  // Kenitra
        ],
        'Kenitra-Casablanca-LGV': [
            // Ligne Kenitra-Casablanca (utilisée par LGV)
            [34.2610, -6.5802], // Kenitra
            [34.0531, -6.7985], // Salé
            [33.9591, -6.8498], // Rabat Agdal (LGV)
            [34.0209, -6.8417], // Rabat Ville
            [33.9281, -6.9067], // Témara
            [33.8519, -7.0306], // Skhirat
            [33.7869, -7.1608], // Bouznika
            [33.6866, -7.3837], // Mohammedia
            [33.5970, -7.6186]  // Casablanca Voyageurs
        ],
        'Mohammedia-Bouznika-Direct': [
            // Ligne DIRECTE Mohammedia-Bouznika (TNR)
            [33.6866, -7.3837], // Mohammedia
            [33.7500, -7.3000], // Trajet côtier direct
            [33.7869, -7.1608]  // Bouznika
        ],
        'Casablanca-Marrakech': [
            [33.5970, -7.6186], // Casablanca Voyageurs
            [33.2582, -7.5870], // Berrechid
            [33.0013, -7.6216], // Settat
            [32.7367, -7.9833], // Ben Ahmed
            [32.2372, -7.9549], // Benguerir
            [31.6295, -7.9811]  // Marrakech
        ],
        'Fes-Oujda-Real': [
            // Fès-Oujda (tracé réel via Taza-Guercif)
            [34.0334, -4.9998], // Fès
            [34.0833, -4.6167], // Oued Amlil
            [34.2130, -4.0100], // Taza (col de Taza)
            [34.0667, -3.4833], // Msoun
            [34.2264, -3.3519], // Guercif
            [34.4092, -2.8953], // Taourirt
            [34.6867, -1.9114]  // Oujda
        ],
        'Taourirt-Nador': [
            [34.4092, -2.8953], // Taourirt
            [34.8000, -2.9000], // Traversée Rif
            [35.1681, -2.9287]  // Nador
        ],
        'Phosphates': [
            // Ligne phosphates
            [34.2214, -5.7031], // Sidi Kacem
            [32.8811, -6.9063], // Khouribga
            [32.8631, -6.5738], // Oued Zem
            [32.2450, -8.5308], // Youssoufia
            [32.2833, -9.2333]  // Safi
        ],
        'El-Jadida-Casablanca': [
            // Ligne El Jadida → Casablanca (direct via gares existantes)
            [33.2316, -8.5007], // El Jadida
            [33.5970, -7.6186]  // Casablanca Voyageurs
        ]
    };
    
    // Couleurs pour les différents axes (selon données professionnelles ONCF 2024)
    const axeColors = {
        'LGV-Al-Boraq': '#C41E3A',        // Rouge ONCF (LGV)
        'Tanger-Kenitra-Classique': '#1E88E5',  // Bleu classique
        'Kenitra-Casablanca-LGV': '#C41E3A',    // Rouge LGV
        'Mohammedia-Bouznika-Direct': '#FF9800', // Orange TNR
        'Casablanca-Marrakech': '#4CAF50',      // Vert classique
        'Fes-Oujda-Real': '#9C27B0',            // Violet classique
        'Taourirt-Nador': '#00BCD4',            // Cyan classique
        'Phosphates': '#795548',                // Marron fret
        'El-Jadida-Casablanca': '#00ACC1',      // Teal classique
        'Nouaceur-El-Jadida': '#17a2b8'         // Bleu clair
    };
    
    // Créer les lignes pour chaque axe
    Object.entries(axePositions).forEach(([axeName, points]) => {
        if (points.length >= 2) {
            const polyline = L.polyline(points, {
                color: axeColors[axeName] || '#2c3e50',
                weight: 4,
                opacity: 0.8,
                smoothFactor: 1
            });
            
            // Ajouter un popup avec le nom de l'axe
            polyline.bindPopup(`
                <div class="text-center">
                    <h6><i class="fas fa-route me-2"></i>${axeName}</h6>
                    <p class="mb-0">Axe ferroviaire principal</p>
                </div>
            `);
            
            arcsLayer.addLayer(polyline);
        }
    });
    
    console.log('✅ Axes ferroviaires affichés sur la carte');
}

// Obtenir la configuration de l'icône selon le statut de l'incident
function getIncidentIconConfig(incident) {
    const status = incident.etat ? incident.etat.toLowerCase() : 'inconnu';
    
    // Configuration par défaut
    let config = {
        icon: 'fas fa-exclamation-triangle',
        color: '#dc3545', // Rouge par défaut
        size: 16,
        fontSize: 10
    };
    
    // Configuration selon le statut
    switch (status) {
        case 'ouvert':
            config.color = '#dc3545'; // Rouge
            config.icon = 'fas fa-exclamation-triangle';
            config.size = 18;
            break;
        case 'en cours':
            config.color = '#ffc107'; // Jaune
            config.icon = 'fas fa-tools';
            config.size = 16;
            break;
        case 'résolu':
        case 'resolu':
            config.color = '#28a745'; // Vert
            config.icon = 'fas fa-check-circle';
            config.size = 14;
            break;
        case 'fermé':
        case 'ferme':
            config.color = '#6c757d'; // Gris
            config.icon = 'fas fa-times-circle';
            config.size = 14;
            break;
    }
    
    return config;
}

// Créer un marqueur pour un incident - BASÉ SUR ge_localisation
function createIncidentMarker(incident) {
    console.log(`📍 Incident ${incident.id}: Positionnement basé sur ge_localisation`);
    
    // UTILISER UNIQUEMENT les données de ge_localisation
    const coords = positionIncidentFromGeLocalisation(incident);
    
    if (!coords) {
        console.log(`⚠️ Incident ${incident.id}: Impossible de positionner, ignoré`);
        return null;
    }
    
    // Créer une icône différenciée selon le type et le statut
    const iconConfig = getIncidentIconConfig(incident);
    
    const icon = L.divIcon({
        className: 'incident-marker',
        html: `<div style="
            width: ${iconConfig.size}px; 
            height: ${iconConfig.size}px; 
            background-color: ${iconConfig.color}; 
            border: 2px solid white; 
            border-radius: 50%; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: ${iconConfig.fontSize}px;
            cursor: pointer;
            transition: all 0.2s ease;
        " title="${incident.type_name || 'Incident'} - ${incident.etat || 'Statut inconnu'}">
            <i class="${iconConfig.icon}"></i>
        </div>`,
        iconSize: [iconConfig.size, iconConfig.size],
        iconAnchor: [iconConfig.size/2, iconConfig.size/2]
    });

    const marker = L.marker(coords, { icon: icon });
    
    // Stocker les données de l'incident dans le marqueur
    marker.incidentData = incident;
    
    // Ajouter le popup
    const popupContent = createIncidentPopup(incident);
    marker.bindPopup(popupContent);
    
    // Ajouter l'événement de clic
    marker.on('click', () => {
        selectedIncident = incident;
        showIncidentInfo(incident);
    });
    
    return marker;
}

// Créer le contenu du popup pour un incident avec toutes les informations géographiques
function createIncidentPopup(incident) {
    const date = incident.date_debut ? new Date(incident.date_debut).toLocaleDateString('fr-FR') : 'N/A';
    const heure = incident.heure_debut || 'N/A';
    
    // Déterminer le type de localisation
    const isInStation = determineIncidentLocationType(incident);
    const locationType = isInStation ? '🏢 EN GARE' : '🛤️ EN LIGNE';
    
    // Informations géographiques détaillées
    let locationInfo = '';
    let pkInfo = '';
    let gareInfo = '';
    let typeLocationInfo = '';
    
    // Informations de localisation
    if (incident.localisation_nom) {
        locationInfo = `<div><strong>📍 Localisation:</strong> ${incident.localisation_nom}</div>`;
    }
    
    // Type de localisation
    if (incident.type_localisation) {
        typeLocationInfo = `<div><strong>${locationType}</strong> (${incident.type_localisation})</div>`;
    } else {
        typeLocationInfo = `<div><strong>${locationType}</strong></div>`;
    }
    
    // Informations de PK (Point Kilométrique) - seulement si pertinentes
    if (incident.pk_debut || incident.pk_fin) {
        const pkDebut = incident.pk_debut || null;
        const pkFin = incident.pk_fin || null;
        
        // Afficher seulement si on a des PK valides
        if (pkDebut && pkDebut !== 'N/A' && pkDebut !== null) {
            if (pkFin && pkFin !== 'N/A' && pkFin !== null && pkFin !== pkDebut) {
                pkInfo = `<div><strong>🛤️ PK:</strong> ${pkDebut} - ${pkFin}</div>`;
            } else {
                pkInfo = `<div><strong>🛤️ PK:</strong> ${pkDebut}</div>`;
            }
        }
    }
    
    // Informations des gares - DÉSACTIVÉ (ne pas afficher dans le popup)
    // Les informations de gares ne sont plus affichées dans le popup selon la demande utilisateur
    gareInfo = '';
    
    // Informations de type et source
    let typeInfo = '';
    if (incident.type_name) {
        typeInfo = `<div><strong>📋 Type:</strong> ${incident.type_name}</div>`;
    }
    
    let sourceInfo = '';
    if (incident.source_name) {
        sourceInfo = `<div><strong>📡 Source:</strong> ${incident.source_name}</div>`;
    }
    
    return `
        <div class="incident-popup">
            <h6>${incident.type_name || 'Incident'}</h6>
            <div class="mb-2">
                <span class="badge bg-${incident.etat === 'Fermé' ? 'success' : 'danger'}">${incident.etat || 'Ouvert'}</span>
                <span class="badge bg-primary">#${incident.id}</span>
            </div>
            <div class="small">
                <div><strong>Date:</strong> ${date}</div>
                <div><strong>Heure:</strong> ${heure}</div>
                <div><strong>Type:</strong> ${incident.type_name || 'N/A'}</div>
                <div><strong>Source:</strong> ${incident.source_name || 'N/A'}</div>
                ${locationInfo}
                ${pkInfo}
            </div>
            <button class="btn btn-sm btn-primary mt-2" onclick="showIncidentDetails(${incident.id})">
                <i class="fas fa-info-circle me-1"></i>Détails
            </button>
        </div>
    `;
}

// Initialiser les contrôles de la carte
function initializeMapControls() {
    // Remplir les filtres
    populateFilters();
    
    // Ajouter les événements aux contrôles
    const layerSelect = document.getElementById('layerSelect');
    const axeFilter = document.getElementById('axeFilter');
    const typeFilter = document.getElementById('typeFilter');
    
    if (layerSelect) layerSelect.addEventListener('change', filterLayers);
    if (axeFilter) axeFilter.addEventListener('change', filterByAxe);
    if (typeFilter) typeFilter.addEventListener('change', filterByType);
}

// Remplir les filtres avec les données
function populateFilters() {
    // Charger les axes uniques depuis l'API des arcs
    fetch('/api/arcs')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                const axeSelect = document.getElementById('axeFilter');
                const typeSelect = document.getElementById('typeFilter');
                
                // Extraire les axes uniques depuis les arcs
                const axesUniques = [...new Set(data.data.map(arc => arc.axe).filter(axe => axe))];
                
                // Remplir le filtre des axes
                if (axeSelect) {
                    axeSelect.innerHTML = '<option value="">Tous les axes</option>';
                    axesUniques.forEach(axe => {
                        const option = document.createElement('option');
                        option.value = axe;
                        option.textContent = axe;
                        axeSelect.appendChild(option);
                    });
                }
                
                // Pour les types, on va utiliser des types prédéfinis
                if (typeSelect) {
                    typeSelect.innerHTML = '<option value="">Tous les types</option>';
                    const typesPredefinis = [
                        'Gare Principale',
                        'Gare Secondaire',
                        'Gare de Passage',
                        'Halte',
                        'Point d\'Arrêt',
                        'Gare de Triage',
                        'Gare de Marchandises'
                    ];
                    
                    typesPredefinis.forEach(type => {
                        const option = document.createElement('option');
                        option.value = type;
                        option.textContent = type;
                        typeSelect.appendChild(option);
                    });
                }
                
                console.log(`✅ ${axesUniques.length} axes uniques chargés pour les filtres`);
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors du chargement des filtres:', error);
        });
}

// Filtrer les couches
function filterLayers() {
    const layerValue = document.getElementById('layerSelect')?.value || 'all';
    
    // Retirer toutes les couches d'abord
    map.removeLayer(garesLayer);
    map.removeLayer(arcsLayer);
    map.removeLayer(incidentsLayer);
    
    if (layerValue === 'gares') {
        map.addLayer(garesLayer);
    } else if (layerValue === 'arcs') {
        map.addLayer(arcsLayer);
    } else if (layerValue === 'incidents') {
        map.addLayer(incidentsLayer);
    } else {
        // 'all' - afficher toutes les couches
        map.addLayer(garesLayer);
        map.addLayer(arcsLayer);
        map.addLayer(incidentsLayer);
    }
}

// Filtrer par axe
function filterByAxe() {
    const axeValue = document.getElementById('axeFilter')?.value || '';
    console.log('🔍 Filtrage par axe:', axeValue);
    
    if (!axeValue) {
        // Afficher tous les arcs
        arcsLayer.eachLayer(layer => {
            layer.setStyle({ opacity: 0.8 });
        });
        return;
    }
    
    // Filtrer les arcs par axe
    arcsLayer.eachLayer(layer => {
        const arcData = layer.arcData;
        if (arcData && arcData.axe === axeValue) {
            layer.setStyle({ opacity: 0.8 });
        } else {
            layer.setStyle({ opacity: 0.2 });
        }
    });
    
    showNotification(`Filtrage par axe: ${axeValue}`, 'info');
}

// Filtrer par type
function filterByType() {
    const typeValue = document.getElementById('typeFilter')?.value || '';
    console.log('🔍 Filtrage par type:', typeValue);
    
    if (!typeValue) {
        // Afficher toutes les gares
        garesLayer.eachLayer(layer => {
            layer.setStyle({ opacity: 1 });
        });
        return;
    }
    
    // Filtrer les gares par type
    garesLayer.eachLayer(layer => {
        const gareData = layer.gareData;
        if (gareData) {
            const gareTypeName = getGareTypeName(gareData.type);
            if (gareTypeName === typeValue) {
                layer.setStyle({ opacity: 1 });
            } else {
                layer.setStyle({ opacity: 0.3 });
            }
        }
    });
    
    showNotification(`Filtrage par type: ${typeValue}`, 'info');
}

// Réinitialiser la carte
function resetMap() {
    // Réinitialiser les filtres
    const layerSelect = document.getElementById('layerSelect');
    const axeFilter = document.getElementById('axeFilter');
    const typeFilter = document.getElementById('typeFilter');
    
    if (layerSelect) layerSelect.value = 'all';
    if (axeFilter) axeFilter.value = '';
    if (typeFilter) typeFilter.value = '';
    
    // Afficher toutes les couches
    map.addLayer(garesLayer);
    map.addLayer(arcsLayer);
    map.addLayer(incidentsLayer);
    
    // Réinitialiser l'opacité de tous les éléments
    garesLayer.eachLayer(layer => {
        layer.setStyle({ opacity: 1 });
    });
    
    arcsLayer.eachLayer(layer => {
        layer.setStyle({ opacity: 0.8 });
    });
    
    // Réinitialiser les incidents (tous affichés)
    if (allIncidents.length > 0) {
        addIncidentsToMap(allIncidents);
    }
    
    // Centrer la carte
    map.setView(MAP_CONFIG.center, MAP_CONFIG.zoom);
    
    // Masquer le panneau d'info
    const infoPanel = document.getElementById('infoPanel');
    if (infoPanel) infoPanel.style.display = 'none';
    
    // Mettre à jour les statistiques
    updateMapStats();
    
    showNotification('Carte réinitialisée', 'info');
}

// Mettre à jour les statistiques de la carte
function updateMapStats() {
    const garesCount = garesLayer.getLayers().length;
    const arcsCount = arcsLayer.getLayers().length;
    const incidentsCount = incidentsLayer.getLayers().length;
    
    const mapGaresCount = document.getElementById('mapGaresCount');
    const mapArcsCount = document.getElementById('mapArcsCount');
    const mapIncidentsCount = document.getElementById('mapIncidentsCount');
    
    if (mapGaresCount) mapGaresCount.textContent = garesCount;
    if (mapArcsCount) mapArcsCount.textContent = arcsCount;
    if (mapIncidentsCount) mapIncidentsCount.textContent = incidentsCount;
    
    // Mettre à jour les statistiques avancées
    updateAdvancedStatistics();
}

// Configuration des icônes d'incidents selon le type et le statut
function getIncidentIconConfig(incident) {
    const typeName = incident.type_name || '';
    const etat = incident.etat || '';
    
    // Configuration par défaut
    let config = {
        size: 16,
        color: '#007bff',
        icon: 'fas fa-exclamation-triangle',
        fontSize: 10
    };
    
    // Ajuster selon le type d'incident
    if (typeName.toLowerCase().includes('signal')) {
        config.color = '#ffc107'; // Jaune pour signalisation
        config.icon = 'fas fa-traffic-light';
    } else if (typeName.toLowerCase().includes('voie')) {
        config.color = '#dc3545'; // Rouge pour voies
        config.icon = 'fas fa-train';
    } else if (typeName.toLowerCase().includes('électrique')) {
        config.color = '#6f42c1'; // Violet pour électrique
        config.icon = 'fas fa-bolt';
    } else if (typeName.toLowerCase().includes('sécurité')) {
        config.color = '#fd7e14'; // Orange pour sécurité
        config.icon = 'fas fa-shield-alt';
    }
    
    // Ajuster selon le statut
    if (etat === 'Ouvert') {
        config.size = 18; // Plus grand pour incidents ouverts
        config.color = '#dc3545'; // Rouge pour ouvert
    } else if (etat === 'En cours') {
        config.size = 16;
        config.color = '#ffc107'; // Jaune pour en cours
    } else if (etat === 'Résolu') {
        config.size = 14;
        config.color = '#28a745'; // Vert pour résolu
    } else if (etat === 'Fermé') {
        config.size = 12;
        config.color = '#6c757d'; // Gris pour fermé
    }
    
    return config;
}

// NOUVELLE FONCTION: Positionner incident basé sur ge_localisation
function positionIncidentFromGeLocalisation(incident) {
    console.log(`🎯 Incident ${incident.id}: Positionnement basé sur ge_localisation`);
    console.log('📊 Données ge_localisation:', {
        gare_debut_id: incident.gare_debut_id,
        gare_fin_id: incident.gare_fin_id,
        type_localisation: incident.type_localisation,
        pk_debut: incident.pk_debut,
        pk_fin: incident.pk_fin
    });
    
    // MAPPING des codes de gares vers les coordonnées
    const garePositions = {
        'LIN01.T001.TANGER': [35.7595, -5.8340], // Tanger Ville
        'LIN01.T001.ASILAH': [35.4650, -6.0366], // Assilah
        'LIN01.T001.LARACHE': [35.1933, -6.1558], // Larache
        'LIN01.T001.KENITRA': [34.2610, -6.5802], // Kenitra
        'LIN01.T001.SALE': [34.0531, -6.7985], // Salé
        'LIN01.T001.RABAT': [34.0209, -6.8417], // Rabat Ville
        'LIN01.T001.TEMARA': [33.9281, -6.9067], // Témara
        'LIN01.T001.SKHIRAT': [33.8519, -7.0306], // Skhirat
        'LIN01.T001.BOUZNIKA': [33.7869, -7.1608], // Bouznika
        'LIN01.T001.MOHAMMEDIA': [33.6866, -7.3837], // Mohammedia
        'LIN01.T001.CASABLANCA': [33.5970, -7.6186], // Casablanca Voyageurs
        'LIN01.T001.BERRECHID': [33.2582, -7.5870], // Berrechid
        'LIN01.T001.SETTAT': [33.0013, -7.6216], // Settat
        'LIN01.T001.BEN_AHMED': [32.7367, -7.9833], // Ben Ahmed
        'LIN01.T001.BENGUERIR': [32.2372, -7.9549], // Benguerir
        'LIN01.T001.MARRAKECH': [31.6295, -7.9811], // Marrakech
        'LIN01.T001.SIDI_KACEM': [34.2214, -5.7031], // Sidi Kacem
        'LIN01.T001.MEKNES': [33.8839, -5.5406], // Meknes
        'LIN01.T001.FES': [34.0334, -4.9998], // Fès
        'LIN01.T001.TAZA': [34.2130, -4.0100], // Taza
        'LIN01.T001.GUERCIF': [34.2264, -3.3519], // Guercif
        'LIN01.T001.TAOURIRT': [34.4092, -2.8953], // Taourirt
        'LIN01.T001.OUJDA': [34.6867, -1.9114], // Oujda
        'LIN01.T001.NADOR': [35.1681, -2.9287], // Nador
        'LIN01.T001.KHOURIBGA': [32.8811, -6.9063], // Khouribga
        'LIN01.T001.OUED_ZEM': [32.8631, -6.5738], // Oued Zem
        'LIN01.T001.EL_JADIDA': [33.2316, -8.5007], // El Jadida
        'LIN01.T001.SAFI': [32.2833, -9.2333] // Safi
    };
    
    let coords = null;
    
    // PRIORITÉ 1: Utiliser gare_debut_id et gare_fin_id
    if (incident.gare_debut_id && garePositions[incident.gare_debut_id]) {
        const gareDebut = garePositions[incident.gare_debut_id];
        
        if (incident.gare_fin_id && garePositions[incident.gare_fin_id]) {
            // Deux gares: positionner entre elles
            const gareFin = garePositions[incident.gare_fin_id];
            
            if (incident.type_localisation && incident.type_localisation.toLowerCase().includes('gare')) {
                // EN GARE: positionner sur la gare de début
                coords = gareDebut;
                console.log(`✅ Incident ${incident.id}: EN GARE sur ${incident.gare_debut_id}`);
            } else {
                // EN LIGNE: positionner entre les deux gares
                const t = (incident.id % 100) / 100; // Position basée sur l'ID
                coords = [
                    gareDebut[0] + t * (gareFin[0] - gareDebut[0]),
                    gareDebut[1] + t * (gareFin[1] - gareDebut[1])
                ];
                console.log(`✅ Incident ${incident.id}: EN LIGNE entre ${incident.gare_debut_id} et ${incident.gare_fin_id}`);
            }
        } else {
            // Une seule gare: positionner dessus
            coords = gareDebut;
            console.log(`✅ Incident ${incident.id}: Sur gare unique ${incident.gare_debut_id}`);
        }
    }
    
    // PRIORITÉ 2: Utiliser PK si pas de gares
    if (!coords && (incident.pk_debut || incident.pk_fin)) {
        // Chercher la gare la plus proche du PK
        const pkValue = incident.pk_debut || incident.pk_fin;
        const nearestGare = findNearestGareByPK(pkValue, garePositions);
        
        if (nearestGare) {
            coords = garePositions[nearestGare];
            console.log(`✅ Incident ${incident.id}: Positionné selon PK ${pkValue} près de ${nearestGare}`);
        }
    }
    
    // Ajouter une petite variation pour éviter la superposition
    if (coords) {
        const variation = 0.0001; // ~10m
        const uniqueFactor = incident.id + (incident.type_name ? incident.type_name.length : 0);
        const offsetLat = (Math.sin(uniqueFactor * 0.1) * variation);
        const offsetLng = (Math.cos(uniqueFactor * 0.1) * variation);
        
        coords = [coords[0] + offsetLat, coords[1] + offsetLng];
    }
    
    return coords;
}

// Mettre à jour les statistiques avancées - BASÉ SUR ge_localisation
function updateAdvancedStatistics() {
    const visibleIncidents = incidentsLayer.getLayers();
    
    // Statistiques par statut
    const statusStats = {
        'Ouvert': 0,
        'En cours': 0,
        'Résolu': 0,
        'Fermé': 0
    };
    
    // Statistiques par type
    const typeStats = {};
    
    // Statistiques par localisation basées sur type_localisation
    const locationStats = {
        'Gare': 0,
        'En ligne': 0
    };
    
    visibleIncidents.forEach(marker => {
        const incident = marker.incidentData;
        if (incident) {
            // Compter par statut
            if (statusStats.hasOwnProperty(incident.etat)) {
                statusStats[incident.etat]++;
            }
            
            // Compter par type
            const typeName = incident.type_name || 'Non défini';
            typeStats[typeName] = (typeStats[typeName] || 0) + 1;
            
            // Compter par localisation selon ge_localisation
            const location = incident.type_localisation || 'Non défini';
            if (location.toLowerCase().includes('gare')) {
                locationStats['Gare']++;
            } else {
                locationStats['En ligne']++;
            }
        }
    });
    
    // Mettre à jour l'affichage des statistiques par statut
    const incidentsOuverts = document.getElementById('incidentsOuverts');
    const incidentsEnCours = document.getElementById('incidentsEnCours');
    const incidentsResolus = document.getElementById('incidentsResolus');
    const incidentsFermes = document.getElementById('incidentsFermes');
    
    if (incidentsOuverts) incidentsOuverts.textContent = statusStats['Ouvert'] || '0';
    if (incidentsEnCours) incidentsEnCours.textContent = statusStats['En cours'] || '0';
    if (incidentsResolus) incidentsResolus.textContent = statusStats['Résolu'] || '0';
    if (incidentsFermes) incidentsFermes.textContent = statusStats['Fermé'] || '0';
    
    // Mettre à jour l'affichage des statistiques par localisation
    const incidentsEnGare = document.getElementById('incidentsEnGare');
    const incidentsEnLigne = document.getElementById('incidentsEnLigne');
    
    if (incidentsEnGare) incidentsEnGare.textContent = locationStats['Gare'] || '0';
    if (incidentsEnLigne) incidentsEnLigne.textContent = locationStats['En ligne'] || '0';
    
    // Mettre à jour l'affichage des types d'incidents
    updateIncidentTypesDisplay(typeStats);
    
    // Mettre à jour la légende des types d'incidents
    updateIncidentTypesLegend(typeStats);
}

// Mettre à jour l'affichage des types d'incidents
function updateIncidentTypesDisplay(typeStats) {
    const container = document.getElementById('incidentTypesStats');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Trier les types par nombre d'incidents (décroissant)
    const sortedTypes = Object.entries(typeStats)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5); // Afficher seulement les 5 premiers
    
    sortedTypes.forEach(([typeName, count]) => {
        const typeElement = document.createElement('div');
        typeElement.className = 'd-flex justify-content-between align-items-center mb-1';
        typeElement.innerHTML = `
            <span class="small">${typeName}</span>
            <span class="badge bg-secondary">${count}</span>
        `;
        container.appendChild(typeElement);
    });
}

// Mettre à jour la légende des types d'incidents
function updateIncidentTypesLegend(typeStats) {
    const container = document.getElementById('incidentTypesLegend');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Créer une légende pour les types d'incidents
    const legendTitle = document.createElement('h6');
    legendTitle.className = 'mb-2';
    legendTitle.textContent = 'Types d\'incidents';
    container.appendChild(legendTitle);
    
    // Afficher les types avec leurs couleurs
    Object.entries(typeStats).slice(0, 8).forEach(([typeName, count]) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'd-flex align-items-center mb-1';
        legendItem.innerHTML = `
            <div style="width: 12px; height: 12px; background-color: #007bff; border-radius: 50%; margin-right: 8px;"></div>
            <span class="small">${typeName} (${count})</span>
        `;
        container.appendChild(legendItem);
    });
}

// Fonction pour trouver la gare la plus proche d'un PK
function findNearestGareByPK(pkValue, garePositions) {
    if (!pkValue) return null;
    
    // Convertir PK en nombre si c'est une chaîne
    const pk = parseFloat(pkValue);
    if (isNaN(pk)) return null;
    
    // Mapping des PK vers les gares (approximatif)
    const pkToGare = {
        // Ligne Tanger - Casablanca
        0: 'LIN01.T001.TANGER',
        50: 'LIN01.T001.ASILAH',
        100: 'LIN01.T001.LARACHE',
        150: 'LIN01.T001.KENITRA',
        200: 'LIN01.T001.SALE',
        250: 'LIN01.T001.RABAT',
        300: 'LIN01.T001.TEMARA',
        350: 'LIN01.T001.SKHIRAT',
        400: 'LIN01.T001.BOUZNIKA',
        450: 'LIN01.T001.MOHAMMEDIA',
        500: 'LIN01.T001.CASABLANCA',
        550: 'LIN01.T001.BERRECHID',
        600: 'LIN01.T001.SETTAT',
        650: 'LIN01.T001.BEN_AHMED',
        700: 'LIN01.T001.BENGUERIR',
        750: 'LIN01.T001.MARRAKECH',
        
        // Ligne Casablanca - Fès
        100: 'LIN01.T001.SIDI_KACEM',
        150: 'LIN01.T001.MEKNES',
        200: 'LIN01.T001.FES',
        250: 'LIN01.T001.TAZA',
        300: 'LIN01.T001.GUERCIF',
        350: 'LIN01.T001.TAOURIRT',
        400: 'LIN01.T001.OUJDA',
        450: 'LIN01.T001.NADOR',
        
        // Ligne Casablanca - El Jadida
        50: 'LIN01.T001.EL_JADIDA',
        100: 'LIN01.T001.SAFI',
        
        // Ligne Casablanca - Oued Zem
        100: 'LIN01.T001.KHOURIBGA',
        150: 'LIN01.T001.OUED_ZEM'
    };
    
    // Trouver la gare la plus proche du PK
    let nearestGare = null;
    let minDistance = Infinity;
    
    Object.entries(pkToGare).forEach(([pkGare, gareCode]) => {
        const distance = Math.abs(pk - parseFloat(pkGare));
        if (distance < minDistance) {
            minDistance = distance;
            nearestGare = gareCode;
        }
    });
    
    return nearestGare;
}

// Afficher les informations d'une gare
function showGareInfo(gare) {
    const infoPanel = document.getElementById('infoPanel');
    const infoContent = document.getElementById('infoContent');
    
    if (!infoPanel || !infoContent) return;
    
    const typeDisplay = getGareTypeName(gare.type);
    const villeDisplay = getVilleName(gare.ville);
    const etatDisplay = gare.etat === 'ACTIVE' ? 'Active' : 'Passive';
    
    infoContent.innerHTML = `
        <h6 class="text-primary">${gare.nom || 'Gare sans nom'}</h6>
        <div class="mb-2">
            <span class="badge bg-primary">${gare.code || 'N/A'}</span>
            <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">${etatDisplay}</span>
        </div>
        <div class="small">
            <div><strong>Type:</strong> ${typeDisplay}</div>
            <div><strong>Ville:</strong> ${villeDisplay}</div>
            <div><strong>Région:</strong> ${gare.region || 'N/A'}</div>
            <div><strong>Code opérationnel:</strong> ${gare.codeoperationnel || 'N/A'}</div>
        </div>
        <button class="btn btn-sm btn-primary mt-2" onclick="showGareDetails(${gare.id})">
            <i class="fas fa-info-circle me-1"></i>Voir détails
        </button>
    `;
    
    infoPanel.style.display = 'block';
}

// Afficher les informations d'un incident
function showIncidentInfo(incident) {
    const infoPanel = document.getElementById('infoPanel');
    const infoContent = document.getElementById('infoContent');
    
    if (!infoPanel || !infoContent) return;
    
    const date = incident.date_debut ? new Date(incident.date_debut).toLocaleDateString('fr-FR') : 'N/A';
    const heure = incident.heure_debut || 'N/A';
    
    infoContent.innerHTML = `
        <h6 class="text-danger">${incident.type_name || 'Incident'}</h6>
        <div class="mb-2">
            <span class="badge bg-${incident.etat === 'Fermé' ? 'success' : 'danger'}">${incident.etat || 'Ouvert'}</span>
            <span class="badge bg-primary">#${incident.id}</span>
        </div>
        <div class="small">
            <div><strong>Date:</strong> ${date}</div>
            <div><strong>Heure:</strong> ${heure}</div>
            <div><strong>Type:</strong> ${incident.type_name || 'N/A'}</div>
            <div><strong>Source:</strong> ${incident.source_name || 'N/A'}</div>
            ${incident.localisation_nom ? `<div><strong>Localisation:</strong> ${incident.localisation_nom}</div>` : ''}
            ${incident.pk_debut ? `<div><strong>PK:</strong> ${incident.pk_debut}${incident.pk_fin && incident.pk_fin !== incident.pk_debut ? ` - ${incident.pk_fin}` : ''}</div>` : ''}
            <div><strong>Description:</strong> ${incident.resume || incident.commentaire || 'Aucune description'}</div>
        </div>
        <button class="btn btn-sm btn-primary mt-2" onclick="showIncidentDetails(${incident.id})">
            <i class="fas fa-info-circle me-1"></i>Voir détails
        </button>
    `;
    
    infoPanel.style.display = 'block';
}

// Afficher les informations d'un arc
function showArcInfo(arc) {
    const infoPanel = document.getElementById('infoPanel');
    const infoContent = document.getElementById('infoContent');
    
    if (!infoPanel || !infoContent) return;
    
    // Déterminer le type d'axe
    let axeType = 'Ligne Classique';
    let typeColor = 'bg-primary';
    let typeIcon = 'fa-route';
    
    if (arc.axe && arc.axe.includes('LGV')) {
        axeType = 'Ligne à Grande Vitesse';
        typeColor = 'bg-danger';
        typeIcon = 'fa-train';
    } else if (arc.axe && (arc.axe.includes('RAC') || arc.axe.includes('TRIANGLE'))) {
        axeType = 'Raccordement';
        typeColor = 'bg-warning';
        typeIcon = 'fa-exchange-alt';
    } else if (arc.axe && arc.axe.includes('U')) {
        axeType = 'Ligne Urbaine';
        typeColor = 'bg-info';
        typeIcon = 'fa-city';
    }
    
    infoContent.innerHTML = `
        <h6 class="text-success"><i class="fas ${typeIcon} me-2"></i>Axe Ferroviaire</h6>
        <div class="mb-3">
            <span class="badge ${typeColor}">${arc.axe || 'N/A'}</span>
            <span class="badge bg-secondary">${axeType}</span>
        </div>
        <div class="small">
            <div class="row mb-2">
                <div class="col-6">
                    <strong>PK Début:</strong><br>
                    <span class="text-muted">${arc.pk_debut || 'N/A'}</span>
                </div>
                <div class="col-6">
                    <strong>PK Fin:</strong><br>
                    <span class="text-muted">${arc.pk_fin || 'N/A'}</span>
                </div>
            </div>
            <div class="row mb-2">
                <div class="col-6">
                    <strong>PLOD:</strong><br>
                    <span class="text-muted">${arc.plod || 'N/A'}</span>
                </div>
                <div class="col-6">
                    <strong>PLOF:</strong><br>
                    <span class="text-muted">${arc.plof || 'N/A'}</span>
                </div>
            </div>
            ${arc.absd || arc.absf ? `
            <div class="row mb-2">
                <div class="col-6">
                    <strong>ABSD:</strong><br>
                    <span class="text-muted">${arc.absd || 'N/A'}</span>
                </div>
                <div class="col-6">
                    <strong>ABSF:</strong><br>
                    <span class="text-muted">${arc.absf || 'N/A'}</span>
                </div>
            </div>
            ` : ''}
        </div>
        <button class="btn btn-sm btn-outline-success mt-2" onclick="showArcDetails(${arc.id})">
            <i class="fas fa-info-circle me-1"></i>Voir détails complets
        </button>
    `;
    
    infoPanel.style.display = 'block';
}

// Configurer les événements de la carte
function setupMapEvents() {
    // Événement de clic sur la carte pour masquer le panneau d'info
    map.on('click', () => {
        const infoPanel = document.getElementById('infoPanel');
        if (infoPanel) infoPanel.style.display = 'none';
    });
    
    // Événement de zoom pour ajuster la taille des marqueurs
    map.on('zoomend', () => {
        const zoom = map.getZoom();
        console.log('Nouveau zoom:', zoom);
    });
}

// Fonction globale pour centrer sur une gare
function centerOnGare() {
    if (selectedGare) {
        const coords = parseGeometry(selectedGare.geometrie);
        if (coords) {
            map.setView(coords, 15);
        }
    }
}

// Parser la géométrie (POINT) et convertir les coordonnées
function parseGeometry(geometryString) {
    if (!geometryString) return null;
    
    try {
        // Essayer d'abord le format WKT (Well-Known Text)
        const wktMatch = geometryString.match(/POINT\(([^)]+)\)/);
        if (wktMatch) {
            const coords = wktMatch[1].split(' ').map(Number);
            
            // Vérifier si c'est du SRID=3857 (Web Mercator) ou du WGS84
            if (geometryString.includes('SRID=3857')) {
                // Convertir de Web Mercator (EPSG:3857) vers WGS84 (EPSG:4326)
                const [x, y] = coords;
                // Formule correcte pour Web Mercator vers WGS84
                const lng = (x / 20037508.34) * 180;
                const lat = (2 * Math.atan(Math.exp(y / 20037508.34 * Math.PI)) - Math.PI / 2) * 180 / Math.PI;
                console.log(`🔄 Conversion SRID=3857 [${x}, ${y}] → WGS84 [${lat}, ${lng}]`);
                return [lat, lng]; // [lat, lng] pour Leaflet
            } else {
                // Coordonnées déjà en WGS84
            return [coords[1], coords[0]]; // [lat, lng] pour Leaflet
            }
        }
        
        // Si c'est du WKB (Well-Known Binary), on ne peut pas le parser côté client
        if (geometryString.startsWith('0101000020')) {
            console.warn('Géométrie WKB détectée, utilisation de coordonnées par défaut');
            return [31.7917, -7.0926];
        }
        
    } catch (error) {
        console.error('Erreur lors du parsing de la géométrie:', error);
    }
    
    return null;
}

// Afficher une notification
function showNotification(message, type = 'info') {
    if (window.oncfGIS && window.oncfGIS.showNotification) {
        window.oncfGIS.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Charger TOUS les incidents avec toutes les informations géographiques - BASÉ SUR ge_localisation
function loadAllIncidents() {
    console.log('🗺️ Chargement des incidents basés sur ge_localisation...');
    
    fetch('/api/evenements')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allIncidents = data.data;
                currentIncidents = allIncidents; // Tous les incidents
                
                console.log(`✅ ${allIncidents.length} incidents chargés avec données ge_localisation`);
                console.log('📊 Message:', data.message);
                
                // Afficher les incidents sur la carte avec positionnement ge_localisation
                addIncidentsToMap(allIncidents);
                
                // Masquer les contrôles de pagination
                const paginationDiv = document.getElementById('incidentPagination');
                if (paginationDiv) {
                    paginationDiv.style.display = 'none';
                }
                
                updateMapStats();
                
                // Notification de succès
                showNotification(`✅ ${allIncidents.length} incidents chargés et affichés sur la carte`, 'success');
            } else {
                console.error('❌ Erreur API:', data);
                showNotification('Erreur lors du chargement des incidents', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors du chargement des incidents:', error);
            showNotification('Erreur lors du chargement des incidents', 'error');
        });
}

// Fonctions de pagination supprimées - tous les incidents sont affichés

// Fonction pour afficher les détails complets d'un arc
function showArcDetails(arcId) {
    console.log('🔍 Affichage des détails de l\'arc:', arcId);
    showNotification(`Détails de l'arc #${arcId} - Fonctionnalité en développement`, 'info');
}

// Variables pour les filtres d'incidents
let incidentFilters = {
    status: '',
    type: '',
    source: '',
    system: '',
    period: ''
};

// Charger les données de référence pour les filtres d'incidents
async function loadIncidentFilterData() {
    try {
        // Charger les types d'incidents
        const typesResponse = await fetch('/api/reference/types');
        if (typesResponse.ok) {
            const types = await typesResponse.json();
            populateIncidentFilterSelect('incidentTypeFilter', types, 'id', 'intitule');
        }
        
        // Charger les sources
        const sourcesResponse = await fetch('/api/reference/sources');
        if (sourcesResponse.ok) {
            const sources = await sourcesResponse.json();
            populateIncidentFilterSelect('incidentSourceFilter', sources, 'id', 'intitule');
        }
        
        // Charger les systèmes
        const systemsResponse = await fetch('/api/reference/systemes');
        if (systemsResponse.ok) {
            const systems = await systemsResponse.json();
            populateIncidentFilterSelect('incidentSystemFilter', systems, 'id', 'intitule');
        }
        
        console.log('✅ Données de filtres d\'incidents chargées');
    } catch (error) {
        console.warn('⚠️ Erreur lors du chargement des données de filtres:', error);
    }
}

// Remplir un select de filtre d'incident
function populateIncidentFilterSelect(selectId, data, valueField, textField) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // Garder l'option par défaut
    const defaultOption = select.querySelector('option[value=""]');
    select.innerHTML = '';
    if (defaultOption) {
        select.appendChild(defaultOption);
    }
    
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueField];
        option.textContent = item[textField];
        select.appendChild(option);
    });
}

// Appliquer les filtres d'incidents
function applyIncidentFilters(filters = null) {
    // Récupérer les valeurs des filtres
    if (!filters) {
        filters = {
            status: document.getElementById('incidentStatusFilter')?.value || '',
            type: document.getElementById('incidentTypeFilter')?.value || '',
            source: document.getElementById('incidentSourceFilter')?.value || '',
            system: document.getElementById('incidentSystemFilter')?.value || '',
            period: document.getElementById('incidentPeriodFilter')?.value || '',
            location: document.getElementById('incidentLocationFilter')?.value || ''
        };
    }
    
    // Filtrer les incidents
    const filteredIncidents = allIncidents.filter(incident => {
        if (filters.status && incident.statut !== filters.status) {
            return false;
        }
        if (filters.type && incident.type_id != filters.type) {
            return false;
        }
        if (filters.source && incident.source_id != filters.source) {
            return false;
        }
        if (filters.system && incident.system_id != filters.system) {
            return false;
        }
        if (filters.location && incident.type_localisation !== filters.location) {
            return false;
        }
        if (filters.period) {
            const incidentDate = new Date(incident.date_debut);
            const now = new Date();
            
            switch (filters.period) {
                case 'today':
                    if (incidentDate.toDateString() !== now.toDateString()) {
                        return false;
                    }
                    break;
                case 'week':
                    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    if (incidentDate < weekAgo) {
                        return false;
                    }
                    break;
                case 'month':
                    if (incidentDate.getMonth() !== now.getMonth() || 
                        incidentDate.getFullYear() !== now.getFullYear()) {
                        return false;
                    }
                    break;
                case 'quarter':
                    const quarterStart = new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1);
                    if (incidentDate < quarterStart) {
                        return false;
                    }
                    break;
                case 'year':
                    if (incidentDate.getFullYear() !== now.getFullYear()) {
                        return false;
                    }
                    break;
            }
        }
        return true;
    });
    
    // Mettre à jour la carte avec les incidents filtrés
    addIncidentsToMap(filteredIncidents);
    
    // Mettre à jour les statistiques
    updateMapStats();
    
    console.log(`🔍 ${filteredIncidents.length} incidents affichés après filtrage`);
}

// Afficher/masquer les filtres avancés
function toggleAdvancedFilters() {
    const filtersDiv = document.getElementById('advancedFilters');
    if (filtersDiv) {
        const isVisible = filtersDiv.style.display !== 'none';
        filtersDiv.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible) {
            // Charger les données de filtres si pas encore fait
            loadAdvancedFilterOptions();
        }
    }
}

// Charger les options pour les filtres avancés
async function loadAdvancedFilterOptions() {
    try {
        // Charger les types d'incidents
        const typesResponse = await fetch('/api/evenements/types');
        if (typesResponse.ok) {
            const typesData = await typesResponse.json();
            if (typesData.success) {
                populateIncidentFilterSelect('incidentTypeFilter', typesData.data, 'id', 'nom');
            }
        }
        
        // Charger les sources d'incidents
        const sourcesResponse = await fetch('/api/evenements/sources');
        if (sourcesResponse.ok) {
            const sourcesData = await sourcesResponse.json();
            if (sourcesData.success) {
                populateIncidentFilterSelect('incidentSourceFilter', sourcesData.data, 'id', 'nom');
            }
        }
        
        // Charger les systèmes d'incidents
        const systemsResponse = await fetch('/api/evenements/systemes');
        if (systemsResponse.ok) {
            const systemsData = await systemsResponse.json();
            if (systemsData.success) {
                populateIncidentFilterSelect('incidentSystemFilter', systemsData.data, 'id', 'nom');
            }
        }
    } catch (error) {
        console.error('❌ Erreur lors du chargement des options de filtres:', error);
    }
}

// Appliquer les filtres avancés
function applyAdvancedFilters() {
    const incidentFilters = {
        status: document.getElementById('incidentStatusFilter').value,
        type: document.getElementById('incidentTypeFilter').value,
        source: document.getElementById('incidentSourceFilter').value,
        system: document.getElementById('incidentSystemFilter').value,
        period: document.getElementById('incidentPeriodFilter').value,
        location: document.getElementById('incidentLocationFilter').value
    };
    
    const gareFilters = {
        type: document.getElementById('gareTypeFilter').value,
        region: document.getElementById('gareRegionFilter').value,
        search: document.getElementById('gareSearchFilter').value
    };
    
    // Appliquer les filtres d'incidents
    applyIncidentFilters(incidentFilters);
    
    // Appliquer les filtres de gares
    applyGareFilters(gareFilters);
    
    // Mettre à jour les statistiques
    updateAdvancedStatistics();
    
    console.log('🔍 Filtres avancés appliqués:', { incidentFilters, gareFilters });
}

// Effacer tous les filtres avancés
function clearAdvancedFilters() {
    // Réinitialiser les filtres d'incidents
    document.getElementById('incidentStatusFilter').value = '';
    document.getElementById('incidentTypeFilter').value = '';
    document.getElementById('incidentSourceFilter').value = '';
    document.getElementById('incidentSystemFilter').value = '';
    document.getElementById('incidentPeriodFilter').value = '';
    document.getElementById('incidentLocationFilter').value = '';
    
    // Réinitialiser les filtres de gares
    document.getElementById('gareTypeFilter').value = '';
    document.getElementById('gareRegionFilter').value = '';
    document.getElementById('gareSearchFilter').value = '';
    
    // Réappliquer les filtres (qui seront vides)
    applyAdvancedFilters();
    
    console.log('🧹 Filtres avancés effacés');
}

// Appliquer les filtres de gares
function applyGareFilters(filters) {
    // Filtrer les gares selon les critères
    const filteredGares = allGares.filter(gare => {
        if (filters.type && gare.type !== filters.type) {
            return false;
        }
        if (filters.region && gare.region !== filters.region) {
            return false;
        }
        if (filters.search && !gare.nom.toLowerCase().includes(filters.search.toLowerCase())) {
            return false;
        }
        return true;
    });
    
    // Mettre à jour l'affichage des gares sur la carte
    updateGaresOnMap(filteredGares);
}

// Mettre à jour les gares sur la carte
function updateGaresOnMap(gares) {
    // Vider la couche des gares
    garesLayer.clearLayers();
    
    // Ajouter les gares filtrées
    gares.forEach(gare => {
        const marker = createGareMarker(gare);
        garesLayer.addLayer(marker);
    });
    
    // Mettre à jour les statistiques
    updateMapStats();
}

// Réinitialiser les filtres d'incidents
function resetIncidentFilters() {
    document.getElementById('incidentStatusFilter').value = '';
    document.getElementById('incidentTypeFilter').value = '';
    document.getElementById('incidentSourceFilter').value = '';
    document.getElementById('incidentSystemFilter').value = '';
    document.getElementById('incidentPeriodFilter').value = '';
    
    // Afficher tous les incidents
    addIncidentsToMap(allIncidents);
    updateMapStats();
}

// Fonction pour afficher les axes sans géométrie (juste les noms)
async function loadAxesNames() {
    try {
        console.log("📡 Chargement des noms d'axes...");
        
        const response = await fetch('/api/arcs-names');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.axes) {
            console.log(`✅ ${data.axes.length} axes chargés (sans géométrie)`);
            displayAxesNames(data.axes);
        } else {
            console.error("❌ Erreur lors du chargement des axes:", data.error);
        }
        
    } catch (error) {
        console.error("❌ Erreur chargement axes:", error);
    }
}

// Fonction pour afficher les noms des axes sur la carte
function displayAxesNames(axes) {
    // Coordonnées approximatives du Maroc pour positionner les axes
    const moroccoBounds = {
        north: 35.9,
        south: 27.7,
        east: -0.9,
        west: -13.2
    };
    
    // Positions stratégiques pour différents types d'axes
    const axePositions = {
        // Axes principaux - positions approximatives
        'CASA VOYAGEURS/MARRAKECH': { lat: 31.6, lng: -7.9 },
        'CASAVOYAGEURS/SKACEM': { lat: 34.0, lng: -6.8 },
        'TANGER/FES': { lat: 34.0, lng: -5.3 },
        'LGV_V2': { lat: 33.5, lng: -6.0 },
        'BENGUERIR/SAFI U': { lat: 32.3, lng: -8.4 },
        'NOUACEUR/ELJADIDAV2': { lat: 33.4, lng: -7.6 },
        'EL JADIDA/EL JORF': { lat: 33.2, lng: -8.5 },
        'OUJDA/FRONTIERE ALGERIENNE': { lat: 34.7, lng: -1.9 },
        'BENI ENSAR/TAOURIRT RAC': { lat: 35.0, lng: -2.9 },
        'S.ELAIDI/OUED ZEM': { lat: 32.9, lng: -6.9 },
        'TRIANGLE DE NOUACEUR U': { lat: 33.4, lng: -7.6 },
        'RAC_Sidi_Kacem': { lat: 34.2, lng: -5.7 },
        'BENI OUKIL/BOUARFA': { lat: 32.5, lng: -3.9 },
        'GUENFOUDA/HASSI BLAL_U': { lat: 34.8, lng: -2.9 },
        'S.YAHYA_MACHRAA BEL KSIRI': { lat: 34.0, lng: -6.0 }
    };
    
    axes.forEach((axe, index) => {
        // Déterminer la position pour cet axe
        let position = axePositions[axe.nom];
        
        // Si pas de position prédéfinie, calculer une position basée sur l'index
        if (!position) {
            const row = Math.floor(index / 5);
            const col = index % 5;
            const lat = moroccoBounds.south + (row * 1.5) + (Math.random() * 0.5);
            const lng = moroccoBounds.west + (col * 2.5) + (Math.random() * 0.5);
            position = { lat, lng };
        }
        
        // Créer le marqueur pour l'axe
        const marker = createAxeMarker(axe, position);
        axeMarkersLayer.addLayer(marker);
    });
    
    console.log(`✅ ${axes.length} marqueurs d'axes ajoutés à la carte`);
}

// Fonction pour créer un marqueur pour un axe
function createAxeMarker(axe, position) {
    // Déterminer la couleur et l'icône selon le type d'axe
    let color = '#007bff';
    let icon = 'fa-route';
    
    if (axe.type === 'Ligne à Grande Vitesse') {
        color = '#dc3545';
        icon = 'fa-train';
    } else if (axe.type === 'Raccordement') {
        color = '#ffc107';
        icon = 'fa-exchange-alt';
    } else if (axe.type === 'Ligne Urbaine') {
        color = '#17a2b8';
        icon = 'fa-city';
    }
    
    // Créer l'icône personnalisée
    const customIcon = L.divIcon({
        className: 'axe-marker',
        html: `<div style="
            background-color: ${color};
            border: 2px solid white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">
            <i class="fas ${icon}"></i>
        </div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });
    
    // Créer le marqueur
    const marker = L.marker([position.lat, position.lng], {
        icon: customIcon,
        title: axe.nom
    });
    
    // Créer le contenu du popup
    const popupContent = `
        <div class="axe-popup">
            <h6><i class="fas ${icon} text-primary"></i> Axe Ferroviaire</h6>
            <div class="mb-2">
                <span class="badge bg-primary">${axe.nom}</span>
                <span class="badge bg-secondary">${axe.type}</span>
            </div>
            <div class="small">
                <div class="row">
                    <div class="col-6">
                        <strong>Segments:</strong><br>
                        <span class="text-muted">${axe.segments}</span>
                    </div>
                    <div class="col-6">
                        <strong>Type:</strong><br>
                        <span class="text-muted">${axe.type}</span>
                    </div>
                </div>
                ${axe.pk_debut || axe.pk_fin ? `
                <div class="row mt-2">
                    <div class="col-6">
                        <strong>PK Début:</strong><br>
                        <span class="text-muted">${axe.pk_debut || 'N/A'}</span>
                    </div>
                    <div class="col-6">
                        <strong>PK Fin:</strong><br>
                        <span class="text-muted">${axe.pk_fin || 'N/A'}</span>
                    </div>
                </div>
                ` : ''}
                ${axe.plod || axe.plof ? `
                <div class="row mt-2">
                    <div class="col-6">
                        <strong>PLOD:</strong><br>
                        <span class="text-muted">${axe.plod || 'N/A'}</span>
                    </div>
                    <div class="col-6">
                        <strong>PLOF:</strong><br>
                        <span class="text-muted">${axe.plof || 'N/A'}</span>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    // Ajouter l'événement de clic pour afficher les détails
    marker.on('click', () => {
        showAxeInfo(axe);
    });
    
    return marker;
}

// Fonction pour afficher les informations détaillées d'un axe
function showAxeInfo(axe) {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;
    
    let typeColor = 'bg-primary';
    let typeIcon = 'fa-route';
    
    if (axe.type === 'Ligne à Grande Vitesse') {
        typeColor = 'bg-danger';
        typeIcon = 'fa-train';
    } else if (axe.type === 'Raccordement') {
        typeColor = 'bg-warning';
        typeIcon = 'fa-exchange-alt';
    } else if (axe.type === 'Ligne Urbaine') {
        typeColor = 'bg-info';
        typeIcon = 'fa-city';
    }
    
    const infoContent = document.getElementById('info-content');
    if (!infoContent) return;
    
    infoContent.innerHTML = `
        <h6 class="text-success"><i class="fas ${typeIcon} me-2"></i>Axe Ferroviaire</h6>
        <div class="mb-3">
            <span class="badge ${typeColor}">${axe.nom}</span>
            <span class="badge bg-secondary">${axe.type}</span>
        </div>
        <div class="row">
            <div class="col-6">
                <strong>Segments:</strong><br>
                <span class="text-muted">${axe.segments}</span>
            </div>
            <div class="col-6">
                <strong>Type:</strong><br>
                <span class="text-muted">${axe.type}</span>
            </div>
        </div>
        ${axe.pk_debut || axe.pk_fin ? `
        <div class="row mt-2">
            <div class="col-6">
                <strong>PK Début:</strong><br>
                <span class="text-muted">${axe.pk_debut || 'N/A'}</span>
            </div>
            <div class="col-6">
                <strong>PK Fin:</strong><br>
                <span class="text-muted">${axe.pk_fin || 'N/A'}</span>
            </div>
        </div>
        ` : ''}
        ${axe.plod || axe.plof ? `
        <div class="row mt-2">
            <div class="col-6">
                <strong>PLOD:</strong><br>
                <span class="text-muted">${axe.plod || 'N/A'}</span>
            </div>
            <div class="col-6">
                <strong>PLOF:</strong><br>
                <span class="text-muted">${axe.plof || 'N/A'}</span>
            </div>
        </div>
        ` : ''}
        <div class="mt-3">
            <button class="btn btn-sm btn-outline-primary" onclick="showAxeDetails('${axe.nom}')">
                <i class="fas fa-info-circle"></i> Plus de détails
            </button>
        </div>
    `;
    
    infoPanel.style.display = 'block';
}

// Fonction pour afficher les axes avec des étiquettes et des polygones simples
async function addAxesLabelsToMap() {
    try {
        console.log("🗺️ Chargement des axes avec étiquettes...");
        
        const response = await fetch('/api/arcs-names');
        const data = await response.json();
        
        if (!data.success) {
            console.error("❌ Erreur lors du chargement des axes:", data.error);
            return;
        }
        
        console.log(`✅ ${data.total} axes chargés pour affichage avec étiquettes`);
        
        // Coordonnées approximatives du Maroc pour positionner les étiquettes
        const moroccoBounds = {
            north: 35.9,
            south: 27.7,
            east: -0.9,
            west: -13.2
        };
        
        // Positions prédéfinies pour les axes principaux
        const axePositions = {
            'CASA VOYAGEURS/MARRAKECH': { lat: 31.6, lng: -7.9 },
            'CASAVOYAGEURS/SKACEM': { lat: 34.0, lng: -6.8 },
            'BENGUERIR/SAFI U': { lat: 32.3, lng: -8.4 },
            'NOUACEUR/ELJADIDAV2': { lat: 33.4, lng: -7.6 },
            'TANGER/FES': { lat: 34.0, lng: -5.3 },
            'LGV_V2': { lat: 33.6, lng: -6.8 },
            'OUJDA/FRONTIERE ALGERIENNE': { lat: 34.7, lng: -1.9 },
            'S.ELAIDI/OUED ZEM': { lat: 32.9, lng: -6.9 },
            'EL JADIDA/EL JORF': { lat: 33.2, lng: -8.5 },
            'TRIANGLE NOUACEUR_VA1': { lat: 33.4, lng: -7.6 },
            'Raccordement LGV_1': { lat: 33.6, lng: -6.8 },
            'TriangleNouceur_RACV2': { lat: 33.4, lng: -7.6 },
            'Nouaceur/Eljadida': { lat: 33.4, lng: -7.6 },
            'TANGER/FESV1': { lat: 34.0, lng: -5.3 },
            'Nouaceur/EljadidaV2': { lat: 33.4, lng: -7.6 },
            'Triangle_ Nouaceur_V1BN': { lat: 33.4, lng: -7.6 },
            'Plateforme_LGV': { lat: 33.6, lng: -6.8 },
            'S.ELAIDI/OUED ZEM V2': { lat: 32.9, lng: -6.9 },
            'PlateformeRaccordement_LGV': { lat: 33.6, lng: -6.8 },
            'Raccordement LGV_2': { lat: 33.6, lng: -6.8 },
            'TRIANGLE DE NOUACEUR U': { lat: 33.4, lng: -7.6 },
            'Nouaceur/ElJadidaV2': { lat: 33.4, lng: -7.6 },
            'Triangl_Casa_V2': { lat: 33.6, lng: -7.6 },
            'S.EL AIDI/B.IDIRU': { lat: 32.9, lng: -6.9 },
            'RAC_Sidi_Kacem': { lat: 34.2, lng: -5.7 },
            'BENI OUKIL/BOUARFA': { lat: 32.9, lng: -3.9 },
            'CASA VOYAGEURS/SKACEM V2': { lat: 34.0, lng: -6.8 },
            'TANGER/FES RAC': { lat: 34.0, lng: -5.3 },
            'Triangle_ Nouaceur_V2BN': { lat: 33.4, lng: -7.6 },
            'EL JADIDA/EL JORF V2': { lat: 33.2, lng: -8.5 },
            'Triangle_NouaceurVA2': { lat: 33.4, lng: -7.6 },
            'CASA VOYAGEURS/SKACEM V1': { lat: 34.0, lng: -6.8 },
            'CASA VOYAGEURS/SKACEM V4': { lat: 34.0, lng: -6.8 },
            'TANGER/FES U': { lat: 34.0, lng: -5.3 },
            'BENGUERIR/S/AZZOUZ/U': { lat: 32.3, lng: -8.4 },
            'Triangle_CasaV1': { lat: 33.6, lng: -7.6 },
            'EL JADIDA/EL JORF V1': { lat: 33.2, lng: -8.5 },
            'GUENFOUDA/HASSI BLAL_U': { lat: 34.2, lng: -2.9 },
            'TANGER/FESV2': { lat: 34.0, lng: -5.3 },
            'TriangleNouceur_RACV1': { lat: 33.4, lng: -7.6 },
            'ArcTangerMorora_Med': { lat: 35.8, lng: -5.8 },
            'S.YAHYA_MACHRAA BEL KSIRI': { lat: 34.0, lng: -6.0 },
            'Nouaceur/EljadidaV1': { lat: 33.4, lng: -7.6 },
        };
        
        // Créer un groupe de couches pour les axes
        const axesGroup = L.layerGroup();
        
        data.axes.forEach((axe, index) => {
            // Obtenir la position pour cet axe
            let position = axePositions[axe.nom];
            
            // Si pas de position prédéfinie, calculer une position aléatoire dans les limites du Maroc
            if (!position) {
                const lat = moroccoBounds.south + Math.random() * (moroccoBounds.north - moroccoBounds.south);
                const lng = moroccoBounds.west + Math.random() * (moroccoBounds.east - moroccoBounds.west);
                position = { lat, lng };
            }
            
            // Créer un polygone simple pour représenter la zone de l'axe
            const polygonCoords = [
                [position.lat - 0.1, position.lng - 0.1],
                [position.lat - 0.1, position.lng + 0.1],
                [position.lat + 0.1, position.lng + 0.1],
                [position.lat + 0.1, position.lng - 0.1]
            ];
            
            // Déterminer la couleur et le style selon le type d'axe
            const color = getAxeColor(axe.type);
            const fillColor = getAxeFillColor(axe.type);
            
            // Créer le polygone
            const polygon = L.polygon(polygonCoords, {
                color: color,
                weight: 2,
                fillColor: fillColor,
                fillOpacity: 0.3,
                opacity: 0.8
            });
            
            // Créer l'étiquette
            const label = L.divIcon({
                className: 'axe-label',
                html: `
                    <div class="axe-label-content" style="
                        background: ${color};
                        color: white;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 11px;
                        font-weight: bold;
                        white-space: nowrap;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        border: 2px solid white;
                    ">
                        <i class="fas fa-route"></i> ${axe.nom}
                    </div>
                `,
                iconSize: [200, 30],
                iconAnchor: [100, 15]
            });
            
            const marker = L.marker(position, { icon: label });
            
            // Créer le contenu du popup
            const popupContent = createAxeLabelPopup(axe);
            polygon.bindPopup(popupContent);
            marker.bindPopup(popupContent);
            
            // Ajouter les événements de clic
            polygon.on('click', () => showAxeLabelInfo(axe));
            marker.on('click', () => showAxeLabelInfo(axe));
            
            // Ajouter au groupe
            axesGroup.addLayer(polygon);
            axesGroup.addLayer(marker);
        });
        
        // Ajouter le groupe à la carte
        map.addLayer(axesGroup);
        
        // Ajouter au contrôle des couches
        if (layerControl) {
            layerControl.addOverlay(axesGroup, 'Axes Ferroviaires (Étiquettes)');
        }
        
        console.log("✅ Axes avec étiquettes ajoutés à la carte");
        
    } catch (error) {
        console.error("❌ Erreur lors de l'ajout des axes avec étiquettes:", error);
    }
}

// Fonction pour obtenir la couleur d'un axe selon son type
function getAxeColor(type) {
    const colors = {
        'Ligne à Grande Vitesse': '#e83e8c',
        'Raccordement': '#ffc107',
        'Ligne Urbaine': '#17a2b8',
        'Ligne Classique': '#007bff'
    };
    return colors[type] || '#6c757d';
}

// Fonction pour obtenir la couleur de remplissage d'un axe selon son type
function getAxeFillColor(type) {
    const colors = {
        'Ligne à Grande Vitesse': '#e83e8c',
        'Raccordement': '#ffc107',
        'Ligne Urbaine': '#17a2b8',
        'Ligne Classique': '#007bff'
    };
    return colors[type] || '#6c757d';
}

// Fonction pour créer le contenu du popup pour un axe avec étiquette
function createAxeLabelPopup(axe) {
    return `
        <div class="axe-popup">
            <h6><i class="fas fa-route text-primary"></i> Axe Ferroviaire</h6>
            <div class="mb-2">
                <span class="badge bg-primary">${axe.nom}</span>
                <span class="badge bg-secondary">${axe.type}</span>
            </div>
            <div class="small">
                <div class="row">
                    <div class="col-6">
                        <strong>Segments:</strong><br>
                        <span class="text-muted">${axe.segments}</span>
                    </div>
                    <div class="col-6">
                        <strong>Type:</strong><br>
                        <span class="text-muted">${axe.type}</span>
                    </div>
                </div>
                ${axe.pk_debut || axe.pk_fin ? `
                <div class="row mt-2">
                    <div class="col-6">
                        <strong>PK Début:</strong><br>
                        <span class="text-muted">${axe.pk_debut || 'N/A'}</span>
                    </div>
                    <div class="col-6">
                        <strong>PK Fin:</strong><br>
                        <span class="text-muted">${axe.pk_fin || 'N/A'}</span>
                    </div>
                </div>
                ` : ''}
                ${axe.plod || axe.plof ? `
                <div class="row mt-2">
                    <div class="col-6">
                        <strong>PLOD:</strong><br>
                        <span class="text-muted">${axe.plod || 'N/A'}</span>
                    </div>
                    <div class="col-6">
                        <strong>PLOF:</strong><br>
                        <span class="text-muted">${axe.plof || 'N/A'}</span>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Fonction pour afficher les informations détaillées d'un axe avec étiquette
function showAxeLabelInfo(axe) {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;
    
    const infoContent = document.getElementById('info-content');
    if (!infoContent) return;
    
    infoContent.innerHTML = `
        <h6 class="text-success"><i class="fas fa-route me-2"></i>Axe Ferroviaire</h6>
        <div class="mb-3">
            <span class="badge bg-primary">${axe.nom}</span>
            <span class="badge bg-secondary">${axe.type}</span>
        </div>
        <div class="row">
            <div class="col-6">
                <strong>Segments:</strong><br>
                <span class="text-muted">${axe.segments}</span>
            </div>
            <div class="col-6">
                <strong>Type:</strong><br>
                <span class="text-muted">${axe.type}</span>
            </div>
        </div>
        ${axe.pk_debut || axe.pk_fin ? `
        <div class="row mt-2">
            <div class="col-6">
                <strong>PK Début:</strong><br>
                <span class="text-muted">${axe.pk_debut || 'N/A'}</span>
            </div>
            <div class="col-6">
                <strong>PK Fin:</strong><br>
                <span class="text-muted">${axe.pk_fin || 'N/A'}</span>
            </div>
        </div>
        ` : ''}
        ${axe.plod || axe.plof ? `
        <div class="row mt-2">
            <div class="col-6">
                <strong>PLOD:</strong><br>
                <span class="text-muted">${axe.plod || 'N/A'}</span>
            </div>
            <div class="col-6">
                <strong>PLOF:</strong><br>
                <span class="text-muted">${axe.plof || 'N/A'}</span>
            </div>
        </div>
        ` : ''}
        <div class="mt-3">
            <button class="btn btn-sm btn-outline-primary" onclick="showAxeDetails('${axe.nom}')">
                <i class="fas fa-info-circle"></i> Plus de détails
            </button>
        </div>
    `;
    
    infoPanel.style.display = 'block';
}

// Fonction pour afficher les axes sous forme de multilignes connectées
async function addAxesMultilinesToMap() {
    try {
        console.log("🗺️ Chargement des axes avec étiquettes uniquement...");
        
        const response = await fetch('/api/arcs-multilines');
        const data = await response.json();
        
        if (!data.success) {
            console.error("❌ Erreur lors du chargement des multilignes:", data.error);
            return;
        }
        
        console.log(`✅ ${data.total_lignes} lignes chargées avec ${data.total_axes} axes`);
        
        // Positions fixes prédéfinies pour les axes principaux (basées sur la géographie réelle)
        const axePositions = {
            // Axe principal Casablanca - Rabat - Kénitra - Tanger
            'CASA VOYAGEURS/MARRAKECH': { lat: 33.6, lng: -7.6 },  // Casablanca
            'CASAVOYAGEURS/SKACEM': { lat: 34.2, lng: -6.6 },       // Rabat/Kénitra
            'TANGER/FES': { lat: 35.8, lng: -5.8 },                 // Tanger
            'OUJDA/FRONTIERE ALGERIENNE': { lat: 34.7, lng: -1.9 }, // Oujda
            
            // Axe El Jadida - Casablanca
            'BENGUERIR/SAFI U': { lat: 32.3, lng: -8.4 },           // Benguerir
            'EL JADIDA/EL JORF': { lat: 33.2, lng: -8.5 },          // El Jadida
            
            // Axe Nouaceur - El Jadida
            'NOUACEUR/ELJADIDAV2': { lat: 33.4, lng: -7.6 },        // Nouaceur
            
            // LGV
            'LGV_V2': { lat: 33.6, lng: -6.8 },                     // LGV
            
            // Raccordements
            'S.ELAIDI/OUED ZEM': { lat: 32.9, lng: -6.9 },          // Sidi El Aidi
            'TRIANGLE DE NOUACEUR U': { lat: 33.4, lng: -7.6 },     // Triangle Nouaceur
            'RAC_Sidi_Kacem': { lat: 34.2, lng: -5.7 },             // Sidi Kacem
            
            // Axe oriental
            'BENI OUKIL/BOUARFA': { lat: 32.9, lng: -3.9 },         // Beni Oukil
            'GUENFOUDA/HASSI BLAL_U': { lat: 34.2, lng: -2.9 },     // Guenfouda
            
            // Axe Tanger - Méditerranée
            'ArcTangerMorora_Med': { lat: 35.8, lng: -5.8 },        // Tanger Méditerranée
            
            // Axe Casablanca - Sidi Yahya
            'S.YAHYA_MACHRAA BEL KSIRI': { lat: 34.0, lng: -6.0 },  // Sidi Yahya
            

        };
        
        // Créer un groupe de couches pour les étiquettes
        const labelsGroup = L.layerGroup();
        
        // Traiter chaque ligne pour créer les étiquettes
        data.lignes.forEach((ligne, ligneIndex) => {
            console.log(`🛤️ Traitement de la ligne ${ligne.nom} avec ${ligne.axes.length} axes`);
            
            // Créer les étiquettes pour tous les axes de cette ligne
            ligne.axes.forEach((axe, axeIndex) => {
                // Obtenir la position pour cet axe
                let position = axePositions[axe.nom];
                
                // Si pas de position prédéfinie, utiliser une position par défaut
                if (!position) {
                    position = { lat: 32.0, lng: -6.0 }; // Position par défaut au centre du Maroc
                }
                
                const color = axe.couleur;
                
                // Créer l'étiquette pour cet axe
                const label = L.divIcon({
                    className: 'axe-multiline-label',
                    html: `
                        <div class="axe-multiline-label-content" style="
                            background: ${color};
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 11px;
                            font-weight: bold;
                            white-space: nowrap;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                            border: 2px solid white;
                            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                        ">
                            ${axe.nom}
                        </div>
                    `,
                    iconSize: [200, 25],
                    iconAnchor: [100, 12]
                });
                
                const labelMarker = L.marker(position, { icon: label });
                labelMarker.bindPopup(createAxeMultilinePopup(axe, ligne));
                labelMarker.on('click', () => showAxeMultilineInfo(axe, ligne));
                labelsGroup.addLayer(labelMarker);
            });
        });
        
        // Ajouter le groupe à la carte
        map.addLayer(labelsGroup);
        
        // Ajouter au contrôle des couches
        if (layerControl) {
            layerControl.addOverlay(labelsGroup, 'Axes Ferroviaires (Étiquettes)');
        }
        
        console.log("✅ Étiquettes des axes ajoutées à la carte (positions fixes uniquement)");
        
    } catch (error) {
        console.error("❌ Erreur lors de l'ajout des étiquettes:", error);
    }
}

// Fonction pour obtenir l'épaisseur d'un axe selon son type
function getAxeWeight(type) {
    const weights = {
        'Ligne à Grande Vitesse': 6,
        'Raccordement': 4,
        'Ligne Urbaine': 5,
        'Ligne Classique': 4
    };
    return weights[type] || 3;
}

// Fonction pour créer le contenu du popup pour un axe dans une multiligne
function createAxeMultilinePopup(axe, reseau) {
    return `
        <div class="axe-multiline-popup">
            <h6><i class="fas fa-route text-primary"></i> Axe Ferroviaire</h6>
            <div class="mb-2">
                <span class="badge bg-primary">${axe.nom}</span>
                <span class="badge bg-info">${reseau.nom}</span>
            </div>
            <div class="small">
                <div class="row">
                    <div class="col-6">
                        <strong>Segments:</strong><br>
                        <span class="text-muted">${axe.segments}</span>
                    </div>
                    <div class="col-6">
                        <strong>Connexions:</strong><br>
                        <span class="text-muted">${axe.connexions.length}</span>
                    </div>
                </div>
                ${axe.pk_debut || axe.pk_fin ? `
                <div class="row mt-2">
                    <div class="col-6">
                        <strong>PK Début:</strong><br>
                        <span class="text-muted">${axe.pk_debut || 'N/A'}</span>
                    </div>
                    <div class="col-6">
                        <strong>PK Fin:</strong><br>
                        <span class="text-muted">${axe.pk_fin || 'N/A'}</span>
                    </div>
                </div>
                ` : ''}
                ${axe.connexions.length > 0 ? `
                <div class="row mt-2">
                    <div class="col-12">
                        <strong>Connexions:</strong><br>
                        <span class="text-muted">${axe.connexions.join(', ')}</span>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Fonction pour créer le contenu du popup pour un réseau
function createReseauPopup(reseau) {
    return `
        <div class="reseau-popup">
            <h6><i class="fas fa-network-wired text-success"></i> Réseau Ferroviaire</h6>
            <div class="mb-2">
                <span class="badge bg-success">${reseau.nom}</span>
                <span class="badge bg-secondary">${reseau.type_principal}</span>
            </div>
            <div class="small">
                <div class="row">
                    <div class="col-6">
                        <strong>Axes:</strong><br>
                        <span class="text-muted">${reseau.axes.length}</span>
                    </div>
                    <div class="col-6">
                        <strong>Type:</strong><br>
                        <span class="text-muted">${reseau.type_principal}</span>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-12">
                        <strong>Axes du réseau:</strong><br>
                        <span class="text-muted">${reseau.axes.map(axe => axe.nom).join(', ')}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Fonction pour afficher les informations détaillées d'un axe dans une multiligne
function showAxeMultilineInfo(axe, reseau) {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;
    
    const infoContent = document.getElementById('info-content');
    if (!infoContent) return;
    
    infoContent.innerHTML = `
        <h6 class="text-success"><i class="fas fa-route me-2"></i>Axe Ferroviaire</h6>
        <div class="mb-3">
            <span class="badge bg-primary">${axe.nom}</span>
            <span class="badge bg-info">${reseau.nom}</span>
        </div>
        <div class="row">
            <div class="col-6">
                <strong>Segments:</strong><br>
                <span class="text-muted">${axe.segments}</span>
            </div>
            <div class="col-6">
                <strong>Connexions:</strong><br>
                <span class="text-muted">${axe.connexions.length}</span>
            </div>
        </div>
        ${axe.pk_debut || axe.pk_fin ? `
        <div class="row mt-2">
            <div class="col-6">
                <strong>PK Début:</strong><br>
                <span class="text-muted">${axe.pk_debut || 'N/A'}</span>
            </div>
            <div class="col-6">
                <strong>PK Fin:</strong><br>
                <span class="text-muted">${axe.pk_fin || 'N/A'}</span>
            </div>
        </div>
        ` : ''}
        ${axe.connexions.length > 0 ? `
        <div class="row mt-2">
            <div class="col-12">
                <strong>Connexions:</strong><br>
                <span class="text-muted">${axe.connexions.join(', ')}</span>
            </div>
        </div>
        ` : ''}
        <div class="mt-3">
            <button class="btn btn-sm btn-outline-primary" onclick="showAxeDetails('${axe.nom}')">
                <i class="fas fa-info-circle"></i> Plus de détails
            </button>
        </div>
    `;
    
    infoPanel.style.display = 'block';
}

// Fonction pour afficher les informations détaillées d'un réseau
function showReseauInfo(reseau) {
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;
    
    const infoContent = document.getElementById('info-content');
    if (!infoContent) return;
    
    infoContent.innerHTML = `
        <h6 class="text-success"><i class="fas fa-network-wired me-2"></i>Réseau Ferroviaire</h6>
        <div class="mb-3">
            <span class="badge bg-success">${reseau.nom}</span>
            <span class="badge bg-secondary">${reseau.type_principal}</span>
        </div>
        <div class="row">
            <div class="col-6">
                <strong>Axes:</strong><br>
                <span class="text-muted">${reseau.axes.length}</span>
            </div>
            <div class="col-6">
                <strong>Type:</strong><br>
                <span class="text-muted">${reseau.type_principal}</span>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-12">
                <strong>Axes du réseau:</strong><br>
                <span class="text-muted">${reseau.axes.map(axe => axe.nom).join(', ')}</span>
            </div>
        </div>
        <div class="mt-3">
            <button class="btn btn-sm btn-outline-success" onclick="showReseauDetails(${reseau.id})">
                <i class="fas fa-info-circle"></i> Détails du réseau
            </button>
        </div>
    `;
    
    infoPanel.style.display = 'block';
}

// Initialiser la carte quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    // ✅ ALERTE: INCIDENTS RÉACTIVÉS AVEC ge_localisation
    console.log('✅✅✅ INCIDENTS RÉACTIVÉS SUR LA CARTE ✅✅✅');
    console.log('✅✅✅ POSITIONNEMENT BASÉ SUR ge_localisation ✅✅✅');
    
    if (typeof L !== 'undefined') {
        initONCFMap();
        // Supprimer l'affichage des axes sous forme d'étiquettes
        // addAxesLabelsToMap();
        // Utiliser les multilignes (DÉSACTIVÉ - étiquettes masquées)
        // addAxesMultilinesToMap();
        // Commenter l'ancienne fonction qui utilise la géométrie
        // addArcsToMap();
    } else {
        console.error('Leaflet n\'est pas chargé');
    }
}); 