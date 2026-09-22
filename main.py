import sys
import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent
    features_root = project_root / "features"

    # Get user input
    if len(sys.argv) != 2:
        print(
            "You need to include a feature directory as an argument.\n"
            "Usage: evaluate <feature_name>  OR  evaluate features/<feature_name>/\n"
            "       python3 main.py <feature_name>  OR  python3 main.py features/<feature_name>/"
        )
        list_features(features_root)
        sys.exit(1)

    raw_input = sys.argv[1]

    # Normalize input to just the folder name
    feature_name = Path(raw_input).name
    feature_dir = features_root / feature_name

    # Validate feature exists and has main.py
    if not feature_dir.is_dir() or not (feature_dir / "main.py").exists():
        print(f"Error: Feature '{feature_name}' not found or missing main.py.")
        list_features(features_root)
        sys.exit(1)
    
    module_path = f"features.{feature_name}.main"
    
    subprocess.run([
      "python3", "-m", module_path],
      cwd=project_root
      )

def list_features(features_root: Path):
    """Print a list of available features for user convenience."""
    if features_root.exists():
        print("Available features:")
        for f in sorted(features_root.iterdir()):
            if f.is_dir() and (f / "main.py").exists():
                print(" -", f.name)
    else:
        print("No 'features' directory found in project root.")


if __name__ == "__main__":
    main()
