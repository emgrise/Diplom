from flask import Flask, render_template, g, render_template_string, url_for, request, send_file, send_from_directory, jsonify, redirect, flash, session
import sqlite3
from generate_modal import generate_modal_html
import os
from cache_manager import CacheManager
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
import urllib.parse

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)  # Required for session management
DATABASE = 'EffectsDB_new.db'
cache_manager = CacheManager(app=app)

# Login required decorator
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
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.route('/')
def Index():
    return render_template('Index.html')

@app.route('/text')
def Text():
    try:
        app.logger.info("Loading text effects")
        db = get_db()
        cursor = db.cursor()
        
        # Get all text effects
        cursor.execute("SELECT name, preview_image, code FROM effects WHERE effect_type = 'text' AND is_public = 1")
        effects = cursor.fetchall()
        app.logger.info(f"Retrieved {len(effects)} effects")
        
        items = []
        for row in effects:
            if row[0] and row[1]:  # Check if both name and image are not None
                items.append({
                    "description": row[0],
                    "image": 'Data_pic/previews/' + row[1],
                    "code": row[2] if row[2] else None
                })
            else:
                app.logger.warning(f"Skipping effect with missing data: {row}")
        
        app.logger.info(f"Processed {len(items)} valid effects")
        return render_template('Text.html', items=items)
        
    except sqlite3.Error as e:
        app.logger.error(f"Database error in Text route: {str(e)}")
        return render_template('error.html', error="Database error"), 500
    except Exception as e:
        app.logger.error(f"Error in Text route: {str(e)}")
        return render_template('error.html', error="Failed to load text effects"), 500

@app.route('/picture')
def Picture():
    try:
        app.logger.info("Loading picture effects")
        db = get_db()
        cursor = db.cursor()
        
        # Get all picture effects
        cursor.execute("SELECT name, preview_image, code FROM effects WHERE effect_type = 'pic' AND is_public = 1")
        effects = cursor.fetchall()
        app.logger.info(f"Retrieved {len(effects)} effects")
        
        items = []
        for row in effects:
            if row[0] and row[1]:  # Check if both name and image are not None
                items.append({
                    "description": row[0],
                    "image": 'Data_pic/previews/' + row[1],
                    "code": row[2] if row[2] else None
                })
            else:
                app.logger.warning(f"Skipping effect with missing data: {row}")
        
        app.logger.info(f"Processed {len(items)} valid effects")
        return render_template('Picture.html', items=items)
        
    except sqlite3.Error as e:
        app.logger.error(f"Database error in Picture route: {str(e)}")
        return render_template('error.html', error="Database error"), 500
    except Exception as e:
        app.logger.error(f"Error in Picture route: {str(e)}")
        return render_template('error.html', error="Failed to load picture effects"), 500

@app.route('/solution')
def Solution():
    try:
        app.logger.info("Loading solution effects")
        db = get_db()
        cursor = db.cursor()
        
        # Get all solution effects
        cursor.execute("SELECT name, preview_image, code FROM effects WHERE effect_type = 'solution' AND is_public = 1")
        effects = cursor.fetchall()
        app.logger.info(f"Retrieved {len(effects)} effects")
        
        items = []
        for row in effects:
            if row[0] and row[1]:  # Check if both name and image are not None
                items.append({
                    "description": row[0],
                    "image": 'Data_pic/previews/' + row[1],
                    "code": row[2] if row[2] else None
                })
            else:
                app.logger.warning(f"Skipping effect with missing data: {row}")
        
        app.logger.info(f"Processed {len(items)} valid effects")
        return render_template('Solution.html', items=items)
        
    except sqlite3.Error as e:
        app.logger.error(f"Database error in Solution route: {str(e)}")
        return render_template('error.html', error="Database error"), 500
    except Exception as e:
        app.logger.error(f"Error in Solution route: {str(e)}")
        return render_template('error.html', error="Failed to load solution effects"), 500

