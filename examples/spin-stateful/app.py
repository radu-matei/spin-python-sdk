"""A stateful counter component.

The runtime keeps one live instance per (component, instance-id) pair and
routes requests to it via the spin.alt addressing scheme. The count lives in
memory across requests for the lifetime of the instance.
"""

from spin_sdk.stateful import stateful_component, Request, Response


@stateful_component
class Counter:
    def __init__(self, id: str):
        # Called once when the runtime first activates this instance.
        self.id = id
        self.count = 0

    def suspend(self):
        # Called before the runtime suspends this instance (idle timeout).
        print(f"suspending counter {self.id} at {self.count}")

    def handle_request(self, request: Request) -> Response:
        self.count += 1
        body = f"counter {self.id} = {self.count}\n".encode()
        return Response(200, {"content-type": "text/plain"}, body)
