"""Uebernimmt RemoteAPIController.cpp aus maxellis/OrcaSlicer (Branch remote-api-242) und wendet
die Creality-Anpassungen an. Jede Ersetzung muss genau einmal treffen, sonst Abbruch.

Aufruf: python port_controller.py <Orca-Controller.cpp> <Ziel-Controller.cpp>
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read()


def sub(old, new, count=1):
    global t
    n = t.count(old)
    if n != count:
        sys.exit(f"FEHLER: {n}x gefunden (erwartet {count}): {old[:80]!r}")
    t = t.replace(old, new)


# 1) Includes: I18N vor den libslic3r-Headern, ModelInstance, Mod-Version; Elegoo raus
sub('#include "RemoteAPIController.hpp"\n',
    '#include "RemoteAPIController.hpp"\n'
    '#include "slic3r/GUI/I18N.hpp" // vor libslic3r-Headern, sonst fehlen _L/_u8L\n'
    '#include "ModVersion.hpp"\n')
sub('#include "libslic3r/Model.hpp"', '#include "libslic3r/Model.hpp"\n#include "libslic3r/ModelInstance.hpp"')
t, n = re.subn(r'#include "slic3r/(GUI/ElegooCanvas\w*|Utils/ElegooCanvas\w*|Utils/ElegooLink)\.hpp"[^\n]*\n', "", t)
if n != 6:
    sys.exit(f"FEHLER: {n} Elegoo-Includes entfernt (erwartet 6)")

# 2) Version der Mod in /status
sub('{"app_version", SoftFever_VERSION},', '{"app_version", CREALITYPRINT_MOD_VERSION},')

# 3) Tab::select_preset hat in Creality kein force_no_transfer
t, n = re.subn(r', /\*force_no_transfer=\*/true\)', ')', t)
if n < 1:
    sys.exit("FEHLER: kein force_no_transfer gefunden")

# 3b) Titelzeile aktualisieren heisst in Creality anders; Ladezustand ueber Accessor (Plater.hpp)
t, n = re.subn(r'plater->update_title_dirty_status\(\);', 'wxGetApp().mainframe->update_title();', t)
if n < 1:
    sys.exit("FEHLER: update_title_dirty_status nicht gefunden")

# 4) Kamera-Blickwinkel: Creality waehlt Ansichten per Name
i = t.index("    static const std::map<std::string, Camera::ViewAngleType> angle_map")
j = t.index("    auto ait = angle_map.find(angle);")
t = t[:i] + '    static const std::set<std::string> angle_map = {"iso", "top", "front", "left", "right", "rear", "bottom"};\n' + t[j:]
sub("const Camera::ViewAngleType va           = ait->second;", "const std::string           va           = *ait;")

# 5) Zeit pro Druckbereich: MoveVertex::time ist in Creality die Zugnummer
sub("""        struct RoleAgg { double time_s = 0.0, max_flow = 0.0, sum_ft = 0.0; };
        RoleAgg agg[erCount];
        for (const auto &mv : res->moves) {
            if (mv.type != EMoveType::Extrude) continue;
            int r = (int) mv.extrusion_role;
            if (r <= 0 || r >= erCount) continue;
            double t = mv.time[0];
            double vr = mv.volumetric_rate(); // feedrate * mm3_per_mm
            agg[r].time_s += t;
            agg[r].sum_ft += vr * t;
            if (vr > agg[r].max_flow) agg[r].max_flow = vr;
        }
""", """        // Creality: MoveVertex::time enthaelt die Zugnummer, keine Zeit. Die Zeit pro
        // Bereich liefert Creality selbst (roles_times); max. Fluss kommt aus den Zuegen,
        // mittlerer Fluss = Filamentvolumen / Zeit.
        struct RoleAgg { double time_s = 0.0, max_flow = 0.0; };
        RoleAgg agg[erCount];
        for (const auto &mv : res->moves) {
            if (mv.type != EMoveType::Extrude) continue;
            int r = (int) mv.extrusion_role;
            if (r <= 0 || r >= erCount) continue;
            double vr = mv.volumetric_rate(); // feedrate * mm3_per_mm
            if (vr > agg[r].max_flow) agg[r].max_flow = vr;
        }
        if (!res->print_statistics.modes.empty())
            for (const auto &rt : res->print_statistics.modes.front().roles_times) {
                int r = (int) rt.first;
                if (r > 0 && r < erCount) agg[r].time_s += rt.second;
            }
        const double fil_d    = res->filament_diameters.empty() ? 1.75 : (double) res->filament_diameters.front();
        const double fil_area = 3.14159265358979 * fil_d * fil_d / 4.0;
""")
sub('{"mean", agg[r].time_s > 0.0 ? agg[r].sum_ft / agg[r].time_s : 0.0}}}',
    '{"mean", (has_fil && agg[r].time_s > 0.0) ? it->second.first * 1000.0 * fil_area / agg[r].time_s : 0.0}}}')

# 6) Creality meldet beim Laden der Vorschau nachtraeglich Fortschritt: kein neuer Slice
sub("""        evt.Skip(); // REQUIRED: let the Plater's own handler run (bound earlier = runs after us)
        if (evt.status.percent >= 0)
