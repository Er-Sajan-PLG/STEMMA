import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';
import { forceX, forceY, forceZ } from 'd3-force-3d';
import { GraphProjection, GraphNode } from '../services/graph-projection';
import { GRAPH_THEME } from '../styles/theme';

export interface GraphViewOptions {
  container: HTMLElement;
  onNodeSelect: (nodeId: string | null) => void;
  onClusterSelect?: (clusterId: string | null) => void;
}

// Shape per entity type: quantity=sphere, law=octahedron, equation=box,
// concept=icosahedron, unit=m-small sphere.
const NODE_GEOMETRY_BY_TYPE: Record<string, (() => THREE.BufferGeometry) | undefined> = {
  law: () => new THREE.OctahedronGeometry(1, 0),
  equation: () => new THREE.BoxGeometry(1, 1, 1),
  quantity: () => new THREE.SphereGeometry(1, 24, 24),
  concept: () => new THREE.IcosahedronGeometry(1, 1),
  unit: () => new THREE.SphereGeometry(1, 20, 20),
};
const _geomCache = new Map<string, THREE.BufferGeometry>();
function geometryFor(type: string): THREE.BufferGeometry {
  if (!_geomCache.has(type || '')) {
    const maker = NODE_GEOMETRY_BY_TYPE[type || ''] || NODE_GEOMETRY_BY_TYPE.quantity!;
    _geomCache.set(type || '', maker());
  }
  return _geomCache.get(type || '')!;
}

