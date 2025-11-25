#CSharp to Mermaid OpenWebUI Tool
Create Mermaid Diagrams for Files Under Path

```mermaid
classDiagram
    class Animal
    Vehicle <|-- Car
```
```csharp
public class Animal{}
public class Vehicle{}
public class Car : Vehicle {}
```
Current Status
```mermaid
---
config:
  theme: redux-color
  themeVariables:
    primaryColor: "#00ff00"
  kanban:
    ticketBaseUrl: 'https://localhost/ticketing/#TICKET#'
---
kanban
  CB[Core Bugs]
  EB[Efficiency Bugs]
   
  IP[In progress]  
    IP1[UserValue -<br> directory path]@{priority: 'Very High', assigned: 'entitycs'}
    IP2[Track Ticket Progress-<br> using comments <br> eg.<br>var a = 5; //TT:01]@{priority: 'Medium', assigned: 'entitycs'}

    
  RD[Ready for Deploy]
    RD1[Basic Tested Concept]@{ assigned: 'entitycs' }
  
  TR[Test Ready]
    TR1[System Prompt Tests]@{ ticket: TST:04, assigned: 'entitycs', priority: 'High' }
  
  fin[Done]
    fin1[Update Open WebUI to <br>LATEST~v0.6.38]@{priority: 'Very High'}
    fin3[-Hello World<br>Initial Tool Integration]@{priotity: 'Very High', ticket: FIN:01}
    fin2[Initiate Git Repo]@{priority: 'Low'}
```
