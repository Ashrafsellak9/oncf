/**
 * Gestion des Gares - ONCF GIS
 * JavaScript pour la page de gestion des gares
 */

// Variables globales
let allGares = [];
let filteredGares = [];
let currentPage = 1;
let itemsPerPage = 25;
let gareFilters = {
    sections: [],
    types: [],
    etats: [],
    regions: [],
    villes: []
};
let selectedGare = null;
let isEditing = false;
let activeFilters = {};
let filterTimeout = null;

// Configuration API
const API_BASE = '/api';

/**
 * Initialisation de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏢 Initialisation de la page des gares');
    
    // Charger les données initiales
    Promise.all([
        loadGares(),
        loadGareFilters(),
        loadStatistics()
    ]).then(() => {
        console.log('✅ Toutes les données des gares chargées');
        setupEventListeners();
        renderGares();
    }).catch(error => {
        console.error('❌ Erreur lors du chargement des données:', error);
        showNotification('Erreur lors du chargement des données', 'error');
    });
});

/**
 * Configuration des écouteurs d'événements
 */
function setupEventListeners() {
    // Filtres en temps réel avec debounce
    document.getElementById('searchGares').addEventListener('input', debounce(applyFilters, 300));
    document.getElementById('filterSection').addEventListener('change', applyFilters);
    document.getElementById('filterType').addEventListener('change', applyFilters);
    document.getElementById('filterEtat').addEventListener('change', applyFilters);
    document.getElementById('filterRegion').addEventListener('change', applyFilters);
    document.getElementById('filterVille').addEventListener('change', applyFilters);
    document.getElementById('pageSize').addEventListener('change', changePageSize);
    
    // Boutons de filtrage rapide
    setupQuickFilters();
    
    // Actualisation automatique toutes les 10 minutes
    setInterval(refreshGares, 10 * 60 * 1000);
}

/**
 * Charger les gares depuis l'API
 */
async function loadGares(page = 1, filters = {}) {
    showLoading(true);
    
    try {
        const params = new URLSearchParams({
            page: page,
            per_page: itemsPerPage,
            ...filters
        });
        
        const response = await fetch(`${API_BASE}/gares?${params}`);
        const data = await response.json();
        
        if (data.success) {
            allGares = data.data;
            filteredGares = [...allGares];
            
            // Mettre à jour la pagination
            if (data.pagination) {
                updatePagination(data.pagination);
            }
            
            // Mettre à jour le nombre de gares filtrées
            updateGareStatistics();
            
            console.log(`✅ ${allGares.length} gares chargées`);
            return data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('❌ Erreur chargement gares:', error);
        showNotification('Erreur lors du chargement des gares', 'error');
        return { data: [], pagination: { total: 0, pages: 0 } };
    } finally {
        showLoading(false);
    }
}

/**
 * Charger les options de filtrage pour les gares
 */
async function loadGareFilters() {
    try {
        const response = await fetch(`${API_BASE}/gares/filters`);
        const data = await response.json();
        
        if (data.success) {
            gareFilters = data.data;
            
            // Extraire les options uniques depuis toutes les gares
            extractUniqueFilterOptions();
            
            populateFilterOptions();
            console.log('✅ Options de filtrage chargées');
        }
    } catch (error) {
        console.error('❌ Erreur chargement filtres:', error);
    }
}

/**
 * Extraire les options uniques pour les filtres
 */
function extractUniqueFilterOptions() {
    if (allGares.length === 0) return;
    
    const sections = new Set();
    const types = new Set();
    const etats = new Set();
    const regions = new Set();
    const villes = new Set();
    
    allGares.forEach(gare => {
        if (gare.section) sections.add(gare.section);
        if (gare.type) types.add(gare.type);
        if (gare.etat) etats.add(gare.etat);
        if (gare.region) regions.add(gare.region);
        if (gare.ville) villes.add(gare.ville);
    });
    
    // Mettre à jour les filtres avec les nouvelles options
    gareFilters.sections = Array.from(sections).sort();
    gareFilters.types = Array.from(types).sort();
    gareFilters.etats = Array.from(etats).sort();
    gareFilters.regions = Array.from(regions).sort();
    gareFilters.villes = Array.from(villes).sort();
}

/**
 * Charger les statistiques
 */
async function loadStatistics() {
    try {
        // Récupérer les statistiques depuis l'API
        const response = await fetch(`${API_BASE}/gares/stats`);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.data;
            
            // Mettre à jour l'affichage avec les vraies statistiques
            document.getElementById('totalGaresCount').textContent = stats.total_gares || 0;
            document.getElementById('activeGaresCount').textContent = stats.active_gares || 0;
            document.getElementById('passiveGaresCount').textContent = stats.passive_gares || 0;
            
            console.log(`📊 Statistiques globales: Total=${stats.total_gares}, Actives=${stats.active_gares}, Passives=${stats.passive_gares}`);
        } else {
            console.error('❌ Erreur API statistiques:', data.error);
            // Fallback: calculer à partir des données locales
            updateGareStatistics();
        }
    } catch (error) {
        console.error('❌ Erreur chargement statistiques:', error);
        // Fallback: calculer à partir des données locales
        updateGareStatistics();
    }
}

