import sys
import os

# Add backend directory to path
sys.path.append('c:/Users/Maheswari/OneDrive/Desktop/my project/front/backend')

try:
    from backend import routes
    print("Successfully imported routes")
except Exception as e:
    print(f"Error importing routes: {e}")
except SyntaxError as e:
    print(f"Syntax Error in routes: {e}")

try:
    from backend import models
    print("Successfully imported models")
except Exception as e:
    print(f"Error importing models: {e}")
