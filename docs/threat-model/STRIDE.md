# STRIDE — Анализ угроз и контроли



## Анализ угроз по потокам

### 1. Поток F1: User → API Gateway (POST /auth/login)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **S** (Spoofing) | Атакующий может подделать учётные данные пользователя через брутфорс или credential stuffing | R1 | Rate limiting на эндпоинт /login; сильные пароли; опционально MFA | NFR-03 | Integration tests; Security audit |
| **T** (Tampering) | MITM-атака с перехватом и изменением credentials в transit | R2 | Обязательное использование HTTPS/TLS 1.2+ | NFR-03 | SSL Labs scan; тесты конфигурации TLS |
| **I** (Info Disclosure) | Утечка подробностей об успехе/неудаче аутентификации (username enumeration) | R3 | Унифицированные сообщения об ошибках; rate limiting | NFR-03 | Negative tests; OWASP ZAP scan |
| **D** (DoS) | Массовые попытки логина исчерпывают ресурсы сервера | R1 | Rate limiting; CAPTCHA после N неудачных попыток | NFR-03 | Load tests |

---

### 2. Поток F2: User → API Gateway (GET /companies)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **E** (Privilege Escalation) | Пользователь получает доступ к компаниям других пользователей/организаций | R5 | Authorization checks на уровне ресурса; JWT содержит scope/tenant ID | NFR-03 | Authorization tests; контрактные тесты |
| **I** (Info Disclosure) | Незащищённый эндпоинт раскрывает бизнес-данные | R3 | Обязательная JWT-аутентификация для всех защищённых эндпоинтов | NFR-03 | E2E tests; негативные тесты без токена |
| **D** (DoS) | Массовые запросы перегружают сервис | R4 | Rate limiting 2 req/sec на GET /leads (по аналогии) | NFR-02 | Performance tests @ 100 RPS |

---

### 3. Поток F3: User → API Gateway (POST /companies)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **D** (DoS) | Пользователь создаёт тысячи компаний, исчерпывая storage/ресурсы | R6 | Rate limiting: max 5 компаний за 10 минут; блокировка + алерт | NFR-01 | Rate limit integration tests |
| **T** (Tampering) | Пользователь подделывает поля запроса (например, owner_id) | R5 | Input validation; server-side проверка прав; запрет изменения critical полей через API | NFR-01, NFR-03 | Schema validation tests |
| **R** (Repudiation) | Пользователь отрицает создание компании | R8 | Audit logging всех операций создания с user_id, timestamp | NFR-05 | Audit log tests |

---

### 4. Поток F4: User → API Gateway (GET /leads)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **D** (DoS) | Чрезмерные запросы списка лидов перегружают БД и API | R4 | Rate limiting: 2 req/sec; статус 429 при превышении | NFR-02 | Load tests; негативные тесты с burst requests |
| **I** (Info Disclosure) | Пользователь видит лиды из других компаний | R5 | Tenant/company-based authorization; фильтрация на уровне SQL запроса | NFR-03 | Authorization tests; data isolation tests |
| **E** (Privilege Escalation) | Подмена JWT или повышение scope для доступа к чужим лидам | R5 | Проверка подписи JWT; валидация scope/claims; short-lived access tokens | NFR-03 | JWT validation tests; token expiry tests |

---

### 5. Поток F5: User → API Gateway (PUT/PATCH /leads/:id)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **D** (DoS) | Массовые изменения лидов перегружают систему | R7 | Rate limiting: 5 операций изменения в минуту | NFR-07 | Rate limit tests |
| **T** (Tampering) | Пользователь изменяет лид другого пользователя или подделывает критические поля | R5 | Authorization check перед изменением; input validation; запрет изменения owner без прав | NFR-03, NFR-07 | Authorization tests; input fuzzing |
| **R** (Repudiation) | Пользователь отрицает внесение изменений | R8 | Audit logging всех операций изменения с полным контекстом | NFR-05 | Audit trail tests |

---

### 6. Поток F6: Application Service → Database (TCP/SQL)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **I** (Info Disclosure) | Перехват SQL-трафика в незашифрованном виде | R9 | Использование TLS для DB connections (planned); сетевая изоляция БД | NFR-08 | Network security audit |
| **T** (Tampering) | SQL Injection через некорректную обработку входных данных | R10 | Использование ORM/prepared statements; input sanitization | NFR-03 | Static analysis (Bandit); SQL injection tests |
| **E** (Privilege Escalation) | Компрометация DB credentials даёт полный доступ к данным | R9 | Least privilege DB accounts; secret rotation; credential encryption | NFR-08 | Security audit; secrets management review |

---

