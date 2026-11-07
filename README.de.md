# Creality Print – MCP Mod

**Inoffizielle Mod von Creality Print 7.3.1 mit eingebauter Remote API für MCP (Model Context Protocol).**
Ein KI-Assistent wie Claude arbeitet damit direkt im laufenden Slicer: Modelle laden, Einstellungen und Profile
ändern, slicen, Ergebnisse auswerten und Vorschaubilder ansehen – jede Änderung ist sofort in der Oberfläche sichtbar.

> **Keine offizielle Version von Creality** und nicht mit Creality verbunden. Gepflegt von [R0g3rT](https://github.com/R0g3rT). Lizenz: AGPL-3.0.
>
> 🇬🇧 **English version:** [README.md](README.md)

**Aktuelle Version:** `7.3.1.6378-mcp.2` (Creality Print 7.3.1.6378 + Mod-Stand 2) · Windows x64

---

## Was damit geht

Frag deinen Assistenten zum Beispiel:

- *„Lade `halter.stl`, richte ihn zum Drucken aus und slice mit 0,16 mm Schichthöhe.“*
- *„Welcher Bereich kostet die meiste Druckzeit, und wird irgendwo durch den maximalen Fluss gebremst?“*
- *„Zeig mir die Vorschau von oben – wo ist der Support gelandet?“*
- *„Leg das zweite Teil auf eine eigene Platte und slice beide Platten.“*
- *„Prüf, ob mein Profil physikalisch plausibel ist, bevor ich es speichere.“*

### Funktionen

| Bereich | Was funktioniert |
|---|---|
| Status | Aktive Drucker-, Prozess- und Filamentprofile, geänderte Einstellungen, Slice-Zustand |
| Einstellungen | Jede Einstellung live lesen und ändern (atomar, ungültige Schlüssel werden abgelehnt), Einstellungen pro Objekt, variable Schichthöhe |
| Profile | Auflisten, auswählen, speichern, umbenennen, löschen, gespeicherte Werte lesen |
| Modelle & Platte | STL / OBJ / 3MF / STEP laden, auflisten, verschieben, drehen, skalieren, duplizieren, löschen, automatisch anordnen und ausrichten |
| Mehrere Platten | Platten anlegen, auswählen, löschen, Objekte zwischen Platten verschieben |
| Slicen | Slicen mit Warten, abbrechen, Warnungen, G-Code abrufen |
| Auswertung | Druckzeit und Filament je Bereich (Wände, Füllung, …), Spitzen- und Durchschnittsfluss |
| Bilder | PNG der Platte vor dem Slicen und der Werkzeugwege-Vorschau, 7 Blickwinkel |
| Senden-Dialog | `set_config {"send_print_calibration": false}` stellt die Checkbox *Druckbettkalibrierung* im Senden-Dialog vor (`get_config` zeigt den aktuellen Wert) |
| Projekte | Speichern, öffnen, zuletzt verwendete, neues Projekt, Projektdateien durchsuchen/verschieben (Löschen/Überschreiben nur mit zusätzlichem Schalter) – braucht orcaslicer-mcp neuer als 0.1.19 (derzeit nur von GitHub) |

---

## Installation

1. **`CrealityPrint_7.3.1.6378-mcp.2_Setup.exe`** unter [Releases](https://github.com/R0g3rT/CrealityPrint-MCP/releases) herunterladen und ausführen.
   Alternativ die portable ZIP: irgendwohin entpacken und `CrealityPrint.exe` starten.
2. Die Mod wird nach `Programme\Creality Print MCP Mod` installiert, mit eigenem Startmenü-Eintrag und Deinstallation.
   **Ein installiertes offizielles Creality Print bleibt unverändert** (eigener Ordner, eigener Registry-Schlüssel,
   eigener Einstellungsordner `%APPDATA%\Creality\Creality Print\7.3 Alpha`; Dateizuordnungen werden nicht geändert).

## Einrichtung

### 1. Remote API einschalten

In Creality Print: **Einstellungen → Allgemein → Abschnitt „Remote API“**

- **Remote API aktivieren** anhaken und den Dialog schließen (der Server startet auf `127.0.0.1:13130`).
- Den angezeigten **API-Token** kopieren.
- **Zugriff aus dem LAN** ausgeschaltet lassen, solange kein anderer Rechner zugreifen muss.

### 2. MCP-Client verbinden

Als MCP-Server dient [orcaslicer-mcp](https://github.com/maxellis/orcaslicer-mcp) von Max Ellis – er funktioniert
unverändert mit dieser Mod. Er braucht [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`).

**Claude Desktop** – in `%APPDATA%\Claude\claude_desktop_config.json` ergänzen:

```json
{
  "mcpServers": {
    "creality_print": {
      "command": "uvx",
      "args": ["orcaslicer-mcp"],
      "env": { "ORCA_API_TOKEN": "<dein Token>" }
    }
  }
}
```

**Codex / andere Clients** – STDIO-Server, Befehl `uvx`, Argument `orcaslicer-mcp`,
Umgebungsvariable `ORCA_API_TOKEN=<dein Token>`.

Client neu starten, Creality Print starten und fragen: *„Welcher Drucker und welches Profil sind in Creality Print aktiv?“*

### Schnelltest ohne KI

```powershell
curl.exe -H "X-Api-Token: <dein Token>" http://127.0.0.1:13130/api/v1/status
```

Ohne Token antwortet die API mit `401 unauthorized`.

---

## Sicherheit

- Die Remote API ist **standardmäßig aus** und lauscht nur auf `127.0.0.1`.
- Jede Anfrage braucht den Token; wird er bekannt, einfach neu erzeugen.
- Mit **LAN-Zugriff** kann jedes Gerät im Netz, das den Token kennt, den Slicer steuern.
- Die API steuert nur den **Slicer** – sie sendet nichts an deinen Drucker.

## Unterschiede zum offiziellen Creality Print

- **Kein Selbst-Update:** Ein offizielles Update würde die Remote API entfernen. Neue Mod-Versionen gibt es hier im Repository.
- Version wird als `7.3.1.6378-mcp.N` angezeigt; Startbild und „Über“-Dialog kennzeichnen den Build als Mod.
- Protokollstufe und der Schalter „Löschen und Überschreiben von Projektdateien erlauben“ (standardmäßig aus) stehen im Abschnitt „Remote API“ der Einstellungen.
- Vollständige Liste der Änderungen, Herkunft und Lizenzen: **[MOD_NOTICE.md](MOD_NOTICE.md)**

## Bekannte Einschränkungen

- Nur Windows x64 (andere Plattformen werden nicht gebaut oder getestet).
- *Objekt duplizieren* setzt jede Kopie neben die vorige (Objektbreite + 5 mm); läuft sie über die Platte hinaus, *Platte anordnen* nutzen.
- Filament-Slots: Die Werkzeuge `get_printer_slots` / `*_slot_mapping` funktionieren in orcaslicer-mcp nur für Elegoo CANVAS und melden hier `not supported`. CFS-Slots wählst du im *Senden*-Dialog von Creality Print.
- Die Flussvorhersage (*prediction check*) von orcaslicer-mcp ist eine grobe Schätzung (Geschwindigkeit × Linienbreite × Schichthöhe). Der tatsächliche Fluss in Creality kann höher liegen, z. B. durch variable Linienbreiten (Arachne), Lückenfüllung oder Einstellungen pro Objekt. `anomaly` ist dort also nicht automatisch ein Problem. Die gemessenen Werte (`observed_max_mm3_s`) stammen direkt aus dem G-Code und sind verlässlich.
- Creality-spezifische Funktionen (Creality Cloud, CFS) sind über die API nicht erreichbar.

---

## Herkunft & Dank

| Baustein | Quelle | Lizenz |
|---|---|---|
| Creality Print 7.3.1 (Basis) | [CrealityOfficial/CrealityPrint](https://github.com/CrealityOfficial/CrealityPrint) | AGPL-3.0 |
| Remote API | OrcaSlicer-MCP-Build von Max Ellis – [maxellis/OrcaSlicer](https://github.com/maxellis/OrcaSlicer) | AGPL-3.0 |
| MCP-Server | [maxellis/orcaslicer-mcp](https://github.com/maxellis/orcaslicer-mcp) | AGPL-3.0 |

Creality Print selbst basiert auf OrcaSlicer und Ultimaker CuraEngine; OrcaSlicer basiert auf Bambu Studio,
PrusaSlicer und SuperSlicer; PrusaSlicer stammt von Slic3r (Alessandro Ranellucci und RepRap-Gemeinschaft).
Crealitys ursprüngliche README: [README.creality.md](README.creality.md).

## Selbst bauen

Branch `mcp-mod` = Creality Print `v7.3.1` + Mod-Commits. Windows-Build: Visual Studio 2022 Build Tools
(C++-Workload, Windows SDK 10.0.22000), CMake 3.28/3.29 (nicht 4.x), Strawberry Perl, Git; danach Crealitys
`test_build.bat deps` und `test_build.bat slicer`. Installer: NSIS mit `package/mod/installer_mod.nsi`.

## Lizenz

AGPL-3.0, wie Creality Print. Namen und Logos von Creality gehören Creality und dienen hier nur zur Kennzeichnung
der Basis dieser inoffiziellen Mod.
