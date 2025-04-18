# Переписываем код: заменяем src="Windows_Logo.jpg" на src="{{ url_for('static', filename='pic/Windows_Logo.jpg') }}"
updated_data = []

for effect_name, preview_image, code in new_data:
    updated_code = code.replace(
        'src="Windows_Logo.jpg"',
        'src="{{ url_for(\'static\', filename=\'pic/Windows_Logo.jpg\') }}"'
    )
    updated_data.append((effect_name, preview_image, updated_code))

# Удаляем старую таблицу и создаём заново
cursor.execute("DROP TABLE IF EXISTS Pic_effects;")

cursor.execute("""
CREATE TABLE Pic_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    effect_name TEXT NOT NULL,
    preview_image TEXT NOT NULL,
    code TEXT NOT NULL
);
""")

# Вставляем обновлённые данные
cursor.executemany("INSERT INTO Pic_effects (effect_name, preview_image, code) VALUES (?, ?, ?);", updated_data)
conn.commit()

# Проверим, что всё записано
cursor.execute("SELECT * FROM Pic_effects;")
refreshed_rows = cursor.fetchall()

refreshed_rows
