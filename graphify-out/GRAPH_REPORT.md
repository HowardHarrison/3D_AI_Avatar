# Graph Report - AI_3D_Avatar  (2026-10-29)

## Corpus Check
- 151 files · ~49,185 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1389 nodes · 2203 edges · 110 communities (90 shown, 17 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `49e94b41`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PresenterPlanService
- AnimationRegistry.ts
- AvatarRuntime
- common.py
- GltfBuilder
- create_animation.py
- package.json
- modify_character.py
- dependencies.py
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
- LLMProvider
- playAssistantReaction.ts
- Expected Output Format
- plans.py
- get_synthesized_audio
- Output Expectations
- Commands available now
- FacialController
- Architecture
- Bug Reporting Format
- Avatar art contract (stylized chatbot)
- build_mask
- Architecture Review Process
- pull_request_template.md
- Agent instructions — learn by building
- AvatarRuntime.ts
- PlanValidationError
- apply_rename_map.py
- frontend-developer-agent.md
- Documentation Standards
- devDependencies
- test_tts_synthesize.py
- main.py
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
- LlmConfigurationError
- Core Responsibilities
- UI Testing
- api/__init__.py
- core/__init__.py
- domain/__init__.py
- infrastructure/__init__.py
- langchain/__init__.py
- app/__init__.py
- services/__init__.py
- utils/__init__.py
- definitions/README.md
- ai-3d-avatar-backend
- dependencies
- Mixamo upload pack
- @vitejs/plugin-react
- Avatar specification
- masks/README.md
- ExpressionName
- Avatar.tsx
- source/README.md
- chat_service.py
- DebugPanel.tsx
- AudioController

## God Nodes (most connected - your core abstractions)
1. `AvatarRuntime` - 29 edges
2. `LLMProvider` - 24 edges
3. `LlmConfigurationError` - 23 edges
4. `ExpressionName` - 23 edges
5. `FacialController` - 20 edges
6. `PlanValidationError` - 19 edges
7. `LLMResult` - 19 edges
8. `create_app()` - 19 edges
9. `PresenterPlanService` - 19 edges
10. `scripts` - 19 edges

## Surprising Connections (you probably didn't know these)
- `post_chat_turn()` --uses--> `ChatTurnRequest`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/api/schemas.py
- `post_chat_turn()` --uses--> `ChatTurnResponse`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/api/schemas.py
- `post_chat_turn()` --uses--> `LlmConfigurationError`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/core/exceptions.py
- `post_chat_turn()` --uses--> `LlmProviderError`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/core/exceptions.py
- `_to_schema()` --uses--> `AnimationPlan`  [INFERRED]
  backend/app/api/routes/plans.py → backend/app/domain/models.py

## Import Cycles
- None detected.

## Communities (110 total, 17 thin omitted)

### Community 0 - "PresenterPlanService"
Cohesion: 0.22
Nodes (8): get_presenter_plan_service(), get_presenter_plan_service_with_llm(), Provide a shared PresenterPlanService without an LLM (sample plan)., PresenterPlanService with an injected LLM port (for generate-text routes). Not…, PresenterPlanService, Orchestrates animation plans and plan-related text for avatar clients., Return the injected LLM port or raise if missing., Generate a short spoken script for a future animation plan. Args: topic:…

### Community 1 - "AnimationRegistry.ts"
Cohesion: 0.14
Nodes (16): EXPRESSION_NAMES, GESTURE_NAMES, HEAD_NAMES, isExpressionName(), isGestureName(), isHeadMotionName(), resolveExpressionClip(), resolveGestureClip() (+8 more)

### Community 2 - "AvatarRuntime"
Cohesion: 0.06
Nodes (9): Avatar(), loadGltf(), AnimationController, ALLOWED, AnimationStateMachine, IdleController, randomBetween(), AvatarRuntime (+1 more)

### Community 3 - "common.py"
Cohesion: 0.07
Nodes (50): assert_export_path_allowed(), blender_dir(), candidate_presenter_glb(), emit(), exports_dir(), exports_tmp_dir(), load_scripts_module(), presenter_blend_path() (+42 more)

### Community 4 - "GltfBuilder"
Cohesion: 0.05
Nodes (37): Shared naming contracts for Blender validation, GLB export, and the placeholder…, build_face(), main(), Generate a stylized face-only placeholder GLB for the Head bone socket. Drawn…, Build a Bitmoji-like face with contract morph names on head + mouth meshes., Write face.glb next to the body presenter asset., _align4(), _box_indices() (+29 more)

### Community 5 - "create_animation.py"
Cohesion: 0.07
Nodes (43): _action_fcurve_count(), _allowed_clip_names(), _assign_nla_slot(), _bone_exists(), _build_bone_clip(), key_loc(), key_rot(), need() (+35 more)

### Community 6 - "package.json"
Cohesion: 0.13
Nodes (16): name, private, type, version, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+8 more)

