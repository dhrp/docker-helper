#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import pprint
	
	
# ===============================
# Getting docker info
# ===============================

class DockerHandler(BaseHTTPRequestHandler):
    
    
    def do_GET(self):
        
        try:
            if self.path.endswith("json/"):
                """
                Return all the containers inspection data
                """
                
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                containerlist = self.getContainerList()
                containers = []

                i = 0
                for container in containerlist:
                    if 'mongod' in container[2]:
                        containers.append(self.getInspect(container[0]))
                        i += 1

                self.wfile.write(json.dumps(containers))
                return

            if self.path.endswith("json/rsconf/"):
                """
                Path specific to generate mongoDB replication configuration data
                """
                
                rsconf = {
                  "_id": "rs0",
                  "members": []
                } 
            
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()

                containerlist = self.getContainerList()
                containers = []
                i = 0
                for container in containerlist:
                    if 'mongod' in container[2]:
                        container_info = self.getInspect(container[0])
                        networksettings = container_info["NetworkSettings"]
                        privateipaddress = networksettings["IpAddress"]
                        privateport = networksettings["PortMapping"].keys()[0]   

                        rsconf["members"].append({"_id": int(i), "host": str(privateipaddress + ":" + privateport) }) 
                        i += 1

                self.wfile.write(json.dumps(rsconf))
                return

            else:
                """
                Default, print the equivalent of a homepage
                """

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                self.wfile.write("<h1>Information about Docker containers</h1>")     
                
                containerlist = self.getContainerList()
                containers = []
                i = 0
                for container in containerlist:
                    if 'mongod' in container[2]:
                        container_info = self.getInspect(container[0])
                        networksettings = container_info["NetworkSettings"]
                        privateipaddress = networksettings["IpAddress"]
                        privateport = networksettings["PortMapping"].keys()[0]
                        
                        self.wfile.write("<h2>node</h2>")
                        
                        for key, value in networksettings["PortMapping"].iteritems():
                            self.wfile.write("<pre>Hostname {0}:{1} -> {2}</pre>".format(privateipaddress, key, value))
                        
#                         self.wfile.write("<pre>Hostname {0}:{1} -> {2}</pre>".format(privateipaddress, privateport, networksettings["PortMapping"][privateport]))
                        i += 1
                    if 'express' in container[1]:
                        container_info = self.getInspect(container[0])
                        networksettings = container_info["NetworkSettings"]
                        privateipaddress = networksettings["IpAddress"]

                        self.wfile.write("<h2>express</h2>")
                        for key, value in networksettings["PortMapping"].iteritems():
                            self.wfile.write("<pre>Hostname {0}:{1} -> {2}</pre>".format(privateipaddress, key, value))


#                         self.wfile.write("<pre>Hostname {0}:{1} -> {2}</pre>".format(privateipaddress, privateport, networksettings["PortMapping"][privateport]))
                        
                        i += 1


                return
            
        except IOError:
            self.send_error(500,'Server error: %s' % self.path)

    def getContainerList(self):
        call = subprocess.Popen(["docker", "ps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = call.communicate()
        result = out.split('\n')

        containerlist = []
        i = 0
        for row in result:
            item = row.split('   ')
            if len(item) > 2:
                containerlist.append(item)

        return containerlist


    def getInspect(self, id):
        
        call = subprocess.Popen(["docker", "inspect", id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err, = call.communicate()
       
        container_info = json.loads(out)

        return container_info         

	
# ===============================
# HTTP Server
# ===============================

print "starting http server"

def main(): 
    try: 
        server = HTTPServer(('', 8888), DockerHandler)
        print 'started http server'
        server.serve_forever()
    except KeyboardInterrupt:
        print " keyboard interrupt, stopping server"
        server.socket.close()
		
if __name__ == '__main__':
    main()