# setup_database.py
# Versi ini sudah mencakup semua tabel termasuk users, friendships, posts (dengan kolom live stream),
# likes, comments, shares, user_blocks, dan notifications, beserta trigger dan indeks.

import sqlite3
import os

# Nama file database SQLite
DB_FILE = "social_media_app.db"

def create_connection(db_file):
    """ Membuat koneksi ke database SQLite.
        Akan membuat file database jika belum ada.
    Args:
        db_file (str): Path ke file database.
    Returns:
        sqlite3.Connection: Objek koneksi atau None jika gagal.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Berhasil terhubung ke SQLite versi: {sqlite3.sqlite_version}")
        print(f"Database disimpan di: {os.path.abspath(db_file)}")
    except sqlite3.Error as e:
        print(f"Error saat menghubungkan ke database: {e}")
    return conn

def create_tables(conn):
    """ Membuat tabel-tabel yang dibutuhkan dalam database.
    Args:
        conn (sqlite3.Connection): Objek koneksi database.
    """
    if conn is None:
        print("Tidak ada koneksi ke database. Tabel tidak dapat dibuat.")
        return

    # Mengaktifkan foreign key constraints (penting untuk integritas data)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Skema SQL untuk membuat tabel-tabel
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        profile_picture_url TEXT,
        bio TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    sql_create_friendships_table = """
    CREATE TABLE IF NOT EXISTS friendships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACCEPTED')) DEFAULT 'PENDING',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (sender_id, receiver_id)
    );
    """
    
    sql_create_posts_table = """
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT, -- Bisa NULL untuk live stream atau post hanya media
        image_url TEXT,
        video_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_live BOOLEAN DEFAULT FALSE,         -- Untuk fitur live stream
        live_status TEXT,                    -- 'PENDING', 'LIVE', 'ENDED' (NULL jika bukan live)
        stream_playback_url TEXT,            -- URL untuk menonton live stream
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """

    sql_create_likes_table = """
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        UNIQUE (user_id, post_id)
    );
    """

    sql_create_comments_table = """
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        parent_comment_id INTEGER,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
    );
    """

    sql_create_shares_table = """
    CREATE TABLE IF NOT EXISTS shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        original_post_id INTEGER NOT NULL,
        caption TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (original_post_id) REFERENCES posts(id) ON DELETE CASCADE
    );
    """

    sql_create_user_blocks_table = """
    CREATE TABLE IF NOT EXISTS user_blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blocker_id INTEGER NOT NULL, 
        blocked_user_id INTEGER NOT NULL, 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (blocked_user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (blocker_id, blocked_user_id)
    );
    """

    sql_create_notifications_table = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient_user_id INTEGER NOT NULL, 
        actor_user_id INTEGER,             
        type TEXT NOT NULL,                
        target_entity_type TEXT,           
        target_entity_id INTEGER,          
        is_read BOOLEAN DEFAULT FALSE,     
        message TEXT,                      
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recipient_user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """

    # Skema SQL untuk membuat trigger updated_at
    trigger_update_users = """
    CREATE TRIGGER IF NOT EXISTS update_users_updated_at
    AFTER UPDATE ON users
    FOR EACH ROW
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """
    trigger_update_friendships = """
    CREATE TRIGGER IF NOT EXISTS update_friendships_updated_at
    AFTER UPDATE ON friendships
    FOR EACH ROW
    BEGIN
        UPDATE friendships SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """
    trigger_update_posts = """
    CREATE TRIGGER IF NOT EXISTS update_posts_updated_at
    AFTER UPDATE ON posts
    FOR EACH ROW
    BEGIN
        UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """
    trigger_update_comments = """
    CREATE TRIGGER IF NOT EXISTS update_comments_updated_at
    AFTER UPDATE ON comments
    FOR EACH ROW
    BEGIN
        UPDATE comments SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    """

    # Skema SQL untuk membuat indeks
    index_friendships_sender = "CREATE INDEX IF NOT EXISTS idx_friendships_sender_id ON friendships(sender_id);"
    index_friendships_receiver = "CREATE INDEX IF NOT EXISTS idx_friendships_receiver_id ON friendships(receiver_id);"
    index_posts_user = "CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);"
    index_likes_post = "CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id);"
    index_comments_post = "CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);"
    index_shares_original_post = "CREATE INDEX IF NOT EXISTS idx_shares_original_post_id ON shares(original_post_id);"
    index_user_blocks_blocker = "CREATE INDEX IF NOT EXISTS idx_user_blocks_blocker_id ON user_blocks(blocker_id);"
    index_user_blocks_blocked = "CREATE INDEX IF NOT EXISTS idx_user_blocks_blocked_user_id ON user_blocks(blocked_user_id);"
    index_notifications_recipient = "CREATE INDEX IF NOT EXISTS idx_notifications_recipient_id ON notifications(recipient_user_id, is_read, created_at);"
    index_notifications_actor = "CREATE INDEX IF NOT EXISTS idx_notifications_actor_id ON notifications(actor_user_id);"

    try:
        cursor = conn.cursor()
        print("Membuat tabel users...")
        cursor.execute(sql_create_users_table)
        print("Membuat tabel friendships...")
        cursor.execute(sql_create_friendships_table)
        print("Membuat tabel posts (dengan kolom live stream)...") # Pesan diupdate
        cursor.execute(sql_create_posts_table)
        print("Membuat tabel likes...")
        cursor.execute(sql_create_likes_table)
        print("Membuat tabel comments...")
        cursor.execute(sql_create_comments_table)
        print("Membuat tabel shares...")
        cursor.execute(sql_create_shares_table)
        print("Membuat tabel user_blocks...")
        cursor.execute(sql_create_user_blocks_table)
        print("Membuat tabel notifications...")
        cursor.execute(sql_create_notifications_table)

        print("Membuat trigger untuk updated_at...")
        cursor.execute(trigger_update_users)
        cursor.execute(trigger_update_friendships)
        cursor.execute(trigger_update_posts)
        cursor.execute(trigger_update_comments)

        print("Membuat indeks...")
        cursor.execute(index_friendships_sender)
        cursor.execute(index_friendships_receiver)
        cursor.execute(index_posts_user)
        cursor.execute(index_likes_post)
        cursor.execute(index_comments_post)
        cursor.execute(index_shares_original_post)
        cursor.execute(index_user_blocks_blocker)
        cursor.execute(index_user_blocks_blocked)
        cursor.execute(index_notifications_recipient)
        cursor.execute(index_notifications_actor)

        conn.commit()
        print("Semua tabel, trigger, dan indeks berhasil dibuat atau sudah ada.")
    except sqlite3.Error as e:
        print(f"Error saat membuat tabel: {e}")
    finally:
        if cursor:
            cursor.close()

def main():
    # Hapus file DB lama jika ada untuk memastikan skema terbaru (hati-hati!)
    # Jika Anda ingin memastikan skema 'posts' diperbarui dengan kolom live stream,
    # uncomment baris di bawah ini SAAT PERTAMA KALI menjalankan setelah perubahan skema posts.
    # Setelah itu, comment lagi agar data tidak hilang setiap kali dijalankan.
    # if os.path.exists(DB_FILE):
    #     print(f"Menghapus database lama: {DB_FILE} untuk menerapkan skema baru pada 'posts'.")
    #     os.remove(DB_FILE)

    conn = create_connection(DB_FILE)
    if conn is not None:
        create_tables(conn)
        conn.close()
        print("Koneksi database ditutup.")
    else:
        print("Gagal membuat koneksi ke database.")

if __name__ == '__main__':
    main()