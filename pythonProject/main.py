import mimetypes
import urllib.parse
import json
import logging
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from datetime import datetime
from pathlib import Path
from jinja2 import Environment,FileSystemLoader

Base_dir = Path()
BUFFER_SIZE = 1024
HTTP_Port = 3000
HTTP_Host = '0.0.0.0'
SOCKET_Host = '127.0.0.1'
SOCKET_PORT = 5000

jinja = Environment(loader=FileSystemLoader('.'))
class Goitframework(BaseHTTPRequestHandler):
    def do_GET(self):
        route = (urllib.parse.urlparse(self.path))
        match route.path:
            case '/':
                self.send_HTML('index.html')
            case '/contact':
                self.send_HTML('message.html')
            case '/blog':
                self.render_template('blog.jinja')
            case _:
                file = Base_dir.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_HTML('error.html', 404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_Host, SOCKET_PORT))
        client_socket.close()

        self.send_response(302)
        self.send_header('Location', '/message.html')
        self.end_headers()

    def send_HTML(self, filename, status_code = 200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def render_template(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def send_static(self, filename, status_code = 200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')

        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

def save_data_from_form(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        time_stamp = datetime.now().isoformat()
        file_path = Path('data/data.json')
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                ex_data = json.load(f)
        else:
            ex_data = {}
        ex_data[time_stamp] = parse_dict
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(ex_data, file, ensure_ascii=False, indent=4)
    except ValueError as er:
        logging.error(er)
    except OSError as err:
        logging.error(err)

def run_socket_server(host,port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info('Starting socket-server')
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info(f'Socket received {address}: {msg}')
            save_data_from_form(msg)
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()


def run_http_server(host,port):
    address = (host,port)
    http_server = HTTPServer(address,Goitframework)
    logging.info('Starting http-server')
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    server= Thread(target=run_http_server, args=(HTTP_Host, HTTP_Port))
    server.start()

    server_socket = Thread(target=run_socket_server, args=(SOCKET_Host,SOCKET_PORT))
    server_socket.start()