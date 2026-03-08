/** World rendering logic with Three.js */

let entityObjects = new Map();
let physicsZones = [];

function initRenderer(scene) {
    // Grid helper
    const gridHelper = new THREE.GridHelper(200, 20, 0x444444, 0x222222);
    scene.add(gridHelper);
    
    // Axes helper
    const axesHelper = new THREE.AxesHelper(50);
    scene.add(axesHelper);
}

function updateRenderer(worldData) {
    if (!worldData || !window.scene) return;
    
    const scene = window.scene;
    const entities = worldData.entities || [];
    const physics = worldData.physics || {};
    const events = worldData.events || [];
    const anomalies = worldData.anomalies || [];
    
    // Update entities
    updateEntities(scene, entities);
    
    // Update physics zones (with labels: gravity = red, time = blue)
    updatePhysicsZones(scene, physics);
    
    // Update events and anomalies as temporary markers
    updateEventsAndAnomalies(scene, events, anomalies);
}

function updateEntities(scene, entities) {
    // Remove old entities not in current data
    const currentIds = new Set(entities.map(e => e.id));
    entityObjects.forEach((obj, id) => {
        if (!currentIds.has(id)) {
            scene.remove(obj);
            entityObjects.delete(id);
        }
    });
    
    // Add/update entities
    entities.forEach(entity => {
        if (!entityObjects.has(entity.id)) {
            const obj = createEntityObject(entity);
            if (obj) {
                scene.add(obj);
                entityObjects.set(entity.id, obj);
            }
        } else {
            updateEntityObject(entityObjects.get(entity.id), entity);
        }
    });
}

function createEntityObject(entity) {
    const type = entity.type || 'Unknown';
    const position = entity.position || { x: 0, y: 0, z: 0 };
    const w = position.w != null ? position.w : 0;
    // Expose 4th dimension (w) via scale: larger |w| = slightly larger object
    const wScale = 1 + Math.min(1, Math.abs(w) / 10) * 0.3;
    
    let geometry, material, mesh;
    
    switch (type) {
        case 'EnergyVortex':
            geometry = new THREE.SphereGeometry(3, 16, 16);
            material = new THREE.MeshPhongMaterial({
                color: 0xff00ff,
                emissive: 0x440044,
                transparent: true,
                opacity: 0.8
            });
            break;
        case 'CrystalFormation':
            geometry = new THREE.OctahedronGeometry(2);
            material = new THREE.MeshPhongMaterial({
                color: 0x00ffff,
                emissive: 0x004444
            });
            break;
        case 'TemporalAnomaly':
            geometry = new THREE.TorusGeometry(5, 1, 8, 16);
            material = new THREE.MeshPhongMaterial({
                color: 0xffff00,
                emissive: 0x444400,
                transparent: true,
                opacity: 0.6
            });
            break;
        case 'QuantumParticle':
            geometry = new THREE.IcosahedronGeometry(1, 0);
            material = new THREE.MeshPhongMaterial({
                color: 0x00ff00,
                emissive: 0x004400
            });
            break;
        default:
            geometry = new THREE.SphereGeometry(2, 8, 8);
            material = new THREE.MeshPhongMaterial({
                color: 0x888888
            });
    }
    
    mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(
        position.x || 0,
        position.y || 0,
        position.z || 0
    );
    mesh.scale.setScalar(wScale);
    mesh.userData = { entity: entity };
    
    return mesh;
}

function updateEntityObject(obj, entity) {
    const position = entity.position || { x: 0, y: 0, z: 0 };
    const w = position.w != null ? position.w : 0;
    const wScale = 1 + Math.min(1, Math.abs(w) / 10) * 0.3;
    obj.position.set(
        position.x || 0,
        position.y || 0,
        position.z || 0
    );
    obj.scale.setScalar(wScale);
    obj.userData.entity = entity;
}

function updatePhysicsZones(scene, physics) {
    // Remove old zones
    physicsZones.forEach(zone => scene.remove(zone));
    physicsZones = [];
    
    // Add gravity zones
    const gravityZones = physics.gravity?.zones || [];
    gravityZones.forEach(zone => {
        const helper = createZoneHelper(zone, 0xff0000);
        if (helper) {
            scene.add(helper);
            physicsZones.push(helper);
        }
    });
    
    // Add time zones
    const timeZones = physics.timeFlow?.zones || [];
    timeZones.forEach(zone => {
        const helper = createZoneHelper(zone, 0x0000ff);
        if (helper) {
            scene.add(helper);
            physicsZones.push(helper);
        }
    });
}

function createZoneHelper(zone, color) {
    if (zone.type === 'sphere') {
        const geometry = new THREE.SphereGeometry(zone.radius || 10, 16, 16);
        const material = new THREE.MeshBasicMaterial({
            color: color,
            wireframe: true,
            transparent: true,
            opacity: 0.3
        });
        const mesh = new THREE.Mesh(geometry, material);
        const center = zone.center || { x: 0, y: 0, z: 0 };
        mesh.position.set(center.x || 0, center.y || 0, center.z || 0);
        return mesh;
    }
    return null;
}

let eventAnomalyMarkers = [];

function updateEventsAndAnomalies(scene, events, anomalies) {
    eventAnomalyMarkers.forEach(m => scene.remove(m));
    eventAnomalyMarkers = [];
    const recentEvents = (events || []).slice(-15);
    const list = [
        ...recentEvents.map(e => ({ ...e, isAnomaly: false })),
        ...(anomalies || []).map(a => ({ ...a, isAnomaly: true }))
    ];
    list.forEach(item => {
        const pos = item.position || item.center || {};
        const geometry = new THREE.SphereGeometry(1.5, 8, 8);
        const material = new THREE.MeshBasicMaterial({
            color: item.isAnomaly ? 0xff8800 : 0x88ff88,
            transparent: true,
            opacity: 0.7
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(pos.x || 0, pos.y || 0, pos.z || 0);
        mesh.userData = { event: item };
        scene.add(mesh);
        eventAnomalyMarkers.push(mesh);
    });
}

// Expose to global scope
window.scene = null;
window.updateRenderer = updateRenderer;

// Initialize when scene is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (typeof THREE !== 'undefined') {
            // Scene will be set by main.js
            const checkScene = setInterval(() => {
                if (window.scene) {
                    initRenderer(window.scene);
                    clearInterval(checkScene);
                }
            }, 100);
        }
    }, 100);
});
