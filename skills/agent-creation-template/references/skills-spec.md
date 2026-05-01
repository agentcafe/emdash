# Agent Skills Specification

The formal specification for Agent Skills. This document describes the directory structure, `SKILL.md` format, frontmatter fields, progressive disclosure model, and validation rules that all EmDash skills must follow.

## Directory Structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## SKILL.md Format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter Fields

| Field           | Required | Constraints                                                                                                                                                  |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen. Must match the parent directory name.                  |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it. Should include specific keywords that help agents identify relevant tasks. |
| `license`       | No       | License name or reference to a bundled license file.                                                                                                         |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.).                                            |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata.                                                                                                         |
| `allowed-tools` | No       | Space-separated string of pre-approved tools the skill may use. (Experimental)                                                                               |

### Name Field Rules

- 1-64 characters
- Only lowercase alphanumeric characters and hyphens
- Must not start or end with a hyphen
- Must not contain consecutive hyphens
- Must match the parent directory name

### Description Field Rules

- 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

## Progressive Disclosure

Agents load skills progressively:

1. **Metadata** (~100 tokens): The `name` and `description` fields are loaded at startup for all skills
2. **Instructions** (< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files in `scripts/`, `references/`, or `assets/` are loaded only when required

Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files in `references/`.

## File References

When referencing other files in your skill, use relative paths from the skill root. Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

## Validation

Use the `skills-ref` reference library to validate skills:

```bash
skills-ref validate ./my-skill
```

This checks that the `SKILL.md` frontmatter is valid and follows all naming conventions.