### Community 7 - "modify_character.py"
Cohesion: 0.09
Nodes (33): _apply_transforms(), _build_parser(), _count_ops(), _fmt_vec(), _list_objects(), _load_common(), modify_character(), _parse_bone_rename() (+25 more)

### Community 8 - "dependencies.py"
Cohesion: 0.07
Nodes (42): get_tts_audio_service(), get_tts_cache_dir(), get_tts_provider(), get_tts_service(), Path, FastAPI dependency injection wiring., TtsService with injected TTS port (for synthesize)., TtsService without a provider — serve cached audio files only. (+34 more)

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
Cohesion: 0.12
Nodes (8): ReplyReaction, ResolvedClip, AnimationLayerPriority, GazeTarget, GestureName, HeadMotionName, PlayAnimationOptions, AvatarController

### Community 26 - "LLMProvider"
Cohesion: 0.05
Nodes (45): Provider ports implemented by infrastructure adapters., LLMProvider, ABC, LLM provider port. Implementations live under infrastructure/ (e.g. LangChain…, Generate a text response from the given prompt., Interface for large language model text generation., LLMResult, Raw text result from an LLM provider. (+37 more)

### Community 27 - "playAssistantReaction.ts"
Cohesion: 0.06
Nodes (42): ChatApiRole, ChatHistoryItem, ChatTurnResponse, postChatTurn(), PostChatTurnOptions, readErrorDetail(), resolveAudioUrl(), synthesizeSpeech() (+34 more)

### Community 28 - "Expected Output Format"
Cohesion: 0.13
Nodes (15): Assumptions, Business Context, Component Diagram Description, Current Architecture Assessment, Data Flow, Expected Output Format, Final Recommendation, Implementation Roadmap (+7 more)

### Community 29 - "plans.py"
Cohesion: 0.08
Nodes (39): Interactive chatbot turn routes. Thin layer — orchestration stays in services., health_check(), get, Return API liveness status., generate_plan(), generate_plan_text(), get_sample_plan(), get (+31 more)

### Community 30 - "get_synthesized_audio"
Cohesion: 0.50
Nodes (4): get_synthesized_audio(), get, Serve a previously synthesized MP3 from the local TTS cache., FileResponse

### Community 32 - "Output Expectations"
Cohesion: 0.17
Nodes (12): Accessibility Considerations, API Integration Strategy, Architecture Approach, Clean Production-Ready Code, Folder Structure, Output Expectations, Performance Considerations, Requirement Analysis (+4 more)

### Community 33 - "Commands available now"
Cohesion: 0.10
Nodes (21): Agent decision rule, Blender asset pipeline, Check Blender CLI, Commands available now, Create stub animations (Step 7), Example: change suit color, Export → validate → promote, Inspect scene (always run before modifying) (+13 more)

### Community 34 - "FacialController"
Cohesion: 0.16
Nodes (6): FACE_MASK_BASE_PATH, FACE_PACK_CROSSFADE_MS, facePackRegistry, isFacePackExpression(), resolveFaceMask(), FacialController

### Community 35 - "Architecture"
Cohesion: 0.67
Nodes (3): Architecture, Future attachment points, Responsibilities

### Community 36 - "Bug Reporting Format"
Cohesion: 0.18
Nodes (11): Actual Result, Bug Reporting Format, Environment, Evidence, Expected Result, Possible Root Cause, Preconditions, Priority (+3 more)

### Community 37 - "Avatar art contract (stylized chatbot)"
Cohesion: 0.12
Nodes (16): Animation clips, Avatar art contract (stylized chatbot), Chatbot “talk” (behavior, not a new required clip yet), Face on Head (cohesive character), Face pack (production expressions), Facial morphs (shape keys), Optional body (legs / eyes), Optional fingers (Mixamo path) (+8 more)

### Community 38 - "build_mask"
Cohesion: 0.33
Nodes (11): _base(), _brows(), build_mask(), _eyes(), main(), _mouth(), _nose(), Generate placeholder face-pack mask textures (stylized, pale skin to match… (+3 more)

### Community 39 - "Architecture Review Process"
Cohesion: 0.22
Nodes (9): Alignment with business goals, Architecture Review Process, Cost implications, Maintainability, Operational complexity, Reliability risks, Scalability risks, Security risks (+1 more)

### Community 40 - "pull_request_template.md"
Cohesion: 0.40
Nodes (4): Area, How to verify, Notes, Summary

### Community 41 - "Agent instructions — learn by building"
Cohesion: 0.22
Nodes (7): After each step, Agent instructions — learn by building, Default: one small step, Do not finish a whole phase unprompted, Durable context (Obsidian), GitFlow-lite, Navigate by graphify nodes (save tokens)

### Community 42 - "AvatarRuntime.ts"
Cohesion: 0.28
Nodes (7): animationRegistry, MorphMesh, BlendShapeMap, FaceMaskSpec, logger, LogLevel, three

### Community 43 - "PlanValidationError"
Cohesion: 0.07
Nodes (41): AnimationSegment, Any, PlanValidationError, Raised when an animation plan fails semantic validation., AnimationPlan, AnimationSegment, Core domain models for presenter plans (semantic only — no bones/clips)., One timed slice of a presenter performance plan. (+33 more)

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

### Community 48 - "test_tts_synthesize.py"
Cohesion: 0.12
Nodes (14): _FakeTts, Path, API tests for POST /api/v1/tts/synthesize and GET audio (mocked TTS)., Writes a tiny fake MP3 marker file into the cache., Install fake TTS and a test cache dir before each test., Clear overrides and test cache files., Route returns audioUrl and estimated duration., Pydantic rejects blank text. (+6 more)

### Community 49 - "main.py"
Cohesion: 0.10
Nodes (13): Application-wide logging setup., Configure root logging to stdout., setup_logging(), get_settings(), Application configuration loaded from environment variables., Parse CORS origins into a list for middleware., Return a cached settings instance., Runtime settings. Secrets must come from env / `.env`, never source code. (+5 more)

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

### Community 85 - "LlmConfigurationError"
Cohesion: 0.12
Nodes (21): get_llm_provider(), Build the configured OpenAI-compatible ``LLMProvider``. Reads ``LLM_API_KEY``,…, AppError, LlmConfigurationError, LlmProviderError, Raised when LLM settings are missing or invalid for a provider call., Raised when an LLM provider request fails., Base application error. (+13 more)

### Community 86 - "Core Responsibilities"
Cohesion: 0.67
Nodes (3): 1. Requirement Analysis, 2. Test Planning, Core Responsibilities

### Community 87 - "UI Testing"
Cohesion: 0.67
Nodes (3): Functional Quality, UI Testing, Visual Quality

### Community 102 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, react, react-dom, @react-three/drei, @react-three/fiber, three

### Community 103 - "Mixamo upload pack"
Cohesion: 0.33
Nodes (5): 1. Prepare the mesh (already done by script), 2. Auto-rig on Mixamo (you do this in the browser), 3. Drop the file back into the repo, 4. Tell the agent (or run yourself), Mixamo upload pack

### Community 105 - "Avatar specification"
Cohesion: 0.40
Nodes (5): Asset, Avatar specification, Look vs motion, Placeholder vs authored character, Runtime API

### Community 109 - "Avatar.tsx"
Cohesion: 0.12
Nodes (18): avatarConfig, defaultExpression, defaultGaze, SemanticExpression, SemanticGesture, SemanticHeadMotion, studioConfig, AvatarCamera() (+10 more)

### Community 114 - "chat_service.py"
Cohesion: 0.15
Nodes (15): get_chat_service(), ChatService with an injected LLM port (for chat turn routes). Not cached: thin…, post_chat_turn(), post, Run one chat turn: user ``message`` (+ optional ``history``) → ``reply``.…, ChatValidationError, Raised when a chat turn request fails validation., build_chat_turn_prompt() (+7 more)

### Community 116 - "DebugPanel.tsx"
Cohesion: 0.14
Nodes (15): StatusPanel(), StatusPanelProps, AnimationControls(), AnimationControlsProps, EXPRESSIONS, GESTURES, HEADS, DebugPanel() (+7 more)

## Knowledge Gaps
- **386 isolated node(s):** `ai-3d-avatar-backend`, `singleQuote`, `semi`, `trailingComma`, `printWidth` (+381 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 780 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Stylized Chatbot Avatar — Overall Architecture` connect `Stylized Chatbot Avatar — Overall Architecture` to `avatar-art-contract.md`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `react` connect `playAssistantReaction.ts` to `DebugPanel.tsx`, `Avatar.tsx`, `package.json`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `PlanValidationError` connect `PlanValidationError` to `PresenterPlanService`, `dependencies.py`, `main.py`, `LlmConfigurationError`, `plans.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `LlmConfigurationError` (e.g. with `get_llm_provider()` and `post_chat_turn()`) actually correct?**
  _`LlmConfigurationError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ai-3d-avatar-backend`, `singleQuote`, `semi` to the rest of the system?**
  _386 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AnimationRegistry.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.14333333333333334 - nodes in this community are weakly interconnected._
- **Should `AvatarRuntime` be split into smaller, more focused modules?**
  _Cohesion score 0.0641025641025641 - nodes in this community are weakly interconnected._