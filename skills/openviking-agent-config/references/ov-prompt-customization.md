# OpenViking Prompt Customization

Reference from OpenViking documentation (`docs/en/guides/10-prompt-guide.md`). Covers how to tune the memory extraction pipeline — the prompts that control what memories get extracted and how duplicates are handled.

## Key Templates for Agent Memory

| Template | Stage | What it controls |
|---|---|---|
| `compression.memory_extraction` | Session commit | What memory candidates get extracted from session transcripts |
| `compression.dedup_decision` | Memory deduplication | Whether a new candidate is skipped, created, or merged into existing memory |
| `compression.structured_summary` | Session archive | How archived sessions get summarized (affects what survives across sessions) |
| `retrieval.intent_analysis` | Pre-search | How queries get decomposed into typed queries (affects search quality) |

## Memory Schema Extensions

OV supports custom memory schemas via `memory.custom_templates_dir`. Built-in schemas define the structure for all 10 memory types (profile, preferences, entities, events, cases, patterns, tools, skills, identity, soul). Custom schemas can add domain-specific memory types.

### Built-in Pattern Schema

```yaml
memory_type: "patterns"
description: "Pattern memory for reusable workflows and methods"
fields:
  - name: "pattern_name"
    type: "string"
  - name: "pattern_type"
    type: "string"
  - name: "content"
    type: "string"
operation_mode: "upsert"
```

### Built-in Case Schema

```yaml
memory_type: "cases"
description: "Case memory for problem-to-solution records"
fields:
  - name: "case_name"
    type: "string"
  - name: "problem"
    type: "string"
  - name: "solution"
    type: "string"
  - name: "content"
    type: "string"
operation_mode: "create"
```

## Tuning the Extraction Pipeline

Customize via `prompts.templates_dir` in `ov.conf` or `OPENVIKING_PROMPT_TEMPLATES_DIR` env var:

```json
{
  "prompts": {
    "templates_dir": "/path/to/custom-prompts"
  }
}
```

Copy the built-in template, modify only the prompt body/output requirements, keep variable names stable.

### Risk Levels

| Change | Risk |
|---|---|
| Adjusting tone, adding examples | Low |
| Changing output style, extraction preference | Medium |
| Changing variable names, output structure | High |
| Changing `directory`, `filename_template`, `merge_op` | Very high |
