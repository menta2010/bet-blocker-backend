from app.config import settings

def test_env():
    print("🔧 SMTP_HOST:", settings.SMTP_HOST)
    print("📧 ADMIN_EMAIL:", settings.ADMIN_EMAIL)
    print("🔐 SMTP_USER:", settings.SMTP_USER)
    print("🧪 Tudo ok com o carregamento do .env!")

if __name__ == "__main__":
    test_env()