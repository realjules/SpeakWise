## Overview

The Irembo Voice AI Agent is structured around three main components that work together to enable phone-based access to government services.

```mermaid
graph TD
    User[User with Phone] -->|Makes call| TelSys[Telephony Interface]
    
    subgraph "Frontend System - Jules"
        TelSys -->|Routes audio| AudioRouter[Audio Router]
        AudioRouter -->|Streams| CallMgr[Call Manager]
        CallMgr --> Dashboard[Admin Dashboard]
        Dashboard --> Analytics[Real-time Analytics]
    end
    
    AudioRouter -->|Audio streams| CoreSTT[Speech-to-Text]
    
    subgraph "Core Engine - Floris"
        CoreSTT -->|Text| LLM[LLM Service]
        LLM -->|Responses| CoreTTS[Text-to-Speech]
        CoreTTS -->|Speech| AudioRouter
        
        LLM <-->|Intents| Orchestrator[Agent Orchestrator]
        Orchestrator <--> SessionMgr[Session Manager]
        Orchestrator -->|Actions| AgentAPI[Agent API]
    end
    
    AgentAPI -->|Commands| BrowserCore[Browser Core]
    
    subgraph "Browser-based AI Agent - Leonard"
        BrowserCore --> Navigator[Web Navigator]
        BrowserCore --> FormFiller[Form Filler]
        BrowserCore --> PaymentProc[Payment Processor]
        BrowserCore --> DocCapture[Document Capture]
        
        Navigator -->|Controls| Browser[Headless Browser]
        FormFiller -->|Populates| Browser
        PaymentProc -->|Processes| Browser
        DocCapture -->|Extracts from| Browser
    end
    
    Browser -->|Interacts with| Irembo[Irembo Website]
    DocCapture -->|Sends to| WhatsApp[WhatsApp Service]
    WhatsApp -->|Delivers to| UserWA[User's WhatsApp]
    
    SessionMgr <-->|Stores/retrieves| DB[(Database)]
    Analytics -->|Reads from| DB
    
    classDef frontend fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    classDef core fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef browser fill:#ffecb3,stroke:#ff8f00,stroke-width:2px
    classDef external fill:#e0e0e0,stroke:#616161,stroke-width:2px
    classDef database fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px
    classDef user fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    
    class User user
    class TelSys,AudioRouter,CallMgr,Dashboard,Analytics frontend
    class CoreSTT,LLM,CoreTTS,Orchestrator,SessionMgr,AgentAPI core
    class BrowserCore,Navigator,FormFiller,PaymentProc,DocCapture,Browser browser
    class Irembo,WhatsApp,UserWA external
    class DB database