/**
 * Mettre à jour les statistiques des gares filtrées
 */
function updateGareStatistics() {
    // Cette fonction met à jour seulement le nombre de gares filtrées
    // Les statistiques globales sont gérées par loadStatistics()
    
    const filteredCount = filteredGares ? filteredGares.length : 0;
    document.getElementById('filteredGaresCount').textContent = filteredCount;
    
    console.log(`📊 Gares filtrées: ${filteredCount}`);
}

/**
 * Peupler les options de filtrage
 */
function populateFilterOptions() {
    // Sections
    const sectionSelect = document.getElementById('filterSection');
    if (sectionSelect) {
        sectionSelect.innerHTML = '<option value="">Toutes les sections</option>';
        gareFilters.sections.forEach(section => {
            const option = document.createElement('option');
            option.value = section;
            option.textContent = section;
            sectionSelect.appendChild(option);
        });
    }
    
    // Types
    const typeSelect = document.getElementById('filterType');
    if (typeSelect) {
        typeSelect.innerHTML = '<option value="">Tous les types</option>';
        gareFilters.types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeSelect.appendChild(option);
        });
    }
    
    // États
    const etatSelect = document.getElementById('filterEtat');
    if (etatSelect) {
        etatSelect.innerHTML = '<option value="">Tous les états</option>';
        gareFilters.etats.forEach(etat => {
            const option = document.createElement('option');
            option.value = etat;
            option.textContent = etat;
            etatSelect.appendChild(option);
        });
    }
    
    // Régions
    const regionSelect = document.getElementById('filterRegion');
    if (regionSelect) {
        regionSelect.innerHTML = '<option value="">Toutes les régions</option>';
        gareFilters.regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            regionSelect.appendChild(option);
        });
    }
    
    // Villes
    const villeSelect = document.getElementById('filterVille');
    if (villeSelect) {
        villeSelect.innerHTML = '<option value="">Toutes les villes</option>';
        gareFilters.villes.forEach(ville => {
            const option = document.createElement('option');
            option.value = ville;
            option.textContent = ville;
            villeSelect.appendChild(option);
        });
    }
}

/**
 * Appliquer les filtres
 */
async function applyFilters() {
    // Annuler le timeout précédent
    if (filterTimeout) {
        clearTimeout(filterTimeout);
    }
    
    // Appliquer les filtres avec un délai pour éviter trop de requêtes
    filterTimeout = setTimeout(async () => {
        const search = document.getElementById('searchGares')?.value || '';
        const section = document.getElementById('filterSection')?.value || '';
        const type = document.getElementById('filterType')?.value || '';
        const etat = document.getElementById('filterEtat')?.value || '';
        const region = document.getElementById('filterRegion')?.value || '';
        const ville = document.getElementById('filterVille')?.value || '';
        
        // Construire l'objet des filtres actifs
        activeFilters = {};
        if (search) activeFilters.search = search;
        if (section) activeFilters.section = section;
        if (type) activeFilters.type = type;
        if (etat) activeFilters.etat = etat;
        if (region) activeFilters.region = region;
        if (ville) activeFilters.ville = ville;
        
        // Afficher les filtres actifs
        updateActiveFiltersDisplay();
        
        currentPage = 1;
        await loadGares(currentPage, activeFilters);
        renderGares();
        
        // Mettre à jour les statistiques après avoir appliqué les filtres
        updateGareStatistics();
        
        console.log(`🔍 Filtres appliqués: ${filteredGares.length} gares trouvées`);
        console.log('📋 Filtres actifs:', activeFilters);
    }, 300);
}

