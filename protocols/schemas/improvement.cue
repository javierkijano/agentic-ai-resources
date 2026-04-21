package ecosystem

// Contrato para propuestas de mejora continua
#ImprovementProposal: {
    id: string
    timestamp: string
    source_workflow: string
    category: "performance" | "security" | "reliability" | "documentation" | "architecture"
    description: string
    suggested_action: string
    context_links: [...{
        type: "log" | "manifest" | "source"
        path: string
    }]
    priority?: "low" | "medium" | "high"
    status: "pending" | "analyzed" | "discarded" | "implemented" | *"pending"
    ... // Apertura para datos de diagnóstico extra
}
