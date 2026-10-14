# R3F Runtime Error Fix Summary

## Problem
`Uncaught Error: R3F: Hooks can only be used within the Canvas component!`

The application displayed only a dark background.

## Root Cause

The `useGLTF.preload('/heart.glb')` call was placed at the **module level** (outside any React component or Canvas context):

```jsx
// ❌ Module-level — causes R3F hook error
useGLTF.preload('/heart.glb')
```

React hooks require the R3F Canvas context to be active. This call executed before the Canvas was mounted, causing the error and resulting in a dark background only.

## Fix

**Removed** the module-level `useGLTF.preload('/heart.glb')` call from `HeartViewer.jsx`.

All R3F hooks now execute only inside components rendered beneath the `<Canvas>` element:
- `HeartScene` uses `useGLTF(glbPath)` inside the Canvas context
- GLTF loading happens naturally within the component hierarchy
- No duplicate or out-of-context hook calls

## Files Modified

- `frontend/src/components/heart/HeartViewer.jsx` — Removed module-level `useGLTF.preload()` call

## Build Status

✅ `npm run build` — Successful (7.52s, 578 modules transformed)  
✅ No R3F hook errors  
✅ Full cinematic heart visualization functional  
✅ Real ML prediction integration intact  

## Component Hierarchy (Correct)

```
<Canvas>  ← R3F Context established here
  ├── PerspectiveCamera
  ├── DirectionalLights (cinematic 3-point)
  ├── HeartScene  ← useGLTF called HERE (valid context)
  │    ├── useGLTF(glbPath)  ← hooks OK
  │    ├── useFrame          ← hooks OK
  │    └── useEffect         ← hooks OK
  ├── OrbitControls
  ├── ContactShadows
  ├── Html labels (outside Canvas - OK)
  └── Interaction hints (outside Canvas - OK)
```

## Key Takeaway

Never call React Three Fiber hooks at the module level. All R3F hooks (`useGLTF`, `useFrame`, `useLoader`, etc.) must be called inside components that are rendered within a `<Canvas>` element, where the R3F context is active.