/**
 * Mettre à jour l'affichage des filtres actifs
 */
function updateActiveFiltersDisplay() {
    const activeFiltersContainer = document.getElementById('activeFiltersContainer');
    if (!activeFiltersContainer) return;
    
    const activeFiltersList = Object.entries(activeFilters)
        .filter(([key, value]) => value && value.trim() !== '')
        .map(([key, value]) => ({
            key: key,
            value: value,
            label: getFilterLabel(key, value)
        }));
    
    if (activeFiltersList.length === 0) {
        activeFiltersContainer.innerHTML = '';
        return;
    }
    
    let html = '<div class="d-flex flex-wrap gap-2 align-items-center">';
    html += '<span class="text-muted small">Filtres actifs:</span>';
    
    activeFiltersList.forEach(filter => {
        html += `
            <span class="badge bg-primary d-flex align-items-center gap-1">
                ${filter.label}
                <button type="button" class="btn-close btn-close-white" 
                        onclick="removeFilter('${filter.key}')" 
                        style="font-size: 0.5rem;"></button>
            </span>
        `;
    });
    
    html += `
        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="clearAllFilters()">
            <i class="fas fa-times"></i> Effacer tout
        </button>
    `;
    
    html += '</div>';
    activeFiltersContainer.innerHTML = html;
}

/**
 * Obtenir le label d'un filtre
 */
function getFilterLabel(key, value) {
    const labels = {
        search: `Recherche: "${value}"`,
        section: `Section: ${value}`,
        type: `Type: ${value}`,
        etat: `État: ${value}`,
        region: `Région: ${value}`,
        ville: `Ville: ${value}`
    };
    return labels[key] || `${key}: ${value}`;
}

/**
 * Supprimer un filtre spécifique
 */
function removeFilter(filterKey) {
    const element = document.getElementById(`filter${filterKey.charAt(0).toUpperCase() + filterKey.slice(1)}`);
    if (element) {
        element.value = '';
    }
    applyFilters();
}

/**
 * Effacer tous les filtres
 */
function clearAllFilters() {
    const filterElements = [
        'searchGares',
        'filterSection',
        'filterType',
        'filterEtat',
        'filterRegion',
        'filterVille'
    ];
    
    filterElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.value = '';
        }
    });
    
    applyFilters();
}

/**
 * Réinitialiser les filtres
 */
function resetFilters() {
    clearAllFilters();
    showNotification('Filtres réinitialisés', 'info');
}

/**
 * Configurer les filtres rapides
 */
function setupQuickFilters() {
    const quickFiltersContainer = document.getElementById('quickFiltersContainer');
    if (!quickFiltersContainer) return;
    
    const quickFilters = [
        { label: 'Gares Actives', filter: { etat: 'ACTIVE' }, icon: 'fas fa-check-circle', color: 'success' },
        { label: 'Gares Passives', filter: { etat: 'PASSIVE' }, icon: 'fas fa-pause-circle', color: 'warning' },
        { label: 'Stations', filter: { type: 'STATION' }, icon: 'fas fa-building', color: 'primary' },
        { label: 'Haltes', filter: { type: 'Haltes' }, icon: 'fas fa-map-marker-alt', color: 'info' },
        { label: 'Casablanca', filter: { region: 'CASABLANCA' }, icon: 'fas fa-city', color: 'secondary' },
        { label: 'Rabat', filter: { region: 'RABAT' }, icon: 'fas fa-city', color: 'secondary' }
    ];
    
    let html = '<div class="d-flex flex-wrap gap-2">';
    html += '<span class="text-muted small me-2">Filtres rapides:</span>';
    
    quickFilters.forEach(quickFilter => {
        html += `
            <button type="button" class="btn btn-sm btn-outline-${quickFilter.color}" 
                    onclick="applyQuickFilter(${JSON.stringify(quickFilter.filter).replace(/"/g, '&quot;')})">
                <i class="${quickFilter.icon}"></i> ${quickFilter.label}
            </button>
        `;
    });
    
    html += '</div>';
    quickFiltersContainer.innerHTML = html;
}

