# Credential Portal — Optional .NET Web UI

This directory is the placeholder for an optional ASP.NET Core Razor Pages web interface
that provides a browser-based form for triggering credential distributions.

## Planned Features
- Web form: recipient name, email, system name, credential
- Calls the Python mailer as a subprocess or via a thin REST wrapper
- Displays audit log table
- Role-based access (IT Ops only)

## Integration
The Python backend can expose a REST endpoint by wrapping `core/splitter.py`
with FastAPI (see the incident-notification-bot project for a reference pattern).
The .NET Razor Pages frontend then calls that API.

## Status
Not yet implemented — Python CLI is the primary interface.
