// ONCF EMS - Gestion des Données de Référence

let currentTab = 'types';
let currentTypeId = null;

// Initialisation de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation de la page de référence');
    loadReferenceData('types');
    
    // Gestion des onglets
    setupTabs();
});

/**
 * Configurer les onglets
 */
function setupTabs() {
    const tabLinks = document.querySelectorAll('[data-tab]');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tab = this.getAttribute('data-tab');
            switchTab(tab);
        });
    });
}

/**
 * Changer d'onglet
 */
function switchTab(tab) {
    // Mettre à jour les onglets actifs
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    // Mettre à jour le contenu
    document.querySelectorAll('.tab-pane').forEach(content => {
        content.classList.remove('show', 'active');
    });
    document.getElementById(`${tab}Tab`).classList.add('show', 'active');
    
    currentTab = tab;
    loadReferenceData(tab);
}

/**
 * Charger les données de référence
 */
async function loadReferenceData(type) {
    try {
        showLoading(type);
        
        let endpoint = '';
        switch(type) {
            case 'types':
                endpoint = '/api/reference/types';
                break;
            case 'sous-types':
                endpoint = '/api/reference/sous-types';
                if (currentTypeId) {
                    endpoint += `?type_id=${currentTypeId}`;
                }
                break;
            case 'systemes':
                endpoint = '/api/reference/systemes';
                break;
            case 'sources':
                endpoint = '/api/reference/sources';
                break;
            case 'entites':
                endpoint = '/api/reference/entites';
                break;
            default:
                throw new Error('Type de référence inconnu');
        }
        
        console.log(`📡 Chargement des données de référence: ${type}`);
        
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
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
            displayReferenceData(type, data.data);
            console.log(`✅ ${data.data.length} éléments chargés pour ${type}`);
        } else {
            throw new Error(data.error || 'Erreur lors du chargement des données');
        }
    } catch (error) {
        console.error(`❌ Erreur chargement ${type}:`, error);
        showAlert(`Erreur lors du chargement des ${type}. Veuillez réessayer.`, 'danger');
        displayError(type);
    }
}

/**
 * Afficher les données de référence
 */
