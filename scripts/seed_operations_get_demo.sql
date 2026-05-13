-- =============================================================================
-- Демо-данные для GET-ручек операций: отгрузка, выпуск с производства,
-- списание в производство (PostgreSQL).
--
-- Условия: миграции применены; есть users; warehouses; materials;
--   counterparties с ролью CUSTOMER (как в seed_metalproc_demo — ООО «СтройМонтаж»).
--   Списки с фильтром по текущему пользователю: created_by_id = admin_demo
--   (если пользователя нет — берётся минимальный id из users).
--
--   Если отгрузки не создались: нужен контрагент с inn = '7801555666' (ООО «СтройМонтаж» из сида)
--   или поправьте подзапрос counterparty_id в этом файле.
--
-- Идемпотентность: строки с префиксом имён/комментария [seed-get-demo] …
--   повторный запуск не дублирует те же операции и заказ.
-- =============================================================================

BEGIN;

SET client_encoding = 'UTF8';

-- ----------------------------------------------------------------------------- минимальный заказ на производство (нужен для JOIN в GET выпуска)
INSERT INTO production_orders (performed_at, warehouse_id, comment, status, created_by_id)
SELECT
    timestamptz '2026-01-18 09:00:00+00',
    (SELECT id FROM warehouses WHERE name = 'Склад сырья' ORDER BY id LIMIT 1),
    '[seed-get-demo] Заказ под демо API',
    'IN_PROGRESS'::productionorderstatus,
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    ))
WHERE EXISTS (SELECT 1 FROM users)
  AND EXISTS (SELECT 1 FROM warehouses WHERE name = 'Склад сырья')
  AND NOT EXISTS (
      SELECT 1 FROM production_orders po
      WHERE po.comment = '[seed-get-demo] Заказ под демо API'
  );

-- ----------------------------------------------------------------------------- 1) Отгрузка — черновик (2 строки номенклатуры)
INSERT INTO stock_operations (type, name, performed_at, created_by_id)
SELECT
    'SHIPMENT'::stockoperationtype,
    '[seed-get-demo] Отгрузка — черновик',
    timestamptz '2026-01-20 11:00:00+00',
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    ))
WHERE NOT EXISTS (
    SELECT 1 FROM stock_operations x
    WHERE x.type = 'SHIPMENT'::stockoperationtype
      AND x.name = '[seed-get-demo] Отгрузка — черновик'
)
  AND EXISTS (SELECT 1 FROM counterparties WHERE inn = '7801555666');

INSERT INTO shipments (operation_id, counterparty_id, warehouse_id, order_number, status)
SELECT
    so.id,
    (SELECT id FROM counterparties WHERE inn = '7801555666' ORDER BY id LIMIT 1),
    (SELECT id FROM warehouses WHERE name = 'Склад сырья' ORDER BY id LIMIT 1),
    'ORD-SEED-1001',
    'DRAFT'::operationstatus
FROM stock_operations so
WHERE so.type = 'SHIPMENT'::stockoperationtype
  AND so.name = '[seed-get-demo] Отгрузка — черновик'
  AND NOT EXISTS (SELECT 1 FROM shipments s WHERE s.operation_id = so.id);

INSERT INTO shipment_items (operation_id, material_id, quantity, batch_id)
SELECT so.id, m.id, 2.500::numeric(15, 3), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'LIST-09G2S-4-1500-6000' ORDER BY id LIMIT 1
) m
WHERE so.type = 'SHIPMENT'::stockoperationtype
  AND so.name = '[seed-get-demo] Отгрузка — черновик'
  AND NOT EXISTS (
      SELECT 1 FROM shipment_items si
      WHERE si.operation_id = so.id AND si.material_id = m.id
  );

