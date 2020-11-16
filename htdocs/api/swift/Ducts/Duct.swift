//
//  WSClient.swift
//  NDS
//
//  Created by Susumu Saito on 2020/06/02.
//  Copyright © 2020 Susumu Saito. All rights reserved.
//

import Foundation
import MessagePack
import Starscream
import SwiftyJSON
import Promises

enum DuctConnectionState: Int {
    case close = -1
    case openConnecting = 0
    case openConnected = 1
    case openClosing = 2
    case openClosed = 3
}

class Duct {
    var wsdUrl: String
    var uuid: String
    var user: String
    var kwargs: [String: String]
    
    var WSD: JSON?
    var EVENT: JSON?
    var _ws: WebSocket?
    var _lastRid: Int! = 0
    var state: Int = DuctConnectionState.close.rawValue
    
    var sendTimestamp: Double!
    var timeOffset: Double = 0
    var timeLatency: Double = 0
    var timeCount: Int = 0
    
    var uaString = "TemporaryUserAgentString"
    
    var eventHandlers: [Int: ((Int, Int, Any) -> Void)] = [:]
    var uncaughtEventHandler: ((Int, Int, Any) -> Void)?
    var catchAllEventHandler: ((Int, Int, Any) -> Void)?
    
    var connectionListener: DuctConnectionEventListener! = nil
    var starscreamConnectionListener: StarscreamEventListener! = nil
    
    init(wsdUrl: String, uuid: String, user: String, kwargs: [String: String]) {
        self.wsdUrl = wsdUrl
        self.uuid = uuid
        self.user = user
        self.kwargs = kwargs
        
        connectionListener = DuctConnectionEventListener()
        starscreamConnectionListener = StarscreamEventListener()
    }
        
    func send(rid request_id: Int, eid event_id: Int, data: Any?) -> Void {
        guard let ws = self._ws else { return }
        
        let msgpack = pack(anyToMPValue([request_id, event_id, data!])!)
        ws.write(data: msgpack)
    }
    
    func connectWS(timeoutInterval: Double, reconnect: Bool = false) {
        let url = reconnect ? self.WSD!["websocket_url_reconnect"].stringValue : self.WSD!["websocket_url"].stringValue
        var request = URLRequest(url: URL(string: url)!)
        request.timeoutInterval = timeoutInterval
        request.setValue(uaString, forHTTPHeaderField: "User-Agent")
        let ws = WebSocket(request: request)
        ws.onEvent = self.onEvent
        self._ws = ws
        self._ws!.connect()
    }
    
