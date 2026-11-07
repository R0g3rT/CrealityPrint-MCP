// Kennzeichnung dieses Builds als inoffizielle Mod von Creality Print.
// Bei jeder neuen Mod-Version CREALITYPRINT_MOD_NUMBER um eins erhoehen.
#ifndef slic3r_RemoteAPI_ModVersion_hpp_
#define slic3r_RemoteAPI_ModVersion_hpp_

#include "libslic3r_version.h"

#define CREALITYPRINT_MOD_NUMBER  "2"
#define CREALITYPRINT_MOD_TAG     "mcp." CREALITYPRINT_MOD_NUMBER
// z. B. "7.3.1.0-mcp.1": Creality-Basisversion + Mod-Nummer
#define CREALITYPRINT_MOD_VERSION CREALITYPRINT_VERSION "-" CREALITYPRINT_MOD_TAG

#endif
