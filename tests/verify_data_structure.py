# scripts/verify_data_structure.py

from pathlib import Path
import pandas as pd
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_project_root() -> Path:
    """Get the project root directory."""
    # Start with the directory containing this script
    current_path = Path(__file__).resolve()
    
    # Go up one level (to project root) since script is in 'scripts' directory
    project_root = current_path.parent.parent
    
    # Verify it's the correct directory by checking for some key files/directories
    if not (project_root / 'app').exists():
        raise RuntimeError(
            f"Cannot find project root directory (looking for 'app' directory)\n"
            f"Current path: {project_root}"
        )
    
    return project_root

def verify_data_structure():
    """Verify and create necessary data structure."""
    try:
        # Get project root
        project_root = get_project_root()
        logger.info(f"Project root: {project_root}")
        
        # Required directories
        directories = [
            project_root / 'data',
            project_root / 'data/geospatial',
            project_root / 'data/outputs',
            project_root / 'data/maps'
        ]
        
        # Create directories
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Verified directory: {directory}")
        
        # Verify coordinates file
        coords_file = project_root / 'data/station_coordinates.csv'
        if not coords_file.exists():
            # Create sample coordinates file with more stations
            sample_data = {
                'station_name': [
                    'Finsbury Park',
                    'Kings Cross',
                    'London Liverpool Street',
                    'Cambridge',
                    'Stevenage',
                    'Peterborough',
                    'Welwyn Garden City',
                    'Letchworth Garden City',
                    'Hitchin',
                    'Alexandra Palace'
                ],
                'crs': [
                    'FPK',
                    'KGX',
                    'LST',
                    'CBG',
                    'SVG',
                    'PBO',
                    'WGC',
                    'LET',
                    'HIT',
                    'AAP'
                ],
                'latitude': [
                    51.5643,
                    51.5320,
                    51.5177,
                    52.1947,
                    51.9017,
                    52.5747,
                    51.8026,
                    51.9758,
                    51.9535,
                    51.5941
                ],
                'longitude': [
                    -0.1063,
                    -0.1240,
                    -0.0817,
                    0.1374,
                    -0.2067,
                    -0.2405,
                    -0.2032,
                    -0.2289,
                    -0.2631,
                    -0.1200
                ]
            }
            
            df = pd.DataFrame(sample_data)
            df.to_csv(coords_file, index=False)
            logger.info(f"✅ Created sample coordinates file: {coords_file}")
            logger.info(f"   Added {len(df)} stations")
        else:
            df = pd.read_csv(coords_file)
            logger.info(f"✅ Coordinates file exists: {coords_file}")
            logger.info(f"   Contains {len(df)} stations")
        
        logger.info("\n✅ Data structure verification completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error verifying data structure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    verify_data_structure()