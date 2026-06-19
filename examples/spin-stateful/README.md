# Stateful counter (Python)

A [stateful component](https://spinframework.dev): a long-lived, addressable
Wasm instance. The runtime keeps one live instance per `(component, instance-id)`
pair, calls the lifecycle hooks, and routes requests to it via the `spin.alt`
addressing scheme. The count lives in memory across requests for the lifetime of
the instance.

```python
from spin_sdk.stateful import stateful_component, Request, Response

@stateful_component
class Counter:
    def __init__(self, id: str):       # called once on activation
        self.id = id
        self.count = 0

    def suspend(self):                  # called before idle suspension (optional)
        print(f"suspending counter {self.id} at {self.count}")

    def handle_request(self, request: Request) -> Response:
        self.count += 1
        return Response(200, {"content-type": "text/plain"},
                        f"counter {self.id} = {self.count}\n".encode())
```

Stateful components are not publicly routable; pair this with a router component
that forwards `GET /<id>` to `https://spin.alt/component/counter/<id>/` (see the
Rust SDK's `stateful-counter` example for a complete router + counter app).

## Building

> **Tooling requirement.** Stateful components export the WASI Preview 3 HTTP
> handler (`wasi:http/handler@0.3.0-rc-2026-03-15`), whose bodies are
> `stream<u8>`. This needs a `componentize-py` with WASI 0.3 support
> ([bytecodealliance/componentize-py#225](https://github.com/bytecodealliance/componentize-py/pull/225)),
> which is newer than the 0.17.2 pinned in `CONTRIBUTING.md`. Build it from that
> branch until a release is available.

```bash
componentize-py --all-features componentize \
    -m spin_sdk=spin-stateful-http \
    app -o app.wasm
```

`-m spin_sdk=spin-stateful-http` selects the stateful world from the SDK's
`componentize-py.toml` (which exposes several worlds), and `--all-features`
enables the `@since`/`@unstable` WASI annotations. If the SDK isn't installed in
the active environment, add `-p <path-to>/spin-python-sdk/src`.

## Running end-to-end

Pair this counter with a router (e.g. the Rust SDK's `stateful-counter` router)
and run on a Spin v4 host:

```bash
spin up --stateful-idle-timeout 30s
curl localhost:3000/alice   # counter alice = 1
curl localhost:3000/alice   # counter alice = 2
curl localhost:3000/bob     # counter bob = 1   (isolated per instance)
```
