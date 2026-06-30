# AI Guidelines

This document defines the development philosophy for DistrictIntel.

## Primary Objective
Build a maintainable, extensible research platform. Favor readability, maintainability,
correctness, modularity, and transparency over clever implementations.

## AI Role
- AI is a software engineer, not the architect.
- Explain major architectural tradeoffs before implementing them.
- Do not make sweeping changes without approval.

## Research Philosophy
- Never invent facts.
- Every stored fact must have one or more sources.
- Prefer primary sources.
- Preserve conflicting evidence and record confidence.

## Preferred Source Priority
1. County Auditor
2. OFCC
3. District Facility Plans
4. District Website
5. Board Minutes
6. Architect Documents
7. Government Publications
8. Local Newspapers

## Design Principles
- Single responsibility.
- Small focused modules.
- Composition over inheritance.
- No duplicated logic.
- Database writes should be traceable.
- Resume safely after interruption.

## Coding Standards
- Python 3.12+
- Type hints required
- pathlib over os.path
- Context managers
- Minimal dependencies
- Ruff linting

## Logging
Log every research task with enough detail to diagnose failures.

## Guiding Principle
When in doubt, choose the implementation that another engineer will easily
understand six months from now.
