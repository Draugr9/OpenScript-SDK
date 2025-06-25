import sys
from osc.runtime import run

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.osc>")
        return
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    run(code)

if __name__ == "__main__":
    main()
