import os
import sqlite3
from datetime import datetime
import hashlib
import json
import re
from urllib.parse import urljoin
from flask import url_for, render_template_string

class CacheManager:
    def __init__(self, cache_dir='static/cache', app=None):
        self.cache_dir = cache_dir
        self.cache_index_file = os.path.join(cache_dir, 'cache_index.json')
        self.app = app
        os.makedirs(cache_dir, exist_ok=True)
        self._load_cache_index()

    def _load_cache_index(self):
        if os.path.exists(self.cache_index_file):
            with open(self.cache_index_file, 'r') as f:
                self.cache_index = json.load(f)
        else:
            self.cache_index = {}

    def _save_cache_index(self):
        with open(self.cache_index_file, 'w') as f:
            json.dump(self.cache_index, f)

    def _generate_cache_key(self, index, effect_type):
        # Создаем уникальный ключ на основе индекса, типа эффекта и времени
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"effect_{effect_type}_{index}_{timestamp}"

    def _process_template(self, html_content):
        # Обрабатываем шаблоны url_for
        url_for_pattern = r'\{\{\s*url_for\([\'"]static[\'"],\s*filename=[\'"]([^\'"]+)[\'"]\)\s*\}\}'
        
        def replace_url_for(match):
            filename = match.group(1)
            return f'/static/{filename}'
        
        return re.sub(url_for_pattern, replace_url_for, html_content)

    def _fix_image_paths(self, html_content):
        # Сначала обрабатываем шаблоны
        html_content = self._process_template(html_content)
        
        # Находим все теги img и их атрибуты src
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        
        def replace_path(match):
            img_tag = match.group(0)
            src = match.group(1)
            
            # Если путь уже абсолютный или это URL, оставляем как есть
            if src.startswith(('http://', 'https://', '/')):
                return img_tag
            
            # Преобразуем относительный путь в абсолютный
            new_src = urljoin('/static/', src)
            return img_tag.replace(src, new_src)
        
        return re.sub(img_pattern, replace_path, html_content)

    def generate_html(self, index, effect_type, db_path='EffectsDB_new.db'):
        try:
            # Подключаемся к базе данных
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Получаем данные эффекта
            cursor.execute("SELECT code FROM effects WHERE effect_type = ? LIMIT 1 OFFSET ?", (effect_type, index))
            row = cursor.fetchone()
            
            if not row:
                return None

            # Читаем шаблон modal.html
            with open(os.path.join('static', 'Modal', 'modal.html'), 'r', encoding='utf-8') as f:
                template = f.read()

            # Генерируем HTML
            original_code = row[0]
            style_block = """
            <style>
            img, video, object {
                object-fit: contain;
                width: 100%;
                height: 100%;
            }
            div {
                font-size: 50px;
                font-weight: bold;
                text-align: center;
            }
            </style>
            """
            
            if "<head>" in original_code:
                modified_code = original_code.replace("<head>", "<head>" + style_block)
            else:
                modified_code = f'''
                <!DOCTYPE html>
                <html>
                <head>{style_block}</head>
                <body>
                {original_code} 
                </body>
                </html>
                '''

            # Рендерим HTML с использованием контекста приложения
            with self.app.app_context():
                rendered_html = render_template_string(modified_code)

            # Генерируем имя файла для кэша
            cache_key = self._generate_cache_key(index, effect_type)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.html")

            # Сохраняем в кэш
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(rendered_html)

            # Обновляем индекс кэша
            self.cache_index[f"{effect_type}_{index}"] = {
                'file': f"{cache_key}.html",
                'timestamp': datetime.now().isoformat()
            }
            self._save_cache_index()

            return cache_file

        except Exception as e:
            print(f"Error generating HTML: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def get_cached_file(self, index, effect_type):
        # Проверяем, есть ли файл в кэше
        cache_key = f"{effect_type}_{index}"
        if cache_key in self.cache_index:
            cache_file = os.path.join(self.cache_dir, self.cache_index[cache_key]['file'])
            if os.path.exists(cache_file):
                return cache_file
        
        # Если файла нет в кэше или он устарел, генерируем новый
        return self.generate_html(index, effect_type)

    def clear_cache(self):
        # Удаляем все файлы кэша
        for file in os.listdir(self.cache_dir):
            if file.endswith('.html'):
                os.remove(os.path.join(self.cache_dir, file))
        # Очищаем индекс
        self.cache_index = {}
        self._save_cache_index() 