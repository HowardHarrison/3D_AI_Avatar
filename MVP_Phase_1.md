# 3D Avatar News Presenter — Phase 1 MVP Implementation Specification

## 1. Project Overview

Build a scalable and maintainable **Phase 1 MVP** for a browser-based 3D Avatar News Presenter.

The system should use:

- **Blender** for creating and authoring the 3D avatar and animations.
- **GLB/GLTF** as the asset boundary between Blender and the web application.
- **React + TypeScript** for the frontend application.
- **Three.js / React Three Fiber** for rendering the 3D avatar in the browser.
- A modular avatar runtime that can later support:
  - lip synchronization
  - TTS
  - subtitles
  - multilingual speech
  - LLM-generated animation plans
  - WebSocket-based real-time interaction
  - FastAPI backend
  - video generation
  - iframe embedding

The Phase 1 implementation must focus on building a strong foundation rather than implementing AI functionality.

---

# 2. Phase 1 Goal

The Phase 1 MVP should produce a web application where:

1. A professional humanoid 3D presenter is loaded from a `.glb` file.
2. The avatar is displayed using Three.js / React Three Fiber.
3. The avatar has a proper humanoid skeleton.
4. The avatar has facial shape keys / blend shapes.
5. The avatar can:
   - stand naturally
   - breathe
   - blink
   - move its eyes
   - perform subtle head movements
   - change facial expressions
   - perform hand gestures
6. Animations can be controlled through a clean TypeScript API.
7. Animations blend smoothly.
8. Audio can be loaded and played locally.
9. A development/debug panel can trigger animations manually.
10. The architecture is ready for future AI integration.

The system should be designed so that future backend/AI functionality can be added without rewriting the avatar runtime.

---

# 3. Phase 1 Scope

## 3.1 Included

Phase 1 must include:

- React
- TypeScript
- Vite
- Three.js
- React Three Fiber
- Drei
- Blender
- GLB/GLTF
- Humanoid avatar
- Facial shape keys
- Idle animation
- Breathing animation
- Blinking
- Eye movement
- Head movement
- Facial expressions
- At least 5 hand/body gestures
- Animation state management
- Animation blending
- Camera system
- Lighting
- Studio background
- Local audio playback
- Debug controls
- Error handling
- Basic performance optimization
- Unit tests
- Documentation
- Clean project structure

---

# 4. Phase 1 Out of Scope

Do NOT implement these yet:

- LLM integration
- Gemini integration
- TTS
- ASR
- Production lip synchronization
- Translation
- Subtitles
- WebSocket
- FastAPI
- Database
- Redis
- Celery
- Authentication
- Cloud storage
- CDN
- Production deployment
- Blender server rendering
- Automated video generation
- Motion capture
- AI facial animation
- Complex physics
- Real-time conversational AI
- Production-level streaming

However, the architecture must allow these features to be added later without major refactoring.

---

# 5. Core Architecture

The most important architectural decision is:

> Blender is an asset creation and animation authoring tool, NOT the browser runtime renderer.

The browser should render the exported GLB file using Three.js.

Architecture:

```text
                    BLENDER
                       │
                       │
                       ▼
                presenter.blend
                       │
                       │ Export
                       ▼
                 presenter.glb
                       │
                       │
                       ▼
                React Application
                       │
                       ▼
             React Three Fiber
                       │
                       ▼
                Avatar Runtime
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Animation       Facial         Audio
   Controller      Controller     Controller
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                  Three.js
                       │
                       ▼
                Browser GPU
                       │
                       ▼
               3D News Presenter
```

---

# 6. Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Three.js
- React Three Fiber
- Drei

## 3D

- Blender
- GLB
- GLTF
- Humanoid armature
- Shape keys / morph targets

## Testing

- Vitest

## Code Quality

- ESLint
- Prettier

## Package Manager

Use npm unless there is a strong reason to use another package manager.

---

# 7. Repository Structure

Use the following structure:

