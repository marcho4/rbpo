# RISKS — Реестр рисков

## Введение
Данный документ содержит реестр рисков информационной безопасности для CRM-системы. Каждый риск оценивается по вероятности (Likelihood, L) и влиянию (Impact, I) по шкале 1–5, где Risk = L × I.

## Шкала оценки

### Likelihood (L) — Вероятность реализации угрозы
- **1** — Очень низкая (маловероятно, требует значительных ресурсов атакующего)
- **2** — Низкая (возможно при определённых условиях)
- **3** — Средняя (реальный сценарий при типичных условиях)
- **4** — Высокая (вероятно без дополнительных барьеров)
- **5** — Очень высокая (практически неизбежно)

### Impact (I) — Влияние на бизнес/безопасность
- **1** — Минимальное (незначительное неудобство)
- **2** — Низкое (локальное влияние, быстрое восстановление)
- **3** — Среднее (заметное влияние на операции/репутацию)
- **4** — Высокое (существенный ущерб, регуляторные последствия)
- **5** — Критическое (катастрофический ущерб, потеря бизнеса)

### Приоритет по Risk Score
- **1-5** — Низкий (мониторинг)
- **6-12** — Средний (план снижения)
- **13-19** — Высокий (немедленные действия)
- **20-25** — Критический (экстренное реагирование)

---

## Реестр рисков

| RiskID | Описание | Связь (Поток/NFR) | L | I | Risk | Приоритет | Стратегия | Владелец | Срок | Критерий закрытия |
|--------|----------|-------------------|---|---|------|-----------|-----------|----------|------|-------------------|
| **R1** | Брутфорс учётных данных через эндпоинт /login | F1, NFR-03 | 3 | 4 | **12** | Средний | Снизить | @security-team | 2025-10-25 | Rate limit 5 попыток/мин на /login + integration tests + алерты в SIEM |
| **R2** | MITM-атака с перехватом credentials из-за слабой TLS-конфигурации | F1, NFR-03 | 2 | 5 | **10** | Средний | Снизить | @devops-team | 2025-10-22 | TLS 1.2+ only; SSL Labs grade A+; автоматические проверки в CI |
| **R3** | DDoS на API Gateway исчерпывает ресурсы и нарушает SLA | F2, F4, NFR-02, NFR-06 | 3 | 4 | **12** | Средний | Снизить | @devops-team | 2025-11-05 | Global rate limiting + CDN/DDoS protection + load tests @ 500 RPS |
| **R4** | Horizontal privilege escalation: доступ к данным других компаний/пользователей | F2, F4, F5, NFR-03 | 3 | 5 | **15** | Высокий | Снизить | @backend-team | 2025-10-28 | Tenant isolation tests + authorization tests для всех CRUD операций + code review |
| **R5** | Отсутствие audit trail не позволяет расследовать инциденты | F3, F5, F8, NFR-05 | 3 | 4 | **12** | Средний | Снизить | @backend-team | 2025-10-27 | Централизованное логирование всех CRUD операций + immutable logs + audit tests |
| **R6** | Компрометация DB credentials даёт полный доступ ко всем данным | F6, NFR-08 | 2 | 5 | **10** | Средний | Снизить | @devops-team | 2025-11-01 | Secret rotation + HashiCorp Vault + least privilege DB accounts + TLS для DB connections |
| **R7** | SQL Injection через некорректную обработку пользовательского ввода | F6, NFR-03 | 2 | 5 | **10** | Средний | Снизить | @backend-team | 2025-10-25 | ORM/prepared statements + input validation + static analysis (Bandit) в CI + SQL injection tests |
| **R8** | Утечка чувствительных данных (refresh tokens, PII) из БД при компрометации | F7, NFR-08 | 2 | 5 | **10** | Средний | Снизить | @backend-team | 2025-11-15 | Encryption at rest (AES-256) для PII-полей + тесты чтения без ключа + backup encryption |
| **R9** | Утечка PII/credentials через логи (GDPR violation) | F8, NFR-05 | 3 | 4 | **12** | Средний | Снизить | @backend-team | 2025-10-30 | PII scrubbing в логах + structured logging + log content audit + GDPR compliance review |
| **R10** | Alert fatigue или потеря критических алертов из-за flood/блокировки | F10, NFR-05 | 2 | 4 | **8** | Средний | Снизить | @devops-team | 2025-11-05 | Alert throttling + priority routing + multiple channels (PagerDuty) + alert delivery tests |