""", """        evt.Skip(); // REQUIRED: let the Plater's own handler run (bound earlier = runs after us)
        // Creality meldet nach fertigem Slice beim Laden der Vorschau noch Fortschritt
        // ("Anzeigedaten werden geladen"). Das ist kein neuer Slice: ignorieren, solange
        // das vorhandene Ergebnis gueltig ist.
        if (slice_state().state == "done") {
            PartPlate *plate = wxGetApp().plater()->get_partplate_list().get_curr_plate();
            if (plate != nullptr && plate->is_slice_result_valid())
                return;
        }
        if (evt.status.percent >= 0)
""")

# 7) Spuelvolumen-Warnhinweis gibt es in Creality nicht
sub("""            if (touched_flush)
                wxGetApp().sidebar().set_flushing_volume_warning(is_flush_config_modified());
""", """            // Creality hat keinen Spuelvolumen-Warnhinweis in der Seitenleiste (Orca-only)
            (void) touched_flush;
""")

# 7b) Duplizieren: Kopie neben das letzte Exemplar statt fest 10 mm versetzt (ueberlappte sonst)
sub("""        const ModelInstance *src = mo->instances.front();
        Vec3d off = src->get_offset() + Vec3d(10.0, 10.0, 0.0);
""", """        const ModelInstance *src = mo->instances.front();
        // Mod: neben das letzte Exemplar setzen (Objektbreite + 5 mm), damit sich nichts ueberlappt
        const double step = mo->instance_bounding_box(0).size().x() + 5.0;
        Vec3d off = mo->instances.back()->get_offset() + Vec3d(step, 0.0, 0.0);
""")

# 8) Elegoo CANVAS (Slots/Slot-Zuordnung) gibt es in Creality nicht: klare Absage statt Fehler
i = t.index("// --- Elegoo CANVAS: printer slots and the filament slot mapping")
j = t.index("Response Controller::dispatch(const Request &req)")
t = t[:i] + """// --- Filament-Slots: in der Creality-Mod nicht unterstuetzt ------------------------------
// Orca liest hier die CANVAS-Einheit von Elegoo-Druckern. Crealitys CFS-Zuordnung passiert in der
// Web-Oberflaeche des Sendedialogs; der Nutzer waehlt die Slots dort.
static nlohmann::json slots_unsupported()
{
    return {{"supported", false},
            {"reason", "not_supported_printer"},
            {"message", "Filament slots cannot be read or mapped through the API in Creality Print MCP Mod. "
                        "Choose the CFS slots in Creality Print's Send dialog."}};
}

Response Controller::handle_printer_slots() { return { 200, slots_unsupported() }; }
Response Controller::handle_get_slot_mapping() { return { 200, slots_unsupported() }; }
Response Controller::handle_put_slot_mapping(const std::string &) { return { 200, slots_unsupported() }; }

""" + t[j:]

# 9) Senden-Dialog: Vorgabe "Druckbettkalibrierung" als Pseudo-Schluessel send_print_calibration.
#    Creality merkt sich die Checkbox in data_dir()/cache/send_to_printer/user_operation_state.json
#    (CxSentToPrinterDialog::load_user_operation_state); der Dialog liest sie beim Oeffnen.
sub("#include <boost/filesystem.hpp>", "#include <boost/filesystem.hpp>\n#include <boost/nowide/fstream.hpp>\n#include \"libslic3r/Utils.hpp\" // data_dir()")
sub("Response Controller::handle_get_config(const std::string &target)\n{",
"""// --- MCP-Mod: Vorgabe Druckbettkalibrierung im Senden-Dialog -----------------------------
static const char *MOD_SEND_CAL_KEY = "send_print_calibration";

static boost::filesystem::path mod_send_state_path()
{
    return boost::filesystem::path(data_dir()) / "cache" / "send_to_printer" / "user_operation_state.json";
}

static nlohmann::json mod_read_send_state()
{
    try {
        boost::nowide::ifstream in(mod_send_state_path().string());
        if (in.is_open()) {
            std::stringstream ss; ss << in.rdbuf();
            auto j = nlohmann::json::parse(ss.str(), nullptr, false);
            if (!j.is_discarded() && j.is_object()) return j;
        }
    } catch (...) {}
    return nlohmann::json::object();
}

static int mod_get_send_calibration()
{
    auto j = mod_read_send_state();
    if (!j.contains("print_calibration")) return 1; // Creality-Standard: an
    const auto &v = j["print_calibration"];
    if (v.is_boolean()) return v.get<bool>() ? 1 : 0;
    if (v.is_number_integer()) return v.get<int>() == 1 ? 1 : 0;
    return 0;
}

