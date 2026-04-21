# Agentic Resources - Canonical Gateway

Bienvenido a la fuente de verdad. Este repositorio contiene el ADN del sistema.

## 🏛 Responsabilidades del Canon
- **Definir Skills**: Lógica pura y contratos.
- **Protocolos**: Las leyes del ecosistema (ver `/protocols`).
- **Validación**: Asegurar que nada rompa la integridad del sistema.

## 🛠 Herramientas de Gobernanza
Para interactuar con el canon, usa la skill `resources-repo-manager`:
- `validate`: Comprobar integridad del repo.
- `create`: Generar nuevos recursos siguiendo el estándar.
- `explore`: Navegar por el mapa de inteligencia.

## 📂 Estructura Crítica
- `resources/skills/`: El corazón funcional. Cada carpeta es una capacidad aislada.
- `protocols/`: Lectura obligatoria para entender la disciplina Git y de logging.
- `docs/architecture.md`: La visión técnica detrás de este diseño.

## 🚨 Reglas de Oro
1. **No toques el Clone Base**: Usa `task.py` desde el Workspace para crear un worktree.
2. **Sin Estado Local**: Nunca commitees archivos `runtime/` o logs locales en este repositorio.
3. **Contratos sobre Código**: Define siempre la interfaz en `resource.yaml` antes de implementar.
