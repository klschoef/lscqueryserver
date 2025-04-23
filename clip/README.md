# CLIP Server

The **CLIP Server** is a Python-based application designed to handle natural language queries using the CLIP 
(Contrastive Language–Image Pretraining) model. It supports FAISS indices for efficient similarity search and
integrates seamlessly with the LifeXplore Backend System.

---

## **Features**
- Processes natural language queries using the CLIP model.
- Supports FAISS indices for fast similarity search.
- Provides a WebSocket interface for communication with other modules.
- Can be configured to use existing FAISS indices or generate new ones.

---

## **Requirements**
- Python 3.8 or higher.
- Required Python dependencies (see `requirements.txt`).
- Optional: Existing FAISS index
---

## **Setup**

### **1. Install Python**
Ensure Python 3.8 or higher is installed on your system.

### **2. Configure the Environment**
1. Copy the example environment file and adjust the configuration:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with the following key parameters if needed (keep the default values if unsure):
    - `VENV_NAME`: Name of the virtual environment to be created.
    - `SHARED_LIB_PATH`: Path to the shared library required for the build process.

### **3. Run the Setup Script**
Use the `setup.sh` script to create the virtual environment:
```bash
bash setup.sh
```
This script will:
- Create a virtual environment.
- Install required Python dependencies.
- Create a symbolic link for the shared library.

### **4. Activate the Virtual Environment**
Switch to the virtual environment:
```bash
source .venv/bin/activate
```

### **5. Start the CLIP Server**
Run the server with the following command:
```bash
python clip.py --keyframe_base_root ../shared/images --faiss_folder ../shared/faiss/path_to_faiss_folder.faiss --ws_port 8002
```
- Use the `--create_faiss_folder true` flag if a new FAISS index needs to be created. This index can later be populated by the `analysis_server`.

---

## **Command-Line Parameters**
The following parameters can be used to configure the CLIP server:

| Parameter               | Default Value                      | Description                                                                 |
|-------------------------|------------------------------------|-----------------------------------------------------------------------------|
| `--keyframe_base_root`  | `/images`                          | Base path to the images (keyframes).                                       |
| `--faiss_folder`        | None                               | Path to the FAISS folder.                                                  |
| `--create_faiss_folder` | `False`                            | Set to `true` to create the FAISS folder if it does not exist.             |
| `--ws_port`             | `8002`                             | WebSocket port for the server.                                             |
| `--image_server_path`   | `http://localhost:8122/lifexplore` | Base path to the image server.                                             |
| `--image_server_timeout`| `5`                                | Timeout (in seconds) for image server requests.                            |
| `--model_name`          | `ViT-H-14`                         | Name of the CLIP model to be used.                                         |
| `--weights_name`        | `laion2b_s32b_b79k`                | Name of the pre-trained weights to be used.                                |

---

## **FAISS Index Management**
- **Generate a New Index**: Use the `--create_faiss_folder true` flag to create a new FAISS index.

---

## **Troubleshooting**
- Ensure all dependencies are installed correctly.
- Verify the `.env` file is configured with the correct paths and settings.
- Check the logs for detailed error messages.