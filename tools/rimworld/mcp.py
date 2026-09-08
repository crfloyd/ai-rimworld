"""Streamable HTTP MCP, with no automatic replay of tool requests."""

import json
from . import __version__
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from .core import Error, identifier


PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26")


class Uncertain(Error):
    """The request may have reached the server. Reconcile before another mutation."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def endpoint_key(endpoint):
    p = urllib.parse.urlsplit(endpoint)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise Error("Use an HTTP(S) MCP endpoint without credentials, query or fragment.")
    host = p.hostname.lower()
    if host in ("localhost", "127.0.0.1", "::1"):
        host = "loopback"
    return f"{p.scheme}://{host}:{p.port or (443 if p.scheme == 'https' else 80)}{p.path.rstrip('/') or '/'}"


class Client:
    def __init__(self, endpoint, session=None, opener=None, timeout=55):
        endpoint_key(endpoint)
        self.endpoint = endpoint
        self.session = dict(session or {})
        self.opener = opener or urllib.request.build_opener(NoRedirect()).open
        self.timeout = timeout
        self.notifications = []

    def rpc(self, method, params=None, request_id=None, notification=False):
        rid = request_id or identifier("rpc-")
        body = {"jsonrpc": "2.0", "method": method}
        if not notification:
            body["id"] = rid
        if params is not None:
            body["params"] = params
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
        if self.session.get("session_id"):
            headers["Mcp-Session-Id"] = self.session["session_id"]
        if self.session.get("protocol"):
            headers["MCP-Protocol-Version"] = self.session["protocol"]
        request = urllib.request.Request(self.endpoint, json.dumps(body).encode(), headers)
        try:
            with self.opener(request, timeout=self.timeout) as response:
                sid = response.headers.get("Mcp-Session-Id")
                if sid:
                    self.session["session_id"] = sid
                if notification and response.status == 202:
                    return None
                content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
                if content_type == "text/event-stream":
                    result = self._sse(response, rid)
                else:
                    result = json.load(response)
        except (OSError, ValueError, urllib.error.URLError) as exc:
            raise Uncertain(f"{method} response unavailable ({exc}). No request was retried.") from exc
        if not isinstance(result, dict) or result.get("id") != rid:
            raise Uncertain("Response ID or shape does not match the request; no retry.")
        if "error" in result:
            raise Error("MCP rejected request: " + json.dumps(result["error"]))
        if "result" not in result:
            raise Uncertain("Response contains no result; request outcome unknown.")
        return result

    def _sse(self, response, rid):
        data = []
        for raw_line in response:
            line = raw_line.decode("utf-8").rstrip("\r\n")
            if line.startswith("id:"):
                self.session["last_event_id"] = line[3:].lstrip()
            elif line.startswith("data:"):
                data.append(line[5:].lstrip())
            elif not line and data:
                payload = json.loads("\n".join(data))
                data = []
                messages = payload if isinstance(payload, list) else [payload]
                for message in messages:
                    if message.get("id") == rid and ("result" in message or "error" in message):
                        return message
                    # This client advertises no sampling/elicitation capabilities.
                    if "method" in message and "id" in message:
                        raise Uncertain("Server requested an unsupported client capability.")
                    self.notifications.append(message)
        raise Uncertain("SSE ended before the matching response. It did not cancel the request.")

    def initialize(self):
        response = self.rpc("initialize", {
            "protocolVersion": PROTOCOLS[0], "capabilities": {},
            "clientInfo": {"name": "ai-rimworld", "version": __version__}})
        result = response["result"]
        protocol = result.get("protocolVersion")
        if protocol not in PROTOCOLS:
            raise Error(f"Unsupported negotiated protocol {protocol!r}. Use a compatible MCP client.")
        self.session.update(protocol=protocol, server=result.get("serverInfo"),
                            capabilities=result.get("capabilities", {}))
        self.rpc("notifications/initialized", notification=True)
        return result

    def catalog(self):
        tools, cursor, seen = {}, None, set()
        while True:
            result = self.rpc("tools/list", {"cursor": cursor} if cursor else {})["result"]
            if not isinstance(result.get("tools"), list):
                raise Error("Invalid tools/list response.")
            for tool in result["tools"]:
                if tool["name"] in tools:
                    raise Error("Duplicate tool name in catalog.")
                tools[tool["name"]] = tool
            cursor = result.get("nextCursor")
            if not cursor:
                return tools
            if cursor in seen:
                raise Error("Catalog pagination repeated its cursor.")
            seen.add(cursor)


ANNOTATIONS = {"title", "description", "default", "examples", "$schema", "$id",
               "$comment", "deprecated", "readOnly", "writeOnly"}
SUPPORTED = {"type", "properties", "required", "additionalProperties", "items", "enum", "const",
             "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minItems", "maxItems",
             "minLength", "maxLength", "pattern", "anyOf", "oneOf", "allOf", "$ref", "$defs",
             "definitions", "uniqueItems"}


def validate(schema, value, root=None, path="$", strict_top=True):
    """A declared, conservative JSON Schema subset. Unsupported constraints fail closed."""
    root = root or schema
    if schema is True:
        return
    if schema is False:
        raise Error(f"{path}: schema forbids this value.")
    if not isinstance(schema, dict):
        raise Error(f"{path}: invalid schema.")
    unknown = set(schema) - SUPPORTED - ANNOTATIONS
    if unknown:
        raise Error(f"{path}: schema constraints need a fuller validator: {sorted(unknown)}")
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise Error("Only local schema references are supported.")
        target = root
        try:
            for part in ref[2:].split("/"):
                target = target[part.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError) as exc:
            raise Error(f"Unresolved schema reference {ref}") from exc
        validate(target, value, root, path, strict_top)
    for mode in ("anyOf", "oneOf", "allOf"):
        if mode in schema:
            results = []
            for branch in schema[mode]:
                try:
                    validate(branch, value, root, path, False)
                    results.append(True)
                except Error:
                    results.append(False)
            if (mode == "anyOf" and not any(results)) or (
                mode == "oneOf" and sum(results) != 1) or (mode == "allOf" and not all(results)):
                raise Error(f"{path}: value fails {mode}.")
    types = schema.get("type")
    if types:
        types = [types] if isinstance(types, str) else types
        valid = {"object": isinstance(value, dict), "array": isinstance(value, list),
                 "string": isinstance(value, str), "integer": type(value) is int,
                 "number": type(value) in (int, float), "boolean": type(value) is bool,
                 "null": value is None}
        if not any(valid.get(t, False) for t in types):
            raise Error(f"{path}: expected {types}.")
    if "enum" in schema and not any(type(value) is type(v) and value == v for v in schema["enum"]):
        raise Error(f"{path}: value is outside enum.")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise Error(f"{path}: value differs from const.")
    if isinstance(value, dict):
        missing = set(schema.get("required", [])) - set(value)
        if missing:
            raise Error(f"{path}: missing {sorted(missing)}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate(properties[key], item, root, f"{path}.{key}", False)
            else:
                extra = schema.get("additionalProperties", not (path == "$" and strict_top))
                if extra is False:
                    raise Error(f"{path}: unknown argument {key}; allowed fields: {sorted(properties)}")
                if isinstance(extra, dict):
                    validate(extra, item, root, f"{path}.{key}", False)
    if isinstance(value, list):
        for key, test in (("minItems", len(value) < schema.get("minItems", 0)),
                          ("maxItems", len(value) > schema.get("maxItems", float("inf")))):
            if test:
                raise Error(f"{path}: violates {key}.")
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise Error(f"{path}: duplicate items.")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(schema["items"], item, root, f"{path}.{i}", False)
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", float("inf")):
            raise Error(f"{path}: invalid string length.")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise Error(f"{path}: string does not match pattern.")
    if type(value) in (int, float):
        tests = {"minimum": lambda x: value < x, "maximum": lambda x: value > x,
                 "exclusiveMinimum": lambda x: value <= x, "exclusiveMaximum": lambda x: value >= x}
        for key, test in tests.items():
            if key in schema and test(schema[key]):
                raise Error(f"{path}: violates {key}.")
