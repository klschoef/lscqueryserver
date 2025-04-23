# Solr Server

The **Solr Server** is a search engine used for indexing and querying descriptions. It is deployed using Docker and configured via the `docker-compose.solr.yml` file.

---

## **Requirements**
- Docker and Docker Compose must be installed on your system.

---

## **Setup**

### **1. Start the Solr Server**
Run the following command to start the Solr server in the background:
```bash
docker compose -f docker-compose.solr.yml up -d
```

### **2. Monitor Logs**
To monitor the logs of the running Solr container, use:
```bash
docker compose -f docker-compose.solr.yml logs -f
```

---

## **Data Management**

### **1. Writing Descriptions to Solr**
Use the helper scripts in the `helpers` folder to write descriptions from MongoDB to Solr. Refer to the script documentation for usage details.

### **2. Loading Backups**
To load a backup, replace the `.solrdata` folder with the backup data. The `.solrdata` folder is mapped to the Solr container and contains all indexed data.

---

## **Notes**
- The `docker-compose.solr.yml` file does not require any modifications.
- The `.solrdata` folder is mapped to the Solr container's data directory (`/var/solr`).