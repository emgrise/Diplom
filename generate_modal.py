import sqlite3
import os
from datetime import datetime
import shutil

def generate_modal_html():
    # Создаем директорию для кэша, если её нет
    cache_dir = os.path.join('static', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    # Генерируем уникальное имя файла на основе времени
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(cache_dir, f'modal_{timestamp}.html')
    
    # Читаем шаблон modal.html
    with open(os.path.join('static', 'Modal', 'modal.html'), 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('EffectsDB_new.db')
    cursor = conn.cursor()
    
    try:
        # Получаем данные из базы данных
        cursor.execute('SELECT * FROM effects')
        effects = cursor.fetchall()
        
        # Получаем названия колонок
        column_names = [description[0] for description in cursor.description]
        
        # Создаем HTML таблицу с данными
        table_html = '<table class="effects-table">\n'
        table_html += '<thead><tr>'
        for column in column_names:
            table_html += f'<th>{column}</th>'
        table_html += '</tr></thead>\n<tbody>'
        
        for effect in effects:
            table_html += '<tr>'
            for value in effect:
                table_html += f'<td>{value}</td>'
            table_html += '</tr>'
        
        table_html += '</tbody></table>'
        
        # Вставляем таблицу в шаблон
        final_html = template.replace('</body>', f'{table_html}\n</body>')
        
        # Добавляем стили для таблицы
        table_styles = '''
        <style>
            .effects-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .effects-table th, .effects-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .effects-table th {
                background-color: #f5f5f5;
            }
            .effects-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .effects-table tr:hover {
                background-color: #f0f0f0;
            }
        </style>
        '''
        final_html = final_html.replace('</head>', f'{table_styles}\n</head>')
        
        # Сохраняем результат в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        return output_file
        
    finally:
        conn.close()

if __name__ == '__main__':
    output_path = generate_modal_html()
    print(f'Generated modal HTML file: {output_path}') 