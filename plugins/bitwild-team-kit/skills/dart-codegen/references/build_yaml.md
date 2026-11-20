# `build.yaml` Configuration

Use the `build_config` version resolved by the target repository as the schema authority. The package's README and parser source are more reliable than a copied configuration from another generator.

## Exposed builders

A builder definition normally includes:

```yaml
builders:
  my_builder:
    import: "package:my_generator/builder.dart"
    builder_factories: ["myBuilder"]
    build_extensions: {".dart": [".my_builder.g.part"]}
    auto_apply: dependents
    build_to: cache
    applies_builders: ["source_gen|combining_builder"]
```

`import`, `builder_factories`, and `build_extensions` are the core required fields. The declared extensions must agree with the merged `Builder.buildExtensions` returned by the factories.

Select optional fields from the actual build contract:

- `auto_apply`: `none`, `dependents`, `all_packages`, or `root_package`;
- `build_to`: `cache` for hidden intermediates or `source` for visible output;
- `applies_builders`: activates companion builders on the same target;
- `required_inputs`: orders this builder after builders that can produce the listed extensions;
- `runs_before`: orders named builders later without activating them;
- `is_optional`: permits lazy execution when a downstream output requests it;
- `defaults`: provides `generate_for`, ordinary options, and mode-specific options.

Builders configured with `build_to: source` run only on the root package. Do not select `root_package` or source output by habit; choose them when the output belongs in the root source tree.

## Target overrides

Consumers enable, scope, or configure builders under a target:

```yaml
targets:
  $default:
    builders:
      my_generator|my_builder:
        enabled: true
        generate_for:
          include: ["lib/models/**.dart"]
        options:
          strict: true
```

Keep target configuration in the consuming package when it is consumer policy. Keep portable defaults with the builder definition.

## Ordering

Use `required_inputs` and `runs_before` only when one builder genuinely needs another builder's output. They add dependency-graph edges and can create cycles.

`runs_before` changes order but does not activate the named builder. Pair it with `applies_builders` only when the companion must also be enabled.

## Post-process builders

Post-process builders use `post_process_builders`, a single `builder_factory`, and `input_extensions`. Their available fields depend on `build_config`; current releases support `build_to: cache` and `build_to: source`, while older releases did not expose the same choice. Check the resolved package before adding it.

Post-process builders run after ordinary builders and are appropriate for operations on completed assets. They are not a substitute for a multi-phase semantic generator.

## Triggers and newer fields

Recent `build_config` releases support builder triggers and `run_only_if_triggered` as a performance optimization. Add them only when the target dependency versions support them and the trigger can conservatively identify every relevant input.

## Verification

- Parse the configuration with the repository's resolved `build_config`/`build_runner` versions.
- Confirm every possible write is declared.
- Run a focused fixture that exercises activation and ordering, not only YAML parsing.
- Inspect generated asset locations in both development and release modes when mode-specific options differ.
