// ============================================================================
// GLOBAL STATE
// ============================================================================

const fileStorage = {
    scope: [],
    spec: [],
    drawing: [],
    assembly: []
};

let currentData = null;
let currentView = 'table'; // Default to table view
let workflowStates = {};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeFileInputs();
    loadWorkflowStates();
    loadSavedSession();
});

function initializeFileInputs() {
    const fileInputs = ['scope', 'spec', 'drawing', 'assembly'];
    
    fileInputs.forEach(type => {
        const input = document.getElementById(type);
        
        input.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            
            if (type === 'drawing' || type === 'assembly') {
                fileStorage[type] = [...fileStorage[type], ...files];
            } else {
                fileStorage[type] = files;
            }
            
            displayFiles(type);
        });
    });
}

// ============================================================================
// FILE HANDLING
// ============================================================================

function displayFiles(type) {
    const list = document.getElementById(`${type}-list`);
    const files = fileStorage[type];
    
    if (files.length === 0) {
        list.innerHTML = '';
        return;
    }
    
    list.innerHTML = files.map((file, index) => `
        <div class="file-item">
            <span>${file.name}</span>
            <span class="remove-file" onclick="removeFile('${type}', ${index})">✕</span>
        </div>
    `).join('');
}

window.removeFile = function(type, index) {
    fileStorage[type].splice(index, 1);
    displayFiles(type);
    
    if (fileStorage[type].length === 0) {
        document.getElementById(type).value = '';
    }
}

// ============================================================================
// FORM SUBMISSION
// ============================================================================

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInputs = ['scope', 'spec', 'drawing', 'assembly'];
    
    fileInputs.forEach(type => {
        fileStorage[type].forEach(file => {
            formData.append(type, file);
        });
    });
    
    document.getElementById('loading').classList.add('show');
    document.getElementById('results').classList.remove('show');
    
    try {
        const response = await fetch('/parse', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentData = data;
        saveSession(data);
        
        document.getElementById('loading').classList.remove('show');
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').classList.remove('show');
        showNotification('Error parsing documents', 'error');
    }
});

// ============================================================================
// WORKFLOW STATE MANAGEMENT
// ============================================================================

function getWorkflowState(sheetId) {
    return workflowStates[sheetId] || 'detected';
}

function setWorkflowState(sheetId, state) {
    workflowStates[sheetId] = state;
    saveWorkflowStates();
    displayResults(currentData);
}

function saveWorkflowStates() {
    try {
        localStorage.setItem('workflowStates', JSON.stringify(workflowStates));
    } catch (e) {
        console.warn('Could not save workflow states');
    }
}

function loadWorkflowStates() {
    try {
        const saved = localStorage.getItem('workflowStates');
        if (saved) {
            workflowStates = JSON.parse(saved);
        }
    } catch (e) {
        console.warn('Could not load workflow states');
    }
}

// ============================================================================
// SESSION MANAGEMENT
// ============================================================================

function saveSession(data) {
    try {
        localStorage.setItem('drawingParserSession', JSON.stringify({
            data: data,
            timestamp: new Date().toISOString()
        }));
    } catch (e) {
        console.warn('Could not save session');
    }
}

function loadSavedSession() {
    try {
        const saved = localStorage.getItem('drawingParserSession');
        if (saved) {
            const session = JSON.parse(saved);
            const savedDate = new Date(session.timestamp);
            const daysSince = (new Date() - savedDate) / (1000 * 60 * 60 * 24);
            
            if (daysSince < 7) {
                // Session available but don't auto-load
            }
        }
    } catch (e) {
        console.warn('Could not load session');
    }
}

window.clearSession = function() {
    if (confirm('Clear all saved data?')) {
        localStorage.removeItem('drawingParserSession');
        localStorage.removeItem('workflowStates');
        workflowStates = {};
        showNotification('Session cleared', 'info');
        document.getElementById('results').classList.remove('show');
    }
}

// ============================================================================
// VIEW SWITCHING
// ============================================================================

