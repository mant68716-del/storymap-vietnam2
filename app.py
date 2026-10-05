import os, sqlite3, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'storymap.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'storymap-dev-change-me'),
    MAX_CONTENT_LENGTH=512 * 1024 * 1024,  # 512 MB/request for local MVP
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE','true').lower() == 'true',
)

IMAGE_EXT = {'png','jpg','jpeg','gif','webp'}
VIDEO_EXT = {'mp4','mov','webm','m4v'}
ALLOWED_EXT = IMAGE_EXT | VIDEO_EXT

PROVINCES = [
('01','Hà Nội'),('02','Hà Giang'),('04','Cao Bằng'),('06','Bắc Kạn'),('08','Tuyên Quang'),('10','Lào Cai'),('11','Điện Biên'),('12','Lai Châu'),('14','Sơn La'),('15','Yên Bái'),('17','Hòa Bình'),('19','Thái Nguyên'),('20','Lạng Sơn'),('22','Quảng Ninh'),('24','Bắc Giang'),('25','Phú Thọ'),('26','Vĩnh Phúc'),('27','Bắc Ninh'),('30','Hải Dương'),('31','Hải Phòng'),('33','Hưng Yên'),('34','Thái Bình'),('35','Hà Nam'),('36','Nam Định'),('37','Ninh Bình'),('38','Thanh Hóa'),('40','Nghệ An'),('42','Hà Tĩnh'),('44','Quảng Bình'),('45','Quảng Trị'),('46','Thừa Thiên Huế'),('48','Đà Nẵng'),('49','Quảng Nam'),('51','Quảng Ngãi'),('52','Bình Định'),('54','Phú Yên'),('56','Khánh Hòa'),('58','Ninh Thuận'),('60','Bình Thuận'),('62','Kon Tum'),('64','Gia Lai'),('66','Đắk Lắk'),('67','Đắk Nông'),('68','Lâm Đồng'),('70','Bình Phước'),('72','Tây Ninh'),('74','Bình Dương'),('75','Đồng Nai'),('77','Bà Rịa - Vũng Tàu'),('79','TP. Hồ Chí Minh'),('80','Long An'),('82','Tiền Giang'),('83','Bến Tre'),('84','Trà Vinh'),('86','Vĩnh Long'),('87','Đồng Tháp'),('89','An Giang'),('91','Kiên Giang'),('92','Cần Thơ'),('93','Hậu Giang'),('94','Sóc Trăng'),('95','Bạc Liêu'),('96','Cà Mau')]

