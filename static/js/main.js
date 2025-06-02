// Web Crawler Main JavaScript
// Global variables for tree visualization
let treeData = null;
let svg, g, tree, root;
let width = 800, height = 400;
let i = 0;
const duration = 750;

// Helper function to safely get element
function safeGetElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with id '${id}' not found`);
    }
    return element;
}

// Helper function to safely load JSON data
function loadJSONData(id) {
    try {
        const dataElement = document.getElementById(id);
        if (!dataElement) {
            console.warn(`JSON data element '${id}' not found`);
            return null;
        }
        return JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error(`Error parsing JSON data from '${id}':`, error);
        return null;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    
    const form = document.querySelector('form');
    const loading = safeGetElement('loading');
    
    // Initialize tree visualization if data exists
    const crawlData = loadJSONData('crawl-data');
    const configData = loadJSONData('config-data');
    
    if (crawlData && crawlData.length > 0) {
        console.log('Crawl data found, initializing tree visualization...');
        initializeTreeVisualization(crawlData, configData);
    } else {
        console.log('No crawl data found, skipping tree visualization');
    }
    
    // Tab switching functionality
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update button states
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update content visibility
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            const targetContent = safeGetElement(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
            }
            
            // Refresh tree if switching to tree view
            if (targetTab === 'tree-view' && treeData) {
                setTimeout(() => {
                    refreshTreeVisualization();
                }, 100);
            }
        });
    });
    
    // Main form submission
    if (form) {
        form.addEventListener('submit', function(event) {
            const keywordElement = safeGetElement('keyword');
            const keyword = keywordElement ? keywordElement.value : '';
            
            if (!keyword.trim()) {
                event.preventDefault();
                alert('Please enter a keyword to search');
                return false;
            }
            
            if (loading) {
                loading.classList.remove('hidden');
            }
            
            const progressModal = safeGetElement('progress-modal');
            if (progressModal) {
                progressModal.classList.remove('opacity-0', 'pointer-events-none');
            }
            
            startProgressTracking();
        });
    }
    
    // Modal functionality
    setupModalHandlers();
    
    // View Route button click handlers
    setupRouteButtonHandlers();
    
    // Progress tracking function
    function startProgressTracking() {
        const progressInterval = setInterval(function() {
            fetch('/get_progress')
                .then(response => response.json())
                .then(data => {
                    updateProgressDisplay(data);
                    
                    if (data.total_visited > 0 && data.current_depth >= data.max_depth) {
                        if (loading) {
                            loading.classList.add('hidden');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error fetching progress:', error);
                });
        }, 100);
        
        window.progressInterval = progressInterval;
        
        setTimeout(function() {
            if (window.progressInterval) {
                clearInterval(window.progressInterval);
            }
        }, 5 * 60 * 1000);
    }
});

function setupModalHandlers() {
    const modalOpenBtn = safeGetElement('modal-open-btn');
    const closeModalBtn = safeGetElement('close-modal');
    const closeProgressModalBtn = safeGetElement('close-progress-modal');
    const modal = safeGetElement('search-modal');
    const progressModal = safeGetElement('progress-modal');
    const viewDetailedBtn = safeGetElement('view-detailed-progress');
    
    // Open detailed progress modal
    if (viewDetailedBtn) {
        viewDetailedBtn.addEventListener('click', function() {
            if (progressModal) {
                progressModal.classList.remove('opacity-0', 'pointer-events-none');
            }
        });
    }
    
    // Close modals
    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', function() {
            modal.classList.add('opacity-0', 'pointer-events-none');
        });
    }
    
    if (closeProgressModalBtn && progressModal) {
        closeProgressModalBtn.addEventListener('click', function() {
            progressModal.classList.add('opacity-0', 'pointer-events-none');
        });
    }
}

function setupRouteButtonHandlers() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('view-route-btn') || 
            event.target.closest('.view-route-btn')) {
            
            const button = event.target.classList.contains('view-route-btn') ? 
                           event.target : 
                           event.target.closest('.view-route-btn');
            
            const url = button.dataset.url;
            const parent = button.dataset.parent || '-';
            const depth = button.dataset.depth || '0';
            const title = button.dataset.title || url;
            
            displayRouteDetails(url, parent, depth, title);
        }
    });
}

function displayRouteDetails(url, parent, depth, title) {
    const modal = safeGetElement('search-modal');
    const routeUrl = safeGetElement('route-url');
    const routeParent = safeGetElement('route-parent');
    const routeDepth = safeGetElement('route-depth');
    const routeLoading = safeGetElement('route-loading');
    const routePathContent = safeGetElement('route-path-content');
    
    if (routeUrl) routeUrl.textContent = url;
    if (routeParent) routeParent.textContent = parent !== '-' ? parent : 'None';
    if (routeDepth) routeDepth.textContent = depth;
    
    if (routeLoading) routeLoading.classList.remove('hidden');
    if (routePathContent) {
        routePathContent.innerHTML = '<p class="text-center text-gray-500">Loading path information...</p>';
    }
    
    if (modal) {
        modal.classList.remove('opacity-0', 'pointer-events-none');
    }
    
    setTimeout(() => {
        generateRoutePath(url, parent, depth, title);
    }, 500);
}

function generateRoutePath(url, parent, depth, title) {
    const routeLoading = safeGetElement('route-loading');
    const routePathContent = safeGetElement('route-path-content');
    const seedUrlElement = safeGetElement('seed_url');
    const seedUrl = seedUrlElement ? seedUrlElement.value : 'http://upi.edu';
    
    let routePath = '';
    
    if (parent !== '-' && parent !== '') {
        routePath = `
            <div class="space-y-2">
                <div class="flex items-start">
                    <div class="bg-green-100 rounded-full flex items-center justify-center h-6 w-6 flex-shrink-0 mr-2">
                        <span class="text-xs font-medium text-green-800">1</span>
                    </div>
                    <div>
                        <p class="text-sm font-medium">Start URL</p>
                        <a href="${seedUrl}" target="_blank" class="text-xs text-blue-600 hover:underline break-all">
                            ${seedUrl}
                        </a>
                    </div>
                </div>
                <div class="ml-3 border-l-2 border-gray-200 pl-5 py-2">
                    <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                    </svg>
                </div>
                <div class="flex items-start">
                    <div class="bg-blue-100 rounded-full flex items-center justify-center h-6 w-6 flex-shrink-0 mr-2">
                        <span class="text-xs font-medium text-blue-800">${parseInt(depth) > 1 ? '...' : '2'}</span>
                    </div>
                    <div>
                        <p class="text-sm font-medium">Parent Page</p>
                        <a href="${parent}" target="_blank" class="text-xs text-blue-600 hover:underline break-all">${parent}</a>
                    </div>
                </div>
                <div class="ml-3 border-l-2 border-gray-200 pl-5 py-2">
                    <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                    </svg>
                </div>
                <div class="flex items-start">
                    <div class="bg-purple-100 rounded-full flex items-center justify-center h-6 w-6 flex-shrink-0 mr-2">
                        <span class="text-xs font-medium text-purple-800">${parseInt(depth) + 1}</span>
                    </div>
                    <div>
                        <p class="text-sm font-medium">${title}</p>
                        <a href="${url}" target="_blank" class="text-xs text-blue-600 hover:underline break-all">${url}</a>
                    </div>
                </div>
            </div>
        `;
    } else {
        routePath = `
            <div class="space-y-2">
                <div class="flex items-start">
                    <div class="bg-green-100 rounded-full flex items-center justify-center h-6 w-6 flex-shrink-0 mr-2">
                        <span class="text-xs font-medium text-green-800">1</span>
                    </div>
                    <div>
                        <p class="text-sm font-medium">Start URL</p>
                        <a href="${seedUrl}" target="_blank" class="text-xs text-blue-600 hover:underline break-all">
                            ${seedUrl}
                        </a>
                    </div>
                </div>
                <div class="ml-3 border-l-2 border-gray-200 pl-5 py-2">
                    <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                    </svg>
                </div>
                <div class="flex items-start">
                    <div class="bg-purple-100 rounded-full flex items-center justify-center h-6 w-6 flex-shrink-0 mr-2">
                        <span class="text-xs font-medium text-purple-800">2</span>
                    </div>
                    <div>
                        <p class="text-sm font-medium">${title}</p>
                        <a href="${url}" target="_blank" class="text-xs text-blue-600 hover:underline break-all">${url}</a>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (routeLoading) routeLoading.classList.add('hidden');
    if (routePathContent) routePathContent.innerHTML = routePath;
}