```text
avatar-news-presenter/
│
├── apps/
│   └── web/
│       ├── public/
│       │   ├── avatars/
│       │   │   └── presenter.glb
│       │   │
│       │   └── audio/
│       │       └── test-presenter.mp3
│       │
│       └── src/
│           │
│           ├── app/
│           │   ├── App.tsx
│           │   └── routes.tsx
│           │
│           ├── avatar/
│           │   │
│           │   ├── components/
│           │   │   ├── Avatar.tsx
│           │   │   ├── AvatarScene.tsx
│           │   │   ├── AvatarCamera.tsx
│           │   │   └── AvatarLighting.tsx
│           │   │
│           │   ├── animation/
│           │   │   ├── AnimationController.ts
│           │   │   ├── AnimationStateMachine.ts
│           │   │   ├── AnimationRegistry.ts
│           │   │   ├── IdleController.ts
│           │   │   └── animationTypes.ts
│           │   │
│           │   ├── facial/
│           │   │   ├── FacialController.ts
│           │   │   └── facialTypes.ts
│           │   │
│           │   ├── avatarTypes.ts
│           │   └── avatarConfig.ts
│           │
│           ├── audio/
│           │   ├── AudioController.ts
│           │   └── audioTypes.ts
│           │
│           ├── studio/
│           │   ├── Studio.tsx
│           │   └── studioConfig.ts
│           │
│           ├── ui/
│           │   ├── DebugPanel.tsx
│           │   ├── AnimationControls.tsx
│           │   └── StatusPanel.tsx
│           │
│           ├── hooks/
│           │   ├── useAvatar.ts
│           │   ├── useAnimation.ts
│           │   └── useAudio.ts
│           │
│           ├── config/
│           │   └── environment.ts
│           │
│           ├── types/
│           │   └── index.ts
│           │
│           ├── main.tsx
│           └── App.css
│
├── packages/
│   └── shared/
│       └── src/
│           ├── animation.ts
│           ├── avatar.ts
│           ├── events.ts
│           └── index.ts
│
├── blender/
│   ├── source/
│   │   └── presenter.blend
│   │
│   ├── scripts/
│   │   ├── export_glb.py
│   │   └── validate_rig.py
│   │
│   ├── animations/
│   │   ├── idle/
│   │   ├── gestures/
│   │   └── expressions/
│   │
│   ├── exports/
│   │   └── presenter.glb
│   │
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── avatar-spec.md
│   ├── animation-system.md
│   └── blender-pipeline.md
│
├── package.json
├── README.md
├── .env.example
└── .gitignore
```

Do not put all avatar logic into one React component.

---

# 8. Blender Asset Specification

The Blender character should be a lightweight professional humanoid news presenter.

The initial camera framing should be approximately waist-up.

The character should be suitable for:

- news presentation
- educational presentation
- AI assistant
- future conversational avatar

Avoid unnecessarily high-poly geometry.

---

# 9. Character Requirements

The avatar should contain:

## Body

- Head
- Neck
- Shoulders
- Upper body
- Arms
- Hands
- Fingers where practical

## Rig

Use a proper humanoid armature.

The rig should support:

- head rotation
- neck movement
- shoulder movement
- arm movement
- hand movement
- body posture

---

# 10. Facial Shape Keys

The avatar should expose facial shape keys / morph targets.

At minimum:

```text
mouth_open
mouth_close
mouth_wide
mouth_round
mouth_smile
mouth_frown
jaw_open
brow_up
brow_down
eye_blink_left
eye_blink_right
eye_wide
eye_squint
```

The exact implementation may vary depending on the Blender rig.

The important requirement is that the browser can access the facial controls through GLB morph targets.

---

# 11. Animation Naming Contract

Use semantic and stable animation names.

Do NOT rely on Blender animation array indexes.

Recommended animation names:

```text
Idle_Neutral
Idle_Breathing
Idle_ShiftWeight

Head_Nod_Small
Head_Turn_Left
Head_Turn_Right
Head_Tilt_Left
Head_Tilt_Right

Gesture_OpenHand
Gesture_Emphasize
Gesture_PointLeft
Gesture_PointRight
Gesture_HandsTogether
Gesture_Nod

Emotion_Neutral
Emotion_Serious
Emotion_Positive
Emotion_Concerned

Blink
```

At least five gesture animations must exist.

---

# 12. GLB Export Requirements

The exported GLB should contain:

- meshes
- materials
- textures
- armature
- bones
- facial morph targets
- animation clips

The browser must NOT need the `.blend` file.

