Requerimientos:

Funcionales:

Módulo 1: Gestión de usuarios y registro

| Número | Requerimiento | Prioridad | Estado |
| ----- | ----- | ----- | ----- |
| RF-01 | El sistema debe permitir el registro de participantes mediante un formulario web que capture: nombre completo, correo electronico, telefono, pais, rol (mentora/emprendedora/becada), descripción profesional | Alta | Validado |
| RF-02 | El sistema debe validar automáticamente que el correo electrónico ingresado tenga un formato válido y que no esté duplicado en la base de datos | Alta | Validado |
| RF-03 | El sistema debe clasificar automáticamente al participante según el rol seleccionado durante el registro, asignándole al flujo de proceso correspondiente (Mentora → validación de perfil; Emprendedora → pago directo; Becada → evaluación de beca).  | Alta | Validado |

Módulo 2: Gestión de membresías y pagos

| Número | Requerimiento | Prioridad | Estado |
| ----- | ----- | ----- | ----- |
| RF-05 | El sistema debe registrar automáticamente la fecha de inicio de la membresía al confirmar el pago, y calcular la fecha de vencimiento | Alta | Validado |
| RF-06 | El sistema debe generar una alerta automática cuando falten 15 días o menos para el vencimiento de una membresía, enviando notificación por correo electrónico al participante y a la Coordinadora.  | Alta | Validado |
| RF-07 | El sistema debe permitir registrar el estado de pago de cada participante con los siguientes estados: Pendiente, por vencer, pagado y Becado (Exento) | Alta | Validado |
| RF-08 | El sistema debe permitir a la Coordinadora registrar manualmente un pago cuando se realiza por transferencia bancaria, subiendo el comprobante como evidencia | Alta | Validado |
| RF-09 | El sistema debe generar un historial de pagos por participante, mostrando fecha, monto, método de pago y comprobante asociado | Alta | Validado |

Módulo 3: Gestión de asistencias

| Número | Requerimiento | Prioridad | Estado |
| ----- | ----- | ----- | ----- |
| RF-10 | El sistema debe permitir marcar la asistencia de participantes a actividades (talleres, mentorías, charlas) mediante un registro manual en una matriz | Alta | Validado |
| RF-12 | El sistema debe calcular automáticamente el porcentaje de asistencia de cada participante | Media | Validado |

Módulo 4: Gestión de becas

| Número | Requerimiento | Prioridad | Estado |
| ----- | ----- | ----- | ----- |
| RF-14 | El sistema debe diferenciar claramente entre participantes becadas y no becadas, mostrando un indicador visual (badge/etiqueta) en el perfil y listados | Media | Validado |
| RF-15 | El sistema debe permitir a la Coordinadora asignar o revocar una beca a un participante, registrando el motivo, fecha y período de vigencia | Alta | Validado |

Módulo 6: Dashboard y reportes

| Número | Requerimiento | Prioridad | Estado |
| ----- | ----- | ----- | ----- |
| RF-20 | El sistema debe mostrar un dashboard con métricas clave: total de participantes activos, membresías por vencer (próximos 15 días), % de asistencia promedio, becas activas vs. revocadas, ingresos por membresías | Alta | Validado |
| RF-21 | El sistema debe permitir visualizar el estado de pago de cada participante en su ficha individual, con indicador visual (verde=pagado, amarillo=por vencer, rojo=vencido, morado \= becada) | Alta | Validado |

Requerimientos no funcionales:

| Número | Requerimiento | Categoría | Estado |
| ----- | ----- | ----- | ----- |
| RNF-01 | La interfaz de usuario debe ser simple e intuitiva, con botones visibles, formularios claros y navegación consistente, permitiendo conocimientos técnicos. | Usabilidad | Validado |
| RNF-02 | El sistema debe ejecutarse en navegador web, siendo accesible desde el dispositivo utilizado | Compatibilidad /Accesibilidad | Validado |
| RNF-03 | El sistema debe permitir agregar nuevos participantes, sin afectar el rendimiento, manteniendo tiempos de respuesta inmediata | Escalabilidad/Rendimiento | Validado |
| RNF-04 | El sistema debe utilizar la paleta de colores corporativa de Creete el Cuento: tonos pasteles en amarillo, dorados, blancos, como colores principales, tipografía legible y diseño coherente con identidad visual de la marca | Diseño/Identidad | Validado |
| RNF-05 | El sistema debe permitir la carga de archivos que sean necesarios subir | Capacidad | Validado |
| RNF-06 | El sistema debe registrar un historial de acciones que permita saber quién realizó cada cambio, qué modificó y cuándo, para garantizar trazabilidad | Trazabilidad | Validado |
