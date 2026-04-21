# Protocolo Git: Worktree por Tarea

Este protocolo define cómo deben gestionarse los cambios en el código para mantener la integridad del canon y la agilidad operativa.

## 1. La Regla de Oro
**NUNCA trabajes directamente en un Clone Base.**
Los clones ubicados en `git-repositories/own/` son fuentes de mantenimiento y deben permanecer limpios.

## 2. Estructura de Trabajo
Para cada tarea, se debe crear un **Git Worktree** independiente:
- **Repositorio**: El clone base correspondiente.
- **Ubicación**: Un directorio efímero fuera del árbol del clone base (preferiblemente en `~/hermes-workspace/`).
- **Rama**: Una rama descriptiva para la tarea (ej: `task/refactor-auth`).

## 3. Ciclo de Vida de una Tarea
1. **Apertura**: Crear el worktree y la rama.
2. **Ejecución**: Realizar los cambios y tests en el worktree.
3. **Commit**: Commitear los cambios desde el worktree.
4. **Promoción**: Realizar el merge o push desde el worktree.
5. **Cierre**: Eliminar el worktree físicamente una vez que la tarea ha sido integrada (`git worktree remove`).

## 4. Ventajas
- **Aislamiento**: Puedes trabajar en múltiples tareas en paralelo sin conflictos de archivos.
- **Limpieza**: El clone base siempre está en un estado conocido y válido.
- **Eficiencia**: No hay necesidad de hacer `stash` o cambiar de rama constantemente.

---
*Disciplina en el flujo, excelencia en el código.*