static bool mod_set_send_calibration(int on)
{
    try {
        auto j = mod_read_send_state();
        j["print_calibration"] = on ? 1 : 0;
        const auto p = mod_send_state_path();
        boost::filesystem::create_directories(p.parent_path());
        boost::nowide::ofstream out(p.string(), std::ios::out | std::ios::trunc);
        if (!out.is_open()) return false;
        out << j.dump(-1, ' ', true);
        return true;
    } catch (...) { return false; }
}

// -1 = ungueltig
static int mod_parse_on_off(const nlohmann::json &v)
{
    if (v.is_boolean()) return v.get<bool>() ? 1 : 0;
    if (v.is_number_integer()) { auto n = v.get<long long>(); return n == 0 ? 0 : n == 1 ? 1 : -1; }
    if (v.is_string()) {
        std::string s = v.get<std::string>();
        for (auto &c : s) c = (char) std::tolower((unsigned char) c);
        if (s == "1" || s == "true" || s == "on") return 1;
        if (s == "0" || s == "false" || s == "off") return 0;
    }
    return -1;
}

Response Controller::handle_get_config(const std::string &target)
{""")
sub("""        return config_to_json(cfg, keys.empty() ? nullptr : &keys);
    });
    return { 200, {{"config", j}} };""",
"""        nlohmann::json out = config_to_json(cfg, keys.empty() ? nullptr : &keys);
        if (keys.empty() || std::find(keys.begin(), keys.end(), MOD_SEND_CAL_KEY) != keys.end())
            out[MOD_SEND_CAL_KEY] = std::to_string(mod_get_send_calibration());
        return out;
    });
    return { 200, {{"config", j}} };""")
sub("""Response Controller::handle_put_config(const std::string &body)
{
    // May throw nlohmann::json::parse_error - caught by the dispatch route
    // below and turned into a 400, distinct from the generic 500 path.
    nlohmann::json in = nlohmann::json::parse(body);
    if (!in.is_object())
        return { 400, {{"error", "body_must_be_object"}} };
""",
"""Response Controller::handle_put_config(const std::string &body)
{
    // May throw nlohmann::json::parse_error - caught by the dispatch route
    // below and turned into a 400, distinct from the generic 500 path.
    nlohmann::json in = nlohmann::json::parse(body);
    if (!in.is_object())
        return { 400, {{"error", "body_must_be_object"}} };

    // MCP-Mod: send_print_calibration ist keine Preset-Einstellung, sondern die Vorgabe der
    // Checkbox "Druckbettkalibrierung" im Senden-Dialog. Atomar wie der Rest: erst nach
    // fehlerfreiem Anwenden der uebrigen Schluessel schreiben.
    int mod_cal = -2;
    if (in.contains(MOD_SEND_CAL_KEY)) {
        mod_cal = mod_parse_on_off(in[MOD_SEND_CAL_KEY]);
        if (mod_cal < 0)
            return { 422, {{"applied", nlohmann::json::array()},
                           {"errors", {{MOD_SEND_CAL_KEY, "expected 0/1 or true/false"}}}} };
        in.erase(MOD_SEND_CAL_KEY);
        if (in.empty()) {
            if (!mod_set_send_calibration(mod_cal))
                return { 422, {{"applied", nlohmann::json::array()},
                               {"errors", {{MOD_SEND_CAL_KEY, "could_not_write_send_dialog_state"}}}} };
            return { 200, {{"applied", nlohmann::json::array({MOD_SEND_CAL_KEY})},
                           {"errors", nlohmann::json::object()}}};
        }
    }
""")
sub("""    int status = result["errors"].empty() ? 200 : 422;
    return { status, result };
}
""", """    if (mod_cal >= 0 && result["errors"].empty()) {
        if (mod_set_send_calibration(mod_cal))
            result["applied"].push_back(MOD_SEND_CAL_KEY);
        else
            result["errors"][MOD_SEND_CAL_KEY] = "could_not_write_send_dialog_state";
    }
    int status = result["errors"].empty() ? 200 : 422;
    return { status, result };
}
""")

# 10) Projekt oeffnen: Orca kennt "<loadall>" als Sonderwert, Creality nicht. Creality behandelt jeden
#     Wert ausser "-" und "<silence>" als Wiederherstellungsdatei (LoadStrategy::Restore) und laedt
#     "<loadall>" als zweite Datei -> "Laden der Modelldatei fehlgeschlagen" (modaler Dialog, API haengt).
#     "-" ist Crealitys Standard fuer Datei > Oeffnen.
sub('plater->load_project(wpath, "<loadall>"); // "<loadall>": open as a project, no import-type dialog',
    'plater->load_project(wpath, "-"); // Creality: "-" = normal als Projekt oeffnen (kein "<loadall>")')

left = [l for l in t.splitlines() if re.search(r"Elegoo|ElegooCanvas|CanvasState|elegoo_canvas", l) and not l.lstrip().startswith("//")]
if left:
    sys.exit("FEHLER: Elegoo-Reste:\n" + "\n".join(left[:10]))
open(dst, "w", encoding="utf-8", newline="").write(t)
print("ok")
