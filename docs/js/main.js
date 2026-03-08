/** Three.js scene setup and main application logic */

let scene, camera, renderer, controls;
let worldData = null;

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
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start API polling
    api.startPolling(updateWorld, updateNews);
    
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
