# Skill: Repository Manager

Esta skill permite a un agente gestionar la estructura y el ciclo de vida del repositorio de recursos agénticos.

## Herramientas

### validate_repo
Valida que la estructura del repositorio y los metadatos de los recursos sean correctos.
- **Comando**: `python3 resources/skills/repository-manager/core/validate_repo.py`

### create_resource
Crea un nuevo pack de recurso con la estructura estándar.
- **Comando**: `python3 resources/skills/repository-manager/core/create_resource.py --type <type> --id <id>`
- **Argumentos**:
    - `type`: Categoría (skills, agents, workflows, etc.)
    - `id`: ID único en kebab-case.

### build_platform
Genera una distribución preparada para una plataforma específica.
- **Comando**: `python3 resources/skills/repository-manager/core/build_platform.py --platform <platform>`

### install_hermes
Instala los recursos construidos en el entorno de Hermes.
- **Comando**: `python3 resources/skills/repository-manager/core/install_hermes.py`

## Instrucciones de Uso
- Valida siempre el repositorio después de crear o modificar recursos.
- No edites directamente archivos en `vendor/`.
- Asegúrate de que cada nuevo recurso tenga su `resource.yaml` correctamente cumplimentado.
