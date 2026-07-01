# Guía de Sincronización Offline-First (Frontend)

Este documento define el contrato de comunicación entre la aplicación móvil (Frontend) y el servidor (Backend) para el sistema de logística de Acopio.

## 1. Estrategia de Almacenamiento Local (Zustand + AsyncStorage)

Dado que la aplicación debe funcionar sin conexión a internet, el móvil es la fuente de verdad temporal. 

### Flujo de Trabajo en el Móvil:
1. **El usuario escanea un QR:** Ya sea para armar una caja, sellarla, subirla al camión o recibirla.
2. **Creación del Evento:** El frontend genera un objeto `LogisticaEvent` en memoria. **Importante:** Cada evento debe tener un `event_id` (UUID) generado en el dispositivo y capturar la fecha/hora exacta en `device_timestamp`.
3. **Persistencia Local:** El evento se guarda en una cola (Queue) persistida en `AsyncStorage` usando Zustand (ej. `eventQueue = [...state.eventQueue, newEvent]`).
4. **Optimistic UI:** La interfaz se actualiza inmediatamente para mostrar el éxito de la operación al voluntario, sin esperar a la red.

---

## 2. Proceso de Sincronización (Batch)

Cuando el dispositivo detecta conexión a internet, o cuando el usuario presiona "Sincronizar":

1. Se toman todos los eventos pendientes de la cola local.
2. Se genera un único **`sync_id` (UUID)** para representar este lote. *(Esto es crucial para la idempotencia: si la red se cae durante el envío, puedes reintentar enviar el mismo JSON exacto con el mismo `sync_id` y el backend no duplicará los datos).*
3. Se envía el lote completo al endpoint de sincronización.

### Endpoint

`POST /api/v1/sync`

### Payload Esperado (JSON)

```json
{
  "sync_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "centro_acopio_id": "CAMP-01",
  "events": [
    {
      "event_id": "4b68ef5a-c941-4568-a400-dc97cd3fbc82",
      "package_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "action": "PACK_START",
      "device_timestamp": "2026-06-30T10:00:00Z",
      "operator_name": "Juan Perez",
      "payload": {}
    },
    {
      "event_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "package_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "action": "PACK_ADD_ITEM",
      "device_timestamp": "2026-06-30T10:02:00Z",
      "operator_name": "Juan Perez",
      "payload": {
        "category_id": 5,
        "quantity": 10
      }
    }
  ]
}
```

#### Tipos de Acciones Válidas (`action`)
- `PACK_START`: El voluntario inicia una nueva caja vacía.
- `PACK_ADD_ITEM`: El voluntario mete un ítem en la caja (requiere `category_id` y `quantity` en el campo `payload`).
- `PACK_SEAL`: El voluntario cierra la caja.
- `LOAD_SCAN`: El transportista escanea la caja para subirla al camión.
- `RECEIVE_SCAN`: El centro de destino escanea la caja confirmando la recepción.

*(Nota de Consistencia Eventual: Si un `LOAD_SCAN` llega antes que un `PACK_START` porque los teléfonos sincronizaron a destiempo, el backend creará el paquete automáticamente. ¡El móvil no debe preocuparse por el orden!)*

---

## 3. Manejo de la Respuesta en Frontend

El backend procesa todos los eventos en una sola transacción. Si algunos eventos tienen errores de negocio (ej. identificador vacío), el backend guarda los buenos en la base de datos principal, y los malos en una "Dead-Letter Queue" para auditoría.

### Respuestas del Servidor

**A. Éxito Total o Parcial (`HTTP 200` o `HTTP 207`)**
Si el backend responde con estos códigos, significa que **recibió y guardó** el lote (ya sea como éxito, o mandando las fallas al DLQ). 
* **Acción en Frontend:** Vaciar/Eliminar estos eventos de la cola local de Zustand. ¡Ya no son tu responsabilidad!

```json
{
  "status": "success", // o "partial_success", "all_failed", "duplicate"
  "sync_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "processed": 1,
  "failed": 1,
  "failed_events": [
    {
      "event_id": "5c79a05f-d052-5679-b511-ed08de40cd93",
      "reason": "operator_name is empty"
    }
  ]
}
```

**B. Idempotencia - Reintento Exitoso (`HTTP 200` status: `duplicate`)**
Si el móvil reintenta enviar un `sync_id` que ya había llegado bien.
* **Acción en Frontend:** Vaciar/Eliminar estos eventos de la cola local.

**C. Fallo de Red o Servidor Caído (`HTTP 500+` o Timeout)**
El servidor explotó o no hay internet. El backend hizo un "Rollback" automático, nada se guardó.
* **Acción en Frontend:** **NO** vaciar la cola. Mantener los eventos y volver a intentarlo más tarde con el **mismo** `sync_id`.
