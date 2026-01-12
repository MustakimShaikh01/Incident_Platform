LIB_VERSION_RULES = {
    "numpy": {
        "max_python": "3.10",
        "issue": "numpy 2.x has compatibility issues with Python 3.11"
    }
}

def detect_version_conflicts(runtime):
    conflicts = []
    python_version = runtime.get("python", "")
    libs = runtime.get("libs", {})

    for lib, rule in LIB_VERSION_RULES.items():
        if lib in libs and python_version > rule["max_python"]:
            conflicts.append({
                "library": lib,
                "problem": rule["issue"]
            })

    return conflicts
