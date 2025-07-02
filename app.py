from flask import Flask, render_template, g, render_template_string, url_for, request, send_file, send_from_directory, jsonify, redirect, flash, session
import sqlite3
import os
from cache_manager import CacheManager
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
import urllib.parse
from forms import EffectForm

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'EffectsDB.db'
cache_manager = CacheManager(app=app)

# Constants
EFFECT_TYPE_MAP = {
    'picture': 'picture',
    'text': 'text',
    'solution': 'solution',
    'animation': 'animation'
}

# Helper functions
def validate_effect_type(effect_type):
    db_effect_type = EFFECT_TYPE_MAP.get(effect_type)
    if not db_effect_type:
        raise ValueError(f"Invalid effect type. Must be one of: {', '.join(EFFECT_TYPE_MAP.keys())}")
    return db_effect_type

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            app.logger.error(f"Invalid value: {str(e)}")
            return render_template('error.html', error=str(e)), 400
        except sqlite3.Error as e:
            app.logger.error(f"Database error: {str(e)}")
            return render_template('error.html', error="Database error"), 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return render_template('error.html', error="An unexpected error occurred"), 500
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

# Function to get effect by index
def get_effect_by_index(effect_type, index):
    db_effect_type = validate_effect_type(effect_type)
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM effects WHERE effect_type = ?", (db_effect_type,))
    total_effects = cursor.fetchone()[0]
    
    if total_effects == 0:
        raise ValueError(f"No effects found for type: {effect_type}")
        
    if index < 0 or index >= total_effects:
        raise ValueError(f"Invalid effect index. Must be between 0 and {total_effects-1}")
    
    cursor.execute("""
        SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public 
        FROM effects 
        WHERE effect_type = ? 
        LIMIT 1 OFFSET ?
    """, (db_effect_type, index))
    
    effect = cursor.fetchone()
    if not effect:
        raise ValueError('Effect not found')
    
    return dict(effect)

@app.route('/')
def Index():
    return render_template('Index.html')

@app.route('/effects/<effect_type>')
@handle_errors
def effects(effect_type):
    db_effect_type = validate_effect_type(effect_type)
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT name, preview_image, code FROM effects WHERE effect_type = ? AND is_public = 1", (db_effect_type,))
    effects = cursor.fetchall()
    
    items = []
    for row in effects:
        if row[0] and row[1]:  # Check if both name and image are not None
            items.append({
                "description": row[0],
                "image": 'Data_pic/previews/' + row[1],
                "code": row[2] if row[2] else None
            })
    
    return render_template('effects.html', items=items, effect_type=effect_type)

@app.route('/modal')
@handle_errors
def modal():
    index = int(request.args.get('index', 0))
    effect_type = request.args.get('type', 'pic')
    
    cache_file = cache_manager.get_cached_file(index, effect_type)
    if not cache_file:
        raise ValueError("Failed to generate cache file")
    return send_file(cache_file)

@app.route('/generate_modal/<effect_type>/<int:index>')
@handle_errors
def generate_modal(effect_type, index):
    cache_file = cache_manager.get_cached_file(index, effect_type)
    if not cache_file:
        raise ValueError("Failed to generate cache file")
    return jsonify({'path': f'/static/cache/{os.path.basename(cache_file)}'})

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        filename = urllib.parse.unquote(filename)
        return send_from_directory('static', filename)
    except Exception as e:
        app.logger.error(f"Error serving static file: {str(e)}")
        return render_template('error.html', error="File not found"), 404



@app.route('/api/effect/<effect_type>/<int:index>')
@handle_errors
def get_effect(effect_type, index):
    effect = get_effect_by_index(effect_type, index)
    return jsonify(effect)

