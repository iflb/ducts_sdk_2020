//
//  NDS.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/03.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation
import SwiftyJSON
import Promises


class NDSDuct: Duct {
    var resource: ResourceController! = nil
    var dialogue: DialogueController! = nil
    var asr: SpeechRecognizer! = nil
    
    var resourceListener = ResourceEventListener()
    var dialogueListener = DialogueEventListener()
    var asrListener = SpeechRecognizerEventListener()
    
    override init(wsdUrl: String, uuid: String, user: String, kwargs: [String : String]) {
        super.init(wsdUrl: wsdUrl, uuid: uuid, user: user, kwargs: kwargs)
        
        resource = ResourceController(self)
        dialogue = DialogueController(self)
        asr = SpeechRecognizer(self)
        
        resourceListener = ResourceEventListener()
        dialogueListener = DialogueEventListener()
        asrListener = SpeechRecognizerEventListener()
    }
    
    override func onOpen() {
        super.onOpen()
        send(rid: nextRid(), eid: EVENT!["SYSTEM_BEHAVIOR_MODEL"].intValue, data: "")
        send(rid: nextRid(), eid: EVENT!["SYSTEM_AUDIO_MODEL"].intValue, data: "")
        send(rid: nextRid(), eid: EVENT!["ASRCTRL_MODEL"].intValue, data: "")
        setEventHandlers()
    }
    
    private func setEventHandlers() {
        setEventHandler(forEid: EVENT!["SYSTEM_AUDIO_MODEL"].intValue) { rid, eid, data in
            self.sendAudioPlayerCallback()
            if let d = data as? Data { self.dialogueListener.handle(Audio(audioData: d)) }
        }
        setEventHandler(forEid: EVENT!["SYSTEM_BEHAVIOR_MODEL"].intValue, handler: handleDialogueEvent)
        setEventHandler(forEid: EVENT!["ASRCTRL_MODEL"].intValue,          handler: handleASREvent)
        setEventHandler(forEid: EVENT!["GET_SCENARIO_METADATA"].intValue) { rid, eid, data in
            self.resourceListener.handle(ScenarioForKey(resource: data as! ScenarioMetadata.rawFormat))
        }
        setEventHandler(forEid: EVENT!["GET_SCENARIOS_BY_LOCATION"].intValue) { rid, eid, data in
            self.resourceListener.handle(ScenariosByLocation(resources: data as! [ScenarioMetadata.rawFormat]))
        }
        setEventHandler(forEid: EVENT!["GET_SCENARIOS_BY_DATE"].intValue) { rid, eid, data in
            self.resourceListener.handle(ScenariosByDate(resources: data as! [ScenarioMetadata.rawFormat]))
        }
    }
    
    private func sendAudioPlayerCallback() {
        let rid = nextRid()
        let eid = EVENT!["AUDIO_PLAYER_LISTENER"].intValue
        let data = [NSDate().timeIntervalSince1970, timeOffset, timeLatency]
        return send(rid: rid, eid: eid, data: data)
    }

    private func handleDialogueEvent(rid: Int, eid: Int, data: Any) -> Void {
        let data = data as! [String: String]
        for (_,val) in data {
            switch(val) {
                case "START_SCENARIO": dialogueListener.handle(StartScenario(data))
                case "START_SENTENCE": dialogueListener.handle(StartSentence(data))
                case "START_SECTION":  dialogueListener.handle(StartSection(data))
                case "NEXT_CLAUSE":    dialogueListener.handle(Clause(data))
                case "END_SECTION":    dialogueListener.handle(EndSection())
                case "END_SENTENCE":   dialogueListener.handle(EndSentence())
                case "DISCUSSION":     dialogueListener.handle(Discussion())
                case "END_SCENARIO":   dialogueListener.handle(EndScenario())
                case "SKIP_SCENARIO":  dialogueListener.handle(SkipScenario())
                case "SUSPEND":        dialogueListener.handle(Suspend())
                case "RESUME":         dialogueListener.handle(Resume())
                case "REQUEST":        dialogueListener.handle(Request(data))
                default:               break
            }
        }
    }
    private func handleASREvent(rid: Int, eid: Int, data: Any) -> Void {
        let dataJSON = data as! [String:String]
        let state = dataJSON["STATE"]!
        switch state {
            case "RUNNING":
                asrListener.handle(Available())
            case "QUEUE":
                asrListener.handle(Preparing())
            case "END", "ERROR", "INIT":
                asrListener.handle(Unavailable())
            default:
                break
        }
        
    }
}

/// `Facade`は、NDSの各種機能を提供するクラスです。
public class Facade {
               
    var duct: NDSDuct

    /// `DuctConnectionEventListener`の単一インスタンス。
    public var onConnection: DuctConnectionEventListener
    /// `StarscreamEventListener`の単一インスタンス。
    public var onStarscreamEvent: StarscreamEventListener
    
    /// `ResourceEventListener`の単一インスタンス。
    public var onResource: ResourceEventListener
    /// `DialogueEventListener`の単一インスタンス。
    public var onDialogue: DialogueEventListener
    /// `SpeechRecognizerEventListener`の単一インスタンス。
    public var onASR: SpeechRecognizerEventListener
    
    /// `ResourceController`の単一インスタンス。
    public var resourceController: ResourceController
    /// `DialogueController`の単一インスタンス。
    public var dialogueController: DialogueController
    /// `SpeechRecognizer`の単一インスタンス。
    public var speechRecognizer: SpeechRecognizer

    /// `Facade`クラスのインスタンス生成を行います。
    /// - Parameter wsdUrl: Web Service Descriptorを返すサーバーURI（e.g., `https://nds.ducts.io/ducts/wsd`）
    /// - Parameter uuid: アプリに紐づくUUID
    /// - Parameter user: ユーザー名
    /// - Parameter kwargs: その他各種セッション情報
    public init(wsdUrl: String, uuid: String, user: String, kwargs: [String : String]){
        duct = NDSDuct(wsdUrl: wsdUrl, uuid: uuid, user: user, kwargs: kwargs)
        
        onConnection = duct.connectionListener
        onStarscreamEvent = duct.starscreamConnectionListener
        onResource = duct.resourceListener
        onDialogue = duct.dialogueListener
        onASR = duct.asrListener
        
        resourceController = duct.resource
        dialogueController = duct.dialogue
        speechRecognizer = duct.asr
    }
    
    /// NDSサーバーとの接続を開始します。
    public func open(timeoutInterval: Double = 5) { duct.open(timeoutInterval: timeoutInterval) }

    /// NDSサーバーへ再接続します。
    public func reconnect(timeoutInterval: Double = 5) { duct.reconnect(timeoutInterval: timeoutInterval) }
    
    /// NDSサーバーとの接続を終了します。
    public func close() { duct.close() }
}