function updateProgressDisplay(data) {
    const depthPercent = data.max_depth ? (data.current_depth / data.max_depth) * 100 : 0;
    const widthPercent = data.max_width ? (data.current_width / data.max_width) * 100 : 0;
    
    // Update modal elements
    const elements = {
        'depth-progress-bar': elem => elem.style.width = depthPercent + '%',
        'depth-progress-text': elem => elem.textContent = data.current_depth + '/' + data.max_depth,
        'width-progress-bar': elem => elem.style.width = widthPercent + '%',
        'width-progress-text': elem => elem.textContent = data.current_width + '/' + data.max_width,
        'current-url': elem => elem.textContent = data.current_url || '-',
        'pages-visited': elem => elem.textContent = data.total_visited,
        'matches-found': elem => elem.textContent = data.matched_count,
        'main-depth-progress': elem => elem.style.width = depthPercent + '%',
        'main-width-progress': elem => elem.style.width = widthPercent + '%',
        'main-current-depth': elem => elem.textContent = data.current_depth,
        'main-max-depth': elem => elem.textContent = data.max_depth,
        'main-current-width': elem => elem.textContent = data.current_width,
        'main-max-width': elem => elem.textContent = data.max_width,
        'main-current-url': elem => elem.textContent = data.current_url || 'Not started'
    };
    
    Object.entries(elements).forEach(([id, updateFn]) => {
        const elem = safeGetElement(id);
        if (elem) updateFn(elem);
    });
}

