# Protocolo de Uso del Workspace

Este documento define las reglas de interacción entre el entorno operativo local (`agentic-ai-workspace`) y los recursos canónicos (`agentic-ai-resources`).

## 1. Responsabilidades del Workspace
El workspace es un facilitador. Sus funciones son:
- Mantener la **topología local** (dónde están los repositorios físicamente).
- Gestionar el **estado mutable** (logs, runtime, dist).
- Exponer **entrypoints de conveniencia** para el operador humano y los agentes.

## 2. Acceso a Recursos
- El workspace debe tratar a `agentic-ai-resources` como una dependencia de **solo lectura** para la lógica operativa normal.
- Cualquier "mejora" o cambio propuesto en los recursos debe nacer en el sandbox del workspace y ser promovido mediante la skill `resources-repo-manager`.

## 3. Manejo de Rutas y Paths
- **Prohibición de Paths Absolutos**: No se deben cablear rutas que incluyan el nombre de usuario o rutas de máquina específicas dentro de los recursos.
- **Inyección de Contexto**: El workspace es responsable de informar a las skills sobre la ubicación del `RESOURCES_ROOT`.

## 4. Estructura de Salidas (Output)
- Las carpetas `runtime/` y `dist/` son gestionadas por el workspace. 
- Los builders en `resources` pueden definir la *lógica* de construcción, pero el *destino* físico del artefacto debe ser una ruta configurada en el workspace.

## 5. Sincronización
El workspace debe verificar periódicamente la integridad de su conexión con los recursos utilizando el comando `validate` de la skill `resources-repo-manager`.
