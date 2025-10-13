// File upload handling with individual file removal
const fileInputs = ['scope', 'spec', 'drawing', 'assembly'];
const fileData = {
    scope: [],
    spec: [],
    drawing: [],
    assembly: []
};

// Define exact field order matching Excel template
const ASSEMBLY_FIELD_ORDER = [
    'assembly_roof_area',
    'spec_number',
    'manufacturer',
    'system',
    'date_of_assembly_letter',
    // SPACE 1
    'contractor',
    'contractor_address',
    'project_name',
    'project_location',
    // SPACE 2
    'roof_height',
    'membrane_1',
    'membrane_1_attachment',
    'membrane_2',
    'membrane_2_attachment',
    'membrane_3',
    'membrane_3_attachment',
    'coverboard_1',
    'coverboard_1_attachment',
    'insulation_layer_1',
    'insulation_layer_1_attachment',
    'insulation_layer_2',
    'insulation_layer_2_attachment',
    'insulation_layer_3',
    'insulation_layer_3_attachment',
    'vapor_barrier',
    'vapor_barrier_attachment',
    'coverboard_2',
    'coverboard_2_attachment',
    'deck_slope',
    'deck_slope_attachment',
    // SPACE 3
    'approval_fm_roofnav',
    'approval_fm_global_listing',
    'approval_ul_rating',
    'approval_astm_standards'
];

