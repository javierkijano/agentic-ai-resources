package ecosystem

// Esquema para la Memoria de Trabajo (Contexto) del Agente
#Context: {
    // Estado del entorno local
    workspace_state?: #Topology
    
    // Datos de la última operación
    last_input?:  _
    last_output?: _
    
    // Metadatos de la tarea actual
    task_metadata?: {
        goal: string
        priority: "high" | "medium" | "low" | *"medium"
        iterations: int & >=0 & <=3 | *0
    }

    // Historial de la sesión actual (opcional)
    session_history?: [...{
        step_id: string
        action:  string
        result:  "success" | "failure"
    }]

    ... // Apertura para datos específicos de Skills (ej: data_payload, query_results)
}
