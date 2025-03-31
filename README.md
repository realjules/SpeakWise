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
```


## Components

### 1. Frontend System (Jules)

Handles all user interactions and provides administrative interfaces.

* *Telephony Interface*
  * Processes incoming and outgoing calls
  * Routes audio streams to/from the core engine
  * Uses Twilio or Africa's Talking API for call handling

* *Admin Web Portal*
  * Monitors active sessions
  * Provides system configuration
  * Manages service workflows

* *Real-time Dashboard*
  * Visualizes call volumes and success rates
  * Shows agent activities in real-time
  * Tracks key performance metrics

### 2. Core Engine (Floris)

Acts as the central intelligence, processing speech and coordinating actions.

* *LLM Service with TTS/STT*
  * Converts user speech to text
  * Processes natural language to determine intent
  * Generates responses as text
  * Converts text responses back to speech

* *Agent Orchestrator*
  * Plans the sequence of actions based on user intent
  * Maintains conversation context
  * Handles error recovery
  * Routes commands to the browser agent

* *Session Manager*
  * Maintains state between interactions
  * Handles user authentication
  * Tracks progress through multi-step processes
  * Manages data persistence

### 3. Browser-based AI Agent (Leonard)

Interacts with the Irembo website to execute user requests.

* *Web Navigation Module*
  * Automates browser interactions
  * Handles site navigation
  * Manages authentication with Irembo
  * Handles dynamic page elements

* *Form Filling Module*
  * Maps user information to form fields
  * Handles complex form validation
  * Adjusts for different service requirements
  * Captures errors and feedback

* *Payment Processing*
  * Integrates with payment workflows
  * Handles payment verification
  * Captures receipts and confirmations
  * Processes mobile money transactions

### 4. External Systems

* *Irembo Website*
  * Target platform that the browser agent interacts with
  * Source of government services and forms
  * Payment processing system

* *WhatsApp API*
  * Delivery channel for documents and confirmations
  * Secondary communication channel
  * Provides status updates and notifications

* *Database*
  * Stores user session information
  * Records transaction history
  * Logs system activities
  * Maintains configuration settings

## Data Flow

1. *Call Initiation*
   * User calls the system phone number
   * Telephony system answers and establishes a session
   * Audio stream is connected to the Core Engine

2. *Service Selection*
   * LLM processes user's spoken request
   * Intent is determined and service workflow is selected
   * Agent Orchestrator begins planning necessary steps

3. *Information Collection*
   * Core Engine engages in dialog to collect required information
   * Session Manager stores collected data
   * Validation is performed on user inputs

4. *Service Execution*
   * Browser Agent navigates to appropriate Irembo service
   * Form Filling Module completes necessary forms
   * Payment Processing handles any required payments

5. *Completion and Delivery*
   * Browser Agent captures confirmation and documents
   * Documents are delivered to user via WhatsApp
   * Call concludes with summary and next steps

## Team Responsibilities

The system architecture is designed to allow parallel development by our three-person team:

* *Jules*: Frontend System and External Integrations
* *Floris*: Core Engine and Dialog Management
* *Leonard*: Browser-based Agent and Web Automation
