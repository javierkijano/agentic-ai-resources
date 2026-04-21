package ecosystem

#Skill: #Metadata & {
    kind: "skill"
    status: "active" | "deprecated" | "dev"
    tags?: [...string]
    platforms?: [...string]
    
    interfaces: {
        cli?: {
            enabled: bool
            commands: {
                [string]: string
            }
        }
        api?: {
            enabled: bool
            endpoints: {
                [string]: string
            }
        }
    }
    
    // Punteros a esquemas de validación de datos
    input_schema?: string
    output_schema?: string
    
    storage?: {
        standard_layout: bool
        description?: string
        contract?: string
    }
    
    dependencies?: {
        resources?: [...string]
        system?: [...{id: string, version: string}]
        packages?: [...string]
    }
}
