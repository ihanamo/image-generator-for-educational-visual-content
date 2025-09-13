# app/prompt_ui.py
import streamlit as st
import requests
import replicate
import os
from db import add_user_prompt, get_last_prompt_id, get_predefined_prompts, set_prompt_like_status

# 👇 تنظیم توکن برای replicate
os.environ["REPLICATE_API_TOKEN"] = "heheh"
replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def prompt_input_ui(user_id):
    st.subheader("📝 تولید تصویر با هوش مصنوعی")

    # دریافت پرامپت‌های آماده از دیتابیس
    predefined = get_predefined_prompts()
    predefined_prompts = [p[1] for p in predefined]

    # انتخاب یا نوشتن پرامپت
    selected = st.selectbox("یا یکی از پرامپت‌های آماده رو انتخاب کن:", [""] + predefined_prompts)
    prompt = st.text_area("یا خودت یه پرامپت بنویس:", selected if selected else "")

    if st.button("تولید تصویر"):
        if not prompt.strip():
            st.warning("لطفاً یک پرامپت وارد کن.")
            return

        with st.spinner("در حال تولید تصویر..."):
            try:
                output = replicate.run(
                    "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                    input={
                        "prompt": prompt,
                        "width": 1024,
                        "height": 1024
                    }
                )
                image_url = output[0]  # خروجی یک لیست با یک URL است

                # ذخیره‌سازی پرامپت کاربر
                add_user_prompt(user_id, prompt, image_url)
                prompt_id = get_last_prompt_id(user_id, prompt, image_url)

                # ذخیره در session_state
                st.session_state["generated_image"] = image_url
                st.session_state["current_prompt"] = prompt

            except Exception as e:
                st.error(f"❌ خطا در تولید تصویر: {e}")
                return

        st.success("✅ تصویر با موفقیت تولید شد!")
        st.image(image_url)

        # دکمه دانلود
        image_bytes = requests.get(image_url, timeout=30).content
        st.download_button(
            label="📥 دانلود تصویر",
            data=image_bytes,
            file_name="generated_image.png",
            mime="image/png"
        )

        # لایک / دیسلایک
        col1, col2 = st.columns(2)
        # with col1:
        #     if st.button("👍 لایک"):
        #         set_prompt_like_status(image_url, 1)
        #         st.success("تصویر لایک شد!")
        # with col2:
        #     if st.button("👎 دیسلایک"):
        #         set_prompt_like_status(image_url, 0)
        #         st.success("تصویر دیسلایک شد!")


        if prompt_id:
            with col1:
                if st.button("👍 لایک"):
                    set_prompt_like_status(prompt_id, 1)
                    st.success("تصویر لایک شد!")
            with col2:
                if st.button("👎 دیسلایک"):
                    set_prompt_like_status(prompt_id, 0)
                    st.success("تصویر دیسلایک شد!")