@app.route('/animation')
def Animation():
    try:
        app.logger.info("Loading animation effects")
        db = get_db()
        cursor = db.cursor()
        
        # Get all animation effects
        cursor.execute("SELECT name, preview_image, code FROM effects WHERE effect_type = 'animation' AND is_public = 1")
        effects = cursor.fetchall()
        app.logger.info(f"Retrieved {len(effects)} effects")
        
        items = []
        for row in effects:
            if row[0] and row[1]:  # Check if both name and image are not None
                items.append({
                    "description": row[0],
                    "image": 'Data_pic/previews/' + row[1],
                    "code": row[2] if row[2] else None
                })
            else:
                app.logger.warning(f"Skipping effect with missing data: {row}")
        
        app.logger.info(f"Processed {len(items)} valid effects")
        return render_template('Animation.html', items=items)
        
    except sqlite3.Error as e:
        app.logger.error(f"Database error in Animation route: {str(e)}")
        return render_template('error.html', error="Database error"), 500
    except Exception as e:
        app.logger.error(f"Error in Animation route: {str(e)}")
        return render_template('error.html', error="Failed to load animation effects"), 500

@app.route('/modal')
def modal():
    try:
        index = int(request.args.get('index', 0))
        effect_type = request.args.get('type', 'pic')
        
        # Map effect type from URL to database value
        effect_type_map = {
            'picture': 'pic',
            'text': 'text',
            'solution': 'solution',
            'animation': 'animation'
        }
        
        db_effect_type = effect_type_map.get(effect_type)
        if not db_effect_type:
            app.logger.error(f"Invalid effect type: {effect_type}")
            return render_template('error.html', error=f"Invalid effect type. Must be one of: {', '.join(effect_type_map.keys())}"), 400
        
        # Check if there are any effects of this type
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM effects WHERE effect_type = ?", (db_effect_type,))
        total_effects = cursor.fetchone()[0]
        
        if total_effects == 0:
            app.logger.error(f"No effects found for type: {db_effect_type}")
            return render_template('error.html', error=f"No effects found for type: {effect_type}"), 404
            
        if index < 0 or index >= total_effects:
            app.logger.error(f"Index {index} out of range (0-{total_effects-1})")
            return render_template('error.html', error=f"Invalid effect index. Must be between 0 and {total_effects-1}"), 400
        
        cache_file = cache_manager.get_cached_file(index, effect_type)
        
        if not cache_file:
            return render_template('error.html', error="Effect not found"), 404

        return send_file(cache_file)
    except ValueError as e:
        app.logger.error(f"Invalid index value: {str(e)}")
        return render_template('error.html', error="Invalid index value"), 400
    except Exception as e:
        app.logger.error(f"Error in modal route: {str(e)}")
        return render_template('error.html', error="Failed to load effect"), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        # Decode URL-encoded filename
        filename = urllib.parse.unquote(filename)
        return send_from_directory('static', filename)
    except Exception as e:
        app.logger.error(f"Error serving static file: {str(e)}")
        return render_template('error.html', error="File not found"), 404