INSERT INTO shipment_items (operation_id, material_id, quantity, batch_id)
SELECT so.id, m.id, 5.000::numeric(15, 3), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'UGL-63X63X5-12M' ORDER BY id LIMIT 1
) m
WHERE so.type = 'SHIPMENT'::stockoperationtype
  AND so.name = '[seed-get-demo] Отгрузка — черновик'
  AND NOT EXISTS (
      SELECT 1 FROM shipment_items si
      WHERE si.operation_id = so.id AND si.material_id = m.id
  );

-- ----------------------------------------------------------------------------- 2) Отгрузка — проведена (completed_at + статус)
INSERT INTO stock_operations (type, name, performed_at, created_by_id, completed_at)
SELECT
    'SHIPMENT'::stockoperationtype,
    '[seed-get-demo] Отгрузка — проведена',
    timestamptz '2026-01-19 14:30:00+00',
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    )),
    timestamptz '2026-01-19 15:00:00+00'
WHERE NOT EXISTS (
    SELECT 1 FROM stock_operations x
    WHERE x.type = 'SHIPMENT'::stockoperationtype
      AND x.name = '[seed-get-demo] Отгрузка — проведена'
)
  AND EXISTS (SELECT 1 FROM counterparties WHERE inn = '7801555666');

INSERT INTO shipments (operation_id, counterparty_id, warehouse_id, order_number, status)
SELECT
    so.id,
    (SELECT id FROM counterparties WHERE inn = '7801555666' ORDER BY id LIMIT 1),
    (SELECT id FROM warehouses WHERE name = 'Склад сырья' ORDER BY id LIMIT 1),
    'ORD-SEED-1002',
    'COMPLETED'::operationstatus
FROM stock_operations so
WHERE so.type = 'SHIPMENT'::stockoperationtype
  AND so.name = '[seed-get-demo] Отгрузка — проведена'
  AND NOT EXISTS (SELECT 1 FROM shipments s WHERE s.operation_id = so.id);

INSERT INTO shipment_items (operation_id, material_id, quantity, batch_id)
SELECT so.id, m.id, 1.000::numeric(15, 3), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'LIST-3SP-3-1250-2500' ORDER BY id LIMIT 1
) m
WHERE so.type = 'SHIPMENT'::stockoperationtype
  AND so.name = '[seed-get-demo] Отгрузка — проведена'
  AND NOT EXISTS (
      SELECT 1 FROM shipment_items si
      WHERE si.operation_id = so.id AND si.material_id = m.id
  );

-- ----------------------------------------------------------------------------- 3) Выпуск с производства — черновик
INSERT INTO stock_operations (type, name, performed_at, created_by_id)
SELECT
    'PRODUCTION_OUTPUT'::stockoperationtype,
    '[seed-get-demo] Выпуск с производства — черновик',
    timestamptz '2026-01-21 07:45:00+00',
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    ))
WHERE EXISTS (SELECT 1 FROM production_orders WHERE comment = '[seed-get-demo] Заказ под демо API')
  AND NOT EXISTS (
    SELECT 1 FROM stock_operations x
    WHERE x.type = 'PRODUCTION_OUTPUT'::stockoperationtype
      AND x.name = '[seed-get-demo] Выпуск с производства — черновик'
);

INSERT INTO production_outputs (operation_id, production_order_id, warehouse_id, status)
SELECT
    so.id,
    po.id,
    (SELECT id FROM warehouses WHERE name = 'Склад ГП' ORDER BY id LIMIT 1),
    'DRAFT'::operationstatus
FROM stock_operations so
CROSS JOIN (
    SELECT id FROM production_orders
    WHERE comment = '[seed-get-demo] Заказ под демо API'
    ORDER BY id LIMIT 1
) po
WHERE so.type = 'PRODUCTION_OUTPUT'::stockoperationtype
  AND so.name = '[seed-get-demo] Выпуск с производства — черновик'
  AND NOT EXISTS (SELECT 1 FROM production_outputs p WHERE p.operation_id = so.id);

