import socket
import threading
import sys
import os

def generateBody(path):
    body = path.replace("/echo/", "")
    ans = (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
        f"{body}"
    )
    return ans.encode()

def handle_client(conn, address):
    with conn:
        # Get Data
        data = conn.recv(1024).decode()
        data_list = data.split("\r\n")  #Headers ,mid, body etc
        head = data.split("\r\n")[0].split(" ")
        path = head[1]
        req_type = head[0]
        print("Request Type = " , req_type)
        if path == "/":
            conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
        else:
            split_path = path.split("/")
            # ["" ,"echo","messgages"]
            if split_path[1] == "echo":
                ans = generateBody(path)
                print("Body - ", ans)
                conn.send(ans)
            elif split_path[1] == "user-agent":
                ua = data.split("\r\n")[2].split(" ")[1]
                print("User Agent - ", ua)
                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(ua)}\r\n\r\n"
                    f"{ua}"
                )
                conn.send(response.encode())
            elif split_path[1] == "files" and req_type == "GET":
                fileName = path[6:]
                print("File Name = " , fileName)
                directory = sys.argv[-1]

                if os.path.exists(directory + fileName):
                    file = open(directory + fileName , "rb")
                    body = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {os.path.getsize(directory + fileName)}\r\n\r\n"
                    conn.send(body.encode())
                    conn.send(file.read())
                    file.close()
                else:
                    conn.send(b"HTTP/1.1 404 Not Found \r\n\r\n")   #File Not Found
            
            elif split_path[1] == "files" and req_type == "POST":
                    filename = path[6:]
                    directory = sys.argv[-1]
                    location = directory + filename
                    print("Writing to location " , location)
                    with open(location , "w") as f:
                        #print("Writing Data " , data_list[-1])
                        f.write(data_list[-1])
                        f.close()
                    conn.send(b"HTTP/1.1 201 OK \r\n\r\n")

            else:
                conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        conn, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()

if __name__ == "__main__":
    main()
