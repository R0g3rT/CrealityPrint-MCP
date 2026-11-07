# Creality Print – MCP Mod

**Unofficial mod of Creality Print 7.3.1 with a built-in Remote API for MCP (Model Context Protocol).**
Let an AI assistant such as Claude work directly in your running slicer: load models, change settings and
profiles, slice, read the results and look at preview renders – every change is visible live in the GUI.

> **Not an official Creality release** and not affiliated with Creality. Maintained by [R0g3rT](https://github.com/R0g3rT). License: AGPL-3.0.
>
> 🇩🇪 **Deutsche Fassung:** [README.de.md](README.de.md)

**Current version:** `7.3.1.6378-mcp.2` (Creality Print 7.3.1.6378 + mod release 2) · Windows x64

---

## What you can do with it

Ask your assistant things like:

- *“Load `bracket.stl`, orient it for printing and slice it with 0.16 mm layers.”*
- *“Which feature takes the most print time, and is any speed limited by the max. volumetric flow?”*
- *“Show me the sliced preview from the top – where did the support go?”*
- *“Put the second part on its own plate and slice both plates.”*
- *“Check whether my profile is physically plausible before I save it.”*

### Features

| Area | What works |
|---|---|
| Status | Active printer / process / filament presets, modified settings, slice state |
| Settings | Read and change any setting live (atomic, invalid keys are rejected), per-object settings, variable layer height |
| Presets | List, select, save, rename, delete, read stored preset values |
| Models & plate | Load STL / OBJ / 3MF / STEP, list, move, rotate, scale, duplicate, delete, auto-arrange, auto-orient |
| Multiple plates | Add, select, delete plates, move objects between plates |
| Slicing | Slice and wait, cancel, warnings, G-code download |
| Analysis | Print time and filament per feature (walls, infill, …), flow peaks and averages |
| Images | PNG render of the plate before slicing and of the toolpath preview, 7 view angles |
| Send dialog | `set_config {"send_print_calibration": false}` presets the *bed calibration* checkbox of the Send dialog (`get_config` shows the current value) |
| Projects | Save, open, recent projects, new project, browse/move project files (delete/overwrite only with an extra switch) – needs orcaslicer-mcp newer than 0.1.19 (currently only from GitHub) |

---

## Installation

1. Download **`CrealityPrint_7.3.1.6378-mcp.2_Setup.exe`** from [Releases](https://github.com/R0g3rT/CrealityPrint-MCP/releases) and run it.
   Alternatively use the portable ZIP: unpack anywhere and start `CrealityPrint.exe`.
2. The mod installs to `Program Files\Creality Print MCP Mod` with its own start-menu entry and uninstaller.
   **An installed official Creality Print stays untouched** (separate folder, registry key and settings folder
   `%APPDATA%\Creality\Creality Print\7.3 Alpha`; no file associations are changed).

## Setup

### 1. Enable the Remote API

In Creality Print: **Preferences → General → section “Remote API”**

- Tick **Enable Remote API** and close the dialog (the server starts on `127.0.0.1:13130`).
- Copy the **API token** shown there.
- Leave **Allow LAN access** off unless another computer needs access.

### 2. Connect your MCP client

The MCP server is [orcaslicer-mcp](https://github.com/maxellis/orcaslicer-mcp) by Max Ellis – it works unchanged
with this mod. It needs [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`).

**Claude Desktop** – add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "creality_print": {
      "command": "uvx",
      "args": ["orcaslicer-mcp"],
      "env": { "ORCA_API_TOKEN": "<your token>" }
    }
  }
}
```

**Codex / other clients** – STDIO server, command `uvx`, argument `orcaslicer-mcp`,
environment variable `ORCA_API_TOKEN=<your token>`.

Restart the client, start Creality Print, then ask: *“Which printer and profile are active in Creality Print?”*

### Quick check without AI

```powershell
curl.exe -H "X-Api-Token: <your token>" http://127.0.0.1:13130/api/v1/status
```

Without the token the API answers `401 unauthorized`.

---

## Security

- The Remote API is **off by default** and only listens on `127.0.0.1`.
- Every request needs the token; regenerate it if it leaks.
- With **LAN access** enabled, any device on your network that knows the token can control the slicer.
- The API controls the **slicer** only – it never sends anything to your printer.

## Differences from official Creality Print

- **No self-update:** an official update would remove the Remote API. Check this repository for new mod releases.
- Version shows as `7.3.1.6378-mcp.N`; splash screen and *About* dialog mark the build as a mod.
- Log level and the *Allow deleting and replacing project files* switch (off by default) are in the *Remote API* section of the preferences.
- Full list of changes, origins and licenses: **[MOD_NOTICE.md](MOD_NOTICE.md)**

## Known limitations

- Windows x64 only (other platforms are not built or tested).
- *Duplicate object* places each copy next to the previous one (object width + 5 mm); use *arrange plate* if it runs off the bed.
- Filament slots: the `get_printer_slots` / `*_slot_mapping` tools only work for Elegoo CANVAS in orcaslicer-mcp and report `not supported` here. Choose CFS slots in Creality Print's *Send* dialog.
- The flow *prediction check* of orcaslicer-mcp is a rough estimate (speed × line width × layer height). Creality's actual flow can be higher, e.g. with Arachne variable line widths, gap fill or per-object overrides, so `anomaly` there is not necessarily a problem. The observed values (`observed_max_mm3_s`) come straight from the G-code and are reliable.
- Creality-specific features (Creality Cloud, CFS) are not exposed through the API.

---

## Credits & lineage

| Component | Source | License |
|---|---|---|
| Creality Print 7.3.1 (base) | [CrealityOfficial/CrealityPrint](https://github.com/CrealityOfficial/CrealityPrint) | AGPL-3.0 |
| Remote API | OrcaSlicer MCP build by Max Ellis – [maxellis/OrcaSlicer](https://github.com/maxellis/OrcaSlicer) | AGPL-3.0 |
| MCP server | [maxellis/orcaslicer-mcp](https://github.com/maxellis/orcaslicer-mcp) | AGPL-3.0 |

Creality Print itself is based on OrcaSlicer and Ultimaker CuraEngine; OrcaSlicer is based on Bambu Studio,
PrusaSlicer and SuperSlicer; PrusaSlicer originates from Slic3r by Alessandro Ranellucci and the RepRap community.
Creality's original README: [README.creality.md](README.creality.md).

## Building from source

Branch `mcp-mod` = Creality Print `v7.3.1` + mod commits. Windows build: Visual Studio 2022 Build Tools
(C++ workload, Windows SDK 10.0.22000), CMake 3.28/3.29 (not 4.x), Strawberry Perl, Git; then Creality's
`test_build.bat deps` and `test_build.bat slicer`. Installer: NSIS with `package/mod/installer_mod.nsi`.

## License

AGPL-3.0, same as Creality Print. Creality names and logos belong to Creality and are used only to identify the base
of this unofficial mod.
