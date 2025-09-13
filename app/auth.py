# app/auth.py
import streamlit as st
import re
from db import add_user, get_user_by_email
from utils import hash_password, check_password


# تابع بررسی فرمت ایمیل
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


# فرم ثبت‌نام
def signup():
    st.subheader("📋 ثبت‌نام")

    name = st.text_input("نام کامل", key="signup_name")
    email = st.text_input("ایمیل", key="signup_email")
    password = st.text_input("رمز عبور", type="password", key="signup_password")
    confirm = st.text_input("تکرار رمز عبور", type="password", key="signup_confirm")

    if st.button("ثبت‌نام", key="signup_button"):
        if not name or not email or not password or not confirm:
            st.error("لطفاً تمام فیلدها را پر کنید.")
        elif password != confirm:
            st.error("رمز عبور و تکرار آن یکسان نیست.")
        elif len(password) < 6:
            st.error("رمز عبور باید حداقل ۶ کاراکتر باشد.")
        elif not is_valid_email(email):
            st.error("فرمت ایمیل وارد شده معتبر نیست.")
        else:
            # بررسی تکراری بودن ایمیل
            existing_user = get_user_by_email(email)
            if existing_user:
                st.error("این ایمیل قبلاً ثبت شده است.")
            else:
                hashed = hash_password(password)
                success = add_user(name, email, hashed)
                if success:
                    st.success("✅ ثبت‌نام با موفقیت انجام شد. اکنون وارد شوید.")
                else:
                    st.error("مشکلی در ثبت‌نام پیش آمده است.")


# فرم ورود
def login():
    st.subheader("🔐 ورود")

    email = st.text_input("ایمیل", key="login_email")
    password = st.text_input("رمز عبور", type="password", key="login_password")

    if st.button("ورود", key="login_button"):
        if not email or not password:
            st.error("لطفاً ایمیل و رمز عبور را وارد کنید.")
        elif not is_valid_email(email):
            st.error("فرمت ایمیل وارد شده معتبر نیست.")
        else:
            user = get_user_by_email(email)
            if user:
                if check_password(password, user[3]):  # ستون ۳: رمز عبور هش‌شده
                    st.session_state.user = {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2]
                    }
                    st.success(f"🎉 خوش آمدی {user[1]} 👋")
                else:
                    st.error("رمز عبور اشتباه است.")
            else:
                st.error("ایمیل وجود ندارد.")
