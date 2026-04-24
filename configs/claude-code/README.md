# Claude Code configs — Djinn

Optional per-user Claude Code settings snippets for Djinn. These are suggestions, not requirements — the plugin works without any settings changes.

## `settings.json` patterns

### Allow-list the sub-plugin Bash commands

If you install `djinn` and want to skip the permission prompt for its known-safe Bash commands, add them to your user or project `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 *)",
      "Bash(jq *)"
    ]
  }
}
```

### Hook integration

Djinn sub-plugins install their own hooks via `/plugin install`. You do not need to copy hook definitions into your user settings — the plugin manifests handle registration.

## Status line (optional)

If you use Claude Code's status line, Djinn surfaces per-sub-plugin state at `plugins/<name>/state/` that you can read via `statusLine.command`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash -c 'cat plugins/intent-anchor/state/status 2>/dev/null || echo Djinn'"
  }
}
```

## Reference

See Claude Code documentation for full `settings.json` schema. Every Djinn snippet here is optional; the plugin is fully functional with default settings.