@app.route('/generate_modal/<effect_type>/<int:index>')
def generate_modal(effect_type, index):
    try:
        app.logger.info(f"Generating modal for effect type: {effect_type}, index: {index}")
        
        # Map effect type from URL to database value
        effect_type_map = {
            'picture': 'pic',
            'text': 'text',
            'solution': 'solution',
            'animation': 'animation'
        }
        
        db_effect_type = effect_type_map.get(effect_type)
        if not db_effect_type:
            app.logger.error(f"Invalid effect type: {effect_type}")
            return jsonify({'error': f'Invalid effect type. Must be one of: {", ".join(effect_type_map.keys())}'}), 400
        
        # Get the effect from the database
        db = get_db()
        cursor = db.cursor()
        
        # Get the total count of effects for this type
        cursor.execute("SELECT COUNT(*) FROM effects WHERE effect_type = ?", (db_effect_type,))
        total_effects = cursor.fetchone()[0]
        app.logger.info(f"Total effects of type {db_effect_type}: {total_effects}")
        
        if total_effects == 0:
            app.logger.error(f"No effects found for type: {db_effect_type}")
            return jsonify({'error': f'No effects found for type: {effect_type}'}), 404
            
        if index < 0 or index >= total_effects:
            app.logger.error(f"Index {index} out of range (0-{total_effects-1})")
            return jsonify({'error': f'Invalid effect index. Must be between 0 and {total_effects-1}'}), 400
            
        # Get the effect code
        cursor.execute("SELECT code FROM effects WHERE effect_type = ? LIMIT 1 OFFSET ?", (db_effect_type, index))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            app.logger.error(f"No effect found at index {index}")
            return jsonify({'error': 'Effect not found'}), 404
            
        effect_code = result[0]
        
        # Generate a unique cache key for this effect
        cache_key = f"{effect_type}_{index}"
        cache_file = os.path.join('static', 'cache', f"{cache_key}.html")
        
        # Create cache directory if it doesn't exist
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        # Generate the HTML content
        style_block = """
        <style>
        img, video, object {
            object-fit: contain;
            width: 100%;
            height: 100%;
        }
        </style>
        """
        
        if "<head>" in effect_code:
            modified_code = effect_code.replace("<head>", "<head>" + style_block)
        else:
            modified_code = f'''
            <!DOCTYPE html>
            <html>
            <head>{style_block}</head>
            <body>
            {effect_code} 
            </body>
            </html>
            '''
        
        # Save the generated HTML to cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(modified_code)
        
        # Return the path relative to static directory
        return jsonify({'path': f'/static/cache/{cache_key}.html'})
        
    except Exception as e:
        app.logger.error(f"Error generating modal: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/effect/<effect_type>/<int:index>')
def render_effect(effect_type, index):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get the effect code
        cursor.execute("SELECT code FROM effects WHERE effect_type = ? LIMIT 1 OFFSET ?", (effect_type, index))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            return "Effect not found", 404
            
        effect_code = result[0]
        
        # Split the code into CSS and HTML parts
        css_parts = []
        html_parts = []
        
        for line in effect_code.split('\n'):
            if line.strip().startswith('<style>'):
                css_parts.append(line)
            elif line.strip().startswith('</style>'):
                css_parts.append(line)
            elif line.strip().startswith('<div'):
                html_parts.append(line)
            elif line.strip().startswith('</div>'):
                html_parts.append(line)
            elif css_parts and not html_parts:
                css_parts.append(line)
            elif html_parts:
                html_parts.append(line)
        
        css_code = '\n'.join(css_parts)
        html_code = '\n'.join(html_parts)
        
        return render_template('effect_template.html', 
                             effect_code=css_code,
                             effect_html=html_code)
        
    except Exception as e:
        app.logger.error(f"Error rendering effect: {str(e)}")
        return "Error loading effect", 500

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

def init_db():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create effects table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                preview_image TEXT NOT NULL,
                code TEXT,
                effect_type TEXT NOT NULL,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_public BOOLEAN DEFAULT 1
            )
        ''')
        
        db.commit()
        app.logger.info("Database schema initialized successfully")
        
    except sqlite3.Error as e:
        app.logger.error(f"Error initializing database: {str(e)}")
        raise

# Initialize the database when the app starts
with app.app_context():
    init_db()

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
        
        return render_template('register.html')
        
    except Exception as e:
        app.logger.error(f"Error in register route: {str(e)}")
        flash('An error occurred during registration. Please try again.')
        return render_template('register.html')

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
        
        return render_template('login.html')
        
    except Exception as e:
        app.logger.error(f"Error in login route: {str(e)}")
        flash('An error occurred during login. Please try again.')
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('Index'))

@app.route('/cabinet')
@login_required
def cabinet():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get user's effects
        user_id = session['user_id']
        cursor.execute('''
            SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public 
            FROM effects 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        effects = cursor.fetchall()
        
        formatted_effects = []
        for effect in effects:
            # Convert Row object to dict
            effect_dict = dict(effect)
            
            # Add image path
            effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
            
            # Map database effect type to URL effect type
            effect_type_map = {
                'pic': 'picture',
                'text': 'text',
                'solution': 'solution',
                'animation': 'animation'
            }
            effect_dict['url_type'] = effect_type_map.get(effect_dict['effect_type'], effect_dict['effect_type'])
            
            # Add additional fields for template
            effect_dict['has_preview'] = bool(effect_dict['preview_image'])
            effect_dict['has_code'] = bool(effect_dict['code'])
            
            formatted_effects.append(effect_dict)
        
        return render_template('cabinet.html', effects=formatted_effects)
        
    except Exception as e:
        app.logger.error(f"Error in cabinet route: {str(e)}")
        flash('An error occurred while loading your cabinet. Please try again.')
        return redirect(url_for('Index'))

