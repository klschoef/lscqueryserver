# Images Server

The **Images Server** is a lightweight server for serving images (required for the frontend) using `nginx` in a Docker container. It uses `docker-compose` for setup and deployment.

---

## **Requirements**
- Docker and Docker Compose must be installed on your system.

---

## **Setup**

### **1. Configure the Environment**
1. Copy the example environment file and adjust the configuration:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with the following key parameters:
    - `IMAGES_PATH`: Absolute path to the folder containing the images. This path must be absolute because it is mounted into the Docker container.
    - `IMAGES_SERVER_PORT`: Port that Docker maps to the `nginx` server.

---

## **Usage**

### **1. Start the Server**
Run the following command to start the `nginx` server in a Docker container:
```bash
docker compose up -d
```

### **2. Monitor Logs**
To monitor the logs of the running container, use:
```bash
docker compose logs -f
```

---

## **Notes**
- The `docker-compose.yml` and `nginx.conf` files do not require any modifications.
- Ensure the `IMAGES_PATH` in the `.env` file points to the correct absolute path of your images folder.