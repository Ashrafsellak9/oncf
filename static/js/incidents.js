/**
 * Gestion des Incidents - ONCF GIS
 * JavaScript pour la page de gestion des incidents
 */

// Variables globales
let allIncidents = [];
let filteredIncidents = [];
let currentPage = 1;
let itemsPerPage = 50; // Augmenté de 12 à 50 pour afficher plus d'incidents
let totalPages = 1;
let totalIncidents = 0;
let selectedIncident = null;
let incidentTypes = [];
let incidentLocations = [];
let incidentSousTypes = [];
let incidentSources = [];
let incidentSystems = [];
let incidentEntites = [];

// Configuration API
const API_BASE = '/api';

/**
 * Initialisation de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚨 Initialisation de la page des incidents');
    
    // Charger les données initiales
    Promise.all([
        loadIncidents(),
        loadIncidentTypes(),
        loadLocations(),
        loadStatistics(),
        loadReferenceData() // Charger les données de référence
    ]).then(() => {
        console.log('✅ Toutes les données des incidents chargées');
        setupEventListeners();
        renderIncidents();
    }).catch(error => {
        console.error('❌ Erreur lors du chargement des données:', error);
        showNotification('Erreur lors du chargement des données', 'error');
    });
});

/**
 * Configuration des écouteurs d'événements
 */
function setupEventListeners() {
    // Filtres en temps réel
    document.getElementById('statusFilter').addEventListener('change', applyFilters);
    document.getElementById('periodFilter').addEventListener('change', applyFilters);
    document.getElementById('searchFilter').addEventListener('input', debounce(applyFilters, 500));
    
    // Actualisation automatique toutes les 5 minutes
    setInterval(refreshIncidents, 5 * 60 * 1000);
}

/**
 * Charger les incidents avec pagination
 */
