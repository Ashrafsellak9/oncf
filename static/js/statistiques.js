// ONCF EMS - Gestion des Statistiques

let charts = {};
let currentData = null;

// Initialisation de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Initialisation de la page des statistiques');
    
    // Charger les options de filtrage d'abord
    loadFilterOptions().then(() => {
        // Puis charger les statistiques
        loadStatistics();
    });
    
    setupEventListeners();
});

/**
 * Configurer les écouteurs d'événements
 */
function setupEventListeners() {
    // Filtres
    document.getElementById('periodSelect')?.addEventListener('change', updateCharts);
document.getElementById('regionSelect')?.addEventListener('change', updateCharts);
document.getElementById('typeSelect')?.addEventListener('change', updateCharts);
document.getElementById('statusSelect')?.addEventListener('change', updateCharts);
document.getElementById('gareTypeSelect')?.addEventListener('change', updateCharts);
document.getElementById('searchInput')?.addEventListener('input', debounce(updateCharts, 500));
document.getElementById('sortSelect')?.addEventListener('change', updateCharts);
document.getElementById('limitSelect')?.addEventListener('change', updateCharts);

// Fonction debounce pour optimiser les recherches
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
    
    // Bouton d'actualisation
    document.querySelector('button[onclick="updateCharts()"]')?.addEventListener('click', updateCharts);
}

/**
 * Charger les statistiques
 */
