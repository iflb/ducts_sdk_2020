//
//  Event.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/08.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation
import Starscream

/// `DuctEvent`は、Ductsに関連する全てのイベントの基底クラスです。
public class DuctEvent {
    /// イベントのクラス名。
    class var name: String {
        return String(describing: self)
    }
    /// 子クラスインスタンスのクラス名（イベント名）を取得します。
    public func getName() -> String {
        return Self.name
    }
}




/// `DuctMessageEvent`は、Ductsのメッセージ通信に関連する全てのイベントの基底クラスです。
public class DuctMessageEvent: DuctEvent {
}




/// `DuctConnectionEvent`は、Ductsの接続に関連する全てのイベントの基底クラスです。
public class DuctConnectionEvent: DuctEvent {
}

/// `OpenEvent`は、Ductsが接続成功した際のイベントクラスです。
public class OpenEvent: DuctConnectionEvent {
    /// サーバーレスポンスのヘッダ
    public enum Status {
        /// 新規接続要求の成功を示すステータス
        case sessionCreated
        /// 再接続要求の成功を示すステータス
        case sessionRestored
    }
    public var status: Status
    public var header: [String: String]
    init(status: Status, header: [String: String]) {
        self.status = status
        self.header = header
    }
}
/// `MessageEvent`は、Ductsのメッセージを受け取った際のイベントクラスです。
public class MessageEvent: DuctConnectionEvent {
    /// Ductsメッセージのバイナリデータ
    public var binary: Data
    init(_ binary: Data) {
        self.binary = binary
    }
}
public class CloseEvent: DuctConnectionEvent {
    public var status: Status
    public var message: String?
    public enum Status {
        /// クライアント側から明示的に接続が切断されたことを示すステータス
        case byPeer
        /// サーバー側から明示的に接続が切断されたことを示すステータス
        case byServer
    }
    init(status: Status, message: String? = nil) {
        self.status = status
        self.message = message
    }
}

public class ErrorEvent: DuctConnectionEvent {
    /// エラー内容
    public var error: Error?
    public var status: Status
    public enum Status {
        /// 接続に失敗したことを表すステータス
        case connectionFailed
        /// 接続が意図せず切断されたことを表すステータス
        case connectionDead
    }
    init(status: Status, error: Error?) {
        self.status = status
        self.error = error
    }
}


/**
`StarscreamEvent`は、SDK内部で使用しているWebSocketライブラリである[Starscream](https://github.com/daltoniam/Starscream)の接続に関連する全てのイベントを受け取るクラスです。
 
 利用例は以下のとおりです。`WebSocketEvent`列挙型メンバの詳細は[公式ドキュメント](https://github.com/daltoniam/Starscream)を参照してください。
 ```
 self.nds.onStarscreamEvent.setHandler(forEvent: StarscreamEvent.self) { connEvt in
    switch connEvt.event {
        case .connected(let header):
            print(header)
        case .disconnected(let reason, let code):
            ...
        default:
            break
    }
 }
 ```
**/
public class StarscreamEvent: DuctEvent {
    /// Starscreamにおける`didReceive(event:client:)`の`event`引数として渡されるイベント。
    public var event: WebSocketEvent?
    init(_ event: WebSocketEvent?) {
        self.event = event
    }
}
