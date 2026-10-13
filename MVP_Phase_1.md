# 3D Avatar News Presenter — Phase 1 MVP Architecture and Implementation Specification

## 1. Project Overview

The objective of Phase 1 is to build a scalable, maintainable, and AI-agent-friendly foundation for a browser-based 3D Avatar News Presenter. The application will display a professional humanoid presenter in a browser, support basic idle behavior, facial expressions, head movements, hand gestures, and local audio playback, and establish an architecture that can later support lip synchronization, multilingual speech, subtitles, LLM-driven behavior, and real-time interaction.

The most important architectural change from the original specification is that **Blender will no longer be treated as the place where every animation or visual change must be manually authored**. Blender will be used primarily for operations that benefit from a dedicated 3D authoring environment, including character modeling, rigging, mesh editing, skin weighting, facial topology, and exporting 3D assets. Blender's Python API will allow AI coding agents to inspect and modify scenes programmatically. Three.js will be responsible for browser rendering and runtime animation, while TypeScript and JSON definitions will represent the editable behavior of the avatar wherever practical.

This architecture is intended for a software developer who does not use Blender professionally every day. The developer should be able to request changes in natural language, have an AI coding agent modify configuration files or TypeScript animation definitions, and use generated Blender Python scripts when actual 3D asset changes are necessary. The workflow should favor readable source files, deterministic automation, validation, and visual previews over manually editing complex binary assets.

Phase 1 must remain a focused MVP. It must not attempt to implement the entire future AI news production platform. Instead, it should deliver a reliable local browser application and the reusable foundations needed to add future functionality without rewriting the core runtime.

## 2. Core Architectural Principles

The system will follow six principles.

**First, the AI agent should modify source definitions rather than directly editing compiled assets.** JSON, TypeScript, Python scripts, and documented naming contracts should be the primary editable representations. GLB files are generated or exported assets, not the main source of application logic. If a character's suit color can be changed through a material definition or a Three.js material override, the AI agent should not need to rebuild the character in Blender. If a character's proportions, facial topology, rig, or skin weights need to change, the agent should generate and run a controlled Blender automation script.

**Second, Blender is the 3D authoring and asset automation environment, while Three.js is the browser runtime.** Blender should not be launched for every interactive browser request. The browser should load the prepared GLB asset and execute runtime behavior locally through Three.js and React Three Fiber.

**Third, avatar behavior must be represented through semantic commands.** Application code and future AI systems should use commands such as `playGesture("emphasize")`, `setExpression("serious")`, and `setGaze("camera")`. They must not depend on bone indexes, animation clip array positions, mesh internals, or raw morph target indexes. This protects the project from changes to the underlying character or rig.

**Fourth, separate the visual asset from its behavior.** The avatar model, material overrides, gestures, expressions, idle behavior, camera settings, and studio configuration should be independently maintainable wherever practical. Not every animation needs to be a separate Blender animation clip. Simple procedural motions such as subtle head movement, eye movement, breathing offsets, and some hand gestures may be implemented in TypeScript when they can be performed reliably by the available rig.

**Fifth, all asset modifications must be inspectable and reversible.** Blender automation scripts must validate the existing scene before modifying it, avoid silently destroying user work, save recoverable project versions, and export only after validation. Generated assets must be reproducible from documented source files and scripts as far as practical.

**Sixth, Phase 1 must not be over-engineered for hypothetical future requirements.** The code should have clean boundaries for future AI services, but it should not implement FastAPI, databases, Redis, Celery, LLMs, TTS, ASR, translation, subtitles, WebSockets, or video generation yet.

## 3. High-Level Architecture

The system consists of four primary layers: the asset authoring layer, the editable definition layer, the avatar runtime layer, and the web application layer.

The asset authoring layer uses Blender to create or modify the humanoid presenter. The original Blender project and its Python automation scripts are the maintainable source for structural 3D changes. Blender exports the resulting model to GLB, which acts as the distribution boundary between the authoring environment and the browser.

