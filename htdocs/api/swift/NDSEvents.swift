//
//  NDSEvents.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/21.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation




/// 対話関連イベントの基底クラスです。
public class DialogueEvent: DuctMessageEvent {}

/// シナリオ開始時に発火するイベントです。
public class StartScenario: DialogueEvent {
    private var scenarioKey: String
    init(_ data: [String: String]) {
        self.scenarioKey = data["SCENARIO_KEY"]!
    }
    /// シナリオキーを返します。
    /// - Returns: シナリオキー
    public func getScenarioKey() -> String { return self.scenarioKey }
}
/// 文章開始時に発火するイベントです。
public class StartSentence: DialogueEvent {
    private var sentenceId: String
    private var utterance: String
    init(_ data: [String: String]) {
        self.sentenceId = data["SENTENCE_ID"]!
        self.utterance = data["UTTERANCE"]!
    }
    /// 文章IDを返します。
    /// - Returns: 文章ID
    public func getSentenceId() -> String { return self.sentenceId }
    /// 文章テキストを返します。
    /// - Returns: 文章テキスト
    public func getUtterance() -> String { return self.utterance }
}
/// 文節開始時に発火するイベントです。
public class StartSection: DialogueEvent {
    private var sectionId: String
    private var utterance: String
    private var questions: [String] = []
    init(_ data: [String: String]) {
        self.sectionId = data["SECTION_ID"]!
        self.utterance = data["UTTERANCE"]!
        for (key,val) in data {
            if(key.hasPrefix("REQUEST")){
                self.questions.append(val)
            }
        }
    }
    /// 文節IDを返します。
    /// - Returns: 文節ID
    public func getSectionId() -> String { return self.sectionId }
    /// 文節テキストを返します。
    /// - Returns: 文節テキスト
    public func getUtterance() -> String { return self.utterance }
    /// 文節の内容に関連するユーザー質問の候補を返します。
    /// - Returns: ユーザー質問候補
    public func getQuestions() -> [String] { return self.questions }
}
/// システム発話テキストの最小単位受信時に発火するイベントです。
public class Clause: DialogueEvent {
    private var clause: String
    init(_ data: [String: String]) { self.clause = data["UTTERANCE"]! }
    /// 発話最小単位を返します。
    /// - Returns: 発話最小単位
    public func getClause() -> String { return clause }
}
/// 文節終了時に発火するイベントです。
public class EndSection: DialogueEvent {}
/// 文章終了時に発火するイベントです。
public class EndSentence: DialogueEvent {}
/// シナリオ終了時に発火するイベントです。
public class EndScenario: DialogueEvent {}
/// シナリオ終了後、ユーザー質問受付開始時に発火するイベントです。
public class Discussion: DialogueEvent {}
/// シナリオスキップ時に発火するイベントです。
public class SkipScenario: DialogueEvent {}
/// 対話停止時に発火するイベントです。
public class Suspend: DialogueEvent {}
/// 対話再開時に発火するイベントです。（暫定、`Play`クラスと等価）
public class Resume: DialogueEvent {}
/// システム発話音声受信時に発火するイベントです。
public class Audio: DialogueEvent {
    private var audioData: Data
    private var _isPlaying: Bool
    init(audioData: Data) {
        self.audioData = audioData
        _isPlaying = audioData.count>0 ? true : false
    }
    /// システム発話音声を返します。
    /// - Returns: システム発話音声
    public func getAudio() -> Data { return audioData }
    /// システム発話音声が再生中か否かを返します。
    /// - Returns: 再生ステータス
    public func isPlaying() -> Bool { return _isPlaying }
}
/// ユーザーのリクエスト受付時に発火するイベントです。
public class Request: DialogueEvent {
    private var text: String
    init(_ data: [String: String]) { self.text = data["UTTERANCE"]! }
    /// ユーザーのリクエスト内容を返します。
    /// - Returns: ユーザーリクエスト
    public func getText() -> String { return text }
}



/// シナリオのメタデータを表す構造です。
public struct ScenarioMetadata {
    typealias rawFormat = [String: String]
    /// シナリオの位置情報に関連するメタデータを表す構造体です。
    public struct Geolocation {
        /// 緯度
        public var latitude: Double
        /// 経度
        public var longitude: Double
        /// 距離
        public var distance: Double?
        init(latitude: Double, longitude: Double, distance: Double?) {
            self.latitude = latitude
            self.longitude = longitude
            self.distance = distance
        }
    }
    
    
    /// キー
    public var key: String
    /// タイトル
    public var title: String
    /// あらすじ
    public var description: String?
    /// 位置情報
    public var geo: Geolocation?
    
    init(resource: rawFormat) {
        self.key = resource["key"]!
        self.title = resource["title"]!
        if let description = resource["description"] { self.description = description }
        if let latitude = resource["latitude"], let longitude = resource["longitude"] {
            self.geo = Geolocation(latitude: Double(latitude)!, longitude: Double(longitude)!, distance: Double(resource["distance"]!))
        }
    }
}

/// シナリオ関連のイベントの基底クラスです。
public class ResourceEvent: DuctMessageEvent {}

/// シナリオのデータを受信した時に発火するイベントです。
public class ScenarioForKey: ResourceEvent {
    private var resource: ScenarioMetadata.rawFormat
    init(resource: ScenarioMetadata.rawFormat) {
        self.resource = resource
    }
    /// シナリオのメタデータを返します。
    /// - Returns: メタデータ
    public func getMetadata() -> ScenarioMetadata {
        return ScenarioMetadata(resource: resource)
    }
}
/// 日付順にソートされたシナリオ一覧を受信時に発火するイベントです。
public class ScenariosByDate: ResourceEvent {
    private var resources: [ScenarioMetadata.rawFormat]
    init(resources: [ScenarioMetadata.rawFormat]) { self.resources = resources }
    /// シナリオ一覧を返します。
    /// - Returns: シナリオ一覧
    public func getMetadata() -> [ScenarioMetadata] {
        var scenarios: [ScenarioMetadata] = []
        for resource in resources { scenarios.append(ScenarioMetadata(resource: resource)) }
        return scenarios
    }
}
/// 現在位置からの距離の近い順にソートされたシナリオ一覧を受信時に発火するイベントです。
public class ScenariosByLocation: ResourceEvent {
    private var resources: [ScenarioMetadata.rawFormat]
    init(resources: [ScenarioMetadata.rawFormat]) { self.resources = resources }
    /// シナリオ一覧を返します。
    /// - Returns: シナリオ一覧
    public func getMetadata() -> [ScenarioMetadata] {
        var scenarios: [ScenarioMetadata] = []
        for resource in resources { scenarios.append(ScenarioMetadata(resource: resource)) }
        return scenarios
    }

}







/// 音声認識関連のイベントの基底クラスです。
public class SpeechRecognizerEvent: DuctMessageEvent {}

/// 音声認識モジュールが準備状態となった時に発火するイベントです。
public class Preparing: SpeechRecognizerEvent {}
/// 音声認識モジュールが入力受付状態となった時に発火するイベントです。
public class Available: SpeechRecognizerEvent {}
/// 音声認識モジュールが入力受付を終了した時に発火するイベントです。
public class Unavailable: SpeechRecognizerEvent {}
