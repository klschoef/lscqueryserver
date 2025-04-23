# Analysis Server

The **Analysis Server** is a standalone component of the LifeXplore Backend System. It processes images by analyzing them, adding metadata to MongoDB, and updating the FAISS index. It supports extensible pipelines for custom analysis logic and provides a file watcher for automated processing of new images. Additionally, an optional upload server is available for HTTP-based image uploads.

---

## **Requirements**
- Python 3.8 or higher.
- MongoDB server and CLIP server must be running (refer to their respective `README` files for setup).

---

## **Setup**

### **1. Install Python**
Ensure Python 3.8 or higher is installed on your system.

### **2. Configure the Environment**
1. Copy the example environment file and adjust the configuration:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with the following key parameters:
    - `VENV_NAME`: Name of the virtual environment to be created. (use the default one if not sure)
    - `SHARED_LIB_PATH`: Path to the shared library required for the build process. (use the default one if not sure)
    - `MONGO_DB_URL`: MongoDB connection URL.
    - `MONGO_DB_DATABASE`: MongoDB database name.
    - `CLIP_URL`: URL of the running CLIP server.
    - Other parameters can be adjusted as needed.

### **3. Create and Activate the Virtual Environment**
Run the setup script to create the virtual environment:
```bash
bash setup.sh
```
Activate the virtual environment:
```bash
source .venv/bin/activate
```

---

## **Usage**

### **1. Start the Watcher**
The watcher monitors a folder for new images, processes them, and moves them to the specified storage folder. Use the following command to start the watcher:
```bash
python add-image.py <image_path> --image-storage <storage_path> --watch-folder --watch-interval <interval_in_seconds>
```

#### **Command-Line Parameters**
| Parameter              | Default Value                          | Description                                                                 |
|------------------------|----------------------------------------|-----------------------------------------------------------------------------|
| `image_path`           | None                                   | Path to the input image or folder with images.                             |
| `--image-storage`      | `/images`                              | Directory where processed images will be saved (in a subfolder `uploads`). |
| `--upload-folder-name` | `uploads`                              | Name of the subfolder for processed images.                                |
| `--watch-folder`       | `False`                                | Watch the folder for new images.                                           |
| `--class-names`        | `InitialPipeline,OpenClipPipeline,BlurFacesPipeline` | Comma-separated list of pipeline class names to use.                       |
| `--watch-interval`     | `60`                                   | Interval (in seconds) to check for new images.                             |

#### **Example**
```bash
python add-image.py ../../../backup/imgs/raw-uploads --image-storage ../../../backup/imgs/data --watch-folder --watch-interval 10
```

---

### **2. Start the Upload Server**
The upload server is a Flask-based application that allows HTTP-based image uploads to the watcher folder. Use the following command to start the server:
```bash
python upload-server.py --upload_folder <folder_path> --max_content_length <max_size_in_bytes> --port <port_number>
```

#### **Command-Line Parameters**
| Parameter              | Default Value | Description                                      |
|------------------------|---------------|--------------------------------------------------|
| `--upload_folder`      | None          | Folder to store uploaded files.                 |
| `--max_content_length` | `50 * 1024 * 1024` | Maximum upload size in bytes.                   |
| `--port`               | `5000`        | Port to run the Flask server on.                |

#### **Example**
```bash
python upload-server.py --upload_folder ../../../backup/imgs/raw-uploads --port 5000
```

---

### **(Optional) Update Existing Entries**
To process existing database entries (e.g., when adding a new pipeline), use the `run-pipeline.py` script:
```bash
python run-pipeline.py --image-storage <storage_path> --class-names <pipeline_classes> --update-after <timestamp>
```

#### **Command-Line Parameters**
| Parameter              | Default Value                          | Description                                                                 |
|------------------------|----------------------------------------|-----------------------------------------------------------------------------|
| `--image-storage`      | `/images`                              | Directory where images are stored.                                         |
| `--class-names`        | `BlurFacesPipeline,OpenClipPipeline`   | Comma-separated list of pipeline class names to use.                       |
| `--update-after`       | None                                   | Process entries updated after this timestamp (format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`). |

#### **Example**
```bash
python run-pipeline.py --image-storage ../../../backup/imgs/data --class-names BlurFacesPipeline,OpenClipPipeline --update-after 2023-01-01
```

---

## **Adding New Pipelines**
To add new analysis logic, create a new pipeline in the `core/processing_pipelines` directory by inheriting from the `base_pipeline`. Pipelines are executed in the order they are passed to the script. **Important:** Always include `InitialPipeline` as the first pipeline for new uploads, as it handles resizing, metadata extraction, and database insertion.

---

This modular design allows for flexible and extensible image analysis workflows.