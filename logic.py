import sqlite3
from config import DATABASE

skills = [(_,) for _ in (['Python', 'SQL', 'API', 'Telegram'])]
statuses = [(_,) for _ in (['На этапе проектирования',
                           'В процессе разработки',
                           'Разработан. Готов к использованию.',
                           'Обновлен',
                           'Завершен. Не поддерживается',])]


class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS Status (
                    status_id INTEGER PRIMARY KEY,
                    status_name VARCHAR NOT NULL UNIQUE
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS Project (
                    project_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    project_name VARCHAR NOT NULL,
                    description TEXT,
                    url VARCHAR,
                    status_id INTEGER,
                    FOREIGN KEY (status_id) REFERENCES Status (status_id)
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS Skill (
                    skill_id INTEGER PRIMARY KEY,
                    skill_name VARCHAR NOT NULL UNIQUE
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS ProjectSkill (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    skill_id INTEGER,
                    FOREIGN KEY (project_id) REFERENCES Project (project_id),
                    FOREIGN KEY (skill_id) REFERENCES Skill (skill_id),
                    UNIQUE(project_id, skill_id)
                )
            ''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __execute(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(sql, data)
            conn.commit()

    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    # ==================== СПРАВОЧНИКИ ====================

    def default_insert(self):
        self.__executemany('INSERT OR IGNORE INTO Skill (skill_name) VALUES (?)', skills)
        self.__executemany('INSERT OR IGNORE INTO Status (status_name) VALUES (?)', statuses)

    def add_skill(self, skill_name):
        self.__execute('INSERT OR IGNORE INTO Skill (skill_name) VALUES (?)', (skill_name,))

    def update_skill(self, skill_id, new_name):
        self.__execute('UPDATE Skill SET skill_name = ? WHERE skill_id = ?', (new_name, skill_id))

    def delete_skill_from_dict(self, skill_id):
        self.__execute('DELETE FROM ProjectSkill WHERE skill_id = ?', (skill_id,))
        self.__execute('DELETE FROM Skill WHERE skill_id = ?', (skill_id,))

    def add_status(self, status_name):
        self.__execute('INSERT OR IGNORE INTO Status (status_name) VALUES (?)', (status_name,))

    def update_status(self, status_id, new_name):
        self.__execute('UPDATE Status SET status_name = ? WHERE status_id = ?', (new_name, status_id))

    def delete_status(self, status_id):
        used = self.__select_data('SELECT COUNT(*) FROM Project WHERE status_id = ?', (status_id,))[0][0]
        if used > 0:
            raise ValueError(f"Нельзя удалить статус {status_id}: он используется в {used} проекте(ах)")
        self.__execute('DELETE FROM Status WHERE status_id = ?', (status_id,))

    # ==================== ПРОЕКТЫ ====================

    def insert_project(self, data):
        # data: [(user_id, project_name, description, url, status_id)]
        sql = '''INSERT INTO Project (user_id, project_name, description, url, status_id)
                 VALUES (?, ?, ?, ?, ?)'''
        self.__executemany(sql, data)

    def update_projects(self, param, data):
        # data: (новое_значение, project_name, user_id)
        allowed = {'project_name', 'description', 'url', 'status_id'}
        if param not in allowed:
            raise ValueError(f"Нельзя обновлять поле '{param}'. Разрешены: {allowed}")
        self.__executemany(
            f'UPDATE Project SET {param} = ? WHERE project_name = ? AND user_id = ?', [data]
        )

    def delete_project(self, user_id, project_id):
        self.__execute('DELETE FROM ProjectSkill WHERE project_id = ?', (project_id,))
        self.__execute('DELETE FROM Project WHERE user_id = ? AND project_id = ?', (user_id, project_id))

    # ==================== СВЯЗИ ====================

    def insert_skill(self, user_id, project_name, skill):
        result = self.__select_data(
            'SELECT project_id FROM Project WHERE project_name = ? AND user_id = ?',
            (project_name, user_id)
        )
        if not result:
            raise ValueError(f"Проект '{project_name}' не найден")
        project_id = result[0][0]

        skill_result = self.__select_data(
            'SELECT skill_id FROM Skill WHERE skill_name = ?', (skill,)
        )
        if not skill_result:
            raise ValueError(f"Навык '{skill}' не найден в справочнике")
        skill_id = skill_result[0][0]

        self.__execute(
            'INSERT OR IGNORE INTO ProjectSkill (project_id, skill_id) VALUES (?, ?)',
            (project_id, skill_id)
        )

    def delete_skill(self, project_id, skill_id):
        self.__execute(
            'DELETE FROM ProjectSkill WHERE skill_id = ? AND project_id = ?',
            (skill_id, project_id)
        )

    # ==================== ПОЛУЧЕНИЕ ДАННЫХ ====================

    def get_statuses(self):
        # [(status_id, status_name), ...]
        return self.__select_data('SELECT status_id, status_name FROM Status ORDER BY status_id')

    def get_status_id(self, status_name):
        res = self.__select_data('SELECT status_id FROM Status WHERE status_name = ?', (status_name,))
        return res[0][0] if res else None

    def get_projects(self, user_id):
        # Порядок колонок: 0 project_id, 1 user_id, 2 project_name, 3 description, 4 url, 5 status_id
        return self.__select_data(
            '''SELECT project_id, user_id, project_name, description, url, status_id
               FROM Project
               WHERE user_id = ?
               ORDER BY project_id''',
            (user_id,)
        )

    def get_project_id(self, project_name, user_id):
        res = self.__select_data(
            'SELECT project_id FROM Project WHERE project_name = ? AND user_id = ?',
            (project_name, user_id)
        )
        if not res:
            raise ValueError(f"Проект '{project_name}' не найден")
        return res[0][0]

    def get_skills(self):
        # [(skill_id, skill_name), ...]
        return self.__select_data('SELECT skill_id, skill_name FROM Skill ORDER BY skill_id')

    def get_project_skills(self, project_name, user_id):
        res = self.__select_data('''
            SELECT s.skill_name
            FROM Project p
            JOIN ProjectSkill ps ON p.project_id = ps.project_id
            JOIN Skill s ON s.skill_id = ps.skill_id
            WHERE p.project_name = ? AND p.user_id = ?
            ORDER BY s.skill_name
        ''', (project_name, user_id))
        return ', '.join([x[0] for x in res]) if res else ''

    def get_project_info(self, user_id, project_name):
        return self.__select_data('''
            SELECT p.project_name, p.description, p.url, s.status_name
            FROM Project p
            JOIN Status s ON s.status_id = p.status_id
            WHERE p.project_name = ? AND p.user_id = ?
        ''', (project_name, user_id))

    def get_projects_by_status(self, status_name):
        return self.__select_data('''
            SELECT p.project_id, p.user_id, p.project_name, p.description, p.url
            FROM Project p
            JOIN Status s ON s.status_id = p.status_id
            WHERE s.status_name = ?
        ''', (status_name,))


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()