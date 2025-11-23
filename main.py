
import mimetypes
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from pymongo import MongoClient


HTTP_HOST = '0.0.0.0'
HTTP_PORT = 3000
SOCKET_HOST = '0.0.0.0'
SOCKET_PORT = 5000
MONGO_URI = "mongodb://mongo:27017/"  

BASE_DIR = Path(__file__).parent.joinpath('front')


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr = urlparse(self.path)
        if pr.path == '/':
            self.send_html_file('index.html')
        elif pr.path == '/message.html':
            self.send_html_file('message.html')
        else:
            file_path = BASE_DIR.joinpath(pr.path[1:])
            if file_path.exists():
                self.send_static(file_path)
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        pr = urlparse(self.path)
        if pr.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.send_data_to_socket(post_data)
            self.send_response(302)
            self.send_header('Location', '/message.html')
            self.end_headers()
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(BASE_DIR.joinpath(filename), 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self, file_path, status=200):
        self.send_response(status)
        mimetype, _ = mimetypes.guess_type(file_path)
        if mimetype:
            self.send_header('Content-type', mimetype)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(file_path, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_data_to_socket(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((SOCKET_HOST, SOCKET_PORT))
                sock.sendall(data)
            except socket.error as e:
                print(f"Failed to connect or send data to socket server: {e}", flush=True)


def run_http_server():
    httpd = HTTPServer((HTTP_HOST, HTTP_PORT), MyHTTPRequestHandler)
    print(f"HTTP server running on http://{HTTP_HOST}:{HTTP_PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def run_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SOCKET_HOST, SOCKET_PORT))
    server_socket.listen(5)
    print(f"Socket server running on {SOCKET_HOST}:{SOCKET_PORT}", flush=True)

    try:
        client = MongoClient(MONGO_URI)
        db = client.messages_db
        collection = db.messages
        print("MongoDB connected.", flush=True)

        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}", flush=True)
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    try:
                        data_str = data.decode('utf-8')
                        data_dict = parse_qs(data_str)
                        
                        username = data_dict.get('username', [''])[0]
                        message = data_dict.get('message', [''])[0]

                        if username and message:
                            message_doc = {
                                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                'username': username,
                                'message': message
                            }
                            collection.insert_one(message_doc)
                            print(f"Saved to DB: {message_doc}", flush=True)
                        else:
                            print(f"Received empty username or message. Data: {data_dict}", flush=True)

                    except (UnicodeDecodeError, KeyError, IndexError) as e:
                        print(f"Error processing data: {e}", flush=True)
                    except Exception as e:
                        print(f"An unexpected error occurred in data processing: {e}", flush=True)
    except Exception as e:
        print(f"Socket server crashed: {e}", flush=True)



if __name__ == '__main__':
    http_process = Process(target=run_http_server)
    socket_process = Process(target=run_socket_server, daemon=True)

    http_process.start()
    socket_process.start()
    
    http_process.join()