The browser should only load:

```text
presenter.glb
```

---

# 13. Blender Validation

Create a Blender validation script:

```text
blender/scripts/validate_rig.py
```

The validation script should check:

- avatar exists
- armature exists
- required bones exist
- required animations exist
- required shape keys exist
- scale is reasonable
- orientation is correct
- transforms are applied where appropriate
- materials exist
- textures are available
- animation clips are present

The script should report:

```text
PASS
WARNING
ERROR
```

Missing optional animations should generate warnings rather than immediately crashing the pipeline.

---

# 14. Avatar Runtime API

The rest of the application should communicate with the avatar through a clean runtime API.

Example:

```ts
interface AvatarController {
  playGesture(name: GestureName): void;

  setExpression(name: ExpressionName): void;

  setHeadMotion(name: HeadMotionName): void;

  setGaze(target: GazeTarget): void;

  startSpeaking(): void;

  stopSpeaking(): void;

  reset(): void;
}
```

External UI code should NOT directly manipulate:

- AnimationMixer
- AnimationAction
- Three.js scene objects
- bones
- morphTargetInfluences

Those implementation details must remain inside the avatar runtime.

---

# 15. Animation Controller

Create:

```text
AnimationController.ts
```

Responsibilities:

- load animation clips
- register animations
- play animations
- stop animations
- loop animations
- play one-shot animations
- crossfade animations
- manage priorities
- return to idle
- handle invalid animation names
- update animations every frame
- dispose resources

Example API:

```ts
class AnimationController {
  play(name: string, options?: PlayAnimationOptions): void;

  stop(name?: string): void;

  stopAll(): void;

  update(delta: number): void;

  dispose(): void;
}
```

---

# 16. Animation Layers

Use conceptual animation layers.

Recommended priorities:

```text
Idle              0
Head Motion      10
Gesture          20
Expression       30
Speech/LipSync   40
Override        100
```

Phase 1 does not need full production-grade layered animation blending, but the architecture should support it later.

---

# 17. Animation State Machine

Create:

```text
AnimationStateMachine.ts
```

Initial states:

```text
IDLE
SPEAKING
GESTURE
TRANSITION
```

Example:

```text
IDLE
 │
 │ play gesture
 ▼
GESTURE
 │
 │ gesture finished
 ▼
IDLE
```

Future:

```text
IDLE
  ↓
SPEAKING
  ↓
SPEAKING + GESTURE
  ↓
SPEAKING
  ↓
IDLE
```

---

# 18. Animation Registry

Create a semantic registry.

Example:

```ts
const animationRegistry = {
  idle: {
    neutral: "Idle_Neutral",
    breathing: "Idle_Breathing",
  },

  gestures: {
    openHand: "Gesture_OpenHand",
    emphasize: "Gesture_Emphasize",
    pointLeft: "Gesture_PointLeft",
    pointRight: "Gesture_PointRight",
    handsTogether: "Gesture_HandsTogether",
  },

  expressions: {
    neutral: "Emotion_Neutral",
    serious: "Emotion_Serious",
    positive: "Emotion_Positive",
    concerned: "Emotion_Concerned",
  },

  head: {
    nod: "Head_Nod_Small",
    left: "Head_Turn_Left",
    right: "Head_Turn_Right",
  },

  blink: "Blink",
};
```

The rest of the application should use:

```ts
playGesture("emphasize");
```

instead of:

```ts
playAnimation(7);
```

Never expose numeric animation indexes.

---

# 19. Idle Controller

Create:

```text
IdleController.ts
```

The idle system should make the presenter feel alive.

It should support:

- subtle breathing
- random blinking
- eye movement
- occasional small head movement
- optional posture shifting

The movements should be subtle.

Avoid:

```text
constant head movement
constant blinking
exaggerated breathing
random large movements
```

The goal is:

> Professional human presenter waiting or listening.

---

# 20. Blink System

Blinking should be controlled independently.

Example behavior:

```text
wait 3–6 seconds
      ↓
close eyes
      ↓
short delay
      ↓
open eyes
      ↓
reset timer
```

The exact timing should include small random variation.

Do not blink on a perfectly predictable timer.

---

# 21. Facial Controller

Create:

```text
FacialController.ts
```

Example API:

