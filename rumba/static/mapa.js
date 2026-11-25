// Código web común a todas las tareas: sondeo del servidor y dibujo del mapa.
// Sistema de referencia: origen donde arranca el robot, x hacia delante, y hacia la izquierda (mm).

const $ = id => document.getElementById(id);
const r2 = v => Math.round(v * 100) / 100;
const RADIO_ROBOT = 174;   // mm, Ø 348,5 mm según la spec

// ---------- Comunicación con el servidor ----------
const post = url => fetch(url, { method: 'POST' }).catch(() => {});

// Pide /estado cada `periodo` ms y acumula el rastro. alRecibir(datos, camino) pinta el resto.
function iniciarSondeo({ alRecibir, alFallar, periodo = 100 }) {
  let camino = [], rev = -1, temporizador = null;
  async function sondear() {
    try {
      const r = await fetch('/estado?desde=' + camino.length + '&rev=' + rev);
      const d = await r.json();
      if (d.rev !== rev) { camino = []; rev = d.rev; }
      camino.push(...d.nuevos);
      alRecibir(d, camino);
    } catch (e) {
      if (alFallar) alFallar();
    }
    temporizador = setTimeout(sondear, periodo);
  }
  const ya = () => { clearTimeout(temporizador); sondear(); };
  sondear();
  return { sondearYa: ya };
}

const gradosDe = theta => Math.atan2(Math.sin(theta), Math.cos(theta)) * 180 / Math.PI;

// ---------- Mapa ----------
class Mapa {
  constructor(canvas) {
    this.cv = canvas;
    this.ctx = canvas.getContext('2d');
    this.vista = null;
  }

  // Limpia, encuadra todos los puntos con margen (mínimo 2 m x 2 m), dibuja la cuadrícula
  // cada 0,5 m y devuelve la función mm -> píxeles.
  preparar(puntos) {
    const { cv, ctx } = this;
    const dpr = devicePixelRatio || 1, W = cv.clientWidth, H = cv.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const [px, py] of puntos) {
      if (px < minX) minX = px; if (px > maxX) maxX = px;
      if (py < minY) minY = py; if (py > maxY) maxY = py;
    }
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    const ancho = Math.max(maxX - minX + 1000, 2000);
    const alto = Math.max(maxY - minY + 1000, 2000);
    const esc = Math.min(W / ancho, H / alto);           // px por mm
    this.vista = { cx, cy, esc, W, H };
    const aPx = (x, y) => [W / 2 + (x - cx) * esc, H / 2 - (y - cy) * esc];
    this.aPx = aPx;

    const paso = 500;
    const x0 = cx - W / 2 / esc, x1 = cx + W / 2 / esc;
    const y0 = cy - H / 2 / esc, y1 = cy + H / 2 / esc;
    ctx.font = '11px system-ui'; ctx.fillStyle = '#8a8f94';
    for (let gx = Math.ceil(x0 / paso) * paso; gx <= x1; gx += paso) {
      const [px] = aPx(gx, 0);
      ctx.strokeStyle = gx === 0 ? '#a3a3a3' : '#e4e4df'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
      ctx.fillText((gx / 1000).toFixed(1) + ' m', px + 3, H - 6);
    }
    for (let gy = Math.ceil(y0 / paso) * paso; gy <= y1; gy += paso) {
      const [, py] = aPx(0, gy);
      ctx.strokeStyle = gy === 0 ? '#a3a3a3' : '#e4e4df'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(W, py); ctx.stroke();
      ctx.fillText((gy / 1000).toFixed(1) + ' m', W - 40, py - 3);
    }
    return aPx;
  }

  // Coordenadas del clic en metros (para "ir a este punto")
  clicAMetros(e) {
    if (!this.vista) return null;
    const v = this.vista, r = this.cv.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    return [(v.cx + (px - v.W / 2) / v.esc) / 1000, (v.cy - (py - v.H / 2) / v.esc) / 1000];
  }

  linea(puntos, { color, ancho = 1.5, guiones = [] }) {
    const { ctx, aPx } = this;
    ctx.strokeStyle = color; ctx.lineWidth = ancho; ctx.setLineDash(guiones);
    ctx.beginPath();
    puntos.forEach(([x, y], i) => { const [px, py] = aPx(x, y); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
    ctx.stroke(); ctx.setLineDash([]);
  }

  punto(p, color, radio, cuadrado) {
    const { ctx, aPx } = this, [px, py] = aPx(p[0], p[1]);
    ctx.fillStyle = color;
    ctx.beginPath();
    if (cuadrado) ctx.rect(px - radio, py - radio, 2 * radio, 2 * radio);
    else ctx.arc(px, py, radio, 0, 2 * Math.PI);
    ctx.fill();
  }

  aspa(p, color = '#ea580c') {
    const { ctx, aPx } = this, [ox, oy] = aPx(p[0], p[1]);
    ctx.strokeStyle = color; ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(ox - 8, oy - 8); ctx.lineTo(ox + 8, oy + 8);
    ctx.moveTo(ox + 8, oy - 8); ctx.lineTo(ox - 8, oy + 8);
    ctx.stroke();
  }

  // Rastro recorrido hasta la posición actual
  camino(camino, pose) {
    const { ctx, aPx } = this, [rx, ry] = aPx(pose.x, pose.y);
    ctx.strokeStyle = '#2563eb'; ctx.lineWidth = 2.2; ctx.lineJoin = 'round';
    ctx.beginPath();
    camino.forEach(([x, y], i) => { const [px, py] = aPx(x, y); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
    if (camino.length) ctx.lineTo(rx, ry);
    ctx.stroke();
  }

  // Robot con su orientación; `giroRestante` (rad) dibuja el arco de un giro en curso
  robot(pose, giroRestante) {
    const { ctx, aPx, vista } = this, [rx, ry] = aPx(pose.x, pose.y);
    const r = RADIO_ROBOT * vista.esc;
    ctx.fillStyle = 'rgba(220, 38, 38, 0.13)'; ctx.strokeStyle = '#dc2626'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(rx, ry, r, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(rx, ry);
    ctx.lineTo(rx + Math.cos(pose.theta) * r, ry - Math.sin(pose.theta) * r); ctx.stroke();
    if (giroRestante) {
      const a0 = -pose.theta, a1 = -(pose.theta + giroRestante);
      ctx.strokeStyle = '#ea580c'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(rx, ry, r + 8, Math.min(a0, a1), Math.max(a0, a1)); ctx.stroke();
    }
  }
}
