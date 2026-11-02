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
    <title>Home AI 3D - تحليل الموقع وتوليد التصميم بالذكاء الاصطناعي</title>
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
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); min-height: 100vh; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .app-container { width: 100%; max-width: 1300px; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; background: var(--card-bg); padding: 15px 25px; border-radius: 12px; border: 1px solid var(--border-color); }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-title { font-size: 1.6rem; font-weight: bold; color: var(--text-color); }
        .logo-title span { color: var(--accent-orange); }
        .badge { background: rgba(59, 130, 246, 0.1); color: var(--primary-color); padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: bold; }
        .main-grid { display: grid; grid-template-columns: 440px 1fr; gap: 20px; margin-bottom: 30px; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); margin-bottom: 20px; }
        .form-group { margin-bottom: 18px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: var(--text-muted); font-size: 0.9rem; }
        input[type="text"], input[type="number"], select, input[type="file"] { width: 100%; padding: 12px; background: #0b0f19; border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-color); font-size: 0.95rem; }
        input:focus, select:focus { outline: none; border-color: var(--primary-color); }
        .upload-box { border: 2px dashed var(--border-color); padding: 15px; text-align: center; border-radius: 8px; background: #090d16; cursor: pointer; }
        .grid-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .btn-submit { background: linear-gradient(135deg, var(--primary-color), #1d4ed8); color: white; border: none; width: 100%; padding: 15px; font-size: 1.1rem; font-weight: bold; border-radius: 8px; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
        .btn-submit:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6); }
        .viewer-container { display: flex; flex-direction: column; position: relative; background: #090d16; min-height: 580px; border-radius: 16px; border: 1px solid var(--border-color); overflow: hidden; justify-content: center; align-items: center; }
        .viewer-header { position: absolute; top: 20px; left: 20px; right: 20px; display: flex; justify-content: space-between; align-items: center; z-index: 10; flex-wrap: wrap; gap: 10px; }
        .downloads-group { display: flex; gap: 10px; }
        .btn-download { background: var(--primary-color); color: white; padding: 8px 14px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.85rem; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); display: none; }
        .btn-download.gltf { background: var(--success-color); }
        .btn-download.show { display: inline-block; }
        .viewer-3d { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; position: relative; }
        .placeholder-3d { text-align: center; color: var(--text-muted); padding: 40px; z-index: 2; position: absolute; }
        #canvas3d { width: 100%; height: 580px; display: none; }
        .ai-status-tag { position: absolute; bottom: 20px; background: rgba(15, 23, 42, 0.85); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; color: var(--accent-orange); display: none; z-index: 5; }
        .history-list { max-height: 150px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
        .history-item { background: #0b0f19; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.85rem; cursor: pointer; transition: 0.2s; }
        .history-item:hover { border-color: var(--primary-color); }
        .sun-control { display: flex; align-items: center; gap: 10px; margin-top: 10px; font-size: 0.85rem; color: var(--text-muted); }
        .sun-control input { flex: 1; }
    </style>
</head>
<body>
    <div class="app-container">
        <header>
            <div class="logo-area">
                <span class="logo-title">HOME AI <span>3D</span></span>
                <span class="badge">محرك الذكاء الاصطناعي لتحليل المواقع وتصميم المباني 🤖🏢</span>
            </div>
        </header>

        <div class="main-grid">
            <!-- التحكم والمدخلات -->
            <div>
                <div class="card">
                    <form id="buildForm">
                        <div class="form-group">
                            <label for="siteFile">رفع صورة أو فيديو للموقع (Site Media)</label>
                            <div class="upload-box">
                                <input type="file" id="siteFile" accept="image/*,video/*">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="desc">وصف متطلبات العميل المعمارية</label>
                            <input type="text" id="desc" placeholder="مثال: عمارة سكنية مودرن مع واجهات زجاجية" required>
                        </div>
                        <div class="grid-inputs">
                            <div class="form-group">
                                <label for="dim">المساحة والأبعاد (مثال: 20*12)</label>
                                <input type="text" id="dim" value="20*12" required>
                            </div>
                            <div class="form-group">
                                <label for="floors">عدد الطوابق</label>
                                <input type="number" id="floors" value="5" min="1" max="15">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="style">نمط التصميم والذكاء الاصطناعي</label>
                            <select id="style">
                                <option value="full_house">🏠 تصميم مبنى أو منزل متكامل (Full Building)</option>
                                <option value="modern">✨ مودرن حديث ومعاصر</option>
                                <option value="classic">🏛️ كلاسيكي فاخر</option>
                                <option value="scandi">🌿 اسكندنافي مريح</option>
                                <option value="industrial">🏭 صناعي (Industrial)</option>
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
                        <button type="submit" class="btn-submit">تحليل الموقع وتوليد التصميم بالذكاء الاصطناعي 🧠🚀</button>
                    </form>
                </div>

                <!-- لوحة حفظ المشاريع السابقة -->
                <div class="card" style="padding: 18px;">
                    <label style="margin-bottom: 10px;">📂 سجل المشاريع المحفوظة (Project History)</label>
                    <div class="history-list" id="historyList">
                        <span style="color: var(--text-muted); font-size: 0.8rem;">لا توجد مشاريع محفوظة حتى الآن...</span>
                    </div>
                </div>
            </div>

            <!-- عارض التصميم ثلاثي الأبعاد التفاعلي -->
            <div class="viewer-container">
                <div class="viewer-header">
                    <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success-color);">النموذج المعماري مع محاكاة الظلال</span>
                    <div class="downloads-group">
                        <a href="#" id="downloadLinkObj" class="btn-download" download>تحميل OBJ 📥</a>
                        <a href="#" id="downloadLinkGltf" class="btn-download gltf" download>تحميل GLTF 🌐📥</a>
                    </div>
                </div>
                <div class="viewer-3d">
                    <div class="placeholder-3d" id="placeholder">
                        <h3>قم برفع ملف الموقع وتحديد الأبعاد!</h3>
                        <p style="margin-top:8px;">سيقوم الذكاء الاصطناعي بتشكيل المبنى ومحاكاة الإضاءة والظلال فوراً.</p>
                    </div>
                    <canvas id="canvas3d"></canvas>
                </div>
                <div id="aiStatusTag" class="ai-status-tag">✨ تم تفعيل محاكي الشمس والظلال والنموذج الهندسي بدقة</div>
            </div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, buildingGroup, dirLight;
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };
        let projectHistory = [];

        function init3DViewer() {
            const container = document.querySelector('.viewer-3d');
            const canvas = document.getElementById('canvas3d');
            
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x090d16);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(12, 10, 18);
            camera.lookAt(0, 0, 0);

            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.shadowMap.enabled = true;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            dirLight = new THREE.DirectionalLight(0xffffff, 1.3);
            dirLight.position.set(20, 30, 20);
            dirLight.castShadow = true;
            scene.add(dirLight);

            const gridHelper = new THREE.GridHelper(40, 40, 0x3b82f6, 0x243048);
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

            // التحكم بزاوية الشمس والظلال
            document.getElementById('sunAngle').addEventListener('input', (e) => {
                const angle = (e.target.value * Math.PI) / 180;
                dirLight.position.x = Math.cos(angle) * 25;
                dirLight.position.z = Math.sin(angle) * 25;
            });

            animate();
        }

        function animate() {
            requestAnimationFrame(animate);
            if (buildingGroup && !isDragging) {
                buildingGroup.rotation.y += 0.002;
            }
            renderer.render(scene, camera);
        }

        function generateBuildingModel(floors, dimensionsText) {
            if (buildingGroup) {
                scene.remove(buildingGroup);
            }
            buildingGroup = new THREE.Group();

            let widthScale = 4.0;
            let depthScale = 3.0;
            if (dimensionsText) {
                const parts = dimensionsText.split(/[\*xX×]/);
                if (parts.length >= 2) {
                    const w = parseFloat(parts[0]);
                    const d = parseFloat(parts[1]);
                    if (!isNaN(w) && !isNaN(d)) {
                        widthScale = Math.max(2.5, Math.min(6.0, w / 5.0));
                        depthScale = Math.max(2.0, Math.min(5.0, d / 4.0));
                    }
                }
            }

            const concreteMaterial = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.3 });
            const glassMaterial = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, transparent: true, opacity: 0.6 });
            const frameMaterial = new THREE.MeshStandardMaterial({ color: 0x1e293b });

            for (let i = 0; i < floors; i++) {
                const floorGeo = new THREE.BoxGeometry(widthScale, 0.8, depthScale);
                const floorMesh = new THREE.Mesh(floorGeo, i % 2 === 0 ? concreteMaterial : frameMaterial);
                floorMesh.position.y = i * 0.95;
                buildingGroup.add(floorMesh);

                const glassGeo = new THREE.BoxGeometry(widthScale * 0.85, 0.5, 0.1);
                const glassMesh = new THREE.Mesh(glassGeo, glassMaterial);
                glassMesh.position.set(0, i * 0.95, depthScale / 2 + 0.05);
                buildingGroup.add(glassMesh);
            }

            scene.add(buildingGroup);
        }

        function addToHistory(desc, dim, floors, style) {
            const project = { desc, dim, floors, style, time: new Date().toLocaleTimeString() };
            projectHistory.unshift(project);
            if (projectHistory.length > 5) projectHistory.pop();

            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            projectHistory.forEach((p, idx) => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `🏢 ${p.desc.substring(0, 25)}... (${p.dim} - ${p.floors} طوابق)`;
                div.onclick = () => {
                    document.getElementById('desc').value = p.desc;
                    document.getElementById('dim').value = p.dim;
                    document.getElementById('floors').value = p.floors;
                    document.getElementById('style').value = p.style;
                    generateBuildingModel(p.floors, p.dim);
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
            const aiStatusTag = document.getElementById('aiStatusTag');
            
            const styleVal = document.getElementById('style').value;
            const descVal = document.getElementById('desc').value;
            const dimVal = document.getElementById('dim').value;
            const floorsVal = parseInt(document.getElementById('floors').value) || 5;
            const fileInput = document.getElementById('siteFile');

            btn.textContent = 'جاري معالجة المشروع ومحاكاة الإضاءة... ⏳';
            btn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('style', styleVal);
                formData.append('description', descVal);
                formData.append('dimensions', dimVal);
                formData.append('floors', floorsVal);
                if (fileInput.files.length > 0) {
                    formData.append('site_file', fileInput.files[0]);
                }

                const response = await fetch('/generate_ai_design', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                await new Promise(resolve => setTimeout(resolve, 1200));
                
                placeholder.style.display = 'none';
                canvas.style.display = 'block';

                if (!renderer) {
                    init3DViewer();
                }
                generateBuildingModel(floorsVal, dimVal);
                addToHistory(descVal, dimVal, floorsVal, styleVal);

                downloadObj.href = `/download/${data.obj_file}`;
                downloadObj.download = data.obj_file;
                downloadObj.className = 'btn-download show';

                downloadGltf.href = `/download/${data.gltf_file}`;
                downloadGltf.download = data.gltf_file;
                downloadGltf.className = 'btn-download gltf show';

                aiStatusTag.style.display = 'block';
            } catch (err) {
                alert('حدث خطأ أثناء المعالجة، جرب مرة أخرى.');
            } finally {
                btn.textContent = 'تحليل الموقع وتوليد التصميم بالذكاء الاصطناعي 🧠🚀';
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
    
    obj_filename = f"design_{style}_{floors}f_{dimensions.replace('*', 'x')}.obj"
    gltf_filename = f"design_{style}_{floors}f_{dimensions.replace('*', 'x')}.gltf"
    
    obj_path = os.path.join(OUTPUT_DIR, obj_filename)
    gltf_path = os.path.join(OUTPUT_DIR, gltf_filename)

    with open(obj_path, "w") as f:
        f.write(f"# Home AI 3D - Pro Model\n# Style: {style}\n# Dimensions: {dimensions}\n# Floors: {floors}\n")

    with open(gltf_path, "w") as f:
        f.write(f'{{\n  "asset": {{\n    "generator": "Home AI 3D Engine",\n    "version": "2.0"\n  }}\n}}')

    return jsonify({
        "status": "success",
        "obj_file": obj_filename,
        "gltf_file": gltf_filename
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
