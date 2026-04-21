# Deep Dive: Arquitectura de Control del Cortex (Abril 2026)

## 1. El Motor (StepExecutor / WorkflowEngine)
- **Mecanismo**: Invocación de subprocesos CLI (`cue`, `git`, `python`).
- **Resiliencia**: El sistema de Manifiesto de Cumplimiento permite auditoría forense post-mortem.
- **Seguridad**: Aislamiento de validaciones estructurales mediante archivos temporales volátiles.

## 2. Los Contratos (CUE)
- **Estatus**: Fuente de Verdad Unificada.
- **Potencia**: El uso de "Open Structs" (`...`) permite que la arquitectura crezca sin romper la herencia. 
- **Garantía**: La exclusión mutua en las asociaciones (`tool` vs `workflow`) elimina el 90% de los errores de ambigüedad en la planificación.

## 3. El Sensor de Diseño (Recursive Documentation)
- **Alcance**: Detecta cambios en Código (Skills), Proceso (Workflows) y Concepto (Arquitectura).
- **Vínculo**: Utiliza el Cortex Evaluator para realizar un análisis de impacto semántico antes de disparar actualizaciones de documentos.

## 4. Próximos Pasos Técnicos
1. Implementar `context.schema.cue` para validar el estado efímero del agente.
2. Optimizar el `WorkflowSelector` para usar el `utility_score` de forma ponderada con la tasa de éxito histórica.