```ts
interface FacialController {
  setExpression(name: ExpressionName): void;

  setBlendShape(name: string, value: number): void;

  reset(): void;
}
```

Expression type:

```ts
type ExpressionName =
  | "neutral"
  | "serious"
  | "positive"
  | "concerned";
```

The facial controller should hide the actual Three.js morph target implementation.

---

# 22. Gesture Controller

Gestures should be semantic.

Example:

```ts
playGesture("openHand");
playGesture("emphasize");
playGesture("pointLeft");
playGesture("pointRight");
playGesture("handsTogether");
```

Gesture behavior:

```text
Idle
 ↓
Crossfade into gesture
 ↓
Play gesture
 ↓
Crossfade back to idle
```

Gestures should not permanently leave the avatar in an invalid pose.

---

# 23. Head Motion

Support:

```text
nod
turnLeft
turnRight
tiltLeft
tiltRight
```

Head motion should be subtle and should blend with idle animation.

---

# 24. Camera

The default camera should be suitable for a news presenter.

Example configuration:

```ts
const cameraConfig = {
  position: [0, 1.65, 3.2],
  target: [0, 1.4, 0],
  fov: 35,
};
```

The avatar should appear approximately waist-up.

The camera should be configurable rather than hard-coded inside the component.

---

# 25. Lighting

Use a lightweight studio lighting setup.

Conceptually:

```text
             Rim Light
                 \
                  \
        Presenter
          /     \
         /       \
     Key Light   Fill Light
```

Use:

- key light
- fill light
- rim light
- optional environment light

Avoid expensive lighting techniques during Phase 1.

---

# 26. Studio

Create:

```text
Studio.tsx
```

The studio can contain:

- background
- floor
- lights
- optional desk
- optional news props

Keep geometry simple.

Avoid:

- high-resolution textures
- heavy post-processing
- expensive simulations
- unnecessary geometry

---

# 27. React Component Architecture

Recommended structure:

```tsx
<App>
  <AvatarPage>
    <AvatarScene>
      <Studio />
      <Avatar />
      <AvatarCamera />
      <AvatarLighting />
    </AvatarScene>

    <DebugPanel />
  </AvatarPage>
</App>
```

Responsibilities:

### React

React manages:

- UI
- lifecycle
- user interaction
- configuration
- page state

### Three.js / R3F

Three.js manages:

- 3D scene
- models
- camera
- lighting
- rendering

### Avatar Runtime

Runtime manages:

- animations
- facial controls
- gestures
- idle behavior
- state machine
- audio synchronization

Do not mix these responsibilities unnecessarily.

---

# 28. State Management

Do not introduce a large global state library unless it becomes necessary.

Use:

- React state for UI state
- runtime classes for animation state
- refs for Three.js objects

Avoid putting per-frame state into React.

Do NOT do:

```ts
setState(...)
```

every animation frame.

The render loop should directly update the avatar runtime.

Conceptually:

```text
requestAnimationFrame
        ↓
delta
        ↓
AvatarRuntime.update(delta)
        ↓
AnimationController
FacialController
IdleController
AudioController
```

---

# 29. Audio Controller

Create:

```text
AudioController.ts
```

Phase 1 only requires local audio playback.

Example API:

```ts
interface AudioController {
  load(url: string): Promise<void>;

  play(): void;

  pause(): void;

  stop(): void;

  getCurrentTime(): number;

  getDuration(): number;

  dispose(): void;
}
```

Use:

```text
public/audio/test-presenter.mp3
```

for testing.

---

# 30. Future Lip Sync Architecture

Do not implement production lip sync in Phase 1.

However, the architecture should allow:

```text
Audio
  ↓
LipSyncController
  ↓
Viseme Events
  ↓
FacialController
  ↓
Morph Targets
```

Future event:

```ts
interface VisemeEvent {
  time: number;
  duration: number;
  viseme: string;
}
```

Example:

```json
{
  "time": 1.42,
  "duration": 0.12,
  "viseme": "AA"
}
```

---

# 31. Future Animation Plan

The runtime should eventually support semantic animation plans.

Example:

```ts
interface AnimationSegment {
  start: number;
  end: number;

  emotion?: ExpressionName;

  gesture?: GestureName;

  headMotion?: HeadMotionName;

  gaze?: GazeTarget;
}
```

