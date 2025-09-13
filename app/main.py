# app/main.py
import os
import sqlite3
import requests
import streamlit as st
from db import DB_PATH, get_user_prompts_with_images, init_db, get_predefined_prompts
from auth import signup, login
from prompt_ui import prompt_input_ui 
from tst import prompt_input_ui_test

# تنظیمات اولیه
st.set_page_config(page_title="AI Image Generator", page_icon="🎨")

# اجرای تابع ساخت دیتابیس
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

st.title("🧠 سامانه تولید تصویر با هوش مصنوعی")

# بررسی وضعیت ورود
if "user" not in st.session_state:
    tab1, tab2 = st.tabs(["🔐 ورود", "📝 ثبت‌نام"])
    with tab1:
        login()
    with tab2:
        signup()
else:
    user = st.session_state.user

    # اگر کاربر به صورت tuple ذخیره شده، تبدیلش کن به dict
    if isinstance(user, tuple):
        user = {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "password": user[3]
        }
        st.session_state.user = user

    st.success(f"خوش آمدی {user['name']} 🌟")
    
    # اضافه کردن تب‌های جدید برای ویرایش و انتخاب پرامپت و تاریخچه
    tab3, tab4, tab5, tab6 = st.tabs(["📝 تولید تصویر", "🔄 مدیریت پرامپت‌ها", "📸 هیستوری تصاویر", "📖 راهنما"])
    
    # تب برای تولید تصویر
    with tab3:
        # prompt_input_ui(user['id'])
        prompt_input_ui_test(user['id'])

    
    # تب برای مدیریت پرامپت‌ها
    with tab4:
        st.subheader("📝 مدیریت پرامپت‌ها")
        
        # دریافت پرامپت‌های پیش‌فرض
        predefined = get_predefined_prompts()
        predefined_prompts = [p[1] for p in predefined]
        
        selected = st.selectbox("یکی از پرامپت‌های آماده را انتخاب کن:", predefined_prompts)
        
        # ویرایش پرامپت انتخاب شده
        if selected:
            edited_prompt = st.text_area("ویرایش پرامپت:", selected)
            if st.button("ذخیره تغییرات"):
                for p in predefined:
                    if p[1] == selected:
                        # تغییر پرامپت در دیتابیس
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("UPDATE predefined_prompts SET prompt = ? WHERE id = ?", (edited_prompt, p[0]))
                        conn.commit()
                        conn.close()
                        st.success("تغییرات با موفقیت ذخیره شد!")
                        break
        
        # اضافه کردن پرامپت جدید
        new_prompt = st.text_input("یک پرامپت جدید وارد کنید:")
        if st.button("افزودن پرامپت جدید"):
            if new_prompt:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO predefined_prompts (prompt) VALUES (?)", (new_prompt,))
                conn.commit()
                conn.close()
                st.success("پرامپت جدید با موفقیت اضافه شد!")
            else:
                st.warning("لطفاً پرامپت جدید را وارد کنید.")
    
    # تب برای نمایش تاریخچه پرامپت‌ها
    with tab5:
        st.subheader("📸 هیستوری تصاویر تولیدشده")

        if user.get("id"):
            try:
                history = get_user_prompts_with_images(user["id"])
            except Exception as e:
                st.error(f"خطا در دریافت هیستوری: {e}")
                history = []
        else:
            st.warning("مشکلی در شناسایی کاربر وجود دارد.")
            history = []

        if not history:
            st.info("هنوز هیچ تصویری تولید نکردی.")
        else:
            for prompt, image_url, liked in history:
                st.markdown(f"**📝 پرامپت:** {prompt}")

            try:
                # اگر image_url مسیر لوکال باشه
                if os.path.exists(image_url):
                    with open(image_url, "rb") as f:
                        image_bytes = f.read()
                else:
                    # اگر image_url لینک اینترنتی باشه
                    response = requests.get(image_url)
                    response.raise_for_status()
                    image_bytes = response.content

                st.image(image_bytes, width=256)

                # دکمه دانلود
                st.download_button(
                    label="📥 دانلود تصویر",
                    data=image_bytes,
                    file_name="image.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"❌ خطا در بارگذاری تصویر: {e}")

            # نمایش وضعیت لایک
            if liked == 1:
                st.success("👍 لایک شده")
            elif liked == 0:
                st.warning("👎 دیسلایک شده")
            else:
                st.info("بدون رأی")

                st.markdown("---")
    
    # تب برای راهنما
    with tab6:
        st.subheader("📖 راهنما")
        st.write("""
        خوش آمدید به سامانه تولید تصویر با هوش مصنوعی! در اینجا می‌توانید از پرامپت‌های آماده برای تولید تصاویر استفاده کنید یا خودتان پرامپت جدید وارد کنید.
        
        - در تب "تولید تصویر" می‌توانید با انتخاب یا نوشتن پرامپت، تصویر دلخواه خود را تولید کنید.
        - در تب "مدیریت پرامپت‌ها" می‌توانید پرامپت‌های پیش‌فرض را ویرایش یا اضافه کنید.
        - در تب "تاریخچه پرامپت‌ها" می‌توانید تصاویر تولیدشده و وضعیت لایک/دیسلایک آن‌ها را مشاهده کنید.
        """)
