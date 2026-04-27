# OpenViking Architecture Overview

Reference from OpenViking documentation. System architecture, core modules, data flow, and design principles.

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        OpenViking System Architecture                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                              ┌─────────────┐                               │
│                              │   Client    │                               │
│                              │ (OpenViking)│                               │
│                              └──────┬──────┘                               │
│                                     │ delegates                            │
│                              ┌──────▼──────┐                               │
│                              │   Service   │                               │
│                              │    Layer    │                               │
│                              └──────┬──────┘                               │
│                                     │                                      │
│           ┌─────────────────────────┼─────────────────────────┐            │
│           │                         │                         │            │
│           ▼                         ▼                         ▼            │
│    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐      │
│    │  Retrieve   │          │   Session   │          │    Parse    │      │
│    │  search/find│          │  Management │          │  Doc parsing │      │
│    │  Intent/Rnk │          │  add/commit  │          │ L0/L1/L2    │      │
│    └──────┬──────┘          └──────┬──────┘          └──────┬──────┘      │
│           │                        │                        │             │
│           │                        ▼                        │             │
│           │                 ┌─────────────┐                 │             │
│           │                 │ Compressor  │                 │             │
│           │                 │ Compress/   │                 │             │
│           │                 │ Deduplicate │                 │             │
│           │                 └──────┬──────┘                 │             │
│           │                        │                        │             │
│           └────────────────────────┼────────────────────────┘             │
│                                    ▼                                      │
│    ┌─────────────────────────────────────────────────────────────────┐    │
│    │                         Storage Layer                            │    │
│    │               AGFS (File Content)  +  Vector Index               │    │
│    └─────────────────────────────────────────────────────────────────┘    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Core Modules

| Module | Responsibility | Key Capabilities |
|---|---|---|
| Client | Unified entry | Provides all operation interfaces, delegates to Service layer |
| Service | Business logic | FSService, SearchService, SessionService, ResourceService, RelationService, PackService, DebugService |
| Retrieve | Context retrieval | IntentAnalyzer, HierarchicalRetriever, Rerank |
| Session | Session management | Message recording, usage tracking, session compression, memory commit |
| Parse | Context extraction | Document parsing (PDF/MD/HTML), TreeBuilder, async semantic generation |
| Compressor | Memory compression | 6-category memory extraction, LLM deduplication decisions |
| Storage | Storage layer | VikingFS virtual filesystem, vector index, AGFS integration |

## Dual-Layer Storage

| Layer | Responsibility | Content |
|---|---|---|
| AGFS | Content storage | L0/L1/L2 full content, multimedia files, relations |
| Vector Index | Index storage | URIs, vectors, metadata (no file content) |

## Data Flows

### Adding Context
```
Input → Parser → TreeBuilder → AGFS → SemanticQueue → Vector Index
```
Parser: Parse documents, create file structure (no LLM)
TreeBuilder: Move to AGFS, enqueue for semantic processing
SemanticQueue: Async bottom-up L0/L1 generation
Vector Index: Build for semantic search

### Retrieving Context
```
Query → Intent Analysis → Hierarchical Retrieval → Rerank → Results
```
Intent Analysis: 0-5 typed queries
Hierarchical Retrieval: Directory-level recursive search with priority queue
Rerank: Scalar filtering + model reranking

### Session Commit
```
Messages → Compress → Archive → Memory Extraction → Storage
```
Messages: Accumulate conversation and usage records
Compress: Keep recent N rounds, archive older
Archive: Generate L0/L1 for history segments
Memory Extraction: Extract 6-category memories
Storage: Write to AGFS + vector index

## Design Principles

| Principle | Description |
|---|---|
| Pure Storage Layer | Storage only handles AGFS + basic vector search; Rerank is in retrieval layer |
| Three-Layer Information | L0/L1/L2 enables progressive detail loading, saving token consumption |
| Two-Stage Retrieval | Vector search recalls candidates + Rerank improves accuracy |
| Single Data Source | All content read from AGFS; vector index only stores references |
