# Canto Connector — Auth & Credentials Standard

**Compliance:** AUTH_AND_CREDENTIALS_STANDARD.md (B1–B10)

## Схема аутентификации
- **Метод:** OAuth 2.0 Bearer Token (App ID / Secret)
- **Хранение:** Секреты сохраняются изолированно в хранилище секретов платформы Imperal.
- **Валидация:** При сохранении ключа выполняется тестовый запрос `GET /api/v1/tree`.
- **Отключение:** Удаление локальных ключей без воздействия на аккаунт вендора.
