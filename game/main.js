// GooBall Revival — Three.js 可玩重建（level3 / New Mexico）
// 资产：2005 原版 Unity 1.x 逆向出土（OBJ 网格 + PNG 纹理 + 场景图 + 材质绑定）
import * as THREE from './lib/three.module.js';

const $ = id => document.getElementById(id);
const R = 0.3;                 // 球半径（来自原版 SphereCollider m_Radius）
const GRAV = -25, ACCEL = 30, MAXSPD = 16, JUMP = 9;   // BallController 实测参数

// ---------- 极简 OBJ 解析器（v/vt/vn/f，支持多边形扇形三角化） ----------
function parseOBJ(text) {
  const P = [], N = [], UV = [], F = [];
  for (const line of text.split('\n')) {
    const t = line.trim().split(/\s+/);
    if (t[0] === 'v')   P.push([+t[1], +t[2], +t[3]]);
    else if (t[0] === 'vn')  N.push([+t[1], +t[2], +t[3]]);
    else if (t[0] === 'vt')  UV.push([+t[1], +t[2]]);
    else if (t[0] === 'f') {
      const idx = t.slice(1).map(s => {
        const [p, u, n] = s.split('/');
        return [+p - 1, u ? +u - 1 : -1, n ? +n - 1 : -1];
      });
      F.push(idx);
    }
  }
  const pos = [], nor = [], uv = [];
  for (const f of F)
    for (let i = 1; i < f.length - 1; i++)
      for (const k of [0, i, i + 1]) {
        const [p, u, n] = f[k];
        pos.push(...P[p]);
        if (n >= 0 && N[n]) nor.push(...N[n]);
        uv.push(...(u >= 0 && UV[u] ? UV[u] : [0, 0]));
      }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  if (nor.length === pos.length) g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  if (uv.length / 2 === pos.length / 3) g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  if (nor.length !== pos.length) g.computeVertexNormals();
  return g;
}

// 行主序 TRS 数组 → three 列主序 Matrix4
function matFromRows(m) {
  return new THREE.Matrix4().fromArray(
    [m[0], m[4], m[8], m[12], m[1], m[5], m[9], m[13],
     m[2], m[6], m[10], m[14], m[3], m[7], m[11], m[15]]);
}

// ---------- 场景初始化 ----------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87a8d4);
scene.fog = new THREE.Fog(0x87a8d4, 120, 420);
const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 1200);
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x54492e, 1.0));
const sun = new THREE.DirectionalLight(0xfff2d9, 1.4);
sun.position.set(60, 120, 40);
scene.add(sun);

const world = new THREE.Group();
world.rotation.y = Math.PI;          // Unity(左手) → three(右手)
scene.add(world);

const loader = new THREE.TextureLoader();
const geoCache = new Map(), texCache = new Map();
const colliders = [];   // 参与碰撞的网格

function getTex(url) {
  if (!texCache.has(url)) texCache.set(url, loader.load(url, t => { t.colorSpace = THREE.SRGBColorSpace; }));
  return texCache.get(url);
}

async function loadLevel(data) {
  const total = data.objects.length;
  let done = 0;
  for (const it of data.objects) {
    let geo = geoCache.get(it.mesh);
    if (!geo) {
      try {
        geo = parseOBJ(await (await fetch(it.mesh)).text());
      } catch (e) { done++; continue; }
      geoCache.set(it.mesh, geo);
    }
    let mat;
    if (it.textures && it.textures.length)
      mat = new THREE.MeshLambertMaterial({ map: getTex(it.textures[0]), side: THREE.DoubleSide });
    else {
      const c = it.color ? new THREE.Color(it.color[0], it.color[1], it.color[2]) : new THREE.Color(0x9a8a6a);
      mat = new THREE.MeshLambertMaterial({ color: c, side: THREE.DoubleSide });
    }
    const mesh = new THREE.Mesh(geo, mat);
    if (it.matrix) mesh.matrixAutoUpdate = false, mesh.matrix.copy(matFromRows(it.matrix));
    world.add(mesh);
    if (it.mesh.includes('sky') === false) colliders.push(mesh);
    done++;
    if (done % 20 === 0 || done === total) {
      $('bar').firstElementChild.style.width = (done / total * 80) + '%';
      $('loadmsg').textContent = `构建关卡 ${done}/${total}`;
      await new Promise(r => setTimeout(r));
    }
  }
  return data;
}

