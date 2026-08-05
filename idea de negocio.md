# Idea de negocio — Deja Vu Rent Car

Documento de referencia que resume la visión del producto: sitio web público + panel operativo integrados en un solo sistema.

---

## Objetivo general

Ofrecer a **Deja Vu Rent Car** una presencia web profesional donde los **clientes** descubran la flota, consulten **disponibilidad real** y **reserven en línea**, mientras el equipo sigue operando (reservas, pagos, entregas, reportes) desde el **panel interno** existente.

Todo el contenido público relevante debe poder **configurarse desde el panel**, sin depender de cambios de código para textos, vehículos visibles o políticas básicas.

---

## Dos caras del mismo sistema

| Cara | Usuarios | Propósito |
|------|----------|-----------|
| **Sitio web público** | Clientes (sin login de empleado) | Marketing, catálogo, disponibilidad, reservas online |
| **Panel administrativo** | Administrador y empleados | Operación diaria, configuración del sitio, control de flota y reservas |

Los datos viven en la **misma base de datos**: vehículos, clientes y reservas del panel y de la web son un solo flujo de negocio.

---

## Sitio web público — secciones previstas

### Inicio (Home)

- Presentación de la empresa (textos e imágenes configurables).
- Vehículos o categorías **destacados** (los que el negocio elija mostrar).
- Llamadas a la acción: ver flota, reservar, contacto.

### Páginas de información

- Contenido editable desde el panel, por ejemplo:
  - Quiénes somos / sobre la empresa
  - Servicios y condiciones generales
  - Contacto (teléfono, dirección, horarios, WhatsApp, redes)
  - Otras páginas que el negocio necesite (términos, preguntas frecuentes, etc.)

### Catálogo — todos los vehículos

- Una sección dedicada donde aparezcan **todos los vehículos publicados en web** (no todo el inventario interno, solo lo marcado como visible).
- Vista en tarjetas o listado, con paginación si hace falta.
- **Filtros** para que el cliente elija, entre otros:
  - **Transmisión:** manual, automático (y otros tipos si aplica: CVT, etc.)
  - **Categoría:** sedán, SUV, pick-up, van, lujo (alineado con la operación interna)
  - **Disponibilidad por rango de fechas** (opcional en listado: mostrar solo autos libres entre fecha inicio y fin)
  - Otros filtros futuros: rango de precio, pasajeros, etc.

### Ficha por vehículo

- Fotos, descripción para web, categoría, transmisión, tarifa referencial.
- **Calendario o selector de fechas** con la **disponibilidad real** de ese vehículo (días ocupados vs libres).
- Cálculo estimado del total (días × tarifa diaria).
- Botón para **iniciar reserva** con vehículo y fechas preseleccionados.

### Reserva online

- Formulario con datos del cliente (identificación, contacto, licencia, etc.).
- Validación en servidor: fechas válidas, sin conflicto con otras reservas, licencia vigente, vehículo publicado y operativo.
- Creación de **cliente** y **reserva** en el mismo sistema que usa el panel.
- Mensaje de confirmación al cliente (email o pantalla de éxito; canal a definir en implementación).

---

## Panel administrativo — configuración del negocio web

Desde el panel (módulo tipo **Sitio web / Contenido público**), el negocio controla:

### Vehículos en la web

- Marcar cada vehículo: **visible en web** sí/no.
- Orden de aparición en home y en catálogo.
- Texto e imágenes orientados al público (puede reutilizar o complementar la ficha interna).
- **Transmisión** (manual / automático / etc.) — campo a incorporar en flota si no existe.
- Tarifa mostrada (normalmente la misma tarifa diaria interna).

### Contenido del sitio

- Textos del home, banners, enlaces.
- Páginas informativas (nosotros, contacto, cláusulas visibles al cliente).
- Datos de empresa (nombre, teléfono, dirección, RNC, etc.) coherentes con contratos y web.

### Políticas de reserva web (a definir en implementación)

- Estado inicial de la reserva: **pendiente de confirmación** por empleado vs **confirmación automática** si hay disponibilidad.
- Depósito requerido al reservar vs pago total en sucursal.
- Anticipación mínima (ej. no reservar con menos de 24 h).
- Si los días en **mantenimiento** bloquean disponibilidad en la web.

---

## Integración con la operación actual

El sistema interno ya contempla:

- Clientes, vehículos, reservas con estados y validación de solapamiento de fechas.
- Pagos, depósitos, entrega y devolución, contratos, calendario, reportes.
- Roles administrador / empleado y permisos por módulo.

La web pública **reutiliza** esas reglas de negocio (disponibilidad, precios, conflictos) y añade:

- Rutas y diseño orientados al cliente.
- Campos y pantallas de **publicación** y **contenido**.
- Posible identificación de reservas originadas en **web** (filtro o etiqueta en el panel).

---

## Flujo del cliente (resumen)

1. Entra al sitio → conoce la empresa (home / información).
2. Va a **Vehículos** → filtra (ej. automático, SUV) → elige un auto.
3. En la ficha ve **fechas disponibles** → selecciona inicio y fin.
4. Completa datos y envía la **reserva**.
5. Recibe confirmación; el negocio ve la reserva en el panel y continúa el proceso habitual (confirmación, pago, entrega).

---

## Decisiones pendientes (antes o durante la implementación)

- Confirmación manual vs automática de reservas web.
- Pago en línea (depósito con tarjeta/transferencia) vs solo reserva y cobro en sucursal.
- Cuenta de cliente (“mis reservas”) o solo reserva como invitado en una primera versión.
- Bloqueo de fechas por mantenimiento además de reservas.
- Notificaciones (email, WhatsApp) al cliente y al negocio cuando llega una reserva web.

---

## Alcance sugerido por fases (orientativo)

**Fase 1 — Presencia y catálogo**

- Sitio público: home, información, contacto, listado de vehículos con filtros (transmisión, categoría).
- Panel: visible en web, transmisión, contenido básico de páginas.

**Fase 2 — Disponibilidad y reserva**

- Ficha con calendario/disponibilidad por vehículo.
- Formulario de reserva integrado al panel (estado y políticas acordadas).

**Fase 3 — Mejoras**

- Pago online, cuenta cliente, notificaciones, SEO, analytics, etc.

---

## Nombre del documento

**Idea de negocio** — visión acordada para Deja Vu Rent Car: web configurable + catálogo completo con filtros + disponibilidad por vehículo + reserva online, unificado con el panel operativo.

*Última actualización: documento creado a partir de la definición conjunta del producto.*