@app.route('/preview/<effect_type>/<int:effect_id>')
@handle_errors
def preview_effect(effect_type, effect_id):
    db_effect_type = validate_effect_type(effect_type)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
        FROM effects 
        WHERE id = ? AND effect_type = ?
    """, (effect_id, db_effect_type))
    effect = cursor.fetchone()
    if not effect:
        raise ValueError('Effect not found')
    # Генерируем HTML-файл через cache_manager (можно по id или по коду)
    # Здесь для простоты используем code напрямую:
    modified_code = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style></style>
    </head>
    <body>
        {effect['code']}
    </body>
    </html>
    '''
    from flask import render_template_string, make_response
    rendered_html = render_template_string(modified_code)
    response = make_response(rendered_html)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    app.logger.error(f"Unhandled exception: {str(e)}")
    return render_template('error.html', error="An unexpected error occurred"), 500

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password')
                return redirect(url_for('login'))
            
            db = get_db()
            cursor = db.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                flash('Database not properly initialized. Please contact administrator.')
                return redirect(url_for('login'))
            
            cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                flash('Logged in successfully!')
                return redirect(url_for('cabinet'))
            
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        return render_template('auth_form.html',
            title='Login',
            submit_text='Login',
            link_text="Don't have an account?",
            link_url=url_for('register'),
            link_label='Register here')
        
    except Exception as e:
        app.logger.error(f"Error in login route: {str(e)}")
        flash('An error occurred during login. Please try again.')
        return render_template('auth_form.html',
            title='Login',
            submit_text='Login',
            link_text="Don't have an account?",
            link_url=url_for('register'),
            link_label='Register here')

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password')
                return redirect(url_for('register'))
            
            if len(username) < 3:
                flash('Username must be at least 3 characters long')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long')
                return redirect(url_for('register'))
            
            db = get_db()
            cursor = db.cursor()
            
            try:
                # Check if username already exists
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    flash('Username already exists')
                    return redirect(url_for('register'))
                
                # Create new user
                hashed_password = generate_password_hash(password)
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                            (username, hashed_password))
                db.commit()
                
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
                
            except sqlite3.Error as e:
                db.rollback()
                app.logger.error(f"Database error during registration: {str(e)}")
                flash('An error occurred during registration. Please try again.')
                return redirect(url_for('register'))
        
        return render_template('auth_form.html',
            title='Register',
            submit_text='Register',
            link_text='Already have an account?',
            link_url=url_for('login'),
            link_label='Login here')
        
    except Exception as e:
        app.logger.error(f"Error in register route: {str(e)}")
        flash('An error occurred during registration. Please try again.')
        return render_template('auth_form.html',
            title='Register',
            submit_text='Register',
            link_text='Already have an account?',
            link_url=url_for('login'),
            link_label='Login here')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('Index'))

@app.route('/cabinet')
@login_required
@handle_errors
def cabinet():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public 
        FROM effects 
        WHERE user_id = ? 
        ORDER BY id ASC
    ''', (session['user_id'],))
    effects = cursor.fetchall()
    formatted_effects = []
    for idx, effect in enumerate(effects):
        effect_dict = dict(effect)
        effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
        effect_dict['url_type'] = next((k for k, v in EFFECT_TYPE_MAP.items() if v == effect_dict['effect_type']), effect_dict['effect_type'])
        effect_dict['has_preview'] = bool(effect_dict['preview_image'])
        effect_dict['has_code'] = bool(effect_dict['code'])
        effect_dict['index'] = idx
        formatted_effects.append(effect_dict)
    form = EffectForm()
    return render_template('cabinet.html', effects=formatted_effects, form=form)

@app.route('/add_effect', methods=['GET', 'POST'])
@login_required
@handle_errors
def add_effect():
    form = EffectForm()
    if form.validate_on_submit():
        name = form.name.data
        code = form.code.data
        effect_type = form.effect_type.data
        is_public = form.is_public.data
        db_effect_type = validate_effect_type(effect_type)
        preview_image = form.preview_image.data
        if not preview_image:
            raise ValueError('No preview image provided')
        filename = secure_filename(preview_image.filename)
        preview_path = os.path.join('static', 'Data_pic', 'previews', filename)
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        preview_image.save(preview_path)
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO effects (name, code, effect_type, preview_image, user_id, is_public)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, code, db_effect_type, filename, session['user_id'], is_public))
        db.commit()
        effect_id = cursor.lastrowid
        cursor.execute('''
            SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
            FROM effects
            WHERE id = ?
        ''', (effect_id,))
        effect = cursor.fetchone()
        effect_dict = dict(effect)
        effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
        effect_dict['url_type'] = db_effect_type
        return jsonify({
            'message': 'Effect added successfully',
            'effect': effect_dict
        })
    # Если не POST или невалидно, просто возвращаем кабинет с формой
    return redirect(url_for('cabinet'))
@app.route('/edit_effect/<effect_type>/<int:effect_id>', methods=['GET', 'POST'])
@login_required
@handle_errors
def edit_effect(effect_type, effect_id):
    db_effect_type = validate_effect_type(effect_type)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
        FROM effects
        WHERE id = ? AND user_id = ? AND effect_type = ?
    ''', (effect_id, session['user_id'], db_effect_type))
    effect = cursor.fetchone()
    if not effect:

        raise ValueError('Effect not found')
    form = EffectForm()
    if request.method == 'GET':
        # Заполняем форму данными эффекта
        form.effect_type.data = effect['effect_type']
        form.name.data = effect['name']
        form.code.data = effect['code']
        form.is_public.data = effect['is_public']
        form.effect_id.data = effect['id']
        # preview_image не заполняем (файл)
        return jsonify(dict(effect))
    if form.validate_on_submit():
        effect_name = form.name.data
        code = form.code.data
        is_public = form.is_public.data
        preview_image = form.preview_image.data
        if preview_image and preview_image.filename:
            filename = secure_filename(preview_image.filename)
            previews_dir = os.path.join('static', 'Data_pic', 'previews')
            os.makedirs(previews_dir, exist_ok=True)
            if effect['preview_image']:
                old_image_path = os.path.join('static', 'Data_pic', 'previews', effect['preview_image'])
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            preview_image.save(os.path.join(previews_dir, filename))
            cursor.execute('''
                UPDATE effects
                SET name = ?, preview_image = ?, code = ?, is_public = ?, updated_at = datetime('now')
                WHERE id = ? AND user_id = ? AND effect_type = ?
            ''', (effect_name, filename, code, is_public, effect_id, session['user_id'], db_effect_type))
        else:
            cursor.execute('''
                UPDATE effects
                SET name = ?, code = ?, is_public = ?, updated_at = datetime('now')
                WHERE id = ? AND user_id = ? AND effect_type = ?
            ''', (effect_name, code, is_public, effect_id, session['user_id'], db_effect_type))
        db.commit()
        cursor.execute('''
            SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
            FROM effects
            WHERE id = ? AND user_id = ? AND effect_type = ?
        ''', (effect_id, session['user_id'], db_effect_type))
        updated_effect = cursor.fetchone()
        effect_dict = dict(updated_effect)
        effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
        effect_dict['url_type'] = effect_type
        return jsonify({
            'message': 'Effect updated successfully',
            'effect': effect_dict
        })
    # Если не POST или невалидно, просто возвращаем кабинет с формой
    return redirect(url_for('cabinet'))

@app.route('/delete_effect/<effect_type>/<int:effect_id>', methods=['POST'])
@login_required
@handle_errors
def delete_effect(effect_type, effect_id):
    
    db_effect_type = validate_effect_type(effect_type)
    db = get_db()
    cursor = db.cursor()
    # Get effect information before deletion
    cursor.execute('''
        SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
        FROM effects
        WHERE id = ? AND user_id = ? AND effect_type = ?
    ''', (effect_id, session['user_id'], db_effect_type))
    effect = cursor.fetchone()
    if not effect:
        raise ValueError('Effect not found')
    # Удаляем файл превью, если он есть
    if effect['preview_image']:
        preview_path = os.path.join('static', 'Data_pic', 'previews', effect['preview_image'])
        if os.path.exists(preview_path):
            os.remove(preview_path)
    # Удаляем кэшированные HTML-файлы для этого эффекта
    cache_dir = os.path.join('static', 'cache')
    if os.path.exists(cache_dir):
        for file in os.listdir(cache_dir):
            if file.startswith(f"effect_{db_effect_type}_") and (str(effect_id) in file or effect['preview_image'] in file):
                try:
                    os.remove(os.path.join(cache_dir, file))
                except Exception:
                    pass
    # Delete the effect
    cursor.execute('''
        DELETE FROM effects
        WHERE id = ? AND user_id = ? AND effect_type = ?
    ''', (effect_id, session['user_id'], db_effect_type))
    db.commit()
    # Prepare response data
    effect_dict = dict(effect)
    effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
    effect_dict['url_type'] = db_effect_type
    return jsonify({
        'message': 'Effect deleted successfully',
        'effect': effect_dict
    })

@app.route('/render_effect_card', methods=['POST'])
@login_required
def render_effect_card():
    effect = request.json.get('effect')
    return render_template('effect_card.html', item=effect, context='cabinet')

@app.route('/toggle_public/<effect_type>/<int:effect_id>', methods=['POST'])
@login_required
def toggle_public(effect_type, effect_id):
    db_effect_type = validate_effect_type(effect_type)
    db = get_db()
    cursor = db.cursor()
    is_public = request.json.get('is_public', 0)
    cursor.execute('''
        UPDATE effects
        SET is_public = ?
        WHERE id = ? AND user_id = ? AND effect_type = ?
    ''', (is_public, effect_id, session['user_id'], db_effect_type))
    db.commit()
    return jsonify({'message': 'Статус публикации обновлён'})

if __name__ == '__main__':
    app.run(debug=True)