    func open(timeoutInterval: Double) {
        if self._ws != nil { return }
        
        var urlString = self.wsdUrl + "?uuid=" + self.uuid + "&user=" + self.user
        for (key,val) in self.kwargs { urlString += "&\(key)=\(val)" }
        var request = URLRequest(url: URL(string: urlString)!)
        request.setValue(uaString, forHTTPHeaderField: "User-Agent")

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let data = data {
                do {
                    self.WSD = try JSON(data: data)
                    self.EVENT = self.WSD!["EVENT"]
                    self.connectWS(timeoutInterval: timeoutInterval)
                } catch let error {
                    self.connectionListener.handle(ErrorEvent(status: .connectionFailed, error: error))
                }
            }
        }
        task.resume()
    }
    
    func reconnect(timeoutInterval: Double) {
        guard let WSD = self.WSD else { return }
        if state==DuctConnectionState.openConnected.rawValue { return }
        self.connectWS(timeoutInterval: timeoutInterval, reconnect: true)
    }

    func close() -> Void {
        if let ws = _ws {
            state = DuctConnectionState.openClosing.rawValue
            ws.disconnect()  // -> starscream .cancelled
        }
    }
    func nextRid() -> Int {
        var nextId = Int(NSDate().timeIntervalSince1970*1000)
        if(nextId <= _lastRid) {
            nextId = _lastRid + 1
        }
        _lastRid = nextId
        return nextId
    }
    
    func setEventHandler(forEid event_id: Int, handler: @escaping (Int, Int, Any) -> Void) { eventHandlers[event_id] = handler }
    func setUncaughtEventHandler(_ handler: @escaping (Int, Int, Any) -> Void ) { uncaughtEventHandler = handler }
    func setCatchAllEventHandler(_ handler: @escaping (Int, Int, Any) -> Void ) { catchAllEventHandler = handler }
    
    func onOpen() {
        //self.setEventHandler(forEid: self.EVENT!["ALIVE_MONITORING"].intValue) { _,_,_ in }
        setEventHandler(forEid: EVENT!["ALIVE_MONITORING"].intValue) { rid, eid, data in
//            print(data)
            let dataArray = data as! [Double]
            let clientReceived = NSDate().timeIntervalSince1970
            let serverSent = dataArray[0]
            let serverReceived = dataArray[1]
            let clientSent = self.sendTimestamp
            let newOffset = ((serverReceived-clientSent!)-(clientReceived-serverSent))/2
            let newLatency = ((clientReceived-clientSent!)-(serverSent-serverReceived))/2
            self.timeOffset = (self.timeOffset*Double(self.timeCount) + newOffset) / (Double(self.timeCount)+1)
            self.timeLatency = (self.timeLatency*Double(self.timeCount) + newLatency) / (Double(self.timeCount)+1)
            self.timeCount += 1
        }
        sendTimestamp = NSDate().timeIntervalSince1970
        self.send(rid: self.nextRid(), eid: self.EVENT!["ALIVE_MONITORING"].intValue, data: sendTimestamp)
    }
    func onReconnect() {
    }
    
    func onEvent(event: WebSocketEvent) {
        
        starscreamConnectionListener.handle(StarscreamEvent(event))
        
        switch event {
            case .connected(let header):
                if self._ws!.request.url!.absoluteString.hasSuffix("reconnect") {   // reconnection open
                    connectionListener.handle(OpenEvent(status: .sessionRestored, header: header))
                    self.onReconnect()
                } else {
                    connectionListener.handle(OpenEvent(status: .sessionCreated, header: header))
                    self.onOpen()
                }
                state = DuctConnectionState.openConnected.rawValue
            
            case .binary(let binary):
                connectionListener.handle(MessageEvent(binary))
                let msg: MessagePackValue = try! unpack(binary).value
                let msgArray = MPValueToJSON(msg) as! Array<Any>
                let rid = msgArray[0] as! Int, eid = msgArray[1] as! Int, data = msgArray[2]
                
                if let handler = catchAllEventHandler { handler(rid, eid, data) }
                if let handler = eventHandlers[eid] { handler(rid, eid, data) }
                else if let handler = uncaughtEventHandler { handler(rid, eid, data) }
            
            case .disconnected(let reason, _):
                _ws = nil
                state = DuctConnectionState.close.rawValue
                if reason=="session expired" { connectionListener.handle(CloseEvent(status: .byServer, message: reason)) }
                else { connectionListener.handle(CloseEvent(status: .byServer)) }

            case .cancelled:
                if state == DuctConnectionState.openClosed.rawValue {
                    // ignoring since already handled by .error
                } else {
                    _ws = nil
                    state = DuctConnectionState.close.rawValue
                    connectionListener.handle(CloseEvent(status: .byPeer))
                }
            
            case .error(let error):
                if state==DuctConnectionState.openConnected.rawValue {
                    state = DuctConnectionState.openClosed.rawValue
                    connectionListener.handle(ErrorEvent(status: .connectionDead, error: error))
                } else {
                    _ws = nil
                    state = DuctConnectionState.close.rawValue
                    connectionListener.handle(ErrorEvent(status: .connectionFailed, error: error))
                }
//            case .viabilityChanged(_):
//            case .reconnectSuggested(_):
//            case .text(let string):
//            case .ping(_):
//            case .pong(_):
            default:
                break
        }
    }
}
