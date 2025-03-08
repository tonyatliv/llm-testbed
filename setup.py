from utils.handlers import ConfigHandler
import os

def setup():
    # setup folder structure
    config = ConfigHandler()
    folders = [
        config.getStatusFolderPath(),
        config.getJSONFolderPath(),
        config.getPDFsFolderPath(),
        config.getPlaintextFolderPath(),
        config.getSummaryFolderPath(),
        config.getResultFolderPath(),
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

if __name__ == "__main__":
    setup()
    print("Setup script successful")
    