### 7. Поток F7: Encryption Service → Database (Encrypted writes)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **I** (Info Disclosure) | Чувствительные данные (refresh_tokens) хранятся в открытом виде | R11 | Encryption at rest (AES-256) для PII-полей | NFR-08 | Encryption tests; проверка невозможности чтения без ключа |
| **T** (Tampering) | Подмена encryption keys или алгоритмов | R12 | Key management system (KMS); ротация ключей; access control на ключи | NFR-08 | Key rotation tests; HSM integration review |
| **E** (Privilege Escalation) | Доступ к encryption keys = доступ ко всем данным | R12 | Строгий RBAC на ключи; audit logging доступа к ключам; HSM | NFR-08 | Access control tests |

---

### 8. Поток F8: Logger → Log Storage (TCP)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **T** (Tampering) | Атакующий удаляет/изменяет логи для сокрытия следов | R8 | Write-only access для приложения; immutable log storage; retention policy | NFR-05 | Log integrity tests |
| **I** (Info Disclosure) | Логи содержат чувствительные данные (PII, tokens) | R13 | Scrubbing PII из логов; structured logging без credentials | NFR-05 | Log content audit; GDPR compliance check |
| **R** (Repudiation) | Отсутствие логов не позволяет доказать действия пользователя | R8 | Централизованное логирование всех критических операций с user_id, timestamp, action | NFR-05 | Audit tests; log completeness check |

---

### 9. Поток F9: Application Service → Metrics (HTTP/gRPC)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **T** (Tampering) | Подделка метрик приводит к ложным представлениям о состоянии системы | R14 | Аутентификация metrics endpoint; read-only access для dashboards | NFR-04, NFR-06 | Metrics integrity tests |
| **D** (DoS) | Перегрузка metrics service приводит к потере observability | R14 | Buffering; backpressure; отдельная инфраструктура для метрик | NFR-06 | Metrics availability tests |
| **I** (Info Disclosure) | Метрики раскрывают бизнес-информацию (количество пользователей, запросов и т.д.) | R15 | Access control на metrics dashboards; aggregation без детализации | NFR-04 | Access control review |

---

### 10. Поток F10: Logger → Alert System (HTTP/SMTP)

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **D** (DoS) | Flood алертов (alert fatigue) или блокировка alert channel | R16 | Alert throttling; priority-based routing; multiple channels | NFR-05 | Alert delivery tests |
| **S** (Spoofing) | Фальшивые алерты вызывают ложные срабатывания | R16 | Подпись алертов; аутентификация источника | NFR-05 | Alert authenticity tests |
| **T** (Tampering) | MITM изменяет содержание алертов | R16 | TLS для SMTP; подписанные сообщения | NFR-05 | Transport security audit |

---

## Дополнительные компоненты

### API Gateway

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **D** (DoS) | Перегрузка API Gateway из-за отсутствия глобальных лимитов | R4 | Global rate limiting; DDoS protection (Cloudflare/AWS Shield) | NFR-02, NFR-07 | Load tests; DDoS simulation |
| **E** (Privilege Escalation) | Обход authentication middleware | R5 | Обязательная авторизация на всех защищённых роутах; fail-secure defaults | NFR-03 | Security audit; negative tests |

### Database

| Угроза (STRIDE) | Описание угрозы | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|------|----------|---------------|-------------------|
| **I** (Info Disclosure) | Резервные копии БД хранятся без шифрования | R11 | Encryption at rest для backups; access control на backups | NFR-08 | Backup encryption tests |
| **D** (DoS) | Отсутствие backups приводит к data loss при сбое | R17 | Automated backups; RPO/RTO targets; disaster recovery plan | NFR-06 | Backup/restore tests |

---

## Сводная таблица покрытия

| Категория STRIDE | Количество угроз | Основные контроли |
|------------------|------------------|-------------------|
| Spoofing (S) | 3 | JWT authentication, MFA, rate limiting |
| Tampering (T) | 7 | HTTPS/TLS, input validation, audit logs, encryption |
| Repudiation (R) | 3 | Centralized audit logging |
| Information Disclosure (I) | 8 | Access control, encryption at rest/in transit, PII scrubbing |
| Denial of Service (D) | 9 | Rate limiting, resource limits, monitoring |
| Elevation of Privilege (E) | 5 | Authorization checks, JWT validation, RBAC |

**Всего проанализировано угроз: 35**

---

## Ссылки на NFR (P03)

- **NFR-01**: Rate limiting для создания компаний (5/10 min)
- **NFR-02**: Rate limiting для GET /leads (2/sec)
- **NFR-03**: JWT-аутентификация для защищённых эндпоинтов
- **NFR-04**: Latency < 200ms @ p95, 100 RPS
- **NFR-05**: Централизованное логирование ошибок и security events
- **NFR-06**: SLA 99% uptime
- **NFR-07**: Rate limiting для изменений лидов/компаний (5/min)
- **NFR-08**: Encryption at rest (AES-256) для чувствительных данных

---