Example:

```json
{
  "segments": [
    {
      "start": 0,
      "end": 4.2,
      "emotion": "positive",
      "gesture": "openHand",
      "headMotion": "nod",
      "gaze": "camera"
    },
    {
      "start": 4.2,
      "end": 9.8,
      "emotion": "serious",
      "gesture": "emphasize",
      "gaze": "camera"
    }
  ]
}
```

Phase 1 may use hard-coded animation plans.

The important requirement is:

> The runtime must not care where the animation plan came from.

Later it may come from:

- LLM
- Python backend
- WebSocket
- database
- predefined script

---

# 32. AI Semantic Boundary

Future AI systems must NOT directly control:

- Blender bones
- Three.js objects
- AnimationMixer
- morph target indexes
- mesh names
- skeleton implementation

Instead:

```text
AI / Backend
      ↓
Semantic Animation Commands
      ↓
Avatar Runtime
      ↓
Animation Controller
      ↓
Three.js
      ↓
GLB
```

For example:

```json
{
  "emotion": "serious",
  "gesture": "emphasize",
  "headMotion": "nod",
  "gaze": "camera"
}
```

The AI should never output:

```json
{
  "bone_rotation_x": 0.238,
  "bone_rotation_y": -0.71
}
```

This separation is critical for maintainability.

---

# 33. Debug Panel

Create a development-only debug panel.

It should provide:

## Animation Controls

Buttons:

```text
Idle
Open Hand
Emphasize
Point Left
Point Right
Hands Together
Nod
```

## Expression Controls

```text
Neutral
Serious
Positive
Concerned
```

## Head Controls

```text
Nod
Turn Left
Turn Right
Tilt Left
Tilt Right
```

## Audio Controls

```text
Load Audio
Play
Pause
Stop
```

## Runtime Information

Display:

```text
FPS
Avatar Loaded
Current State
Active Animation
Current Expression
Audio Time
Audio Duration
```

The debug panel should be easy to disable through configuration.

---

# 34. Avatar Configuration

Create:

```text
avatarConfig.ts
```

Example:

```ts
export const avatarConfig = {
  modelUrl: "/avatars/presenter.glb",

  camera: {
    position: [0, 1.65, 3.2],
    target: [0, 1.4, 0],
    fov: 35,
  },

  performance: {
    pixelRatioMax: 1.5,
  },
};
```

Do not scatter these values throughout the codebase.

---

# 35. Environment Configuration

Create:

```text
.env.example
```

Example:

```env
VITE_APP_NAME=Avatar News Presenter

VITE_AVATAR_MODEL_URL=/avatars/presenter.glb

VITE_ENABLE_DEBUG_PANEL=true
```

Never put secrets into frontend environment variables.

---

# 36. Performance Requirements

The development machine may have approximately:

```text
CPU:
Intel Core i7-1255U

RAM:
16 GB

GPU:
Intel Iris Xe
NVIDIA GeForce MX550 2 GB
```

Therefore, optimize the MVP for modest hardware.

Target:

```text
1080p
30–60 FPS where practical
```

Avoid:

- ray tracing
- extremely high polygon counts
- 4K textures
- unnecessary shadow maps
- expensive post-processing
- complex physics
- heavy particle systems
- unnecessary simulations

Use efficient GLB assets.

Future optimization options may include:

- Draco compression
- Meshopt
- KTX2 textures

Do not add these unless they provide a measurable benefit or are necessary.

---

# 37. Loading and Error Handling

The application must handle:

## GLB Loading Failure

Display:

```text
Failed to load avatar.
```

Do not crash the entire application.

## Missing Animation

Display a warning:

```text
Animation "Gesture_PointLeft" not found.
```

The application should continue running.

## Missing Facial Shape Key

Display a warning.

Do not crash.

## Audio Failure

Display an appropriate error.

## Invalid Configuration

Validate configuration during initialization.

## Unsupported Rendering

Provide a useful fallback/error message.

---

# 38. Logging

Create a lightweight logging abstraction.

Example:

```ts
logger.debug(...)
logger.info(...)
logger.warn(...)
logger.error(...)
```

Avoid scattered:

```ts
console.log(...)
```

