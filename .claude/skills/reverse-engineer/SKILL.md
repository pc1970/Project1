---
name: reverse-engineer
description: Reverse-engineer a website, web app, desktop app, or software product into clean, reproducible source code. Analyzes UI, structure, behavior, and technology stack from screenshots, URLs, descriptions, or binary artifacts, then reconstructs the equivalent implementation.
---

# Reverse Engineer

Reconstruct the source code of any website, web app, mobile app, or software product from visual inspection, screenshots, live URLs, or behavioral descriptions.

## What this skill does

Given any of these inputs:
- A URL to a live website or web app
- One or more screenshots or screen recordings
- A description of the UI, features, and behavior
- A compiled/minified artifact (JS bundle, APK, binary)
- A network traffic capture (HAR file, API logs)

…produce clean, modern, maintainable source code that faithfully reproduces the target's appearance and behavior.

## Process

### 1. Reconnaissance — identify the stack

**For websites / web apps:**
- Inspect page source: meta tags, script/link tags, generator comments
- Identify framework signals: `__NEXT_DATA__`, `ng-version`, `data-reactroot`, `__vue__`, Svelte comments
- Note CSS methodology: utility classes (Tailwind), BEM, CSS modules, styled-components
- Check `package.json` or bundler fingerprints if accessible
- Identify UI component library: MUI, shadcn/ui, Ant Design, Chakra, Bootstrap, etc.
- Map API calls: REST vs GraphQL, auth scheme, base URL patterns

**For mobile apps:**
- Identify framework: React Native (`__fbBatchedBridge`), Flutter (skia canvas), Expo, native Swift/Kotlin
- Note navigation pattern: stack, tab, drawer
- Observe network calls for API shape

**For desktop / compiled software:**
- Identify runtime: Electron (`chrome-devtools://`), Tauri, Qt, .NET WinForms/WPF, JavaFX
- Infer language from binary metadata or strings
- Map observable behavior to known patterns

### 2. Decompose the UI

Break the interface into a component tree:

```
App
├── Layout (header, sidebar, footer)
├── Page components (one per route/screen)
│   ├── Feature sections
│   │   ├── Atomic components (buttons, inputs, cards)
│   │   └── Composed components (forms, tables, modals)
└── Shared / design-system primitives
```

For each component, record:
- Visual appearance (dimensions, spacing, colors, typography)
- State variations (default, hover, active, disabled, loading, error)
- Props / inputs it accepts
- Events it emits

### 3. Extract the design system

| Token | Value |
|---|---|
| Primary color | e.g. `#6366F1` |
| Font family | e.g. `Inter, sans-serif` |
| Border radius | e.g. `8px` |
| Spacing scale | e.g. `4 / 8 / 16 / 24 / 32px` |
| Shadow | e.g. `0 1px 3px rgba(0,0,0,.12)` |

### 4. Map data & API contracts

For each visible data surface:
- Infer the JSON shape from rendered content
- Reconstruct endpoint paths and HTTP verbs
- Note pagination, filtering, and sorting patterns
- Identify auth flow (JWT in header, cookie session, OAuth redirect)

### 5. Generate the code

Produce a fully runnable project:

```
project/
├── src/
│   ├── components/       # atomic + composed UI
│   ├── pages/ (or app/)  # route-level components
│   ├── hooks/            # data-fetching, state logic
│   ├── lib/              # API client, utils
│   └── styles/           # tokens, global CSS
├── public/
├── package.json
└── README.md             # setup + run instructions
```

Default output stack (override if target stack is known):
- **Web**: Next.js 14 (App Router) + Tailwind CSS + shadcn/ui
- **Mobile**: React Native + Expo + NativeWind
- **Desktop**: Electron + React + Tailwind

If the target stack is identified, match it exactly.

### 6. Verify fidelity

After generating, compare against the original on:
- [ ] Layout and spacing (pixel-accurate to within ~4px)
- [ ] Color palette and typography
- [ ] Interactive states (hover, focus, active)
- [ ] Responsive breakpoints
- [ ] Navigation / routing flow
- [ ] Data loading and error states
- [ ] Animations and transitions

## Input prompts

Use one of these to invoke the skill:

**From a URL:**
> Reverse-engineer `https://example.com`. Identify the tech stack, decompose the UI into components, extract the design system, map the API calls, and produce a fully runnable Next.js + Tailwind clone with the same visual design and behavior.

**From a screenshot:**
> I'm attaching a screenshot of [app name]. Reconstruct the full source code for this screen. Identify the component hierarchy, infer the data model, and implement it in [target stack].

**From a description:**
> Build a clone of [product]. It has [feature list]. Replicate the UI and core functionality as closely as possible.

**Deep API reverse-engineering:**
> Analyze the network traffic from [app] and reconstruct the full API client: all endpoints, request/response shapes, authentication, and error handling.

## Constraints and ethics

- This skill reconstructs **interfaces and patterns**, not proprietary business logic or trade secrets.
- Do not reproduce verbatim copyrighted content (text, images, brand assets).
- API reverse-engineering is for **interoperability and integration** — not for bypassing authentication or rate limits.
- Identify and respect `robots.txt` and Terms of Service restrictions on scraping.
- Output is a clean reimplementation, not a copy of minified/obfuscated source.

## Output format

Always deliver:
1. **Stack identification** — what the target is built with
2. **Component tree** — annotated hierarchy
3. **Design tokens** — color, type, spacing extracted
4. **Source code** — complete, runnable files
5. **Setup instructions** — how to install and run the clone
6. **Gap report** — anything that couldn't be reconstructed and why
