# Agentic Onboarding & Mission

Bienvenido al repositorio central de **Agentic Resources**. Este sistema está diseñado para ser operado por humanos y agentes de forma armoniosa y predecible.

## 📚 Mapa de Lectura Obligatoria
Antes de realizar cualquier cambio o análisis, DEBES procesar estos documentos en el orden indicado para comprender el funcionamiento del repositorio:

1. **`docs/architecture.md`**: Estructura de los 5 pilares (Vendor, Resources, Contexts, Shared, Dist).
2. **`docs/repo-rules.md`**: Las leyes fundamentales (Vendor es Read-Only, Recursos son la Verdad, Dist es Generado).
3. **`docs/conventions.md`**: Estándar de carpetas, esquema de `resource.yaml` e **Interfaces** (CLI/Web).
4. **`docs/lifecycle.md`**: Flujos de trabajo para importar, derivar, crear y buildear recursos.
5. **Descubrimiento de Capacidades**: Utiliza `./scripts/navigator.py list` para catalogar las habilidades (`skills/`), agentes (`agents/`) y conocimiento (`knowledge-packs/`) ya disponibles. No reinventes lo que ya existe.

## 🛠 Contratos de Recurso
Cada capacidad en este repositorio se rige por tres contratos explícitos que encontrarás en la carpeta de cada recurso:
- **Interfaces**: Puntos de entrada definidos en `resource.yaml` (Sección `interfaces`).
- **Almacenamiento (Storage)**: Contrato definido en `core/docs/STORAGE.md`.
- **Seguridad (Credentials)**: Requisitos de secretos definidos en `core/docs/CREDENTIALS.md`.

## 🚀 Protocolo de Operación para Agentes
Para mantener la integridad del sistema, sigue siempre este protocolo:

1. **Investigación**: Valida tus suposiciones leyendo el `resource.yaml` y el `STORAGE.md` del recurso afectado.
2. **Validación**: Ejecuta `./scripts/validate_repo.py` antes de considerar una tarea como completada.
3. **Runtime**: NUNCA escribas logs o estado dentro de las carpetas de recursos. Usa el path normalizado: `runtime/{{agent_id}}/{{env}}/{{resource_id}}/{{session_id}}/`.
4. **Auditoría Local**: Registra tus acciones en el archivo `history.local.md` dentro de la carpeta del recurso. Este archivo está en el `.gitignore` y es para trazabilidad local.
5. **Evolución Orgánica**: Si durante tu ejecución identificas una posible mejora, bug potencial o funcionalidad faltante, DEBES registrarla en `core/docs/TODOs.md`. No la implementes tú mismo a menos que se te pida; limítate a documentar la sugerencia.
6. **Commits**: Utiliza `./scripts/describe_changes.py` para generar mensajes de commit estructurados y descriptivos.

---
**Misión**: Tu objetivo es expandir las capacidades de este hub de forma modular, segura y altamente documentada.