The editable definition layer contains JSON and TypeScript definitions for supported gestures, expressions, idle behavior, material overrides, camera configuration, and runtime settings. The AI agent should modify these definitions for behavior changes whenever possible. For example, adjusting the intensity of an emphasis gesture should generally involve changing a gesture parameter rather than modifying the character mesh or manually editing Blender.

The avatar runtime layer uses Three.js to load and render the GLB model. It exposes a stable semantic API and coordinates animation, facial controls, gaze, idle behavior, and audio playback. The runtime translates high-level commands into the concrete actions required by the loaded model. It must validate that requested bones, morph targets, and animation clips exist before using them.

The web application layer uses React, TypeScript, Vite, React Three Fiber, and Drei. React manages the page, UI controls, configuration, and lifecycle. React Three Fiber integrates the Three.js scene into React. The runtime handles animation updates without causing unnecessary React re-renders. A development panel allows a developer or AI agent to test the avatar interactively.

The intended architecture is:

```text
Developer describes a requested change
                 |
                 v
            AI Coding Agent
                 |
        Inspect current source and assets
                 |
                 v
       Choose the appropriate change path
                 |
        +--------+---------+
        |                  |
        v                  v
 JSON / TypeScript     Blender Python
 behavior changes      structural 3D changes
        |                  |
        v                  v
 Avatar Definitions    Blender Source Project
        |                  |
        |                  v
        |               Validate
        |                  |
        |                  v
        |              Export GLB
        |                  |
        +--------+---------+
                 |
                 v
           Avatar Runtime
                 |
                 v
       Three.js / React Three Fiber
                 |
                 v
       Browser-rendered 3D Presenter
```

The AI agent should decide which path to use based on the nature of the requested change. A material color, gesture intensity, camera position, or idle timing change should normally be handled in source configuration. A change to facial topology, body proportions, skin weights, or the skeleton requires Blender automation or another suitable 3D asset workflow.

## 4. Technology Stack

The frontend will use React, TypeScript, Vite, Three.js, React Three Fiber, and Drei. Blender will provide the 3D authoring environment and its Python API will support scripted scene inspection, modifications, validation, and GLB export. JSON will be used for editable declarative definitions when the information is naturally data-oriented, while TypeScript will be used for runtime behavior and validation. Vitest will provide unit testing, and ESLint and Prettier will enforce consistent code quality. npm will be the default package manager.

The application should initially run locally without requiring a backend. It should load the presenter asset from the frontend's public assets and play a local audio sample. This reduces setup complexity and makes it easier to validate the avatar runtime before introducing network services.

## 5. Repository Structure

Use a repository structure that separates the web application, avatar definitions, runtime, Blender automation, and documentation. Keep the project simple enough for a single developer and AI coding agent to understand.