// ---------- 球 / 星 / 目标 ----------
const ball = new THREE.Mesh(
  new THREE.SphereGeometry(R, 32, 24),
  new THREE.MeshStandardMaterial({ color: 0xd8dbe2, roughness: .35, metalness: .1 }));
scene.add(ball);
const ballV = new THREE.Vector3();

function makeStar(p) {
  const m = new THREE.Mesh(new THREE.OctahedronGeometry(0.45),
    new THREE.MeshStandardMaterial({ color: 0xffd23e, emissive: 0xcc8800, roughness: .3 }));
  m.position.set(p[0], p[1] + 1.2, p[2]);
  world.add(m);
  return m;
}
function makeGoal(p) {
  const m = new THREE.Mesh(new THREE.TorusGeometry(1.6, .18, 12, 40),
    new THREE.MeshStandardMaterial({ color: 0x53ff88, emissive: 0x0a9944 }));
  m.position.set(p[0], p[1] + 1.6, p[2]);
  world.add(m);
  return m;
}

// ---------- 输入 ----------
const key = {};
addEventListener('keydown', e => { key[e.code] = true; if (e.code === 'KeyR') respawn(); });
addEventListener('keyup', e => key[e.code] = false);

let stars = [], goal = null, level = null, playing = false;
let got = 0, t0 = 0, spawn = new THREE.Vector3(0, 8, 0);

function respawn() {
  ball.position.copy(spawn);
  ballV.set(0, 0, 0);
}

// ---------- 物理 ----------
const down = new THREE.Vector3(0, -1, 0), tmp = new THREE.Vector3(), tmp2 = new THREE.Vector3();
const ray = new THREE.Raycaster();

function physics(dt) {
  const f = new THREE.Vector3(
    (key.KeyD || key.ArrowRight ? 1 : 0) - (key.KeyA || key.ArrowLeft ? 1 : 0), 0,
    (key.KeyS || key.ArrowDown ? 1 : 0) - (key.KeyW || key.ArrowUp ? 1 : 0));
  // 相机相对
  const yaw = Math.atan2(camera.position.x - ball.position.x, camera.position.z - ball.position.z);
  f.applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
  if (f.lengthSq() > 0) f.normalize().multiplyScalar(ACCEL);
  ballV.addScaledVector(f, dt);
  ballV.y += GRAV * dt;
  if (key.Space && ballGrounded) { ballV.y = JUMP; ballGrounded = false; }
  if (ballV.length() > MAXSPD) ballV.setLength(MAXSPD);
  ball.position.addScaledVector(ballV, dt);
  // 地面
  ballGrounded = false;
  ray.set(ball.position, down); ray.far = R + 0.6;
  const hit = ray.intersectObjects(colliders, false)[0];
  if (hit && hit.distance < R + 0.05) {
    ball.position.copy(hit.point).addScaledVector(down, -R);
    if (ballV.y < 0) ballV.y = 0;
    ballGrounded = true;
    ballV.x *= 0.96; ballV.z *= 0.96;
  }
  // 墙面（水平方向）
  tmp.copy(ballV); tmp.y = 0;
  if (tmp.lengthSq() > 1e-4) {
    tmp.normalize();
    ray.set(ball.position, tmp); ray.far = R + 0.2;
    const wh = ray.intersectObjects(colliders, false)[0];
    if (wh && wh.distance < R) {
      tmp2.copy(wh.face.normal).transformDirection(wh.object.matrixWorld);
      ballV.addScaledVector(tmp2, Math.min(0, -ballV.dot(tmp2)));
      ball.position.copy(wh.point).addScaledVector(tmp, -R);
    }
  }
  if (ball.position.y < -60) respawn();
}
let ballGrounded = false;

