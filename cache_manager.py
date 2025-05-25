import os
import sqlite3
from datetime import datetime
import json
from flask import render_template_string

class CacheManager:
    def __init__(self, cache_dir='static/cache', app=None):
        self.cache_dir = cache_dir
        self.cache_index_file = os.path.join(cache_dir, 'cache_index.json')
        self.app = app
        os.makedirs(cache_dir, exist_ok=True)
        self._load_cache_index()

    def _load_cache_index(self):
        self.cache_index = json.load(open(self.cache_index_file, 'r')) if os.path.exists(self.cache_index_file) else {}

    def _save_cache_index(self):
        json.dump(self.cache_index, open(self.cache_index_file, 'w'))

    def generate_html(self, index, effect_type, db_path='EffectsDB_new.db'):
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT code FROM effects WHERE effect_type = ? LIMIT 1 OFFSET ?", (effect_type, index))
                row = cursor.fetchone()
                
                if not row:
                    return None

                
                
                original_code = row[0]
                modified_code = f'''
                <!DOCTYPE html>
                <html>
                <head></head>
                <body>{original_code}</body>
                </html>
                ''' 

                with self.app.app_context():
                    rendered_html = render_template_string(modified_code)

                cache_key = f"effect_{effect_type}_{index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                cache_file = os.path.join(self.cache_dir, f"{cache_key}.html")

                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)

                self.cache_index[f"{effect_type}_{index}"] = {
                    'file': f"{cache_key}.html",
                    'timestamp': datetime.now().isoformat()
                }
                self._save_cache_index()

                return cache_file

        except Exception as e:
            print(f"Error generating HTML: {str(e)}")
            return None

    def get_cached_file(self, index, effect_type):
        cache_key = f"{effect_type}_{index}"
        if cache_key in self.cache_index:
            cache_file = os.path.join(self.cache_dir, self.cache_index[cache_key]['file'])
            if os.path.exists(cache_file):
                return cache_file
        return self.generate_html(index, effect_type)

    def clear_cache(self):
        for file in os.listdir(self.cache_dir):
            if file.endswith('.html'):
                os.remove(os.path.join(self.cache_dir, file))
        self.cache_index = {}
        self._save_cache_index() 