```text
avatar-news-presenter/
├── apps/
│   └── web/
│       ├── public/
│       │   ├── avatars/
│       │   │   └── presenter.glb
│       │   └── audio/
│       │       └── test-presenter.mp3
│       └── src/
│           ├── app/
│           │   ├── App.tsx
│           │   └── routes.tsx
│           ├── avatar/
│           │   ├── components/
│           │   │   ├── Avatar.tsx
│           │   │   ├── AvatarScene.tsx
│           │   │   ├── AvatarCamera.tsx
│           │   │   ├── AvatarLighting.tsx
│           │   │   └── AvatarStatus.tsx
│           │   ├── runtime/
│           │   │   ├── AvatarRuntime.ts
│           │   │   ├── AnimationRuntime.ts
│           │   │   ├── GestureRuntime.ts
│           │   │   ├── FacialRuntime.ts
│           │   │   ├── GazeRuntime.ts
│           │   │   ├── IdleRuntime.ts
│           │   │   ├── RigAdapter.ts
│           │   │   └── runtimeTypes.ts
│           │   ├── definitions/
│           │   │   ├── avatar.schema.json
│           │   │   ├── avatar.json
│           │   │   ├── materials.json
│           │   │   ├── gestures/
│           │   │   │   ├── emphasize.json
│           │   │   │   ├── open-hand.json
│           │   │   │   ├── point-left.json
│           │   │   │   ├── point-right.json
│           │   │   │   └── hands-together.json
│           │   │   ├── expressions.json
│           │   │   └── idle.json
│           │   ├── animation/
│           │   │   ├── AnimationRegistry.ts
│           │   │   ├── AnimationStateMachine.ts
│           │   │   └── animationTypes.ts
│           │   ├── facial/
│           │   │   └── facialTypes.ts
│           │   ├── avatarConfig.ts
│           │   └── avatarTypes.ts
│           ├── audio/
│           │   ├── AudioController.ts
│           │   └── audioTypes.ts
│           ├── studio/
│           │   ├── Studio.tsx
│           │   └── studioConfig.ts
│           ├── ui/
│           │   ├── DebugPanel.tsx
│           │   ├── AnimationControls.tsx
│           │   ├── ExpressionControls.tsx
│           │   └── StatusPanel.tsx
│           ├── hooks/
│           │   ├── useAvatar.ts
│           │   └── useAudio.ts
│           ├── config/
│           │   └── environment.ts
│           ├── main.tsx
│           └── App.css
├── blender/
│   ├── source/
│   │   └── presenter.blend
│   ├── automation/
│   │   ├── inspect_scene.py
│   │   ├── modify_materials.py
│   │   ├── modify_character.py
│   │   ├── create_animation.py
│   │   ├── validate_rig.py
│   │   ├── validate_export.py
│   │   └── export_glb.py
│   ├── definitions/
│   │   ├── avatar.json
│   │   ├── materials.json
│   │   └── animations.json
│   ├── exports/
│   │   └── presenter.glb
│   └── README.md
├── tests/
│   ├── definitions/
│   ├── runtime/
│   └── fixtures/
├── docs/
│   ├── architecture.md
│   ├── avatar-spec.md
│   ├── animation-system.md
│   ├── blender-automation.md
│   └── asset-pipeline.md
├── package.json
├── README.md
├── .env.example
└── .gitignore
```

This structure is a starting point rather than a requirement to create empty files for every possible future feature. The coding agent should add modules when their functionality is implemented, and it should avoid creating unnecessary abstractions that have no current use.

## 6. The Avatar Asset and Blender Automation Strategy

The avatar must have a maintainable source project. The `.blend` file is the authoritative source for geometry, rigging, facial topology, skin weights, and any animation authored directly in Blender. The exported `presenter.glb` is the runtime asset used by the browser. Changes to the GLB must not be treated as the primary source-editing workflow.

The character should be a lightweight, professional humanoid news presenter suitable for waist-up framing. It should have a head, neck, torso, shoulders, arms, hands, and fingers where practical. It should use a humanoid armature that supports head rotation, neck movement, shoulder and arm movement, hand gestures, and natural posture. Facial controls should be included where the base character supports them, with semantic morph target names such as `mouth_open`, `mouth_wide`, `mouth_round`, `mouth_smile`, `mouth_frown`, `jaw_open`, `brow_up`, `brow_down`, `eye_blink_left`, `eye_blink_right`, `eye_wide`, and `eye_squint`.

The project should not depend on the AI agent creating a realistic human character from primitive meshes. Creating convincing human anatomy, topology, hair, hands, facial deformation, and skin weighting entirely from code would add unnecessary complexity and produce inconsistent results. Instead, begin with a suitable base humanoid model that has appropriate licensing and can legally be used and modified for the intended project. Verify that the character's rig and facial controls can support the required browser behaviors before adopting it as the project standard.

The Blender automation layer should provide scripts that inspect the current scene, list objects and collections, inspect materials, list bones and shape keys, list animation clips, apply supported modifications, validate requirements, and export the model. Each script should be runnable independently and should provide useful output that an AI coding agent can inspect. Scripts should not assume that objects have particular names without checking the scene first. If required objects are missing, the script should report a clear error instead of silently creating duplicate or incorrect objects.

