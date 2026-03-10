Disable Error Reporting
=======================

Controls whether the application sends anonymous crash reports
and error telemetry to help improve the software.

## Behavior

- **OFF (default):** Error reports are sent via Sentry when
  unhandled exceptions occur. No personal data is included —
  only stack traces and device type.
- **ON:** All error reporting is disabled. No data is sent.

## What Is Collected

When enabled, error reporting includes:
- Exception type and stack trace
- Application version
- Platform (Raspberry Pi model, OS version)

It does NOT include:
- Network credentials or passwords
- Position data or machine configurations
- Any personally identifiable information

## Notes

- Enabling error reporting helps the developer fix bugs faster
- If you are in an air-gapped or secure environment, disable this