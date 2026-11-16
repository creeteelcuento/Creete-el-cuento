# Creete-el-cuento

## Objetivo central del proyecto

Desarrollar una plataforma web que centralice y estandarice la gestión de información de mentoras y emprendedoras, facilitando el registro de 
participantes, el control de cobros, la asistencia.

## Funcionalidades

- ✅ Registro de mentoras y emprendedoras
- ✅ Control de cobros y pagos
- ✅ Registro de asistencia

## Instalación

### Inicio sencillo en Windows

Cada integrante debe clonar el repositorio y abrir `iniciar.bat` desde la carpeta
`Creete-el-cuento` (también se puede ejecutar con `.\iniciar.bat` desde PowerShell).
El archivo crea `.venv` local si no existe, instala las dependencias de
`requirements.txt` y ejecuta la aplicación. No es necesario activar el entorno
virtual ni subirlo a GitHub.

La primera ejecución necesita conexión a internet para instalar los paquetes.
Antes de iniciar sesión, cada integrante debe copiar `.env.example` como `.env`
y completar sus datos de Supabase. Comparte las claves de forma segura; no
uses una clave `service_role` ni subas `.env` a GitHub.

### Inicio manual

Desde la carpeta del proyecto, instala las dependencias y ejecuta la aplicación:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe -m streamlit run .\src\lineacodigo.py
```

Ejecuta estos comandos desde la carpeta `Creete-el-cuento`, donde está
`requirements.txt`. El directorio `.venv` es local y no se comparte por GitHub.

### Opcional: pruebas para desarrollo

Este paso no es necesario para abrir la aplicación. Las pruebas comprueban
algunos casos de pagos, autenticación y becas usando datos simulados; no agregan
funciones visibles en la página ni modifican Supabase.

```powershell
python -m unittest discover -s tests -v
```

## Tecnologías Utilizadas

- **Frontend:** HTML, Streamlit
- **Backend:** (Python)
- **Base de datos:** (MySQL, SupaBase)
- **Control de versiones:** Git y GitHub

## Pagos y comprobantes

Los pagos se guardan en la tabla `Pagos` de Supabase y los comprobantes en un
bucket **privado** de Supabase Storage. Configura en `.env`:

```env
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_PAYMENTS_BUCKET=comprobantes-pagos
```

El bucket debe existir y permitir a la aplicación subir y descargar archivos
con las políticas de Storage correspondientes. El campo `comprobante_url` de
`Pagos` guarda la ruta del objeto, no un enlace público. Las transferencias
bancarias requieren comprobante; otros métodos lo permiten de forma opcional.

La aplicación solicita inicio de sesión con Supabase Auth. Crea y confirma las
cuentas autorizadas desde **Authentication → Users** en Supabase; no hay
registro público desde la aplicación. Las políticas del bucket privado deben
aplicarse a `authenticated`. No habilites acceso público para los comprobantes.

El estado visible de una participante se deriva de su membresía vigente o de
una beca exenta, por lo que un valor antiguo como `Pendiente de pago` no oculta
un pago que ya está registrado.

Las donaciones se cargan y guardan en la tabla existente `Donaciones`. Sus
comprobantes opcionales se almacenan en el bucket privado configurado para
pagos. El panel suma las donaciones por fecha del registro.

## Becas

Las participantes cuyo rol en `Participantes` sea `Becada` aparecen en Gestión
de becas y tienen el estado de pago `Becado (exento)`. Al registrar una nueva
becada, el formulario solicita motivo e inicio y término de vigencia. Estos
datos, además de asignaciones, renovaciones y revocaciones, se guardan en la
tabla `Becas`.

Antes de usar la gestión de becas, ejecuta una vez el contenido de
`supabase/migrations/20261113000000_create_becas.sql` en el SQL Editor de
Supabase. La migración crea la tabla con permisos RLS para usuarios
autenticados. Las participantes Becadas antiguas que solo tengan rol, pero no
una asignación formal, seguirán sin fechas hasta que se les asigne una beca
desde Gestión de becas.

## Estructura del Proyecto
```bash
Creete-el-cuento/
── src/              # Código fuente
├── db/               # Base de datos
├── docs/             # Documentación
└── README.md         # Este archivo
```

## Equipo de Desarrollo

- Juan Cardenas - Facilitación de datos y recopilar lo necesario (Bitacoras, reuniones, etc)
- Heidy Calizaya - Creación del código (Frontend/Backend)
- Annais Henriquez - Creación del código (Base de datos)

## Contribuciones

Las contribuciones son bienvenidas. Cada reunión el cual validará nuestros cambios. Cada uno sube antes a su rama personal antes de la rama main. El cual deberá tener precisión y revisión previa. 

### Publicar la app en Streamlit Community Cloud

Conecta el repositorio y selecciona `src/lineacodigo.py` como archivo principal.
En **Advanced settings → Secrets**, agrega la configuracion en formato TOML:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu_clave_anon_o_publishable"
SUPABASE_PAYMENTS_BUCKET = "comprobantes-pagos"
```

La app lee estos valores desde los Secrets de Streamlit Cloud y sigue aceptando
`.env` en el entorno local. Usa una clave `anon`/`publishable` protegida por
politicas RLS; nunca publiques `.env` ni uses una clave `service_role`.