For example, when asked to change the presenter's suit color, the AI agent should first inspect the existing materials and identify the correct material slot. It should then update the relevant material definition or execute a controlled Blender material modification script, depending on where the material is managed. When asked to change the emphasis gesture, the agent should prefer editing a gesture definition or runtime animation rather than modifying the Blender model. When asked to change the shape of the face or the body proportions, the agent should inspect the available source geometry and rig before deciding whether a scripted Blender change is feasible.

The Blender automation workflow should follow this sequence:

```text
Inspect source project
        |
        v
Check required objects and materials
        |
        v
Apply a targeted modification
        |
        v
Save a recoverable project version
        |
        v
Validate scene and rig
        |
        v
Export GLB to a temporary location
        |
        v
Validate exported asset
        |
        v
Promote validated export to runtime assets
```

The original source file should not be overwritten before a modification has passed validation. For destructive or structural operations, create a backup or save to a new version first. A failed export must not replace a previously working runtime asset.

## 7. Data-Driven Avatar Definitions

Avatar definitions are the preferred interface for AI-agent edits that do not require changes to the 3D mesh or skeleton. These definitions should be readable, version-controlled, schema-validated, and independent of low-level Three.js implementation details.

The avatar definition should identify the asset, supported semantic capabilities, optional material overrides, and configuration. For example:

```json
{
  "schemaVersion": 1,
  "avatarId": "news-presenter",
  "modelUrl": "/avatars/presenter.glb",
  "capabilities": {
    "idle": true,
    "gestures": true,
    "expressions": true,
    "gaze": true,
    "audioPlayback": true,
    "productionLipSync": false
  },
  "defaults": {
    "expression": "neutral",
    "gaze": "camera",
    "idleBehavior": "professional"
  }
}
```

Gesture definitions should describe semantic intent and configurable behavior. The runtime should translate these definitions into supported bone transforms, animation clips, or procedural motion. A gesture should not expose internal bone names as its public interface. For example:

```json
{
  "schemaVersion": 1,
  "name": "emphasize",
  "duration": 1.2,
  "hand": "right",
  "intensity": 0.65,
  "headMotion": {
    "type": "nod",
    "intensity": 0.25
  },
  "returnToIdle": true
}
```

This definition describes the intended behavior, but it does not guarantee that any arbitrary model can perform the gesture. The runtime must check the loaded model's capabilities and rig mapping. If the rig cannot perform a requested gesture correctly, the application should display a useful warning and fall back to an available behavior rather than corrupting the character pose.

A JSON schema or equivalent runtime validation must check required fields, supported gesture names, numeric ranges, duration, and schema version. Invalid definitions should be rejected with readable errors. Definitions should include versioning so future changes to the data format can be migrated without silently breaking existing assets.

## 8. Avatar Runtime Architecture

The avatar runtime is the boundary between semantic commands and the actual 3D implementation. It should expose a stable TypeScript API and hide Three.js objects, animation mixers, bone mappings, morph target indexes, and loaded scene internals from application UI code.

A conceptual API is:

```ts
type GestureName =
  | "openHand"
  | "emphasize"
  | "pointLeft"
  | "pointRight"
  | "handsTogether";

type ExpressionName =
  | "neutral"
  | "serious"
  | "positive"
  | "concerned";

type GazeTarget = "camera" | "left" | "right" | "neutral";

interface AvatarController {
  playGesture(name: GestureName): void;
  setExpression(name: ExpressionName): void;
  setGaze(target: GazeTarget): void;
  setHeadMotion(name: string): void;
  startSpeaking(): void;
  stopSpeaking(): void;
  reset(): void;
  dispose(): void;
}
```

This interface is illustrative; the coding agent should refine it into fully typed contracts and avoid unnecessary methods. Production lip synchronization is out of scope for Phase 1, so `startSpeaking` and `stopSpeaking` may remain simple placeholders or be omitted from the initial public API if they are not needed. The important requirement is that future speech behavior can be introduced without exposing renderer internals.