// Tree Visualization Functions
function initializeTreeVisualization(crawlData, configData) {
    try {
        console.log('Building tree data from crawl results...');
        treeData = buildTreeData(crawlData, configData);
        console.log('Tree data built successfully:', treeData);
        createTreeVisualization();
    } catch (error) {
        console.error('Error initializing tree visualization:', error);
    }
}

function buildTreeData(results, config) {
    const nodeMap = new Map();
    const seedUrl = config ? config.seed_url : 'http://upi.edu';
    
    // Create root node
    const root = {
        name: seedUrl,
        title: "Root",
        url: seedUrl,
        depth: 0,
        children: []
    };
    nodeMap.set(seedUrl, root);
    
    // Sort results by depth
    results.sort((a, b) => a.depth - b.depth);
    
    // Add each result to the tree
    results.forEach(result => {
        const node = {
            name: result.url,
            title: result.title || result.url,
            url: result.url,
            depth: result.depth,
            children: []
        };
        
        nodeMap.set(result.url, node);
        
        // Find parent and add this node as child
        if (result.parent && nodeMap.has(result.parent)) {
            nodeMap.get(result.parent).children.push(node);
        } else {
            root.children.push(node);
        }
    });
    
    return root;
}

function createTreeVisualization() {
    const container = safeGetElement('tree-visualization');
    if (!container) {
        console.error('Tree visualization container not found');
        return;
    }
    
    const rect = container.getBoundingClientRect();
    width = rect.width || 800;
    height = rect.height || 400;
    
    // Clear existing SVG
    d3.select('#tree-svg').selectAll('*').remove();
    
    svg = d3.select('#tree-svg')
        .attr('width', width)
        .attr('height', height);
    
    g = svg.append('g');
    
    // Add zoom and pan
    const zoom = d3.zoom()
        .scaleExtent([0.1, 3])
        .on('zoom', function(event) {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Create tree layout
    tree = d3.tree().size([height - 100, width - 100]);
    
    // Create hierarchy
    root = d3.hierarchy(treeData, d => d.children);
    root.x0 = height / 2;
    root.y0 = 0;
    
    // Initially collapse nodes beyond depth 2
    if (root.children) {
        root.children.forEach(collapse);
    }
    
    update(root);
    setupTreeControls();
}

function update(source) {
    if (!tree || !root) return;
    
    // Compute the new tree layout
    const treeData = tree(root);
    const nodes = treeData.descendants();
    const links = treeData.descendants().slice(1);
    
    // Normalize for fixed-depth
    nodes.forEach(d => { d.y = d.depth * 180 });
    
    // Update the nodes
    const node = g.selectAll('g.node')
        .data(nodes, d => d.id || (d.id = ++i));
        
    // Enter any new nodes
    const nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${source.y0},${source.x0})`)
        .on('click', click)
        .on('mouseover', function(event, d) {
            showTooltip(event, d);
        })
        .on('mouseout', hideTooltip);
        
    // Add circles for the nodes
    nodeEnter.append('circle')
        .attr('r', 1e-6)
        .style('fill', d => d._children ? '#3b82f6' : '#fff')
        .style('stroke', d => getNodeColor(d))
        .style('stroke-width', '2px');
        
    // Add labels for the nodes
    nodeEnter.append('text')
        .attr('dy', '.35em')
        .attr('x', d => d.children || d._children ? -13 : 13)
        .attr('text-anchor', d => d.children || d._children ? 'end' : 'start')
        .text(d => truncateText(d.data.title, 20))
        .style('fill-opacity', 1e-6);
        
    // Transition nodes to their new position
    const nodeUpdate = nodeEnter.merge(node);
    
    nodeUpdate.transition()
        .duration(duration)
        .attr('transform', d => `translate(${d.y},${d.x})`);
        
    nodeUpdate.select('circle')
        .attr('r', 6)
        .style('fill', d => d._children ? '#3b82f6' : '#fff')
        .style('stroke', d => getNodeColor(d))
        .attr('class', d => getNodeClass(d));
        
    nodeUpdate.select('text')
        .style('fill-opacity', 1);
        
    // Transition exiting nodes
    const nodeExit = node.exit().transition()
        .duration(duration)
        .attr('transform', d => `translate(${source.y},${source.x})`)
        .remove();
        
    nodeExit.select('circle')
        .attr('r', 1e-6);
        
    nodeExit.select('text')
        .style('fill-opacity', 1e-6);
        
    // Update the links
    const link = g.selectAll('path.link')
        .data(links, d => d.id);
        
    // Enter any new links
    const linkEnter = link.enter().insert('path', 'g')
        .attr('class', 'link')
        .attr('d', d => {
            const o = {x: source.x0, y: source.y0};
            return diagonal(o, o);
        });
        
    // Transition links
    linkEnter.merge(link).transition()
        .duration(duration)
        .attr('d', d => diagonal(d, d.parent));
        
    // Transition exiting links
    link.exit().transition()
        .duration(duration)
        .attr('d', d => {
            const o = {x: source.x, y: source.y};
            return diagonal(o, o);
        })
        .remove();
        
    // Store old positions
    nodes.forEach(d => {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

function diagonal(s, d) {
    return `M ${s.y} ${s.x}
            C ${(s.y + d.y) / 2} ${s.x},
              ${(s.y + d.y) / 2} ${d.x},
              ${d.y} ${d.x}`;
}

function click(event, d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    update(d);
}

function collapse(d) {
    if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
    }
}

function expand(d) {
    if (d._children) {
        d.children = d._children;
        d.children.forEach(expand);
        d._children = null;
    }
}

function getNodeColor(d) {
    if (d.depth === 0) return '#059669'; // Root - green
    if (d.children || d._children) return '#1e40af'; // Internal - blue
    return '#d97706'; // Leaf - orange
}

function getNodeClass(d) {
    if (d.depth === 0) return 'root';
    if (d.children || d._children) return 'internal';
    return 'leaf';
}

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function showTooltip(event, d) {
    const tooltip = safeGetElement('tree-tooltip');
    if (!tooltip) return;
    
    tooltip.innerHTML = `
        <strong>${d.data.title}</strong><br/>
        URL: ${d.data.url}<br/>
        Depth: ${d.depth}<br/>
        Children: ${(d.children || d._children || []).length}
    `;
    tooltip.style.display = 'block';
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY - 10) + 'px';
}

function hideTooltip() {
    const tooltip = safeGetElement('tree-tooltip');
    if (tooltip) {
        tooltip.style.display = 'none';
    }
}

function setupTreeControls() {
    const controls = {
        'expand-all': () => { expandAll(root); update(root); },
        'collapse-all': () => { collapseAll(root); update(root); },
        'center-tree': centerTree,
        'fit-to-screen': fitToScreen
    };
    
    Object.entries(controls).forEach(([id, handler]) => {
        const element = safeGetElement(id);
        if (element) {
            element.addEventListener('click', handler);
        }
    });
}

function expandAll(d) {
    if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    if (d.children) {
        d.children.forEach(expandAll);
    }
}

function collapseAll(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
        d._children.forEach(collapseAll);
    }
}

function centerTree() {
    if (!g || !svg) return;
    
    try {
        const bounds = g.node().getBBox();
        const fullWidth = width;
        const fullHeight = height;
        const widthScale = fullWidth / bounds.width;
        const heightScale = fullHeight / bounds.height;
        const scale = 0.8 * Math.min(widthScale, heightScale);
        const translate = [
            fullWidth / 2 - scale * (bounds.x + bounds.width / 2), 
            fullHeight / 2 - scale * (bounds.y + bounds.height / 2)
        ];
        
        svg.transition()
            .duration(750)
            .call(d3.zoom().transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
    } catch (error) {
        console.error('Error centering tree:', error);
    }
}

function fitToScreen() {
    if (!g || !svg) return;
    
    try {
        const bounds = g.node().getBBox();
        const fullWidth = width;
        const fullHeight = height;
        const widthScale = (fullWidth * 0.9) / bounds.width;
        const heightScale = (fullHeight * 0.9) / bounds.height;
        const scale = Math.min(widthScale, heightScale);
        const translate = [
            fullWidth / 2 - scale * (bounds.x + bounds.width / 2), 
            fullHeight / 2 - scale * (bounds.y + bounds.height / 2)
        ];
        
        svg.transition()
            .duration(750)
            .call(d3.zoom().transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
    } catch (error) {
        console.error('Error fitting tree to screen:', error);
    }
}

function refreshTreeVisualization() {
    if (treeData) {
        createTreeVisualization();
    }
}

// Handle window resize
window.addEventListener('resize', function() {
    if (treeData) {
        setTimeout(refreshTreeVisualization, 100);
    }
});
