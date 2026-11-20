# Troubleshooting

Use the observed failure and installed package versions to select one diagnostic path.

## Stale results / changes not picked up
**Symptoms**: edits to source don't trigger regeneration, or generated file has outdated content.
**Fix order**:
1. Check `generate_for`, target activation, builder triggers, and the expected input extension.
2. Run a normal rebuild with verbose diagnostics.
3. Restart watch mode after configuration changes when the installed version requires it.
4. Use `dart run build_runner clean` only when evidence points to stale build state, then rebuild.

## Conflicting outputs error
**Message**: "Found X declared outputs which already exist on disk..."
**Fix**: Identify which tool owns each conflicting file. Pass `--delete-conflicting-outputs` only for known generated output that the current builder is expected to replace; otherwise stop and preserve the file.

## "part 'foo.g.dart'; is missing"
**Cause**: user forgot to add `part 'file.g.dart';` to source.
**Prevention**: In your generator, detect the missing part and throw a clear `InvalidGenerationSource` pointing at the library element.

## Analyzer version conflict
**Message**: `version solving failed … analyzer ^11.0.0 required by build_runner …`.
**Fix**:
1. Inspect the solver explanation and the constraints declared by each generator package.
2. Check current changelogs and published compatible versions.
3. Upgrade the smallest compatible set of generator dependencies.
4. Loosen a direct analyzer constraint only when the package does not require that narrower range.

## Cycle detected
**Message**: "Cycle in build phase graph".
**Cause**: `required_inputs` / `runs_before` chain loops back.
**Fix**: Draw the phase graph. A builder cannot (directly or transitively) depend on its own output.

## Generator runs on every file → slow builds
**Fix**: Scope `generate_for` in root package's build.yaml:
```yaml
targets:
  $default:
    builders:
      my_pkg|my_gen:
        generate_for: [lib/models/**]
```
Also consider `build_runner build --build-filter="lib/specific/*.dart"` for targeted rebuilds.

## `dart:mirrors` error during AOT
**Cause**: The selected build mode cannot compile reflection-dependent builder code.
**Fix**: Verify the installed build runner's execution mode and supported flags. Prefer analyzer/resolver APIs over `dart:mirrors`; use a JIT fallback only when the current tool documents one and the project accepts it.

## Resolver returns null or incomplete type
**Cause**: Primary input doesn't transitively import the type you're resolving.
**Fix**: `final isLib = await step.resolver.isLibrary(id);` first. If you need a file not in the import graph, use `readAsString` and parse manually — the resolver won't see it.

## InvalidGenerationSource vs InvalidGenerationSourceError
Use current `InvalidGenerationSource` for invalid user source. Pass `element:` when a resolved declaration is responsible, and `node:` when an AST node provides a more precise location. Build configuration or internal generator failures that do not correspond to user source need a different diagnostic rather than a fabricated element.

## findAssets returns nothing
- It only scans the **current package**. Use `auto_apply: dependents` + cache intermediates + root-package aggregator for cross-package work.
- Your Glob pattern may not match — test with a simple `Glob('lib/**/*.dart')` first.
- You may be using a synthetic input when you shouldn't; `$lib$` runs once, while a regular extension runs per-file.

## Generated file not visible to tests
Use `dart run build_runner test` instead of plain `dart test`. It exposes the cache to the test runner.

## Watch mode rebuild storms
Barrel files cause cascades — changing one export invalidates everything importing the barrel. Use direct imports in annotated files.

## Published package: users can't build
**Cause**: Published library source references generated files that were not included, or the package's consumer-generation contract is incomplete.
**Fix**: Include generated files that the published library imports or declares as parts. If generation is intentionally performed in the consuming package, publish the annotations, builder registration, and setup required for that workflow instead.

## Private imports / access issues
- `SharedPartBuilder` / `PartBuilder` outputs can access private members of the including library (same library scope).
- `LibraryBuilder` outputs are standalone libraries and CANNOT see private members. If you need private access, choose a part-based builder.
- Part files cannot declare their own imports — all imports go in the user's source file, which is a limitation.