The runtime should contain dedicated modules for animation, gestures, facial expressions, gaze, idle behavior, rig adaptation, and audio playback. These modules should be small and composable. The `RigAdapter` should inspect the loaded model and map semantic capabilities to available bones, morph targets, and animation clips. It should be the only module that knows the model-specific mapping details.

The runtime must not assume that all assets share identical rig structures. It should validate the capabilities available in the loaded GLB and report missing features. The runtime API should remain stable even if a later avatar asset uses a different skeleton or facial rig.

## 9. Animation Strategy

Phase 1 should use a hybrid animation approach rather than requiring every motion to be authored in Blender. Existing GLB animation clips should be used when they are available and suitable. Procedural animation should be used for simple motions that can be implemented safely and naturally in the runtime. More complex or highly art-directed animation can be authored in Blender and exported as a clip.

Use stable semantic names for any imported clips, such as `Idle_Neutral`, `Idle_Breathing`, `Head_Nod_Small`, `Gesture_OpenHand`, `Gesture_Emphasize`, `Gesture_PointLeft`, `Gesture_PointRight`, `Gesture_HandsTogether`, `Emotion_Neutral`, `Emotion_Serious`, `Emotion_Positive`, `Emotion_Concerned`, and `Blink`. These names are a naming contract, not a requirement to fabricate clips that the character cannot support. If a required gesture is not available, the team must either implement it procedurally, create it through Blender automation, or clearly report that the capability remains incomplete.

The runtime should support idle animation, one-shot gestures, looping motions, smooth transitions, and return-to-idle behavior. It should prevent conflicting commands from leaving the avatar in invalid poses. Animation priorities may be used to coordinate idle, head motion, gestures, facial expressions, and future speech. Phase 1 does not need a sophisticated universal animation blending framework, but its implementation should be structured so more advanced layers can be added later.

At minimum, the demonstrator should support five gestures: open hand, emphasize, point left, point right, and hands together. It should support neutral, serious, positive, and concerned expressions. Head motions should include nod, turn left, turn right, tilt left, and tilt right where the available rig permits them.

## 10. Idle Behavior, Gaze, and Facial Controls

The idle system should make the presenter appear attentive and professional while waiting or listening. It should support subtle breathing, randomized blinking, small eye movements, occasional gentle head movements, and optional posture adjustments. The movements must not be exaggerated or continuous enough to distract from a news presentation.

Blinking should use small randomized intervals rather than a perfectly predictable timer. The implementation should avoid modifying the same facial controls from multiple controllers without coordination. For example, a blink controller and an expression controller must not overwrite each other's values unexpectedly. Facial controls should use a centralized controller that manages the final blend shape values or coordinates the supported animation layers.

Expressions should be semantic. The UI should call `setExpression("serious")` rather than manipulating morph target indexes. The runtime should map each expression to the controls supported by the loaded asset, blend changes smoothly where practical, and restore neutral values when requested.

Gaze should initially support camera-facing behavior and simple directional changes. Eye tracking should remain subtle. If the model has no independent eye bones or usable eye controls, the runtime should report the limitation and use a safe fallback.

## 11. Three.js Scene and Studio

The browser scene should be implemented with React Three Fiber and Drei. It should include a configurable camera, lightweight studio background, floor or backdrop, and simple key, fill, and rim lighting where useful. The presenter should be framed approximately waist-up for a news presentation. Camera position, target, field of view, lighting intensity, background color, and pixel ratio should be centrally configurable rather than scattered throughout components.

Three.js may create simple studio geometry and presentation props directly in code. This is a good use of procedural geometry because desks, panels, screens, and simple set elements are easier to describe as parameters than as complex sculpted assets. The frontend should not attempt to procedurally construct a realistic human character from primitive geometry.

The studio should remain lightweight. Avoid unnecessary geometry, expensive post-processing, excessive shadow maps, complex physics, and large textures. The goal is a clean, professional prototype that runs comfortably on modest development hardware.

## 12. Audio Controller

Phase 1 must support local audio loading and playback. The audio controller should provide load, play, pause, stop, current time, duration, and cleanup operations. A sample file should be included at `/audio/test-presenter.mp3`, or the application should provide a clear setup instruction if a licensed sample is not supplied.

