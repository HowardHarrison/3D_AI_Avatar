# Graph Report - AI_3D_Avatar  (2026-10-21)

## Corpus Check
- 124 files · ~35,809 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1166 nodes · 1711 edges · 106 communities (88 shown, 15 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `95d51d95`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AvatarScene.tsx
- AnimationRegistry.ts
- AnimationController
- common.py
- GltfBuilder
- create_animation.py
- package.json
- modify_character.py
- AudioController
- import_base_glb
- modify_materials.py
- scripts
- _improve_impl
- compilerOptions
- scaffold_presenter_blend.py
- add_stub_shape_keys.py
- inspect_scene.py
- export_mesh_for_mixamo.py
- main
- export_glb.py
- validate_rig.py
- .prettierrc.json
- vite-env.d.ts
- Stylized Chatbot Avatar — Overall Architecture
- animation.ts
- Settings
- AvatarRuntime
- PresenterPlanService
- Expected Output Format
- main.py
- LLMProvider
- AnimationStateMachine
- Output Expectations
- Commands available now
- AvatarRuntime.ts
- plans.py
- Bug Reporting Format
- Avatar art contract (stylized chatbot)
- tts_provider.py
- Architecture Review Process
- pull_request_template.md
- Agent instructions — learn by building
- FacialController
- PlanValidationError
- apply_rename_map.py
- frontend-developer-agent.md
- Documentation Standards
- devDependencies
- validateAvatarConfig.ts
- LlmConfigurationError
- QA Engineer Agent
- Output Formats
- solution-architect-agent.md
- Technical Decision Making
- avatar-art-contract.md
- Contributing — GitFlow-lite
- test_health.py
- Blender avatar pipeline
- System Design Responsibilities
- Architecture Analysis Framework
- Stylized Chatbot Avatar
- Backend — Chatbot Avatar API
- UI/UX Principles
- Performance Optimization
- Frontend Security
- Browser Knowledge
- Technology Awareness
- Security Awareness
- Test Design Guidelines
- Security Architecture
- Cloud Architecture
- Animation system
- API Integration
- Code Quality
- Component Design
- Frontend Testing
- Responsive Design
- Frontend Architecture
- State Management
- API Testing
- Automation Mindset
- Risk-Based Thinking
- Business Requirement Analysis
- Current System Understanding
- Observability
- Architecture
- Core Responsibilities
- UI Testing
- api/__init__.py
- core/__init__.py
- domain/__init__.py
- infrastructure/__init__.py
- langchain/__init__.py
- app/__init__.py
- presenter_plan_service.py
- services/__init__.py
- utils/__init__.py
- definitions/README.md
- ai-3d-avatar-backend
- dependencies
- Mixamo upload pack
- @vitejs/plugin-react
- Avatar specification

## God Nodes (most connected - your core abstractions)
1. `AvatarRuntime` - 26 edges
2. `PlanValidationError` - 19 edges
3. `LLMProvider` - 19 edges
4. `PresenterPlanService` - 19 edges
5. `scripts` - 19 edges
6. `Stylized Chatbot Avatar — Overall Architecture` - 19 edges
7. `LlmConfigurationError` - 18 edges
8. `LLMResult` - 16 edges
9. `AnimationController` - 16 edges
10. `AvatarController` - 16 edges

## Surprising Connections (you probably didn't know these)
- `get_llm_provider()` --uses--> `LlmConfigurationError`  [INFERRED]
  backend/app/api/dependencies.py → backend/app/core/exceptions.py
- `_to_schema()` --uses--> `AnimationPlan`  [INFERRED]
  backend/app/api/routes/plans.py → backend/app/domain/models.py
- `get_sample_plan()` --uses--> `PresenterPlanService`  [INFERRED]
  backend/app/api/routes/plans.py → backend/app/services/presenter_plan_service.py
- `generate_plan_text()` --uses--> `LlmConfigurationError`  [INFERRED]
  backend/app/api/routes/plans.py → backend/app/core/exceptions.py
- `generate_plan_text()` --uses--> `LlmProviderError`  [INFERRED]
  backend/app/api/routes/plans.py → backend/app/core/exceptions.py

## Import Cycles
- None detected.

## Communities (106 total, 15 thin omitted)

### Community 0 - "AvatarScene.tsx"
Cohesion: 0.07
Nodes (33): App(), StatusPanel(), StatusPanelProps, avatarConfig, AppEnvironment, environment, studioConfig, AnimationControls() (+25 more)

### Community 1 - "AnimationRegistry.ts"
Cohesion: 0.16
Nodes (16): EXPRESSION_NAMES, GESTURE_NAMES, HEAD_NAMES, isExpressionName(), isGestureName(), isHeadMotionName(), resolveExpressionClip(), resolveGestureClip() (+8 more)

### Community 2 - "AnimationController"
Cohesion: 0.17
Nodes (3): AnimationController, IdleController, randomBetween()

### Community 3 - "common.py"
Cohesion: 0.07
Nodes (50): assert_export_path_allowed(), blender_dir(), candidate_presenter_glb(), emit(), exports_dir(), exports_tmp_dir(), load_scripts_module(), presenter_blend_path() (+42 more)

### Community 4 - "GltfBuilder"
Cohesion: 0.06
Nodes (32): Shared naming contracts for Blender validation, GLB export, and the placeholder…, _align4(), _box_indices(), _box_normals(), _box_positions(), build_presenter(), _facial_morph_deltas(), GltfBuilder (+24 more)

### Community 5 - "create_animation.py"
Cohesion: 0.07
Nodes (43): _action_fcurve_count(), _allowed_clip_names(), _assign_nla_slot(), _bone_exists(), _build_bone_clip(), key_loc(), key_rot(), need() (+35 more)

### Community 6 - "package.json"
Cohesion: 0.13
Nodes (16): name, private, type, version, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+8 more)