// ---------- HUD / 拾取 ----------
function updateGame(dt) {
  for (const s of stars) if (s.visible) {
    s.rotation.y += dt * 2.5;
    s.position.y += Math.sin(performance.now() / 400) * 0.002;
    if (s.position.distanceTo(ball.position) < 1.1) {
      s.visible = false; got++; blip(880);
      $('stars').textContent = `★ ${got} / ${stars.length}`;
      if (got === stars.length) blip(1320);
    }
  }
  if (goal) {
    goal.rotation.z += dt;
    if (got === stars.length && goal.position.distanceTo(ball.position) < 2.2) win();
  }
  $('time').textContent = ((performance.now() - t0) / 1000).toFixed(1) + ' s';
}
function blip(freq) {
  try {
    const ac = blip.ac || (blip.ac = new AudioContext());
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.value = freq; o.type = 'triangle';
    g.gain.setValueAtTime(.15, ac.currentTime);
    g.gain.exponentialRampToValueAtTime(.001, ac.currentTime + .25);
    o.connect(g).connect(ac.destination); o.start(); o.stop(ac.currentTime + .25);
  } catch (e) { }
}
function win() {
  playing = false;
  $('overlay').classList.remove('hidden');
  $('overlay').querySelector('h1').textContent = '关卡完成！';
  $('overlay').querySelector('p').innerHTML =
    `★ ${got}/${stars.length} · 用时 ${((performance.now() - t0) / 1000).toFixed(1)} s<br>2005 年的 goo 球，2026 年重新滚动`;
  $('play').textContent = '再来一次';
  $('play').style.display = '';
}

// ---------- 主循环 ----------
let last = 0;
function loop(t) {
  requestAnimationFrame(loop);
  const dt = Math.min((t - last) / 1000, 0.05); last = t;
  if (playing) {
    physics(dt);
    updateGame(dt);
    // 相机跟随
    tmp.copy(ball.position).add(new THREE.Vector3(0, 6, 9));
    camera.position.lerp(tmp, 1 - Math.pow(0.001, dt));
    camera.lookAt(ball.position);
    // 球滚动
    const spin = new THREE.Vector3(ballV.z, 0, -ballV.x).multiplyScalar(dt / R);
    if (spin.lengthSq() > 0) ball.rotateOnWorldAxis(spin.normalize(), spin.length());
  }
  renderer.render(scene, camera);
}

// ---------- 启动 / 选关 ----------
// 关卡表出土自 MapInfo::SetupLevels 的 IL 硬编码（12 章 51 关）
const bgm = new Audio('assets/audio/techno-jazz.ogg'); bgm.loop = true; bgm.volume = 0.8;

async function startLevel(lv) {
  $('back').style.display = '';
  $('subtitle').textContent = `${lv.name} · level${lv.id} · ${lv.chapter}`;
  if (lv.bgm) bgm.src = lv.bgm;
  $('loadmsg').textContent = '正在加载出土资产…';
  $('bar').style.display = '';
  const data = await (await fetch(`data/level${lv.id}.json`)).json();
  level = await loadLevel(data);
  stars = data.stars.map(makeStar);
  if (data.goals.length) goal = makeGoal(data.goals[0]);
  spawn.fromArray(data.spawn);
  respawn();
  $('bar').firstElementChild.style.width = '100%';
  $('loadmsg').textContent = `就绪：${data.objects.length} 对象 · ${stars.length} ★`;
  $('play').style.display = '';
  $('play').onclick = () => {
    $('overlay').classList.add('hidden');
    got = 0; stars.forEach(s => s.visible = true);
    $('stars').textContent = `★ 0 / ${stars.length}`;
    respawn(); t0 = performance.now(); playing = true;
    bgm.play().catch(() => { });
  };
}

async function boot() {
  const meta = await (await fetch('data/levels.json')).json();
  const avail = new Set(meta.generated || []);
  $('bar').style.display = 'none';
  $('loadmsg').textContent = '选择关卡';
  const menu = $('menu');
  menu.style.display = 'block';
  for (const ch of meta.chapters) {
    const list = ch.levels.filter(l => avail.has(l.id));
    if (!list.length) continue;
    const h = document.createElement('div');
    h.className = 'chapter'; h.textContent = ch.name;
    menu.appendChild(h);
    for (const lv of list) {
      const b = document.createElement('button');
      b.className = 'lvbtn'; b.textContent = lv.name;
      b.onclick = () => { menu.style.display = 'none'; startLevel({ ...lv, chapter: ch.name, bgm: ch.bgm }); };
      menu.appendChild(b);
    }
  }
}
$('back').onclick = () => location.reload();
requestAnimationFrame(loop);
boot();
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
