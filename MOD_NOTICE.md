# Creality Print – MCP Mod (inoffiziell)

**Version:** `7.3.1.0-mcp.1` = Creality Print 7.3.1.0 + Mod-Stand 1
**Gepflegt von:** R0g3rT
**Lizenz:** AGPL-3.0 (wie Creality Print und OrcaSlicer)

Dies ist **keine offizielle Version von Creality**. Die Mod ergänzt Creality Print um eine
lokale Remote API, über die KI-Assistenten (z. B. Claude) per MCP (Model Context Protocol)
das laufende Programm steuern können: Modelle laden, Profile und Einstellungen ändern,
slicen, Ergebnisse auswerten und Vorschaubilder abrufen.

## Versionsschema

`<Creality-Version>-mcp.<Mod-Nummer>`, z. B. `7.3.1.0-mcp.1`.
Die Mod-Nummer steigt bei jeder neuen Mod-Version (`CREALITYPRINT_MOD_NUMBER` in
`src/slic3r/GUI/RemoteAPI/ModVersion.hpp`; Programm und Installer lesen sie von dort). Intern rechnet Creality weiter mit `7.3.1.0`.

## Worauf die Mod aufbaut

| Baustein | Herkunft | Lizenz |
|---|---|---|
| Creality Print 7.3.1 (Basis) | Creality – github.com/CrealityOfficial/CrealityPrint | AGPL-3.0 |
| Remote API (HTTP/WebSocket im Programm) | OrcaSlicer-MCP-Build von Max Ellis – github.com/maxellis/OrcaSlicer (Branch `remote-api-242`) | AGPL-3.0 |
| MCP-Server (separates Programm) | orcaslicer-mcp von Max Ellis – github.com/maxellis/orcaslicer-mcp | AGPL-3.0 |

Herkunftskette von Creality Print selbst (laut Creality):

- Creality Print ist entwickelt auf Basis von **OrcaSlicer** und **Ultimaker CuraEngine**
- OrcaSlicer basiert auf **Bambu Studio**, **PrusaSlicer** und **SuperSlicer**
- Bambu Studio basiert auf **PrusaSlicer** (Prusa Research) und **SuperSlicer** (Merill)
- PrusaSlicer wurde ursprünglich auf Basis von **Slic3r** (Alessandro Ranellucci und RepRap-Gemeinschaft) entwickelt

## Änderungen gegenüber Creality Print 7.3.1

- Remote API (`src/slic3r/GUI/RemoteAPI/`): Port, Token-Pflicht, standardmäßig aus, nur 127.0.0.1 (LAN optional)
- Creality-Anpassungen: Kamera-Blickwinkel, G-Code-Renderer, Preset-Auswahl, Zeit pro Druckbereich aus `roles_times`, Statusmeldung beim Laden der Vorschau
- Einstellungen → Allgemein: Abschnitt „Remote API“ (Ein/Aus, LAN, Token, Protokollstufe)
- Selbst-Update deaktiviert (ein offizielles Update würde die Remote API entfernen)
- Fix: fehlende `resources/printers/version.txt` im öffentlichen Quellcode führte zum Absturz beim Start
- Kennzeichnung als Mod: Versionsnummer, „Über“-Dialog, Startbild (Eckband „MCP MOD“, Plakette „by R0g3rT“; erzeugt mit `tools/mod/make_splash.py` aus Crealitys Original-Startbild)

Marken, Logos und Namen von Creality gehören Creality. Ihre Verwendung hier dient nur der
Kennzeichnung der Basis dieser inoffiziellen Mod.
