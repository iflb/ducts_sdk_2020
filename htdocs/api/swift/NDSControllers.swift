//
//  NDSControllers.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/21.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation




/**
`DialogController`は、対話に対する操作を行うために、NDSサーバーへリクエストを送信するためのクラスです。

`Facade`クラスのインスタンス生成時に内部的に初期化され、利用可能となります。
 */
public class DialogueController {
    let duct: Duct
    init(_ duct: Duct) {
        self.duct = duct
    }
    private func sendUserBehavior(_ data: String) {
        let rid = duct.nextRid()
        let eid = duct.EVENT!["USER_BEHAVIOR_LISTENER"].intValue
        duct.send(rid: rid, eid: eid, data: data)
    }
    private func sendStartScenario(_ key: String) {
        let rid = duct.nextRid()
        let eid = duct.EVENT!["MAIN_CONTROLLER"].intValue
        let data = ["key": key]
        duct.send(rid: rid, eid: eid, data: data)
    }
    
    /// 指定されたキーのトピック記事の配信を開始します。
    /// - Parameter key: シナリオキー
    public func play(_ scenarioKey: String) { sendStartScenario(scenarioKey) }
    /// システム発話を再開します。
    public func resume()         { sendUserBehavior("Resume") }
    /// システム発話を中断/停止します。
    public func suspend()        { sendUserBehavior("Suspend") }
    /// システム発話をトピックシナリオの最後まで送ります。
    public func skipByScenario()   { sendUserBehavior("SkipScenario") }
    /// 現在システム発話中の文章を初めから再生します。
    public func repeatBySentence() { sendUserBehavior("RepeatSentence") }
    /// 現在システム発話中のセクションを初めから再生します。
    public func repeatBySection()  { sendUserBehavior("RepeatSection") }
    /// システム発話の次の文章を再生します。
    public func skipBySentence()   { sendUserBehavior("SkipSentence") }
    /// システム発話の次のセクションを再生します。
    public func skipBySection()    { sendUserBehavior("SkipSection") }
    
    /// 発話テキストをシステムへ送信します。
    /// - Parameter utterance: 発話テキストデータ
    public func sendUtteranceText(_ utterance: String) { sendUserBehavior(utterance) }
}





/**
`ResourceController`は、対話リソース（シナリオ）に対する操作を行うために、NDSサーバーへリクエストを送信するためのクラスです。

`Facade`クラスのインスタンス生成時に内部的に初期化され、利用可能となります。
 */
public class ResourceController {
    let duct: Duct
    init(_ duct: Duct) {
        self.duct = duct
    }
    private func sendResourceCommand(_ eid: Int, kwargs: [String: Any]) { duct.send(rid: duct.nextRid(), eid: eid, data: kwargs) }
    /// シナリオのメタデータを取得します。
    /// - Parameter key: シナリオキー
    public func getScenarioMetadata(forKey key: String) {
        sendResourceCommand(duct.EVENT!["GET_SCENARIO_METADATA"].intValue, kwargs: ["key":key])
    }
    /// 現在位置からの距離の近い順にソートされたシナリオ一覧を取得します。
    /// - Parameters:
    ///   - latitude: 現在位置の緯度
    ///   - longitude: 現在位置の経度
    ///   - radius: 現在位置からの半径距離の数値
    ///   - unit: 現在位置からの半径距離の単位
    public func getScenariosByLocation(latitude: Double, longitude: Double, radius: Int, unit: String = "km") {
        sendResourceCommand(duct.EVENT!["GET_SCENARIOS_BY_LOCATION"].intValue, kwargs: ["latitude": latitude, "longitude": longitude, "radius": radius, "unit": unit])
    }
    /// 日付順にソートされたシナリオ一覧を取得します。
    /// - Parameters:
    ///   - from: 開始インデックス
    ///   - to: 終了インデックス
    public func getScenariosByDate(from: Int, to: Int) {
        sendResourceCommand(duct.EVENT!["GET_SCENARIOS_BY_DATE"].intValue, kwargs: ["from": from, "to": to])
    }
}






/**
`SpeechRecognizer`は、ユーザー音声入力に対する操作を行うために、NDSサーバーへリクエストを送信するためのクラスです。
 
`Facade`クラスのインスタンス生成時に内部的に初期化され、利用可能となります。
*/
public class SpeechRecognizer {
    let duct: Duct!
    init(_ duct: Duct) {
        self.duct = duct
    }
    private func userBehaviorListener(_ data: String) {
        duct.send(rid: duct.nextRid(), eid: duct.EVENT!["USER_BEHAVIOR_LISTENER"].intValue, data: data)
    }
    private func userWavAudioListener(_ audioData: Data) {
        duct.send(rid: duct.nextRid(), eid: duct.EVENT!["USER_WAV_AUDIO_LISTENER"].intValue, data: audioData)
    }
    private func asrCtrlListener(_ data: String) {
        duct.send(rid: duct.nextRid(), eid: duct.EVENT!["ASRCTRL_LISTENER"].intValue, data: data)
    }
    /// 音声認識の待ち状態を開始します。
    public func start() { asrCtrlListener("START") }
    /// 音声認識の待ち状態を終了します。
    public func stop() { asrCtrlListener("STOP") }
    /// 発話データの音声認識をリクエストします。
    /// - Parameter audioData: 発話音声データ
    public func process(_ audioData: Data) { userWavAudioListener(audioData) }
}
