# TUI dependency and startup-repair candidates

Baseline: official v0.65.2.2 / `12023d89feb5425c766ba05e8d8e4cfc176e3991`.
These are candidate branches in the owner's fork. No installed application,
daemon, Cloud machine, real journal or registry has been changed.

## Dependency candidate

Commit `382106e5e1bdb4466c7f5296b39a14a13719ab70` updates:

- ctutils 0.4.2 to 0.4.4, h2 0.4.15 to 0.4.16,
  hickory-resolver 0.26.1 to 0.26.2;
- rustls 0.23.43 to 0.23.46, rustls-webpki 0.103.13 to 0.103.16,
  tokio 1.53.1 to 1.53.3;
- webpki-root-certs and webpki-roots 1.0.9 to 1.0.10;
- rusqlite 0.39.0 to 0.41.0, resolving libsqlite3-sys 0.39.1 instead of 0.37.0.

The SQLite wrapper constraint changes; the other fixes stay within their
existing compatible ranges. The new rusqlite declares Rust 1.89 support,
below the workspace's advertised 1.91 minimum. Verification used the pinned
1.95.0 toolchain; an actual 1.91 build was not performed.

On 2026-11-09, OSV querybatch checked all 606 unique registry versions in the
candidate lock. The nine packages with vulnerability findings are resolved.
`paste` 1.0.15 still has RUSTSEC-2024-0436, an unmaintained notice. It is
reported, not excluded. This is not a whole-app safety assessment.

## Existing startup repair defect

The original baseline and dependency-only commit both fail
`workspace_registry::tests::startup_repairs_legacy_terminal_close_dangling_resource_rows`
when reopening the synthetic legacy registry: a tab still references a closed
terminal. Dependency-only registry results were 126 passed, 1 failed and
1 ignored manual throughput probe. The baseline comparison selected the one
failing test and reproduced the same failure with the original SQLite version.

The separate repair branch adds explicit tab/active-tab expectations in
`9da263f1`, then fixes the shared mutation path in `4466f768`. Startup repair
and ordinary terminal close now use the same tab tombstone helper. Startup
does not invoke the rest of ordinary host close: host lifecycle and processes
are unchanged. Existing integrity validation, schema version, revision increment
and journal repair event remain in place.

## Executed evidence

HAL9000 macOS arm64, isolated Rust 1.95.0, Zig 0.16.0 and the unchanged
Ghostty submodule `cb1ef7091cdef0b581ee2cbd83742b653253523e`:

```sh
cd cmux-tui
cargo test -p cmux-tui-core workspace_registry::tests:: --lib --locked -- --test-threads=1
cargo test -p cmux-tui-core journal_ingress::tests:: --lib --locked -- --test-threads=1
cargo test -p cmux-wg --locked
```

At repair source `4466f768`: registry 127 passed / 1 ignored manual probe;
journal ingress 34 passed / 1 ignored manual probe; WireGuard 9 unit + 6
loopback integration tests passed. All inputs were synthetic/in-memory or
temporary; the tunnel uses loopback peers without a system interface or root.

Initial tool-PATH and sparse-fixture setup failures ran no tests and are not
behavioral regression evidence. Full hosted Linux/macOS/Windows verification,
the remaining core suites, a full app build, remote TLS/DNS runtime paths,
physical dogfood and binary rollback after opening real data are unverified.
Outside contributors cannot dispatch the upstream hosted merge gate; a
maintainer must run it before adoption. This document is not merge or deployment
authority. See IAM-1268 and IAM-1269; the independent Native candidate is IAM-1267.
