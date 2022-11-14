import json
import websocket
import uuid
from datetime import datetime
from pathlib import Path


class ArtMode:
    def __init__(self, server) -> None:
        self.server = server
        self.conn = websocket.create_connection(
            f"ws://{self.server}:8001/api/v2/channels/com.samsung.art-app?name=ArtModeClient"
        )
        self.recv_data(message_event="ms.channel.connect")
        self.recv_data(message_event="ms.channel.ready")

    def recv_data(self, message_event="d2d_service_message", data_event=None):
        """
        Receive, parse, and (optionally) validate data. If `message_event` or `data_event` are supplied,
        an `Exception` will be raised if the actual message/data event values don't match the expected values.
        """
        data = self.conn.recv()
        if isinstance(data, str):
            obj = json.loads(data)
            if message_event:
                assert obj["event"] == message_event, f"expected {message_event}, found {obj['event']}"
            data = obj["data"]
            if isinstance(data, str):
                data = json.loads(data)
            if data_event:
                assert data["event"] == data_event, f"expected {data_event}, found {data['event']}"
            return data
        else:
            raise Exception(f"Expected {str}, found {type(data)}")

    def send_data(self, data, content=None):
        """
        Send data over the websocket. If the `content` parameter is supplied, the connection
        will send a binary websocket message (<length of json message><json string><content>).
        """
        data["id"] = str(uuid.uuid4())
        json_str = json.dumps(
            dict(method="ms.channel.emit", params=dict(event="art_app_request", to="host", data=json.dumps(data)))
        )
        if not content:
            return self.conn.send(json_str)
        else:
            json_len = len(json_str)
            json_len_bytes = json_len.to_bytes(2, "big")
            message = bytearray(json_len_bytes)
            message += json_str.encode("utf-8")
            message += content
            return self.conn.send_binary(message)

    def get_content_list(self):
        """
        Wrapper method for the `get_content_list` request message.
        """
        self.send_data(dict(request="get_content_list"))
        return json.loads(self.recv_data(data_event="content_list")["content_list"])

    def send_image(self, file):
        """
        Wrapper method for the `send_image` request message. `file` is a path to a jpg/png file.
        """
        path = Path(file)
        self.send_data(
            dict(
                request="send_image",
                matte_id="shadowbox_polar",
                file_type=dict(jpg="JPEG", png="PNG").get(path.suffix.lower(), "JPEG"),
                image_date=datetime.fromtimestamp(path.stat().st_ctime).strftime("%Y:%m:%d %H:%M:%S"),
                portrait_matte_id="flexible_polar",
            ),
            path.read_bytes(),
        )
        return self.recv_data(data_event="image_added")

    def delete_image_list(self, content_ids):
        """
        Wrapper method for the `delete_image_list` request message. Multiple `content_ids` can be supplied in one request.
        """
        self.send_data(
            dict(
                request="delete_image_list",
                content_id_list=[dict(content_id=content_id) for content_id in content_ids],
            )
        )
        return self.recv_data()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("server")
    subparsers = parser.add_subparsers(dest="command")
    parser_list = subparsers.add_parser("list")
    parser_upload = subparsers.add_parser("upload")
    parser_upload.add_argument("file")
    parser_delete = subparsers.add_parser("delete")
    parser_delete.add_argument("content_id", nargs="+")
    args = parser.parse_args()
    artmode = ArtMode(args.server)
    if args.command == "list":
        print(json.dumps(artmode.get_content_list(), indent=2))
    elif args.command == "upload":
        print(json.dumps(artmode.send_image(args.file), indent=2))
    elif args.command == "delete":
        print(json.dumps(artmode.delete_image_list(args.content_id), indent=2))