window.switchView = function(view) {
    currentView = view;
    displayResults(currentData);
    showNotification(`Switched to ${view} view`, 'info');
}

// ============================================================================
// DISPLAY RESULTS
// ============================================================================

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    let html = '';
    
    if (data.drawing) {
        html += renderDrawingResults(data.drawing);
    }
    
    if (data.spec) {
        html += renderSpecResults(data.spec);
    }
    
    if (data.assembly) {
        html += renderAssemblyResults(data.assembly);
    }
    
    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('show');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================================
// SPECIFICATION RESULTS
// ============================================================================

function renderSpecResults(specs) {
    if (!specs || specs.length === 0) {
        return '';
    }
    
    const stats = calculateSpecStats(specs);
    
    let html = `
        <div class="toolbar">
            <div class="toolbar-top">
                <h2>📄 Specification Documents</h2>
                <div class="toolbar-actions">
                    <button class="toolbar-btn ${currentView === 'table' ? 'active' : ''}" onclick="switchView('table')">
                        📊 Table
                    </button>
                    <button class="toolbar-btn ${currentView === 'cards' ? 'active' : ''}" onclick="switchView('cards')">
                        🎴 Cards
                    </button>
                    <button class="toolbar-btn" onclick="exportSpecToCSV()">
                        📥 Export
                    </button>
                </div>
            </div>
            
            <input type="text" class="search-bar" placeholder="🔍 Search specifications..." oninput="filterSpecData(this.value)">
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${specs.length}</div>
                <div class="stat-label">Specifications</div>
            </div>
            <div class="stat-card orange">
                <div class="stat-value">${stats.totalManufacturers}</div>
                <div class="stat-label">Manufacturers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.totalProducts}</div>
                <div class="stat-label">Products</div>
            </div>
            <div class="stat-card orange">
                <div class="stat-value">${stats.totalShopDrawingReqs}</div>
                <div class="stat-label">Shop Drawing Requirements</div>
            </div>
        </div>
    `;
    
    html += currentView === 'table' ? renderSpecTableView(specs) : renderSpecCardsView(specs);
    
    return html;
}

function calculateSpecStats(specs) {
    let totalManufacturers = 0;
    let totalProducts = 0;
    let totalShopDrawingReqs = 0;
    
    specs.forEach(spec => {
        if (!spec.error) {
            totalManufacturers += spec.manufacturers ? spec.manufacturers.length : 0;
            totalProducts += spec.products ? spec.products.length : 0;
            totalShopDrawingReqs += spec.shop_drawing_requirements ? spec.shop_drawing_requirements.length : 0;
        }
    });
    
    return {
        totalManufacturers,
        totalProducts,
        totalShopDrawingReqs
    };
}