async function loadIncidents(page = 1, filters = {}) {
    showLoading(true);
    
    try {
        // Construire les paramètres de requête
        const params = new URLSearchParams({
            page: page,
            per_page: itemsPerPage
        });
        
        // Ajouter les filtres
        if (filters.status) params.append('statut', filters.status);
        if (filters.type) params.append('type_id', filters.type);
        if (filters.search) params.append('search', filters.search);
        
        const response = await fetch(`${API_BASE}/evenements?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            allIncidents = data.data;
            
            // Mettre à jour la pagination
            updatePagination(data.pagination);
            updatePaginationInfo();
            updateIncidentStats();
            
            // Afficher les incidents
            displayIncidents(allIncidents);
            
            console.log(`✅ ${allIncidents.length} incidents chargés (page ${page}/${data.pagination.pages})`);
            return data;
        } else {
            throw new Error(data.error || 'Erreur lors du chargement des données');
        }
    } catch (error) {
        console.error('❌ Erreur chargement incidents:', error);
        showNotification('Erreur lors du chargement des incidents. Veuillez réessayer.', 'error');
        return { data: [], pagination: { total: 0, pages: 0 } };
    } finally {
        showLoading(false);
    }
}

/**
 * Afficher les incidents dans la liste
 */
function displayIncidents(incidents) {
    const container = document.getElementById('incidentsList');
    container.innerHTML = '';
    
    if (!incidents || incidents.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Aucun incident trouvé</strong>
                    <br>
                    <small class="text-muted">Essayez de modifier vos filtres de recherche</small>
                </div>
            </div>
        `;
        return;
    }
    
    incidents.forEach((incident, index) => {
        const incidentCard = createIncidentCard(incident, index);
        container.appendChild(incidentCard);
    });
    
    // Mettre à jour les informations de pagination
    updatePaginationInfo();
}

/**
 * Mettre à jour les informations de pagination
 */
function updatePaginationInfo() {
    const start = ((currentPage - 1) * itemsPerPage) + 1;
    const end = Math.min(currentPage * itemsPerPage, totalIncidents);
    
    const paginationInfo = document.getElementById('paginationInfo');
    if (paginationInfo) {
        paginationInfo.innerHTML = `
            <i class="fas fa-list me-2"></i>
            <strong>Affichage de ${start} à ${end}</strong> sur <strong>${totalIncidents} incidents</strong>
        `;
    }
    
    const paginationStats = document.getElementById('paginationStats');
    if (paginationStats) {
        paginationStats.textContent = `Page ${currentPage} sur ${totalPages}`;
    }
}

/**
 * Mettre à jour les statistiques des incidents
 */
function updateIncidentStats() {
    // Cette fonction met à jour les statistiques affichées en haut de la page
    // Les statistiques sont déjà chargées par loadStatistics()
    console.log('📊 Statistiques des incidents mises à jour');
}

/**
 * Charger les types d'incidents
 */
async function loadIncidentTypes() {
    try {
        const response = await fetch(`${API_BASE}/types-incidents`);
        const data = await response.json();
        
        if (data.success) {
            incidentTypes = data.data;
            populateTypeFilters();
            populateTypeSelect();
            console.log(`✅ ${incidentTypes.length} types d'incidents chargés`);
        }
    } catch (error) {
        console.error('❌ Erreur chargement types:', error);
    }
}

/**
 * Charger les localisations
 */
async function loadLocations() {
    try {
        const response = await fetch(`${API_BASE}/localisations`);
        const data = await response.json();
        
        if (data.success) {
            incidentLocations = data.data;
            populateLocationSelect();
            console.log(`✅ ${incidentLocations.length} localisations chargées`);
        }
    } catch (error) {
        console.error('❌ Erreur chargement localisations:', error);
    }
}

/**
 * Charger les statistiques
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/statistiques`);
        const data = await response.json();
        
        if (data.success && data.data.evenements) {
            const stats = data.data.evenements;
            
            document.getElementById('totalIncidents').textContent = stats.total || 0;
            
            // Calculer les incidents par statut
            let openCount = 0, resolvedCount = 0;
            stats.par_statut.forEach(item => {
                if (item.statut && item.statut.toLowerCase().includes('ouvert')) {
                    openCount += item.count;
                } else if (item.statut && (item.statut.toLowerCase().includes('résolu') || item.statut.toLowerCase().includes('fermé'))) {
                    resolvedCount += item.count;
                }
            });
            
            document.getElementById('openIncidents').textContent = openCount;
            document.getElementById('resolvedIncidents').textContent = resolvedCount;
            document.getElementById('avgResolutionTime').textContent = '2.5h'; // Exemple
            
            console.log('✅ Statistiques des incidents chargées');
        }
    } catch (error) {
        console.error('❌ Erreur chargement statistiques:', error);
    }
}

/**
 * Charger les données de référence pour le formulaire
 */
async function loadReferenceData() {
    console.log('📚 Chargement des données de référence...');
    
    try {
        // Charger les types d'incidents
        const typesResponse = await fetch(`${API_BASE}/reference/types`);
        if (typesResponse.ok) {
            incidentTypes = await typesResponse.json();
            populateSelect('incidentType', incidentTypes, 'id', 'intitule');
        }
        
        // Charger les sous-types
        const sousTypesResponse = await fetch(`${API_BASE}/reference/sous-types`);
        if (sousTypesResponse.ok) {
            incidentSousTypes = await sousTypesResponse.json();
            populateSelect('incidentSousType', incidentSousTypes, 'id', 'intitule');
        }
        
        // Charger les sources
        const sourcesResponse = await fetch(`${API_BASE}/reference/sources`);
        if (sourcesResponse.ok) {
            incidentSources = await sourcesResponse.json();
            populateSelect('incidentSource', incidentSources, 'id', 'intitule');
        }
        
        // Charger les systèmes
        const systemsResponse = await fetch(`${API_BASE}/reference/systemes`);
        if (systemsResponse.ok) {
            incidentSystems = await systemsResponse.json();
            populateSelect('incidentSystem', incidentSystems, 'id', 'intitule');
        }
        
        // Charger les entités
        const entitesResponse = await fetch(`${API_BASE}/reference/entites`);
        if (entitesResponse.ok) {
            incidentEntites = await entitesResponse.json();
            populateSelect('incidentEntite', incidentEntites, 'id', 'intitule');
        }
        
        // Charger les localisations
        const locationsResponse = await fetch(`${API_BASE}/reference/localisations`);
        if (locationsResponse.ok) {
            incidentLocations = await locationsResponse.json();
            populateSelect('incidentLocation', incidentLocations, 'id', 'nom');
        }
        
        console.log('✅ Données de référence chargées');
    } catch (error) {
        console.error('❌ Erreur chargement données de référence:', error);
    }
}

/**
 * Remplir un select avec des données
 */
function populateSelect(selectId, data, valueField, textField) {
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

/**
 * Peupler les filtres par type
 */
function populateTypeFilters() {
    const container = document.getElementById('typeFilters');
    container.innerHTML = '';
    
    incidentTypes.forEach(type => {
        const chip = document.createElement('div');
        chip.className = 'type-chip';
        chip.textContent = type.libelle;
        chip.dataset.typeId = type.id;
        chip.onclick = () => toggleTypeFilter(chip, type.id);
        container.appendChild(chip);
    });
}

/**
 * Peupler le select des types pour le nouveau formulaire
 */
function populateTypeSelect() {
    const select = document.getElementById('incidentType');
    select.innerHTML = '<option value="">Sélectionner un type</option>';
    
    incidentTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.libelle;
        select.appendChild(option);
    });
}

