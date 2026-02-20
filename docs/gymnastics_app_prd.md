# PRD — App Web + Móvil (PWA) para Gimnasia Artística

## 1) Resumen del producto
Plataforma integral para gestión operativa de un gimnasio de gimnasia artística, orientada a entrenadoras, recepción y administración.
Incluye panel web y experiencia móvil/PWA para uso en entrenamiento diario.

### Objetivos
- Centralizar datos de alumnas, tutores, salud y contactos de emergencia.
- Organizar grupos por días/horarios recurrentes y asignación de alumnas.
- Registrar asistencia por clase con estados ampliados (Presente, Ausente, Tarde, Justificada) y motivo.
- Proveer historial, reportes y exportaciones (CSV/Excel).

### Métricas de éxito (KPIs)
- 95% de clases con asistencia cargada dentro de las 24h.
- Reducción del tiempo de toma de asistencia a < 3 minutos por grupo.
- 0 pérdida de información de contacto/emergencia.
- Exportación de reportes en < 10 segundos para rangos de hasta 12 meses.

---

## 2) Alcance funcional (MVP)

### 2.1 Gestión de alumnas y tutores
**Debe permitir:**
- Alta/edición/baja lógica de alumnas.
- Datos mínimos de alumna:
  - Nombre y apellido
  - Fecha de nacimiento
  - Documento
  - Nivel (inicial/intermedio/avanzado/competitivo)
  - Fecha de ingreso
  - Estado (activa/inactiva)
  - Notas internas
- Salud/emergencia:
  - Obra social/seguro
  - Condiciones médicas relevantes
  - Alergias
  - Medicación
  - Restricciones físicas
  - Contacto de emergencia principal
- Asociación de **1 o más tutores** por alumna:
  - Nombre, vínculo, teléfono, email, preferencia de contacto
  - Permitir marcar tutor principal para comunicación administrativa

### 2.2 Grupos y horarios recurrentes
**Debe permitir:**
- Crear grupos (ej. “Pre-Infantil A”, “Juveniles Competitivo”).
- Configurar recurrencia semanal por días y horarios (ej. Lunes/Miércoles 18:00–19:30).
- Definir sede/salón/capacidad/entrenadora a cargo.
- Asignar y remover alumnas de grupos.
- Validar conflictos (alumna en dos grupos superpuestos).

### 2.3 Asistencia
**Debe permitir:**
- Tomar asistencia por grupo y fecha.
- Estados por alumna:
  - Presente
  - Ausente
  - Tarde
  - Justificada
- Campo de motivo (obligatorio para Ausente/Justificada, opcional para Tarde).
- Carga rápida (checklist masivo + edición individual).
- Historial por alumna y por grupo.
- Reportes por período, nivel, entrenadora, estado.
- Exportar a CSV y Excel.

---

## 3) Mejoras sugeridas (Roadmap)

### 3.1 Pagos
- Gestión de cuotas mensuales, vencimientos y estados.
- Integración con pasarelas (Mercado Pago/Stripe) o registro manual.
- Recordatorios automáticos de vencimiento.
- Reporte de morosidad por grupo.

### 3.2 Notificaciones
- Notificaciones push/email/WhatsApp (según política del gimnasio).
- Alertas por inasistencia reiterada.
- Avisos de suspensión/reprogramación de clases.

### 3.3 Progreso por aparatos
- Seguimiento técnico por aparato:
  - Suelo
  - Viga
  - Barras
  - Salto
- Evaluaciones periódicas con rúbricas y niveles.
- Evolución con gráficos y observaciones para tutores.

---

## 4) Roles y permisos

### Admin
- Control total del sistema.
- Configuración de usuarios, roles, sedes, catálogos.
- Acceso a todos los reportes y exportaciones.
- Gestión de pagos (si módulo activo).

### Entrenador/a
- Ver grupos asignados.
- Gestionar asistencia de sus grupos.
- Ver ficha de alumna (incluyendo alertas de salud relevantes).
- Cargar notas de progreso técnico.

### Recepción
- Alta inicial de alumnas y tutores.
- Actualización de contactos y documentación.
- Consulta de estado de asistencia e información administrativa.
- Gestión operativa de pagos (si aplica), sin permisos de configuración avanzada.

---

## 5) User stories (MVP)

1. **Como recepción**, quiero registrar una nueva alumna con sus tutores para tener su ficha completa desde el primer día.
2. **Como recepción**, quiero adjuntar datos de salud/emergencia para actuar rápido ante incidentes.
3. **Como admin**, quiero crear grupos con días/horarios recurrentes para planificar la grilla mensual.
4. **Como admin**, quiero asignar alumnas a grupos evitando superposiciones para reducir errores operativos.
5. **Como entrenadora**, quiero tomar asistencia desde el celular en menos de 3 minutos para no perder tiempo de entrenamiento.
6. **Como entrenadora**, quiero marcar “Justificada” con motivo para diferenciar ausencias avisadas.
7. **Como admin**, quiero consultar reportes de asistencia por período y nivel para analizar retención.
8. **Como admin/recepción**, quiero exportar CSV/Excel para compartir datos con contabilidad/dirección.
9. **Como tutor (futuro portal)**, quiero recibir notificaciones de inasistencias para dar seguimiento.
10. **Como admin**, quiero ver historial completo de una alumna para evaluar continuidad y compromiso.