### Community 7 - "modify_character.py"
Cohesion: 0.09
Nodes (33): _apply_transforms(), _build_parser(), _count_ops(), _fmt_vec(), _list_objects(), _load_common(), modify_character(), _parse_bone_rename() (+25 more)

### Community 9 - "import_base_glb"
Cohesion: 0.23
Nodes (12): _backup_existing_blend(), _clear_scene(), import_base_glb(), _load_common(), Path, Import an external GLB as the Blender source presenter.blend. Use this when…, Load ``common.py`` from the same scripts directory (works inside Blender)., Return arguments after ``--`` when launched via ``blender --python``. (+4 more)

### Community 10 - "modify_materials.py"
Cohesion: 0.15
Nodes (20): _build_parser(), _list_materials(), _load_common(), _material_has_nodes(), modify_materials(), _parse_color(), ArgumentParser, Change one material base color in the open .blend (targeted, reversible edit).… (+12 more)

### Community 11 - "scripts"
Cohesion: 0.11
Nodes (19): scripts, avatar:export, avatar:export-mixamo, avatar:import-rigged, avatar:inspect, avatar:promote, avatar:release, avatar:scaffold (+11 more)

### Community 12 - "_improve_impl"
Cohesion: 0.12
Nodes (19): _apply_deltas(), _find_armature(), _head_vertex_data(), improve_facial_shape_keys(), _improve_impl(), _load_common(), _pick_mesh(), Rebuild contract facial shape keys with visible head-region deformations.… (+11 more)

### Community 13 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+9 more)

### Community 14 - "scaffold_presenter_blend.py"
Cohesion: 0.17
Nodes (15): _add_bone(), _build_armature(), _build_meshes(), _clear_scene(), _load_common(), Create a contract-compliant learning scaffold at…, Create simple body + head meshes with required shape keys., Build and save the learning presenter.blend; return exit code. (+7 more)

### Community 15 - "add_stub_shape_keys.py"
Cohesion: 0.27
Nodes (9): add_stub_shape_keys(), _load_common(), _pick_mesh(), Add contract-named facial shape keys (tiny stubs) to the presenter mesh. Mixamo…, Load ``common.py`` from the same scripts directory (works inside Blender)., Return script flags after ``--``, or plain-python argv; ignore Blender flags., Return the mesh object to receive shape keys., Create missing required shape keys on the presenter mesh. (+1 more)

### Community 16 - "inspect_scene.py"
Cohesion: 0.40
Nodes (5): inspect_scene(), _load_common(), Inventory the open Blender scene for AI-agent and developer inspection. Prints…, Load ``common.py`` from the same scripts directory (works inside Blender)., Walk the open .blend and print an inventory; return process exit code.

