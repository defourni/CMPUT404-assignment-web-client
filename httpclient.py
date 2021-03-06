#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

#----------------------------------------------------------------------

#Copyright 2020 Dexter Fournier
#
#  HTTPClient class used to send get and post requests to a given url. prints to stdout the body of the response and returns in an object both the body and HTTP code.
#
#Licensed under the Apache License, Version 2.0 (the "License");   
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

    #http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import sys
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
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(host)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        #split body and head
        raw_parts = data.split('\r\n\r\n')
        #extract code
        head_lines = raw_parts[0].split('\n')
        code = head_lines[0].split()[1]
        return code

    def get_headers(self,data):
        raw_parts = data.split('\r\n\r\n')
        #extract code
        head_lines = raw_parts[0].split('\n')
        return head_lines

    def get_body(self, data):
        raw_parts = data.split('\r\n\r\n')
        #extract code
        body = raw_parts[1]
        return body
    
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
    
    def parse_url(self, url):
        #parse URL
        #remove http://
        if (url[:7] == "http://") or (url[:8] == "https://"):
            url = url.split('//')[1]
        #separate path and host
        if '/' in url:
            host = url.split('/')[0]
            #path could very easily have more than one /, so take the rest of it.
            path = url[len(host):]
        else:
            host = url
            path = '/'
        #separate port from host
        if ':' in host:
            port = host.split(':')[1]
            host = host[:-(len(port)+1)]
        else:
            #80 is default TCP port
            port = 80
        return(host,port,path)
        

    def GET(self, url, args=None):
        if args:
            print("no args handler for GET")

        host,port,path = self.parse_url(url)
        
        self.connect(host, int(port))
        headers = '\r\nUser-Agent: curl/7.47.0\r\nAccept: text/html'
        payload = 'GET ' + path + ' HTTP/1.1\r\nHost: ' + host + headers +'\r\n\r\n'
        self.sendall(payload)
        
        full_data = self.recvall(self.socket)
        self.close()
    
        code = int(self.get_code(full_data))
        body = self.get_body(full_data)
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #args = {'a':'aaaaaaaaaaaaa',
                #'b':'bbbbbbbbbbbbbbbbbbbbbb',
                #'c':'c',
                #'d':'012345\r67890\n2321321\n\r'} 
        
        host,port,path = self.parse_url(url)
        if args:
            encoded_content = ""
            for a in args:
                encoded_content += (a + '=' + args[a] + '&')
            #remove trailing ampersand
            encoded_content = encoded_content[:-1]
        else:
            #still needs something in encoded content since Content-Length requires this to be not null ( becomes 0 instead)
            encoded_content = ""
        
        self.connect(host, int(port))
        #using curl as a user agent since some websites didn't like no user agent.
        headers = '\r\nUser-Agent: curl/7.47.0\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: ' + str(len(encoded_content))
        payload = 'POST ' + path + ' HTTP/1.1\r\nHost: ' + host + headers +'\r\n\r\n'
        
        payload = payload + encoded_content
        
        self.sendall(payload)
        
        full_data = self.recvall(self.socket)
        self.close()
        #print(full_data)
        code = int(self.get_code(full_data))
        body = self.get_body(full_data)
        print(body)
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