/**
 * Appliquer un filtre rapide
 */
function applyQuickFilter(filter) {
    // Réinitialiser tous les filtres
    clearAllFilters();
    
    // Appliquer le filtre rapide
    Object.entries(filter).forEach(([key, value]) => {
        const element = document.getElementById(`filter${key.charAt(0).toUpperCase() + key.slice(1)}`);
        if (element) {
            element.value = value;
        }
    });
    
    applyFilters();
    showNotification('Filtre rapide appliqué', 'info');
}

/**
 * Afficher les gares
 */
function renderGares() {
    const tbody = document.getElementById('garesTableBody');
    tbody.innerHTML = '';
    
    if (filteredGares.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4>Aucune gare trouvée</h4>
                    <p class="text-muted">Essayez de modifier vos filtres de recherche</p>
                </td>
            </tr>
        `;
    } else {
        filteredGares.forEach(gare => {
            const row = createGareRow(gare);
            tbody.appendChild(row);
        });
    }
    
    // Mettre à jour les statistiques après avoir affiché les gares
    updateGareStatistics();
    updatePaginationInfo();
}

/**
 * Créer une ligne de gare
 */
function createGareRow(gare) {
    const row = document.createElement('tr');
    
    const statusClass = gare.etat === 'ACTIVE' ? 'active' : 'passive';
    const statusText = gare.etat === 'ACTIVE' ? 'Active' : 'Passive';
    const typeDisplay = getGareTypeName(gare.type);
    const villeDisplay = getVilleName(gare.ville);
    const regionDisplay = getRegionName(gare.region);
    
    row.innerHTML = `
        <td>
            <input type="checkbox" class="gare-checkbox" value="${gare.id}">
        </td>
        <td>
            <strong>${gare.nom || 'Sans nom'}</strong>
            <br><small class="text-muted">ID: ${gare.id}</small>
        </td>
        <td>${gare.code || 'N/A'}</td>
        <td>${typeDisplay}</td>
        <td>${regionDisplay}</td>
        <td>${villeDisplay}</td>
        <td>
            <span class="gare-status ${statusClass}"></span>
            ${statusText}
        </td>
        <td>
            <div class="action-buttons">
                <button class="btn btn-sm btn-outline-primary" onclick="showGareDetails(${gare.id})" title="Voir détails">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning" onclick="editGare(${gare.id})" title="Modifier">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteGare(${gare.id})" title="Supprimer">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    
    return row;
}

/**
 * Afficher les détails d'une gare
 */
function showGareDetails(gareId) {
    console.log('🔍 Affichage des détails de la gare:', gareId);
    
    // Afficher un indicateur de chargement
    const content = document.getElementById('gareModalContent');
    content.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-2">Chargement des détails...</p>
        </div>
    `;
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('gareDetailsModal'));
    modal.show();
    
    // Récupérer les détails complets depuis l'API
    fetch(`/api/gares/${gareId}/details`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const gare = data.data;
                selectedGare = gare;
                
                // Formater les détails pour l'affichage
                const gareFormatted = formatGareDetails(gare);
                
                content.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-info-circle me-2"></i>Informations générales</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>ID:</strong></td>
                                    <td><span class="badge bg-secondary">#${gare.id}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Nom:</strong></td>
                                    <td>${gare.nom || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Code Gare:</strong></td>
                                    <td><span class="badge bg-primary">${gare.code_gare || 'Non défini'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Type:</strong></td>
                                    <td>${gareFormatted.type_display}</td>
                                </tr>
                                <tr>
                                    <td><strong>Type Commercial:</strong></td>
                                    <td>${gare.type_commercial || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>État:</strong></td>
                                    <td>
                                        <span class="badge bg-${gare.etat === 'ACTIVE' ? 'success' : 'secondary'}">
                                            ${gareFormatted.etat_display}
                                        </span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Statut:</strong></td>
                                    <td>${gareFormatted.statut_display}</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-map-marker-alt me-2"></i>Localisation</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Région:</strong></td>
                                    <td>${gareFormatted.region_display}</td>
                                </tr>
                                <tr>
                                    <td><strong>Ville:</strong></td>
                                    <td>${gareFormatted.ville_display}</td>
                                </tr>
                                <tr>
                                    <td><strong>Section:</strong></td>
                                    <td>${gare.section || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>PK Début:</strong></td>
                                    <td>${gare.pk_debut || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Distance:</strong></td>
                                    <td>${gare.distance ? `${gare.distance} km` : 'Non définie'}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <h6><i class="fas fa-cogs me-2"></i>Paramètres techniques</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>PLOD:</strong></td>
                                    <td>${gare.plod || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>PLOF:</strong></td>
                                    <td>${gare.plof || 'Non défini'}</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-chart-bar me-2"></i>Statistiques</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Total Incidents:</strong></td>
                                    <td><span class="badge bg-info">${gare.statistiques.total_incidents}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Incidents Ouverts:</strong></td>
                                    <td><span class="badge bg-warning">${gare.statistiques.incidents_ouverts}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Incidents Fermés:</strong></td>
                                    <td><span class="badge bg-success">${gare.statistiques.incidents_fermes}</span></td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    
                    ${gare.commentaire ? `
                    <div class="mt-3">
                        <h6><i class="fas fa-comment me-2"></i>Commentaire</h6>
                        <div class="border rounded p-3 bg-light">
                            ${gare.commentaire}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${gare.geometrie ? `
                    <div class="mt-3">
                        <h6><i class="fas fa-map me-2"></i>Coordonnées géographiques</h6>
                        <div class="border rounded p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-info">Format WKT</span>
                                <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('${gare.geometrie}')">
                                    <i class="fas fa-copy"></i> Copier
                                </button>
                            </div>
                            <code class="d-block">${gare.geometrie}</code>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${gare.geometrie_dec ? `
                    <div class="mt-3">
                        <h6><i class="fas fa-code me-2"></i>Géométrie décodée</h6>
                        <div class="border rounded p-3 bg-light">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-warning">Format WKB</span>
                                <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('${gare.geometrie_dec}')">
                                    <i class="fas fa-copy"></i> Copier
                                </button>
                            </div>
                            <code class="d-block">${gare.geometrie_dec}</code>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${gare.geometrie ? `
                    <div class="mt-3">
                        <h6><i class="fas fa-map-marked-alt me-2"></i>Visualisation de la position</h6>
                        <div class="border rounded p-3 bg-light">
                            <div id="gareMap-${gare.id}" style="height: 300px; width: 100%;"></div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${gare.incidents && gare.incidents.length > 0 ? `
                    <div class="mt-3">
                        <h6><i class="fas fa-exclamation-triangle me-2"></i>Incidents récents (${gare.incidents.length})</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Date</th>
                                        <th>Heure</th>
                                        <th>État</th>
                                        <th>Entité</th>
                                        <th>Résumé</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${gare.incidents.map(incident => `
                                        <tr>
                                            <td><span class="badge bg-secondary">#${incident.id}</span></td>
                                            <td>${incident.date_debut ? new Date(incident.date_debut).toLocaleDateString('fr-FR') : 'N/A'}</td>
                                            <td>${incident.heure_debut || 'N/A'}</td>
                                            <td>
                                                <span class="badge bg-${incident.etat === 'Ouvert' ? 'warning' : 'success'}">
                                                    ${incident.etat || 'N/A'}
                                                </span>
                                            </td>
                                            <td>${incident.entite || 'N/A'}</td>
                                            <td>${incident.resume ? (incident.resume.length > 50 ? incident.resume.substring(0, 50) + '...' : incident.resume) : 'N/A'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    ` : ''}
                `;
                
                // Initialiser la carte si la géométrie est disponible
                if (gare.geometrie) {
                    setTimeout(() => {
                        initGareMap(gare.id, gare.geometrie);
                    }, 300);
                }
                
            } else {
                content.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Erreur lors du chargement des détails: ${data.error}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors du chargement des détails:', error);
            content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erreur de connexion lors du chargement des détails
                </div>
            `;
        });
}

/**
 * Ajouter une nouvelle gare
 */
function addNewGare() {
    console.log('🔄 Début de addNewGare()');
    
    isEditing = false;
    selectedGare = null;
    
    // Réinitialiser le formulaire
    const form = document.getElementById('gareForm');
    if (form) {
        form.reset();
        console.log('✅ Formulaire réinitialisé');
    } else {
        console.error('❌ Formulaire non trouvé');
    }
    
    // Mettre à jour le titre
    const titleElement = document.getElementById('gareFormTitle');
    if (titleElement) {
        titleElement.innerHTML = '<i class="fas fa-plus me-2"></i>Nouvelle Gare';
        console.log('✅ Titre mis à jour');
    } else {
        console.error('❌ Élément titre non trouvé');
    }
    
    // Afficher la modal
    const modalElement = document.getElementById('gareFormModal');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        console.log('✅ Modal affichée');
    } else {
        console.error('❌ Élément modal non trouvé');
    }
    
    console.log('🏁 Fin de addNewGare()');
}

/**
 * Modifier une gare
 */
function editGare(gareId) {
    const gare = allGares.find(g => g.id === gareId);
    if (!gare) return;
    
    isEditing = true;
    selectedGare = gare;
    
    // Remplir le formulaire
    document.getElementById('gareNom').value = gare.nom || '';
    document.getElementById('gareCode').value = gare.code || '';
    document.getElementById('gareType').value = gare.type || '';
    document.getElementById('gareAxe').value = gare.axe || '';
    document.getElementById('gareVille').value = gare.ville || '';
    document.getElementById('gareEtat').value = gare.etat || 'ACTIVE';
    document.getElementById('gareCodeOp').value = gare.codeoperationnel || '';
    document.getElementById('gareCodeReseau').value = gare.codereseau || '';
    
    document.getElementById('gareFormTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Modifier la Gare';
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('gareFormModal'));
    modal.show();
}

/**
 * Sauvegarder une gare (création ou modification)
 */
async function saveGare() {
    console.log('🔄 Début de saveGare()');
    
    const form = document.getElementById('gareForm');
    if (!form) {
        console.error('❌ Formulaire gare non trouvé');
        showNotification('Erreur: Formulaire non trouvé', 'error');
        return;
    }
    
    if (!form.checkValidity()) {
        console.log('⚠️ Formulaire invalide, affichage des erreurs');
        form.reportValidity();
        return;
    }
    
    showLoading(true);
    
    try {
        const gareData = {
            nom: document.getElementById('gareNom').value,
            code: document.getElementById('gareCode').value,
            type: document.getElementById('gareType').value,
            axe: document.getElementById('gareAxe').value,
            ville: document.getElementById('gareVille').value,
            etat: document.getElementById('gareEtat').value,
            codeoperationnel: document.getElementById('gareCodeOp').value,
            codereseau: document.getElementById('gareCodeReseau').value
        };
        
        console.log('📤 Données de la gare:', gareData);
        console.log('🔧 Mode édition:', isEditing);
        
        const url = isEditing ? 
            `${API_BASE}/gares/${selectedGare.id}` : 
            `${API_BASE}/gares`;
        
        const method = isEditing ? 'PUT' : 'POST';
        
        console.log('🌐 URL:', url);
        console.log('📡 Méthode:', method);
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(gareData)
        });
        
        console.log('📥 Réponse reçue, status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('📋 Résultat:', result);
        
        if (result.success) {
            console.log('✅ Succès, fermeture de la modal');
            
            // Fermer la modal
            const modalElement = document.getElementById('gareFormModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modal.hide();
            } else {
                console.error('❌ Élément modal non trouvé');
            }
            
            // Recharger les gares
            await loadGares();
            renderGares();
            
            showNotification(
                isEditing ? 'Gare modifiée avec succès' : 'Gare créée avec succès', 
                'success'
            );
        } else {
            console.error('❌ Erreur API:', result.error);
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Erreur lors de la sauvegarde:', error);
        showNotification('Erreur lors de la sauvegarde de la gare', 'error');
    } finally {
        showLoading(false);
        console.log('🏁 Fin de saveGare()');
    }
}

/**
 * Supprimer une gare
 */
async function deleteGare(gareId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette gare ?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/gares/${gareId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Recharger les gares
            await loadGares();
            renderGares();
            
            showNotification('Gare supprimée avec succès', 'success');
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la suppression:', error);
        showNotification('Erreur lors de la suppression de la gare', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Voir la gare sur la carte
 */
function showOnMap() {
    if (!selectedGare) return;
    
    // Rediriger vers la carte avec la gare sélectionnée
    window.location.href = `/carte?gare=${selectedGare.id}`;
}

/**
 * Exporter les gares
 */
function exportGares() {
    // Créer un fichier CSV avec les gares filtrées
    const headers = ['ID', 'Nom', 'Code', 'Type', 'Axe', 'Ville', 'État', 'Code Opérationnel', 'Code Réseau'];
    const csvContent = [
        headers.join(','),
        ...filteredGares.map(gare => [
            gare.id,
            `"${gare.nom || ''}"`,
            `"${gare.code || ''}"`,
            `"${gare.type || ''}"`,
            `"${gare.axe || ''}"`,
            `"${gare.ville || ''}"`,
            `"${gare.etat || ''}"`,
            `"${gare.codeoperationnel || ''}"`,
            `"${gare.codereseau || ''}"`
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `gares_oncf_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Export des gares terminé', 'success');
}

/**
 * Actualiser les gares
 */
async function refreshGares() {
    console.log('🔄 Actualisation des gares...');
    await Promise.all([
        loadGares(),
        loadGareFilters(),
        loadStatistics()
    ]);
    applyFilters();
    showNotification('Gares actualisées', 'success');
}

/**
 * Changer la taille de page
 */
function changePageSize() {
    itemsPerPage = parseInt(document.getElementById('pageSize').value);
    currentPage = 1;
    applyFilters();
}

/**
 * Mettre à jour la pagination
 */
function updatePagination(pagination) {
    const paginationElement = document.getElementById('pagination');
    
    if (pagination.pages <= 1) {
        paginationElement.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Bouton précédent
    html += `
        <li class="page-item ${pagination.page === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.page - 1}); return false;">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Numéros de pages
    const maxVisiblePages = 5;
    let startPage = Math.max(1, pagination.page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(pagination.pages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === pagination.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    // Bouton suivant
    html += `
        <li class="page-item ${pagination.page === pagination.pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.page + 1}); return false;">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginationElement.innerHTML = html;
}

/**
 * Aller à une page spécifique
 */
async function goToPage(page) {
    currentPage = page;
    await loadGares(page);
    renderGares();
}

/**
 * Mettre à jour les informations de pagination
 */
function updatePaginationInfo() {
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredGares.length);
    
    document.getElementById('paginationInfo').textContent = 
        `Affichage ${startIndex}-${endIndex} de ${filteredGares.length} résultats`;
}

/**
 * Basculer la sélection de toutes les gares
 */
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const gareCheckboxes = document.querySelectorAll('.gare-checkbox');
    
    gareCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

/**
 * Trier le tableau
 */
function sortTable(columnIndex) {
    // Implémentation du tri (à développer selon les besoins)
    showNotification('Fonctionnalité de tri en développement', 'info');
}

/**
 * Afficher/masquer le loading
 */
function showLoading(show) {
    // Utiliser un indicateur de chargement global si disponible
    if (window.oncfGIS && window.oncfGIS.showLoading) {
        window.oncfGIS.showLoading(show);
    }
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    // Utiliser le système de notifications global si disponible
    if (window.oncfGIS && window.oncfGIS.showNotification) {
        window.oncfGIS.showNotification(message, type);
    } else {
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

/**
 * Fonction debounce pour optimiser les recherches
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copier du texte dans le presse-papiers
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Texte copié dans le presse-papiers', 'success');
    }).catch(err => {
        console.error('Erreur lors de la copie:', err);
        showNotification('Erreur lors de la copie', 'error');
    });
}

/**
 * Initialiser la carte pour une gare spécifique
 */
function initGareMap(gareId, geometrie) {
    try {
        // Extraire les coordonnées du format WKT POINT(x y)
        const match = geometrie.match(/POINT\(([-\d.]+)\s+([-\d.]+)\)/);
        if (!match) {
            console.error('Format de géométrie non reconnu:', geometrie);
            return;
        }
        
        const lon = parseFloat(match[1]);
        const lat = parseFloat(match[2]);
        
        // Créer la carte Leaflet
        const mapElement = document.getElementById(`gareMap-${gareId}`);
        if (!mapElement) {
            console.error('Élément de carte non trouvé');
            return;
        }
        
        const map = L.map(`gareMap-${gareId}`).setView([lat, lon], 13);
        
        // Ajouter la couche OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Ajouter le marqueur de la gare
        const marker = L.marker([lat, lon]).addTo(map);
        
        // Ajouter un popup avec les informations de la gare
        const gare = allGares.find(g => g.id === gareId);
        if (gare) {
            marker.bindPopup(`
                <div class="text-center">
                    <h6><i class="fas fa-train"></i> ${gare.nom}</h6>
                    <p class="mb-1"><strong>Code:</strong> ${gare.code}</p>
                    <p class="mb-1"><strong>Type:</strong> ${gare.type}</p>
                    <p class="mb-0"><strong>Coordonnées:</strong><br>${lat.toFixed(6)}, ${lon.toFixed(6)}</p>
                </div>
            `);
        }
        
        // Ajouter un cercle pour indiquer la précision
        L.circle([lat, lon], {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.2,
            radius: 500
        }).addTo(map);
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation de la carte:', error);
    }
}

/**
 * Parser les coordonnées WKT
 */
function parseWKT(wkt) {
    try {
        if (wkt.startsWith('POINT(')) {
            const coords = wkt.replace('POINT(', '').replace(')', '').split(' ');
            return {
                type: 'Point',
                coordinates: [parseFloat(coords[0]), parseFloat(coords[1])]
            };
        }
        return null;
    } catch (error) {
        console.error('Erreur lors du parsing WKT:', error);
        return null;
    }
}

// Fonctions globales pour les événements onclick
window.showGareDetails = showGareDetails;
window.editGare = editGare;
window.deleteGare = deleteGare;
window.saveGare = saveGare;
window.addNewGare = addNewGare;
window.showOnMap = showOnMap;
window.exportGares = exportGares;
window.refreshGares = refreshGares;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.goToPage = goToPage;
window.changePageSize = changePageSize;
window.toggleSelectAll = toggleSelectAll;
window.sortTable = sortTable;
window.copyToClipboard = copyToClipboard;
window.initGareMap = initGareMap;
window.removeFilter = removeFilter;
window.clearAllFilters = clearAllFilters;
window.applyQuickFilter = applyQuickFilter; 

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

// Fonction pour convertir les codes de région en noms
function getRegionName(regionCode) {
    const regionNames = {
        '1': 'Casablanca-Settat',
        '2': 'Rabat-Salé-Kénitra',
        '3': 'Marrakech-Safi',
        '4': 'Fès-Meknès',
        '5': 'Tanger-Tétouan-Al Hoceima',
        '6': 'Souss-Massa',
        '7': 'Oriental',
        '8': 'Béni Mellal-Khénifra',
        '9': 'Drâa-Tafilalet',
        '10': 'Guelmim-Oued Noun',
        '11': 'Laâyoune-Sakia El Hamra',
        '12': 'Dakhla-Oued Ed-Dahab'
    };
    
    return regionNames[regionCode] || `Région ${regionCode}`;
}

// Fonction pour formater l'affichage des détails de gare
function formatGareDetails(gare) {
    return {
        ...gare,
        type_display: getGareTypeName(gare.type),
        ville_display: getVilleName(gare.ville),
        region_display: getRegionName(gare.region),
        etat_display: gare.etat === 'ACTIVE' ? 'Active' : 'Passive',
        statut_display: gare.statut || 'Non défini'
    };
} 