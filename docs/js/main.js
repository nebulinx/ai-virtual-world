/** Three.js scene setup and main application logic */

let scene, camera, renderer, controls;
let worldData = null;
let raycaster, mouse;

function init() {
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    window.scene = scene; // Expose for renderer.js
    
    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(0, 50, 100);
    camera.lookAt(0, 0, 0);
    
    // Renderer
    const canvas = document.getElementById('world-canvas');
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 50, 50);
    scene.add(directionalLight);
    
    // Simple orbit controls (manual implementation)
    setupControls();
    
    // Entity click: raycast and show entity details (properties, age, position including w)
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    const canvas = document.getElementById('world-canvas');
    canvas.addEventListener('click', onCanvasClick);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start API polling
    api.startPolling(updateWorld, updateNews, updateDirection);
    
    // Start render loop
    animate();
}

function setupControls() {
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let rotation = { x: 0, y: 0 };
    let distance = 150;
    
    const canvas = document.getElementById('world-canvas');
    
    canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;
        
        rotation.y += deltaX * 0.01;
        rotation.x += deltaY * 0.01;
        
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    canvas.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        distance += e.deltaY * 0.1;
        distance = Math.max(50, Math.min(500, distance));
    });
    
    // Update camera position in render loop
    function updateCamera() {
        const x = distance * Math.sin(rotation.y) * Math.cos(rotation.x);
        const y = distance * Math.sin(rotation.x);
        const z = distance * Math.cos(rotation.y) * Math.cos(rotation.x);
        
        camera.position.set(x, y, z);
        camera.lookAt(0, 0, 0);
    }
    
    window.updateCameraControls = updateCamera;
}

function onWindowResize() {
    const canvas = document.getElementById('world-canvas');
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
}

function updateWorld(data) {
    if (!data) return;
    worldData = data;
    if (window.updateRenderer) {
        window.updateRenderer(data);
    }
}

function updateNews(data) {
    newsFeed.update(data);
}

function updateDirection(data) {
    if (window.directionPanel) window.directionPanel.update(data);
}

function onCanvasClick(event) {
    if (!scene || !camera || !worldData) return;
    const canvas = document.getElementById('world-canvas');
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const entityMeshes = [];
    scene.traverse(obj => {
        if (obj.userData && obj.userData.entity) entityMeshes.push(obj);
    });
    const hits = raycaster.intersectObjects(entityMeshes);
    const panel = document.getElementById('entity-details');
    const info = document.getElementById('entity-info');
    const newsPanel = document.getElementById('news-panel');
    const directionPanel = document.getElementById('direction-panel');
    if (!panel || !info) return;
    if (hits.length === 0) {
        panel.style.display = 'none';
        if (newsPanel) newsPanel.classList.add('active');
        if (directionPanel) directionPanel.classList.remove('active');
        return;
    }
    const entity = hits[0].object.userData.entity;
    info.innerHTML = '';
    const add = (label, value) => {
        const p = document.createElement('p');
        p.innerHTML = '<strong>' + label + ':</strong> ' + (typeof value === 'object' ? JSON.stringify(value) : value);
        info.appendChild(p);
    };
    add('ID', entity.id);
    add('Type', entity.type);
    add('Position', (entity.position || {}).x + ', ' + (entity.position || {}).y + ', ' + (entity.position || {}).z + (entity.position && entity.position.w != null ? ', w=' + entity.position.w : ''));
    if (entity.age != null) add('Age', entity.age);
    if (entity.properties && Object.keys(entity.properties).length) add('Properties', entity.properties);
    panel.style.display = 'block';
    if (newsPanel) newsPanel.classList.remove('active');
    if (directionPanel) directionPanel.classList.remove('active');
    document.querySelectorAll('.sidebar-tabs .tab-btn').forEach(b => b.classList.remove('active'));
}

function animate() {
    requestAnimationFrame(animate);
    
    if (window.updateCameraControls) {
        window.updateCameraControls();
    }
    
    renderer.render(scene, camera);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