CENTERS = {
'Hà Nội':(21.03,105.85),'Hà Giang':(22.82,104.98),'Cao Bằng':(22.67,106.25),'Bắc Kạn':(22.15,105.83),'Tuyên Quang':(21.82,105.22),'Lào Cai':(22.34,104.15),'Điện Biên':(21.39,103.02),'Lai Châu':(22.39,103.47),'Sơn La':(21.33,103.91),'Yên Bái':(21.72,104.91),'Hòa Bình':(20.81,105.34),'Thái Nguyên':(21.59,105.84),'Lạng Sơn':(21.85,106.76),'Quảng Ninh':(21.01,107.29),'Bắc Giang':(21.27,106.19),'Phú Thọ':(21.32,105.23),'Vĩnh Phúc':(21.31,105.60),'Bắc Ninh':(21.19,106.07),'Hải Dương':(20.94,106.33),'Hải Phòng':(20.84,106.69),'Hưng Yên':(20.65,106.05),'Thái Bình':(20.45,106.34),'Hà Nam':(20.54,105.91),'Nam Định':(20.42,106.17),'Ninh Bình':(20.25,105.97),'Thanh Hóa':(19.81,105.78),'Nghệ An':(19.24,104.92),'Hà Tĩnh':(18.36,105.90),'Quảng Bình':(17.48,106.62),'Quảng Trị':(16.75,107.19),'Thừa Thiên Huế':(16.47,107.59),'Đà Nẵng':(16.05,108.20),'Quảng Nam':(15.57,108.47),'Quảng Ngãi':(15.12,108.80),'Bình Định':(13.78,109.22),'Phú Yên':(13.09,109.31),'Khánh Hòa':(12.25,109.19),'Ninh Thuận':(11.57,108.99),'Bình Thuận':(10.93,108.10),'Kon Tum':(14.35,108.00),'Gia Lai':(13.98,108.00),'Đắk Lắk':(12.67,108.04),'Đắk Nông':(12.00,107.69),'Lâm Đồng':(11.57,108.00),'Bình Phước':(11.75,106.88),'Tây Ninh':(11.31,106.10),'Bình Dương':(11.17,106.65),'Đồng Nai':(11.07,107.17),'Bà Rịa - Vũng Tàu':(10.58,107.24),'TP. Hồ Chí Minh':(10.78,106.70),'Long An':(10.53,106.41),'Tiền Giang':(10.36,106.36),'Bến Tre':(10.24,106.38),'Trà Vinh':(9.95,106.34),'Vĩnh Long':(10.25,105.97),'Đồng Tháp':(10.59,105.64),'An Giang':(10.52,105.13),'Kiên Giang':(9.78,105.08),'Cần Thơ':(10.03,105.78),'Hậu Giang':(9.78,105.47),'Sóc Trăng':(9.60,105.98),'Bạc Liêu':(9.29,105.72),'Cà Mau':(9.18,105.15)}
ISLANDS=[('Hoàng Sa',16.50,111.75),('Trường Sa',10.50,114.00),('Phú Quốc',10.23,103.97),('Côn Đảo',8.68,106.60),('Cát Bà',20.73,107.05)]

def db():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c