throughout the application.

This makes it easier to change logging behavior later.

---

# 39. Testing

Use Vitest.

Unit tests should cover:

## Animation Registry

Verify:

- semantic names map correctly
- invalid names are handled

## Animation State Machine

Test:

```text
IDLE → GESTURE
GESTURE → IDLE
IDLE → SPEAKING
```

## Gesture Mapping

Test:

```text
openHand
emphasize
pointLeft
pointRight
handsTogether
```

## Expression Mapping

Test:

```text
neutral
serious
positive
concerned
```

## Animation Plan Parsing

Validate:

```text
start
end
emotion
gesture
headMotion
gaze
```

## Configuration

Validate avatar configuration.

---

# 40. Manual Testing

The implementation must be manually tested in a browser.

Verify:

- GLB loads
- avatar is visible
- camera framing is correct
- lighting works
- idle animation works
- breathing works
- blinking works
- eye movement works
- expressions work
- gestures work
- gestures return to idle
- animations crossfade correctly
- audio loads
- audio plays
- debug panel works
- browser resizing works
- loading errors are handled

---

# 41. Acceptance Criteria

## Avatar

- [ ] Presenter loads from GLB.
- [ ] Presenter is humanoid.
- [ ] Presenter has facial morph targets.
- [ ] Presenter has a working armature.
- [ ] Presenter looks professional.
- [ ] Presenter is framed waist-up.

## Animation

- [ ] Idle animation works.
- [ ] Breathing works.
- [ ] Blinking works.
- [ ] Eye movement works.
- [ ] Head movement works.
- [ ] At least five gestures work.
- [ ] Facial expressions work.
- [ ] Gestures return to idle.
- [ ] Animation transitions are smooth.

## Audio

- [ ] Local audio can be loaded.
- [ ] Audio can play.
- [ ] Audio can pause.
- [ ] Audio can stop.
- [ ] Current audio time is available.

## UI

- [ ] Debug panel works.
- [ ] Animation buttons work.
- [ ] Expression buttons work.
- [ ] Head controls work.
- [ ] Audio controls work.
- [ ] Runtime status is displayed.

## Engineering

- [ ] TypeScript is used.
- [ ] No large monolithic components.
- [ ] Animation indexes are not exposed.
- [ ] Runtime logic is separated from UI.
- [ ] Configuration is centralized.
- [ ] Errors are handled.
- [ ] Tests exist.
- [ ] Documentation exists.
- [ ] Project can be started from a clean checkout.

---

# 42. Definition of Done

A developer should be able to:

```bash
git clone <repository>
cd avatar-news-presenter
npm install
npm run dev
```

Then open the application in a browser.

The application should display the presenter.

The developer should be able to:

1. See the presenter.
2. See the presenter breathing.
3. See the presenter blinking.
4. See subtle eye movement.
5. Trigger a gesture.
6. Trigger an expression.
7. Trigger head movement.
8. Play test audio.
9. See debug information.

No source-code modification should be required to demonstrate the Phase 1 functionality.

---

# 43. Implementation Order

Implement in this exact general order.

## Step 1 — Project Setup

Create:

- React
- TypeScript
- Vite
- ESLint
- Prettier
- Vitest

Verify:

```bash
npm run dev
```

works.

---

## Step 2 — Basic Three.js Scene

Create:

- Canvas
- Camera
- Lights
- Studio
- basic environment

Verify the scene renders.

---

## Step 3 — GLB Loader

Add:

```text
presenter.glb
```

Load it using React Three Fiber / Drei.

Verify:

- model loads
- model appears correctly
- scale is correct
- orientation is correct

---

## Step 4 — Avatar Component

Create:

```text
Avatar.tsx
```

Responsibilities:

- load model
- initialize runtime
- expose avatar controller
- handle cleanup

---

## Step 5 — Animation Registry

Create semantic animation mappings.

Do not use animation indexes.

---

## Step 6 — Animation Controller

Implement:

- play
- stop
- loop
- one-shot
- crossfade
- update
- cleanup

---

## Step 7 — Idle System

Implement:

- breathing
- blinking
- eye movement
- subtle head movement

---

## Step 8 — Facial Controller

Implement:

- expressions
- shape key control
- reset

---

