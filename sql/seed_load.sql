-- Подключаемся к базе
\c Des1

-- Простейшая нагрузка: создаём тестовую таблицу, вставляем, обновляем, удаляем
CREATE TABLE IF NOT EXISTS test_load (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Вставляем 100 строк
INSERT INTO test_load (category)
SELECT 'load_' || generate_series(1, 100);

-- Обновляем часть строк
UPDATE test_load
SET category = 'updated'
WHERE id % 10 = 0;

-- Удаляем 5 случайных строк
DELETE FROM test_load WHERE id IN (SELECT id FROM test_load LIMIT 5);

-- Смотрим активность
SELECT COUNT(*) FROM test_load;
