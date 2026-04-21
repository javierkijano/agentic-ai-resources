package ecosystem

#Association: {
    strength: >=0.0 & <=1.0
    // Exclusión mutua estricta: No puede tener 'tool' y 'workflow' al mismo tiempo
    { tool: string, workflow?: _|_ } | { workflow: string, tool?: _|_ }
}

#StepValidation: {
    input_schema?:  string
    output_schema?: string
}

#Step: {
    id: string
    intent: string
    associations: [...#Association]
    validation?: #StepValidation
}

#StateValidation: {
    pre_state_schema?:  string
    post_state_schema?: string
}

#Workflow: #Metadata & {
    kind: "workflow"
    status: "core" | "dev" | "archive" | "deprecated"
    utility_score: >=0 & <=100 | *50
    
    // Semántica pura para el LLM
    preconditions: [...string]
    postconditions: [...string]
    
    // Validación estructural y de estado (Máquina/CUE)
    state_validation?: #StateValidation
    
    steps: [...#Step]
}
