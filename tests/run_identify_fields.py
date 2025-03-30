from pathlib import Path
import sys
import logging

# Caminhos
project_root = Path(__file__).resolve().parent.parent
scripts_dir = project_root / "scripts"
identify_script_path = scripts_dir / "identify_fields.py"

# Logs visuais
logging.basicConfig(level=logging.INFO)
logging.info(f"🧪 Executando: {identify_script_path}")

# Ajustar o sys.path (caso tenha imports relativos)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Executar o script
if identify_script_path.exists():
    with open(identify_script_path, encoding="utf-8") as f:
        code = compile(f.read(), identify_script_path.name, 'exec')
        exec(code, {
            "__name__": "__main__",
            "__file__": str(identify_script_path)
        })
else:
    logging.error(f"❌ Script não encontrado: {identify_script_path}")
