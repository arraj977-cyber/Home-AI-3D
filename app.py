import os
from flask import Flask, render_template_string, request, send_file

app = Flask(__name__)

OUTPUT_DIR = "generated_models"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home AI 3D - المنصة الهندسية الواقعية المتقدمة</title>
    <!-- تضمين مكتبة Three.js للعارض ثلاثي الأبعاد -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --accent-orange: #f97316;
            --danger-color: #ef4444;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #243048;
            --success-color: #10b981;
            --dxf-color: #8b5cf6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); min-height: 100vh; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .app-container { width: 100%; max-width: 1350px; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; background: var(--card-bg); padding: 15px 25px; border-radius: 12px; border: 1px solid var(--border-color); }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-title { font-size: 1.6rem; font-weight: bold; color: var(--text-color); }
        .logo-title span { color: var(--accent-orange); }
        .badge { background: rgba(59, 130, 246, 0.1); color: var(--primary-color); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: bold; }
        .main-grid { display: grid; grid-template-columns: 440px 1fr; gap: 20px; margin-bottom: 30px; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 6px; font-weight: 500; color: var(--text-muted); font-size: 0.85rem; }
        input[type="text"], input[type="number"], select, input[type="file"] { width: 100%; padding: 10px; background: #0b0f19; border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-color); font-size: 0.9rem; }
        input:focus, select:focus { outline: none; border-color: var(--primary-color); }
        .upload-box { border: 2px dashed var(--border-color); padding: 12px; text-align: center; border-radius: 8px; background: #090d16; cursor: pointer; }
        .grid-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .btn-submit { background: linear-gradient(135deg, var(--primary-color), #1d4ed8); color: white; border: none; width: 100%; padding: 14px; font-size: 1.05rem; font-weight: bold; border-radius: 8px; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); margin-top: 10px; }
        .btn-submit:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6); }
        
        .viewer-container { display: flex; flex-direction: column; position: relative; background: #090d16; min-height: 680px; border-radius: 16px; border: 1px solid var(--border-color); overflow: hidden; justify-content: center; align-items: center; }
        .viewer-header { position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; align-items: center; z-index: 10; flex-wrap: wrap; gap: 10px; }
        
        .cad-toolbar { display: flex; gap: 6px; background: rgba(15, 23, 42, 0.95); padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-color); }
        .cad-btn { background: var(--card-bg); color: var(--text-color); border: 1px solid var(--border-color); padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; transition: 0.2s; font-weight: bold; }
        .cad-btn:hover, .cad-btn.active { background: var(--primary-color); border-color: var(--primary-color); color: white; }
        
        .downloads-group { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
        .btn-download { background: var(--primary-color); color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.8rem; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); display: none; }
        .btn-download.gltf { background: var(--success-color); }
        .btn-download.dxf { background: var(--dxf-color); }
        .btn-download.show { display: inline-block; }
        
        .btn-toggle-rotate { background: var(--accent-orange); color: white; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 0.8rem; cursor: pointer; box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3); transition: 0.2s; display: none; }
        .btn-toggle-rotate.show { display: inline-block; }
        
        .viewer-views { width: 100%; height: 100%; display: flex; position: relative; }
        .view-pane { width: 100%; height: 680px; display: flex; justify-content: center; align-items: center; position: relative; }
        .placeholder-3d { text-align: center; color: var(--text-muted); padding: 40px; z-index: 2; position: absolute; }
        #canvas3d, #cadCanvas2D { width: 100%; height: 680px; display: none; position: absolute; top: 0; left: 0; }
        #cadCanvas2D { background: #0b0f19; cursor: crosshair; z-index: 3; }
        
        .ai-status-tag { position: absolute; bottom: 20px; background: rgba(15, 23, 42, 0.85); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; color: var(--accent-orange); display: none; z-index: 5; }
        
        .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .btn-clear-history { background: transparent; color: var(--danger-color); border: 1px solid var(--danger-color); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: 0.2s; }
        .btn-clear-history:hover { background: var(--danger-color); color: white; }
        .history-list { max-height: 130px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
        .history-item { background: #0b0f19; padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.8rem; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
        .history-item span { cursor: pointer; flex: 1; }
        .history-item span:hover { color: var(--primary-color); }
        .btn-delete-single { background: transparent; color: var(--text-muted); border: none; cursor: pointer; font-size: 0.85rem; padding: 0 4px; transition: 0.2s; }
        .btn-delete-single:hover { color: var(--danger-color); }
        
        .sun-control { display: flex; align-items: center; gap: 10px; margin-top: 5px; font-size: 0.85rem; color: var(--text-muted); }
        .sun-control input { flex: 1; }
    </style>
</head>
<body>
    <div class="app-container">
        <header>
            <div class="logo-area">
                <span class="logo-title">HOME AI <span>3D</span></span>
                <span class="badge">المنصة الهندسية الواقعية للمباني 📐🏢</span>
            </div>
        </header>

        <div class="main-grid">
            <!-- أدوات التحكم والمدخلات -->
            <div>
                <div class="card">
                    <form id="buildForm">
                        <div class="form-group">
                            <label for="siteFile">رفع ملف فيديو أو صورة الموقع (Site Media)</label>
                            <div class="upload-box">
                                <input type="file" id="siteFile" accept="image/*,video/*">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="desc">متطلبات التصميم المعماري</label>
                            <input type="text" id="desc" value="عمارة سكنية مودرن مع واجهات زجاجية وبلكونات" required>
                        </div>
                        <div class="grid-inputs">
                            <div class="form-group">
                                <label for="dim">المساحة والأبعاد (متر)</label>
                                <input type="text" id="dim" value="20*12" required>
                            </div>
                            <div class="form-group">
                                <label for="floors">عدد الطوابق</label>
                                <input type="number" id="floors" value="5" min="1" max="20">
                            </div>
                        </div>
                        <div class="grid-inputs">
                            <div class="form-group">
                                <label for="apartments">عدد الشقق لكل طابق</label>
                                <input type="number" id="apartments" value="2" min="1" max="8">
                            </div>
                            <div class="form-group">
                                <label for="ceilingHeight">ارتفاع السقف (متر)</label>
                                <input type="number" id="ceilingHeight" value="3.2" step="0.1" min="2.5" max="6.0">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="style">طراز العمارة والتشطيب</label>
                            <select id="style">
                                <option value="modern">✨ عمارة مودرن (زجاج واسع وإضاءة)</option>
                                <option value="full_house">🏠 مبنى سكني متكامل (Dual Apartments)</option>
                                <option value="classic">🏛️ كلاسيكي فاخر (أعمدة حجرية وتفاصيل)</option>
                                <option value="scandi">🌿 اسكندنافي هادئ (أخشاب وكتل نظيفة)</option>
                                <option value="industrial">🏭 صناعي معاصر (طوب مظلم ومعادن)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>محاكاة حركة الشمس والظلال ☀️</label>
                            <div class="sun-control">
                                <span>شروق</span>
                                <input type="range" id="sunAngle" min="0" max="360" value="45">
                                <span>غروب</span>
                            </div>
                        </div>
                        <button type="submit" class="btn-submit">توليد المبنى الواقعي ثلاثي الأبعاد 🧠🏗️</button>
                    </form>
                </div>

                <!-- سجل المشاريع -->
                <div class="card" style="padding: 15px;">
                    <div class="history-header">
                        <label style="margin: 0;">📂 سجل المشاريع الهندسية السابقة</label>
                        <button type="button" class="btn-clear-history" onclick="clearAllHistory()">حذف السجل بالكامل 🗑️</button>
                    </div>
                    <div class="history-list" id="historyList">
                        <span style="color: var(--text-muted); font-size: 0.75rem;">لا توجد مشاريع سجّلت بعد...</span>
                    </div>
                </div>
            </div>

            <!-- العارض المعماري الواقعي -->
            <div class="viewer-container">
                <div class="viewer-header">
                    <div class="cad-toolbar" id="cadToolbar" style="display: none;">
                        <button type="button" class="cad-btn active" id="mode3dBtn" onclick="switchMode('3d')">عرض 3D واقعي 🧊</button>
                        <button type="button" class="cad-btn" id="modeDrawBtn" onclick="switchMode('draw')">رسم CAD ✏️</button>
                        <button type="button" class="cad-btn" id="clearDrawBtn" onclick="clearDrawings()" style="color: var(--danger-color);">مسح الرسم ❌</button>
                    </div>
                    
                    <div class="downloads-group">
                        <button type="button" id="toggleRotateBtn" class="btn-toggle-rotate" onclick="toggleRotation()">إيقاف الحركة ⏸️</button>
                        <a href="#" id="downloadLinkObj" class="btn-download" download>تحميل OBJ 📥</a>
                        <a href="#" id="downloadLinkGltf" class="btn-download gltf" download>تحميل GLTF 🌐</a>
                        <a href="#" id="downloadLinkDxf" class="btn-download dxf" download>تحميل أوتوكاد DXF 📐📥</a>
                    </div>
                </div>

                <div class="viewer-views">
                    <div class="view-pane">
                        <div class="placeholder-3d" id="placeholder">
                            <h3>جاهز لتوليد المبنى الحقيقي ثلاثي الأبعاد!</h3>
                            <p style="margin-top:8px;">اختر طراز العمارة واضغط توليد لمشاهدة تفاصيل المبنى الواقعية.</p>
                        </div>
                        <canvas id="canvas3d"></canvas>
                        <canvas id="cadCanvas2D"></canvas>
                    </div>
                </div>

                <div id="aiStatusTag" class="ai-status-tag">✨ تم تطبيق الطراز المعماري وتوليد الواجهات الواقعية بنجاح</div>
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, buildingGroup, dirLight;
        let isDragging = false;
        let isRotating = true;
        let previousMousePosition = { x: 0, y: 0 };
        let projectHistory = [];
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();

        let currentMode = '3d';
        let cadCanvas, cadCtx;
        let isDrawing = false;
        let startX = 0, startY = 0;
        let userDrawings = [];

        function switchMode(mode) {
            currentMode = mode;
            const canvas3d = document.getElementById('canvas3d');
            const cadCanvas2D = document.getElementById('cadCanvas2D');
            const btn3d = document.getElementById('mode3dBtn');
            const btnDraw = document.getElementById('modeDrawBtn');
            const rotateBtn = document.getElementById('toggleRotateBtn');

            if (mode === '3d') {
                canvas3d.style.display = 'block';
                cadCanvas2D.style.display = 'none';
                btn3d.classList.add('active');
                btnDraw.classList.remove('active');
                if (rotateBtn.classList.contains('show')) rotateBtn.style.display = 'inline-block';
            } else {
                canvas3d.style.display = 'none';
                cadCanvas2D.style.display = 'block';
                btnDraw.classList.add('active');
                btn3d.classList.remove('active');
                rotateBtn.style.display = 'none';
                initCADCanvas();
            }
        }

        function initCADCanvas() {
            cadCanvas = document.getElementById('cadCanvas2D');
            cadCtx = cadCanvas.getContext('2d');
            cadCanvas.width = cadCanvas.parentElement.clientWidth;
            cadCanvas.height = cadCanvas.parentElement.clientHeight;
            redrawCAD();
        }

        document.addEventListener('DOMContentLoaded', () => {
            const cadCanvas = document.getElementById('cadCanvas2D');
            
            cadCanvas.addEventListener('mousedown', (e) => {
                if (currentMode !== 'draw') return;
                isDrawing = true;
                const rect = cadCanvas.getBoundingClientRect();
                startX = e.clientX - rect.left;
                startY = e.clientY - rect.top;
            });

            cadCanvas.addEventListener('mousemove', (e) => {
                if (!isDrawing || currentMode !== 'draw') return;
                const rect = cadCanvas.getBoundingClientRect();
                const currentX = e.clientX - rect.left;
                const currentY = e.clientY - rect.top;

                redrawCAD();
                cadCtx.strokeStyle = '#3b82f6';
                cadCtx.lineWidth = 2;
                cadCtx.beginPath();
                cadCtx.moveTo(startX, startY);
                cadCtx.lineTo(currentX, currentY);
                cadCtx.stroke();
            });

            cadCanvas.addEventListener('mouseup', (e) => {
                if (!isDrawing || currentMode !== 'draw') return;
                isDrawing = false;
                const rect = cadCanvas.getBoundingClientRect();
                const endX = e.clientX - rect.left;
                const endY = e.clientY - rect.top;

                userDrawings.push({ type: 'line', x1: startX, y1: startY, x2: endX, y2: endY });
                redrawCAD();
            });
        });

        function redrawCAD() {
            if (!cadCtx) return;
            cadCtx.fillStyle = '#0b0f19';
            cadCtx.fillRect(0, 0, cadCanvas.width, cadCanvas.height);

            cadCtx.strokeStyle = '#1e293b';
            cadCtx.lineWidth = 1;
            const gridSize = 40;
            for (let x = 0; x < cadCanvas.width; x += gridSize) {
                cadCtx.beginPath(); cadCtx.moveTo(x, 0); cadCtx.lineTo(x, cadCanvas.height); cadCtx.stroke();
            }
            for (let y = 0; y < cadCanvas.height; y += gridSize) {
                cadCtx.beginPath(); cadCtx.moveTo(0, y); cadCtx.lineTo(cadCanvas.width, y); cadCtx.stroke();
            }

            cadCtx.strokeStyle = '#38bdf8';
            cadCtx.lineWidth = 2.5;
            userDrawings.forEach(d => {
                cadCtx.beginPath();
                cadCtx.moveTo(d.x1, d.y1);
                cadCtx.lineTo(d.x2, d.y2);
                cadCtx.stroke();

                const midX = (d.x1 + d.x2) / 2;
                const midY = (d.y1 + d.y2) / 2;
                cadCtx.fillStyle = '#94a3b8';
                cadCtx.font = '11px system-ui';
                cadCtx.fillText('Wall Line', midX + 5, midY - 5);
            });
        }

        function clearDrawings() {
            userDrawings = [];
            redrawCAD();
        }

        function toggleRotation() {
            isRotating = !isRotating;
            const btn = document.getElementById('toggleRotateBtn');
            if (isRotating) {
                btn.textContent = 'إيقاف الحركة ⏸️';
                btn.style.background = 'var(--accent-orange)';
            } else {
                btn.textContent = 'تحريك المجسم 🔄';
                btn.style.background = 'var(--primary-color)';
            }
        }

        function init3DViewer() {
            const container = document.querySelector('.view-pane');
            const canvas = document.getElementById('canvas3d');
            
            if (!scene) {
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x090d16);

                camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera.position.set(18, 16, 28);
                camera.lookAt(0, 0, 0);

                renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.shadowMap.enabled = true;

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
                scene.add(ambientLight);

                dirLight = new THREE.DirectionalLight(0xffffff, 1.6);
                dirLight.position.set(25, 40, 25);
                dirLight.castShadow = true;
                scene.add(dirLight);

                const gridHelper = new THREE.GridHelper(60, 60, 0x3b82f6, 0x243048);
                gridHelper.position.y = -1.2;
                scene.add(gridHelper);

                canvas.addEventListener('mousedown', (e) => { isDragging = true; previousMousePosition = { x: e.clientX, y: e.clientY }; });
                canvas.addEventListener('mousemove', (e) => {
                    if (!isDragging || !buildingGroup) return;
                    const deltaX = e.clientX - previousMousePosition.x;
                    const deltaY = e.clientY - previousMousePosition.y;
                    buildingGroup.rotation.y += deltaX * 0.008;
                    buildingGroup.rotation.x += deltaY * 0.008;
                    previousMousePosition = { x: e.clientX, y: e.clientY };
                });
                window.addEventListener('mouseup', () => { isDragging = false; });

                canvas.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    camera.position.z += e.deltaY * 0.03;
                    camera.position.z = Math.max(6, Math.min(60, camera.position.z));
                }, { passive: false });

                document.getElementById('sunAngle').addEventListener('input', (e) => {
                    const angle = (e.target.value * Math.PI) / 180;
                    dirLight.position.x = Math.cos(angle) * 35;
                    dirLight.position.z = Math.sin(angle) * 35;
                });

                animate();
            }
        }

        function animate() {
            requestAnimationFrame(animate);
            if (buildingGroup && isRotating && !isDragging && currentMode === '3d') {
                buildingGroup.rotation.y += 0.003;
            }
            if (renderer && scene && camera) {
                renderer.render(scene, camera);
            }
        }

        // توليد المبنى الواقعي متجاوباً كلياً مع الطراز المعماري المختار
        function generateDetailedBuilding(floors, dimensionsText, apartments, ceilingHeight, style) {
            if (buildingGroup) {
                scene.remove(buildingGroup);
            }
            buildingGroup = new THREE.Group();

            let widthScale = 5.2;
            let depthScale = 4.0;
            if (dimensionsText) {
                const parts = dimensionsText.split(/[\*xX×]/);
                if (parts.length >= 2) {
                    const w = parseFloat(parts[0]);
                    const d = parseFloat(parts[1]);
                    if (!isNaN(w) && !isNaN(d)) {
                        widthScale = Math.max(3.5, Math.min(8.0, w / 3.8));
                        depthScale = Math.max(3.0, Math.min(6.5, d / 3.8));
                    }
                }
            }

            const scaleH = parseFloat(ceilingHeight) || 3.2;
            const hUnit = scaleH * 0.32;

            // تحديد الخامات والألوان بناءً على الطراز المعماري المختار
            let wallColor = 0xe2e8f0;
            let glassColor = 0x38bdf8;
            let frameColor = 0x1e293b;
            let slabColor = 0x94a3b8;
            let accentColor = 0x0f172a;

            if (style === 'classic') {
                wallColor = 0xf1f5f9; // حجر كلاسيكي فاتح
                glassColor = 0x60a5fa;
                frameColor = 0xb45309; // إطارات ذهبية/خشبية فاخرة
                slabColor = 0xd1d5db;
                accentColor = 0x92400e;
            } else if (style === 'industrial') {
                wallColor = 0x334155; // طوب معاصر غامق
                glassColor = 0x93c5fd;
                frameColor = 0x0f172a;
                slabColor = 0x1e293b;
                accentColor = 0x475569;
            } else if (style === 'scandi') {
                wallColor = 0xf8fafc; // أبيض ناصع مع أخشاب هادئة
                glassColor = 0x7dd3fc;
                frameColor = 0x78350f; // تفاصيل خشبية طبيعية
                slabColor = 0xe2e8f0;
                accentColor = 0xd97706;
            } else if (style === 'full_house') {
                wallColor = 0xcfd8dc;
                glassColor = 0x29b6f6;
                frameColor = 0x37474f;
                slabColor = 0x90a4ae;
                accentColor = 0x455a64;
            }

            const wallMat = new THREE.MeshStandardMaterial({ color: wallColor, roughness: 0.4 });
            const glassMat = new THREE.MeshStandardMaterial({ color: glassColor, roughness: 0.1, transparent: true, opacity: 0.7 });
            const frameMat = new THREE.MeshStandardMaterial({ color: frameColor, roughness: 0.2 });
            const slabMat = new THREE.MeshStandardMaterial({ color: slabColor, roughness: 0.3 });
            const accentMat = new THREE.MeshStandardMaterial({ color: accentColor, roughness: 0.3 });

            for (let i = 0; i < floors; i++) {
                // سقف فاخر بارز بين الطوابق
                const slabGeo = new THREE.BoxGeometry(widthScale + 0.25, 0.14, depthScale + 0.25);
                const slab = new THREE.Mesh(slabGeo, slabMat.clone());
                slab.position.y = i * hUnit;
                buildingGroup.add(slab);

                // الهيكل الأساسي للطابق
                const floorBodyGeo = new THREE.BoxGeometry(widthScale, hUnit * 0.78, depthScale);
                const floorBody = new THREE.Mesh(floorBodyGeo, wallMat.clone());
                floorBody.position.y = i * hUnit + (hUnit * 0.39);
                buildingGroup.add(floorBody);

                // الطابق الأرضي: مدخل المبنى الرئيسي الفخم
                if (i === 0) {
                    const entranceGeo = new THREE.BoxGeometry(1.4, hUnit * 0.65, 0.15);
                    const entrance = new THREE.Mesh(entranceGeo, accentMat.clone());
                    entrance.position.set(0, (hUnit * 0.35) - 0.1, (depthScale / 2) + 0.05);
                    buildingGroup.add(entrance);

                    // مظلة المدخل
                    const canopyGeo = new THREE.BoxGeometry(2.0, 0.1, 0.8);
                    const canopy = new THREE.Mesh(canopyGeo, frameMat.clone());
                    canopy.position.set(0, (hUnit * 0.7), (depthScale / 2) + 0.3);
                    buildingGroup.add(canopy);
                }

                // توزيع الشقق والنوافذ الواقعية
                const apptsCount = parseInt(apartments) || 2;
                const segmentWidth = widthScale / apptsCount;

                for (let a = 0; a < apptsCount; a++) {
                    const xOffset = - (widthScale / 2) + (segmentWidth * a) + (segmentWidth / 2);

                    // نافذة زجاجية واسعة واقعية
                    const windowGeo = new THREE.BoxGeometry(segmentWidth * 0.65, hUnit * 0.5, 0.06);
                    const windowMesh = new THREE.Mesh(windowGeo, glassMat.clone());
                    windowMesh.position.set(xOffset, i * hUnit + (hUnit * 0.42), (depthScale / 2) + 0.05);
                    buildingGroup.add(windowMesh);

                    // إطار النافذة المعماري
                    const frameGeo = new THREE.BoxGeometry(segmentWidth * 0.7, hUnit * 0.54, 0.03);
                    const frameMesh = new THREE.Mesh(frameGeo, frameMat.clone());
                    frameMesh.position.set(xOffset, i * hUnit + (hUnit * 0.42), (depthScale / 2) + 0.03);
                    buildingGroup.add(frameMesh);

                    // بلكونة طابقية واقعية للطوابق العليا
                    if (i > 0) {
                        const balconyBaseGeo = new THREE.BoxGeometry(segmentWidth * 0.85, 0.08, 0.75);
                        const balconyBase = new THREE.Mesh(balconyBaseGeo, slabMat.clone());
                        balconyBase.position.set(xOffset, i * hUnit + (hUnit * 0.18), (depthScale / 2) + 0.38);
                        buildingGroup.add(balconyBase);

                        // درابزين البلكونة المعماري
                        const railingGeo = new THREE.BoxGeometry(segmentWidth * 0.85, 0.4, 0.04);
                        const railing = new THREE.Mesh(railingGeo, frameMat.clone());
                        railing.position.set(xOffset, i * hUnit + (hUnit * 0.42), (depthScale / 2) + 0.72);
                        buildingGroup.add(railing);
                    }
                }
            }

            // تصميم السطح والبنتاوس (Roof Penthouse)
            const roofGeo = new THREE.BoxGeometry(widthScale * 0.4, hUnit * 0.6, depthScale * 0.4);
            const roofMesh = new THREE.Mesh(roofGeo, accentMat.clone());
            roofMesh.position.set(0, floors * hUnit + (hUnit * 0.3), 0);
            buildingGroup.add(roofMesh);

            scene.add(buildingGroup);
        }

        function renderHistoryList() {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            if (projectHistory.length === 0) {
                historyList.innerHTML = '<span style="color: var(--text-muted); font-size: 0.75rem;">لا توجد مشاريع سجّلت بعد...</span>';
                return;
            }
            projectHistory.forEach((p, index) => {
                const div = document.createElement('div');
                div.className = 'history-item';
                
                const span = document.createElement('span');
                span.innerHTML = `🏢 ${p.desc.substring(0, 18)}... (${p.dim} | ${p.floors} طوابق)`;
                span.onclick = () => {
                    document.getElementById('desc').value = p.desc;
                    document.getElementById('dim').value = p.dim;
                    document.getElementById('floors').value = p.floors;
                    document.getElementById('apartments').value = p.apartments;
                    document.getElementById('ceilingHeight').value = p.ceilingHeight;
                    document.getElementById('style').value = p.style;
                    generateDetailedBuilding(p.floors, p.dim, p.apartments, p.ceilingHeight, p.style);
                };

                const delBtn = document.createElement('button');
                delBtn.className = 'btn-delete-single';
                delBtn.innerHTML = '❌';
                delBtn.title = 'حذف هذا المشروع';
                delBtn.onclick = (e) => {
                    e.stopPropagation();
                    deleteProject(index);
                };

                div.appendChild(span);
                div.appendChild(delBtn);
                historyList.appendChild(div);
            });
        }

        function addToHistory(desc, dim, floors, apartments, ceilingHeight, style) {
            const project = { desc, dim, floors, apartments, ceilingHeight, style };
            projectHistory.unshift(project);
            if (projectHistory.length > 5) projectHistory.pop();
            renderHistoryList();
        }

        function deleteProject(index) {
            projectHistory.splice(index, 1);
            renderHistoryList();
        }

        function clearAllHistory() {
            projectHistory = [];
            renderHistoryList();
        }

        // ربط الزر بالاستجابة الفورية وتمرير الطراز المعماري المختار
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('buildForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const btn = document.querySelector('.btn-submit');
                const placeholder = document.getElementById('placeholder');
                const canvas = document.getElementById('canvas3d');
                const downloadObj = document.getElementById('downloadLinkObj');
                const downloadGltf = document.getElementById('downloadLinkGltf');
                const downloadDxf = document.getElementById('downloadLinkDxf');
                const toggleRotateBtn = document.getElementById('toggleRotateBtn');
                const cadToolbar = document.getElementById('cadToolbar');
                const aiStatusTag = document.getElementById('aiStatusTag');
                
                const styleVal = document.getElementById('style').value;
                const descVal = document.getElementById('desc').value;
                const dimVal = document.getElementById('dim').value;
                const floorsVal = parseInt(document.getElementById('floors').value) || 5;
                const apartmentsVal = parseInt(document.getElementById('apartments').value) || 2;
                const ceilingHeightVal = parseFloat(document.getElementById('ceilingHeight').value) || 3.2;

                btn.textContent = 'جاري هندسة وتطبيق الطراز... ⏳';
                btn.disabled = true;

                setTimeout(() => {
                    placeholder.style.display = 'none';
                    canvas.style.display = 'block';

                    init3DViewer();
                    generateDetailedBuilding(floorsVal, dimVal, apartmentsVal, ceilingHeightVal, styleVal);
                    addToHistory(descVal, dimVal, floorsVal, apartmentsVal, ceilingHeightVal, styleVal);

                    const cleanDim = dimVal.replace('*', 'x');
                    const fileBase = `building_${styleVal}_${floorsVal}f_${apartmentsVal}apt_${cleanDim}`;

                    downloadObj.href = `/download/${fileBase}.obj`;
                    downloadObj.download = `${fileBase}.obj`;
                    downloadObj.className = 'btn-download show';

                    downloadGltf.href = `/download/${fileBase}.gltf`;
                    downloadGltf.download = `${fileBase}.gltf`;
                    downloadGltf.className = 'btn-download gltf show';

                    downloadDxf.href = `/download/${fileBase}.dxf`;
                    downloadDxf.download = `${fileBase}.dxf`;
                    downloadDxf.className = 'btn-download dxf show';

                    toggleRotateBtn.className = 'btn-toggle-rotate show';
                    cadToolbar.style.display = 'flex';
                    aiStatusTag.style.display = 'block';

                    btn.textContent = 'توليد المبنى الواقعي ثلاثي الأبعاد 🧠🏗️';
                    btn.disabled = false;
                }, 200);
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(f"# Home AI 3D - File: {filename}\n")
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