// A persistent, always-visible sprite label so users can orient in 3D without
// hovering. Hubs (high degree) get larger labels.
function makeLabelSprite(node: GraphNode): THREE.Sprite {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d')!;
  const fontSize = 42;
  canvas.width = 700;
  canvas.height = 180;
  ctx.font = `${fontSize}px Inter, sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  const label = `${node.name}`;
  // faint pill background
  const w = ctx.measureText(label).width + 60;
  const h = 90;
  ctx.fillStyle = 'rgba(5, 2, 15, 0.65)';
  ctx.beginPath();
  ctx.roundRect((canvas.width - w) / 2, (canvas.height - h) / 2, w, h, 40);
  ctx.fill();
  ctx.fillStyle = '#ffffff';
  ctx.shadowColor = node.color;
  ctx.shadowBlur = 22;
  ctx.fillText(label, canvas.width / 2, canvas.height / 2);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(9, 2.3, 1);
  sprite.position.y = 1.6;
  return sprite;
}

// Halo sprite used for selection/hover glow.
function makeGlowSprite(color: string, radius: number): THREE.Sprite {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  const grad = ctx.createRadialGradient(128, 128, 4, 128, 128, 128);
  grad.addColorStop(0, color);
  grad.addColorStop(0.28, `${color}aa`);
  grad.addColorStop(0.62, `${color}44`);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 256, 256);
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    opacity: 0.85,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(radius, radius, 1);
  return sprite;
}

// A camera-facing ring that marks the selected / hovered node.
function makeRingSprite(color: string, radius: number): THREE.Sprite {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  ctx.strokeStyle = color;
  ctx.lineWidth = 10;
  ctx.shadowColor = color;
  ctx.shadowBlur = 22;
  ctx.beginPath();
  ctx.arc(128, 128, 108, 0, Math.PI * 2);
  ctx.stroke();
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    opacity: 0.95,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(radius, radius, 1);
  return sprite;
}

type Endpoint = string | { id: string };
function endpointId(value: Endpoint): string {
  return typeof value === 'string' ? value : value?.id ?? '';
}

export class GraphView {
  private graph: any;
  private container: HTMLElement;
  private onNodeSelect: (nodeId: string | null) => void;
  private onClusterSelect?: (clusterId: string | null) => void;
  private currentProjection: GraphProjection | null = null;
  private selectedNodeId: string | null = null;
  private hoveredNodeId: string | null = null;
  private isAutoRotating: boolean = false;
  private clusterAnchors = new Map<string, { x: number; y: number; z: number }>();
  private spriteLayer: THREE.Group = new THREE.Group();

  // Node object / animation bookkeeping for hover & selection pop.
  private nodeObjMap = new Map<string, THREE.Object3D>();
  private scaleAnimTargets = new Map<string, number>();
  private scaleAnimRunning = false;

  constructor(options: GraphViewOptions) {
    this.container = options.container;
    this.onNodeSelect = options.onNodeSelect;
    this.onClusterSelect = options.onClusterSelect;
    this.initGraph();
    this.attachResizeListener();
  }

  private initGraph(): void {
    const Factory = (ForceGraph3D as any).default || ForceGraph3D;
    const width = this.container.clientWidth || Math.floor(window.innerWidth * 0.75);
    const height = this.container.clientHeight || (window.innerHeight - 61);

    this.graph = Factory()(this.container)
      .width(width)
      .height(height)
      .backgroundColor(GRAPH_THEME.canvas.background)
      .nodeId('id')
      .nodeLabel((node: any) => `
        <div style="background:rgba(8,4,26,0.95);backdrop-filter:blur(8px);padding:8px 14px;border-radius:10px;border:1px solid ${node.color}66;color:#fff;font-family:'Inter',sans-serif;font-size:0.85rem;box-shadow:0 10px 28px rgba(0,0,0,0.6),0 0 18px ${node.color}33;max-width:300px;">
          <div style="font-weight:800;color:#fff;font-size:0.95rem;font-family:'Outfit',sans-serif;text-shadow:0 0 14px ${node.color}55;">${node.name}</div>
          <div style="display:flex;align-items:center;gap:6px;margin-top:2px;">
            <span style="color:${node.color};font-size:0.72rem;font-weight:800;text-transform:uppercase;letter-spacing:0.06em;">${node.domain}</span>
            <span style="color:#a9b3d9;font-size:0.72rem;">· ${node.type}</span>
          </div>
          ${node.clusterLabel ? `<div style="color:#8088ad;font-size:0.7rem;margin-top:2px;">${node.clusterLabel}</div>` : ''}
          <div style="color:#6b7394;font-size:0.68rem;margin-top:4px;font-family:'Fira Code',monospace;">${node.id}</div>
        </div>
      `)
      .nodeColor((node: any) => {
        const activeId = this.selectedNodeId || this.hoveredNodeId;
        if (activeId && node.id !== activeId) {
          const isConnected = this.currentProjection?.links.some(
            l => (endpointId(l.source) === activeId && endpointId(l.target) === node.id) ||
                 (endpointId(l.target) === activeId && endpointId(l.source) === node.id)
          );
          return isConnected ? node.color : '#3a3757';
        }
        return node.color;
      })
      .nodeVal((node: any) => node.val)
      .nodeThreeObject((node: any) => this.renderNode(node))
      .nodeThreeObjectExtend(true)
      .linkColor((link: any) => {
        const activeId = this.selectedNodeId || this.hoveredNodeId;
        if (activeId) {
          const isConnected = endpointId(link.source) === activeId || endpointId(link.target) === activeId;
          return isConnected ? link.color : 'rgba(58, 55, 87, 0.2)';
        }
        return link.color;
      })
      .linkWidth((link: any) => {
        const activeId = this.selectedNodeId || this.hoveredNodeId;
        if (activeId) {
          const isConnected = endpointId(link.source) === activeId || endpointId(link.target) === activeId;
          return isConnected ? link.width * 1.6 : 0.6;
        }
        return link.width;
      })
      .linkOpacity((link: any) => {
        const activeId = this.selectedNodeId || this.hoveredNodeId;
        if (activeId) {
          const isConnected = endpointId(link.source) === activeId || endpointId(link.target) === activeId;
          return isConnected ? 1 : 0.06;
        }
        // E1.6: opacity carries assertion trust — unreviewed claims read as faint edges.
        return link.trustOpacity ?? 0.55;
      })
      .linkDirectionalParticles((link: any) => link.directional ? 2 : 0)
      .linkDirectionalParticleSpeed((link: any) => link.particleSpeed || 0.006)
      .linkDirectionalParticleWidth(2.8)
      .linkDirectionalArrowLength((link: any) => link.directional ? 4 : 0)
      .linkDirectionalArrowRelPos(0.9)
      .linkCurvature('curvature')
      .onNodeHover((node: any) => this.animateHover(node ? node.id : null))
      .onNodeClick((node: any) => {
        if (node && node.id) { this.onNodeSelect(node.id); this.focusOnNode(node); }
      })
      .onBackgroundClick(() => {
        this.onNodeSelect(null);
        if (this.onClusterSelect) this.onClusterSelect(null);
      });

    if (this.graph.d3Force) {
      this.graph.d3Force('charge').strength(-90);
      this.graph.d3Force('link').distance(60);
    }
  }

  private renderNode(node: GraphNode): THREE.Object3D {
    const geo = geometryFor(node.type);
    const baseScale = node.val / 6.5;
    const mat = new THREE.MeshStandardMaterial({
      color: node.color,
      emissive: node.color,
      emissiveIntensity: this.selectedNodeId === node.id ? 0.85 : 0.22,
      roughness: 0.28,
      metalness: 0.55,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.scale.set(baseScale, baseScale, baseScale);

    // persistent sprite label
    const sprite = makeLabelSprite(node);
    const group = new THREE.Group();
    group.add(mesh);
    group.add(sprite);

    // Selection + hover bloom
    const isSelected = this.selectedNodeId === node.id;
    const isHovered = this.hoveredNodeId === node.id;
    const halo = makeGlowSprite(node.color, baseScale * 3.1);
    const ring = makeRingSprite('#ffffff', baseScale * 2.5);
    halo.visible = isSelected || isHovered;
    ring.visible = isSelected;
    group.add(halo);
    group.add(ring);

    group.userData = {
      nodeId: node.id,
      baseScale,
      mesh,
      material: mat,
      halo,
      ring,
    };
    this.nodeObjMap.set(node.id, group);
    this.scaleAnimTargets.set(node.id, isHovered ? 1.28 : isSelected ? 1.12 : 1);
    return group;
  }

  private animateHover(nodeId: string | null): void {
    this.hoveredNodeId = nodeId;
    if (!this.nodeObjMap.size) return;
    for (const [id, obj] of this.nodeObjMap) {
      const isHover = id === this.hoveredNodeId;
      const isSelected = id === this.selectedNodeId;
      this.scaleAnimTargets.set(id, isHover ? 1.28 : isSelected ? 1.12 : 1);
      const halo = obj.userData?.halo as THREE.Sprite | undefined;
      const ring = obj.userData?.ring as THREE.Sprite | undefined;
      if (halo) halo.visible = isHover || isSelected;
      if (ring) ring.visible = isSelected;
    }
    this.animateNodeScales();
  }

  private animateNodeScales(): void {
    if (this.scaleAnimRunning) return;
    this.scaleAnimRunning = true;
    const loop = () => {
      let done = true;
      const now = performance.now();
      for (const obj of this.nodeObjMap.values()) {
        const user = obj.userData;
        if (!user?.mesh) continue;
        const target = this.scaleAnimTargets.get(user.nodeId) ?? 1;
        const base = user.baseScale ?? 1;
        const desired = base * target;
        const cur = user.mesh.scale.x;
        const next = cur + (desired - cur) * 0.16;
        user.mesh.scale.set(next, next, next);
        if (Math.abs(next - desired) > 0.002) done = false;

        // emissive pop on hover / selection
        const isHover = this.hoveredNodeId === user.nodeId;
        const isSelected = this.selectedNodeId === user.nodeId;
        if (user.material) {
          const targetGlow = isHover ? 1.05 : isSelected ? 0.9 : 0.22;
          const curGlow = user.material.emissiveIntensity;
          user.material.emissiveIntensity = curGlow + (targetGlow - curGlow) * 0.16;
        }

        if (user.halo) {
          const pulse = 1 + Math.sin(now / 420) * 0.12;
          const h = base * 3.1 * pulse;
          user.halo.scale.set(h, h, 1);
        }
        if (user.ring) {
          const pulse = 1 + Math.sin(now / 320) * 0.08;
          const r = base * 2.5 * pulse;
          user.ring.scale.set(r, r, 1);
        }
      }
      if (done) {
        this.scaleAnimRunning = false;
        return;
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  private applyClusterForces(): void {
    if (!this.graph || !this.currentProjection) return;
    // Gently pull each node toward its seeded cluster coordinate so grouped
    // regions hold their shape instead of collapsing into a single blob. The
    // seed positions were computed in graph-projection.ts per domain/topic.
    const get = (d: any, key: string) => (d && typeof d[key] === 'number' ? d[key] : 0);
    this.graph.d3Force('clusterX', forceX().x((d: any) => get(d, 'seedX')).strength(0.06));
    this.graph.d3Force('clusterY', forceY().y((d: any) => get(d, 'seedY')).strength(0.06));
    this.graph.d3Force('clusterZ', forceZ().z((d: any) => get(d, 'seedZ')).strength(0.06));
  }

  private attachResizeListener(): void {
    window.addEventListener('resize', () => {
      if (this.graph && this.container) {
        const w = this.container.clientWidth || Math.floor(window.innerWidth * 0.75);
        const h = this.container.clientHeight || (window.innerHeight - 61);
        this.graph.width(w).height(h);
      }
    });
  }

  public updateProjection(projection: GraphProjection, selectedId: string | null): void {
    this.currentProjection = projection;
    this.selectedNodeId = selectedId;
    this.hoveredNodeId = null;
    this.clusterAnchors.clear();
    this.nodeObjMap.clear();
    for (const cluster of projection.clusters) {
      this.clusterAnchors.set(cluster.id, { x: cluster.anchorX, y: cluster.anchorY, z: cluster.anchorZ });
    }
    const dataNodes = projection.nodes.map(n => ({ ...n, x: n.seedX, y: n.seedY, z: n.seedZ }));
    this.graph.graphData({ nodes: dataNodes, links: projection.links.map(l => ({ ...l })) });
    this.applyClusterForces();
    if (selectedId) {
      const node = projection.nodes.find(n => n.id === selectedId);
      if (node) setTimeout(() => this.focusOnNode(node), 250);
    }
  }

  public focusOnNode(node: GraphNode): void {
    const distance = 70;
    const nodes = this.graph.graphData().nodes;
    const graphNode = nodes.find((n: any) => n.id === node.id);
    if (!graphNode) return;
    const x = graphNode.x || 0, y = graphNode.y || 0, z = graphNode.z || 0;
    const distRatio = 1 + distance / (Math.hypot(x, y, z) || 1);
    this.graph.cameraPosition(
      { x: x * distRatio, y: y * distRatio, z: z * distRatio },
      { x, y, z },
      1400
    );
  }

  public focusOnCluster(clusterId: string): void {
    const anchor = this.clusterAnchors.get(clusterId);
    if (!anchor) return;
    this.graph.cameraPosition(
      { x: anchor.x * 2, y: anchor.y * 2, z: anchor.z * 2 },
      { x: anchor.x, y: anchor.y, z: anchor.z },
      1600
    );
  }

  public toggleAutoRotate(): boolean {
    this.isAutoRotating = !this.isAutoRotating;
    const controls = this.graph.controls();
    if (controls) { controls.autoRotate = this.isAutoRotating; controls.autoRotateSpeed = 0.8; }
    return this.isAutoRotating;
  }
  public zoomIn(): void {
    const cam = this.graph.cameraPosition();
    this.graph.cameraPosition({ x: cam.x * 0.8, y: cam.y * 0.8, z: cam.z * 0.8 });
  }
  public zoomOut(): void {
    const cam = this.graph.cameraPosition();
    this.graph.cameraPosition({ x: cam.x * 1.25, y: cam.y * 1.25, z: cam.z * 1.25 });
  }
  public resetView(): void {
    this.graph.zoomToFit(1000, 60);
  }
}
