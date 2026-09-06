# Canto Connector — Discovery

**Vendor:** Canto (https://canto.com)  
**API Base URL:** `https://<tenant>.canto.com/api/v1`  
**Authentication:** OAuth 2.0 Bearer Token (App ID / Secret)

## Архитектура API
- **Ключевые сущности:** дерево папок и альбомов (/tree), медиафайлы (изображения/видео/документы), схемы метаданных, порталы дистрибуции
- **Формат обмена данными:** JSON / HTTPS REST.
- **Обработка ошибок:** Стандартные HTTP-коды (400, 401, 403, 404, 429, 500) с типизацией ответа.
- **Тестовая точка проверки подключения:** `GET /api/v1/tree`.
