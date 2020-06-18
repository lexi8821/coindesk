import os
import sqlite3

DB = 'coindesk.sqlite'

class ContentError(Exception):
    pass

class Handler:
    def __init__(self, db_file=DB):
        self.db_file = db_file
        if not os.path.exists(self.db_file):
            self.create_tables()
        else:
            self.conn = self.create_connection()
            self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def create_connection(self):
        conn = None
        conn = sqlite3.connect(self.db_file)
        return conn

    def create_tables(self):
        sql_create_table_authors = """ CREATE TABLE IF NOT EXISTS articles (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    title text,
                                    author text,
                                    published date,
                                    updated date,
                                    tags text,
                                    link text,
                                    content text
                                    );"""
        self.conn = self.create_connection()
        self.cur = self.conn.cursor()
        self.cur.execute(sql_create_table_authors)
        self.conn.commit()

    def check_article(self, article):
        sql_check_article = """ SELECT id FROM articles WHERE title=? """
        self.cur.execute(sql_check_article, (article['title'],))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return None

    def insert_article(self, article):
        sql_insert_article = """ INSERT INTO articles (title, author, published,
            updated, tags, link, content) VALUES (?,?,?,?,?,?,?) """
        self.cur.execute(sql_insert_article, (article['title'], article['author'],
            article['published'], article['updated'], article['tags'], article['link'],
            article['text']))
        self.conn.commit()
        return self.cur.lastrowid

    def get_article(self, id):
        sql_get_article_by_id = """ SELECT title, author, published, updated,
            tags, link, content FROM articles WHERE id=? """
        self.cur.execute(sql_get_article_by_id, (id,))
        return self.cur.fetchone()

    def get_ids(self):
        sql_get_ids = """ SELECT id FROM articles """
        self.cur.execute(sql_get_ids)
        result = self.cur.fetchall()
        if result:
            return [i[0] for i in result]

    def get_link_by_id(self, id):
        sql_get_link = """ SELECT link FROM articles WHERE id=? """
        self.cur.execute(sql_get_link, (id,))
        result = self.cur.fetchone()
        if result:
            return result[0]

    def update_content_by_id(self, id, content):
        sql_update_content = """ UPDATE articles SET content=? WHERE id=? """
        self.cur.execute(sql_update_content, (content, id))
        self.conn.commit()

    def get_content_by_id(self, id):
        sql_get_content = """ SELECT content FROM articles WHERE id=? """
        self.cur.execute(sql_get_content, (id,))
        result = self.cur.fetchone()
        if result:
            return result[0]
