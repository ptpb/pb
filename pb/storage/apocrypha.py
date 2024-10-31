from typing import *

from contextlib import closing
from http import client
import ssl

from pb.storage import types

host = "localhost"
port = 10000

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

connect = lambda: client.HTTPSConnection(host, port, context=ssl_context)


def read(name: str) -> Tuple[types.READ, bytes]:
    with closing(connect()) as connection:
        connection.request(
            method="GET",
            url="/" + name,
        )
        response = connection.getresponse()
        if response.code == 200:
            return types.READ.FOUND, response.read()
        elif response.code == 404:
            return types.READ.NOT_FOUND, b""
        else:
            return types.READ.ERROR, b""


def write(content: bytes) -> Tuple[types.READ, types.PasteLabel]:
    with closing(connect()) as connection:
        connection.request(
            method="POST",
            url="/",
            body=content,
        )
        response = connection.getresponse()
        if response.code == 200:
            return types.WRITE.CREATED, response.read().decode('utf-8')
        else:
            return types.WRITE.ERROR, ""
