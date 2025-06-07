import subprocess

result = subprocess.run(["ls", "-l"], capture_output=True, text=True)

print("Command:", result.args)
print("Return Code:", result.returncode)
print("Standard Output:\n", result.stdout)
print("Standard Error:\n", result.stderr)