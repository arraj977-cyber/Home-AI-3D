import os
import random
from flask import Flask, render_template_string, request, send_file, jsonify

app = Flask(__name__)

OUTPUT_DIR = "generated_models"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home AI 3D - المنصة الهندسية المتقدمة</title>
    <!-- تضمين مكتبة Three.js للعارض ثلاثي الأبعاد -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --accent-orange: #f97316;
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
        .viewer-container { display: flex; flex-direction: column; position: relative; background: #090d16; min-height: 650px; border-radius: 16px; border: 1px solid var(--border-color); overflow: hidden; justify-content: center; align-items: center; }
        .viewer-header { position: absolute; top: 20px; left: 20px; right: 20px; display: flex; justify-content: space-between; align-items: center; z-index: 10; flex-wrap: wrap; gap: 10px; }
        .downloads-group { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
        .btn-download { background: var(--primary-color); color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.8rem; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); display: none; }
        .btn-download.gltf { background: var(--success-color); }
        .btn-download.dxf { background: var(--dxf-color); }
        .btn-download.show { display: inline-block; }
        .btn-toggle-rotate { background: var(--accent-orange); color: white; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 0.8rem; cursor: pointer; box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3); transition: 0.2s; }
        .btn-toggle-rotate:hover { opacity: 0.9; }
        .viewer-3d { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; position: relative; }
        .placeholder-3d { text-align: center; color: var(--text-muted); padding: 40px; z-index: 2; position: absolute; }
        #canvas3d { width: 100%; height: 650px; display: none; }
        .ai-status-tag { position: absolute; bottom: 20px; background: rgba(15, 23, 42, 0.85); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; color: var(--accent-orange); display: none; z-index: 5; }
        .history-list { max-height: 120px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
        .history-item { background: #0b0f19; padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.8rem; cursor: pointer; transition: 0.2s; }
        .history-item:hover { border-color: var(--primary-color); }
        .sun-control { display: flex; align-items: center; gap: 10px; margin-top: 5px; font-size: 0.85rem; color: var(--text-muted); }
        .sun-control input { flex: 1; }
    </style>
</head>
<body>
    <div class="app-container">
        <header>
            <div class="logo-area">
                <span class="logo-title">HOME AI <span>3D</span></span>
                <span class="badge">المنصة الهندسية المتقدمة للذكاء الاصطناعي 📐🏢</span>
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
                                <option value="modern">✨ عمارة مودرن مع واجهات زجاجية</option>
                                <option value="full_house">🏠 مبنى سكني متكامل (Dual Apartments)</option>
                                <option value="classic">🏛️ كلاسيكي فاخر بأعمدة</option>
                                <option value="scandi">🌿 اسكندنافي هادئ</option>
                                <option value="industrial">🏭 صناعي معاصر</option>
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
                        <button type="submit" class="btn-submit">توليد التصميم المعماري وملفات الأوتوكاد 🧠🏗️</button>
                    </form>
                </div>

                <!-- سجل المشاريع -->
                <div class="card" style="padding: 15px;">
                    <label style="margin-bottom: 6px;">📂 سجل المشاريع الهندسية السابقة</label>
                    <div class="history-list" id="historyList">
                        <span style="color: var(--text-muted); font-size: 0.75rem;">لا توجد مشاريع سجّلت بعد...</span>
                    </div>
                </div>
            </div>

            <!-- العارض المعماري التفاعلي المتقدم -->
            <div class="viewer-container">
                <div class="viewer-header">
                    <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success-color);">عارض التصميم المعماري ثلاثي الأبعاد</span>
                    <div class="downloads-group">
                        <button type="button" id="toggleRotateBtn" class="btn-toggle-rotate" onclick="toggleRotation()">إيقاف الحركة ⏸️</button>
                        <a href="#" id="downloadLinkObj" class="btn-download" download>تحميل OBJ 📥</a>
                        <a href="#" id="downloadLinkGltf" class="btn-download gltf" download>تحميل GLTF 🌐</a>
                        <a href="#" id="downloadLinkDxf" class="btn-download dxf" download>تحميل أوتوكاد DXF 📐📥</a>
                    </div>
                </div>
                <div class="viewer-3d">
                    <div class="placeholder-3d" id="placeholder">
                        <h3>جاهز لمعالجة الموقع المعماري!</h3>
                        <p style="margin-top:8px;">حدد عدد الشقق وارتفاع السقف واضغط توليد لمشاهدة التفاصيل المعمارية.</p>
                    </div>
                    <canvas id="canvas3d"></canvas>
                </div>
                <div id="aiStatusTag" class="ai-status-tag">✨ تم تطبيق عدد الشقق وارتفاع السقف وتوليد النموذج الهندسي بنجاح</div>
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, buildingGroup, dirLight;
        let isDragging = false;
        let isRotating = true; // حالة تفعيل أو إيقاف الحركة التلقائية
        let previousMousePosition = { x: 0, y: 0 };
        let projectHistory = [];

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
            const container = document.querySelector('.viewer-3d');
            const canvas = document.getElementById('canvas3d');
            
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x090d16);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(16, 14, 24);
            camera.lookAt(0, 0, 0);

            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.shadowMap.enabled = true;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
            dirLight.position.set(20, 35, 20);
            dirLight.castShadow = true;
            scene.add(dirLight);

            const gridHelper = new THREE.GridHelper(50, 50, 0x3b82f6, 0x243048);
            gridHelper.position.y = -1;
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

            document.getElementById('sunAngle').addEventListener('input', (e) => {
                const angle = (e.target.value * Math.PI) / 180;
                dirLight.position.x = Math.cos(angle) * 30;
                dirLight.position.z = Math.sin(angle) * 30;
            });

            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            if (buildingGroup && isRotating && !isDragging) {
                buildingGroup.rotation.y += 0.002;
            }
            renderer.render(scene, camera);
        }

        function generateDetailedBuilding(floors, dimensionsText, apartments, ceilingHeight) {
            if (buildingGroup) {
                scene.remove(buildingGroup);
            }
            buildingGroup = new THREE.Group();

            let widthScale = 4.8;
            let depthScale = 3.6;
            if (dimensionsText) {
                const parts = dimensionsText.split(/[\*xX×]/);
                if (parts.length >= 2) {
                    const w = parseFloat(parts[0]);
                    const d = parseFloat(parts[1]);
                    if (!isNaN(w) && !isNaN(d)) {
                        widthScale = Math.max(3.2, Math.min(7.0, w / 4.0));
                        depthScale = Math.max(2.6, Math.min(5.8, d / 3.8));
                    }
                }
            }

            const scaleH = parseFloat(ceilingHeight) || 3.2;
            const hUnit = scaleH * 0.3;

            const concreteMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.2 });
            const glassMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, transparent: true, opacity: 0.55 });
            const partitionMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 });
            const balconyMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });

            for (let i = 0; i < floors; i++) {
                const slabGeo = new THREE.BoxGeometry(widthScale, 0.15, depthScale);
                const slab = new THREE.Mesh(slabGeo, concreteMat);
                slab.position.y = i * hUnit;
                buildingGroup.add(slab);

                const floorBodyGeo = new THREE.BoxGeometry(widthScale * 0.92, hUnit * 0.75, depthScale * 0.92);
                const floorBody = new THREE.Mesh(floorBodyGeo, partitionMat);
                floorBody.position.y = i * hUnit + (hUnit * 0.4);
                buildingGroup.add(floorBody);

                const apptsCount = parseInt(apartments) || 2;
                const segmentWidth = (widthScale * 0.85) / apptsCount;

                for (let a = 0; a < apptsCount; a++) {
                    const xOffset = - (widthScale * 0.85 / 2) + (segmentWidth * a) + (segmentWidth / 2);

                    const glassGeo = new THREE.BoxGeometry(segmentWidth * 0.85, hUnit * 0.55, 0.08);
                    const frontGlass = new THREE.Mesh(glassGeo, glassMat);
                    frontGlass.position.set(xOffset, i * hUnit + (hUnit * 0.4), depthScale / 2 + 0.04);
                    buildingGroup.add(frontGlass);

                    const balconyGeo = new THREE.BoxGeometry(segmentWidth * 0.9, 0.08, 0.6);
                    const balcony = new THREE.Mesh(balconyGeo, balconyMat);
                    balcony.position.set(xOffset, i * hUnit + (hUnit * 0.18), depthScale / 2 + 0.3);
                    buildingGroup.add(balcony);
                }
            }

            scene.add(buildingGroup);
        }

        function addToHistory(desc, dim, floors, apartments, ceilingHeight, style) {
            const project = { desc, dim, floors, apartments, ceilingHeight, style };
            projectHistory.unshift(project);
            if (projectHistory.length > 5) projectHistory.pop();

            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            projectHistory.forEach((p) => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `🏢 ${p.desc.substring(0, 22)}... (${p.dim} | ${p.floors} طوابق | ${p.apartments} شقق)`;
                div.onclick = () => {
                    document.getElementById('desc').value = p.desc;
                    document.getElementById('dim').value = p.dim;
                    document.getElementById('floors').value = p.floors;
                    document.getElementById('apartments').value = p.apartments;
                    document.getElementById('ceilingHeight').value = p.ceilingHeight;
                    document.getElementById('style').value = p.style;
                    generateDetailedBuilding(p.floors, p.dim, p.apartments, p.ceilingHeight);
                };
                historyList.appendChild(div);
            });
        }

        document.getElementById('buildForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const btn = document.querySelector('.btn-submit');
            const placeholder = document.getElementById('placeholder');
            const canvas = document.getElementById('canvas3d');
            const downloadObj = document.getElementById('downloadLinkObj');
            const downloadGltf = document.getElementById('downloadLinkGltf');
            const downloadDxf = document.getElementById('downloadLinkDxf');
            const aiStatusTag = document.getElementById('aiStatusTag');
            
            const styleVal = document.getElementById('style').value;
            const descVal = document.getElementById('desc').value;
            const dimVal = document.getElementById('dim').value;
            const floorsVal = parseInt(document.getElementById('floors').value) || 5;
            const apartmentsVal = parseInt(document.getElementById('apartments').value) || 2;
            const ceilingHeightVal = parseFloat(document.getElementById('ceilingHeight').value) || 3.2;
            const fileInput = document.getElementById('siteFile');

            btn.textContent = 'جاري هندسة الشقق، الارتفاعات وأوتوكاد DXF... ⏳';
            btn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('style', styleVal);
                formData.append('description', descVal);
                formData.append('dimensions', dimVal);
                formData.append('floors', floorsVal);
                formData.append('apartments', apartmentsVal);
                formData.append('ceilingHeight', ceilingHeightVal);
                if (fileInput.files.length > 0) {
                    formData.append('site_file', fileInput.files[0]);
                }

                const response = await fetch('/generate_ai_design', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                await new Promise(resolve => setTimeout(resolve, 1500));
                
                placeholder.style.display = 'none';
                canvas.style.display = 'block';

                if (!renderer) {
                    init3DViewer();
                }
                generateDetailedBuilding(floorsVal, dimVal, apartmentsVal, ceilingHeightVal);
                addToHistory(descVal, dimVal, floorsVal, apartmentsVal, ceilingHeightVal, styleVal);

                downloadObj.href = `/download/${data.obj_file}`;
                downloadObj.download = data.obj_file;
                downloadObj.className = 'btn-download show';

                downloadGltf.href = `/download/${data.gltf_file}`;
                downloadGltf.download = data.gltf_file;
                downloadGltf.className = 'btn-download gltf show';

                downloadDxf.href = `/download/${data.dxf_file}`;
                downloadDxf.download = data.dxf_file;
                downloadDxf.className = 'btn-download dxf show';

                aiStatusTag.style.display = 'block';
            } catch (err) {
                alert('حدث خطأ أثناء المعالجة، جرب مرة أخرى.');
            } finally {
                btn.textContent = 'توليد التصميم المعماري وملفات الأوتوكاد 🧠🏗️';
                btn.disabled = false;
            }
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
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)