@app.route('/add_effect', methods=['POST'])
@login_required
def add_effect():
    try:
        app.logger.info("Processing POST request")
        app.logger.info(f"Form data: {request.form}")
        app.logger.info(f"Files: {request.files}")
        
        # Get form data
        form_data = request.form.to_dict()
        app.logger.info(f"Form data dict: {form_data}")
        app.logger.info(f"Form keys: {request.form.keys()}")
        
        effect_name = form_data.get('name')
        code = form_data.get('code')
        db_effect_type = form_data.get('effect_type')
        is_public = bool(form_data.get('is_public'))
        
        app.logger.info(f"Form data - name: {effect_name}, code: {code}, type: {db_effect_type}, is_public: {is_public}")
        
        if not effect_name or not code or not db_effect_type:
            app.logger.error(f"Missing required fields - name: {effect_name}, code: {code}, type: {db_effect_type}")
            flash('Name, code, and effect type are required')
            # We don't redirect back to the form on GET for modal
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Handle preview image upload
        preview_image = request.files.get('preview_image')
        if not preview_image or not preview_image.filename:
            app.logger.error("No preview image provided")
            flash('Preview image is required')
            return jsonify({'error': 'Preview image is required'}), 400
        
        try:
            filename = preview_image.filename
            # Create previews directory if it doesn't exist
            previews_dir = os.path.join('static', 'Data_pic', 'previews')
            os.makedirs(previews_dir, exist_ok=True)
            
            # Save the preview image
            preview_path = os.path.join(previews_dir, filename)
            preview_image.save(preview_path)
            app.logger.info(f"Saved preview image to: {preview_path}")
            
            
            
            db = get_db()
            cursor = db.cursor()
            
            # Insert the effect into the effects table
            cursor.execute('''
                INSERT INTO effects (name, preview_image, code, effect_type, user_id, created_at, updated_at, is_public)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?)
            ''', (effect_name, filename, code, db_effect_type, session['user_id'], is_public))
            
            db.commit()
            app.logger.info("Effect added successfully to database")
            flash('Effect added successfully!')
            return jsonify({'message': 'Effect added successfully'})
            
        except Exception as e:
            db.rollback()
            app.logger.error(f"Error saving effect: {str(e)}")
            flash('Error saving effect. Please try again.')
            return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        app.logger.error(f"Error in add_effect: {str(e)}")
        flash('An error occurred while adding the effect. Please try again.')
        return jsonify({'error': str(e)}), 500

