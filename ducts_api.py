from enum import Enum
import aiohttp
import asyncio
import msgpack
from datetime import datetime
import uuid as uuid_pkg

class DuctEvent:
    pass

class DuctConnectionEvent(DuctEvent):
    def __init__(self, state, source):
        super().__init__()
        self.state = state
        self.source = source

class DuctMessageEvent(DuctEvent):
    def __init__(self, rid, eid, data):
        super().__init__()
        self.rid = rid
        self.eid = eid
        self.data = data

class DuctEventListener:
    def __init__(self):
        self.funcs = {}
    async def on(self, names, func):
        if not isinstance(names, list):  names = [names]
        for name in names:
            if name not in self.funcs:
                raise Exception(f"[{name}]")
            self.funcs[name] = func

class ConnectionEventListener(DuctEventListener):
    async def onopen(self, event):
        pass

    async def onclose(self, event):
        pass

    async def onerror(self, event):
        pass

    async def onmessage(self, event):
        pass

class Duct:
    def __init__(self):
        self.WSD = None
        self.EVENT = None
        self._ws = None
        self._last_rid = 0

        self.connection_listener = ConnectionEventListener()
        self._event_handler = {}

    def next_rid(self):
        next_id = int(datetime.now().timestamp())
        if next_id <= self._last_rid:
            next_id = self._last_rid + 1
        self._last_rid = next_id
        return next_id

    async def _connect(self, session, reconnect=False):
        try:
            connect_url = self.WSD["websocket_url_reconnect"] if reconnect else self.WSD["websocket_url"]
            async with session.ws_connect(connect_url) as ws:
                event = "someevent"  # FIXME

                self._ws = ws

                if reconnect:  await self._onreconnect(event)
                else:          await self._onopen(event)


                await self.connection_listener.onopen(DuctConnectionEvent("onopen", event))
                hoge = asyncio.ensure_future(self._onmessage_loop(ws))
                await hoge

                #await self.send(self.next_rid(), self.EVENT["PROJECT"], { "Command": "List" })
                

        except Exception as e:
            print(e)
            await self.connection_listener.onerror(DuctConnectionEvent("onerror", e))
    
    async def open(self, wsd_url, uuid=None, params=None):
        if self._ws:
            return

        self.wsd_url = wsd_url  # check
        self.query = f"?uuid={uuid}" if uuid else f"?uuid={uuid_pkg.uuid4()}"
        
        if params:
            for key,val in params: self.query += f"&{key}={val}"

        async with aiohttp.ClientSession() as session:
            async with session.get(self.wsd_url + self.query) as resp:
                self.WSD = await resp.json()
                self.EVENT = self.WSD["EVENT"]

            await self._connect(session)

    async def reconnect(self):
        if self._ws:
            return

        async with aiohttp.ClientSession() as session:
            await self._connect(session, reconnect=True)
                
    async def send(self, rid, eid, data):
        data_msgpack = msgpack.packb([rid, eid, data])
        await self._ws.send_bytes(data_msgpack)
        return rid
        
    async def close(self):
        try:
            if self._ws:
                await self._ws.close()
                await self._onclose()
        finally:
            self._ws = None
        
    def set_event_handler(self, event_id, handler):
        self._event_handler[event_id] = handler

    async def catchall_event_handler(self, rid, eid, data):
        pass

    async def uncaught_event_handler(self, rid, eid, data):
        pass

    async def event_error_handler(self, rid, eid, data, error):
        pass

    @property
    def state(self):
        if self._ws:  return self._ws.ready_state  #FIXME ready_state is probably not available in aiohttp
        else:         return State.CLOSE

    async def _onopen(self, event):
        self._send_timestamp = datetime.now().timestamp()
        self.time_offset = 0
        self.time_latency = 0
        self._time_count = 0
        self.set_event_handler(self.EVENT["ALIVE_MONITORING"], self._alive_monitoring_handler)
        rid = self.next_rid()
        eid = self.EVENT["ALIVE_MONITORING"]
        value = self._send_timestamp
        await self.send(rid, eid, value)

        await self.onopen(event)

    async def _onclose(self):
        await self.onclose()

    async def onopen(self, event):
        pass

    async def onclose(self):
        pass

    async def _onreconnect(self, event):
        print("reconnected")

    async def _onmessage_loop(self, ws):
        async for msg in ws:
            try:
                if msg.type==aiohttp.WSMsgType.CLOSE:
                    await self.connection_listener.onclose(DuctConnectionEvent("onclose", msg))
                    break

                elif msg.type==aiohttp.WSMsgType.BINARY:
                    await self.connection_listener.onmessage(DuctConnectionEvent("onmessage", msg))
                    rid, eid, data = msgpack.unpackb(msg.data)
                    try:
                        await self.catchall_event_handler(rid, eid, data)
                        handle = self._event_handler[eid] if eid in self._event_handler else self.uncaught_event_handler
                        await handle(rid, eid, data)
                    except Exception as e:
                        await self.event_error_handler(rid, eid, data, e)
            except Exception as e:
                await self.event_error_handler(-1, -1, None, e)

    async def _alive_monitoring_handler(self, rid, eid, data):
        client_received = datetime.now().timestamp()
        server_sent = data[0]
        server_received = data[1]
        client_sent = self._send_timestamp
        new_offset = ((server_received - client_sent) - (client_received - server_sent))/2
        new_latency = ((client_received - client_sent) - (server_sent - server_received))/2
        self.time_offset = (self.time_offset * self._time_count + new_offset) / (self._time_count + 1)
        self.time_latency = (self.time_latency * self._time_count + new_latency) / (self._time_count + 1)
        self._time_count += 1
