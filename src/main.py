import sys
import os

# Add src to path so relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == "__main__":
    main()