---

## 6) Requisitos no funcionales
- **Seguridad:** control de acceso por rol, cifrado en tránsito (HTTPS), auditoría de cambios.
- **Privacidad:** cumplimiento normativo local para datos personales y de salud.
- **Disponibilidad:** objetivo 99.5% mensual.
- **Performance:** registro de asistencia para grupos de hasta 40 alumnas sin latencia perceptible.
- **Usabilidad móvil:** PWA responsive, offline-first para asistencia (sincronización posterior).

---

## 7) Modelo de datos (propuesto)

### Entidades principales
- **User**(id, name, email, password_hash, role, status, created_at)
- **Role**(id, key: admin|coach|reception)
- **Student**(id, first_name, last_name, birth_date, document_id, level, join_date, status, notes)
- **StudentHealthProfile**(id, student_id, insurance, medical_conditions, allergies, medications, physical_restrictions, emergency_notes)
- **Guardian**(id, first_name, last_name, relationship, phone, email, preferred_contact_channel)
- **StudentGuardian**(id, student_id, guardian_id, is_primary, legal_authorization)
- **Venue**(id, name, address)
- **Group**(id, name, level, venue_id, capacity, coach_user_id, active)
- **GroupSchedule**(id, group_id, weekday, start_time, end_time, timezone, recurrence_rule)
- **GroupEnrollment**(id, group_id, student_id, start_date, end_date, status)
- **AttendanceSession**(id, group_id, class_date, schedule_id, created_by, closed_at)
- **AttendanceRecord**(id, session_id, student_id, status, reason, marked_at, marked_by)
- **AttendanceStatusCatalog**(id, key: present|absent|late|justified)
- **AuditLog**(id, actor_user_id, entity, entity_id, action, payload_json, created_at)

### Relaciones clave
- Student 1—1 StudentHealthProfile
- Student N—N Guardian (vía StudentGuardian)
- Group 1—N GroupSchedule
- Group N—N Student (vía GroupEnrollment)
- AttendanceSession 1—N AttendanceRecord

### Índices sugeridos
- `attendance_session(group_id, class_date)`
- `attendance_record(session_id, student_id)` único
- `group_schedule(group_id, weekday)`
- `group_enrollment(student_id, status)`

---

## 8) Pantallas y navegación

### Web (admin/recepción/entrenadora)
1. **Login**
2. **Dashboard**
   - métricas rápidas: asistencia semanal, ausencias, tardanzas
3. **Alumnas**
   - listado + filtros + alta/edición
   - pestañas: Datos / Salud / Tutores / Historial
4. **Tutores**
   - listado y vinculación con alumnas
5. **Grupos**
   - listado, calendario semanal, asignaciones
6. **Asistencia**
   - selector grupo + fecha
   - grilla de estados y motivos
7. **Reportes**
   - tablas/gráficos + exportación CSV/Excel
8. **Configuración**
   - usuarios, roles, catálogos

### Móvil/PWA (entrenadora y recepción)
1. **Inicio rápido** (grupos de hoy)
2. **Tomar asistencia** (modo optimizado táctil)
3. **Ficha resumida de alumna** (alertas de salud visibles)
4. **Historial simple**
5. **Sincronización offline/online**

---

## 9) Stack recomendado

### Frontend
- **Web:** Next.js (React + TypeScript)
- **UI:** TailwindCSS + componente accesible (Radix/UI o shadcn/ui)
- **Mobile/PWA:** misma base Next.js con capacidades PWA (Service Worker + manifest)

### Backend
- **API:** NestJS o FastAPI (preferencia: NestJS si equipo JS fullstack)
- **Auth:** JWT + refresh tokens + RBAC por rol
- **ORM:** Prisma (si Node) o SQLModel/SQLAlchemy (si Python)

### Base de datos e infraestructura
- **DB:** PostgreSQL
- **Cache/colas opcional:** Redis (notificaciones, trabajos async)
- **Storage:** S3-compatible para adjuntos/documentación
- **Deploy:** Vercel (frontend) + Render/Fly.io/AWS (backend)
- **Observabilidad:** Sentry + logs estructurados + métricas (OpenTelemetry)

### Exportación
- CSV nativo y Excel con librería tipo SheetJS/ExcelJS.

---

## 10) Plan de implementación sugerido
1. **Sprint 1:** Auth + roles + CRUD alumnas/tutores + datos de salud.
2. **Sprint 2:** Grupos + horarios recurrentes + asignaciones + validaciones de solapamiento.
3. **Sprint 3:** Asistencia móvil/PWA + historial.
4. **Sprint 4:** Reportes + exportaciones + hardening seguridad/auditoría.
5. **Sprint 5 (mejoras):** pagos + notificaciones + progreso por aparatos.

---

## 11) Riesgos y mitigaciones
- **Datos sensibles de salud:** políticas estrictas de acceso y auditoría.
- **Conectividad en sala:** modo offline para asistencia.
- **Adopción de usuarios:** UX simplificada, capacitación inicial y plantillas de carga.
- **Calidad de datos:** validaciones, campos obligatorios y deduplicación por documento.
