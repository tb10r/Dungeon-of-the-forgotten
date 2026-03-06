import subprocess
import sys

print("Instalando Flask...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
print("Flask instalado com sucesso!")
