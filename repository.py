import sqlite3
import os
from typing import List, Optional
from models import Movie, Category

class MovieRepository:
    def __init__(self, db_name: str = "movies.db"):
        # Locate database file beside application modules
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_database()

    def _initialize_database(self) -> None:
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        self.conn.commit()

        # Seed default categories if missing
        default_categories = ["Animation", "Comedy", "History", "Action", "Horror", "Sci-Fi"]
        for cat in default_categories:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
        self.conn.commit()

        # Consolidate duplicate categories and preserve references
        self._deduplicate_categories(cursor)

        # Seed 30 sample movies if the movies table is empty
        cursor.execute("SELECT COUNT(*) FROM movies")
        if cursor.fetchone()[0] == 0:
            sample_movies = [
                # Animation (ID: 1)
                ("Toy Story", 1995, 81, 1),
                ("Spirited Away", 2001, 125, 1),
                ("Spider-Man: Into the Spider-Verse", 2018, 117, 1),
                ("The Lion King", 1994, 88, 1),
                ("Coco", 2017, 105, 1),
                
                # Comedy (ID: 2)
                ("Superbad", 2007, 113, 2),
                ("Step Brothers", 2008, 98, 2),
                ("Groundhog Day", 1993, 101, 2),
                ("Anchorman: The Legend of Ron Burgundy", 2004, 94, 2),
                ("Bridesmaids", 2011, 125, 2),
                
                # History (ID: 3)
                ("Schindler's List", 1993, 195, 3),
                ("Saving Private Ryan", 1998, 169, 3),
                ("1917", 2019, 119, 3),
                ("Braveheart", 1995, 178, 3),
                ("Gladiator", 2000, 155, 3),
                
                # Action (ID: 4)
                ("Mad Max: Fury Road", 2015, 120, 4),
                ("Die Hard", 1988, 132, 4),
                ("John Wick", 2014, 101, 4),
                ("The Dark Knight", 2008, 152, 4),
                ("Terminator 2: Judgment Day", 1991, 137, 4),
                
                # Horror (ID: 5)
                ("The Shining", 1980, 144, 5),
                ("Get Out", 2017, 104, 5),
                ("Hereditary", 2018, 127, 5),
                ("The Conjuring", 2013, 112, 5),
                ("A Quiet Place", 2018, 90, 5),
                
                # Sci-Fi (ID: 6)
                ("Interstellar", 2014, 169, 6),
                ("Inception", 2010, 148, 6),
                ("Blade Runner 2049", 2017, 164, 6),
                ("The Matrix", 1999, 136, 6),
                ("Arrival", 2016, 116, 6)
            ]
            cursor.executemany("""
                INSERT INTO movies (title, year, duration, category_id)
                VALUES (?, ?, ?, ?)
            """, sample_movies)
            self.conn.commit()

    def _deduplicate_categories(self, cursor) -> None:
        cursor.execute("SELECT name, GROUP_CONCAT(id) as ids FROM categories GROUP BY name HAVING COUNT(*) > 1")
        duplicates = cursor.fetchall()
        for dup in duplicates:
            name = dup["name"]
            ids = [int(i) for i in dup["ids"].split(",")]
            retained_id = ids[0]
            duplicate_ids = ids[1:]
            
            for dup_id in duplicate_ids:
                cursor.execute("UPDATE movies SET category_id = ? WHERE category_id = ?", (retained_id, dup_id))
                cursor.execute("DELETE FROM categories WHERE id = ?", (dup_id,))
        self.conn.commit()

    def get_categories(self) -> List[Category]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return [Category(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    def get_all_movies(self) -> List[Movie]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.id, m.title, m.year, m.duration, m.category_id, c.name as category_name
            FROM movies m
            JOIN categories c ON m.category_id = c.id
            ORDER BY m.id ASC
        """)
        return [self._row_to_movie(row) for row in cursor.fetchall()]

    def get_movies_by_category(self, category_id: int) -> List[Movie]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.id, m.title, m.year, m.duration, m.category_id, c.name as category_name
            FROM movies m
            JOIN categories c ON m.category_id = c.id
            WHERE m.category_id = ?
            ORDER BY m.id ASC
        """, (category_id,))
        return [self._row_to_movie(row) for row in cursor.fetchall()]

    def get_movies_by_year(self, year: int) -> List[Movie]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.id, m.title, m.year, m.duration, m.category_id, c.name as category_name
            FROM movies m
            JOIN categories c ON m.category_id = c.id
            WHERE m.year = ?
            ORDER BY m.id ASC
        """, (year,))
        return [self._row_to_movie(row) for row in cursor.fetchall()]

    def search_movies_by_title(self, title_query: str) -> List[Movie]:
        cursor = self.conn.cursor()
        search_pattern = f"%{title_query}%"
        cursor.execute("""
            SELECT m.id, m.title, m.year, m.duration, m.category_id, c.name as category_name
            FROM movies m
            JOIN categories c ON m.category_id = c.id
            WHERE m.title LIKE ?
            ORDER BY m.id ASC
        """, (search_pattern,))
        return [self._row_to_movie(row) for row in cursor.fetchall()]

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.id, m.title, m.year, m.duration, m.category_id, c.name as category_name
            FROM movies m
            JOIN categories c ON m.category_id = c.id
            WHERE m.id = ?
        """, (movie_id,))
        row = cursor.fetchone()
        return self._row_to_movie(row) if row else None

    def add_movie(self, title: str, year: int, duration: int, category_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO movies (title, year, duration, category_id)
            VALUES (?, ?, ?, ?)
        """, (title, year, duration, category_id))
        self.conn.commit()

    def delete_movie(self, movie_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def category_exists(self, category_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM categories WHERE id = ?", (category_id,))
        return cursor.fetchone() is not None

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def _row_to_movie(row) -> Movie:
        return Movie(
            id=row["id"],
            title=row["title"],
            year=row["year"],
            duration=row["duration"],
            category_id=row["category_id"],
            category_name=row["category_name"]
        )