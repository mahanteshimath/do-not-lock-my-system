# Security Policy

## Supported versions

The latest release on the `main` branch is supported. Please upgrade to the
newest version before reporting an issue.

| Version | Supported |
| ------- | --------- |
| latest  | ✅        |
| older   | ❌        |

## Reporting a vulnerability

**Please do not open public GitHub issues for security problems.**

Report vulnerabilities privately via GitHub's
[**Report a vulnerability**](https://github.com/mahanteshimath/do-not-lock-my-system/security/advisories/new)
workflow (repository **Security → Advisories → Report a vulnerability**).

Include, where possible:

- A description of the issue and its impact
- Steps to reproduce (a minimal proof of concept)
- The OS, Python version, and app version affected

You can expect an initial acknowledgment within a few days. Once a fix is ready,
a new release will be published and the advisory disclosed.

## Scope & threat model

Don't Lock My PC is a **local desktop utility**:

- It runs with the invoking user's privileges and makes **no network calls**.
- Keep-awake uses OS-native APIs (`SetThreadExecutionState` / `caffeinate`) plus
  a ±1px mouse move and an invisible **F15** keypress.
- The optional **lid-close** and **scheduled power** features change local OS
  power settings (Windows `powercfg` lid action, `SetSuspendState`, `shutdown`;
  macOS `pmset` / `osascript`) and restore the lid setting on **STOP**/exit.

Relevant concerns include unexpected privilege use, unsafe handling of the
power-plan override, or any path that could cause data loss on the scheduled
shutdown. Reports in these areas are especially appreciated.