---

## Сводная статистика

| Приоритет | Количество рисков | Risk Score диапазон |
|-----------|-------------------|---------------------|
| Критический | 0 | 20-25 |
| Высокий | 1 | 13-19 |
| Средний | 9 | 6-12 |
| Низкий | 0 | 1-5 |
| **Всего** | **10** | — |

---

## Стратегии обработки рисков

### Снизить (Mitigate) — 10 рисков
Внедрение контрольных мер для снижения вероятности или влияния. Все риски обрабатываются через технические контроли, автоматизацию и тестирование.

### Принять (Accept) — 0 рисков
Все идентифицированные риски требуют активной обработки.

### Избежать (Avoid) — 0 рисков
Нет рисков, требующих отказа от функциональности.

### Перенести (Transfer) — 0 рисков
Нет рисков, переносимых на третьи стороны (страхование, SLA с vendors и т.д.). Опционально можно рассмотреть киберстрахование для покрытия R4, R6, R8.

---

## План реализации контролей (Timeline)

### Фаза 1: Критические риски
- **R4** (Risk 15): Tenant isolation + authorization tests
- **R7** (Risk 10): ORM/prepared statements + SQL injection tests
- **R1** (Risk 12): Rate limiting на /login

### Фаза 2: Высокие и средние риски
- **R2** (Risk 10): TLS hardening + SSL Labs audit
- **R3** (Risk 12): DDoS protection + global rate limiting
- **R5** (Risk 12): Audit logging + immutable storage
- **R9** (Risk 12): PII scrubbing в логах
- **R10** (Risk 8): Alert throttling + priority routing

### Фаза 3: Остальные средние риски
- **R6** (Risk 10): Secret management (Vault) + DB TLS
- **R8** (Risk 10): Encryption at rest implementation

---

## Владельцы рисков

| Команда | Количество рисков | Основные задачи |
|---------|-------------------|-----------------|
| @backend-team | 5 | Authorization, input validation, audit logging, encryption, GDPR compliance |
| @devops-team | 4 | Infrastructure security, TLS, DDoS protection, secrets, monitoring |
| @security-team | 1 | Rate limiting, SIEM, security audits, penetration testing |

---

## Метрики и KPI

### Метрики для мониторинга эффективности контролей
1. **Authentication Security**
   - Failed login attempts per IP (target: < 5/min before block)
   - JWT validation failure rate (target: < 0.1%)

2. **Rate Limiting Effectiveness**
   - 429 responses per endpoint (baseline + threshold alerts)
   - Blocked IPs/users per day (target: automated unblock after cooldown)

3. **Authorization**
   - Cross-tenant access attempts (target: 0, alert on any)
   - Authorization failures rate (baseline)

4. **Audit & Logging**
   - Log completeness (target: 100% of CRUD operations logged)
   - Log delivery latency (target: < 5 sec)

5. **Encryption**
   - Encrypted fields coverage (target: 100% of sensitive fields)
   - Key rotation frequency (target: 90 days)

6. **Performance & Availability**
   - p95 latency @ 100 RPS (target: < 200ms per NFR-04)
   - Uptime (target: 99%+ per NFR-06)

---

## Процесс пересмотра рисков

- **Частота**: Ежеквартально или при значительных изменениях архитектуры
- **Триггеры внеочередного пересмотра**:
  - Обнаружение новой уязвимости (CVE)
  - Инцидент безопасности
  - Регуляторные изменения (GDPR, PCI DSS и т.д.)
  - Внедрение новых функций с чувствительными данными

- **Ответственный**: Security team + Product Owner
