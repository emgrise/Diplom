from flask import Flask, render_template, g, render_template_string, url_for, request
import sqlite3

app = Flask(__name__)
DATABASE = 'EffectsDB.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Добавить эту строку
    return db

@app.route('/')
def Index():
    return render_template('Index.html')
    

@app.route('/Picture')
def Picture():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT effect_name, preview_image FROM Pic_effects")
    items = [{"description": row[0], "image": row[1]} for row in cursor.fetchall()]
    return render_template('Picture.html', items=items)


@app.route('/Text')
def Text():
    return render_template('Text.html')

@app.route('/Solution')
def Solution():
    return render_template('Solution.html')

@app.route('/Animation')
def Animation():
    return render_template('Animation.html')

@app.route('/modal')
def modal():
    try:
        index = int(request.args.get('index', 0))
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT code FROM Pic_effects LIMIT 1 OFFSET ?", (index,))
        row = cursor.fetchone()
        
        if not row:
            return "Effect not found", 404

        original_code = row[0]
        style_block = """
        <style>
        img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        </style>
        """
    
        if "<head>" in original_code:
            modified_code = original_code.replace("<head>", "<head>" + style_block)
        else:
            # Вставляем <head> вручную
            modified_code = f'''
            <!DOCTYPE html>
            <html>
            <head>{style_block}</head>
            {original_code}
            </html>
            '''

        return render_template_string(modified_code)

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return str(e), 500


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
if __name__ == '__main__':
    app.run(debug=True)