def init_db():
    c=db(); c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL,bio TEXT DEFAULT '',avatar TEXT DEFAULT '',created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS provinces(code TEXT PRIMARY KEY,name TEXT NOT NULL,map_version TEXT NOT NULL DEFAULT '63-pre-2025');
    CREATE TABLE IF NOT EXISTS stories(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,province_code TEXT NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,visit_date TEXT,location TEXT DEFAULT '',latitude REAL,longitude REAL,image_filename TEXT DEFAULT '',created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,FOREIGN KEY(province_code) REFERENCES provinces(code));
    CREATE TABLE IF NOT EXISTS media(id INTEGER PRIMARY KEY AUTOINCREMENT,story_id INTEGER NOT NULL,filename TEXT NOT NULL,media_type TEXT NOT NULL,original_name TEXT DEFAULT '',created_at TEXT NOT NULL,FOREIGN KEY(story_id) REFERENCES stories(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS visits(user_id INTEGER NOT NULL,province_code TEXT NOT NULL,visited_at TEXT NOT NULL,PRIMARY KEY(user_id,province_code),FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,FOREIGN KEY(province_code) REFERENCES provinces(code));
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,province_code TEXT,title TEXT NOT NULL,note TEXT DEFAULT '',due_date TEXT,status TEXT NOT NULL DEFAULT 'todo',created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,FOREIGN KEY(province_code) REFERENCES provinces(code));
    ''')
    for code,name in PROVINCES: c.execute('INSERT OR IGNORE INTO provinces(code,name,map_version) VALUES(?,?,?)',(code,name,'63-pre-2025'))
    c.commit(); c.close()

init_db()

def csrf_token():
    if 'csrf' not in session: session['csrf']=secrets.token_urlsafe(32)
    return session['csrf']
app.jinja_env.globals['csrf_token']=csrf_token

@app.before_request
def csrf_check():
    if request.method=='POST':
        token=request.form.get('csrf') or request.headers.get('X-CSRF-Token')
        if not token or token != session.get('csrf'): abort(400,'CSRF token không hợp lệ')

def user():
    uid=session.get('user_id')
    if not uid: return None
    c=db(); u=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone(); c.close(); return u

def login_required(fn):
    @wraps(fn)
    def w(*a,**kw):
        if not user(): return redirect(url_for('login',next=request.path))
        return fn(*a,**kw)
    return w

@app.context_processor
def globals_(): return {'me':user(),'province_count':63,'islands':ISLANDS}

@app.route('/')
def home():
    c=db(); visited=[]; stories=[]; tasks=[]
    if session.get('user_id'):
        uid=session['user_id']; visited=[r['province_code'] for r in c.execute('SELECT province_code FROM visits WHERE user_id=?',(uid,))]
        stories=c.execute('SELECT s.*,p.name province_name FROM stories s JOIN provinces p ON p.code=s.province_code WHERE s.user_id=? ORDER BY s.created_at DESC',(uid,)).fetchall()
        tasks=c.execute("SELECT t.*,p.name province_name FROM tasks t LEFT JOIN provinces p ON p.code=t.province_code WHERE t.user_id=? ORDER BY t.status,t.created_at DESC",(uid,)).fetchall()
    c.close(); return render_template('index.html',provinces=PROVINCES,centers=CENTERS,visited=visited,stories=stories,tasks=tasks)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        if len(name)<2 or '@' not in email or len(pw)<8: flash('Tên, email hoặc mật khẩu chưa hợp lệ. Mật khẩu tối thiểu 8 ký tự.','danger'); return render_template('auth.html',mode='register')
        c=db()
        try:
            cur=c.execute('INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)',(name,email,generate_password_hash(pw),datetime.utcnow().isoformat())); c.commit(); session.clear(); session['user_id']=cur.lastrowid; csrf_token(); return redirect(url_for('home'))
        except sqlite3.IntegrityError: flash('Email đã được đăng ký.','danger')
        finally: c.close()
    return render_template('auth.html',mode='register')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); pw=request.form.get('password',''); c=db(); u=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone(); c.close()
        if u and check_password_hash(u['password_hash'],pw): session.clear(); session['user_id']=u['id']; csrf_token(); return redirect(request.args.get('next') or url_for('home'))
        flash('Email hoặc mật khẩu không đúng.','danger')
    return render_template('auth.html',mode='login')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    u=user(); c=db()
    if request.method=='POST':
        name=request.form.get('name','').strip(); bio=request.form.get('bio','').strip()
        if len(name)>=2: c.execute('UPDATE users SET name=?,bio=? WHERE id=?',(name,bio,u['id'])); c.commit(); flash('Đã cập nhật hồ sơ.','success')
    u=c.execute('SELECT * FROM users WHERE id=?',(u['id'],)).fetchone(); stats=c.execute('SELECT COUNT(*) n FROM visits WHERE user_id=?',(u['id'],)).fetchone()['n']; sc=c.execute('SELECT COUNT(*) n FROM stories WHERE user_id=?',(u['id'],)).fetchone()['n']; tc=c.execute("SELECT COUNT(*) n FROM tasks WHERE user_id=? AND status='todo'",(u['id'],)).fetchone()['n']; c.close()
    return render_template('profile.html',user=u,visited_count=stats,story_count=sc,task_count=tc)

@app.route('/story/new/<code>',methods=['GET','POST'])
@login_required
def new_story(code):
    c=db(); p=c.execute('SELECT * FROM provinces WHERE code=?',(code,)).fetchone()
    if not p: c.close(); abort(404)
    if request.method=='POST':
        title=request.form.get('title','').strip(); content=request.form.get('content','').strip(); date=request.form.get('visit_date') or None; loc=request.form.get('location','').strip(); lat=request.form.get('latitude') or None; lon=request.form.get('longitude') or None
        files=request.files.getlist('media')
        if not title or not content: c.close(); flash('Hãy nhập tiêu đề và nội dung Story.','danger'); return render_template('story_form.html',province=p,center=CENTERS.get(p['name']))
        valid=[]
        for f in files:
            if f and f.filename:
                ext=f.filename.rsplit('.',1)[-1].lower() if '.' in f.filename else ''
                if ext not in ALLOWED_EXT: c.close(); flash('Chỉ hỗ trợ ảnh PNG/JPG/WebP/GIF và video MP4/MOV/WebM/M4V.','danger'); return render_template('story_form.html',province=p,center=CENTERS.get(p['name']))
                valid.append((f,ext))
        now=datetime.utcnow().isoformat(); cur=c.execute('INSERT INTO stories(user_id,province_code,title,content,visit_date,location,latitude,longitude,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(session['user_id'],code,title,content,date,loc,lat,lon,now)); sid=cur.lastrowid
        for f,ext in valid:
            name=secrets.token_hex(12)+'_'+secure_filename(f.filename); f.save(os.path.join(UPLOAD_DIR,name)); typ='video' if ext in VIDEO_EXT else 'image'; c.execute('INSERT INTO media(story_id,filename,media_type,original_name,created_at) VALUES(?,?,?,?,?)',(sid,name,typ,secure_filename(f.filename),now))
        c.execute('INSERT OR REPLACE INTO visits(user_id,province_code,visited_at) VALUES(?,?,?)',(session['user_id'],code,date or datetime.utcnow().date().isoformat())); c.commit(); c.close(); flash('Đã lưu Story và đánh dấu tỉnh đã đi.','success'); return redirect(url_for('story_view',story_id=sid))
    c.close(); return render_template('story_form.html',province=p,center=CENTERS.get(p['name']))

@app.route('/story/<int:story_id>')
@login_required
def story_view(story_id):
    c=db(); s=c.execute('SELECT s.*,p.name province_name FROM stories s JOIN provinces p ON p.code=s.province_code WHERE s.id=? AND s.user_id=?',(story_id,session['user_id'])).fetchone(); media=c.execute('SELECT * FROM media WHERE story_id=? ORDER BY id',(story_id,)).fetchall() if s else []; c.close()
    if not s: abort(404)
    return render_template('story_view.html',story=s,media=media)

@app.route('/uploads/<path:filename>')
def uploads(filename): return send_from_directory(UPLOAD_DIR,filename)

@app.route('/story/<int:story_id>/delete',methods=['POST'])
@login_required
def delete_story(story_id):
    c=db(); media=c.execute('SELECT filename FROM media WHERE story_id=?',(story_id,)).fetchall(); old=c.execute('SELECT image_filename FROM stories WHERE id=? AND user_id=?',(story_id,session['user_id'])).fetchone()
    for m in media:
        try: os.remove(os.path.join(UPLOAD_DIR,m['filename']))
        except OSError: pass
    if old and old['image_filename']:
        try: os.remove(os.path.join(UPLOAD_DIR,old['image_filename']))
        except OSError: pass
    c.execute('DELETE FROM stories WHERE id=? AND user_id=?',(story_id,session['user_id'])); c.commit(); c.close(); return redirect(url_for('home'))

@app.route('/task/add',methods=['POST'])
@login_required
def add_task():
    title=request.form.get('title','').strip(); code=request.form.get('province_code') or None; note=request.form.get('note','').strip(); due=request.form.get('due_date') or None
    if title:
        c=db(); c.execute('INSERT INTO tasks(user_id,province_code,title,note,due_date,status,created_at) VALUES(?,?,?,?,?,?,?)',(session['user_id'],code,title,note,due,'todo',datetime.utcnow().isoformat())); c.commit(); c.close()
    return redirect(url_for('home'))

@app.route('/task/<int:task_id>/toggle',methods=['POST'])
@login_required
def toggle_task(task_id):
    c=db(); t=c.execute('SELECT status FROM tasks WHERE id=? AND user_id=?',(task_id,session['user_id'])).fetchone()
    if t: c.execute('UPDATE tasks SET status=? WHERE id=?',('done' if t['status']=='todo' else 'todo',task_id)); c.commit()
    c.close(); return redirect(url_for('home'))

@app.route('/task/<int:task_id>/delete',methods=['POST'])
@login_required
def delete_task(task_id):
    c=db(); c.execute('DELETE FROM tasks WHERE id=? AND user_id=?',(task_id,session['user_id'])); c.commit(); c.close(); return redirect(url_for('home'))

if __name__=='__main__':
    # 0.0.0.0 lets phones on the same Wi-Fi open the app.
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG','false').lower() == 'true')