INSERT INTO production_output_items (operation_id, material_id, quantity, unit_price, batch_id)
SELECT so.id, m.id, 800.000::numeric(15, 3), 95.50::numeric(15, 2), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'LIST-AISI304-2-1000' ORDER BY id LIMIT 1
) m
WHERE so.type = 'PRODUCTION_OUTPUT'::stockoperationtype
  AND so.name = '[seed-get-demo] Выпуск с производства — черновик'
  AND NOT EXISTS (
      SELECT 1 FROM production_output_items pi
      WHERE pi.operation_id = so.id AND pi.material_id = m.id
  );

INSERT INTO production_output_items (operation_id, material_id, quantity, unit_price, batch_id)
SELECT so.id, m.id, 40.000::numeric(15, 3), 62.00::numeric(15, 2), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'KRUG-40-A12-6M' ORDER BY id LIMIT 1
) m
WHERE so.type = 'PRODUCTION_OUTPUT'::stockoperationtype
  AND so.name = '[seed-get-demo] Выпуск с производства — черновик'
  AND NOT EXISTS (
      SELECT 1 FROM production_output_items pi
      WHERE pi.operation_id = so.id AND pi.material_id = m.id
  );

-- ----------------------------------------------------------------------------- 4) Выпуск с производства — проведён
INSERT INTO stock_operations (type, name, performed_at, created_by_id, completed_at)
SELECT
    'PRODUCTION_OUTPUT'::stockoperationtype,
    '[seed-get-demo] Выпуск с производства — проведён',
    timestamptz '2026-01-21 16:00:00+00',
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    )),
    timestamptz '2026-01-21 16:05:00+00'
WHERE EXISTS (SELECT 1 FROM production_orders WHERE comment = '[seed-get-demo] Заказ под демо API')
  AND NOT EXISTS (
    SELECT 1 FROM stock_operations x
    WHERE x.type = 'PRODUCTION_OUTPUT'::stockoperationtype
      AND x.name = '[seed-get-demo] Выпуск с производства — проведён'
);

INSERT INTO production_outputs (operation_id, production_order_id, warehouse_id, status)
SELECT
    so.id,
    po.id,
    (SELECT id FROM warehouses WHERE name = 'Склад ГП' ORDER BY id LIMIT 1),
    'COMPLETED'::operationstatus
FROM stock_operations so
CROSS JOIN (
    SELECT id FROM production_orders
    WHERE comment = '[seed-get-demo] Заказ под демо API'
    ORDER BY id LIMIT 1
) po
WHERE so.type = 'PRODUCTION_OUTPUT'::stockoperationtype
  AND so.name = '[seed-get-demo] Выпуск с производства — проведён'
  AND NOT EXISTS (SELECT 1 FROM production_outputs p WHERE p.operation_id = so.id);

INSERT INTO production_output_items (operation_id, material_id, quantity, unit_price, batch_id)
SELECT so.id, m.id, 100.000::numeric(15, 3), 48.75::numeric(15, 2), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'UGL-63X63X5-12M' ORDER BY id LIMIT 1
) m
WHERE so.type = 'PRODUCTION_OUTPUT'::stockoperationtype
  AND so.name = '[seed-get-demo] Выпуск с производства — проведён'
  AND NOT EXISTS (
      SELECT 1 FROM production_output_items pi
      WHERE pi.operation_id = so.id AND pi.material_id = m.id
  );

-- ----------------------------------------------------------------------------- 5) Списание в производство — черновик (production_order_id — строка-ссылка, не FK)
INSERT INTO stock_operations (type, name, performed_at, created_by_id)
SELECT
    'WRITE_OFF_TO_PRODUCTION'::stockoperationtype,
    '[seed-get-demo] Списание в производство — черновик',
    timestamptz '2026-01-22 10:15:00+00',
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    ))
WHERE NOT EXISTS (
    SELECT 1 FROM stock_operations x
    WHERE x.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
      AND x.name = '[seed-get-demo] Списание в производство — черновик'
);

