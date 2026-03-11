# File Descriptions: Morphic Autonomy

This document provides a detailed overview of the repository structure and the role of each component within the Morphic Autonomy project.

## 1. Root Directory
- **`README.md`**: The primary entry point. Contains the project's abstract, core breakthroughs, technical architecture, and reproduction protocol.
- **`FILE_DESCRIPTIONS.md`**: (This file) Detailed mapping of the repository's contents.

## 2. Core Knowledge & Intelligence (`/Database`, `/Knowledge`)
- **`Database/morphic_autonomy.db`**: The **Morphic Quantum Database (MQDB)**. The single source of truth containing atomic primitives (C/Wasm), synthesized logic sequences (DNA), and task definitions.
- **`Knowledge/atomic_primitives.json`**: Definitions of basic computational atoms used for logic synthesis.
- **`Knowledge/semantic_dictionary.json`**: Mapping between natural language concepts and primitive identifiers.
- **`Knowledge/discovered_wisdom.json`**: Registry of logic sequences successfully synthesized by the Discovery Agent.

## 3. Execution Engines & Agents (`/Scripts`)
- **`morphic_wasm_vm.py`**: The primary Python-based Universal Wasm VM for executing logic sequences stored in MQDB.
- **`discovery_agent.py`**: The autonomous agent that performs bounded search to synthesize logic from task definitions.
- **`morphic_synthesizer.py`**: Tool for compiling high-level Natural Logic (.nl) into executable Python/Wasm structures.
- **`compile_db_wasm.py`**: Utility to compile C-source primitives into Wasm binaries and inject them into MQDB.
- **`VM/fortran/`**: The Fortran-based Wasm execution engine, ensuring cross-runtime deterministic parity.

## 4. Task Definitions & Education (`/Tasks`, `/Unsolved`)
- **`Tasks/*.json`**: Formal I/O contracts (test cases) for mathematical and physical challenges.
- **`Tasks/*.nl`**: Natural Logic representations of verified solutions.
- **`Unsolved/*.json`**: Tasks that exceeded the 5.0-second discovery limit, isolated for human review and "education."

## 5. Academic Foundation (`/Docs`, `/References`)
- **`Docs/ACADEMIC_PAPER_EN.md`**: The core research paper in English (Scientific Version).
- **`Docs/ACADEMIC_PAPER_JP.md`**: The core research paper in Japanese (Full Detail Version).
- **`Docs/SYSTEM_DESIGN_JP.md`**: Architectural specification and philosophical framework.
- **`References/`**: Verified academic literature (PDF/TXT pairs) supporting the theoretical claims of the project.
- **`References/REFERENCE_LIST.md`**: Categorized index of all 27 cited academic works.

## 6. Directory Structure Overview
```text
.
├── Database/      # MQDB (SQLite)
├── Docs/          # Academic papers & Design specs
├── Knowledge/     # Primitive definitions & Dictionaries
├── References/    # Academic foundation (27 literature pairs)
├── Scripts/       # VMs, Discovery Agents, Compilers
├── Tasks/         # Verified I/O contracts (37+ tasks)
└── Unsolved/      # Complexity-isolated tasks
```

---
**"Intelligence as Invariant Geometry."**
Morphic Autonomy ensures that the structural integrity of logic is preserved independently of the entropy layers.