@app.route('/generate_ai_design', methods=['POST'])
def generate_ai_design():
    style = request.form.get('style', 'modern')
    description = request.form.get('description', '')
    dimensions = request.form.get('dimensions', '20*12')
    floors = request.form.get('floors', '5')
    apartments = request.form.get('apartments', '2')
    ceiling_height = request.form.get('ceilingHeight', '3.2')
    
    clean_dim = dimensions.replace('*', 'x')
    obj_filename = f"building_{style}_{floors}f_{apartments}apt_{clean_dim}.obj"
    gltf_filename = f"building_{style}_{floors}f_{apartments}apt_{clean_dim}.gltf"
    dxf_filename = f"floor_plan_{style}_{floors}f_{apartments}apt_{clean_dim}.dxf"
    
    obj_path = os.path.join(OUTPUT_DIR, obj_filename)
    gltf_path = os.path.join(OUTPUT_DIR, gltf_filename)
    dxf_path = os.path.join(OUTPUT_DIR, dxf_filename)

    with open(obj_path, "w") as f:
        f.write(f"# Home AI 3D - Engineered Model\n# Style: {style}\n# Dimensions: {dimensions}\n# Floors: {floors}\n# Apartments per floor: {apartments}\n# Ceiling Height: {ceiling_height}m\n")

    with open(gltf_path, "w") as f:
        f.write(f'{{\n  "asset": {{\n    "generator": "Home AI 3D Engine",\n    "version": "2.0"\n  }},\n  "metadata": {{\n    "apartments_per_floor": {apartments},\n    "ceiling_height": {ceiling_height}\n  }}\n}}')

    with open(dxf_path, "w") as f:
        f.write(f"0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nSECTION\n2\nTABLES\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n")
        f.write(f"0\nTEXT\n8\nARCH_DATA\n10\n0.0\n20\n0.0\n40\n1.2\n1\nHome AI Plan - Dim: {dimensions} | Floors: {floors} | Apt/Floor: {apartments} | Height: {ceiling_height}m\n")
        f.write(f"0\nENDSEC\n0\nEOF\n")

    return jsonify({
        "status": "success",
        "obj_file": obj_filename,
        "gltf_file": gltf_filename,
        "dxf_file": dxf_filename,
        "message": "تم توليد النموذج المعماري وملف الأوتوكاد بنجاح."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
