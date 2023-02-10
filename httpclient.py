#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Daryna Chernyavska
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# References:
#   Author: Regexident https://stackoverflow.com/users/227536/regexident
#   Title: regex find all the strings preceded by = and ending in &
#   https://stackoverflow.com/a/8141383
#
#   Author: Fahad Naveed
#   https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2196981


# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys, time
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(re.search("HTTP\/\d\.?\d?\s+(\d{3})\s", data).group(1))

    def get_headers(self,data):
        return None

    def get_body(self, data):
        last = data.rfind("\r\n\r\n")
        return data[last+4: len(data)]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def getHost(self, netloc):
        if netloc.find(":") == -1:
            return netloc
        else:
            parsedNetloc = re.search("(.+):(.+)", netloc)
            return parsedNetloc.group(1)

    def getPort(self, netloc):
        if netloc.find(":") == -1:
            return 80
        else:
            parsedNetloc = re.search("(.+):(.+)", netloc)
            return int(parsedNetloc.group(2))

    def GET(self, url, args=None):
        parsedUrl = urllib.parse.urlsplit(url)
        if parsedUrl.scheme != "http": 
            raise ValueError("Error: no url scheme provided")
        if parsedUrl.path == "":
            parsedUrl = parsedUrl._replace(path="/")
        self.connect(self.getHost(parsedUrl.netloc), self.getPort(parsedUrl.netloc))
        if parsedUrl.query=='' and args==None:
            request = "GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: me\r\nConnection: keep-alive\r\nAccept: */*\r\n\r\n" % (parsedUrl.path, self.getHost(parsedUrl.netloc))
        else:
            if args==None:
                queryPart = parsedUrl.query
            else:
                if type(args) == str:
                    queryPart = args
                else:
                    queryPart = urllib.parse.urlencode(args)
            request = "GET %s?%s HTTP/1.1\r\nHost: %s\r\nUser-Agent: me\r\nConnection: keep-alive\r\nAccept: */*\r\n\r\n" % (parsedUrl.path, queryPart, self.getHost(parsedUrl.netloc))
        self.sendall(request)
        if parsedUrl.netloc == "slashdot.org":
            time.sleep(1)
        self.socket.shutdown(socket.SHUT_WR)
        result = self.recvall(self.socket).strip()
        self.socket.close()
        code = self.get_code(result)
        body = self.get_body(result)
        print(result)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsedUrl = urllib.parse.urlsplit(url)
        if parsedUrl.scheme != "http": 
            raise ValueError("Error: no url scheme provided")
        if parsedUrl.path == "":
            parsedUrl = parsedUrl._replace(path="/")
        self.connect(self.getHost(parsedUrl.netloc), self.getPort(parsedUrl.netloc))
        if args == None:
            request = "POST {} HTTP/1.1\r\nHost: {}\r\nUser-Agent: me\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\n\r\n"
            request = request.format(parsedUrl.path, self.getHost(parsedUrl.netloc))
        else:
            requestBody = urllib.parse.urlencode(args)
            request = "POST {} HTTP/1.1\r\nHost: {}\r\nUser-Agent: me\r\nConnection: keep-alive\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}"
            request = request.format(parsedUrl.path, self.getHost(parsedUrl.netloc), len(requestBody), requestBody)
        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        result = self.recvall(self.socket).strip()
        print(result)
        self.socket.close()
        code = self.get_code(result)
        body = self.get_body(result)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
