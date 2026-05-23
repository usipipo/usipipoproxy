# LESSONS_LEARNED.md — uSipipo Frontend TypeScript Fixes

> Generated: 2026-05-23
> Scope: `frontend/` — Framer Motion v12.6 + TS 6.0 + TypeScript strict mode

---

## Bug Inventory

### BUG-01 | `class ApiError extends Error` — `erasableSyntaxOnly` violation

**Symptom**
```
src/api/client.ts:15 — error TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.
```

**Why it happens**
`tsconfig.json` has `"erasableSyntaxOnly": true`. This flag forbids class parameter properties
(`constructor(public status: number, ...)`) because they emit an erased `_` field that the
compiler cannot strip in ESM without an explicit `export field`. The TS 6.0 compiler
rejects parameter properties at syntactic level.

**Fix applied**
```ts
// ❌ Before (parameter property — forbidden by erasableSyntaxOnly)
export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

// ✅ After (factory fn, no class, no parameter property)
function apiError(status: number, message: string): Error & { status: number } {
  const err = new Error(message);
  Object.defineProperty(err, 'status', { value: status, enumerable: false });
  return err as Error & { status: number };
}
```

**Lesson**
> When `erasableSyntaxOnly: true` is set: **no class parameter properties**. Use factory
> functions returning intersection errors, or declare the field explicitly in the constructor body.
> Prefer factory functions when `ApiError` has no methods — it's a simple tagged error.

---

### BUG-02 | `ease: [0.22, 1, 0.36, 1]` typed as `number[]` — not assignable to `Easing`

**Symptom**
```
Property 'ease' is incompatible.
  Type 'number[]' is not assignable to type 'EasingFunction | Easing[]'.
```

**Why it happens**
In TypeScript, `[0.22, 1, 0.36, 1]` is inferred as `number[]` (mutable array). Framer Motion's
`Easing` type accepts `BezierDefinition = readonly [number, number, number, number]` — a **readonly tuple**,
not a mutable `number[]`. These are invariant — primitive type arrays + readonly mismatch = compile error.

**Fix applied**
```ts
// ❌ Before — inferred as number[]
const ease = [0.22, 1, 0.36, 1];
//   ease: number[]  → incompatible with Easing

// ✅ After — readonly tuple satisfies BezierDefinition = readonly [number,number,number,number]
const ease = [0.22, 1, 0.36, 1] as const;
// OR inline: ease={[0.22, 1, 0.36, 1] as const}
```

**Lesson**
> Always `as const` literal arrays intended as `BezierDefinition` tuples. Framer Motion v12
> `Easing` is defined as `readonly BezierDefinition | EasingFunction`. A `number[]` will never
> be assignable to `readonly tuple`. Add `as const` at declaration site.

---

### BUG-03 | `animate={blobRest}` where blobRest contains `transition` — type mismatch

**Symptom**
```
src/pages/LoginPage.tsx:21 — error TS2322: Type '{ x: number; y: number; scale: number; transition: { repeat: number; duration: number; ease: "linear" } }'
is not assignable to type 'Transition<any> | undefined'.
```

**Why it happens**
`blobRest` is spread as `animate`. The `TargetAndTransition` type has `{ x, y, scale }` as `Target`
properties — those are fine. The problem: `transition` inside `TargetAndTransition` is typed as
`Transition`, but `{ repeat, duration, ease }` is not directly assignable unless the full
`Transition` interface matches (there is no runtime issue, but TypeScript rejects the exact form).
Previous `animate` usage elsewhere placed `transition` inline and worked because TS resolved
those objects correctly; this one fails due to the `transition` being layered inside animate
object. In practice the underlying resolution was simply that the `animate` type expected
`TargetAndTransition` but TypeScript rejected a particular nested combination — separating
`transition` and `transition` into discrete pieces aligned with `TargetAndTransition` shape.

