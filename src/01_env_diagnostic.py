# Importaciones de la librería estándar de Python
import os  # Manejo de la interfaz con el sistema operativo y variables de entorno
import platform  # Detección de la arquitectura y sistema operativo
import sys  # Funciones del sistema e interacción con el intérprete de Python
from pathlib import Path  # Manejo orientado a objetos de rutas de archivos


def load_env_file_natively(env_path: Path) -> None:
    """Lee un archivo .env y carga las variables en os.environ de forma nativa.

    Evita requerir dependencias externas en scripts de diagnóstico base.

    Args:
        env_path (Path): Ruta al archivo .env dentro del sistema de archivos.
    """
    if not env_path.exists():  # Si el archivo .env no existe en disco, finaliza
        return

    # Abre y lee el archivo .env usando codificación utf-8
    with open(env_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()  # Elimina espacios en blanco y saltos de línea al inicio y fin
            # Ignora líneas vacías o comentarios que inician con '#'
            if not line or line.startswith("#"):
                continue

            # Separar únicamente por el primer signo '=' encontrado en la línea
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()  # Limpia la clave
                # Limpia el valor eliminando comillas dobles o simples si existen
                value = value.strip().strip("'\"")

                # Asigna la variable directamente a la memoria de proceso de Python
                os.environ[key] = value


def run_environment_diagnostics() -> bool:
    """Ejecuta diagnósticos del sistema para validar la configuración del entorno local.

    Returns:
        bool: True si todas las verificaciones críticas pasan, False en caso contrario.
    """
    # Determinación de la ruta raíz del proyecto
    base_dir = Path(__file__).resolve().parent.parent

    # Cargar variables de entorno desde el archivo .env en la raíz del proyecto
    load_env_file_natively(base_dir / ".env")

    # Definición de códigos ANSI para salida estructurada en terminal
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    all_passed = True

    print("==================================================")
    print("      DIAGNÓSTICO DE ENTORNO ENTERPRISE GENAI    ")
    print("==================================================\n")

    # --- VERIFICACIÓN 1: Versión del Runtime de Python ---
    major_ver = sys.version_info.major
    minor_ver = sys.version_info.minor
    py_version_str = f"{major_ver}.{minor_ver}.{sys.version_info.micro}"

    if major_ver == 3 and minor_ver >= 11:
        print(f"[{GREEN}PASS{RESET}] Versión de Python: {py_version_str}")
    else:
        print(
            f"[{RED}FAIL{RESET}] Versión de Python: {py_version_str} (Se requiere Python 3.11+)"
        )
        all_passed = False

    # --- VERIFICACIÓN 2: Detección de Arquitectura e Infraestructura ---
    sys_platform = platform.system()
    architecture = platform.machine()

    print(f"[INFO] Sistema Operativo: {sys_platform} ({architecture})")
    if sys_platform == "Darwin" and architecture == "arm64":
        print(
            f"[{GREEN}PASS{RESET}] Hardware Target: Apple Silicon (Aceleración Metal/MPS lista)"
        )
    else:
        print(
            f"[INFO] Hardware Target: Arquitectura estándar x86_64 o servidor Cloud"
        )

    # --- VERIFICACIÓN 3: Estructura de Directorios del Proyecto ---
    required_directories = [
        base_dir / "src",
        base_dir / "config",
        base_dir / "logs",
    ]

    for folder in required_directories:
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            print(
                f"[FIXED] Carpeta creada automáticamente: {folder.relative_to(base_dir)}"
            )
        else:
            print(
                f"[{GREEN}PASS{RESET}] Directorio verificado: {folder.relative_to(base_dir)}"
            )

    # --- VERIFICACIÓN 4: Auditoría de Variables de Entorno ---
    expected_env_vars = ["GEMINI_API_KEY", "ENVIRONMENT"]

    for env_var in expected_env_vars:
        val = os.getenv(env_var)  # Obtiene la variable del proceso del SO
        if val:
            # Enmascaramiento visual de secretos
            masked_val = (
                val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
            )
            print(
                f"[{GREEN}PASS{RESET}] Variable de entorno '{env_var}': Cargada ({masked_val})"
            )
        else:
            print(
                f"[{YELLOW}WARN{RESET}] Variable de entorno '{env_var}': Faltante o vacía (Revisar archivo .env)"
            )

    print("\n--------------------------------------------------")
    if all_passed:
        print(
            f"[{GREEN}ÉXITO{RESET}] Diagnóstico local completado. Entorno listo para producción."
        )
    else:
        print(
            f"[{RED}FALLO{RESET}] Validación de entorno fallida. Resuelve los errores indicados."
        )

    return all_passed


if __name__ == "__main__":
    success = run_environment_diagnostics()
    sys.exit(0 if success else 1)