fileInputs.forEach(category => {
    const input = document.getElementById(category);
    const listDiv = document.getElementById(`${category}-list`);
    
    input.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        
        files.forEach(file => {
            fileData[category].push(file);
            
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span>${file.name}</span>
                <span class="remove-file" data-category="${category}" data-filename="${file.name}">✕</span>
            `;
            listDiv.appendChild(fileItem);
        });
        
        e.target.value = '';
    });
});

// Handle file removal
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-file')) {
        const category = e.target.dataset.category;
        const filename = e.target.dataset.filename;
        
        fileData[category] = fileData[category].filter(f => f.name !== filename);
        e.target.parentElement.remove();
    }
});

// Handle form submission
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    document.getElementById('loading').classList.add('show');
    document.getElementById('results').classList.remove('show');
    
    const formData = new FormData();
    
    fileInputs.forEach(category => {
        fileData[category].forEach(file => {
            formData.append(category, file);
        });
    });
    
    try {
        const response = await fetch('/parse', {
            method: 'POST',
            body: formData
        });
        
        const results = await response.json();
        
        document.getElementById('loading').classList.remove('show');
        displayResults(results);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').classList.remove('show');
        alert('Error parsing documents. Check console for details.');
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    
    // Scope of Work Results
    if (results.scope) {
        const section = createResultSection('Scope of Work', results.scope);
        resultsDiv.appendChild(section);
    }
    
    // Specification Results
    if (results.spec) {
        const section = createResultSection('Specification', results.spec);
        resultsDiv.appendChild(section);
    }
    
    // Drawing Results
    if (results.drawing) {
        const section = createResultSection('Drawing', results.drawing);
        resultsDiv.appendChild(section);
    }
    
    // Assembly Letter Results
    if (results.assembly) {
        if (results.assembly.assemblies && Array.isArray(results.assembly.assemblies)) {
            // Multiple assemblies
            const mainSection = document.createElement('div');
            mainSection.className = 'result-section';
            
            const mainHeading = document.createElement('h2');
            mainHeading.textContent = 'Assembly Letter';
            mainSection.appendChild(mainHeading);
            
            // Add manufacturer and project info at top
            const metadata = document.createElement('div');
            metadata.style.marginBottom = '20px';
            metadata.style.paddingBottom = '20px';
            metadata.style.borderBottom = '2px solid #e0e0e0';
            
            if (results.assembly.manufacturer) {
                const mfr = document.createElement('div');
                mfr.className = 'result-item';
                mfr.innerHTML = `<span class="result-label">Manufacturer:</span> ${results.assembly.manufacturer}`;
                metadata.appendChild(mfr);
            }
            
            // Add project info
            const projectFields = ['project_date', 'project_location', 'project_name'];
            for (const field of projectFields) {
                if (results.assembly[field]) {
                    const item = document.createElement('div');
                    item.className = 'result-item';
                    item.innerHTML = `<span class="result-label">${formatLabel(field)}:</span> ${results.assembly[field]}`;
                    metadata.appendChild(item);
                }
            }
            
            mainSection.appendChild(metadata);
            
            // Create subsection for each assembly in template order
            results.assembly.assemblies.forEach((assembly, index) => {
                const assemblySection = createAssemblySubsectionOrdered(assembly, index + 1);
                mainSection.appendChild(assemblySection);
            });
            
            resultsDiv.appendChild(mainSection);
        } else {
            // Single assembly
            const section = createResultSectionOrdered('Assembly Letter', results.assembly, ASSEMBLY_FIELD_ORDER);
            resultsDiv.appendChild(section);
        }
    }
    
    resultsDiv.classList.add('show');
}

function createAssemblySubsectionOrdered(assembly, number) {
    const section = document.createElement('div');
    section.style.marginTop = '30px';
    section.style.paddingTop = '20px';
    section.style.borderTop = '2px solid #667eea';
    
    // Assembly name as prominent header
    const assemblyName = assembly.assembly_roof_area || `Assembly ${number}`;
    const heading = document.createElement('h3');
    heading.textContent = `Assembly ${number}`;
    heading.style.color = '#667eea';
    heading.style.fontSize = '1.3em';
    heading.style.marginBottom = '15px';
    heading.style.textAlign = 'center';
    heading.style.fontWeight = 'bold';
    section.appendChild(heading);
    
    // Display fields in exact template order
    for (const fieldKey of ASSEMBLY_FIELD_ORDER) {
        if (assembly.hasOwnProperty(fieldKey) && assembly[fieldKey]) {
            const item = document.createElement('div');
            item.className = 'result-item';
            item.style.marginBottom = '12px';
            
            const label = document.createElement('span');
            label.className = 'result-label';
            label.textContent = formatLabel(fieldKey) + ': ';
            label.style.fontWeight = '600';
            label.style.minWidth = '200px';
            label.style.display = 'inline-block';
            
            const valueSpan = document.createElement('span');
            valueSpan.textContent = formatValue(assembly[fieldKey]);
            
            // Indent attachment lines
            if (fieldKey.includes('_attachment')) {
                item.style.marginLeft = '20px';
                item.style.fontStyle = 'italic';
                item.style.fontSize = '0.95em';
                item.style.color = '#555';
            }
            
            item.appendChild(label);
            item.appendChild(valueSpan);
            section.appendChild(item);
        }
    }
    
    return section;
}

function createResultSectionOrdered(title, data, fieldOrder) {
    const section = document.createElement('div');
    section.className = 'result-section';
    
    const heading = document.createElement('h2');
    heading.textContent = title;
    section.appendChild(heading);
    
    // Display in specified order if provided
    if (fieldOrder) {
        for (const fieldKey of fieldOrder) {
            if (data.hasOwnProperty(fieldKey) && data[fieldKey]) {
                const item = document.createElement('div');
                item.className = 'result-item';
                
                const label = document.createElement('span');
                label.className = 'result-label';
                label.textContent = formatLabel(fieldKey) + ': ';
                
                const valueSpan = document.createElement('span');
                valueSpan.textContent = formatValue(data[fieldKey]);
                
                // Indent attachment lines
                if (fieldKey.includes('_attachment')) {
                    item.style.marginLeft = '20px';
                    item.style.fontStyle = 'italic';
                }
                
                item.appendChild(label);
                item.appendChild(valueSpan);
                section.appendChild(item);
            }
        }
    } else {
        // Fallback to regular display
        for (const [key, value] of Object.entries(data)) {
            if (key === 'filename' || key === 'assemblies') continue;
            
            const item = document.createElement('div');
            item.className = 'result-item';
            
            const label = document.createElement('span');
            label.className = 'result-label';
            label.textContent = formatLabel(key) + ': ';
            
            const valueSpan = document.createElement('span');
            valueSpan.textContent = formatValue(value);
            
            item.appendChild(label);
            item.appendChild(valueSpan);
            section.appendChild(item);
        }
    }
    
    return section;
}

function createResultSection(title, data) {
    const section = document.createElement('div');
    section.className = 'result-section';
    
    const heading = document.createElement('h2');
    heading.textContent = title;
    section.appendChild(heading);
    
    for (const [key, value] of Object.entries(data)) {
        if (key === 'filename' || key === 'assemblies') continue;
        
        const item = document.createElement('div');
        item.className = 'result-item';
        
        const label = document.createElement('span');
        label.className = 'result-label';
        label.textContent = formatLabel(key) + ': ';
        
        const valueSpan = document.createElement('span');
        valueSpan.textContent = formatValue(value);
        
        item.appendChild(label);
        item.appendChild(valueSpan);
        section.appendChild(item);
    }
    
    return section;
}

function formatLabel(key) {
    // Convert snake_case to Title Case
    // Special handling for abbreviations
    return key
        .split('_')
        .map(word => {
            // Keep abbreviations uppercase
            if (word === 'fm' || word === 'ul' || word === 'astm') {
                return word.toUpperCase();
            }
            return word.charAt(0).toUpperCase() + word.slice(1);
        })
        .join(' ');
}

function formatValue(value) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    if (Array.isArray(value)) {
        return value.length > 0 ? value.join(', ') : 'None found';
    }
    if (typeof value === 'object') {
        let formatted = '';
        for (const [k, v] of Object.entries(value)) {
            formatted += `${formatLabel(k)}: ${v}\n`;
        }
        return formatted || 'N/A';
    }
    return value.toString();
}