### Community 17 - "export_mesh_for_mixamo.py"
Cohesion: 0.27
Nodes (9): export_mesh_for_mixamo(), _load_common(), _pick_mesh(), Export the presenter mesh as FBX for Mixamo (or similar) auto-rigging. Mixamo…, Load ``common.py`` from the same scripts directory (works inside Blender)., Return script flags after ``--``, or plain-python argv; ignore Blender flags., Prefer a mesh named Man / Presenter*; else the largest mesh by vertex count., Export a Mixamo-upload FBX from the open blend; return exit code. (+1 more)

### Community 18 - "main"
Cohesion: 0.38
Nodes (6): main(), Path, Write a short royalty-free presenter test tone as MP3 (or WAV fallback). python…, Write a simple A4 tone with a short fade so it is pleasant for debug playback., Create public/audio/test-presenter.mp3 when ffmpeg is available, else WAV., _write_wav()

### Community 19 - "export_glb.py"
Cohesion: 0.40
Nodes (5): export(), _load_common(), Export presenter.blend to blender/exports/tmp/presenter.glb (unvalidated).…, Load ``common.py`` from the same scripts directory (works inside Blender)., Export the current Blender scene as a temporary GLB under exports/tmp/.

### Community 20 - "validate_rig.py"
Cohesion: 0.40
Nodes (5): _load_common(), Validate presenter.blend against the Phase 1 avatar contract. Run inside…, Load ``common.py`` from the same scripts directory (works inside Blender)., Inspect the open Blender file and return the process exit code., validate()

### Community 21 - ".prettierrc.json"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 23 - "Stylized Chatbot Avatar — Overall Architecture"
Cohesion: 0.06
Nodes (36): 10.1 Goals, 10.2 Architecture split, 10.3 Paths to change clothes, 10.4 Constraints, 10. Avatar Clothing, 11. Blender Automation Strategy, 12. Animation and Appearance Strategy, 13. Phase Map (+28 more)

### Community 24 - "animation.ts"
Cohesion: 0.08
Nodes (15): defaultExpression, defaultGaze, SemanticExpression, SemanticGesture, SemanticHeadMotion, ResolvedClip, BlendShapeMap, AnimationLayerPriority (+7 more)

### Community 25 - "Settings"
Cohesion: 0.40
Nodes (4): Parse CORS origins into a list for middleware., Runtime settings. Secrets must come from env / `.env`, never source code., Settings, BaseSettings

### Community 27 - "PresenterPlanService"
Cohesion: 0.12
Nodes (15): get_presenter_plan_service(), get_presenter_plan_service_with_llm(), Provide a shared PresenterPlanService without an LLM (sample plan)., PresenterPlanService with an injected LLM port (for generate-text routes). Not…, AnimationPlan, Sequence of semantic animation segments for web/mobile clients., PresenterPlanService, AnimationPlan (+7 more)

### Community 28 - "Expected Output Format"
Cohesion: 0.13
Nodes (15): Assumptions, Business Context, Component Diagram Description, Current Architecture Assessment, Data Flow, Expected Output Format, Final Recommendation, Implementation Roadmap (+7 more)

### Community 29 - "main.py"
Cohesion: 0.16
Nodes (9): Application-wide logging setup., Configure root logging to stdout., setup_logging(), get_settings(), Application configuration loaded from environment variables., Return a cached settings instance., create_app(), FastAPI application entrypoint. (+1 more)

