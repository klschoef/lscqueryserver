# LifeXplore Backend System

The **LifeXplore Backend System** is a modular project designed to process and evaluate queries using a WebSocket-based Python application (`lscqueryserver`) 
and several submodules. Use the [official LifeXplore frontend application](https://github.com/klschoef/lifexplore) or develop your own. 
For more details, refer to the [paper](https://dl.acm.org/doi/abs/10.1145/3643489.3661123). Below is an overview of the system and its components.

---

## **Main Project: `lscqueryserver`**
The `lscqueryserver` (app folder) is the core Python application that processes queries and returns results. It uses WebSocket communication and integrates with the following submodules. [Read more](app/README.md)

## **Submodules**
1. **`clip`**
   - Handles CLIP (Contrastive Language–Image Pretraining) queries for natural language processing.
   - Supports FAISS indices for efficient similarity search. [Read more](clip/README.md)

2. **`mongo`**
   - Provides a Docker container and helper scripts for managing the MongoDB database.
   - Includes functionality for importing database backups. [Read more](mongo/README.md)

3. **`solr`**
   - Includes a Docker Compose file to set up a SOLR instance for searching descriptions.
   - Optional: Use the SOLR Docker Compose script to initialize and configure a SOLR instance. [Read more](solr/README.md)

4. **`images_server`**
   - Provides a Docker Compose file to set up an NGINX instance for hosting images. [Read more](images_server/README.md)

5. **`analysis_server`**
   - A standalone server that communicates with the `lscqueryserver` to add new images.
   - Features:
      - Upload server.
      - File watcher for uploads.
      - Customizable analysis framework with support for additional processing pipelines. [Read more](analysis_server/README.md)

6. **`evaluation`**
   - A framework for creating evaluation projects.
   - Communicates directly with the `lscqueryserver` to perform evaluations based on a `config.yaml` file.
   - Automates testing of various models (e.g., OpenCLIP), query structures, and filters. [Read more](evaluation/README.md)

7. **`helpers`**
   - Provides utility scripts for tasks such as managing SOLR or database dumps. [Read more](helpers/README.md)

8. **`shared`**
   - Contains shared code used across multiple modules.
   - Includes CLIP logic and FAISS index storage for the `clip` server. [Read more](shared/README.md)

---

## **Setup and Workflow**

### **Prerequisites**
1. Install **Docker**.
2. Install **Python**.

### **Setup Steps**
1. **CLIP Server**
   - Configure and start the CLIP server with a Python environment.
   - Optionally, use an existing FAISS index. [Read more](clip/README.md)

2. **MongoDB**
   - Configure and start the MongoDB instance using Docker Compose.
   - Import a database backup if available. [Read more](mongo/README.md)

3. **Image Server**
   - Configure and start the image server using Docker Compose. [Read more](images_server/README.md)

4. **LSC Query Server**
   - Configure and start the `lscqueryserver` using Docker Compose. [Read more](app/README.md)

### **Optional Steps**
- **SOLR**
   - Set up and start a SOLR instance using Docker Compose.
   - Import a backup if needed. [Read more](README.solr.md)

- **Analysis Server**
   - Configure and start the `analysis_server` to add new content or extend existing pipelines. [Read more](analysis_server/README.md)

---

## **Additional Information**
Each module includes a dedicated `README` file with detailed instructions for configuration and usage. Refer to these files for module-specific setup and advanced configurations.

---

This modular design allows for flexibility in deployment and customization, making it easy to extend or adapt the system to specific requirements.

## Documentation

This documentation provides an overview of the LifeXplore Backend System and its components. For detailed instructions and setup information, refer to the individual `README` files included in each module.

---

## New Format for FAISS Indices

### **Overview**
The new format for FAISS indices was designed to save storage space and optimize loading times. Instead of a single CSV file, the new format uses a folder containing two files:

1. **`index.faiss`**
   - Stores the FAISS index in binary format.
   - This format is more efficient in terms of storage and loading performance.

2. **`index.labels`**
   - Contains the labels as strings.
   - This file allows easy mapping of labels to the stored features.

---

### **Comparison with the Old Format**
- **Old Format:**
  - A single CSV file storing both labels and feature sets in ASCII format.
  - This format was storage-intensive and resulted in longer loading times.

- **New Format:**
  - A folder containing the above-mentioned files (`index.faiss` and `index.labels`).
  - Reduces storage requirements and improves performance.

---

### **Migrating Old Index Files**
To convert old CSV-format index files to the new FAISS format, use the script `helpers/migration/csv_index_to_faiss.py`.

#### **Migration Steps:**
1. Copy the `.env.example` file to the `helpers/migration` folder.
2. Run the setup script and activate the virtual environment:
   ```bash
   ./setup.sh
   source .venv/bin/activate
   ```
3. Execute the migration script:
   ```bash
   python helpers/migration/csv_index_to_faiss.py <csv_filename> -f <foldername>
   ```
    - **`<csv_filename>`**: Path to the CSV file containing the old index data.
    - **`<foldername>`**: (Optional) Folder name to save the new files. Defaults to the CSV filename with a `.faiss` extension.

After running the script, a folder containing the `index.faiss` and `index.labels` files will be created.

---

For more details on using and configuring the FAISS index, refer to the `README` files in the respective modules.