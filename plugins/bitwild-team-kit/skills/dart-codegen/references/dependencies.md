# Generated Dependencies and Phase Ordering

Use this reference when one builder consumes generated assets or aggregates several inputs. Map assets before adding ordering configuration.

## Phase edges

The build system orders builders through declared inputs and configuration such as `required_inputs`, `runs_before`, and `applies_builders`.

- `required_inputs` places a builder after builders that can emit the listed extensions.
- `runs_before` places named builders later but does not activate them.
- `applies_builders` activates companion builders and does not by itself prove that their output is an input.

Use the smallest edge that represents the actual dependency. The resulting graph must remain acyclic.

## Reading generated assets

Before reading an asset:

1. Confirm another completed phase declares it as output.
2. Construct its `AssetId` from the primary input or an explicit contract.
3. Use `canRead` when absence is valid; use a located diagnostic when the input is required.
4. Test the ordering with the same builder versions used by consumers.

Resolver access also depends on library reachability. `libraryFor` is not a general filesystem parser; an asset that is not a valid reachable Dart library may need to be read as text or represented by a different intermediate format.

## Aggregation inside one package

A common package-local design uses:

- a per-input builder that emits compact cache intermediates; and
- one builder on a synthetic package input such as `$lib$` that discovers those intermediates with `findAssets` and writes the aggregate output.

Choose this only when aggregation is required. A declared root library that explicitly references the relevant types can be simpler and easier to understand.

## Package boundary

`BuildStep.findAssets` searches readable assets under the **current package**. A root-package builder does not automatically glob generated assets belonging to dependency packages.

For cross-package discovery, define an explicit contract, for example:

- a package-level generated manifest or registry that consumers import;
- user-declared root types that the analyzer can traverse through imports;
- configuration listing participating packages or assets; or
- a repository-specific orchestration step outside a single builder.

Do not claim that `auto_apply: dependents` plus a root `findAssets` call automatically creates cross-package aggregation. Prove the selected design in a multi-package fixture.

## Failure checks

- A builder cannot read output written later in the same phase.
- A build step may write only assets allowed by its `buildExtensions`.
- `runs_before` does not enable a disabled builder.
- An aggregator should execute once per intended scope, not once per ordinary source input.
- Deleting or overwriting a visible asset requires confidence that it is generated output owned by this builder.
