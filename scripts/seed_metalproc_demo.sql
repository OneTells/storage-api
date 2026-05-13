-- =============================================================================
-- Демо-данные для металлопроката (PostgreSQL).
-- Применять ПОСЛЕ миграций / создания схемы из SQLAlchemy-моделей.
--
-- Не заполняет: production_orders и все *_production_order_* таблицы,
-- stock_operations и все операционные таблицы (приёмки, отгрузки и т.д.).
--
-- Единицы измерения: таблица units должна быть уже заполнена (scripts/fill_units.sql).
--   Скрипт опирается на short_name: кг, пог. м, ч — они есть в fill_units.sql.
--
-- Вход для всех демо-пользователей: пароль demo123
-- (хеш SHA256, как в modules/users/utils.py — hash_password).
-- =============================================================================

BEGIN;

SET client_encoding = 'UTF8';

-- ----------------------------------------------------------------------------- склады
INSERT INTO warehouses (name, comment, is_active)
VALUES
    ('Склад сырья',       'Основной склад металла', true),
    ('Склад ГП',          'Готовая продукция',       true),
    ('Участок резки',     'Промежуточный склад',     true)
ON CONFLICT (name) DO NOTHING;

-- ----------------------------------------------------------------------------- сотрудники
INSERT INTO employees (full_name, position, default_hourly_rate)
SELECT v.full_name, v.position, v.rate::numeric(10, 2)
FROM (VALUES
    ('Иванов Сергей Петрович',        'Инженер-технолог',     650.00),
    ('Петрова Анна Викторовна',       'Главный бухгалтер',  580.00),
    ('Сидоров Дмитрий Александрович', 'Менеджер по продажам', 520.00),
    ('Козлов Михаил Олегович',        'Кладовщик',          450.00),
    ('Николаева Елена Сергеевна',     'Оператор станка',    480.00)
) AS v(full_name, position, rate)
WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.full_name = v.full_name);

-- ----------------------------------------------------------------------------- роли
INSERT INTO roles (name, description)
VALUES
    ('Администратор',       'Полный доступ к системе'),
    ('Инженер',            'Технолог: номенклатура, производство, склады (чтение/редактирование)'),
    ('Бухгалтер',          'Учёт: операции, контрагенты, справочники (в основном чтение)'),
    ('Менеджер продаж',    'Клиенты, отгрузки, каталоги, склады')
ON CONFLICT (name) DO NOTHING;