/**
 * Peupler le select des localisations
 */
function populateLocationSelect() {
    const select = document.getElementById('incidentLocation');
    select.innerHTML = '<option value="">Sélectionner une localisation</option>';
    
    incidentLocations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.id;
        option.textContent = `${location.axe || ''} - ${location.description || location.gare || 'Sans nom'}`.trim();
        select.appendChild(option);
    });
}

/**
 * Basculer le filtre par type
 */
function toggleTypeFilter(chip, typeId) {
    chip.classList.toggle('active');
    applyFilters();
}

/**
 * Appliquer les filtres
 */
async function applyFilters() {
    const status = document.getElementById('statusFilter').value;
    const period = document.getElementById('periodFilter').value;
    const search = document.getElementById('searchFilter').value;
    
    // Retourner à la première page lors du filtrage
    currentPage = 1;
    
    const filters = { status, period, search };
    await loadIncidents(1, filters);
}

/**
 * Afficher les incidents
 */
function renderIncidents() {
    const container = document.getElementById('incidentsList');
    container.innerHTML = '';
    
    if (filteredIncidents.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4>Aucun incident trouvé</h4>
                    <p class="text-muted">Essayez de modifier vos filtres de recherche</p>
                </div>
            </div>
        `;
        
        // Mettre à jour les informations de pagination
        updatePaginationInfo();
        return;
    }
    
    // Pagination côté client
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredIncidents.length);
    const pageIncidents = filteredIncidents.slice(startIndex, endIndex);
    
    pageIncidents.forEach(incident => {
        const card = createIncidentCard(incident);
        container.appendChild(card);
    });
    
    // Mettre à jour la pagination et les informations
    updateClientPagination();
    updatePaginationInfo();
}

/**
 * Créer une carte d'incident
 */
function createIncidentCard(incident) {
    const col = document.createElement('div');
    col.className = 'col-lg-4 col-md-6 mb-4';
    
    // Déterminer la classe de statut
    let statusClass = 'open';
    if (incident.statut) {
        const status = incident.statut.toLowerCase();
        if (status.includes('résolu') || status.includes('fermé')) {
            statusClass = 'resolved';
        } else if (status.includes('cours')) {
            statusClass = 'in-progress';
        }
    }
    
    // Utiliser le nom du type directement depuis l'API
    const typeLabel = incident.type_name || 'Type inconnu';
    
    // Formatage des dates
    const dateDebut = incident.date_debut ? 
        new Date(incident.date_debut).toLocaleDateString('fr-FR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        }) : 'Non définie';
    
    // Description tronquée
    const description = incident.description || 'Aucune description disponible';
    const shortDescription = description.length > 150 ? 
        description.substring(0, 150) + '...' : description;
    
    col.innerHTML = `
        <div class="card incident-card ${statusClass}" onclick="showIncidentDetails(${incident.id})">
            <div class="card-header d-flex justify-content-between align-items-center">
                <small class="text-muted">Incident #${incident.id}</small>
                <span class="badge status-badge bg-${getStatusColor(incident.statut)}">
                    ${incident.statut || 'Non défini'}
                </span>
            </div>
            <div class="card-body">
                <h6 class="card-title mb-2">
                    <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                    ${typeLabel}
                </h6>
                <p class="card-text incident-description">
                    ${shortDescription}
                </p>
                <div class="mt-3">
                    <small class="text-muted d-block">
                        <i class="fas fa-calendar me-1"></i>
                        ${dateDebut}
                    </small>
                    ${incident.heure_debut ? `
                        <small class="text-muted d-block">
                            <i class="fas fa-clock me-1"></i>
                            ${incident.heure_debut}
                        </small>
                    ` : ''}
                </div>
            </div>
            <div class="card-footer">
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        ${incident.location_name || 'Localisation non définie'}
                    </small>
                    <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showIncidentDetails(${incident.id})">
                        Détails
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

/**
 * Obtenir la couleur du badge de statut
 */
function getStatusColor(statut) {
    if (!statut) return 'secondary';
    
    const status = statut.toLowerCase();
    if (status.includes('ouvert')) return 'danger';
    if (status.includes('cours')) return 'warning';
    if (status.includes('résolu') || status.includes('fermé')) return 'success';
    return 'secondary';
}

/**
 * Afficher les détails d'un incident
 */
function showIncidentDetails(incidentId) {
    console.log('🔍 Affichage des détails de l\'incident:', incidentId);
    
    // Afficher un indicateur de chargement
    const content = document.getElementById('incidentDetailsContent');
    content.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-2">Chargement des détails...</p>
        </div>
    `;
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('incidentDetailsModal'));
    modal.show();
    
    // Récupérer les détails complets depuis l'API
    fetch(`/api/evenements/${incidentId}/details`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const incident = data.data;
                selectedIncident = incident;
                
                content.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-info-circle me-2"></i>Informations générales</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>ID:</strong></td>
                                    <td><span class="badge bg-secondary">#${incident.id}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>État:</strong></td>
                                    <td>
                                        <span class="badge bg-${getStatusColor(incident.etat)}">
                                            ${incident.etat || 'Non défini'}
                                        </span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Entité:</strong></td>
                                    <td>${incident.entite || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Important:</strong></td>
                                    <td>
                                        <span class="badge bg-${incident.important ? 'danger' : 'secondary'}">
                                            ${incident.important ? 'Oui' : 'Non'}
                                        </span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Impact Service:</strong></td>
                                    <td>
                                        <span class="badge bg-${incident.impact_service ? 'warning' : 'secondary'}">
                                            ${incident.impact_service ? 'Oui' : 'Non'}
                                        </span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Supprimé:</strong></td>
                                    <td>
                                        <span class="badge bg-${incident.deleted ? 'danger' : 'success'}">
                                            ${incident.deleted ? 'Oui' : 'Non'}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-calendar-alt me-2"></i>Dates et heures</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Date Avis:</strong></td>
                                    <td>${incident.date_avis ? new Date(incident.date_avis).toLocaleDateString('fr-FR') : 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Heure Avis:</strong></td>
                                    <td>${incident.heure_avis || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Date Début:</strong></td>
                                    <td>${incident.date_debut ? new Date(incident.date_debut).toLocaleDateString('fr-FR') : 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Heure Début:</strong></td>
                                    <td>${incident.heure_debut || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Date Fin:</strong></td>
                                    <td>${incident.date_fin ? new Date(incident.date_fin).toLocaleDateString('fr-FR') : 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Heure Fin:</strong></td>
                                    <td>${incident.heure_fin || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Date Impact:</strong></td>
                                    <td>${incident.date_impact ? new Date(incident.date_impact).toLocaleDateString('fr-FR') : 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Heure Impact:</strong></td>
                                    <td>${incident.heure_impact || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Date MAJ:</strong></td>
                                    <td>${incident.datemaj ? new Date(incident.datemaj).toLocaleString('fr-FR') : 'Non définie'}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <h6><i class="fas fa-tags me-2"></i>Classifications</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Type:</strong></td>
                                    <td>${incident.type ? incident.type.intitule : 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Sous-Type:</strong></td>
                                    <td>${incident.sous_type ? incident.sous_type.intitule : 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Source:</strong></td>
                                    <td>${incident.source ? incident.source.intitule : 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Entité Référence:</strong></td>
                                    <td>${incident.entite_ref ? incident.entite_ref.intitule : 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Fonction:</strong></td>
                                    <td>${incident.fonction || 'Non définie'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Source Personne:</strong></td>
                                    <td>${incident.source_personne || 'Non définie'}</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-map-marker-alt me-2"></i>Localisation</h6>
                            ${incident.localisation ? `
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Type Localisation:</strong></td>
                                    <td>${incident.localisation.type_localisation || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Type PK:</strong></td>
                                    <td>${incident.localisation.type_pk || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>PK Début:</strong></td>
                                    <td>${incident.localisation.pk_debut || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>PK Fin:</strong></td>
                                    <td>${incident.localisation.pk_fin || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Gare Début ID:</strong></td>
                                    <td>${incident.localisation.gare_debut_id || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Gare Fin ID:</strong></td>
                                    <td>${incident.localisation.gare_fin_id || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Site Sûreté:</strong></td>
                                    <td>${incident.localisation.site_surete ? incident.localisation.site_surete.intitule : 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Zone Clôture:</strong></td>
                                    <td>${incident.localisation.zone_cloture || 'Non définie'}</td>
                                </tr>
                            </table>
                            ` : '<p class="text-muted">Aucune information de localisation disponible</p>'}
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <h6><i class="fas fa-file-alt me-2"></i>Descriptions</h6>
                            ${incident.resume ? `
                            <div class="mb-3">
                                <strong>Résumé:</strong>
                                <div class="border rounded p-3 bg-light">
                                    ${incident.resume}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${incident.commentaire ? `
                            <div class="mb-3">
                                <strong>Commentaire:</strong>
                                <div class="border rounded p-3 bg-light">
                                    ${incident.commentaire}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${incident.extrait ? `
                            <div class="mb-3">
                                <strong>Extrait:</strong>
                                <div class="border rounded p-3 bg-light">
                                    ${incident.extrait}
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-file-text me-2"></i>Rapports</h6>
                            ${incident.rapport_journalier ? `
                            <div class="mb-3">
                                <strong>Rapport Journalier:</strong>
                                <div class="border rounded p-3 bg-light">
                                    ${incident.rapport_journalier}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${incident.rapport_hebdomadaire ? `
                            <div class="mb-3">
                                <strong>Rapport Hebdomadaire:</strong>
                                <div class="border rounded p-3 bg-light">
                                    ${incident.rapport_hebdomadaire}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${incident.localisation && incident.localisation.commentaire ? `
                            <div class="mb-3">
                                <strong>Commentaire Localisation:</strong>
                                <div class="border rounded p-3 bg-light">
                                    ${incident.localisation.commentaire}
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <h6><i class="fas fa-cogs me-2"></i>Paramètres techniques</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>User ID:</strong></td>
                                    <td>${incident.user_id || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Responsabilité ID:</strong></td>
                                    <td>${incident.responsabilite_id || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Workflow Étape ID:</strong></td>
                                    <td>${incident.workflow_etape_id || 'Non défini'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Inclure Commentaire:</strong></td>
                                    <td>
                                        <span class="badge bg-${incident.inclure_commentaire ? 'success' : 'secondary'}">
                                            ${incident.inclure_commentaire ? 'Oui' : 'Non'}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-history me-2"></i>Chronologie</h6>
                            <div class="timeline">
                                ${incident.date_avis ? `
                                <div class="timeline-item">
                                    <strong>Avis:</strong> ${new Date(incident.date_avis).toLocaleString('fr-FR')}
                                    <br><small class="text-muted">Incident signalé</small>
                                </div>
                                ` : ''}
                                
                                ${incident.date_debut ? `
                                <div class="timeline-item">
                                    <strong>Début:</strong> ${new Date(incident.date_debut).toLocaleString('fr-FR')}
                                    <br><small class="text-muted">Début de l'incident</small>
                                </div>
                                ` : ''}
                                
                                ${incident.date_impact ? `
                                <div class="timeline-item">
                                    <strong>Impact:</strong> ${new Date(incident.date_impact).toLocaleString('fr-FR')}
                                    <br><small class="text-muted">Impact sur le service</small>
                                </div>
                                ` : ''}
                                
                                ${incident.date_fin ? `
                                <div class="timeline-item">
                                    <strong>Fin:</strong> ${new Date(incident.date_fin).toLocaleString('fr-FR')}
                                    <br><small class="text-muted">Fin de l'incident</small>
                                </div>
                                ` : ''}
                                
                                ${incident.datemaj ? `
                                <div class="timeline-item">
                                    <strong>Dernière MAJ:</strong> ${new Date(incident.datemaj).toLocaleString('fr-FR')}
                                    <br><small class="text-muted">Dernière mise à jour</small>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
                
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
 * Mettre à jour la pagination côté client
 */
function updateClientPagination() {
    const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage);
    const pagination = document.getElementById('paginationControls');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    // Calculer les indices de début et fin pour la page courante
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, filteredIncidents.length);
    
    let html = '';
    
    // Informations sur la pagination
    html += `
        <li class="page-item disabled">
            <span class="page-link">
                Affichage ${startIndex}-${endIndex} sur ${filteredIncidents.length} incidents
            </span>
        </li>
    `;
    
    // Bouton précédent
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${currentPage - 1}); return false;">
                <i class="fas fa-chevron-left"></i> Précédent
            </a>
        </li>
    `;
    
    // Numéros de pages avec logique intelligente
    const maxVisiblePages = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Ajuster si on est près de la fin
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Première page
    if (startPage > 1) {
        html += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(1); return false;">1</a>
            </li>
        `;
        if (startPage > 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    // Pages visibles
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    // Dernière page
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        html += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${totalPages}); return false;">${totalPages}</a>
            </li>
        `;
    }
    
    // Bouton suivant
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${currentPage + 1}); return false;">
                Suivant <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

/**
 * Mettre à jour la pagination (API)
 */
function updatePagination(pagination) {
    const paginationContainer = document.getElementById('paginationContainer');
    if (!paginationContainer) return;
    
    const { page, pages, total } = pagination;
    currentPage = page;
    totalPages = pages;
    totalIncidents = total;
    
    if (pages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<nav aria-label="Pagination des incidents"><ul class="pagination justify-content-center">';
    
    // Bouton précédent
    if (page > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${page - 1})" aria-label="Précédent">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    } else {
        paginationHTML += `
            <li class="page-item disabled">
                <span class="page-link">
                    <i class="fas fa-chevron-left"></i>
                </span>
            </li>
        `;
    }
    
    // Pages numérotées
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(pages, page + 2);
    
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(1)">1</a>
            </li>
        `;
        if (startPage > 2) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === page) {
            paginationHTML += `
                <li class="page-item active">
                    <span class="page-link">${i}</span>
                </li>
            `;
        } else {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="goToPage(${i})">${i}</a>
                </li>
            `;
        }
    }
    
    if (endPage < pages) {
        if (endPage < pages - 1) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${pages})">${pages}</a>
            </li>
        `;
    }
    
    // Bouton suivant
    if (page < pages) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${page + 1})" aria-label="Suivant">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    } else {
        paginationHTML += `
            <li class="page-item disabled">
                <span class="page-link">
                    <i class="fas fa-chevron-right"></i>
                </span>
            </li>
        `;
    }
    
    paginationHTML += '</ul></nav>';
    paginationContainer.innerHTML = paginationHTML;
}

/**
 * Aller à une page spécifique
 */
async function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    
    // Construire les filtres actuels
    const filters = {
        status: document.getElementById('statusFilter').value,
        period: document.getElementById('periodFilter').value,
        search: document.getElementById('searchFilter').value
    };
    
    // Charger les incidents de la page demandée
    await loadIncidents(page, filters);
    
    // Faire défiler vers le haut de la liste
    document.getElementById('incidentsList').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Changer le nombre d'éléments par page
 */
async function changeItemsPerPage() {
    const newItemsPerPage = parseInt(document.getElementById('itemsPerPageSelect').value);
    itemsPerPage = newItemsPerPage;
    currentPage = 1; // Retourner à la première page
    
    // Construire les filtres actuels
    const filters = {
        status: document.getElementById('statusFilter').value,
        period: document.getElementById('periodFilter').value,
        search: document.getElementById('searchFilter').value
    };
    
    // Recharger les incidents avec le nouveau nombre d'éléments par page
    await loadIncidents(1, filters);
    
    showNotification(`Affichage de ${newItemsPerPage} incidents par page`, 'info');
}

/**
 * Actualiser les incidents
 */
async function refreshIncidents() {
    console.log('🔄 Actualisation des incidents...');
    
    // Construire les filtres actuels
    const filters = {
        status: document.getElementById('statusFilter').value,
        period: document.getElementById('periodFilter').value,
        search: document.getElementById('searchFilter').value
    };
    
    // Recharger les incidents
    await loadIncidents(currentPage, filters);
    
    // Recharger les statistiques
    await loadStatistics();
    
    console.log('✅ Actualisation terminée');
}

/**
 * Appliquer les filtres
 */
async function applyFilters() {
    const status = document.getElementById('statusFilter').value;
    const period = document.getElementById('periodFilter').value;
    const search = document.getElementById('searchFilter').value;
    
    // Retourner à la première page lors du filtrage
    currentPage = 1;
    
    const filters = { status, period, search };
    await loadIncidents(1, filters);
}

/**
 * Enregistrer un nouvel incident
 */
async function saveNewIncident() {
    console.log('🔄 Début de saveNewIncident()');
    
    const form = document.getElementById('newIncidentForm');
    if (!form) {
        console.error('❌ Formulaire incident non trouvé');
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
        const incidentData = {
            type_id: parseInt(document.getElementById('incidentType').value),
            localisation_id: parseInt(document.getElementById('incidentLocation').value),
            date_debut: document.getElementById('incidentDateDebut').value,
            date_fin: document.getElementById('incidentDateFin').value || null,
            description: document.getElementById('incidentDescription').value,
            statut: document.getElementById('incidentStatut').value
        };
        
        console.log('📤 Données de l\'incident:', incidentData);
        
        const response = await fetch(`${API_BASE}/evenements`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(incidentData)
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
            const modalElement = document.getElementById('newIncidentModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modal.hide();
            } else {
                console.error('❌ Élément modal non trouvé');
            }
            
            // Réinitialiser le formulaire
            form.reset();
            
            // Recharger les incidents
            await loadIncidents();
            applyFilters();
            
            showNotification('Incident créé avec succès', 'success');
        } else {
            console.error('❌ Erreur API:', result.error);
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Erreur lors de la création:', error);
        showNotification('Erreur lors de la création de l\'incident', 'error');
    } finally {
        showLoading(false);
        console.log('🏁 Fin de saveNewIncident()');
    }
}

/**
 * Modifier un incident (version améliorée)
 */
function editIncident() {
    if (!selectedIncident) {
        showNotification('Aucun incident sélectionné', 'error');
        return;
    }
    
    console.log('✏️ Modification de l\'incident:', selectedIncident.id);
    
    // Remplir le formulaire avec les données de l'incident sélectionné
    document.getElementById('incidentType').value = selectedIncident.type_id || '';
    document.getElementById('incidentSousType').value = selectedIncident.sous_type_id || '';
    document.getElementById('incidentLocation').value = selectedIncident.localisation_id || '';
    document.getElementById('incidentEntite').value = selectedIncident.entite_id || '';
    document.getElementById('incidentSource').value = selectedIncident.source_id || '';
    document.getElementById('incidentSystem').value = selectedIncident.system_id || '';
    
    // Dates et heures
    if (selectedIncident.date_debut) {
        const dateDebut = new Date(selectedIncident.date_debut);
        document.getElementById('incidentDateDebut').value = dateDebut.toISOString().slice(0, 16);
    }
    if (selectedIncident.date_fin) {
        const dateFin = new Date(selectedIncident.date_fin);
        document.getElementById('incidentDateFin').value = dateFin.toISOString().slice(0, 16);
    }
    if (selectedIncident.heure_debut) {
        document.getElementById('incidentHeureDebut').value = selectedIncident.heure_debut;
    }
    if (selectedIncident.heure_fin) {
        document.getElementById('incidentHeureFin').value = selectedIncident.heure_fin;
    }
    
    // Description et autres champs
    document.getElementById('incidentResume').value = selectedIncident.resume || '';
    document.getElementById('incidentCommentaire').value = selectedIncident.commentaire || '';
    document.getElementById('incidentStatut').value = selectedIncident.etat || 'Ouvert';
    document.getElementById('incidentImpact').value = selectedIncident.impact_service || '';
    document.getElementById('incidentFonction').value = selectedIncident.fonction || '';
    document.getElementById('incidentResponsabilite').value = selectedIncident.responsabilite_id || '';
    document.getElementById('incidentImportant').checked = selectedIncident.important || false;
    
    // Changer le titre de la modal
    document.getElementById('modalTitle').textContent = `Modifier l'Incident #${selectedIncident.id}`;
    
    // Changer les boutons
    const saveButton = document.getElementById('saveButton');
    const previewButton = document.getElementById('previewButton');
    
    saveButton.innerHTML = '<i class="fas fa-save me-1"></i>Modifier';
    saveButton.onclick = updateIncident;
    saveButton.className = 'btn btn-warning';
    
    previewButton.innerHTML = '<i class="fas fa-eye me-1"></i>Aperçu des modifications';
    
    // Fermer la modal de détails et ouvrir la modal de modification
    const detailsModal = bootstrap.Modal.getInstance(document.getElementById('incidentDetailsModal'));
    detailsModal.hide();
    
    const editModal = new bootstrap.Modal(document.getElementById('newIncidentModal'));
    editModal.show();
}

/**
 * Aperçu de l'incident avant sauvegarde
 */
function previewIncident() {
    const form = document.getElementById('newIncidentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const previewData = collectFormData();
    const previewContent = document.getElementById('previewContent');
    
    previewContent.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            Aperçu des données avant sauvegarde
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-primary">Informations générales</h6>
                <table class="table table-sm">
                    <tr><td><strong>Type:</strong></td><td>${getSelectText('incidentType', incidentTypes)}</td></tr>
                    <tr><td><strong>Sous-type:</strong></td><td>${getSelectText('incidentSousType', incidentSousTypes)}</td></tr>
                    <tr><td><strong>Statut:</strong></td><td><span class="badge bg-${getStatusColor(previewData.etat)}">${previewData.etat}</span></td></tr>
                    <tr><td><strong>Important:</strong></td><td>${previewData.important ? '<span class="badge bg-danger">Oui</span>' : '<span class="badge bg-secondary">Non</span>'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-primary">Localisation et entité</h6>
                <table class="table table-sm">
                    <tr><td><strong>Localisation:</strong></td><td>${getSelectText('incidentLocation', incidentLocations)}</td></tr>
                    <tr><td><strong>Entité:</strong></td><td>${getSelectText('incidentEntite', incidentEntites)}</td></tr>
                    <tr><td><strong>Source:</strong></td><td>${getSelectText('incidentSource', incidentSources)}</td></tr>
                    <tr><td><strong>Système:</strong></td><td>${getSelectText('incidentSystem', incidentSystems)}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-md-6">
                <h6 class="text-primary">Dates et heures</h6>
                <table class="table table-sm">
                    <tr><td><strong>Date début:</strong></td><td>${previewData.date_debut || 'Non définie'}</td></tr>
                    <tr><td><strong>Heure début:</strong></td><td>${previewData.heure_debut || 'Non définie'}</td></tr>
                    <tr><td><strong>Date fin:</strong></td><td>${previewData.date_fin || 'Non définie'}</td></tr>
                    <tr><td><strong>Heure fin:</strong></td><td>${previewData.heure_fin || 'Non définie'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-primary">Impact et responsabilité</h6>
                <table class="table table-sm">
                    <tr><td><strong>Impact service:</strong></td><td>${previewData.impact_service || 'Non défini'}</td></tr>
                    <tr><td><strong>Fonction:</strong></td><td>${previewData.fonction || 'Non définie'}</td></tr>
                    <tr><td><strong>Responsabilité:</strong></td><td>${previewData.responsabilite_id || 'Non définie'}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6 class="text-primary">Description</h6>
                <div class="card">
                    <div class="card-body">
                        <h6>Résumé:</h6>
                        <p>${previewData.resume || 'Aucun résumé'}</p>
                        <h6>Commentaire:</h6>
                        <p>${previewData.commentaire || 'Aucun commentaire'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Afficher la modal d'aperçu
    const previewModal = new bootstrap.Modal(document.getElementById('previewIncidentModal'));
    previewModal.show();
}

/**
 * Collecter les données du formulaire
 */
function collectFormData() {
    return {
        type_id: parseInt(document.getElementById('incidentType').value) || null,
        sous_type_id: parseInt(document.getElementById('incidentSousType').value) || null,
        localisation_id: parseInt(document.getElementById('incidentLocation').value) || null,
        entite_id: parseInt(document.getElementById('incidentEntite').value) || null,
        source_id: parseInt(document.getElementById('incidentSource').value) || null,
        system_id: parseInt(document.getElementById('incidentSystem').value) || null,
        date_debut: document.getElementById('incidentDateDebut').value,
        date_fin: document.getElementById('incidentDateFin').value || null,
        heure_debut: document.getElementById('incidentHeureDebut').value || null,
        heure_fin: document.getElementById('incidentHeureFin').value || null,
        resume: document.getElementById('incidentResume').value,
        commentaire: document.getElementById('incidentCommentaire').value,
        etat: document.getElementById('incidentStatut').value,
        impact_service: document.getElementById('incidentImpact').value,
        fonction: document.getElementById('incidentFonction').value,
        responsabilite_id: document.getElementById('incidentResponsabilite').value,
        important: document.getElementById('incidentImportant').checked
    };
}

/**
 * Obtenir le texte d'un select
 */
function getSelectText(selectId, dataArray) {
    const select = document.getElementById(selectId);
    const value = select.value;
    if (!value) return 'Non sélectionné';
    
    const item = dataArray.find(item => item.id == value);
    return item ? item.intitule || item.nom : 'Non trouvé';
}

/**
 * Confirmer et sauvegarder après aperçu
 */
async function confirmSave() {
    // Fermer la modal d'aperçu
    const previewModal = bootstrap.Modal.getInstance(document.getElementById('previewIncidentModal'));
    previewModal.hide();
    
    // Sauvegarder
    if (selectedIncident) {
        await updateIncident();
    } else {
        await saveNewIncident();
    }
}

/**
 * Mettre à jour un incident existant (version améliorée)
 */
async function updateIncident() {
    if (!selectedIncident) {
        showNotification('Aucun incident sélectionné', 'error');
        return;
    }
    
    const form = document.getElementById('newIncidentForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    showLoading(true);
    
    try {
        const incidentData = collectFormData();
        
        console.log('📤 Données de modification:', incidentData);
        
        const response = await fetch(`${API_BASE}/evenements/${selectedIncident.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(incidentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Fermer la modal
            const modalElement = document.getElementById('newIncidentModal');
            const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            modal.hide();
            
            // Réinitialiser le formulaire et le titre
            resetForm();
            
            // Recharger les incidents
            await loadIncidents();
            applyFilters();
            
            showNotification('Incident modifié avec succès', 'success');
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la modification:', error);
        showNotification('Erreur lors de la modification de l\'incident', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Réinitialiser le formulaire
 */
function resetForm() {
    const form = document.getElementById('newIncidentForm');
    form.reset();
    
    // Réinitialiser le titre
    document.getElementById('modalTitle').textContent = 'Nouveau Incident';
    
    // Réinitialiser les boutons
    const saveButton = document.getElementById('saveButton');
    const previewButton = document.getElementById('previewButton');
    
    saveButton.innerHTML = '<i class="fas fa-save me-1"></i>Enregistrer';
    saveButton.onclick = saveNewIncident;
    saveButton.className = 'btn btn-primary';
    
    previewButton.innerHTML = '<i class="fas fa-eye me-1"></i>Aperçu';
    
    // Réinitialiser selectedIncident
    selectedIncident = null;
}

/**
 * Afficher/masquer le loading
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
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

// Fonctions globales pour les événements onclick
window.showIncidentDetails = showIncidentDetails;
window.goToPage = goToPage;
window.refreshIncidents = refreshIncidents;
window.applyFilters = applyFilters;
window.saveNewIncident = saveNewIncident;
window.editIncident = editIncident;
window.updateIncident = updateIncident;
window.previewIncident = previewIncident;
window.confirmSave = confirmSave;
window.resetForm = resetForm;