Audio playback must not depend on a backend. The debug panel should allow the developer to play and pause the sample and inspect its current time and duration. Production lip synchronization is explicitly out of scope, but the audio controller should be designed so future audio-time events can drive a lip-sync controller without requiring the audio implementation to be rewritten.

## 13. Debug Panel and Development Experience

The MVP should include a development-only debug panel for testing avatar capabilities. It should provide controls for idle behavior, the five required gestures, four facial expressions, available head motions, and audio playback. It should also display whether the model has loaded, which semantic capabilities are available, the current animation or state, the current expression, audio time, and any asset validation warnings.

The debug panel should call the public avatar API rather than directly manipulating Three.js meshes or bones. This ensures the UI tests the same interface that future AI commands will use. The panel should be easy to disable through configuration, and it must not become a production dependency of the runtime.

The developer experience should be designed around short feedback loops. An AI agent should be able to modify a gesture JSON file or TypeScript module, run the test suite, start the frontend, and inspect the result. For Blender changes, the agent should run an inspection script first, execute a targeted modification script, validate the result, export the GLB, and then launch the web preview.

## 14. Performance and Compatibility

The application should target 1080p presentation and aim for approximately 30–60 FPS where practical on modest hardware. It should avoid ray tracing, excessively dense meshes, 4K textures, unnecessary real-time shadows, expensive post-processing, and complex simulations. Use efficient GLB assets and sensible material counts. Compression techniques such as Draco, Meshopt, or KTX2 may be introduced later if asset size or load performance justifies them.

The application must handle window resizing, asset loading errors, missing animation clips, missing shape keys, invalid definitions, audio failures, and unsupported rendering environments gracefully. An optional feature being unavailable must not crash the entire application. Warnings should identify the missing capability and, where possible, provide an actionable resolution.

The project should not rely on a specific GPU or a dedicated backend. All Phase 1 functionality should be demonstrable locally with the chosen development environment.

## 15. Testing and Validation

Use Vitest for unit tests covering semantic definition validation, gesture mapping, expression mapping, animation state transitions, configuration validation, and error handling. Runtime tests should verify that invalid semantic commands are rejected safely and that unsupported model capabilities do not produce unhandled errors.

Blender automation should be tested independently where practical. The scene inspection script must report object names, collection names, materials, armatures, bones, shape keys, and animation clips. The rig validation script must check required bones and facial controls against the expected avatar specification. The export validation script must verify that the exported GLB exists and contains the expected model features and clips to the extent that can be checked automatically.

Manual browser validation must verify that the presenter loads correctly, appears at the intended scale and orientation, breathes, blinks, moves its eyes where supported, changes expressions, performs at least five gestures, returns to idle after one-shot gestures, and plays the test audio. It must also verify that the debug panel works, resizing is handled, errors are displayed clearly, and the application remains responsive.

## 16. Implementation Workflow for AI Coding Agents

The AI coding agent must not try to implement the whole project in a single unverified pass. It should inspect the repository and implement the MVP in small, testable stages. Each stage must preserve working functionality and include the necessary documentation.

The first stage is project setup: create React, TypeScript, Vite, linting, formatting, and Vitest. The second stage is the Three.js scene, including camera, lighting, background, and studio. The third stage is GLB loading and model inspection. The fourth stage establishes the avatar runtime API and rig adapter. The fifth stage implements semantic definitions and validation. The sixth stage implements animation playback and state transitions. The seventh stage adds idle behavior, facial expressions, gaze, and gesture playback. The eighth stage adds local audio. The ninth stage creates the debug panel. The tenth stage adds tests, performance checks, and documentation.

If a suitable rigged avatar is not available at the beginning, the coding agent must not pretend that a production-quality presenter exists. It should establish the asset interface, use a clearly identified placeholder if needed, and document the required model capabilities. The project should then replace the placeholder with a properly licensed and validated avatar before claiming that the final character requirements are complete.