-- ----------------------------------------------------------------------------- разрешения (все codename из API require_permissions)
INSERT INTO permissions (name, codename) VALUES
    ('Создание покупателя', 'customer.create'),
    ('Просмотр покупателя', 'customer.read'),
    ('Изменение покупателя', 'customer.update'),
    ('Список покупателей', 'customers.read'),
    ('Создание сотрудника', 'employee.create'),
    ('Просмотр сотрудника', 'employee.read'),
    ('Изменение сотрудника', 'employee.update'),
    ('Список сотрудников', 'employees.read'),
    ('Создание категории материала', 'material.category.create'),
    ('Удаление категории материала', 'material.category.delete'),
    ('Привязка материала к категории', 'material.category.material.assign'),
    ('Отвязка материала от категории', 'material.category.material.remove'),
    ('Просмотр категории материала', 'material.category.read'),
    ('Привязка подкатегории материала', 'material.category.subcategory.assign'),
    ('Отвязка подкатегории материала', 'material.category.subcategory.remove'),
    ('Изменение категории материала', 'material.category.update'),
    ('Создание материала', 'material.create'),
    ('Просмотр материала', 'material.read'),
    ('Изменение материала', 'material.update'),
    ('Каталог материалов', 'materials.catalog.read'),
    ('Корректировка остатков: создание', 'operations.inventory_adjustment.create'),
    ('Корректировка остатков: просмотр', 'operations.inventory_adjustment.read'),
    ('Корректировка остатков: изменение', 'operations.inventory_adjustment.update'),
    ('Выпуск с производства: создание', 'operations.production_output.create'),
    ('Выпуск с производства: просмотр', 'operations.production_output.read'),
    ('Выпуск с производства: изменение', 'operations.production_output.update'),
    ('Приёмка: создание', 'operations.receipt.create'),
    ('Приёмка: просмотр', 'operations.receipt.read'),
    ('Приёмка: изменение', 'operations.receipt.update'),
    ('Резервирование: создание', 'operations.reservation.create'),
    ('Резервирование: просмотр', 'operations.reservation.read'),
    ('Резервирование: изменение', 'operations.reservation.update'),
    ('Отгрузка: создание', 'operations.shipment.create'),
    ('Отгрузка: просмотр', 'operations.shipment.read'),
    ('Отгрузка: изменение', 'operations.shipment.update'),
    ('Перемещение: создание', 'operations.transfer.create'),
    ('Перемещение: просмотр', 'operations.transfer.read'),
    ('Перемещение: изменение', 'operations.transfer.update'),
    ('Списание: создание', 'operations.write_off.create'),
    ('Списание: просмотр', 'operations.write_off.read'),
    ('Списание: изменение', 'operations.write_off.update'),
    ('Списание в производство: создание', 'operations.write_off_to_production.create'),
    ('Списание в производство: просмотр', 'operations.write_off_to_production.read'),
    ('Списание в производство: изменение', 'operations.write_off_to_production.update'),
    ('Создание разрешения', 'permission.create'),
    ('Удаление разрешения', 'permission.delete'),
    ('Просмотр разрешения', 'permission.read'),
    ('Изменение разрешения', 'permission.update'),
    ('Список разрешений', 'permissions.read'),
    ('Создание категории продукции', 'product.category.create'),
    ('Удаление категории продукции', 'product.category.delete'),
    ('Привязка продукта к категории', 'product.category.product.assign'),
    ('Отвязка продукта от категории', 'product.category.product.remove'),
    ('Просмотр категории продукции', 'product.category.read'),
    ('Привязка подкатегории продукции', 'product.category.subcategory.assign'),
    ('Отвязка подкатегории продукции', 'product.category.subcategory.remove'),
    ('Изменение категории продукции', 'product.category.update'),
    ('Создание продукта', 'product.create'),
    ('Просмотр продукта', 'product.read'),
    ('Изменение продукта', 'product.update'),
    ('Создание заказа на производство', 'production_order.create'),
    ('Просмотр заказа на производство', 'production_order.read'),
    ('Изменение заказа на производство', 'production_order.update'),
    ('Список заказов на производство', 'production_orders.read'),
    ('Каталог продукции', 'products.catalog.read'),
    ('Просмотр профиля', 'profile.read'),
    ('Завершение сессий профиля', 'profile.sessions.terminate'),
    ('Изменение профиля', 'profile.update'),
    ('Создание ресурса', 'resource.create'),
    ('Просмотр ресурса', 'resource.read'),
    ('Изменение ресурса', 'resource.update'),
    ('Список ресурсов', 'resources.read'),
    ('Создание роли', 'role.create'),
    ('Удаление роли', 'role.delete'),
    ('Назначение разрешения роли', 'role.permission.assign'),
    ('Снятие разрешения с роли', 'role.permission.remove'),
    ('Просмотр роли', 'role.read'),
    ('Изменение роли', 'role.update'),
    ('Список ролей', 'roles.read'),
    ('Создание поставщика', 'supplier.create'),
    ('Просмотр поставщика', 'supplier.read'),
    ('Изменение поставщика', 'supplier.update'),
    ('Список поставщиков', 'suppliers.read'),
    ('Список единиц измерения', 'units.read'),
    ('Создание пользователя', 'user.create'),
    ('Удаление пользователя', 'user.delete'),
    ('Смена пароля пользователя', 'user.password.change'),
    ('Просмотр пользователя', 'user.read'),
    ('Назначение роли пользователю', 'user.role.assign'),
    ('Снятие роли с пользователя', 'user.role.remove'),
    ('Просмотр сессий пользователя', 'user.sessions.read'),
    ('Завершение сессий пользователя', 'user.sessions.terminate'),
    ('Изменение пользователя', 'user.update'),
    ('Список пользователей', 'users.read'),
    ('Создание склада', 'warehouse.create'),
    ('Просмотр склада', 'warehouse.read'),
    ('Изменение склада', 'warehouse.update'),
    ('Список складов', 'warehouses.read')
