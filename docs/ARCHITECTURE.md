# Architecture

## Layers

User
↓
CLI / Future UI
↓
Research Engine
↓
Research Agents
↓
Web Search / Source Collection
↓
AI Analysis
↓
Validation
↓
SQLite Database

## Suggested Structure

app/
    agents/
    database/
    models/
    research/
    services/
    ui/
    utils/

## Core Concepts

ResearchAgent
- One responsibility
- Accepts a School
- Produces structured findings

ResearchEngine
- Runs searches
- Collects evidence
- Calls AI
- Validates output
- Saves results

Database
- Districts
- Schools
- Buildings
- Facts
- Sources
- ResearchJobs
- Evidence