function displayReferenceData(type, data) {
    const container = document.getElementById(`${type}Container`);
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                Aucune donnée trouvée
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-striped table-hover">';
    
    // En-têtes selon le type
    switch(type) {
        case 'types':
            html += `
                <thead class="table-dark">
                    <tr>
                        <th><i class="fas fa-hashtag"></i> ID</th>
                        <th><i class="fas fa-tag"></i> Intitulé</th>
                        <th><i class="fas fa-link"></i> Entité Type ID</th>
                        <th><i class="fas fa-calendar"></i> Date MAJ</th>
                        <th><i class="fas fa-toggle-on"></i> État</th>
                        <th><i class="fas fa-cogs"></i> Actions</th>
                    </tr>
                </thead>
                <tbody>
            `;
            data.forEach(item => {
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${item.id}</span></td>
                        <td><strong>${item.intitule || 'N/A'}</strong></td>
                        <td>${item.entite_type_id || 'N/A'}</td>
                        <td>${item.date_maj ? new Date(item.date_maj).toLocaleDateString('fr-FR') : 'N/A'}</td>
                        <td>
                            <span class="badge bg-${item.etat === 't' ? 'success' : 'secondary'}">
                                ${item.etat === 't' ? 'Actif' : 'Inactif'}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="filterSousTypes(${item.id})">
                                <i class="fas fa-filter"></i> Filtrer
                            </button>
                        </td>
                    </tr>
                `;
            });
            break;
            
        case 'sous-types':
            html += `
                <thead class="table-dark">
                    <tr>
                        <th><i class="fas fa-hashtag"></i> ID</th>
                        <th><i class="fas fa-tag"></i> Intitulé</th>
                        <th><i class="fas fa-link"></i> Type ID</th>
                        <th><i class="fas fa-calendar"></i> Date MAJ</th>
                        <th><i class="fas fa-toggle-on"></i> État</th>
                    </tr>
                </thead>
                <tbody>
            `;
            data.forEach(item => {
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${item.id}</span></td>
                        <td><strong>${item.intitule || 'N/A'}</strong></td>
                        <td>${item.type_id || 'N/A'}</td>
                        <td>${item.date_maj ? new Date(item.date_maj).toLocaleDateString('fr-FR') : 'N/A'}</td>
                        <td>
                            <span class="badge bg-${item.etat === 't' ? 'success' : 'secondary'}">
                                ${item.etat === 't' ? 'Actif' : 'Inactif'}
                            </span>
                        </td>
                    </tr>
                `;
            });
            break;
            
        case 'systemes':
            html += `
                <thead class="table-dark">
                    <tr>
                        <th><i class="fas fa-hashtag"></i> ID</th>
                        <th><i class="fas fa-cogs"></i> Intitulé</th>
                        <th><i class="fas fa-link"></i> Entité ID</th>
                        <th><i class="fas fa-calendar"></i> Date MAJ</th>
                        <th><i class="fas fa-toggle-on"></i> État</th>
                    </tr>
                </thead>
                <tbody>
            `;
            data.forEach(item => {
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${item.id}</span></td>
                        <td><strong>${item.intitule || 'N/A'}</strong></td>
                        <td>${item.entite_id || 'N/A'}</td>
                        <td>${item.date_maj ? new Date(item.date_maj).toLocaleDateString('fr-FR') : 'N/A'}</td>
                        <td>
                            <span class="badge bg-${item.etat === 't' ? 'success' : 'secondary'}">
                                ${item.etat === 't' ? 'Actif' : 'Inactif'}
                            </span>
                        </td>
                    </tr>
                `;
            });
            break;
            
        case 'sources':
            html += `
                <thead class="table-dark">
                    <tr>
                        <th><i class="fas fa-hashtag"></i> ID</th>
                        <th><i class="fas fa-info-circle"></i> Intitulé</th>
                        <th><i class="fas fa-link"></i> Entité Source ID</th>
                        <th><i class="fas fa-calendar"></i> Date MAJ</th>
                        <th><i class="fas fa-toggle-on"></i> État</th>
                    </tr>
                </thead>
                <tbody>
            `;
            data.forEach(item => {
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${item.id}</span></td>
                        <td><strong>${item.intitule || 'N/A'}</strong></td>
                        <td>${item.entite_source_id || 'N/A'}</td>
                        <td>${item.date_maj ? new Date(item.date_maj).toLocaleDateString('fr-FR') : 'N/A'}</td>
                        <td>
                            <span class="badge bg-${item.etat === 't' ? 'success' : 'secondary'}">
                                ${item.etat === 't' ? 'Actif' : 'Inactif'}
                            </span>
                        </td>
                    </tr>
                `;
            });
            break;
            
        case 'entites':
            html += `
                <thead class="table-dark">
                    <tr>
                        <th><i class="fas fa-hashtag"></i> ID</th>
                        <th><i class="fas fa-building"></i> Intitulé</th>
                    </tr>
                </thead>
                <tbody>
            `;
            data.forEach(item => {
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${item.id}</span></td>
                        <td><strong>${item.intitule || 'N/A'}</strong></td>
                    </tr>
                `;
            });
            break;
    }
    
    html += '</tbody></table></div>';
    
    // Ajouter des statistiques
    html += `
        <div class="mt-3">
            <div class="alert alert-success">
                <i class="fas fa-chart-bar"></i>
                <strong>Statistiques :</strong> ${data.length} élément(s) trouvé(s)
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Mettre à jour le compteur
    const countElement = document.getElementById(`${type}Count`);
    if (countElement) {
        countElement.textContent = `${data.length} élément(s)`;
    }
}

/**
 * Filtrer les sous-types par type
 */
function filterSousTypes(typeId) {
    currentTypeId = typeId;
    if (currentTab === 'sous-types') {
        loadReferenceData('sous-types');
    } else {
        // Changer vers l'onglet sous-types et filtrer
        switchTab('sous-types');
        setTimeout(() => {
            loadReferenceData('sous-types');
        }, 100);
    }
}

/**
 * Effacer le filtre des sous-types
 */
function clearSousTypesFilter() {
    currentTypeId = null;
    loadReferenceData('sous-types');
}

/**
 * Afficher un message d'erreur
 */
function displayError(type) {
    const container = document.getElementById(`${type}Container`);
    container.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i>
            Erreur lors du chargement des données
            <br>
            <button class="btn btn-sm btn-outline-danger mt-2" onclick="loadReferenceData('${type}')">
                <i class="fas fa-redo"></i> Réessayer
            </button>
        </div>
    `;
}

/**
 * Afficher/masquer le loading
 */
function showLoading(type) {
    const container = document.getElementById(`${type}Container`);
    container.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-2 text-muted">Chargement des données de référence...</p>
        </div>
    `;
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
