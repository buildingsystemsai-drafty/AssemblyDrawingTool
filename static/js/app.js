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
    
    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('show');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================================
// DRAWING RESULTS
// ============================================================================

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

// ============================================================================
// TABLE VIEW
// ============================================================================

function renderTableView(drawings) {
    let html = `
        <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #1e2a3a; color: white;">
                        <th style="padding: 1rem; text-align: left; font-weight: 600; border-radius: 8px 0 0 0;">File</th>
                        <th style="padding: 1rem; text-align: left; font-weight: 600;">Sheet</th>
                        <th style="padding: 1rem; text-align: left; font-weight: 600;">Type</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">Status</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">💧 Drains</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">🌊 Scuppers</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">⚡ RTUs</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">🔧 Pens</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600;">📐 Scale</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; border-radius: 0 8px 0 0;">Actions</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody">
    `;
    
    drawings.forEach((drawing, drawingIdx) => {
        if (drawing.roof_plans && drawing.roof_plans.length > 0) {
            drawing.roof_plans.forEach((plan, planIdx) => {
                const sheetId = `${drawingIdx}-${planIdx}`;
                const workflowState = getWorkflowState(sheetId);
                const rowClass = drawingIdx % 2 === 0 ? 'background: #f7fafc;' : 'background: white;';
                
                html += renderTableRow(drawing, plan, sheetId, workflowState, rowClass);
            });
        }
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

function renderTableRow(drawing, plan, sheetId, workflowState, rowClass) {
    const drainCount = extractCount(plan.drains);
    const scupperCount = extractCount(plan.scuppers);
    const rtuCount = extractCount(plan.rtus_curbs);
    const penCount = extractCount(plan.penetrations);
    
    const drainConfidence = getConfidenceLevel(plan.drains);
    const scupperConfidence = getConfidenceLevel(plan.scuppers);
    const rtuConfidence = getConfidenceLevel(plan.rtus_curbs);
    const penConfidence = getConfidenceLevel(plan.penetrations);
    
    const workflowBadge = {
        'detected': '<span style="background: #feebc8; color: #744210; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">🟡 Detected</span>',
        'reviewing': '<span style="background: #bee3f8; color: #2c5282; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">🔵 Reviewing</span>',
        'verified': '<span style="background: #c6f6d5; color: #22543d; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">🟢 Verified</span>',
        'approved': '<span style="background: #9ae6b4; color: #22543d; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">✅ Approved</span>'
    };
    
    return `
        <tr class="data-row" data-sheet="${plan.detail_number}" data-file="${drawing.filename}" style="${rowClass}">
            <td style="padding: 0.75rem; color: #2d3748; font-weight: 500; font-size: 0.875rem;">${drawing.filename}</td>
            <td style="padding: 0.75rem; color: #4a5568; font-family: monospace; font-weight: 600;">${plan.detail_number || '-'}</td>
            <td style="padding: 0.75rem; color: #718096; font-size: 0.875rem;">${plan.type || '-'}</td>
            <td style="padding: 0.75rem; text-align: center;">${workflowBadge[workflowState]}</td>
            ${renderTableCell(drainCount, drainConfidence)}
            ${renderTableCell(scupperCount, scupperConfidence)}
            ${renderTableCell(rtuCount, rtuConfidence)}
            ${renderTableCell(penCount, penConfidence)}
            <td style="padding: 0.75rem; text-align: center; color: #4a5568; font-size: 0.875rem;">${plan.scale !== 'Not specified' ? plan.scale : '-'}</td>
            <td style="padding: 0.75rem; text-align: center;">
                ${renderWorkflowButton(sheetId, workflowState)}
            </td>
        </tr>
    `;
}

function renderTableCell(count, confidence) {
    if (count === 0) {
        return '<td style="padding: 0.75rem; text-align: center; color: #cbd5e0;">-</td>';
    }
    
    const colors = {
        high: { bg: '#c6f6d5', text: '#22543d' },
        medium: { bg: '#bee3f8', text: '#2c5282' },
        low: { bg: '#feebc8', text: '#744210' },
        none: { bg: '#f7fafc', text: '#a0aec0' }
    };
    
    const color = colors[confidence] || colors.none;
    
    return `
        <td style="padding: 0.75rem; text-align: center;">
            <span style="display: inline-block; padding: 0.25rem 0.75rem; background: ${color.bg}; color: ${color.text}; border-radius: 12px; font-weight: 600; font-size: 0.875rem;">
                ${count}
            </span>
        </td>
    `;
}

function renderWorkflowButton(sheetId, state) {
    const buttons = {
        'detected': `<button onclick="updateWorkflow('${sheetId}', 'reviewing')" style="background: #bee3f8; color: #2c5282; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.75rem;">👀 Review</button>`,
        'reviewing': `<button onclick="updateWorkflow('${sheetId}', 'verified')" style="background: #c6f6d5; color: #22543d; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.75rem;">✓ Verify</button>`,
        'verified': `<button onclick="updateWorkflow('${sheetId}', 'approved')" style="background: #9ae6b4; color: #22543d; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.75rem;">✓✓ Approve</button>`,
        'approved': `<span style="color: #48bb78; font-weight: 600;">✓✓✓</span>`
    };
    
    return buttons[state];
}

// ============================================================================
// CARDS VIEW
// ============================================================================

function renderCardsView(drawings) {
    let html = '<div class="cards-grid">';
    
    drawings.forEach((drawing, drawingIdx) => {
        if (drawing.roof_plans && drawing.roof_plans.length > 0) {
            drawing.roof_plans.forEach((plan, planIdx) => {
                const sheetId = `${drawingIdx}-${planIdx}`;
                const workflowState = getWorkflowState(sheetId);
                
                html += renderCard(drawing, plan, sheetId, workflowState);
            });
        }
    });
    
    html += '</div>';
    return html;
}

function renderCard(drawing, plan, sheetId, workflowState) {
    const drainCount = extractCount(plan.drains);
    const scupperCount = extractCount(plan.scuppers);
    const rtuCount = extractCount(plan.rtus_curbs);
    const penCount = extractCount(plan.penetrations);
    
    const drainConfidence = getConfidenceLevel(plan.drains);
    const scupperConfidence = getConfidenceLevel(plan.scuppers);
    const rtuConfidence = getConfidenceLevel(plan.rtus_curbs);
    const penConfidence = getConfidenceLevel(plan.penetrations);
    
    const workflowClass = `workflow-${workflowState}`;
    const workflowLabel = workflowState.charAt(0).toUpperCase() + workflowState.slice(1);
    
    return `
        <div class="drawing-card" data-sheet="${plan.detail_number}" data-file="${drawing.filename}">
            <div class="card-header">
                <div>
                    <div class="card-title">${drawing.filename}</div>
                    <div class="card-title" style="color: #FF6B47; margin-top: 0.25rem;">Sheet: ${plan.detail_number || 'Unknown'}</div>
                </div>
            </div>
            
            <div class="workflow-badge ${workflowClass}">
                ${workflowLabel}
            </div>
            
            <div class="card-data">
                ${plan.type ? `
                    <div class="data-row">
                        <span class="data-label">Type</span>
                        <span class="data-value">${plan.type}</span>
                    </div>
                ` : ''}
                
                <div class="data-row">
                    <span class="data-label">💧 Drains</span>
                    ${drainCount > 0 
                        ? `<span class="data-badge badge-${drainConfidence}">${drainCount}</span>`
                        : `<span class="data-badge badge-none">-</span>`
                    }
                </div>
                
                <div class="data-row">
                    <span class="data-label">🌊 Scuppers</span>
                    ${scupperCount > 0 
                        ? `<span class="data-badge badge-${scupperConfidence}">${scupperCount}</span>`
                        : `<span class="data-badge badge-none">-</span>`
                    }
                </div>
                
                <div class="data-row">
                    <span class="data-label">⚡ RTUs</span>
                    ${rtuCount > 0 
                        ? `<span class="data-badge badge-${rtuConfidence}">${rtuCount}</span>`
                        : `<span class="data-badge badge-none">-</span>`
                    }
                </div>
                
                <div class="data-row">
                    <span class="data-label">🔧 Penetrations</span>
                    ${penCount > 0 
                        ? `<span class="data-badge badge-${penConfidence}">${penCount}</span>`
                        : `<span class="data-badge badge-none">-</span>`
                    }
                </div>
                
                ${plan.scale !== 'Not specified' ? `
                    <div class="data-row">
                        <span class="data-label">📐 Scale</span>
                        <span class="data-value">${plan.scale}</span>
                    </div>
                ` : ''}
            </div>
            
            <div class="card-actions">
                ${workflowState === 'detected' ? `
                    <button class="card-action-btn btn-verify" onclick="updateWorkflow('${sheetId}', 'reviewing')">
                        👀 Review
                    </button>
                ` : ''}
                
                ${workflowState === 'reviewing' ? `
                    <button class="card-action-btn btn-verify" onclick="updateWorkflow('${sheetId}', 'verified')">
                        ✓ Verify
                    </button>
                ` : ''}
                
                ${workflowState === 'verified' ? `
                    <button class="card-action-btn btn-approve" onclick="updateWorkflow('${sheetId}', 'approved')">
                        ✓✓ Approve
                    </button>
                ` : ''}
                
                ${workflowState === 'approved' ? `
                    <button class="card-action-btn" style="background: #9ae6b4; color: #22543d;">
                        ✓✓✓ Approved
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

// ============================================================================
// WORKFLOW ACTIONS
// ============================================================================

window.updateWorkflow = function(sheetId, newState) {
    setWorkflowState(sheetId, newState);
    showNotification(`Status updated to ${newState}`, 'success');
}

// ============================================================================
// SEARCH/FILTER
// ============================================================================

window.filterData = function(searchTerm) {
    const rows = document.querySelectorAll('.data-row');
    const cards = document.querySelectorAll('.drawing-card');
    const term = searchTerm.toLowerCase();
    
    // Filter table rows
    rows.forEach(row => {
        const file = (row.dataset.file || '').toLowerCase();
        const sheet = (row.dataset.sheet || '').toLowerCase();
        const text = row.textContent.toLowerCase();
        
        if (file.includes(term) || sheet.includes(term) || text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Filter cards
    cards.forEach(card => {
        const file = (card.dataset.file || '').toLowerCase();
        const sheet = (card.dataset.sheet || '').toLowerCase();
        const text = card.textContent.toLowerCase();
        
        if (file.includes(term) || sheet.includes(term) || text.includes(term)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

// ============================================================================
// STATS & CHARTS
// ============================================================================

function calculateStats(drawings) {
    let totalSheets = 0;
    let totalDrains = 0;
    let totalScuppers = 0;
    let totalRTUs = 0;
    let totalPenetrations = 0;
    
    drawings.forEach(drawing => {
        if (drawing.roof_plans) {
            drawing.roof_plans.forEach(plan => {
                totalSheets++;
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

window.showCharts = function() {
    if (!currentData || !currentData.drawing) {
        showNotification('No data available', 'error');
        return;
    }
    
    const modal = document.getElementById('chartsModal');
    const content = document.getElementById('chartsContent');
    
    const stats = calculateStats(Array.isArray(currentData.drawing) ? currentData.drawing : [currentData.drawing]);
    
    content.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem;">
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 8px;">
                <h3 style="margin-bottom: 1rem; color: #1e2a3a;">Element Totals</h3>
                ${renderBarChart('Drains', stats.totalDrains, '#FF6B47')}
                ${renderBarChart('Scuppers', stats.totalScuppers, '#4299e1')}
                ${renderBarChart('RTUs', stats.totalRTUs, '#48bb78')}
                ${renderBarChart('Penetrations', stats.totalPenetrations, '#f6ad55')}
            </div>
            
            <div style="background: #f7fafc; padding: 1.5rem; border-radius: 8px;">
                <h3 style="margin-bottom: 1rem; color: #1e2a3a;">Summary</h3>
                <div style="line-height: 2; color: #2d3748;">
                    <div><strong>Total Sheets:</strong> ${stats.totalSheets}</div>
                    <div><strong>Total Elements:</strong> ${stats.totalDrains + stats.totalScuppers + stats.totalRTUs + stats.totalPenetrations}</div>
                    <div><strong>Avg per Sheet:</strong> ${((stats.totalDrains + stats.totalScuppers + stats.totalRTUs + stats.totalPenetrations) / stats.totalSheets).toFixed(1)}</div>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.add('show');
}

function renderBarChart(label, value, color) {
    const maxWidth = 300;
    const width = Math.min((value / 20) * maxWidth, maxWidth);
    
    return `
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: #2d3748;">${label}</span>
                <span style="font-weight: bold; color: ${color};">${value}</span>
            </div>
            <div style="background: #e2e8f0; border-radius: 4px; height: 20px;">
                <div style="background: ${color}; height: 100%; width: ${width}px; border-radius: 4px; transition: width 0.3s;"></div>
            </div>
        </div>
    `;
}

window.closeCharts = function() {
    document.getElementById('chartsModal').classList.remove('show');
}

// ============================================================================
// CSV EXPORT
// ============================================================================

window.exportToCSV = function() {
    if (!currentData || !currentData.drawing) {
        showNotification('No data to export', 'error');
        return;
    }
    
    const drawings = Array.isArray(currentData.drawing) ? currentData.drawing : [currentData.drawing];
    
    let csv = 'File,Sheet,Type,Workflow Status,Drains,Scuppers,RTUs,Penetrations,Scale\n';
    
    drawings.forEach((drawing, idx) => {
        if (drawing.roof_plans) {
            drawing.roof_plans.forEach((plan, pIdx) => {
                const sheetId = `${idx}-${pIdx}`;
                const workflow = getWorkflowState(sheetId);
                
                csv += `"${drawing.filename}",`;
                csv += `"${plan.detail_number || '-'}",`;
                csv += `"${plan.type || '-'}",`;
                csv += `"${workflow}",`;
                csv += `${extractCount(plan.drains)},`;
                csv += `${extractCount(plan.scuppers)},`;
                csv += `${extractCount(plan.rtus_curbs)},`;
                csv += `${extractCount(plan.penetrations)},`;
                csv += `"${plan.scale !== 'Not specified' ? plan.scale : '-'}"\n`;
            });
        }
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `drawing_analysis_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('CSV exported successfully!', 'success');
}

// ============================================================================
// UTILITY FUNCTIONS
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
`;
document.head.appendChild(style);

console.log('✅ Drawing Parser v3.0 - Table View loaded!');