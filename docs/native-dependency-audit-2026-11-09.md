# Native dependency repair candidate

Baseline: official cmux v0.65.2.2, commit `12023d89feb5425c766ba05e8d8e4cfc176e3991`.
The installed application reports the same commit. This candidate is compared
against that commit on a separate branch in the user's fork; it does not update
the fork's default branch or replace the installed application.

| Lock | Dependency | Before | Candidate |
| --- | --- | --- | --- |
| CommandPaletteNucleoFFI | crossbeam-epoch | 0.9.18 | 0.9.20 |
| DiffSidecar | rustls | 0.23.41 | 0.23.46 |
| DiffSidecar | rustls-webpki | 0.103.13 | 0.103.16 |
| DiffSidecar | tokio | 1.52.3 | 1.53.3 |
| DiffSidecar | webpki-root-certs | 1.0.8 | 1.0.10 |

The resolver also normalizes several existing windows-sys dependency edges;
it adds no package/version outside the five upgrades above. Cargo 1.88.0
accepted the resulting locks with `--locked` in the checks below.

On 2026-11-09, OSV querybatch reported zero findings across the two candidate
locks (215 unique registry package/version pairs; 20 in Nucleo and 198 in
DiffSidecar, with overlap). The baseline had one and four flagged packages.
Advisory aliases are not counted as separate affected packages. This scan does
not cover cmux-tui, Swift packages, Ghostty, or the whole app.

DiffSidecar ships with no default Cargo features. Its TLS dependencies are
optional `http-server` development dependencies, so a lock finding is not proof
of production reachability. The upgrade retains both feature configurations.

## Executed verification

HAL9000 macOS arm64, isolated Rust/Cargo 1.88.0:

```sh
cargo +1.88.0 test --manifest-path Native/DiffSidecar/Cargo.toml --all-targets --locked --no-default-features
cargo +1.88.0 test --manifest-path Native/DiffSidecar/Cargo.toml --all-targets --all-features --locked
cargo +1.88.0 build --manifest-path Native/CommandPaletteNucleoFFI/Cargo.toml --release --locked
python3 Native/CommandPaletteNucleoFFI/tests/ffi_smoke.py "$PWD/Native/CommandPaletteNucleoFFI/target/release/libcmux_command_palette_nucleo_ffi.dylib"
CMUX_DIFF_SIDECAR_ARCHS=arm64 ./scripts/build-diff-sidecar.sh
```

Default-feature tests: 12 passed. All-feature tests: 15 unit and 7 integration
passed. Search FFI: 5 passed against the built dynamic library, covering ASCII
and Japanese queries, result limits, repeat queries, and invalid UTF-8. These
are compatibility checks, not a behavioral reproduction of the upstream
dependency vulnerabilities; the before/after advisory scan establishes the
dependency repair. No fabricated failing source-text test was added.

The existing artifact verifier accepted the 654,992-byte arm64 sidecar,
macOS minimum 14.0, system dynamic dependencies, stripped symbols and the real
handshake with stdio/WebKit and no HTTP/WebSocket capability. The local signing
check is not a Developer ID release or notarization receipt.

The verification selector was inspected with `verify-local.py --affected
12023d89feb5425c766ba05e8d8e4cfc176e3991 --list`. The full app static recipe,
Swift app/test compilation, x86_64 build, app-host search benchmarks and physical
dogfood were not run in this scoped checkout. No installed app was launched,
stopped or replaced. No release was signed or published.

Existing upstream PRs #15501 and #18652 cover parts of this dependency family,
but the inspected revisions stop below the rustls/webpki fixes required today.
This candidate regenerates its locks from the official baseline; it does not
modify those contributors' branches or notify upstream. See IAM-1267/IAM-1259.