@app.route('/edit_effect/<effect_type>/<int:effect_id>', methods=['GET', 'POST'])
@login_required
def edit_effect(effect_type, effect_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Map effect type from URL to database value
        effect_type_map = {
            'picture': 'pic',
            'text': 'text',
            'solution': 'solution',
            'animation': 'animation'
        }
        
        db_effect_type = effect_type_map.get(effect_type)
        if not db_effect_type:
            app.logger.error(f"Invalid effect type: {effect_type}")
            return jsonify({'error': 'Invalid effect type'}), 400
        
        # Get the effect details
        cursor.execute('''
            SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
            FROM effects
            WHERE id = ? AND user_id = ? AND effect_type = ?
        ''', (effect_id, session['user_id'], db_effect_type))
        
        effect = cursor.fetchone()
        if not effect:
            app.logger.error(f"Effect not found: id={effect_id}, type={db_effect_type}")
            return jsonify({'error': 'Effect not found'}), 404
        
        if request.method == 'POST':
            try:
                effect_name = request.form.get('effect_name')
                code = request.form.get('code')
                
                if not effect_name or not code:
                    return jsonify({'error': 'Name and code are required'}), 400
                
                # Handle preview image update if provided
                preview_image = request.files.get('preview_image')
                if preview_image and preview_image.filename:
                    filename = preview_image.filename
                    # Create previews directory if it doesn't exist
                    previews_dir = os.path.join('static', 'Data_pic', 'previews')
                    os.makedirs(previews_dir, exist_ok=True)
                    
                    # Delete old preview image if it exists
                    if effect['preview_image']:
                        old_image_path = os.path.join('static','Data_pic', 'previews', effect['preview_image'])
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    # Save new preview image
                    preview_image.save(os.path.join(previews_dir, filename))
                    
                    # Store the relative path in the database
                   
                    
                    cursor.execute('''
                        UPDATE effects
                        SET name = ?, preview_image = ?, code = ?, updated_at = datetime('now')
                        WHERE id = ? AND user_id = ? AND effect_type = ?
                    ''', (effect_name, filename, code, effect_id, session['user_id'], db_effect_type))
                else:
                    cursor.execute('''
                        UPDATE effects
                        SET name = ?, code = ?, updated_at = datetime('now')
                        WHERE id = ? AND user_id = ? AND effect_type = ?
                    ''', (effect_name, code, effect_id, session['user_id'], db_effect_type))
                
                db.commit()
                
                # Get updated effect data
                cursor.execute('''
                    SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
                    FROM effects
                    WHERE id = ? AND user_id = ? AND effect_type = ?
                ''', (effect_id, session['user_id'], db_effect_type))
                
                updated_effect = cursor.fetchone()
                effect_dict = dict(updated_effect)
                effect_dict['image'] = f'Data_pic/previews/{effect_dict['preview_image']}' # Use the full path relative to static
                effect_dict['url_type'] = effect_type
                
                return jsonify({
                    'message': 'Effect updated successfully',
                    'effect': effect_dict
                })
                
            except Exception as e:
                db.rollback()
                app.logger.error(f"Error updating effect: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        # For GET requests, return the effect data
        effect_dict = dict(effect)
        effect_dict['image'] = effect_dict['preview_image']  # Use the path directly from DB
        effect_dict['url_type'] = effect_type
        return jsonify(effect_dict)
                             
    except Exception as e:
        app.logger.error(f"Error in edit_effect: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_effect/<effect_type>/<int:effect_id>', methods=['POST'])
@login_required
def delete_effect(effect_type, effect_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get the effect's preview image before deleting
        cursor.execute('''
            SELECT preview_image
            FROM effects
            WHERE id = ? AND user_id = ? AND effect_type = ?
        ''', (effect_id, session['user_id'], effect_type))
        
        effect = cursor.fetchone()
        if effect:
            old_image_path = os.path.join('static','Data_pic', 'previews', effect['preview_image'])
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # Delete the effect from the database
        cursor.execute('''
            DELETE FROM effects
            WHERE id = ? AND user_id = ? AND effect_type = ?
        ''', (effect_id, session['user_id'], effect_type))
        
        db.commit()
        app.logger.info(f"Effect deleted successfully: id={effect_id}, type={effect_type}")
        return jsonify({'message': 'Effect deleted successfully'})
        
    except Exception as e:
        db.rollback()
        app.logger.error(f"Error deleting effect: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/view_effect/<effect_type>/<int:effect_id>')
@login_required
def view_effect(effect_type, effect_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Map effect type from URL to database value
        effect_type_map = {
            'picture': 'pic',
            'text': 'text',
            'solution': 'solution',
            'animation': 'animation'
        }
        
        db_effect_type = effect_type_map.get(effect_type)
        if not db_effect_type:
            app.logger.error(f"Invalid effect type: {effect_type}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'error': 'Invalid effect type',
                    'valid_types': list(effect_type_map.keys())
                }), 400
            flash('Invalid effect type')
            return redirect(url_for('cabinet'))
        
        # Get the effect details
        cursor.execute('''
            SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public
            FROM effects
            WHERE id = ? AND user_id = ? AND effect_type = ?
        ''', (effect_id, session['user_id'], db_effect_type))
        
        effect = cursor.fetchone()
        if not effect:
            app.logger.error(f"Effect not found: id={effect_id}, type={db_effect_type}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'error': 'Effect not found',
                    'effect_id': effect_id,
                    'effect_type': effect_type
                }), 404
            flash('Effect not found')
            return redirect(url_for('cabinet'))
        
        # Convert Row object to dict
        effect_dict = dict(effect)
        effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
        effect_dict['url_type'] = effect_type
        
        # For API requests, return JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify(effect_dict)
        
        # For web requests, render the view template
        return render_template('view_effect.html',
                             effect_type=effect_type,
                             effect_id=effect_id,
                             effect=effect_dict)
                             
    except Exception as e:
        app.logger.error(f"Error in view_effect: {str(e)}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'error': str(e),
                'message': 'An error occurred while viewing the effect'
            }), 500
        flash('An error occurred while viewing the effect. Please try again.')
        return redirect(url_for('cabinet'))

@app.route('/api/effect/<effect_type>/<int:index>')
def get_effect(effect_type, index):
    try:
        # Check if effect_type is empty or None
        if not effect_type or effect_type.strip() == '':
            app.logger.error("Effect type is missing or empty")
            return jsonify({
                'error': 'Effect type is required',
                'valid_types': ['text', 'picture', 'solution', 'animation']
            }), 400
            
        app.logger.info(f"Getting effect for type: {effect_type}, index: {index}")
        
        # Map effect type from URL to database value
        effect_type_map = {
            'picture': 'pic',
            'text': 'text',
            'solution': 'solution',
            'animation': 'animation'
        }
        
        db_effect_type = effect_type_map.get(effect_type)
        if not db_effect_type:
            app.logger.error(f"Invalid effect type: {effect_type}")
            return jsonify({
                'error': f'Invalid effect type: {effect_type}',
                'valid_types': list(effect_type_map.keys())
            }), 400
        
        # Get the effect from the database
        db = get_db()
        cursor = db.cursor()
        
        # Get the total count of effects for this type
        cursor.execute("SELECT COUNT(*) FROM effects WHERE effect_type = ?", (db_effect_type,))
        total_effects = cursor.fetchone()[0]
        
        if total_effects == 0:
            app.logger.error(f"No effects found for type: {db_effect_type}")
            return jsonify({
                'error': f'No effects found for type: {effect_type}',
                'valid_types': list(effect_type_map.keys())
            }), 404
            
        if index < 0 or index >= total_effects:
            app.logger.error(f"Index {index} out of range (0-{total_effects-1})")
            return jsonify({
                'error': f'Invalid effect index. Must be between 0 and {total_effects-1}',
                'total_effects': total_effects
            }), 400
        
        # Get the effect details
        cursor.execute("""
            SELECT id, name, preview_image, code, effect_type, created_at, updated_at, is_public 
            FROM effects 
            WHERE effect_type = ? 
            LIMIT 1 OFFSET ?
        """, (db_effect_type, index))
        
        effect = cursor.fetchone()
        if not effect:
            app.logger.error(f"No effect found at index {index}")
            return jsonify({
                'error': 'Effect not found',
                'index': index,
                'effect_type': effect_type
            }), 404
            
        # Convert Row object to dict
        effect_dict = dict(effect)
        
        # Add the image path
        effect_dict['image'] = f'Data_pic/previews/{effect_dict["preview_image"]}'
        
        # Add URL type for frontend
        effect_dict['url_type'] = effect_type
        
        return jsonify(effect_dict)
        
    except Exception as e:
        app.logger.error(f"Error getting effect: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'An unexpected error occurred while fetching the effect'
        }), 500

@app.route('/preview/<effect_type>/<int:effect_id>')
def preview_effect(effect_type, effect_id):
    try:
        app.logger.info(f"Getting preview for effect type: {effect_type}, id: {effect_id}")
        
        # Map effect type from URL to database value
        effect_type_map = {
            'picture': 'pic',
            'text': 'text',
            'solution': 'solution',
            'animation': 'animation'
        }
        
        db_effect_type = effect_type_map.get(effect_type)
        if not db_effect_type:
            app.logger.error(f"Invalid effect type: {effect_type}")
            return render_template('error.html', error=f"Invalid effect type. Must be one of: {', '.join(effect_type_map.keys())}"), 400
        
        # Get the effect from the database
        db = get_db()
        cursor = db.cursor()
        
        # Get the effect details
        cursor.execute("""
            SELECT name, preview_image, code, effect_type
            FROM effects 
            WHERE id = ? AND effect_type = ?
        """, (effect_id, db_effect_type))
        
        effect = cursor.fetchone()
        if not effect:
            app.logger.error(f"No effect found with id {effect_id} and type {db_effect_type}")
            return render_template('error.html', error="Effect not found"), 404
            
        # Generate the preview HTML
        style_block = """
        <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f5f5f5;
        }
        .preview-container {
            max-width: 800px;
            width: 100%;
            padding: 20px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        img, video, object {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        </style>
        """
        
        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Preview: {effect['name']}</title>
            {style_block}
        </head>
        <body>
            <div class="preview-container">
                {effect['code']}
            </div>
        </body>
        </html>
        """
        
        return render_template_string(preview_html)
        
    except Exception as e:
        app.logger.error(f"Error generating preview: {str(e)}")
        return render_template('error.html', error="Failed to generate preview"), 500

if __name__ == '__main__':
    app.run(debug=True)
