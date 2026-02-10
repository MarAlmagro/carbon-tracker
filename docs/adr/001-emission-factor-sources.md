# ADR-001: Emission Factor Data Sources

## Status
Accepted

## Context
We need reliable emission factors to calculate CO2 equivalent for user activities. The factors must be:
- Scientifically validated
- Regularly updated
- Free to use
- Covering transport, energy, and food categories

## Decision
Use DEFRA (UK Department for Environment, Food & Rural Affairs) conversion factors as primary source, supplemented by EPA data for US-specific factors.

### Primary Source: DEFRA
- Updated annually
- Well-documented methodology
- Covers all our categories
- UK-centric but widely applicable
- Free and publicly available

### Secondary Source: EPA
- US-specific factors
- Supplements DEFRA for regional accuracy
- Particularly useful for US energy grid factors

### Data Storage
- Store factors in database table `emission_factors`
- Version factors with `source` and `year` columns
- Update annually when new DEFRA data released

## Consequences

### Positive
- Consistent, validated data
- Clear audit trail
- Easy to update annually
- Single source of truth

### Negative
- UK-centric defaults (acceptable for MVP)
- Manual annual update process
- Some factors may not match local conditions exactly

### Risks
- DEFRA methodology changes could affect historical comparisons
- Mitigation: Version all factors, store calculation date with activities

## References
- DEFRA Conversion Factors: https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting
- EPA Emission Factors: https://www.epa.gov/climateleadership/ghg-emission-factors-hub
