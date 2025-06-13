# Processus de pré-traitement des documents

```mermaid
flowchart
    D["Documents bruts (json, pdf, md)"]
    P["Suppression des caractères superflus"]
    P2["Suppression des caractères spéciaux et stopwords"]
    L["Stemming"]
    D-->P
    P-->P2
    P2-->L
    L-->BDD(["BDD"])
    D-->BDD
end
```