async function loadStatistics(filters = {}) {
    try {
        showLoading();
        
        console.log('📡 Chargement des statistiques...');
        
        const response = await fetch('/api/statistiques', {
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
            currentData = data.data;
            displayStatistics(data.data);
            createCharts(data.data);
            console.log('✅ Statistiques chargées avec succès');
        } else {
            throw new Error(data.error || 'Erreur lors du chargement des statistiques');
        }
    } catch (error) {
        console.error('❌ Erreur chargement statistiques:', error);
        showAlert('Erreur lors du chargement des statistiques. Veuillez réessayer.', 'danger');
        displayError();
    }
}

/**
 * Afficher les statistiques principales
 */
function displayStatistics(data) {
    // Statistiques principales
    document.getElementById('totalGares').textContent = data.gares?.total || 0;
    document.getElementById('totalArcs').textContent = data.arcs?.total || 0;
    document.getElementById('totalAxes').textContent = data.arcs?.par_axe?.length || 0;
    document.getElementById('totalVilles').textContent = data.gares?.par_region?.length || 0;
    
    // Tableaux détaillés
    displayTopAxesTable(data.arcs?.par_axe || []);
    displayTypeGaresTable(data.gares?.par_type || []);
}

/**
 * Afficher le tableau des axes les plus importants
 */
function displayTopAxesTable(axesData) {
    const tableBody = document.getElementById('topAxesTable');
    if (!tableBody) return;
    
    if (axesData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-muted">
                    <i class="fas fa-info-circle me-2"></i>
                    Aucune donnée disponible
                </td>
            </tr>
        `;
        return;
    }
    
    // Trier par nombre de gares décroissant et prendre les 10 premiers
    const sortedAxes = axesData
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);
    
    const totalGares = sortedAxes.reduce((sum, axe) => sum + axe.count, 0);
    
    let html = '';
    sortedAxes.forEach((axe, index) => {
        const percentage = totalGares > 0 ? ((axe.count / totalGares) * 100).toFixed(1) : 0;
        html += `
            <tr>
                <td>
                    <span class="badge bg-primary me-2">${index + 1}</span>
                    <strong>${axe.axe}</strong>
                </td>
                <td>
                    <span class="badge bg-info">${axe.count}</span>
                </td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar bg-success" style="width: ${percentage}%">
                            ${percentage}%
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

/**
 * Afficher le tableau des types de gares
 */
function displayTypeGaresTable(typesData) {
    const tableBody = document.getElementById('typeGaresTable');
    if (!tableBody) return;
    
    if (typesData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-muted">
                    <i class="fas fa-info-circle me-2"></i>
                    Aucune donnée disponible
                </td>
            </tr>
        `;
        return;
    }
    
    const totalGares = typesData.reduce((sum, type) => sum + type.count, 0);
    
    let html = '';
    typesData.forEach((type, index) => {
        const percentage = totalGares > 0 ? ((type.count / totalGares) * 100).toFixed(1) : 0;
        const colors = ['primary', 'success', 'warning', 'info', 'danger', 'secondary'];
        const color = colors[index % colors.length];
        
        html += `
            <tr>
                <td>
                    <span class="badge bg-${color} me-2">${index + 1}</span>
                    <strong>${type.type}</strong>
                </td>
                <td>
                    <span class="badge bg-${color}">${type.count}</span>
                </td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar bg-${color}" style="width: ${percentage}%">
                            ${percentage}%
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

/**
 * Créer les graphiques
 */
function createCharts(data) {
    try {
        console.log('📊 Création des graphiques...');
        
        // Graphique des types de gares
        createGaresTypeChart(data.gares?.par_type || []);
        
        // Graphique des axes
        createAxesChart(data.arcs?.par_axe || []);
        
        // Graphique d'évolution
        createTimelineChart(data);
        
        // Graphique d'état des gares
        createEtatChart(data.gares?.par_region || []);
        
        console.log('✅ Graphiques créés avec succès');
    } catch (error) {
        console.error('❌ Erreur lors de la création des graphiques:', error);
    }
}

/**
 * Créer le graphique des types de gares
 */
function createGaresTypeChart(typesData) {
    const ctx = document.getElementById('garesTypeChart');
    if (!ctx) {
        console.log('⚠️ Canvas garesTypeChart non trouvé');
        return;
    }
    
    try {
        // Détruire le graphique existant
        if (charts.garesType) {
            charts.garesType.destroy();
            charts.garesType = null;
        }
        
        // Vérifier que les données sont valides
        if (!Array.isArray(typesData) || typesData.length === 0) {
            console.log('⚠️ Aucune donnée pour le graphique des types de gares');
            return;
        }
        
        const labels = typesData.map(t => t.type || 'Non défini');
        const data = typesData.map(t => t.count);
        const colors = generateColors(labels.length);
        
        charts.garesType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Graphique des types de gares créé');
    } catch (error) {
        console.error('❌ Erreur lors de la création du graphique des types de gares:', error);
    }
}

/**
 * Créer le graphique des axes
 */
function createAxesChart(axesData) {
    const ctx = document.getElementById('axesChart');
    if (!ctx) {
        console.log('⚠️ Canvas axesChart non trouvé');
        return;
    }
    
    try {
        // Détruire le graphique existant
        if (charts.axes) {
            charts.axes.destroy();
            charts.axes = null;
        }
        
        // Vérifier que les données sont valides
        if (!Array.isArray(axesData) || axesData.length === 0) {
            console.log('⚠️ Aucune donnée pour le graphique des axes');
            return;
        }
        
        // Prendre les 10 premiers axes
        const topAxes = axesData
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);
        
        const labels = topAxes.map(a => a.axe || 'Non défini');
        const data = topAxes.map(a => a.count);
        
        charts.axes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Nombre de gares',
                    data: data,
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
        
        console.log('✅ Graphique des axes créé');
    } catch (error) {
        console.error('❌ Erreur lors de la création du graphique des axes:', error);
    }
}

/**
 * Créer le graphique d'évolution
 */
function createTimelineChart(data) {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) {
        console.log('⚠️ Canvas timelineChart non trouvé');
        return;
    }
    
    try {
        // Détruire le graphique existant
        if (charts.timeline) {
            charts.timeline.destroy();
            charts.timeline = null;
        }
        
        // Données simulées pour l'évolution (à adapter selon les vraies données)
        const labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
        const garesData = labels.map(() => Math.floor(Math.random() * 50) + (data.gares?.total || 100) * 0.8);
        const incidentsData = labels.map(() => Math.floor(Math.random() * 20) + 5);
        
        charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Gares',
                    data: garesData,
                    borderColor: 'rgba(13, 110, 253, 1)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Incidents',
                    data: incidentsData,
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        console.log('✅ Graphique d\'évolution créé');
    } catch (error) {
        console.error('❌ Erreur lors de la création du graphique d\'évolution:', error);
    }
}

/**
 * Créer le graphique d'état des gares
 */
function createEtatChart(regionsData) {
    const ctx = document.getElementById('etatChart');
    if (!ctx) {
        console.log('⚠️ Canvas etatChart non trouvé');
        return;
    }
    
    try {
        // Détruire le graphique existant
        if (charts.etat) {
            charts.etat.destroy();
            charts.etat = null;
        }
        
        // Vérifier que les données sont valides
        if (!Array.isArray(regionsData) || regionsData.length === 0) {
            console.log('⚠️ Aucune donnée pour le graphique d\'état des gares');
            return;
        }
        
        const labels = regionsData.map(r => r.region || 'Non définie');
        const data = regionsData.map(r => r.count);
        const colors = generateColors(labels.length);
        
        charts.etat = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        
        console.log('✅ Graphique d\'état des gares créé');
    } catch (error) {
        console.error('❌ Erreur lors de la création du graphique d\'état des gares:', error);
    }
}

/**
 * Mettre à jour l'indicateur de filtres actifs
 */
function updateFilterIndicator(filters) {
    const activeFilters = [];
    
    if (filters.period && filters.period !== 'all') {
        activeFilters.push(`Période: ${filters.period}`);
    }
    if (filters.region) {
        activeFilters.push(`Région: ${filters.region}`);
    }
    if (filters.status) {
        activeFilters.push(`Statut: ${filters.status}`);
    }
    if (filters.gareType) {
        activeFilters.push(`Type: ${filters.gareType}`);
    }
    if (filters.search) {
        activeFilters.push(`Recherche: "${filters.search}"`);
    }
    
    const filterIndicator = document.getElementById('filterIndicator');
    if (filterIndicator) {
        if (activeFilters.length > 0) {
            filterIndicator.innerHTML = `
                <div class="alert alert-info alert-dismissible fade show" role="alert">
                    <i class="fas fa-filter me-2"></i>
                    <strong>Filtres actifs:</strong> ${activeFilters.join(', ')}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            filterIndicator.style.display = 'block';
        } else {
            filterIndicator.style.display = 'none';
        }
    }
}

/**
 * Charger les options de filtrage dynamiques
 */
async function loadFilterOptions() {
    try {
        console.log('📡 Chargement des options de filtrage...');
        
        // Charger les régions depuis l'API des gares
        const garesResponse = await fetch('/api/gares/filters');
        if (garesResponse.ok) {
            const garesData = await garesResponse.json();
            if (garesData.success) {
                updateRegionOptions(garesData.data.regions);
            }
        }
        
        // Charger les types de gares
        const statsResponse = await fetch('/api/statistiques');
        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            if (statsData.success) {
                updateGareTypeOptions(statsData.data.gares?.par_type || []);
            }
        }
        
    } catch (error) {
        console.error('❌ Erreur lors du chargement des options de filtrage:', error);
    }
}

/**
 * Mettre à jour les options de régions
 */
function updateRegionOptions(regions) {
    const regionSelect = document.getElementById('regionSelect');
    if (regionSelect && regions) {
        // Garder l'option par défaut
        const defaultOption = regionSelect.querySelector('option[value=""]');
        regionSelect.innerHTML = '';
        if (defaultOption) {
            regionSelect.appendChild(defaultOption);
        }
        
        // Ajouter les nouvelles options
        regions.forEach(region => {
            if (region) {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                regionSelect.appendChild(option);
            }
        });
    }
}

/**
 * Mettre à jour les options de types de gares
 */
function updateGareTypeOptions(gareTypes) {
    const gareTypeSelect = document.getElementById('gareTypeSelect');
    if (gareTypeSelect && gareTypes) {
        // Garder l'option par défaut
        const defaultOption = gareTypeSelect.querySelector('option[value=""]');
        gareTypeSelect.innerHTML = '';
        if (defaultOption) {
            gareTypeSelect.appendChild(defaultOption);
        }
        
        // Ajouter les nouvelles options
        gareTypes.forEach(type => {
            if (type.type) {
                const option = document.createElement('option');
                option.value = type.type;
                option.textContent = `${type.type} (${type.count})`;
                gareTypeSelect.appendChild(option);
            }
        });
    }
}

/**
 * Mettre à jour les graphiques
 */
function updateCharts() {
    console.log('🔄 Mise à jour des graphiques avec filtres...');
    
    // Récupérer les valeurs des filtres
    const filters = {
        period: document.getElementById('periodSelect')?.value || 'all',
        region: document.getElementById('regionSelect')?.value || '',
        type: document.getElementById('typeSelect')?.value || 'gares',
        status: document.getElementById('statusSelect')?.value || '',
        gareType: document.getElementById('gareTypeSelect')?.value || '',
        search: document.getElementById('searchInput')?.value || '',
        sort: document.getElementById('sortSelect')?.value || 'name',
        limit: document.getElementById('limitSelect')?.value || '25'
    };
    
    console.log('📊 Filtres appliqués:', filters);
    
    // Charger les statistiques avec les filtres
    loadStatistics(filters);
}

function resetFilters() {
    console.log('🔄 Réinitialisation des filtres...');
    
    // Réinitialiser tous les filtres
    document.getElementById('periodSelect').value = 'all';
    document.getElementById('regionSelect').value = '';
    document.getElementById('typeSelect').value = 'gares';
    document.getElementById('statusSelect').value = '';
    document.getElementById('gareTypeSelect').value = '';
    document.getElementById('searchInput').value = '';
    document.getElementById('sortSelect').value = 'name';
    document.getElementById('limitSelect').value = '25';
    
    // Mettre à jour les graphiques
    updateCharts();
    
    // Afficher un message de confirmation
    showAlert('Filtres réinitialisés avec succès', 'success');
}

/**
 * Générer des couleurs pour les graphiques
 */
function generateColors(count) {
    const colors = [
        '#007bff', '#28a745', '#ffc107', '#17a2b8', '#dc3545',
        '#6f42c1', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

/**
 * Afficher le loading
 */
function showLoading() {
    const containers = ['totalGares', 'totalArcs', 'totalAxes', 'totalVilles'];
    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        }
    });
}

/**
 * Afficher une erreur
 */
function displayError() {
    const containers = ['totalGares', 'totalArcs', 'totalAxes', 'totalVilles'];
    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '<span class="text-danger">Erreur</span>';
        }
    });
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