### Community 30 - "LLMProvider"
Cohesion: 0.07
Nodes (39): get_llm_provider(), FastAPI dependency injection wiring., Build the configured OpenAI-compatible ``LLMProvider``. Reads ``LLM_API_KEY``,…, Provider ports implemented by infrastructure adapters., LLMProvider, ABC, LLM provider port. Implementations live under infrastructure/ (e.g. LangChain…, Generate a text response from the given prompt. (+31 more)

### Community 31 - "AnimationStateMachine"
Cohesion: 0.23
Nodes (3): ALLOWED, AnimationStateMachine, AnimationStateName

### Community 32 - "Output Expectations"
Cohesion: 0.17
Nodes (12): Accessibility Considerations, API Integration Strategy, Architecture Approach, Clean Production-Ready Code, Folder Structure, Output Expectations, Performance Considerations, Requirement Analysis (+4 more)

### Community 33 - "Commands available now"
Cohesion: 0.10
Nodes (21): Agent decision rule, Blender asset pipeline, Check Blender CLI, Commands available now, Create stub animations (Step 7), Example: change suit color, Export → validate → promote, Inspect scene (always run before modifying) (+13 more)

### Community 34 - "AvatarRuntime.ts"
Cohesion: 0.32
Nodes (6): animationRegistry, EXPRESSION_SHAPES, MorphMesh, logger, LogLevel, three

### Community 35 - "plans.py"
Cohesion: 0.11
Nodes (28): health_check(), get, Return API liveness status., generate_plan(), generate_plan_text(), get_sample_plan(), get, Animation plan routes. Thin layer — orchestration stays in services. (+20 more)

### Community 36 - "Bug Reporting Format"
Cohesion: 0.18
Nodes (11): Actual Result, Bug Reporting Format, Environment, Evidence, Expected Result, Possible Root Cause, Preconditions, Priority (+3 more)

### Community 37 - "Avatar art contract (stylized chatbot)"
Cohesion: 0.20
Nodes (10): Animation clips, Avatar art contract (stylized chatbot), Chatbot “talk” (behavior, not a new required clip yet), Facial morphs (shape keys), Product look, Required (current contract), Semantic API (unchanged rule), Skeleton (required bones) (+2 more)

### Community 38 - "tts_provider.py"
Cohesion: 0.28
Nodes (7): ABC, TTS provider port. Implementations live under infrastructure/., Interface for text-to-speech synthesis., Synthesize speech and return a playable URL plus duration., Synthesized speech metadata and optional audio URL or bytes path., TtsProvider, TtsResult

### Community 39 - "Architecture Review Process"
Cohesion: 0.22
Nodes (9): Alignment with business goals, Architecture Review Process, Cost implications, Maintainability, Operational complexity, Reliability risks, Scalability risks, Security risks (+1 more)

### Community 40 - "pull_request_template.md"
Cohesion: 0.40
Nodes (4): Area, How to verify, Notes, Summary

### Community 41 - "Agent instructions — learn by building"
Cohesion: 0.22
Nodes (7): After each step, Agent instructions — learn by building, Default: one small step, Do not finish a whole phase unprompted, Durable context (Obsidian), GitFlow-lite, Navigate by graphify nodes (save tokens)

### Community 43 - "PlanValidationError"
Cohesion: 0.13
Nodes (25): AnimationSegment, Any, PlanValidationError, Raised when an animation plan fails semantic validation., AnimationSegment, One timed slice of a presenter performance plan., _coerce_object(), _optional_enum() (+17 more)

### Community 44 - "apply_rename_map.py"
Cohesion: 0.32
Nodes (7): apply_rename_map(), _load_common(), Apply a JSON bone rename map toward the avatar naming contract. Use after…, Load ``common.py`` from the same scripts directory (works inside Blender)., Return arguments after ``--`` when launched via ``blender --python``., Rename bones from a JSON map; return process exit code., _script_argv()

### Community 45 - "frontend-developer-agent.md"
Cohesion: 0.25
Nodes (7): Code Review Responsibilities, Communication Style, Core Responsibilities, Frontend Developer Agent, Recommended Folder Structure, Role, Understand Before Building

### Community 46 - "Documentation Standards"
Cohesion: 0.25
Nodes (8): Architecture Overview, Component Design, Data Flow, Deployment Architecture, Documentation Standards, Executive Summary, Recommendations, Risks

### Community 47 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, jsdom, prettier, @types/react (+7 more)

### Community 48 - "validateAvatarConfig.ts"
Cohesion: 0.47
Nodes (3): AvatarConfigError, AvatarConfigInput, validateAvatarConfig()

### Community 49 - "LlmConfigurationError"
Cohesion: 0.14
Nodes (16): AppError, LlmConfigurationError, LlmProviderError, Domain and application exceptions., Raised when LLM settings are missing or invalid for a provider call., Raised when an LLM provider request fails., Base application error., Create a provider bound to one model endpoint. Args: api_key: Provider secret… (+8 more)

### Community 50 - "QA Engineer Agent"
Cohesion: 0.29
Nodes (6): Code Review Perspective, Communication Style, Database Validation, Performance Awareness, QA Engineer Agent, Role

### Community 51 - "Output Formats"
Cohesion: 0.29
Nodes (7): Automation Opportunities, Output Formats, QA Summary, Recommended Test Cases, Release Recommendation, Risks Identified, Test Scenarios

### Community 52 - "solution-architect-agent.md"
Cohesion: 0.29
Nodes (6): Architectural Principles, Communication Style, Performance Analysis, Primary Objectives, Role, Solution Architect Agent

### Community 53 - "Technical Decision Making"
Cohesion: 0.29
Nodes (7): Alternatives Considered, Context, Decision, Mitigations, Risks, Technical Decision Making, Tradeoffs

### Community 54 - "avatar-art-contract.md"
Cohesion: 0.27
Nodes (3): Presenter source, Quick start (learning scaffold), `frontend/src` layout

### Community 55 - "Contributing — GitFlow-lite"
Cohesion: 0.22
Nodes (9): Agents, Branch names, Commit messages, Contributing — GitFlow-lite, Monorepo, Pull requests, Trunk, What we are not doing yet (+1 more)

### Community 56 - "test_health.py"
Cohesion: 0.33
Nodes (5): Smoke tests for the health endpoint., Health endpoint returns ok., Sample plan returns semantic segments with camelCase headMotion., test_health_ok(), test_sample_plan_has_segments()

### Community 57 - "Blender avatar pipeline"
Cohesion: 0.25
Nodes (8): Blender avatar pipeline, Export settings (manual), Folder layout, Goal, Local workflow, Naming contract, Orientation and scale, Prerequisites

### Community 58 - "System Design Responsibilities"
Cohesion: 0.33
Nodes (6): API Design, Application Architecture, Data Architecture, Integration Architecture, Service Design, System Design Responsibilities

### Community 59 - "Architecture Analysis Framework"
Cohesion: 0.33
Nodes (6): Architecture Analysis Framework, Cost, Maintainability, Reliability, Scalability, Security

### Community 60 - "Stylized Chatbot Avatar"
Cohesion: 0.29
Nodes (7): Architecture in one line, Backend (FastAPI), Docker, Prerequisites, Scripts, Setup, Stylized Chatbot Avatar

### Community 61 - "Backend — Chatbot Avatar API"
Cohesion: 0.40
Nodes (4): Backend — Chatbot Avatar API, Layout, Next (not in this step), Setup

### Community 62 - "UI/UX Principles"
Cohesion: 0.40
Nodes (5): Accessibility, Clarity, Consistency, Feedback, UI/UX Principles

### Community 63 - "Performance Optimization"
Cohesion: 0.40
Nodes (5): Assets, Bundles, Network, Performance Optimization, Rendering

### Community 64 - "Frontend Security"
Cohesion: 0.40
Nodes (5): Authentication, CSRF, Frontend Security, Sensitive Data, XSS

### Community 65 - "Browser Knowledge"
Cohesion: 0.40
Nodes (5): Browser Knowledge, Cookies, IndexedDB, Local Storage, Session Storage

### Community 66 - "Technology Awareness"
Cohesion: 0.40
Nodes (5): Build Tools, Frameworks, State Libraries, Styling, Technology Awareness

### Community 67 - "Security Awareness"
Cohesion: 0.40
Nodes (5): Authentication Issues, Authorization Issues, Input Validation Issues, Security Awareness, Sensitive Data Exposure

### Community 68 - "Test Design Guidelines"
Cohesion: 0.40
Nodes (5): Boundary Testing, Happy Paths, Negative Paths, State Testing, Test Design Guidelines

### Community 69 - "Security Architecture"
Cohesion: 0.40
Nodes (5): Authentication, Authorization, Compliance, Data Protection, Security Architecture

### Community 70 - "Cloud Architecture"
Cohesion: 0.40
Nodes (5): Cloud Architecture, Observability, Reliability, Scalability, Security

### Community 71 - "Animation system"
Cohesion: 0.40
Nodes (4): Animation system, Layers (priorities), Plans, State machine

### Community 72 - "API Integration"
Cohesion: 0.50
Nodes (4): API Integration, API Layer Pattern, Error Handling, Loading States

### Community 73 - "Code Quality"
Cohesion: 0.50
Nodes (4): Code Quality, Maintainable Code, Readable Code, Type Safety

### Community 74 - "Component Design"
Cohesion: 0.50
Nodes (4): Component Design, Composition, Maintainability, Small Components

### Community 75 - "Frontend Testing"
Cohesion: 0.50
Nodes (4): Component Tests, E2E Tests, Frontend Testing, Unit Tests

### Community 76 - "Responsive Design"
Cohesion: 0.50
Nodes (4): Desktop, Mobile, Responsive Design, Tablet

### Community 77 - "Frontend Architecture"
Cohesion: 0.50
Nodes (4): Frontend Architecture, Reusability, Scalability, Separation of Concerns

### Community 78 - "State Management"
Cohesion: 0.50
Nodes (4): Local State, Server State, Shared State, State Management

### Community 79 - "API Testing"
Cohesion: 0.50
Nodes (4): API Testing, Client Errors, Server Errors, Success Cases

### Community 80 - "Automation Mindset"
Cohesion: 0.50
Nodes (4): Automation Mindset, End-to-End Tests, Integration Tests, Unit Tests

### Community 81 - "Risk-Based Thinking"
Cohesion: 0.50
Nodes (4): Functional Risks, Risk-Based Thinking, Technical Risks, User Risks

### Community 82 - "Business Requirement Analysis"
Cohesion: 0.50
Nodes (4): Business Requirement Analysis, Challenge, Identify, Understand

### Community 83 - "Current System Understanding"
Cohesion: 0.50
Nodes (4): Current System Understanding, Existing Architecture, Existing Constraints, Existing Standards

### Community 84 - "Observability"
Cohesion: 0.50
Nodes (4): Logging, Monitoring, Observability, Tracing

### Community 85 - "Architecture"
Cohesion: 0.67
Nodes (3): Architecture, Future attachment points, Responsibilities

### Community 86 - "Core Responsibilities"
Cohesion: 0.67
Nodes (3): 1. Requirement Analysis, 2. Test Planning, Core Responsibilities

### Community 87 - "UI Testing"
Cohesion: 0.67
Nodes (3): Functional Quality, UI Testing, Visual Quality

### Community 94 - "presenter_plan_service.py"
Cohesion: 0.23
Nodes (8): build_animation_plan_prompt(), Prompt templates for LLM-produced semantic AnimationPlan JSON., Ask the model for a JSON AnimationPlan matching the frontend contract. Args:…, Prompt templates. Keep prompts out of services., build_plan_script_prompt(), Prompt templates for presenter script / plan text generation., Build the user prompt for a short spoken presenter script. Args: topic: News or…, Presenter plan use cases. Sample plan is deterministic; LLM builds text/plans.

### Community 102 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, react, react-dom, @react-three/drei, @react-three/fiber, three

### Community 103 - "Mixamo upload pack"
Cohesion: 0.33
Nodes (5): 1. Prepare the mesh (already done by script), 2. Auto-rig on Mixamo (you do this in the browser), 3. Drop the file back into the repo, 4. Tell the agent (or run yourself), Mixamo upload pack

### Community 105 - "Avatar specification"
Cohesion: 0.40
Nodes (5): Asset, Avatar specification, Look vs motion, Placeholder vs authored character, Runtime API

## Knowledge Gaps
- **368 isolated node(s):** `ai-3d-avatar-backend`, `singleQuote`, `semi`, `trailingComma`, `printWidth` (+363 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 689 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `scripts` connect `scripts` to `package.json`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `three` connect `AvatarRuntime.ts` to `AvatarScene.tsx`, `package.json`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `AvatarController` connect `animation.ts` to `AvatarScene.tsx`, `AvatarRuntime.ts`, `AvatarRuntime`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `PlanValidationError` (e.g. with `generate_plan()` and `generate_plan_text()`) actually correct?**
  _`PlanValidationError` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `PresenterPlanService` (e.g. with `generate_plan()` and `generate_plan_text()`) actually correct?**
  _`PresenterPlanService` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ai-3d-avatar-backend`, `singleQuote`, `semi` to the rest of the system?**
  _368 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AvatarScene.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07058823529411765 - nodes in this community are weakly interconnected._