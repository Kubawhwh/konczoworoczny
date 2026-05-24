import os
import sys
import subprocess

pong = os.path.join(os.path.dirname(__file__), "pong.py")

if not os.path.exists(pong):
    print("pong.py not found")
    sys.exit()

subprocess.run([sys.executable, pong])