## Step 9 — Gesture Controller

Implement:

- gesture playback
- blending
- return to idle

---

## Step 10 — Audio Controller

Implement:

- loading
- play
- pause
- stop
- current time
- duration

---

## Step 11 — Debug Panel

Add:

- animation buttons
- expression buttons
- head controls
- audio controls
- runtime information

---

## Step 12 — Performance Pass

Check:

- FPS
- memory
- texture sizes
- polygon count
- draw calls
- shadow performance

Optimize only where necessary.

---

## Step 13 — Tests

Implement unit tests for:

- registry
- controllers
- state machine
- animation plans
- configuration

---

## Step 14 — Documentation

Create:

```text
README.md
docs/architecture.md
docs/avatar-spec.md
docs/animation-system.md
docs/blender-pipeline.md
```

Document:

- setup
- architecture
- Blender workflow
- GLB export
- animation naming
- runtime API
- testing

---

# 44. Critical Engineering Rules

Follow these rules throughout the implementation.

## Rule 1

Do NOT create one giant React component.

Bad:

```text
Avatar.tsx
 ├── loading
 ├── animation
 ├── facial
 ├── audio
 ├── gestures
 ├── state
 ├── debug
 └── rendering
```

Instead use separate controllers/services.

---

## Rule 2

Treat GLB as the asset boundary.

```text
Blender
   ↓
GLB
   ↓
Web Application
```

The web application should not depend on `.blend` files.

---

## Rule 3

Never depend on numeric animation indexes.

Bad:

```ts
animations[7]
```

Good:

```ts
animationRegistry.gestures.emphasize
```

---

## Rule 4

Do not directly manipulate facial morph targets from UI components.

Bad:

```tsx
mesh.morphTargetInfluences[4] = 1;
```

Good:

```ts
facialController.setExpression("serious");
```

---

## Rule 5

Do not put per-frame state into React.

Animation updates belong in the runtime/render loop.

---

## Rule 6

Do not build the backend before the local avatar runtime works.

First:

```text
Browser
 ↓
GLB
 ↓
Avatar Runtime
 ↓
Animations
```

Then:

```text
Backend
 ↓
AI
 ↓
Animation Plan
 ↓
Avatar Runtime
```

---

## Rule 7

Do not implement LLM/TTS/ASR in Phase 1.

Build a stable avatar foundation first.

---

## Rule 8

The future LLM should output semantic behavior.

Example:

```json
{
  "emotion": "serious",
  "gesture": "emphasize",
  "headMotion": "nod"
}
```

Not:

```json
{
  "leftArmBoneRotation": 0.45,
  "rightArmBoneRotation": 0.32
}
```

---

## Rule 9

Use stable semantic identifiers.

Examples:

```text
openHand
emphasize
pointLeft
serious
positive
nod
camera
```

These should remain stable even if the underlying Blender implementation changes.

---

## Rule 10

Keep renderer implementation details inside the runtime.

Future code should be able to say:

```ts
avatar.playGesture("emphasize");
```

without knowing whether the avatar is implemented using:

- Three.js
- another renderer
- different animation clips
- different rigging
- different GLB structure

---

# 45. Runtime Flow

The initial runtime flow should look like this:

```text
Application starts
        ↓
React initializes
        ↓
AvatarScene initializes
        ↓
GLB loads
        ↓
Avatar Runtime initializes
        ↓
AnimationController initializes
        ↓
FacialController initializes
        ↓
IdleController initializes
        ↓
AudioController initializes
        ↓
Idle animation starts
        ↓
User clicks "Emphasize"
        ↓
AvatarController.playGesture("emphasize")
        ↓
AnimationController
        ↓
Crossfade to gesture
        ↓
Gesture plays
        ↓
Return to idle
```

---

# 46. Future Architecture Compatibility

The Phase 1 architecture should support these future phases.

## Phase 2 — Speech

```text
Script
 ↓
TTS
 ↓
Audio
 ↓
Lip Sync
 ↓
Avatar
```

---

## Phase 3 — Subtitles

```text
Speech
 ↓
Subtitle Timing
 ↓
Subtitle Renderer
 ↓
Browser
```

---

## Phase 4 — Backend

```text
React
 ↓
FastAPI
 ↓
Avatar API
```

