# OpenViking Architecture

Reference from OpenViking documentation. Defines the product philosophy, core features, and context types.

## Product Philosophy

OpenViking is an open-source context database for AI Agents. It unifies context management (memory, resources, skills) through a file system paradigm, enabling hierarchical context delivery and self-iteration.

### Problems Solved

| Problem | Solution |
|---|---|
| Context fragmentation | Unified viking:// URI scheme, three context types |
| Context explosion | Three-level hierarchy (L0 abstract, L1 overview, L2 detail), on-demand loading |
| Poor retrieval quality | Directory recursive retrieval: lock onto high-scoring directories, then explore content |
| Context opacity | Visualized retrieval traces with complete directory browsing history |
| Limited memory iteration | 6 memory categories across user and agent, automatic extraction |

## URI Architecture

```
viking://
├── resources/              # Resources: project docs, code repos, web pages
│   └── my_project/
├── user/                   # User: preferences, habits
│   └── memories/
└── agent/                  # Agent: skills, instructions, task memories
    ├── skills/
    └── memories/
```

## Three Context Types

| Type | Purpose | Lifecycle |
|---|---|---|
| Resource | Knowledge and rules (docs, code, FAQ) | Long-term, relatively static |
| Memory | Agent's cognition (user preferences, learned experiences) | Long-term, dynamically updated |
| Skill | Callable capabilities (tools, MCP) | Long-term, static |

## Three Content Levels

| Level | Name | Token Limit | Purpose |
|---|---|---|---|
| L0 | Abstract | ~100 tokens | Vector search, quick filtering |
| L1 | Overview | ~2K tokens | Rerank, content navigation |
| L2 | Detail | Unlimited | Full content, on-demand loading |

## Six Memory Categories

| Category | Owner | Description |
|---|---|---|
| profile | user | User basic information |
| preferences | user | User preferences by topic |
| entities | user | Entity memories (people, projects) |
| events | user | Event records (decisions, milestones) |
| cases | agent | Learned cases |
| patterns | agent | Learned patterns |

## API Style

Unix-like command operations:
- `client.find("query")` — Semantic search
- `client.ls("viking://resources/")` — List directory
- `client.read("viking://resources/doc")` — Read content
- `client.abstract("viking://...")` — Get L0 abstract
- `client.overview("viking://...")` — Get L1 overview
