// ONCF EMS - Gestion des Axes Ferroviaires

let currentPage = 1;
let currentSearch = '';
let totalPages = 1;
let totalAxes = 0;
let currentAxesData = []; // Stocker les données actuelles des axes

// Initialisation de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation de la page des axes');
    loadAxes();
});

/**
 * Charger les axes depuis l'API
 */
async function loadAxes(page = 1, search = '') {
    try {
        showLoading(true);
        
        const params = new URLSearchParams({
            page: page,
            per_page: 50
        });
        
        if (search) {
            params.append('search', search);
        }
        
        console.log(`📡 Chargement des axes - Page ${page}, Recherche: "${search}"`);
        
        const response = await fetch(`/api/axes?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin' // Inclure les cookies de session
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAlert('Session expirée. Veuillez vous reconnecter.', 'warning');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayAxes(data.data);
            displayPagination(data.pagination);
            currentPage = page;
            currentSearch = search;
            totalPages = data.pagination.pages;
            totalAxes = data.pagination.total;
            currentAxesData = data.data; // Stocker les données actuelles
            
            console.log(`✅ ${data.data.length} axes chargés (Total: ${totalAxes})`);
        } else {
            throw new Error(data.error || 'Erreur lors du chargement des données');
        }
    } catch (error) {
        console.error('❌ Erreur chargement axes:', error);
        showAlert('Erreur lors du chargement des axes. Veuillez réessayer.', 'danger');
        displayError();
    } finally {
        showLoading(false);
    }
}

/**
 * Afficher les axes dans le tableau
 */
function displayAxes(axes) {
    const tbody = document.getElementById('axesTableBody');
    tbody.innerHTML = '';
    
    if (axes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Aucun axe trouvé</strong>
                        <br>
                        <small class="text-muted">Essayez de modifier vos critères de recherche</small>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    axes.forEach((axe, index) => {
        const row = document.createElement('tr');
        row.className = 'fade-in-up';
        row.style.animationDelay = `${index * 0.1}s`;
        
        // Déterminer le type d'axe pour la couleur du badge
        const axeType = getAxeType(axe.axe);
        const badgeClass = getBadgeClass(axeType);
        
        row.innerHTML = `
            <td>
                <span class="badge ${badgeClass}">
                    <i class="fas fa-hashtag me-1"></i>${axe.axe_id || axe.id}
                </span>
            </td>
            <td>
                <a href="#" onclick="showAxeDetails(${axe.id})" class="text-decoration-none">
                    <div class="d-flex align-items-center">
                        <div class="me-3">
                            <i class="fas fa-route text-primary fs-5"></i>
                        </div>
                        <div>
                            <div class="fw-bold text-primary">${axe.nom_axe || 'N/A'}</div>
                            <small class="text-muted">${getAxeDescription(axe.nom_axe)}</small>
                        </div>
                    </div>
                </a>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-play text-success me-2"></i>
                    <span class="fw-semibold">${axe.pk_debut ? axe.pk_debut.toFixed(3) : 'N/A'}</span>
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-stop text-danger me-2"></i>
                    <span class="fw-semibold">${axe.pk_fin ? axe.pk_fin.toFixed(3) : 'N/A'}</span>
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-arrow-up text-warning me-2"></i>
                    <span class="fw-semibold">${axe.plod || 'N/A'}</span>
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-arrow-down text-info me-2"></i>
                    <span class="fw-semibold">${axe.plof || 'N/A'}</span>
                </div>
            </td>
            <td>
                ${axe.geometrie ? 
                    '<span class="badge bg-success"><i class="fas fa-map-marker-alt me-1"></i>Géométrie</span>' : 
                    '<span class="badge bg-secondary"><i class="fas fa-times me-1"></i>Aucune</span>'
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Déterminer le type d'axe basé sur le nom
 */
function getAxeType(axeName) {
    if (!axeName) return 'default';
    
    const name = axeName.toLowerCase();
    if (name.includes('casa') || name.includes('marrakech')) return 'principal';
    if (name.includes('rabat') || name.includes('fes')) return 'secondaire';
    if (name.includes('tanger') || name.includes('oujda')) return 'regional';
    return 'default';
}

/**
 * Obtenir la classe de badge appropriée
 */
function getBadgeClass(axeType) {
    switch (axeType) {
        case 'principal': return 'bg-primary';
        case 'secondaire': return 'bg-success';
        case 'regional': return 'bg-warning';
        default: return 'bg-secondary';
    }
}

/**
 * Obtenir une description courte de l'axe
 */
function getAxeDescription(axeName) {
    if (!axeName) return 'Ligne ferroviaire';
    
    const name = axeName.toLowerCase();
    if (name.includes('casa') && name.includes('marrakech')) return 'Ligne principale Casa-Marrakech';
    if (name.includes('nouaceur') && name.includes('eljadida')) return 'Ligne Nouaceur-El Jadida';
    if (name.includes('benguerir') && name.includes('safi')) return 'Ligne Benguerir-Safi';
    if (name.includes('casavoyageurs') && name.includes('skacem')) return 'Ligne Casa Voyageurs-Skacem';
    if (name.includes('bni.ansart') && name.includes('taourirt')) return 'Ligne Bni Ansart-Taourirt';
    if (name.includes('tanger') && name.includes('fes')) return 'Ligne Tanger-Fès';
    if (name.includes('rabat') && name.includes('fes')) return 'Ligne Rabat-Fès';
    return 'Ligne ferroviaire';
}

/**
 * Afficher la pagination
 */
function displayPagination(pagination) {
    const paginationInfo = document.getElementById('paginationInfo');
    const paginationElement = document.getElementById('pagination');
    
    if (pagination.total > 0) {
        const start = ((pagination.page - 1) * pagination.per_page) + 1;
        const end = Math.min(pagination.page * pagination.per_page, pagination.total);
        paginationInfo.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Affichage de ${start} à ${end}</strong> sur <strong>${pagination.total} axes</strong>
        `;
    } else {
        paginationInfo.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Aucun axe trouvé</strong>
        `;
    }
    
    paginationElement.innerHTML = '';
    
    // Bouton précédent
    if (pagination.has_prev) {
        const prevLi = document.createElement('li');
        prevLi.className = 'page-item';
        prevLi.innerHTML = `
            <a class="page-link" href="#" onclick="loadAxes(${pagination.page - 1}, currentSearch)">
                <i class="fas fa-chevron-left me-1"></i>Précédent
            </a>
        `;
        paginationElement.appendChild(prevLi);
    }
    
    // Pages
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === pagination.page ? 'active' : ''}`;
        pageLi.innerHTML = `
            <a class="page-link" href="#" onclick="loadAxes(${i}, currentSearch)">${i}</a>
        `;
        paginationElement.appendChild(pageLi);
    }
    
    // Bouton suivant
    if (pagination.has_next) {
        const nextLi = document.createElement('li');
        nextLi.className = 'page-item';
        nextLi.innerHTML = `
            <a class="page-link" href="#" onclick="loadAxes(${pagination.page + 1}, currentSearch)">
                Suivant<i class="fas fa-chevron-right ms-1"></i>
            </a>
        `;
        paginationElement.appendChild(nextLi);
    }
}

/**
 * Rechercher des axes
 */
function searchAxes() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.trim();
    
    console.log(`🔍 Recherche: "${searchTerm}"`);
    loadAxes(1, searchTerm);
}

/**
 * Afficher les détails d'un axe
 */
function showAxeDetails(axeId) {
    console.log(`📋 Affichage des détails de l'axe ${axeId}`);
    
    // Trouver l'axe dans les données actuelles
    const currentAxes = getCurrentAxesData();
    const axe = currentAxes.find(a => a.id === axeId);
    
    const modal = new bootstrap.Modal(document.getElementById('axeModal'));
    const modalBody = document.getElementById('axeModalBody');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-2 text-muted">Chargement des détails...</p>
        </div>
    `;
    
    modal.show();
    
    // Simuler le chargement des détails
    setTimeout(() => {
                 if (axe) {
             const axeType = getAxeType(axe.nom_axe);
             const badgeClass = getBadgeClass(axeType);
             
             modalBody.innerHTML = `
                 <div class="fade-in-up">
                     <!-- En-tête de l'axe -->
                     <div class="text-center mb-4">
                         <div class="mb-3">
                             <span class="badge ${badgeClass} fs-6">
                                 <i class="fas fa-route me-2"></i>Axe #${axe.axe_id || axe.id}
                             </span>
                         </div>
                         <h4 class="text-primary mb-2">${axe.nom_axe || 'Nom non disponible'}</h4>
                         <p class="text-muted mb-0">${getAxeDescription(axe.nom_axe)}</p>
                     </div>
                    
                    <!-- Informations principales -->
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <div class="card h-100 border-0 bg-light">
                                <div class="card-body text-center">
                                    <div class="mb-2">
                                        <i class="fas fa-play-circle text-success fs-3"></i>
                                    </div>
                                                                         <h6 class="card-title text-success">Point Kilométrique Début</h6>
                                     <p class="card-text fs-5 fw-bold">${axe.pk_debut ? axe.pk_debut.toFixed(3) : 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card h-100 border-0 bg-light">
                                <div class="card-body text-center">
                                    <div class="mb-2">
                                        <i class="fas fa-stop-circle text-danger fs-3"></i>
                                    </div>
                                                                         <h6 class="card-title text-danger">Point Kilométrique Fin</h6>
                                     <p class="card-text fs-5 fw-bold">${axe.pk_fin ? axe.pk_fin.toFixed(3) : 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                                         <!-- Informations secondaires -->
                     <div class="row g-3 mb-4">
                         <div class="col-md-3">
                             <div class="card h-100 border-0 bg-light">
                                 <div class="card-body text-center">
                                     <div class="mb-2">
                                         <i class="fas fa-arrow-up text-warning fs-3"></i>
                                     </div>
                                     <h6 class="card-title text-warning">PLOD</h6>
                                     <p class="card-text fs-5 fw-bold">${axe.plod || 'N/A'}</p>
                                 </div>
                             </div>
                         </div>
                         <div class="col-md-3">
                             <div class="card h-100 border-0 bg-light">
                                 <div class="card-body text-center">
                                     <div class="mb-2">
                                         <i class="fas fa-arrow-down text-info fs-3"></i>
                                     </div>
                                     <h6 class="card-title text-info">PLOF</h6>
                                     <p class="card-text fs-5 fw-bold">${axe.plof || 'N/A'}</p>
                                 </div>
                             </div>
                         </div>
                         <div class="col-md-3">
                             <div class="card h-100 border-0 bg-light">
                                 <div class="card-body text-center">
                                     <div class="mb-2">
                                         <i class="fas fa-arrow-right text-primary fs-3"></i>
                                     </div>
                                     <h6 class="card-title text-primary">ABSD</h6>
                                     <p class="card-text fs-5 fw-bold">${axe.absd ? axe.absd.toFixed(3) : 'N/A'}</p>
                                 </div>
                             </div>
                         </div>
                         <div class="col-md-3">
                             <div class="card h-100 border-0 bg-light">
                                 <div class="card-body text-center">
                                     <div class="mb-2">
                                         <i class="fas fa-arrow-left text-secondary fs-3"></i>
                                     </div>
                                     <h6 class="card-title text-secondary">ABSF</h6>
                                     <p class="card-text fs-5 fw-bold">${axe.absf ? axe.absf.toFixed(3) : 'N/A'}</p>
                                 </div>
                             </div>
                         </div>
                     </div>
                    
                    <!-- Géométrie -->
                    <div class="card border-0 bg-light">
                        <div class="card-body text-center">
                            <div class="mb-2">
                                <i class="fas fa-map-marked-alt ${axe.geometrie ? 'text-success' : 'text-secondary'} fs-3"></i>
                            </div>
                            <h6 class="card-title">Géométrie</h6>
                            <p class="card-text">
                                ${axe.geometrie ? 
                                    '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Géométrie disponible</span>' : 
                                    '<span class="badge bg-secondary"><i class="fas fa-times me-1"></i>Aucune géométrie</span>'
                                }
                            </p>
                        </div>
                    </div>
                    
                    <!-- Actions -->
                    <div class="text-center mt-4">
                        <button type="button" class="btn btn-outline-primary me-2" onclick="viewAxeOnMap(${axe.id})">
                            <i class="fas fa-map me-2"></i>Voir sur la carte
                        </button>
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>Fermer
                        </button>
                    </div>
                </div>
            `;
        } else {
            modalBody.innerHTML = `
                <div class="alert alert-warning text-center">
                    <i class="fas fa-exclamation-triangle fs-1 text-warning mb-3"></i>
                    <h5>Axe non trouvé</h5>
                    <p class="mb-0">Impossible de récupérer les détails de l'axe #${axeId}.</p>
                </div>
            `;
        }
    }, 1000);
}

/**
 * Obtenir les données actuelles des axes (pour le modal)
 */
function getCurrentAxesData() {
    return currentAxesData;
}

/**
 * Voir l'axe sur la carte (fonction à implémenter)
 */
function viewAxeOnMap(axeId) {
    console.log(`🗺️ Affichage de l'axe ${axeId} sur la carte`);
    // Rediriger vers la page carte avec l'axe sélectionné
    window.location.href = `/carte?axe=${axeId}`;
}

/**
 * Afficher un message d'erreur
 */
function displayError() {
    const tbody = document.getElementById('axesTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Erreur lors du chargement des données
                    <br>
                    <button class="btn btn-sm btn-outline-danger mt-2" onclick="loadAxes()">
                        <i class="fas fa-redo"></i> Réessayer
                    </button>
                </div>
            </td>
        </tr>
    `;
}

/**
 * Afficher/masquer le loading
 */
function showLoading(show) {
    const tbody = document.getElementById('axesTableBody');
    
    if (show) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <p class="mt-2 text-muted">Chargement des axes...</p>
                </td>
            </tr>
        `;
    }
}

/**
 * Afficher une alerte
 */
function showAlert(message, type = 'info') {
    // Créer une alerte Bootstrap
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insérer au début du contenu
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-supprimer après 5 secondes
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Gestion de la recherche avec Enter
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchAxes();
            }
        });
    }
});
