# Graph Report - AI_3D_Avatar  (2026-10-28)

## Corpus Check
- 145 files · ~42,249 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1338 nodes · 2096 edges · 121 communities (99 shown, 19 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 68 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ce4187ab`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- playAssistantReaction.ts
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
- get_settings
- AvatarRuntime
- Avatar.tsx
- Expected Output Format
- schemas.py
- exceptions.py
- AnimationStateMachine
- Output Expectations
- Commands available now
- AvatarRuntime.ts
- plans.py
- Bug Reporting Format
- Avatar art contract (stylized chatbot)
- ChatService
- Architecture Review Process
- pull_request_template.md
- Agent instructions — learn by building
- FacialController
- PlanValidationError
- apply_rename_map.py
- frontend-developer-agent.md
- Documentation Standards
- devDependencies
- dependencies.py
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
- TtsService
- Core Responsibilities
- UI Testing
- api/__init__.py
- core/__init__.py
- domain/__init__.py
- infrastructure/__init__.py
- langchain/__init__.py
- app/__init__.py
- PresenterPlanService
- services/__init__.py
- utils/__init__.py
- definitions/README.md
- ai-3d-avatar-backend
- dependencies
- Mixamo upload pack
- @vitejs/plugin-react
- Avatar specification
- test_generate_plan_text.py
- presenter_plan_service.py
- LLMProvider
- AvatarScene.tsx
- test_generate_plan.py
- _FakeTts
- source/README.md
- teardown_function
- LlmConfigurationError
- test_synthesize_ok
- DebugPanel.tsx
- test_synthesize_rejects_empty_text
- PresenterPage.tsx
- useSpeechToText.ts
- useChatTurn.ts

## God Nodes (most connected - your core abstractions)
1. `AvatarRuntime` - 27 edges
2. `LLMProvider` - 24 edges
3. `LlmConfigurationError` - 23 edges
4. `PlanValidationError` - 19 edges
5. `LLMResult` - 19 edges
6. `create_app()` - 19 edges
7. `PresenterPlanService` - 19 edges
8. `scripts` - 19 edges
9. `Stylized Chatbot Avatar — Overall Architecture` - 19 edges
10. `AudioController` - 17 edges

## Surprising Connections (you probably didn't know these)
- `get_llm_provider()` --uses--> `LlmConfigurationError`  [INFERRED]
  backend/app/api/dependencies.py → backend/app/core/exceptions.py
- `post_chat_turn()` --uses--> `ChatValidationError`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/core/exceptions.py
- `post_chat_turn()` --uses--> `LlmConfigurationError`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/core/exceptions.py
- `post_chat_turn()` --uses--> `LlmProviderError`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/core/exceptions.py
- `post_chat_turn()` --uses--> `ChatService`  [INFERRED]
  backend/app/api/routes/chat.py → backend/app/services/chat_service.py

## Import Cycles
- None detected.

## Communities (121 total, 19 thin omitted)

### Community 0 - "playAssistantReaction.ts"
Cohesion: 0.25
Nodes (11): readErrorDetail(), resolveAudioUrl(), synthesizeSpeech(), SynthesizeSpeechResult, mapReplyReaction(), applyReplyReaction(), clearTimedFallback(), playAssistantReaction() (+3 more)

### Community 1 - "AnimationRegistry.ts"
Cohesion: 0.18
Nodes (14): EXPRESSION_NAMES, GESTURE_NAMES, HEAD_NAMES, isExpressionName(), isGestureName(), isHeadMotionName(), resolveGestureClip(), resolveHeadClip() (+6 more)

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
Cohesion: 0.12
Nodes (10): ReplyReaction, ResolvedClip, BlendShapeMap, AnimationLayerPriority, ExpressionName, GazeTarget, GestureName, HeadMotionName (+2 more)

### Community 25 - "get_settings"
Cohesion: 0.25
Nodes (7): get_settings(), Application configuration loaded from environment variables., Parse CORS origins into a list for middleware., Return a cached settings instance., Runtime settings. Secrets must come from env / `.env`, never source code., Settings, BaseSettings

### Community 27 - "Avatar.tsx"
Cohesion: 0.20
Nodes (7): AppEnvironment, environment, Avatar(), AvatarConfigError, AvatarConfigInput, validateAvatarConfig(), @react-three/fiber

### Community 28 - "Expected Output Format"
Cohesion: 0.13
Nodes (15): Assumptions, Business Context, Component Diagram Description, Current Architecture Assessment, Data Flow, Expected Output Format, Final Recommendation, Implementation Roadmap (+7 more)

### Community 29 - "schemas.py"
Cohesion: 0.12
Nodes (22): post_chat_turn(), post, Interactive chatbot turn routes. Thin layer — orchestration stays in services., Run one chat turn: user ``message`` (+ optional ``history``) → ``reply``.…, health_check(), get, Return API liveness status., AnimationSegmentSchema (+14 more)

### Community 30 - "exceptions.py"
Cohesion: 0.14
Nodes (18): get_synthesized_audio(), get, post, TTS routes. Thin layer — orchestration stays in services., Synthesize speech for ``text`` and return a playable audio URL. Audio bytes are…, Serve a previously synthesized MP3 from the local TTS cache., synthesize_speech(), Playable audio URL (relative) plus estimated duration. (+10 more)

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
Cohesion: 0.14
Nodes (21): generate_plan(), generate_plan_text(), get_sample_plan(), get, post, Animation plan routes. Thin layer — orchestration stays in services., Map domain plan to API schema with camelCase aliases., Return a hardcoded sample plan for frontend/mobile integration tests. (+13 more)

### Community 36 - "Bug Reporting Format"
Cohesion: 0.18
Nodes (11): Actual Result, Bug Reporting Format, Environment, Evidence, Expected Result, Possible Root Cause, Preconditions, Priority (+3 more)

### Community 37 - "Avatar art contract (stylized chatbot)"
Cohesion: 0.14
Nodes (14): Animation clips, Avatar art contract (stylized chatbot), Chatbot “talk” (behavior, not a new required clip yet), Facial morphs (shape keys), Optional body (legs / eyes), Optional fingers (Mixamo path), Optional (richer stylized expressions), Product look (+6 more)

### Community 38 - "ChatService"
Cohesion: 0.15
Nodes (10): get_chat_service(), ChatService with an injected LLM port (for chat turn routes). Not cached: thin…, build_chat_turn_prompt(), Prompt templates for interactive chatbot turns., Build the prompt for one stylized chatbot reply, with optional prior turns.…, ChatService, Orchestrates interactive chatbot turns for avatar clients., Create the service. Args: llm: Required LLM port used to generate the assistant… (+2 more)

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

### Community 48 - "dependencies.py"
Cohesion: 0.10
Nodes (26): get_tts_cache_dir(), get_tts_provider(), FastAPI dependency injection wiring., Local directory for synthesized MP3 files (gitignored)., Build the configured OpenAI-compatible ``TtsProvider``. Uses ``TTS_API_KEY``…, Raised when TTS settings are missing or invalid for a provider call., TtsConfigurationError, Provider ports implemented by infrastructure adapters. (+18 more)

### Community 49 - "main.py"
Cohesion: 0.12
Nodes (9): ChatValidationError, Raised when a chat turn request fails validation., Application-wide logging setup., Configure root logging to stdout., setup_logging(), create_app(), FastAPI application entrypoint., Build and configure the ASGI application. (+1 more)

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
Nodes (4): Architecture, Future attachment points, Responsibilities, `frontend/src` layout

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

### Community 85 - "TtsService"
Cohesion: 0.16
Nodes (11): get_tts_audio_service(), get_tts_service(), Path, TtsService with injected TTS port (for synthesize)., TtsService without a provider — serve cached audio files only., Path, Orchestrates speech synthesis for avatar clients., Create the service. Args: tts: TTS port. Required for ``synthesize``; optional… (+3 more)

### Community 86 - "Core Responsibilities"
Cohesion: 0.67
Nodes (3): 1. Requirement Analysis, 2. Test Planning, Core Responsibilities

### Community 87 - "UI Testing"
Cohesion: 0.67
Nodes (3): Functional Quality, UI Testing, Visual Quality

### Community 94 - "PresenterPlanService"
Cohesion: 0.12
Nodes (15): get_presenter_plan_service(), get_presenter_plan_service_with_llm(), Provide a shared PresenterPlanService without an LLM (sample plan)., PresenterPlanService with an injected LLM port (for generate-text routes). Not…, AnimationPlan, Sequence of semantic animation segments for web/mobile clients., PresenterPlanService, AnimationPlan (+7 more)

### Community 102 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, react, react-dom, @react-three/drei, @react-three/fiber, three

### Community 103 - "Mixamo upload pack"
Cohesion: 0.33
Nodes (5): 1. Prepare the mesh (already done by script), 2. Auto-rig on Mixamo (you do this in the browser), 3. Drop the file back into the repo, 4. Tell the agent (or run yourself), Mixamo upload pack

### Community 105 - "Avatar specification"
Cohesion: 0.40
Nodes (5): Asset, Avatar specification, Look vs motion, Placeholder vs authored character, Runtime API

### Community 106 - "test_generate_plan_text.py"
Cohesion: 0.20
Nodes (9): API tests for POST /api/v1/plans/generate-text (mocked LLM)., Install fake LLM before each test., Clear FastAPI overrides after each test., Route injects LLM via DI and returns generated text., Pydantic rejects blank topic before the service runs., setup_function(), teardown_function(), test_generate_plan_text_ok() (+1 more)

### Community 107 - "presenter_plan_service.py"
Cohesion: 0.23
Nodes (8): build_animation_plan_prompt(), Prompt templates for LLM-produced semantic AnimationPlan JSON., Ask the model for a JSON AnimationPlan matching the frontend contract. Args:…, Prompt templates. Keep prompts out of services., build_plan_script_prompt(), Prompt templates for presenter script / plan text generation., Build the user prompt for a short spoken presenter script. Args: topic: News or…, Presenter plan use cases. Sample plan is deterministic; LLM builds text/plans.

### Community 108 - "LLMProvider"
Cohesion: 0.07
Nodes (31): LLMProvider, ABC, LLM provider port. Implementations live under infrastructure/ (e.g. LangChain…, Generate a text response from the given prompt., Interface for large language model text generation., LLMResult, Core domain models for presenter plans (semantic only — no bones/clips)., Raw text result from an LLM provider. (+23 more)

### Community 109 - "AvatarScene.tsx"
Cohesion: 0.15
Nodes (14): avatarConfig, defaultExpression, defaultGaze, SemanticExpression, SemanticGesture, SemanticHeadMotion, studioConfig, AvatarCamera() (+6 more)

### Community 110 - "test_generate_plan.py"
Cohesion: 0.20
Nodes (9): get_llm_provider(), Build the configured OpenAI-compatible ``LLMProvider``. Reads ``LLM_API_KEY``,…, API tests for POST /api/v1/plans/generate (mocked LLM)., Clear FastAPI overrides after each test., Route returns validated camelCase AnimationPlan JSON., Invalid LLM semantics surface as 400 PlanValidationError., teardown_function(), test_generate_plan_invalid_semantics_is_400() (+1 more)

### Community 111 - "_FakeTts"
Cohesion: 0.29
Nodes (5): _FakeTts, Path, Writes a tiny fake MP3 marker file into the cache., Install fake TTS and a test cache dir before each test., setup_function()

### Community 114 - "LlmConfigurationError"
Cohesion: 0.18
Nodes (10): LlmConfigurationError, Raised when LLM settings are missing or invalid for a provider call., Create a provider bound to one model endpoint. Args: api_key: Provider secret…, Unit tests for OpenAI-compatible LLMProvider (no live network)., generate() maps Chat Completions content into LLMResult.text., Blank API key fails before any HTTP call., SDK APIError is wrapped as LlmProviderError., test_api_error_becomes_llm_provider_error() (+2 more)

### Community 116 - "DebugPanel.tsx"
Cohesion: 0.14
Nodes (15): StatusPanel(), StatusPanelProps, AnimationControls(), AnimationControlsProps, EXPRESSIONS, GESTURES, HEADS, DebugPanel() (+7 more)

### Community 118 - "PresenterPage.tsx"
Cohesion: 0.23
Nodes (9): App(), useAvatar(), PresenterLayout(), PresenterLayoutProps, rootElement, PresenterPage(), supportsWebGL(), AppRoutes() (+1 more)

### Community 119 - "useSpeechToText.ts"
Cohesion: 0.21
Nodes (9): useSpeechToText(), UseSpeechToTextOptions, UseSpeechToTextResult, BrowserSpeechRecognition, BrowserSpeechRecognitionErrorEvent, BrowserSpeechRecognitionEvent, getSpeechRecognitionConstructor(), speechErrorMessage() (+1 more)

### Community 120 - "useChatTurn.ts"
Cohesion: 0.19
Nodes (11): ChatApiRole, ChatHistoryItem, ChatTurnResponse, postChatTurn(), PostChatTurnOptions, ChatPanel(), ChatMessage, ChatRole (+3 more)

## Knowledge Gaps
- **384 isolated node(s):** `ai-3d-avatar-backend`, `singleQuote`, `semi`, `trailingComma`, `printWidth` (+379 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 768 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `three` connect `AvatarRuntime.ts` to `Avatar.tsx`, `AvatarScene.tsx`, `package.json`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Why does `react` connect `PresenterPage.tsx` to `package.json`, `AvatarScene.tsx`, `DebugPanel.tsx`, `useSpeechToText.ts`, `useChatTurn.ts`, `Avatar.tsx`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `PlanValidationError` connect `PlanValidationError` to `plans.py`, `presenter_plan_service.py`, `main.py`, `PresenterPlanService`, `exceptions.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `LlmConfigurationError` (e.g. with `get_llm_provider()` and `post_chat_turn()`) actually correct?**
  _`LlmConfigurationError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `PlanValidationError` (e.g. with `generate_plan()` and `generate_plan_text()`) actually correct?**
  _`PlanValidationError` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LLMResult` (e.g. with `LLMProvider` and `OpenAICompatibleLLMProvider`) actually correct?**
  _`LLMResult` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ai-3d-avatar-backend`, `singleQuote`, `semi` to the rest of the system?**
  _384 weakly-connected nodes found - possible documentation gaps or missing edges._