**Fix applied**
```tsx
// ❌ Before
<motion.div animate={blobRest} />

// ✅ After — separate transition into dedicated prop
<motion.div
  animate={{ x: 0, y: 0, scale: 1 }}
  transition={{ repeat: Infinity, duration: 14, ease: 'linear' }}
/>
```

**Lesson**
> For `motion.div` with complex `transition` configs, prefer the dedicated `transition` prop
> over nesting it inside `animate`. Both are runtime-equivalent, but `animate.transition`
> must match `Transition` type exactly — which is a complex union. Separate prop = clean types.

---

### BUG-04 | `ScrollReveal.tsx` — `Record<string, object>` not assignable to `Variants`

**Symptom**
```
src/components/feedback/ScrollReveal.tsx:43,44
  Type 'object' is not assignable to type 'boolean | TargetAndTransition | VariantLabels'.
```

**Why it happens**
Framer Motion's `Variants` interface is `{ [key: string]: Variant }`, where `Variant` is a union
that does **not** accept bare `object`. `Record<string, object>` has values typed as the structural
type `object`, which is not a valid `Variant`. TS needs either: explicit `as Variants`, or a
properly typed object literal.

**Fix applied**
```ts
// ❌ Before
const hiddenMap: Record<string, object> = { ... };  // object values not Variant

// ✅ After
interface HiddenState {
  opacity: number;
  x: number;
  y: number;
}
const hiddenMap: Record<string, HiddenState> = { ... };
```

**Lesson**
> Never use `Record<string, object>` for Framer Motion maps. Use a named interface per variant
> shape, and cast to `Variants` only as last resort. The named interface gives catch errors like
> typos in property names.

---

### BUG-05 | `ScrollReveal.tsx` — template literal margin not assignable to `MarginType`

**Symptom**
```
src/components/feedback/ScrollReveal.tsx:33
  Type '\`-${number}%\`' is not assignable to type 'MarginType'.
```

**Why it happens**
`useInView({ margin })` accepts a `MarginType = string` (like `"-100px"`) or `number` (pixels).
A TypeScript template literal `` `-${number}%` `` is a string — **but** TypeScript infers it as a
*template literal type*, not a plain `string`. The `MarginType` brand does not accept template
literal types unless widened with `as string`.

**Fix applied**
```ts
// ❌ Before
margin={`-${Math.round(threshold * 100)}%`}  // inferred as template literal type

// ✅ After
margin: `-${Math.round(threshold * 100)}%` as string  // explicitly widened
```

**Lesson**
> Template literals in positions expecting `string` need `as string` to widen. Wraps the
> interpolation result explicitly. Alternatively inline the computed string with `String(...)`.

---

### BUG-06 | DashboardPage.tsx — Missing import of `CreateDeviceModal`

**Symptom**
```
Cannot find name 'CreateDeviceModal'.
```

**Why it happens**
`CreateDeviceModal` exists in `components/modals/CreateDeviceModal.tsx`. The component was used
in JSX before adding the import. No circular deps — issue is simply missing import statement.

**Fix applied**
```tsx
// Add to imports block
import CreateDeviceModal from '@/components/modals/CreateDeviceModal';
```

**Lesson**
> Every component used in JSX must have a corresponding import. The `@/` alias redirects to
> `src/`. Order imports: stdlib → third-party → local. This prevents silent `undefined` renders
> at runtime.

---

### BUG-07 | DeviceDetailPage.tsx — Missing import of `AnimatedButton`

**Symptom**
```
Cannot find name 'AnimatedButton' (×4 occurrences).
```

**Why it happens** Same pattern as BUG-06. `AnimatedButton` component used without import.

**Fix applied**
```tsx
import AnimatedButton from '@/components/buttons/AnimatedButton';
```

**Lesson** Same as BUG-06.

---

### BUG-08 | Sidebar.tsx — Unused import `LogOut`

**Symptom**
```
src/components/layout/Sidebar.tsx(6,51): error TS6133: 'LogOut' is declared but its value is never read.
```