The agent should create or modify Blender assets only when required. Before each structural Blender modification, it must inspect the current project and identify the objects, materials, armature, and shape keys involved. It must use a targeted Python script, preserve recoverable versions, validate the result, and export only when checks pass. If a requested visual change cannot be reliably achieved through Blender scripting, the agent must explain the limitation and offer the smallest practical manual step rather than making an unverified destructive change.

## 17. Engineering Rules

Do not put all avatar logic into one React component. Do not directly manipulate Three.js animation objects from UI components. Do not rely on numeric animation indexes. Do not scatter model-specific bone or morph target names throughout the application. Do not update React state on every animation frame. Do not replace a working GLB with an unvalidated export. Do not overwrite the original Blender source before a risky structural operation. Do not introduce backend infrastructure before the local browser runtime is working.

All application-level animation requests must use semantic identifiers. All avatar definitions must be validated. All Blender scripts must inspect the current scene before modifying it. All runtime controllers must handle missing capabilities safely. All important configuration should be centralized. The renderer and rig details must remain hidden behind the runtime API.

## 18. Future Compatibility

The Phase 1 architecture must allow later phases to introduce TTS, lip synchronization, subtitles, multilingual audio, translation, a FastAPI backend, LLM-generated animation plans, WebSocket events, iframe embedding, and automated video generation. These features must not be implemented during Phase 1.

Future AI systems should produce semantic animation plans rather than raw bone rotations or renderer-specific instructions. A future animation plan may include a time range, emotion, gesture, head motion, and gaze target. The runtime will interpret these semantic commands and map them to the capabilities of the active avatar asset.

The same avatar should eventually support multiple languages by changing the audio, subtitle content, and lip-sync timing rather than requiring a separate character for each language. The web application should remain suitable for future iframe embedding, but production embedding and deployment infrastructure are out of scope for Phase 1.

## 19. Definition of Done

Phase 1 is complete when a developer can clone the repository, install dependencies, start the web application locally, and see the presenter in a browser without needing a backend. The presenter must have a working asset pipeline, a semantic runtime API, idle behavior, blinking, subtle eye and head movement where supported, facial expressions, at least five gestures, and local audio playback. The debug panel must trigger these behaviors through the public API, and the project must include tests, setup instructions, architecture documentation, Blender automation documentation, and clear validation output.

The system must also demonstrate that the AI agent can modify an ordinary behavior through JSON or TypeScript, run the tests, and verify the result without editing the GLB directly. For a structural 3D change, the project must provide a documented Blender Python automation workflow that inspects the scene, makes a targeted change, validates the result, and exports a new GLB safely.

## 20. Final Architectural Principle

The long-term design is based on the following division of responsibilities:

- **Blender** is the source environment for character geometry, rigging, facial topology, skin weights, and selected authored animation assets.
- **Blender Python automation** is the controlled mechanism for AI-agent-driven structural 3D changes, inspection, validation, and export.
- **GLB** is the validated runtime asset format, not the primary editable source of application behavior.
- **JSON definitions** represent declarative avatar configuration and simple semantic behavior that should be easy for an AI agent to modify.
- **TypeScript** implements runtime logic, validation, animation coordination, and application-level behavior.
- **Three.js** renders the model and executes browser-side animation efficiently.
- **React** manages the web application, user interface, lifecycle, and configuration.
- **Avatar Runtime** translates semantic commands into model-specific animation and facial controls.
- **Future Python backend services** will orchestrate AI, TTS, ASR, translation, and real-time communication when those phases are implemented.
- **Future LLM systems** will plan semantic presenter behavior without needing to understand Blender internals, GLB structures, Three.js objects, or bone indexes.

The Phase 1 MVP must establish these boundaries clearly. The objective is not to eliminate Blender or build an entire 3D modeling system in TypeScript. The objective is to make 3D authoring programmable, keep ordinary behavior changes in readable source files, and let the browser runtime handle interactive presentation. This gives the project a practical balance of visual quality, AI-agent maintainability, development efficiency, and future scalability.