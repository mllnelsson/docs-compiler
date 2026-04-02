---
name: mermaid-architecture-diagrams
description: >
  Generate clear, accurate Mermaid diagrams for system and service architecture.
  Use this skill whenever a user wants to visualize, map out, or diagram any system,
  service, or infrastructure — including cloud infrastructure, microservices, network
  topology, data flows, API relationships, deployment layouts, and component dependencies.
  Trigger on phrases like "draw", "diagram", "map out", "show me how X connects to Y",
  "what does our architecture look like", "visualize this system", or any request
  involving Azure services, service meshes, or system design. Use even if the user
  does not explicitly say "diagram" — intent to understand structure is enough.
---

# Mermaid Architecture Diagram Skill

Generate readable, well-structured Mermaid diagrams for system and service architecture,
with conventions tailored for Azure-based infrastructure.

---

## Diagram Type Selection

| Use case | Diagram type |
|---|---|
| General architecture, component layout, service map | `graph TD` or `graph LR` |
| Wide service meshes with many lateral relationships | `graph LR` |
| Layered / tiered architectures (e.g. frontend → backend → DB) | `graph TD` |
| Request flow or interaction order between services | `sequenceDiagram` |
| Formal enterprise / bounded context diagrams | `C4Context` or `C4Container` |

Default to `graph TD` unless the layout clearly benefits from horizontal flow.

---

## Node Conventions

| Node type | Mermaid syntax | Example |
|---|---|---|
| Internal service / app | `[Label]` | `[Order Service]` |
| Database / storage | `[(Label)]` | `[(SQL Database)]` |
| External system / user | `([Label])` | `([Mobile Client])` |
| Queue / message bus | `{{Label}}` | `{{Service Bus}}` |
| Decision / gateway | `{Label}` | `{API Gateway}` |

Keep labels short and human-readable. Use the service's common name, not internal codes or hostnames, unless the user provides them explicitly.

---

## Edge Conventions

- Label all edges that carry meaningful context: `-->|REST/HTTPS|`, `-->|gRPC|`, `-->|reads/writes|`, `-->|publishes|`, `-->|subscribes|`
- Use `-->` for unidirectional flow
- Use `<-->` only when bidirectionality is architecturally significant
- Minimize crossing edges by reordering nodes where possible

---

## Azure Service Conventions

Use these standard labels and groupings for common Azure services:

| Azure service | Suggested label | Node type |
|---|---|---|
| Azure API Management | `[APIM]` | Service |
| Azure App Service / Web App | `[App Service]` | Service |
| Azure Function App | `[Function App]` | Service |
| Azure Kubernetes Service | `[AKS Cluster]` | Subgraph |
| Azure Service Bus | `{{Service Bus}}` | Queue |
| Azure Event Hub | `{{Event Hub}}` | Queue |
| Azure SQL Database | `[(Azure SQL)]` | Database |
| Azure Cosmos DB | `[(Cosmos DB)]` | Database |
| Azure Blob Storage | `[(Blob Storage)]` | Database |
| Azure Key Vault | `[Key Vault]` | Service |
| Azure Active Directory / Entra ID | `([Entra ID])` | External |
| Azure Front Door | `{Front Door}` | Gateway |
| Azure Load Balancer | `{Load Balancer}` | Gateway |
| Azure Virtual Network | subgraph `VNet["Azure VNet"]` | Grouping |

Group Azure resources into subgraphs by resource group or logical boundary where relevant:

```
subgraph RG["Resource Group: prod-rg"]
  [App Service]
  [(Azure SQL)]
end
```

---

## Scope and Assumptions

- If the user describes the system vaguely, make reasonable assumptions and briefly state them before the diagram.
- Default to one level of detail. Do not show implementation internals unless asked.
- If the system is too large for a single diagram, split into logical views (e.g. "network boundary", "data flow", "auth flow") and say so.
- Do not invent services or connections not mentioned or implied by the user.

---

## Output Format

Always wrap the diagram in a mermaid code block:

````
```mermaid
graph TD
  ...
```
````

After the diagram, include a 2–3 sentence summary covering: what the diagram shows, the direction of key data flows, and any assumptions made. Keep it plain and non-technical enough for stakeholders to follow.

---

## Example Prompts That Should Trigger This Skill

- "Can you draw our Azure setup? We have an App Service talking to Cosmos DB through an API gateway."
- "Map out how our microservices communicate."
- "Show me a diagram of our data pipeline from Event Hub to Blob Storage."
- "We use AKS, Service Bus, and Azure SQL — can you visualize that?"
- "What would a typical three-tier Azure web app look like as a diagram?"