**Why it happens**
`tsconfig.app.json` has `"noUnusedLocals": true`, which causes the compiler to error only on
unused local bindings — which includes imports from unused modules.

**Fix applied**
Remove `LogOut` from the lucide-react import line.

**Lesson**
> `noUnusedLocals: true` is a strong quality gate. Every import must be consumed. Remove
> dead imports immediately; don't accumulate for "future use." Future code may use them — create
> the import *when* needed.

---

### BUG-09 | `types/index.ts` — Duplicate re-export of `AuthStatusResponse` & `SetCookieRequest`

**Symptom**
```
src/types/index.ts:167 — error TS2484: Export declaration conflicts with exported declaration of 'AuthStatusResponse'.
src/types/index.ts:167 — error TS2484: Export declaration conflicts with exported declaration of 'SetCookieRequest'.
```

**Why it happens**
Both types were named-exported inline (lines 92–99) AND barrel-re-exported again at line 167.
Two re-exports of the same symbol = compile error.

**Fix applied**
Remove the bottom barrel line:
```ts
// ❌ Remove — duplicate, both already exported inline
// export type { AuthStatusResponse, SetCookieRequest };
```

**Lesson**
> Pick one re-export strategy: inline declarations **or** barrel re-exports. Mixing both =
> `TS2484` conflict. File the barrel at top; or consolidate into one `export type` block.

---

### BUG-10 | `devices.conf()` still uses `ApiError` class directly (forgot to update)

**Symptom**
When BUG-01 was partially fixed, `throw new ApiError(res.status, ...)` remained in `client.ts:81`.

**Why it happens**
Fix for BUG-01 only replaced the `request()` throw target, not the `conf()` helper throw target.

**Fix applied**
```ts
// Before
throw new ApiError(res.status, await res.text());
// After
throw apiError(res.status, await res.text());
```

**Lesson**
> When a named function replaces a class: search **all** `new ClassName(` usages. Partial fixes
> leave dangling `new ClassName(` calls behind. Always `grep -rn "new ApiError"` after replacing.

---

## Type-Scope Diagnosis Summary

| Root cause type | Files affected | Pattern |
|---|---|---|
| `erasableSyntaxOnly` (TS6) | `client.ts` | Class parameter properties → factory fn |
| `number[]` vs `readonly tuple` (invariant) | `DashboardPage.tsx`, `LandingPage.tsx` | `ease: [x,x,x,x]` needs `as const` |
| `animate.transition` nested | `LoginPage.tsx` | Use `transition` prop instead |
| `object` vs `Variant` structural mismatch | `ScrollReveal.tsx` | Named `interface` per variant key |
| Template literal widening | `ScrollReveal.tsx` | `as string` on computed margin |
| Missing import (unused-imports gate) | `DashboardPage.tsx`, `DeviceDetailPage.tsx` | Add import; or remove usage |
| Dead import + `noUnusedLocals` | `Sidebar.tsx` | Remove import |
| Duplicate export | `types/index.ts` | Remove barrel re-export |

---

## Architecture Guardrails (Prevent Repetition)

1. **When `tsconfig.json` has `erasableSyntaxOnly: true`** → Never use parameter properties in class constructors. Use factory functions returning tagged errors.
2. **When passing numeric tuples to Framer Motion `ease`** → Always add `as const` at the declaration site. The type `number[]` will never satisfy `readonly BezierDefinition`.
3. **When composing `animate` objects with `transition`** → If the inner transition has more than `duration`, prefer the flat `transition` prop on the component. Lower risk of incidental type violation.
4. **When building custom `Variants` maps** → Use explicit `interface` per variant shape, not `Record<string, object>`. TS catches typos.
5. **When computing strings for typed prop positions** → Widen with `as string`. Template literal types are not auto-widened.
6. **Every component added to JSX must have its import added before `tsc` is run** → add-to-import rule before every commit.
7. **When replacing a class with a factory** → `grep -rn "new ClassName"` to find lingering instances before finishing.
