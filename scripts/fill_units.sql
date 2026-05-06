BEGIN;

-- Дополняем enum новыми категориями, если их ещё нет.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_enum e
        JOIN pg_type t ON t.oid = e.enumtypid
        WHERE t.typname = 'unitcategoryenum'
          AND e.enumlabel = 'TIME'
    ) THEN
        ALTER TYPE unitcategoryenum ADD VALUE 'TIME';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_enum e
        JOIN pg_type t ON t.oid = e.enumtypid
        WHERE t.typname = 'unitcategoryenum'
          AND e.enumlabel = 'ELECTRICITY'
    ) THEN
        ALTER TYPE unitcategoryenum ADD VALUE 'ELECTRICITY';
    END IF;
END $$;

WITH seed_units(category, name, short_name, conversion_factor, is_base) AS (
    VALUES
        -- QUANTITY
        ('QUANTITY', 'Штуки', 'шт', 1.0, true),
        ('QUANTITY', 'Упаковка', 'упак', 1.0, false),
        ('QUANTITY', 'Комплект', 'компл', 1.0, false),

        -- WEIGHT (base: kg)
        ('WEIGHT', 'Килограммы', 'кг', 1.0, true),
        ('WEIGHT', 'Граммы', 'г', 0.001, false),
        ('WEIGHT', 'Миллиграммы', 'мг', 0.000001, false),
        ('WEIGHT', 'Центнеры', 'ц', 100.0, false),
        ('WEIGHT', 'Тонны', 'т', 1000.0, false),
        ('WEIGHT', 'Фунты', 'lbs', 0.45359237, false),
        ('WEIGHT', 'Унции', 'oz', 0.028349523125, false),
        ('WEIGHT', 'Караты', 'кар', 0.0002, false),

        -- LENGTH (base: m)
        ('LENGTH', 'Метры', 'м', 1.0, true),
        ('LENGTH', 'Сантиметры', 'см', 0.01, false),
        ('LENGTH', 'Миллиметры', 'мм', 0.001, false),
        ('LENGTH', 'Километры', 'км', 1000.0, false),
        ('LENGTH', 'Дециметры', 'дм', 0.1, false),
        ('LENGTH', 'Погонные метры', 'пог. м', 1.0, false),
        ('LENGTH', 'Мили', 'mi', 1609.344, false),
        ('LENGTH', 'Футы', 'ft', 0.3048, false),
        ('LENGTH', 'Дюймы', 'in', 0.0254, false),

        -- AREA (base: m2)
        ('AREA', 'Кв. метры', 'кв. м', 1.0, true),
        ('AREA', 'Кв. сантиметры', 'кв. см', 0.0001, false),
        ('AREA', 'Кв. дециметры', 'кв. дм', 0.01, false),
        ('AREA', 'Кв. футы', 'sq ft', 0.09290304, false),

        -- VOLUME (base: liter)
        ('VOLUME', 'Литры', 'л', 1.0, true),
        ('VOLUME', 'Миллилитры', 'мл', 0.001, false),
        ('VOLUME', 'Декалитры', 'дал', 10.0, false),
        ('VOLUME', 'Микролитры', 'мкл', 0.000001, false),
        ('VOLUME', 'Куб. метры', 'куб. м', 1000.0, false),
        ('VOLUME', 'Куб. сантиметры', 'куб. см', 0.001, false),
        ('VOLUME', 'Куб. дециметры', 'куб. дм', 1.0, false),
        ('VOLUME', 'Жидкие унции', 'fl oz', 0.0295735295625, false),
        ('VOLUME', 'Галлоны', 'gal', 3.785411784, false),
        ('VOLUME', 'Куб. футы', 'cu ft', 28.316846592, false),
        ('VOLUME', 'Куб. ярды', 'cu yd', 764.554857984, false),

        -- TIME (base: second)
        ('TIME', 'Секунды', 'сек', 1.0, true),
        ('TIME', 'Минуты', 'мин', 60.0, false),
        ('TIME', 'Часы', 'ч', 3600.0, false),
        ('TIME', 'Сутки', 'сут', 86400.0, false),
        ('TIME', 'Недели', 'нед', 604800.0, false),
        ('TIME', 'Месяцы', 'мес', 2592000.0, false),

        -- ELECTRICITY (base: kWh)
        ('ELECTRICITY', 'Киловатт-часы', 'кВт-ч', 1.0, true),
        ('ELECTRICITY', 'Мегаватт-часы', 'МВт-ч', 1000.0, false),
        ('ELECTRICITY', 'Килокалории', 'ккал', 0.001162222222, false),
        ('ELECTRICITY', 'Килоджоули', 'кДж', 0.000277777778, false)
)
INSERT INTO units (category, name, short_name, conversion_factor, is_base)
SELECT
    s.category::unitcategoryenum,
    s.name,
    s.short_name,
    s.conversion_factor,
    s.is_base
FROM seed_units s
WHERE NOT EXISTS (
    SELECT 1
    FROM units u
    WHERE u.category::text = s.category
      AND u.short_name = s.short_name
);

COMMIT;
