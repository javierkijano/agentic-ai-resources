# Protocolo de Trazabilidad y Commits

Este documento establece las obligaciones de registro y persistencia para cualquier agente o humano que opere en este ecosistema.

## 1. Registro de Actividad (Logging)
- **Obligatoriedad**: Cada acción significativa (creación de skill, refactorización, cambio de contrato) DEBE generar una entrada en el registro de sesiones del workspace.
- **Ubicación**: Los registros deben almacenarse en la carpeta `runtime/` del workspace actual.
- **Formato**: Se prefiere el uso de `session_registry.jsonl` para trazabilidad automática.

## 2. Política de Commits
- **Frecuencia**: Se debe realizar un commit por cada sub-tarea completada y verificada.
- **Mensajes**: Los mensajes deben ser descriptivos y seguir las convenciones definidas en `docs/conventions.md`.
- **Ramas**: 
    - En el Workspace: Se opera siempre sobre la rama `hermes/dev` o equivalente.
    - En Resources: No se hace commit directo; se proponen cambios mediante el flujo de promoción.

## 3. Validación de Higiene
Antes de cerrar una sesión, el agente debe verificar que:
1. Todos los cambios están commiteados.
2. El log de la sesión ha sido cerrado y persistido.
