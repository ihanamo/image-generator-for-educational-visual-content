# app/db.py
import sqlite3
from pathlib import Path


DB_PATH = Path("data/users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # جدول کاربران
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # جدول پرامپت‌های آماده
    c.execute('''
        CREATE TABLE IF NOT EXISTS predefined_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL
        )
    ''')

    # جدول پرامپت‌های کاربران به همراه تصویر و وضعیت لایک
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            like_status INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# =====================
# User Methods
# =====================

def add_user(name, email, hashed_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                  (name, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user


# =====================
# User Prompt Methods
# =====================

def add_user_prompt(user_id, prompt, image_url=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO user_prompts (user_id, prompt, image_url)
        VALUES (?, ?, ?)
    ''', (user_id, prompt, image_url))
    conn.commit()
    conn.close()

def get_user_prompts(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt, image_url, like_status, created_at FROM user_prompts WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    prompts = c.fetchall()
    conn.close()
    return prompts

def update_prompt_image_url(prompt_id, image_url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE user_prompts SET image_url = ? WHERE id = ?", (image_url, prompt_id))
    conn.commit()
    conn.close()

def set_prompt_like_status(prompt_id, liked):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE user_prompts SET like_status = ? WHERE id = ?", (liked, prompt_id))
    conn.commit()
    conn.close()

def get_user_prompts_with_images(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # c.execute("SELECT prompt, image_url, like_status FROM user_prompts WHERE user_id = ? AND image_url IS NOT NULL ORDER BY id DESC", (user_id,))
    c.execute("SELECT prompt, image_url, like_status FROM user_prompts WHERE user_id = ?", (user_id,))
    prompts = c.fetchall()
    conn.close()
    return prompts


# =====================
# Predefined Prompt Methods
# =====================

def add_predefined_prompts():
    predefined_prompts = [
        "A beautifully illustrated scene depicting a young person standing at the edge of a bright and peaceful garden, symbolizing the rewards of faith and righteousness. The scene conveys a sense of serenity and divine guidance. Inspired by the phrase: «إِنَّ اللَّهَ مَعَ الَّذِينَ اتَّقَوْا وَالَّذِينَ هُمْ مُحْسِنُونَ» (God is with those who fear Him and do good deeds). The atmosphere is warm and spiritually uplifting.",
        "An artistic representation of a balanced golden scale floating in the sky, symbolizing divine justice. On one side of the scale, a rich man, and on the other side, a poor man, showing that justice does not favor status. The background features glowing clouds, representing divine fairness. Inspired by the phrase: «إِنَّ اللَّهَ يَأْمُرُ بِالْعَدْلِ وَالْإِحْسَانِ» (God commands justice and kindness).",
        "A thought-provoking digital painting of a man walking on a path made of his own actions—good deeds forming a golden road and bad deeds forming a dark and broken one. The man must choose his direction. Inspired by the verse: «فَمَن يَعْمَلْ مِثْقَالَ ذَرَّةٍ خَيْرًا يَرَهُ وَمَن يَعْمَلْ مِثْقَالَ ذَرَّةٍ شَرًّا يَرَهُ» (Whoever does an atom’s weight of good shall see it, and whoever does an atom’s weight of evil shall see it).",
        "An educational infographic illustrating a logical syllogism. The first box contains a general statement ('All humans are mortal'). The second box presents a specific example ('Socrates is human'). The final box concludes ('Therefore, Socrates is mortal'). The design is clean and modern, making it easy to understand.",
        "A humorous yet educational comic strip showing a man claiming: 'This book is true because it says it is true.' The next panel features a confused student asking, 'But how do you know it's true?' The final panel repeats the same claim, emphasizing the circular reasoning fallacy.",
        "A digital illustration showing two doors: one labeled 'This door is false' and the other labeled 'The previous door is true.' The image visually represents the paradox of self-referential statements, with an intriguing and thought-provoking artistic style.",
        "A detailed and symbolic digital illustration that visually represents the concept of «[your concept]». For example, if the concept is ‘truth’, show a person standing confidently in a spotlight while surrounded by shadows of lies. The style should be clear and educational, using visual metaphors to help students intuitively understand the meaning. Use soft colors, clear outlines, and maintain cultural appropriateness for use in an Islamic high school context. The image should be emotionally engaging but easy to interpret, with no distracting elements.",
        "An artistic and metaphorical scene that represents the abstract idea of «[your concept]». For instance, to depict ‘patience’, show a person calmly sitting in a storm while holding an umbrella with light shining through. The overall tone should be inspirational and serene. Use symbolic elements like light, path, scales, or nature. Ensure the composition is simple, with one or two main characters, and no chaotic background. This image should be suitable for educational and moral storytelling in a religious context.",
        "An educational infographic visually explaining the relationship between «[first concept]» and «[second concept]». Use arrows, diagrams, and labeled blocks to show the connection logically. For example, link ‘free will’ to ‘responsibility’. The layout should be horizontal with clear flow, using friendly icons and contrasting colors. Make the text areas minimal and the visuals the main element. Suitable for classroom presentation or textbook illustration.",
        "A conceptual digital illustration showing a thought-provoking situation related to «[your topic]». For example, illustrate a person facing two paths labeled ‘easy’ and ‘right’, standing confused at a crossroad in a foggy forest. Use a semi-realistic or cartoonish style. The setting should trigger reflective thinking, inviting students to discuss the meaning. Background should be calm and clean, avoiding overwhelming details. Best used in ethics, philosophy, or logic class.",
        "An image inspired by the following sentence from a school textbook: «[insert sentence]». The image should visually interpret this sentence for high school students using symbolic and educational elements. The image must be clear, respectful, and visually aligned with school materials. Use clean design, moderate brightness, and focus on message clarity.",
        "A digital illustration showing two people in a calm and respectful conversation about the topic of «[your topic]». One person should be holding a book, the other pointing at a whiteboard with a logical diagram. The scene is set in a classroom or study room. Expressions should show focus and cooperation. Include elements like diagrams or flowcharts subtly in the background. Style: semi-realistic, educational, culturally appropriate.",
        "A warm and emotional scene that shows the positive outcome of practicing «[moral value]», such as honesty, responsibility, or generosity. For example, show a student helping a classmate pick up their fallen books, while others smile in approval. Use warm lighting and expressive body language. The image should encourage empathy and positive behavior. Avoid cliché or overly symbolic imagery—focus on realistic, relatable actions in school or home settings.",
        "An educational split-scene image that contrasts two different paths related to «[topic]». On the left, show the consequences of the wrong choice (e.g., confusion, isolation), and on the right, the benefits of the right choice (e.g., peace, success, connection). The two sides should be visually balanced but clearly different in color tone and emotional atmosphere. The central character should appear in both sides, representing the result of their decision.",
        "A warm and emotional scene that shows the positive outcome of practicing «[moral value]». Use warm lighting and expressive body language. The image should encourage empathy and positive behavior. Avoid cliché or overly symbolic imagery—focus on realistic, relatable actions in school or home settings.",
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for prompt in predefined_prompts:
        cursor.execute("INSERT INTO predefined_prompts (prompt) VALUES (?)", (prompt,))
    conn.commit()
    conn.close()

def get_predefined_prompts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt FROM predefined_prompts")
    prompts = c.fetchall()
    conn.close()
    return prompts

def get_predefined_prompt_by_id(prompt_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt FROM predefined_prompts WHERE id = ?", (prompt_id,))
    result = c.fetchone()
    conn.close()
    return result


def get_last_prompt_id(user_id, prompt, image_url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id FROM user_prompts
        WHERE user_id = ? AND prompt = ? AND image_url = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (user_id, prompt, image_url))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
