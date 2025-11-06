# استخدم Python 3.10 لتوافق أفضل مع مكتبات Binance وFastAPI
FROM python:3.10

# أنشئ مستخدم عادي لتشغيل التطبيق
RUN useradd -m user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# اجعل مجلد العمل الرئيسي هو /app
WORKDIR /app

# انسخ ملفات المتطلبات
COPY --chown=user:user ./requirements.txt requirements.txt

# ثبّت المكتبات المطلوبة
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# انسخ الكود الأساسي للتطبيق
COPY --chown=user:user ./app.py /app/app.py

# شغّل التطبيق عبر Uvicorn (من FastAPI)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
