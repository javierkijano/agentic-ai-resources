package ecosystem

// Patrón abierto para entidades dinámicas en el Workspace
#Project: {
    id: string
    path: string
    role: string
    description?: string
    tags?: [...string]
}

#Topology: {
    workspace: {
        id: string
        owner: string
        description?: string
    }
    links?: {
        resources?: {
            path: string
            role: string
        }
        worktrees?: {
            [string]: string
        }
    }
    
    // Estructuras dinámicas: Conjunto abierto de proyectos
    projects?: [...#Project]
    
    storage?: {
        runtime?: string
        dist?: string
        data?: string
    }
    
    agents_active?: [...{id: string, profile: string}]
}

#Paths: {
    variables: {
        AGENTIC_RESOURCES: string
    }
    paths: {
        runtime: string
        dist: string
        data: string
    }
}