---

## Phase 5 — AI

```text
News
 ↓
LLM
 ↓
Script
 ↓
Animation Plan
 ↓
Avatar Runtime
```

---

## Phase 6 — Real-Time

```text
Browser
    ↕
WebSocket
    ↕
Python
    ↓
LLM
    ↓
TTS
    ↓
Viseme Events
    ↓
Avatar Runtime
```

---

## Phase 7 — Video Generation

```text
News
 ↓
LLM
 ↓
Script
 ↓
TTS
 ↓
Animation Plan
 ↓
Blender
 ↓
MP4
 ↓
FFmpeg
 ↓
Final News Video
```

---

# 47. Multilingual Compatibility

The avatar should eventually support multiple languages without requiring different characters.

Conceptually:

```text
Same Avatar
     │
     ├── English Audio
     ├── Myanmar Audio
     ├── Chinese Audio
     ├── Japanese Audio
     └── Other Languages
```

Only the following should change:

- audio
- subtitles
- lip-sync timing
- language metadata

The underlying avatar should remain the same.

---

# 48. Web / iframe Compatibility

The final application is intended to be embeddable.

Future example:

```html
<iframe
  src="https://avatar.example.com/presenter/123"
  width="100%"
  height="600"
  allow="autoplay"
></iframe>
```

Phase 1 does not need production iframe infrastructure.

However, avoid architectural decisions that would prevent iframe embedding later.

---

# 49. Final Architecture

The long-term architecture should conceptually become:

```text
                         NEWS / USER
                              │
                              ▼
                         AI BACKEND
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
               LLM           TTS          ASR
                 │            │
                 ▼            ▼
          Animation Plan    Audio
                 │            │
                 └──────┬─────┘
                        ▼
                 Avatar Runtime
                        │
              ┌─────────┼─────────┐
              │         │         │
              ▼         ▼         ▼
          Animation   Facial     Audio
          Controller  Controller Controller
              │         │         │
              └─────────┼─────────┘
                        ▼
                    Three.js
                        │
                        ▼
                    GLB Avatar
                        │
                        ▼
                    Browser
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
          3D Presenter        Subtitles
```

---

# 50. Project Deliverables

Phase 1 must produce:

```text
React application
        +
Three.js / React Three Fiber scene
        +
Professional presenter GLB
        +
Blender source file
        +
Blender validation/export scripts
        +
Animation registry
        +
Animation controller
        +
Animation state machine
        +
Idle controller
        +
Facial controller
        +
Gesture controller
        +
Audio controller
        +
Debug panel
        +
Unit tests
        +
Documentation
```

---

# 51. Final Success Condition

Phase 1 is successful when the application can demonstrate:

```text
Browser
   ↓
3D Presenter
   ↓
Breathing
   ↓
Blinking
   ↓
Eye Movement
   ↓
Head Movement
   ↓
Facial Expression
   ↓
Hand Gesture
   ↓
Return to Idle
   ↓
Play Test Audio
```

while maintaining a clean architecture that allows future integration of:

```text
TTS
Lip Sync
Subtitles
Translation
Multilingual Speech
LLM
FastAPI
WebSocket
Database
Video Generation
Iframe Embedding
Real-Time AI Avatar
```

without requiring a complete rewrite of the avatar runtime.

---

# 52. Important Instruction for the AI Coding Agent

Implement this project incrementally.

Do NOT attempt to build every future feature.

Start with the Phase 1 MVP only.

Before implementing each major subsystem:

1. Inspect the existing project structure.
2. Identify the appropriate module.
3. Implement the smallest maintainable version.
4. Keep the public API semantic.
5. Add tests where appropriate.
6. Verify that existing functionality still works.
7. Document important architectural decisions.

Do not introduce unnecessary dependencies.

Do not over-engineer Phase 1.

The most important architectural principle is:

```text
Blender = 3D Asset + Animation Authoring

GLB = Asset Boundary

Three.js = Browser Renderer

Avatar Runtime = Animation Abstraction

React = Application/UI Layer

Future Python Backend = AI Orchestration

Future LLM = Semantic Animation Planner
```

The Phase 1 implementation should establish these boundaries clearly so that the project can evolve into a production-quality AI-powered 3D news presenter.