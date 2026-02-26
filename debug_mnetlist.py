#!/usr/bin/env python3
"""Debug script to see MnetList response from the controller."""
import sys
import urllib.request

if len(sys.argv) < 2:
    print("Usage: python3 debug_mnetlist.py <controller-ip>")
    sys.exit(1)

host = sys.argv[1]
url = f"http://{host}/servlet/MIMEReceiveServlet"

payload = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<Packet><Command>getRequest</Command>"
    "<DatabaseManager>"
    "<ControlGroup><MnetList /></ControlGroup>"
    "</DatabaseManager></Packet>"
)

print(f"POST {url}")
print(f"Payload: {payload}\n")

req = urllib.request.Request(url, data=payload.encode(), headers={"Content-Type": "text/xml"})
resp = urllib.request.urlopen(req)
print(f"Status: {resp.status}")
print(f"Response:\n{resp.read().decode()}")
