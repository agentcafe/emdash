## Handoff: architect — AGE-5 spec drafted

Date: 2026-05-01
Session: archive_041

### Summary

Drafted the Jobs Schema Foundation engineering spec. Key architectural decision: `ec_jobs` is created via `SchemaRegistry.createContentTable()` (plugin install hook), NOT a numbered migration. The deleted `036_ats_jobs.ts` was doing it wrong — duplicating standard columns that the registry provides automatically.

### Spec Location

`.kilo/architecture/talent247/phase-1-jobs-schema.md`

### Key Design Points

- 15 standard columns + 12 indexes from SchemaRegistry (automatic)
- 18 ATS-specific fields via createField(): title, company, location, department, employment_type, workplace_type, salary range (min/max/currency/period), description (portableText), requirements, benefits, application_email, application_url, closing_date, is_featured, is_remote
- 6 custom composite indexes for ATS query patterns
- 5 seed jobs covering different employment types and locations

### Linear Updated

AGE-5 now has full field list + spec reference: https://linear.app/agentcafe/issue/AGE-5

### Next Step

Dispatch AGE-5 implementation to code-senior:
1. Plugin install hook: SchemaRegistry.createCollection("jobs") + createField() × 18 + custom indexes
2. Unit tests: table existence, column existence, index existence
3. Integration tests: CRUD via Content API
4. Seed file: 5 jobs in seed.json
