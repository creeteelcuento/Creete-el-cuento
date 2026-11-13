\# AGENTS.md · Reglas del proyecto

\> Copie este archivo en la raíz del repositorio como \`AGENTS.md\`. Apruébelo mediante Pull Request antes de comenzar el desarrollo.

\#\# 1\. Propósito y alcance

Este repositorio corresponde al proyecto \*\*Creete el Cuento\*\*, una plataforma web para la gestión de participantes (mentoras, emprendedoras y becadas), membresías, pagos, asistencias, becas y reportes.

\*\*Audiencia:\*\* Estudiantes, desarrolladores, agentes de IA y herramientas automatizadas que colaboren en el código, documentación o pruebas del proyecto.

\*\*Objetivo del sistema:\*\* Centralizar la operación de Creete el Cuento, garantizando trazabilidad, usabilidad y coherencia con la identidad visual de la marca.

\---

\#\# 2\. Fuentes de verdad

1\. \`main\` contiene la versión oficial validada del proyecto.  
2\. \`docs/\` contiene los requerimientos funcionales (RF) y no funcionales (RNF) validados.  
3\. \`src/\` contiene el código fuente organizado por módulos.  
4\. \`tests/\` contiene las pruebas unitarias y de integración.  
5\. El documento \*\*"Información para el Agents.docx"\*\* es la referencia oficial de requerimientos.  
6\. Ante cualquier contradicción entre código y requerimientos, \*\*se detiene el cambio y se consulta al equipo o docente\*\*.

\---

\#\# 3\. Reglas del dominio

\#\#\# 3.1 Participantes y roles

\- Existen \*\*tres roles únicos\*\*: \`Mentora\`, \`Emprendedora\`, \`Becada\`.  
\- Cada participante se registra con: nombre completo, correo electrónico, teléfono, país, rol y descripción profesional.  
\- \*\*No se inventan participantes ni datos personales.\*\*  
\- El correo electrónico debe validarse automáticamente (formato válido \+ no duplicado).  
\- El flujo de proceso depende del rol:  
  \- \*\*Mentora\*\* → validación de perfil.  
  \- \*\*Emprendedora\*\* → pago directo.  
  \- \*\*Becada\*\* → evaluación de beca.

\#\#\# 3.2 Membresías y pagos

\- Estados de pago permitidos: \`Pendiente\`, \`Por vencer\`, \`Pagado\`, \`Becado (Exento)\`.  
\- \*\*No se almacenan datos bancarios completos ni credenciales de pago.\*\*  
\- Los pagos por transferencia bancaria requieren comprobante subido como evidencia.  
\- El sistema calcula automáticamente la fecha de inicio y vencimiento de la membresía.  
\- Se genera alerta automática a los \*\*15 días o menos\*\* antes del vencimiento (notificación por correo al participante y a la Coordinadora).  
\- Se mantiene un historial de pagos por participante (fecha, monto, método, comprobante).

\#\#\# 3.3 Becas

\- El sistema diferencia visualmente a becadas y no becadas mediante un \*\*badge/etiqueta\*\* en perfil y listados.  
\- Solo la \*\*Coordinadora\*\* puede asignar o revocar una beca, registrando motivo, fecha y período de vigencia.  
\- Una participante becada tiene estado de pago \`Becado (Exento)\`.

\#\#\# 3.4 Asistencias (sistema matrix)

\> ⚠️ \*\*Importante:\*\* El sistema \*\*NO utiliza código QR\*\* para marcar asistencia. Se reemplazó por un sistema de \*\*tabla/matrix de asistencia\*\*.

\- La asistencia se gestiona mediante una \*\*matriz visual\*\* donde:  
  \- \*\*Filas\*\* \= participantes (nombre, rol, país).  
  \- \*\*Columnas\*\* \= actividades (nombre, fecha, tipo: Charla-Online / Mentoria-Presencial / Coaching-Presencial, etc.).  
  \- \*\*Celdas\*\* \= estado de asistencia:  
    \- ✅ \*\*Presente\*\* (check verde).  
    \- ❌ \*\*Ausente\*\* (cruz roja).  
\- La fila inferior muestra el \*\*conteo de presentes por actividad\*\* (ej: \`3/7\`, \`4/7\`, \`5/7\`).  
\- Acciones disponibles:  
  \- \*\*\`+ Nueva actividad\`\*\*: crear una nueva columna de actividad.  
  \- \*\*\`Últimas 6 actividades\`\*\*: filtro dropdown para limitar la vista a las 6 actividades más recientes.  
  \- \*\*\`Exportar CSV\`\*\*: descargar la matriz de asistencia en formato CSV.  
\- El sistema calcula automáticamente el \*\*% de asistencia\*\* por participante.  
\- \*\*No se implementa generación ni lectura de códigos QR\*\* (fuera del alcance del proyecto).

\#\#\# 3.5 Dashboard y reportes

\- Métricas clave: total de participantes activos, membresías por vencer (próximos 15 días), % de asistencia promedio, becas activas vs. revocadas, ingresos por membresías.  
\- Indicadores visuales de estado de pago:  
  \- 🟢 Verde \= Pagado  
  \- 🟡 Amarillo \= Por vencer  
  \- 🔴 Rojo \= Vencido  
  \- 🟣 Morado \= Becada

\---

\#\# 4\. Identidad visual y diseño

\- \*\*Paleta corporativa obligatoria:\*\* tonos pasteles en \*\*amarillo, dorados y blancos\*\* como colores principales.  
\- Tipografía legible y diseño coherente con la identidad visual de Creete el Cuento.  
\- Interfaz simple e intuitiva: botones visibles, formularios claros, navegación consistente.  
\- \*\*No se usan colores fuera de la paleta corporativa\*\* sin autorización.

\---

\#\# 5\. Git y Pull Requests

\- Cada estudiante utiliza una \*\*única rama permanente\*\*: \`student/\<username\>\`.  
\- \*\*No se crean ramas nuevas por encuentro.\*\*  
\- \*\*No se hace push directo a \`main\`.\*\*  
\- Antes de trabajar, se actualiza \`main\` y se integra en la rama personal.  
\- Todo aporte llega a \`main\` mediante \*\*Pull Request\*\*.  
\- Se exige al menos \*\*una aprobación formal\*\* de otra persona.  
\- Las correcciones se realizan en la misma rama y el mismo Pull Request.  
\- El jefe, jefa o docente puede realizar el merge después de la aprobación.  
\- Los commits deben ser claros, atómicos y referenciar el RF/RNF correspondiente cuando aplique (ej: \`feat(RF-03): clasificación automática por rol\`).

\---

\#\# 6\. Privacidad y datos

\- \*\*No se suben\*\* datos personales reales, tokens, secretos ni archivos \`.env\`.  
\- Los archivos \`.env\` y credenciales deben estar en \`.gitignore\`.  
\- Se recolecta únicamente la información necesaria para el proyecto (nombre, correo, teléfono, país, rol, descripción profesional).  
\- Las evidencias de pago (comprobantes) se almacenan con acceso restringido.  
\- El historial de acciones garantiza trazabilidad: quién, qué y cuándo (RNF-06).

\---

\#\# 7\. Uso supervisado de IA

\- La IA puede apoyar ideas, redacción, análisis y código; \*\*no sustituye la validación humana ni inventa requerimientos\*\*.  
\- Toda salida de IA se revisa contra los RF/RNF validados y las pruebas.  
\- Se declara qué herramienta se utilizó, para qué y qué verificó una persona.  
\- Ningún dato real o confidencial de participantes se entrega a una herramienta de IA.  
\- Un agente \*\*no elimina ni sobrescribe\*\* trabajo ajeno sin autorización explícita.

\---

\#\# 8\. Verificación mínima antes de solicitar revisión

Antes de abrir un Pull Request, confirme:

\- ✅ Rutas y alcance del cambio son correctos.  
\- ✅ Pruebas unitarias y de integración pasan.  
\- ✅ No existen datos sensibles ni \`.env\` en el commit.  
\- ✅ Documentación afectada está actualizada.  
\- ✅ Commits son claros y referencian RF/RNF cuando aplica.  
\- ✅ Se respeta la paleta de colores corporativa (amarillo, dorados, blancos).  
\- ✅ Se registró el uso de IA, cuando corresponda.  
\- ✅ El cambio no rompe la trazabilidad del historial de acciones (RNF-06).

\---

\#\# 9\. Límites de modificación

\- Los requerimientos validados \*\*no se modifican\*\* sin aprobación formal.  
\- Los RF con estado \`Por validar\` (ej: RF-10) no se implementan como definitivos hasta su validación.  
\- No se realizan cambios masivos, destructivos o fuera del alcance solicitado.  
\- Ante dudas sobre permisos, privacidad o alcance, \*\*consultar antes de actuar\*\*.

\---

\#\# 10\. Referencia rápida de requerimientos

\| Módulo \| RF clave \| Descripción \|  
\|---\|---\|---\|  
\| 1\. Usuarios \| RF-01, RF-02, RF-03 \| Registro, validación de correo, clasificación por rol \|  
\| 2\. Membresías \| RF-05 a RF-09 \| Pagos, alertas de vencimiento, historial \|  
\| 3\. Asistencias \| RF-10, RF-12 \| \*\*Matrix de asistencia (✓/✗) por participante y actividad. Sin QR.\*\* Cálculo de % de asistencia. \|  
\| 4\. Becas \| RF-14, RF-15 \| Diferenciación visual, asignación/revocación \|  
\| 6\. Dashboard \| RF-20, RF-21 \| Métricas clave e indicadores de estado \|

\*\*RNF críticos:\*\* Usabilidad (RNF-01), Compatibilidad web (RNF-02), Escalabilidad (RNF-03), Paleta corporativa (RNF-04), Carga de archivos (RNF-05), Trazabilidad (RNF-06).

\#\#11 Requerimientos 

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
| RF-09 | El sistema debe generar un historial de pagos por participante, mostrando fecha, monto, método de pago y comprobante asociado. | Alta | Validado |

Módulo 3: Gestión de asistencias

| Número | Requerimiento | Prioridad | Estado |
| ----- | ----- | ----- | ----- |
| RF-10 | El sistema debe permitir marcar la asistencia de participantes a actividades mediante matriz matrix | Alta | Por validar |
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

\> 📌 \*\*Nota para agentes de IA:\*\* Antes de generar código, consulte siempre este archivo y el documento de requerimientos. Priorice los RF con estado \`Validado\` y respete la identidad visual de Creete el Cuento. \*\*No implemente código QR bajo ninguna circunstancia.\*\*  
