# Retrieval-Augmented Generation (RAG) Architecture
---

## 1. High-Level Architecture

```mermaid
graph LR
    classDef source fill:#0d47a1,stroke:#64b5f6,stroke-width:2px,color:#ffffff;
    classDef database fill:#1b5e20,stroke:#81c784,stroke-width:2px,color:#ffffff;
    classDef ai fill:#880e4f,stroke:#f06292,stroke-width:2px,color:#ffffff;
    classDef user fill:#4a148c,stroke:#ba68c8,stroke-width:2px,color:#ffffff;
    classDef process fill:#e65100,stroke:#ffb74d,stroke-width:2px,color:#ffffff;

    A[Enterprise Data<br/>Docs/Code]:::source -->|Ingest| B[(Vector Database)]:::database
    C((User Query)):::user -->|1. Question| P{Orchestrator}:::process
    P -->|2. Search| B
    B -->|3. Context| P
    P -->|4. Prompt| D[Large Language Model]:::ai
    D -->|5. Response| C
```

---

## 2. Detailed Component Architecture

```mermaid
graph TD
    classDef source fill:#0d47a1,stroke:#64b5f6,stroke-width:2px,color:#ffffff;
    classDef process fill:#e65100,stroke:#ffb74d,stroke-width:2px,color:#ffffff;
    classDef db fill:#1b5e20,stroke:#81c784,stroke-width:2px,color:#ffffff;
    classDef model fill:#880e4f,stroke:#f06292,stroke-width:2px,color:#ffffff;
    classDef ui fill:#4a148c,stroke:#ba68c8,stroke-width:2px,color:#ffffff;

    VDB[(Vector DB Index<br/>e.g., Pinecone / Qdrant)]:::db

    subgraph "Data Ingestion Pipeline (Offline)"
        DS1[PDFs / Markdown]:::source
        DS2[Confluence API]:::source
        DL[Document Loaders]:::process
        TS[Text Splitter / Chunker]:::process
        EM1[Embedding Model<br/>text-embedding-3]:::model

        DS1 --> DL
        DS2 --> DL
        DL --> TS
        TS -->|Text Chunks| EM1
        EM1 -->|Vectors + Metadata| VDB
    end

    subgraph "Retrieval & Generation Pipeline (Online)"
        User((User Front-End)):::ui
        ORCH{Orchestrator<br/>e.g., LangChain / LlamaIndex}:::process
        EM2[Query Embedding Model<br/>same model as ingestion]:::model
        PT[Prompt Template]:::process
        LLM[Large Language Model<br/>e.g., GPT-4o]:::model

        User -->|1. User Question| ORCH
        ORCH -->|2. Forward Query| EM2
        EM2 -->|3. Query Vector| VDB
        VDB -.->|4. Top-K Relevant Chunks| ORCH
        ORCH -->|5. Inject Context + Query| PT
        PT -->|6. Augmented Prompt| LLM
        LLM -->|7. Generated Answer| ORCH
        ORCH -->|8. Final Response + Citations| User
    end
```

---

## 3. Explanation of Each Phase

A standard RAG workflow operates across three primary phases: **Data Ingestion**, **Retrieval**, and **Generation**.

### Phase 1: Data Ingestion (Indexing)
This offline process prepares and structures organizational data for rapid search.
* **Extraction:** Raw text is systematically gathered from enterprise sources (e.g., Confluence, Jira, PDFs, and code repositories).
* **Chunking:** Documents are segmented into smaller, manageable text blocks to optimize processing. An overlap between chunks is maintained to preserve semantic continuity.
* **Embedding:** An embedding model converts each text block into a mathematical vector representation, capturing its underlying meaning.
* **Storage:** The generated vectors, along with their corresponding text and source metadata, are stored in a Vector Database for highly efficient similarity searches.

### Phase 2: Retrieval
This process locates the most relevant information based on the user's prompt.
* **Query Vectorization:** The user's query is processed through the identical embedding model to generate a query vector.
* **Semantic Search:** The orchestrator queries the Vector Database, computing the mathematical proximity between the query vector and the stored document vectors.
* **Context Extraction:** The database returns the top-ranked (Top-K) document chunks that possess the highest semantic relevance to the query.

### Phase 3: Generation (Augmentation)
This final phase formulates a comprehensive answer using the retrieved facts.
* **Prompt Construction:** The orchestrator integrates the retrieved document chunks and the original user query into a structured Prompt Template.
* **LLM Synthesis:** The Large Language Model analyzes the augmented prompt. Guided by the provided factual context, it generates an accurate, domain-specific response, significantly mitigating the risk of hallucination.
* **Response Delivery:** The synthesized answer is presented to the user, frequently accompanied by citations referencing the original source documents.