ON CONFLICT (codename) DO NOTHING;

-- ----------------------------------------------------------------------------- привязка разрешений к ролям
-- Администратор: все разрешения
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'Администратор'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Инженер
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.codename IN (
    'warehouses.read', 'warehouse.read',
    'materials.catalog.read', 'material.read', 'material.create', 'material.update',
    'material.category.read', 'product.read', 'products.catalog.read',
    'product.category.read', 'resources.read', 'resource.read',
    'units.read', 'employees.read', 'employee.read',
    'production_orders.read', 'production_order.read', 'production_order.create', 'production_order.update',
    'operations.receipt.read', 'operations.shipment.read', 'operations.transfer.read',
    'operations.reservation.read', 'operations.write_off.read', 'operations.write_off_to_production.read',
    'operations.production_output.read', 'operations.inventory_adjustment.read',
    'operations.receipt.create', 'operations.transfer.create', 'operations.reservation.create',
    'operations.write_off_to_production.create', 'operations.production_output.create',
    'operations.inventory_adjustment.create', 'profile.read', 'profile.update'
)
WHERE r.name = 'Инженер'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Бухгалтер
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.codename IN (
    'warehouses.read', 'warehouse.read',
    'materials.catalog.read', 'material.read', 'products.catalog.read', 'product.read',
    'customers.read', 'customer.read', 'suppliers.read', 'supplier.read',
    'units.read', 'employees.read', 'employee.read',
    'operations.receipt.read', 'operations.shipment.read', 'operations.transfer.read',
    'operations.write_off.read', 'operations.inventory_adjustment.read',
    'operations.reservation.read', 'operations.write_off_to_production.read',
    'operations.production_output.read', 'production_orders.read', 'production_order.read',
    'profile.read', 'profile.update'
)
WHERE r.name = 'Бухгалтер'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Менеджер продаж
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.codename IN (
    'warehouses.read', 'warehouse.read',
    'materials.catalog.read', 'material.read', 'products.catalog.read', 'product.read',
    'customers.read', 'customer.create', 'customer.read', 'customer.update',
    'operations.shipment.read', 'operations.shipment.create', 'operations.shipment.update',
    'operations.reservation.read', 'operations.reservation.create', 'operations.reservation.update',
    'suppliers.read', 'supplier.read', 'units.read', 'profile.read', 'profile.update'
)
WHERE r.name = 'Менеджер продаж'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- ----------------------------------------------------------------------------- пользователи (пароль demo123 → SHA256 hex)
INSERT INTO users (name, username, password_hash, is_active)
VALUES
    ('Администратор демо', 'admin_demo',
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', true),
    ('Инженер демо', 'engineer_demo',
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', true),
    ('Бухгалтер демо', 'accountant_demo',
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', true),
    ('Менеджер продаж демо', 'sales_demo',
     'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', true)
ON CONFLICT (username) DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.name = 'Администратор' AND u.username = 'admin_demo'
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.name = 'Инженер' AND u.username = 'engineer_demo'
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.name = 'Бухгалтер' AND u.username = 'accountant_demo'
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.name = 'Менеджер продаж' AND u.username = 'sales_demo'
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------- контрагенты (идемпотентно по ИНН / ФИО+телефон)
INSERT INTO counterparties (role, type, name, phone, email, comment, inn, kpp, ogrn, legal_address, director, director_position, is_active)
SELECT 'SUPPLIER'::counterpartyroletype, 'LEGAL_ENTITY'::counterpartytype,
       'ООО «МеталлСнаб»', '+7 (495) 100-00-01', 'info@metallsnab.example', 'Поставщик проката',
       '7701234567', '770101001', '1027700123456', 'г. Москва, ул. Промышленная, д. 1',
       'Смирнов А.Б.', 'Генеральный директор', true
WHERE NOT EXISTS (SELECT 1 FROM counterparties c WHERE c.inn = '7701234567');

INSERT INTO counterparties (role, type, name, phone, email, comment, inn, kpp, ogrn, legal_address, director, director_position, is_active)
SELECT 'SUPPLIER'::counterpartyroletype, 'ENTREPRENEUR'::counterpartytype,
       'ИП Кузнецов П.С.', '+7 (916) 200-00-02', NULL, 'Резка и доставка',
       '770123456789', NULL, '319774600123456', 'г. Москва', NULL, NULL, true
WHERE NOT EXISTS (SELECT 1 FROM counterparties c WHERE c.inn = '770123456789');

INSERT INTO counterparties (role, type, name, phone, email, comment, inn, kpp, ogrn, legal_address, director, director_position, is_active)
SELECT 'CUSTOMER'::counterpartyroletype, 'LEGAL_ENTITY'::counterpartytype,
       'ООО «СтройМонтаж»', '+7 (812) 300-00-03', 'zakup@stroymont.example', 'Строительная организация',
       '7801555666', '780101001', '1187847123456', 'г. Санкт-Петербург, пр. Металлистов, 10',
       'Волков И.И.', 'Директор', true
WHERE NOT EXISTS (SELECT 1 FROM counterparties c WHERE c.inn = '7801555666');

INSERT INTO counterparties (role, type, name, phone, email, comment, inn, kpp, ogrn, legal_address, director, director_position, is_active)
SELECT 'CUSTOMER'::counterpartyroletype, 'INDIVIDUAL'::counterpartytype,
       'Фролов Геннадий Викторович', '+7 (903) 400-00-04', NULL, 'Розничный заказчик',
       NULL, NULL, NULL, NULL, NULL, NULL, true
WHERE NOT EXISTS (
    SELECT 1 FROM counterparties c
    WHERE c.type = 'INDIVIDUAL'::counterpartytype
      AND c.name = 'Фролов Геннадий Викторович'
      AND c.phone = '+7 (903) 400-00-04'
);

-- ----------------------------------------------------------------------------- категории материалов
INSERT INTO material_categories (name, description)
VALUES
    ('Листовой прокат', 'Листы, рулоны'),
    ('Сортовой прокат', 'Уголок, швеллер, двутавр'),
    ('Трубный прокат', 'Электросварные и бесшовные'),
    ('Нержавеющая сталь', 'Аустенитные марки')
ON CONFLICT (name) DO NOTHING;

INSERT INTO material_category_subcategories (category_id, subcategory_id)
SELECT p.id, c.id
FROM material_categories p
JOIN material_categories c ON c.name = 'Нержавеющая сталь'
WHERE p.name = 'Листовой прокат'
  AND NOT EXISTS (
      SELECT 1 FROM material_category_subcategories x
      WHERE x.category_id = p.id AND x.subcategory_id = c.id
  );

-- ----------------------------------------------------------------------------- материалы (SKU уникален; вес — кг, сортовой/труба — пог. м)
INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'LIST-09G2S-4-1500-6000', 'Лист 09Г2С 4×1500×6000 мм', 'Горячекатаный лист',
       (SELECT id FROM units WHERE short_name = 'кг' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'LIST-09G2S-4-1500-6000');

INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'LIST-3SP-3-1250-2500', 'Лист Ст3сп 3×1250×2500 мм', 'Горячекатаный, конструкционная',
       (SELECT id FROM units WHERE short_name = 'кг' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'LIST-3SP-3-1250-2500');

INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'LIST-AISI304-2-1000', 'Лист AISI 304 2×1000×2000', 'Нержавеющий лист',
       (SELECT id FROM units WHERE short_name = 'кг' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'LIST-AISI304-2-1000');

INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'UGL-63X63X5-12M', 'Уголок 63×63×5 мм, мерная длина 12 м', 'Равнополочный ГОСТ 8509',
       (SELECT id FROM units WHERE short_name = 'пог. м' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'UGL-63X63X5-12M');

INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'SHV-16P-12M', 'Швеллер 16П, 12 м', 'Горячекатаный',
       (SELECT id FROM units WHERE short_name = 'пог. м' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'SHV-16P-12M');

INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'TRUBA-159X6-12M', 'Труба ВГП 159×6 мм, 12 м', 'Водогазопроводная',
       (SELECT id FROM units WHERE short_name = 'пог. м' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'TRUBA-159X6-12M');

INSERT INTO materials (sku, name, description, unit_id, is_active)
SELECT 'KRUG-40-A12-6M', 'Круг 40 мм ст. А12, 6 м', 'Калиброванный прокат',
       (SELECT id FROM units WHERE short_name = 'пог. м' ORDER BY id LIMIT 1), true
WHERE NOT EXISTS (SELECT 1 FROM materials WHERE sku = 'KRUG-40-A12-6M');

-- ----------------------------------------------------------------------------- связь материал ↔ категория
INSERT INTO material_category_materials (category_id, material_id)
SELECT c.id, m.id
FROM material_categories c
JOIN materials m ON (
    (c.name = 'Листовой прокат' AND m.sku LIKE 'LIST-%' AND m.sku NOT LIKE '%AISI%')
    OR (c.name = 'Сортовой прокат' AND m.sku IN ('UGL-63X63X5-12M', 'SHV-16P-12M', 'KRUG-40-A12-6M'))
    OR (c.name = 'Трубный прокат' AND m.sku = 'TRUBA-159X6-12M')
    OR (c.name = 'Нержавеющая сталь' AND m.sku = 'LIST-AISI304-2-1000')
)
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------- ресурсы (станок / смена)
INSERT INTO resources (type, name, unit_id, fixed_rate, initial_amount, service_life)
SELECT 'FIXED_RATE'::resourcetype, 'Смена гильотины',
       (SELECT id FROM units WHERE short_name = 'ч' LIMIT 1),
       12000.00, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM resources WHERE name = 'Смена гильотины');

INSERT INTO resources (type, name, unit_id, fixed_rate, initial_amount, service_life)
SELECT 'DEPRECIATION'::resourcetype, 'Листогибочный станок',
       (SELECT id FROM units WHERE short_name = 'ч' LIMIT 1),
       NULL, 3500000.00, 20000.00
WHERE NOT EXISTS (SELECT 1 FROM resources WHERE name = 'Листогибочный станок');

-- ----------------------------------------------------------------------------- категории продукции (готовая продукция)
INSERT INTO product_categories (name, description)
VALUES
    ('Гнутые элементы', 'Заготовки после гибки'),
    ('Резка листа', 'Услуги раскроя')
ON CONFLICT (name) DO NOTHING;

-- ----------------------------------------------------------------------------- продукция (рецепт: выходной материал + входные материалы)
INSERT INTO products (name, description, output_material_id, output_quantity, is_active)
SELECT
    'Уголок 63×63×5 мм, длина по ТЗ',
    'Резка и подготовка сортового проката',
    m_out.id,
    1.000,
    true
FROM materials m_out
WHERE m_out.sku = 'UGL-63X63X5-12M'
  AND NOT EXISTS (
      SELECT 1 FROM products p WHERE p.name = 'Уголок 63×63×5 мм, длина по ТЗ'
  );

INSERT INTO product_materials (product_id, material_id, quantity)
SELECT p.id, m.id, 0.050
FROM products p
JOIN materials m ON m.sku = 'UGL-63X63X5-12M'
WHERE p.name = 'Уголок 63×63×5 мм, длина по ТЗ'
  AND NOT EXISTS (
      SELECT 1 FROM product_materials pm
      WHERE pm.product_id = p.id AND pm.material_id = m.id
  );

INSERT INTO product_resources (product_id, resource_id, quantity)
SELECT p.id, r.id, 0.25
FROM products p
JOIN resources r ON r.name = 'Смена гильотины'
WHERE p.name = 'Уголок 63×63×5 мм, длина по ТЗ'
  AND NOT EXISTS (
      SELECT 1 FROM product_resources pr
      WHERE pr.product_id = p.id AND pr.resource_id = r.id
  );

INSERT INTO products (name, description, output_material_id, output_quantity, is_active)
SELECT
    'Лист раскрой 1250×2500 из рулона',
    'Раскрой листового проката',
    m_out.id,
    1.000,
    true
FROM materials m_out
WHERE m_out.sku = 'LIST-3SP-3-1250-2500'
  AND NOT EXISTS (
      SELECT 1 FROM products p WHERE p.name = 'Лист раскрой 1250×2500 из рулона'
  );

INSERT INTO product_materials (product_id, material_id, quantity)
SELECT p.id, m.id, 1.020
FROM products p
JOIN materials m ON m.sku = 'LIST-3SP-3-1250-2500'
WHERE p.name = 'Лист раскрой 1250×2500 из рулона'
  AND NOT EXISTS (
      SELECT 1 FROM product_materials pm
      WHERE pm.product_id = p.id AND pm.material_id = m.id
  );

INSERT INTO product_resources (product_id, resource_id, quantity)
SELECT p.id, r.id, 1.50
FROM products p
JOIN resources r ON r.name = 'Листогибочный станок'
WHERE p.name = 'Лист раскрой 1250×2500 из рулона'
  AND NOT EXISTS (
      SELECT 1 FROM product_resources pr
      WHERE pr.product_id = p.id AND pr.resource_id = r.id
  );

INSERT INTO product_category_products (category_id, product_id)
SELECT c.id, p.id
FROM product_categories c
JOIN products p ON p.name IN (
    'Уголок 63×63×5 мм, длина по ТЗ',
    'Лист раскрой 1250×2500 из рулона'
)
WHERE c.name IN ('Гнутые элементы', 'Резка листа')
  AND (
    (c.name = 'Гнутые элементы' AND p.name = 'Уголок 63×63×5 мм, длина по ТЗ')
    OR (c.name = 'Резка листа' AND p.name = 'Лист раскрой 1250×2500 из рулона')
  )
ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------- партии (остатки на складе; без привязки к операциям)
INSERT INTO batches (material_id, warehouse_id, quantity, remaining)
SELECT m.id, w.id, 24.500, 24.500
FROM materials m
CROSS JOIN warehouses w
WHERE m.sku = 'LIST-09G2S-4-1500-6000' AND w.name = 'Склад сырья'
  AND NOT EXISTS (
      SELECT 1 FROM batches b
      WHERE b.material_id = m.id AND b.warehouse_id = w.id
  );

INSERT INTO batches (material_id, warehouse_id, quantity, remaining)
SELECT m.id, w.id, 120.000, 118.500
FROM materials m
CROSS JOIN warehouses w
WHERE m.sku = 'UGL-63X63X5-12M' AND w.name = 'Склад сырья'
  AND NOT EXISTS (
      SELECT 1 FROM batches b
      WHERE b.material_id = m.id AND b.warehouse_id = w.id
  );

INSERT INTO batches (material_id, warehouse_id, quantity, remaining)
SELECT m.id, w.id, 6.000, 6.000
FROM materials m
CROSS JOIN warehouses w
WHERE m.sku = 'LIST-AISI304-2-1000' AND w.name = 'Склад ГП'
  AND NOT EXISTS (
      SELECT 1 FROM batches b
      WHERE b.material_id = m.id AND b.warehouse_id = w.id
  );

COMMIT;
