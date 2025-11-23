# GoIT Computer Science Homework 06 

Simple Web App with TCP Socket and MongoDB

This project is a simple web application that demonstrates a message exchange system using:

- An **HTTP server** to display a web page with a form.
- A **TCP server** to receive messages from the HTTP server.
- **MongoDB** for message history storage.
- **Docker Compose** to run the entire infrastructure with a single command.

---

### 🔧 Tech Stack
- Python 3.9
- Standard Library HTTP Server
- Standard Library TCP Socket Server
- MongoDB 7
- PyMongo
- Docker + Docker Compose
- HTML/CSS (for static files)

---

### How to Run with Docker

1. **Prerequisites**

   - [Docker]
   - [Docker Compose]

2. **Run the Services**

   From the project root, run:
   ```bash
   docker compose up -d --build
   ```

   - `--build`: Rebuilds the application image from the source code.
   - `-d`: Runs containers in detached mode.

   Check the container status:
   ```bash
   docker compose ps
   ```

3. **Check the Application**

   - The web server is available at [http://localhost:3000].
   - The message form is at [http://localhost:3000/message.html].

   Submit a message through the form. It will be saved to MongoDB.

4. **View Logs**

   To see the application logs:
   ```bash
   docker compose logs -f app
   ```

---

### Viewing Data in MongoDB

1. **Access the MongoDB container**:
   ```bash
   docker exec -it goit-cs-hw-06-mongo-1 mongosh
   ```

2. **Inside the `mongosh` console, run**:
   ```javascript
   use messages_db;
   db.messages.find().pretty();
   ```

---

### Project Structure
```
goit-cs-hw-06/
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
└── front/
    ├── error.html
    ├── index.html
    ├── logo.png
    ├── message.html
    └── style.css
```
