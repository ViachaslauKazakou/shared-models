-- Инициализация pgvector расширения
-- Этот файл автоматически выполняется при первом запуске контейнера

-- Создаем расширение pgvector если оно еще не существует
CREATE EXTENSION IF NOT EXISTS vector;

-- Проверяем, что расширение установлено
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Инициализация PostgreSQL с pgvector для RAG Service
-- Этот скрипт выполняется при первом запуске контейнера PostgreSQL

-- Создаем индексы для оптимизации векторного поиска
-- (индексы будут созданы после создания таблиц через миграции Alembic)

-- Устанавливаем параметры для оптимизации векторного поиска
ALTER SYSTEM SET shared_preload_libraries = 'vector';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Применяем изменения
SELECT pg_reload_conf();

-- Создаем пользователя для приложения если нужно
-- (используем существующего пользователя docker)

-- Выводим информацию о настройке
\echo 'PostgreSQL с pgvector успешно инициализирован для RAG Service'
\echo 'Доступные расширения:'
SELECT extname, extversion FROM pg_extension;


-- Выводим информацию о базе
\echo 'PostgreSQL with pgvector extension initialized successfully!'
\echo 'Database: postgres'
\echo 'User: docker'
\echo 'Port: 5432 (mapped to 5433 on host)'