INSERT INTO write_offs_to_production (operation_id, warehouse_id, production_order_id, status)
SELECT
    so.id,
    (SELECT id FROM warehouses WHERE name = 'Склад сырья' ORDER BY id LIMIT 1),
    'ЗНП-SEED-REF-01'::varchar(100),
    'DRAFT'::operationstatus
FROM stock_operations so
WHERE so.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
  AND so.name = '[seed-get-demo] Списание в производство — черновик'
  AND NOT EXISTS (SELECT 1 FROM write_offs_to_production w WHERE w.operation_id = so.id);

INSERT INTO write_off_to_production_items (operation_id, material_id, quantity, unit_price, batch_id)
SELECT so.id, m.id, 10.000::numeric(15, 3), 55.00::numeric(15, 2), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'LIST-09G2S-4-1500-6000' ORDER BY id LIMIT 1
) m
WHERE so.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
  AND so.name = '[seed-get-demo] Списание в производство — черновик'
  AND NOT EXISTS (
      SELECT 1 FROM write_off_to_production_items wi
      WHERE wi.operation_id = so.id AND wi.material_id = m.id
  );

INSERT INTO write_off_to_production_items (operation_id, material_id, quantity, unit_price, batch_id)
SELECT so.id, m.id, 2.000::numeric(15, 3), 52.25::numeric(15, 2), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'SHV-16P-12M' ORDER BY id LIMIT 1
) m
WHERE so.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
  AND so.name = '[seed-get-demo] Списание в производство — черновик'
  AND NOT EXISTS (
      SELECT 1 FROM write_off_to_production_items wi
      WHERE wi.operation_id = so.id AND wi.material_id = m.id
  );

-- ----------------------------------------------------------------------------- 6) Списание в производство — проведено
INSERT INTO stock_operations (type, name, performed_at, created_by_id, completed_at)
SELECT
    'WRITE_OFF_TO_PRODUCTION'::stockoperationtype,
    '[seed-get-demo] Списание в производство — проведено',
    timestamptz '2026-01-22 12:00:00+00',
    (SELECT COALESCE(
        (SELECT id FROM users WHERE username = 'admin_demo' LIMIT 1),
        (SELECT id FROM users ORDER BY id LIMIT 1)
    )),
    timestamptz '2026-01-22 12:10:00+00'
WHERE NOT EXISTS (
    SELECT 1 FROM stock_operations x
    WHERE x.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
      AND x.name = '[seed-get-demo] Списание в производство — проведено'
);

INSERT INTO write_offs_to_production (operation_id, warehouse_id, production_order_id, status)
SELECT
    so.id,
    (SELECT id FROM warehouses WHERE name = 'Склад сырья' ORDER BY id LIMIT 1),
    NULL::varchar(100),
    'COMPLETED'::operationstatus
FROM stock_operations so
WHERE so.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
  AND so.name = '[seed-get-demo] Списание в производство — проведено'
  AND NOT EXISTS (SELECT 1 FROM write_offs_to_production w WHERE w.operation_id = so.id);

INSERT INTO write_off_to_production_items (operation_id, material_id, quantity, unit_price, batch_id)
SELECT so.id, m.id, 3.000::numeric(15, 3), 51.00::numeric(15, 2), NULL::bigint
FROM stock_operations so
CROSS JOIN LATERAL (
    SELECT id FROM materials WHERE sku = 'TRUBA-159X6-12M' ORDER BY id LIMIT 1
) m
WHERE so.type = 'WRITE_OFF_TO_PRODUCTION'::stockoperationtype
  AND so.name = '[seed-get-demo] Списание в производство — проведено'
  AND NOT EXISTS (
      SELECT 1 FROM write_off_to_production_items wi
      WHERE wi.operation_id = so.id AND wi.material_id = m.id
  );

COMMIT;