function renderSpecTableView(specs) {
    let html = `
        <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #1e2a3a; color: white;">
                        <th style="padding: 1rem; text-align: left; font-weight: 600; border-radius: 8px 0 0 0;">File</th>
                        <th style="padding: 1rem; text-align: left; font-weight: 600;">Section</th>
                        <th style="padding: 1rem; text-align: left; font-weight: 600;">Title</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">👨‍🏭 Manufacturers</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">🛠️ Products</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">🔍 Shop Drawing Reqs</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; border-radius: 0 8px 0 0;">Actions</th>
                    </tr>
                </thead>
                <tbody id="specTableBody">
    `;
    
    specs.forEach((spec, specIdx) => {
        if (spec.error) {
            html += `
                <tr class="spec-row" data-file="${spec.filename}" style="background: #fff1f0;">
                    <td style="padding: 0.75rem; color: #e53e3e; font-weight: 500; font-size: 0.875rem;">${spec.filename}</td>
                    <td colspan="6" style="padding: 0.75rem; color: #e53e3e;">Error: ${spec.error}</td>
                </tr>
            `;
        } else {
            const rowClass = specIdx % 2 === 0 ? 'background: #f7fafc;' : 'background: white;';
            
            const section = spec.spec_section || spec.section || '-';
            const title = spec.spec_title || spec.title || '-';

            html += `
                <tr class="spec-row" data-file="${spec.filename}" data-section="${section}" style="${rowClass}">
                    <td style="padding: 0.75rem; color: #2d3748; font-weight: 500; font-size: 0.875rem;">${spec.filename}</td>
                    <td style="padding: 0.75rem; color: #4a5568; font-family: monospace; font-weight: 600;">${section}</td>
                    <td style="padding: 0.75rem; color: #718096; font-size: 0.875rem;">${title}</td>
                    <td style="padding: 0.75rem; text-align: center;">
                        <span style="display: inline-block; padding: 0.25rem 0.75rem; background: #c6f6d5; color: #22543d; border-radius: 12px; font-weight: 600; font-size: 0.875rem;">
                            ${spec.manufacturers ? spec.manufacturers.length : 0}
                        </span>
                    </td>
                    <td style="padding: 0.75rem; text-align: center;">
                        <span style="display: inline-block; padding: 0.25rem 0.75rem; background: #bee3f8; color: #2c5282; border-radius: 12px; font-weight: 600; font-size: 0.875rem;">
                            ${spec.products ? spec.products.length : 0}
                        </span>
                    </td>
                    <td style="padding: 0.75rem; text-align: center;">
                        <span style="display: inline-block; padding: 0.25rem 0.75rem; background: #feebc8; color: #744210; border-radius: 12px; font-weight: 600; font-size: 0.875rem;">
                            ${spec.shop_drawing_requirements ? spec.shop_drawing_requirements.length : 0}
                        </span>
                    </td>
                    <td style="padding: 0.75rem; text-align: center;">
                        <button onclick="viewSpecDetails('${specIdx}')" style="background: #4299e1; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.75rem;">
                            View Details
                        </button>
                    </td>
                </tr>
            `;
        }
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

function renderSpecCardsView(specs) {
    let html = '<div class="cards-grid">';
    
    specs.forEach((spec, specIdx) => {
        if (spec.error) {
            html += `
                <div class="spec-card error-card" data-file="${spec.filename}">
                    <div class="card-header">
                        <div class="card-title">${spec.filename}</div>
                    </div>
                    <div class="error-message">Error: ${spec.error}</div>
                </div>
            `;
        } else {
            const section = spec.spec_section || spec.section || 'Unknown';
            const title = spec.spec_title || spec.title || 'Untitled';

            html += `
                <div class="spec-card" data-file="${spec.filename}" data-section="${section}">
                    <div class="card-header">
                        <div>
                            <div class="card-title">${spec.filename}</div>
                            <div class="card-subtitle">${section} - ${title}</div>
                        </div>
                    </div>
                    
                    <div class="card-data">
                        <div class="data-row">
                            <span class="data-label">👨‍🏭 Manufacturers</span>
                            <span class="data-badge badge-high">${spec.manufacturers ? spec.manufacturers.length : 0}</span>
                        </div>
                        
                        <div class="data-row">
                            <span class="data-label">🛠️ Products</span>
                            <span class="data-badge badge-medium">${spec.products ? spec.products.length : 0}</span>
                        </div>
                        
                        <div class="data-row">
                            <span class="data-label">🔍 Shop Drawing Requirements</span>
                            <span class="data-badge badge-low">${spec.shop_drawing_requirements ? spec.shop_drawing_requirements.length : 0}</span>
                        </div>
                    </div>
                    
                    <div class="card-actions">
                        <button class="card-action-btn btn-view" onclick="viewSpecDetails('${specIdx}')">
                            View Details
                        </button>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    return html;
}

window.viewSpecDetails = function(specIdx) {
    const spec = currentData.spec[specIdx];
    
    if (!spec) {
        showNotification('Specification data not found', 'error');
        return;
    }
    
    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    
    let shopDrawingsHtml = '';
    if (spec.shop_drawing_requirements && spec.shop_drawing_requirements.length > 0) {
        shopDrawingsHtml = `
            <div class="detail-section">
                <h3>Shop Drawing Requirements</h3>
                <ul class="detail-list">
                    ${spec.shop_drawing_requirements.map(req => `
                        <li>${req}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    } else {
        shopDrawingsHtml = `
            <div class="detail-section">
                <h3>Shop Drawing Requirements</h3>
                <p class="empty-notice">No shop drawing requirements found</p>
            </div>
        `;
    }
    
    let manufacturersHtml = '';
    if (spec.manufacturers && spec.manufacturers.length > 0) {
        manufacturersHtml = `
            <div class="detail-section">
                <h3>Manufacturers</h3>
                <ul class="detail-list">
                    ${spec.manufacturers.map(mfr => `
                        <li>${mfr}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    } else {
        manufacturersHtml = `
            <div class="detail-section">
                <h3>Manufacturers</h3>
                <p class="empty-notice">No manufacturers found</p>
            </div>
        `;
    }
    
    let productsHtml = '';
    if (spec.products && spec.products.length > 0) {
        productsHtml = `
            <div class="detail-section">
                <h3>Products</h3>
                <ul class="detail-list">
                    ${spec.products.map(product => `
                        <li>${product}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    } else {
        productsHtml = `
            <div class="detail-section">
                <h3>Products</h3>
                <p class="empty-notice">No products found</p>
            </div>
        `;
    }
    
    // Put it all together
    modalContent.innerHTML = `
        <div class="modal-header">
            <h2>${spec.filename}</h2>
            <button class="modal-close" onclick="closeDetailsModal()">✕ Close</button>
        </div>
        
        <div class="spec-details-overview">
            <div class="detail-item">
                <span class="detail-label">Section:</span>
                <span class="detail-value">${spec.spec_section || spec.section || 'Unknown'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Title:</span>
                <span class="detail-value">${spec.spec_title || spec.title || 'Unknown'}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Category:</span>
                <span class="detail-value">${spec.section_category || spec.category || 'Unknown'}</span>
            </div>
        </div>
        
        <div class="details-container">
            ${shopDrawingsHtml}
            ${manufacturersHtml}
            ${productsHtml}
        </div>
    `;
    
    // Show the modal
    showDetailsModal(modalContent);
};

window.filterSpecData = function(searchTerm) {
    const rows = document.querySelectorAll('.spec-row');
    const cards = document.querySelectorAll('.spec-card');
    const term = searchTerm.toLowerCase();
    
    // Filter table rows
    rows.forEach(row => {
        const file = (row.dataset.file || '').toLowerCase();
        const section = (row.dataset.section || '').toLowerCase();
        const text = row.textContent.toLowerCase();
        
        if (file.includes(term) || section.includes(term) || text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Filter cards
    cards.forEach(card => {
        const file = (card.dataset.file || '').toLowerCase();
        const section = (card.dataset.section || '').toLowerCase();
        const text = card.textContent.toLowerCase();
        
        if (file.includes(term) || section.includes(term) || text.includes(term)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
};

window.exportSpecToCSV = function() {
    if (!currentData || !currentData.spec) {
        showNotification('No specification data to export', 'error');
        return;
    }
    
    const specs = currentData.spec;
    
    let csv = 'Filename,Section,Title,Manufacturers Count,Products Count,Shop Drawing Requirements Count,Shop Drawing Requirements\n';
    
    specs.forEach(spec => {
        if (!spec.error) {
            const manufacturersCount = spec.manufacturers ? spec.manufacturers.length : 0;
            const productsCount = spec.products ? spec.products.length : 0;
            const reqsCount = spec.shop_drawing_requirements ? spec.shop_drawing_requirements.length : 0;
            const reqsList = spec.shop_drawing_requirements ? spec.shop_drawing_requirements.map(r => r.replace(/,/g, ';')).join(' | ') : '';
            
            csv += `"${spec.filename}",`;
            csv += `"${spec.section || '-'}",`;
            csv += `"${(spec.title || '-').replace(/"/g, '""')}",`;
            csv += `${manufacturersCount},`;
            csv += `${productsCount},`;
            csv += `${reqsCount},`;
            csv += `"${reqsList.replace(/"/g, '""')}"\n`;
        }
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spec_analysis_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('CSV exported successfully!', 'success');
};

// ============================================================================
// DRAWING RESULTS
// ============================================================================

function calculateStats(drawings) {
    let totalSheets = 0;
    let totalDrains = 0;
    let totalScuppers = 0;
    let totalRTUs = 0;
    let totalPenetrations = 0;

    drawings.forEach(drawing => {
        if (drawing.roof_plans) {
            totalSheets += drawing.roof_plans.length;
            drawing.roof_plans.forEach(plan => {
                totalDrains += extractCount(plan.drains);
                totalScuppers += extractCount(plan.scuppers);
                totalRTUs += extractCount(plan.rtus_curbs);
                totalPenetrations += extractCount(plan.penetrations);
            });
        }
    });

    return {
        totalSheets,
        totalDrains,
        totalScuppers,
        totalRTUs,
        totalPenetrations
    };
}

function renderDrawingResults(drawings) {
    const drawingArray = Array.isArray(drawings) ? drawings : [drawings];
    const stats = calculateStats(drawingArray);
    
    return `
        <div class="toolbar">
            <div class="toolbar-top">
                <h2>🏗️ Architectural Drawings</h2>
                <div class="toolbar-actions">
                    <button class="toolbar-btn ${currentView === 'table' ? 'active' : ''}" onclick="switchView('table')">
                        📊 Table
                    </button>
                    <button class="toolbar-btn ${currentView === 'cards' ? 'active' : ''}" onclick="switchView('cards')">
                        🎴 Cards
                    </button>
                    <button class="toolbar-btn" onclick="showCharts()">
                        📈 Charts
                    </button>
                    <button class="toolbar-btn" onclick="exportToCSV()">
                        📥 Export
                    </button>
                    <button class="toolbar-btn danger" onclick="clearSession()">
                        🗑️ Clear
                    </button>
                </div>
            </div>
            
            <input type="text" class="search-bar" placeholder="🔍 Search sheets, files, or data..." oninput="filterData(this.value)">
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${stats.totalSheets}</div>
                <div class="stat-label">Sheets</div>
            </div>
            <div class="stat-card orange">
                <div class="stat-value">${stats.totalDrains}</div>
                <div class="stat-label">Drains</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.totalScuppers}</div>
                <div class="stat-label">Scuppers</div>
            </div>
            <div class="stat-card orange">
                <div class="stat-value">${stats.totalRTUs}</div>
                <div class="stat-label">RTUs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.totalPenetrations}</div>
                <div class="stat-label">Penetrations</div>
            </div>
        </div>
        
        ${currentView === 'table' ? renderTableView(drawingArray) : renderCardsView(drawingArray)}
    `;
}

function renderTableView(drawings) {
    let html = `
        <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #1e2a3a; color: white;">
                        <th style="padding: 1rem; text-align: left;">File</th>
                        <th style="padding: 1rem; text-align: center;">Drains</th>
                        <th style="padding: 1rem; text-align: center;">Scuppers</th>
                        <th style="padding: 1rem; text-align: center;">RTUs</th>
                        <th style="padding: 1rem; text-align: center;">Penetrations</th>
                    </tr>
                </thead>
                <tbody>
    `;

    drawings.forEach((drawing, idx) => {
        const rowClass = idx % 2 === 0 ? 'background: #f7fafc;' : 'background: white;';
        const drains = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.drains), 0) : 0;
        const scuppers = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.scuppers), 0) : 0;
        const rtus = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.rtus_curbs), 0) : 0;
        const penetrations = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.penetrations), 0) : 0;

        html += `
            <tr style="${rowClass}">
                <td style="padding: 0.75rem;">${drawing.filename || 'Unknown'}</td>
                <td style="padding: 0.75rem; text-align: center;">${drains}</td>
                <td style="padding: 0.75rem; text-align: center;">${scuppers}</td>
                <td style="padding: 0.75rem; text-align: center;">${rtus}</td>
                <td style="padding: 0.75rem; text-align: center;">${penetrations}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;
    return html;
}

function renderCardsView(drawings) {
    let html = '<div class="cards-grid">';

    drawings.forEach(drawing => {
        const drains = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.drains), 0) : 0;
        const scuppers = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.scuppers), 0) : 0;
        const rtus = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.rtus_curbs), 0) : 0;
        const penetrations = drawing.roof_plans ? drawing.roof_plans.reduce((sum, p) => sum + extractCount(p.penetrations), 0) : 0;

        html += `
            <div class="drawing-card">
                <div class="card-header">
                    <div class="card-title">${drawing.filename || 'Unknown'}</div>
                </div>
                <div class="card-data">
                    <div class="data-row">
                        <span class="data-label">Drains</span>
                        <span class="data-value">${drains}</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">Scuppers</span>
                        <span class="data-value">${scuppers}</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">RTUs</span>
                        <span class="data-value">${rtus}</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">Penetrations</span>
                        <span class="data-value">${penetrations}</span>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    return html;
}

// ============================================================================
// ASSEMBLY RESULTS
// ============================================================================

function renderAssemblyResults(assemblies) {
    // Add your assembly rendering code here
    return '';
}

// ============================================================================
// MODAL FOR DETAILS
// ============================================================================

function showDetailsModal(content) {
    let modal = document.getElementById('detailsModal');
    
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'detailsModal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }
    
    modal.innerHTML = '';
    modal.appendChild(content);
    modal.classList.add('show');
}

window.closeDetailsModal = function() {
    const modal = document.getElementById('detailsModal');
    if (modal) {
        modal.classList.remove('show');
    }
};

// ============================================================================
// UTILITY FUNCTIONS (existing from your code)
// ============================================================================

function extractCount(detectionString) {
    if (!detectionString) return 0;
    const match = detectionString.match(/\((\d+)\)/);
    return match ? parseInt(match[1]) : 0;
}

function getConfidenceLevel(detectionString) {
    if (!detectionString) return 'none';
    if (detectionString.includes('✓✓✓')) return 'high';
    if (detectionString.includes('✓✓')) return 'medium';
    if (detectionString.includes('✓')) return 'low';
    return 'none';
}

function showNotification(message, type = 'info') {
    const colors = {
        success: '#48bb78',
        error: '#fc8181',
        info: '#4299e1',
        warning: '#f6ad55'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================================================
// ADD ADDITIONAL CSS
// ============================================================================

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
    
    /* Modal Styles */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.7);
        z-index: 1000;
        overflow-y: auto;
    }
    
    .modal.show {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background: #fff;
        border-radius: 12px;
        max-width: 1000px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #edf2f7;
    }
    
    .modal-close {
        background: #fc8181;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .modal-close:hover {
        background: #e53e3e;
    }
    
    /* Spec Details Styles */
    .spec-details-overview {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: #f7fafc;
        border-radius: 8px;
    }
    
    .detail-item {
        display: flex;
        flex-direction: column;
    }
    
    .detail-label {
        font-size: 0.875rem;
        color: #718096;
        margin-bottom: 0.25rem;
    }
    
    .detail-value {
        font-weight: 600;
        color: #2d3748;
    }
    
    .details-container {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }
    
    .detail-section {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    .detail-section h3 {
        margin-bottom: 1rem;
        color: #2d3748;
        font-size: 1.25rem;
    }
    
    .detail-list {
        list-style-type: disc;
        padding-left: 1.5rem;
        margin-top: 0.5rem;
    }
    
    .detail-list li {
        margin-bottom: 0.75rem;
        line-height: 1.5;
    }
    
    .empty-notice {
        color: #a0aec0;
        font-style: italic;
    }
`;

document.head.appendChild(style);

console.log('✅ BuildingSystemsAI - App loaded with shop drawing extraction support!');