# Evaluation Framework

The **Evaluation Framework** is a Python-based system for creating and running evaluation projects. It processes queries using the `lscqueryserver` and calculates metrics based on the results. The framework supports flexible configurations for different query transformations and search configurations.

---

## **Requirements**
- Python 3.8 or higher.
- A running instance of the `lscqueryserver` (refer to its `README` for setup).

---

## **Setup**

### **1. Install Python**
Ensure Python 3.8 or higher is installed on your system.

### **2. Configure the Environment**
1. Copy the example environment file and adjust the configuration:
   ```bash
   cp .env.example .env
   ```
2. For standard usage, no changes are required. The file includes:
   - `VENV_NAME`: Name of the virtual environment.
   - `SHARED_LIB_PATH`: Path to the shared library.

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

## **Creating an Evaluation Project**

### **1. Project Folder**
Create a project folder (e.g., in `evaluation_projects`) containing a `config.yml` file. This file defines the evaluation configuration.

### **2. Configuration File**
The `config.yml` file specifies the following:

#### **Key Parameters**
1. **`lsc_server_url`**: URL of the running `lscqueryserver` instance.
2. **`topic_files`**: List of JSON files containing queries and answers. Here you can add multiple files with different query structures, or to test different filters against each other. Each file has the following format:
   ```json
   [
       {
           "query_name": "query_id",
           "hints": ["hint1", "hint2", "hint3", "hint4", "hint5", "hint6"],
           "answers": ["answer1.jpg", "answer2.jpg", ...]
       },
   ...
   ]
   ```
3. **`steps`**: List of search configurations. Each step defines how queries are processed (e.g., using FAISS with specific models or SOLR). Here you can test different clip models or solr cores against each other. Each step has the following format:
   ```yaml
   - name: "step_name"
     type: "faiss" or "solr"
     faiss:
       model: "model_name"
       weights: "weights_name"
       index_path: "path_to_index"
     solr:
       core: "core_name"
   ```

#### **Example `config.yml`**
```yaml
lsc_server_url: "http://localhost:8000"
topic_files:
  - "topics/keywords.json"
  - "topics/filtered.json"
  - "topics/optimized.json"
steps:
  - name: "clip_model_1"
    type: "faiss"
    faiss:
      model: "ViT-H-14"
      weights: "laion2b_s32b_b79k"
      index_path: "../shared/faiss/index_1.faiss"
  - name: "clip_model_2"
    type: "faiss"
    faiss:
      model: "ViT-B-32"
      weights: "laion400m_e32"
      index_path: "../shared/faiss/index_2.faiss"
  - name: "solr_search"
    type: "solr"
    solr:
      core: "descriptions_core"
```

### **Possible Parameters for Steps in the `config.yml`**

#### **Step Parameters**
| Parameter              | Type            | Default Value       | Description                                                        |
|------------------------|-----------------|---------------------|--------------------------------------------------------------------|
| `type`                 | `str`           | None                | Type of the step (`faiss` or `solr`).                              |
| `name`                 | `Optional[str]` | `None`              | Name of the step (used for identification and results foldername). |
| `stop_if_no_results`   | `bool`          | `True`              | Whether to stop processing if no results are found.                |
| `prefix`               | `Optional[str]` | `None`              | Prefix to add to the results folder name.                          |
| `postfix`              | `Optional[str]` | `None`              | Postfix to add to the results folder anme.                         |
| `faiss`                | `Optional[FaissStepConfig]` | `None` | FAISS-specific configuration (if `type` is `faiss`).               |
| `solr`                 | `Optional[SolrStepConfig]`  | `None` | SOLR-specific configuration (if `type` is `solr`).                 |

---

#### **FAISS Step Configuration (`faiss`)**
| Parameter              | Type   | Description                                  |
|------------------------|--------|----------------------------------------------|
| `path`                 | `str`  | Path to the FAISS index folder.              |
| `model`                | `str`  | Name of the OpenCLIP model to use.           |
| `weights`              | `str`  | Pre-trained weights for the specified model. |

---

#### **SOLR Step Configuration (`solr`)**
| Parameter              | Type   | Description                                                                 |
|------------------------|--------|-----------------------------------------------------------------------------|
| `core`                 | `str`  | Name of the SOLR core to use for the search.                                |

---

## **Running an Evaluation**

### **Command**
Run the evaluation using the `evaluate.py` script:
```bash
python evaluate.py <project_folder> --config_file_name <config_file>
```

#### **Parameters**
| Parameter              | Default Value | Description                                      |
|------------------------|---------------|--------------------------------------------------|
| `project_folder`       | None          | Path to the project folder.                     |
| `--config_file_name`   | `config.yml`  | Name of the configuration file in the folder.   |

#### **Example**
```bash
python evaluate.py evaluation_projects/first.lsceval
```

---

## **How It Works**

1. **Configuration Parsing**:
   - The `config.yml` file is read and transformed into Python classes.

2. **Stage Execution**:
   - The framework executes stages defined in `core/stages`. New stages can be added by inheriting from `BaseStage` and appending them to the `stages` array in `evaluate.py`.

3. **Query Processing**:
   - All combinations of `topic_files` and `steps` are executed.
   - For each combination, all hints from all queries in the `topic_files` are processed using the corresponding search configuration (`step`) via the `lscqueryserver`.
   - Results are saved in the project folder under `results/single_results/prefix_<step_name>_postfix/<topic_file_name>.json`.

4. **Summary Generation**:
   - The `summary_stage` calculates metrics (e.g., H@K) from the results, and store them into the individual result folders.
   - Summaries are saved in the `results/summaries` folder in both CSV and LaTeX formats.

---

## **Metrics**
- **H@K**: Hit rate at K.
- **Aggregated H@K**: Aggregated version of H@K across all queries.

For more details on the metrics, refer to the project's Master Thesis.