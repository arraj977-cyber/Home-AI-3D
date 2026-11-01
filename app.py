from flask import Flask, render_template_string, request, jsonify, send_file
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home AI 3D - منصة التصميم والواقع المعزز الذكي</title>
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
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .app-container {
            width: 100%;
            max-width: 1280px;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            background: var(--card-bg);
            padding: 15px 25px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        .logo-area {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .logo-title {
            font-size: 1.6rem;
            font-weight: bold;
            color: var(--text-color);
        }
        .logo-title span {
            color: var(--accent-orange);
        }
        .badge {
            background: rgba(59, 130, 246, 0.1);
            color: var(--primary-color);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 420px 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        .form-group {
            margin-bottom: 18px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 12px;
            background: #0b0f19;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-color);
            font-size: 0.95rem;
        }
        input:focus, select:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        .grid-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .checkbox-container {
            background: #0b0f19;
            padding: 12px 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin-bottom: 15px;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        .checkbox-item:last-child {
            margin-bottom: 0;
        }
        .btn-submit {
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
            color: white;
            border: none;
            width: 100%;
            padding: 15px;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        }
        /* 3D Viewer styles */
        .viewer-container {
            display: flex;
            flex-direction: column;
            position: relative;
            background: #090d16;
            min-height: 550px;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            overflow: hidden;
            justify-content: center;
            align-items: center;
        }
        .viewer-header {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }
        .btn-download {
            background: var(--primary-color);
            color: white;
            padding: 10px 18px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
            display: none;
        }
        .btn-download.show {
            display: inline-block;
        }
        .viewer-3d {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        .grid-3d-bg {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: linear-gradient(to right, rgba(59,130,246,0.05) 1px, transparent 1px),
                              linear-gradient(to bottom, rgba(59,130,246,0.05) 1px, transparent 1px);
            background-size: 30px 30px;
            pointer-events: none;
        }
        .placeholder-3d {
            text-align: center;
            color: var(--text-muted);
            padding: 40px;
            z-index: 2;
        }
        .render-3d {
            max-width: 90%;
            max-height: 420px;
            object-fit: contain;
            border-radius: 12px;
            display: none;
            animation: fadeIn 0.5s ease-in-out;
        }
        /* Gallery */
        .gallery-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--text-color);
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .gallery-item {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 15px;
            transition: transform 0.3s;
        }
        .gallery-item:hover {
            transform: translateY(-5px);
        }
        .gallery-preview {
            width: 100%;
            height: 180px;
            background: #090d16;
            border-radius: 8px;
            margin-bottom: 12px;
            background-size: cover;
            background-position: center;
        }
        .gallery-info h4 {
            font-size: 1rem;
            margin-bottom: 5px;
        }
        .gallery-info p {
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
    </style>
</head>
<body>

    <div class="app-container">
        <header>
            <div class="logo-area">
                <span class="logo-title">HOME AI <span>3D</span></span>
                <span class="badge">تطبيق التصميم والواقع المعزز الذكي 🏢</span>
            </div>
        </header>

        <div class="main-grid">
            <!-- التحكم والمدخلات -->
            <div class="card">
                <form id="buildForm">
                    <div class="form-group">
                        <label for="desc">وصف الغرفة أو المساحة</label>
                        <input type="text" id="desc" placeholder="مثال: غرفة معيشة مودرن واسعة" required>
                    </div>

                    <div class="grid-inputs">
                        <div class="form-group">
                            <label for="dim">الأبعاد (طول×عرض م)</label>
                            <input type="text" id="dim" placeholder="مثال: 5 × 4" required>
                        </div>
                        <div class="form-group">
                            <label for="height">الارتفاع (م)</label>
                            <input type="number" step="0.1" id="height" value="3.0">
                        </div>
                    </div>

                    <div class="grid-inputs">
                        <div class="form-group">
                            <label for="rooms">عدد الغرف</label>
                            <input type="number" id="rooms" value="1" min="1">
                        </div>
                        <div class="form-group">
                            <label for="baths">الحمامات</label>
                            <input type="number" id="baths" value="1" min="0">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="style">نمط التصميم الداخلي</label>
                        <select id="style">
                            <option value="modern">مودرن حديث (معاصر)</option>
                            <option value="classic">كلاسيكي دافئ</option>
                            <option value="scandi">اسكندنافي مريح</option>
                            <option value="industrial">صناعي (Industrial)</option>
                        </select>
                    </div>

                    <div class="checkbox-container">
                        <label class="checkbox-item"><input type="checkbox" id="furnish" checked> تأثيث تلقائي (Auto-Furnish)</label>
                        <label class="checkbox-item"><input type="checkbox" id="lighting" checked> إضاءة واقعية (Realistic Lighting)</label>
                        <label class="checkbox-item"><input type="checkbox" id="decor" checked> إضافة نباتات وديكور</label>
                    </div>

                    <div class="form-group">
                        <label for="engine">محرك التوليد</label>
                        <select id="engine">
                            <option value="3d">توليد مجسم ثلاثي الأبعاد تفاعلي (Interactive 3D)</option>
                            <option value="ar">عرض واقع معزز (AR View)</option>
                        </select>
                    </div>

                    <button type="submit" class="btn-submit">بدء التوليد والمعالجة ثلاثية الأبعاد 🚀</button>
                </form>
            </div>

            <!-- عارض الـ 3D التفاعلي -->
            <div class="viewer-container">
                <div class="viewer-header">
                    <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success-color);">بيئة عارض الـ 3D التفاعلية</span>
                    <a href="#" id="downloadLink" class="btn-download" download="home_ai_design_3d.obj">تحميل المجسم 3D (OBJ) 📥</a>
                </div>
                
                <div class="viewer-3d">
                    <div class="grid-3d-bg"></div>
                    <div class="placeholder-3d" id="placeholder">
                        <h3>جاهز لبدء التصميم والتحويل!</h3>
                        <p style="margin-top:8px;">أدخل المواصفات واضغط على زر التوليد لعرض المجسم ثلاثي الأبعاد والتحكم به.</p>
                    </div>
                    <!-- صورة محاكاة التوليد التفاعلي -->
                    <img id="renderImg" class="render-3d" src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80" alt="3D Render View">
                </div>
            </div>
        </div>

        <!-- معرض المشاريع -->
        <div class="gallery-title">معرض الشقق والتصاميم المقترحة</div>
        <div class="gallery-grid">
            <div class="gallery-item">
                <div class="gallery-preview" style="background-image: url('https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=400&q=80')"></div>
                <div class="gallery-info">
                    <h4>شقة عصرية (أثاث متكامل)</h4>
                    <p>صالون مفتوح مع تفاصيل طبيعية ونمط اسكندنافي مميز.</p>
                </div>
            </div>
            <div class="gallery-item">
                <div class="gallery-preview" style="background-image: url('https://images.unsplash.com/photo-1617806118233-18e1db207fd6?auto=format&fit=crop&w=400&q=80')"></div>
                <div class="gallery-info">
                    <h4>شقة فاخرة (طابقين)</h4>
                    <p>نمط معاصر مميز بنظام إضاءة مدروس ومساحات مفتوحة.</p>
                </div>
            </div>
            <div class="gallery-item">
                <div class="gallery-preview" style="background-image: url('https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=400&q=80')"></div>
                <div class="gallery-info">
                    <h4>صالة جلوس صغيرة الحجم</h4>
                    <p>استغلال ذكي للمساحات مع ألوان دافئة ونباتات زينة مريحة.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('buildForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const btn = document.querySelector('.btn-submit');
            const placeholder = document.getElementById('placeholder');
            const renderImg = document.getElementById('renderImg');
            const downloadLink = document.getElementById('downloadLink');

            btn.textContent = 'جاري المعالجة وتوليد المجسمات... ⏳';
            btn.disabled = true;

            try {
                // محاكاة الطلب والتحويل بمهلة قصيرة
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                placeholder.style.display = 'none';
                renderImg.style.display = 'block';
                downloadLink.className = 'btn-download show';

            } catch (err) {
                alert('حدث خطأ أثناء الاتصال بالخادم، جرب مرة أخرى.');
            } finally {
                btn.textContent = 'بدء التوليد والمعالجة ثلاثية الأبعاد 🚀';
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

@app.route('/process', methods=['POST'])
def process():
    # في المستقبل، يمكن ربط هذه الوظيفة مع API توليد النماذج مثل Meshy أو Get3D
    return jsonify({
        "status": "success",
        "message": "تم إعداد المجسم ثلاثي الأبعاد ومعالجته بنجاح."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
