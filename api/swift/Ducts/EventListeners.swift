//
//  EventHandlers.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/21.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation

/// `DuctEventListener`は、Ductsに関連する各種イベントのリスナーの基底クラスです。
public class DuctEventListener {
    var handlers: [String: Any] = [:]
    var userDefaultHandler: Any? = nil
    // MARK: 型エイリアス
    /// ハンドラ関数の型仕様を定めるエイリアス。ハンドラは、唯一の引数として`DialogueEvent`を基底クラスとする発火イベントのインスタンスを渡され、かつ返り値はVoidであることを表します。
    public typealias Event = DuctEvent
    public typealias handlerType<E: Event> = (E) -> Void
    
    // MARK: メソッド
    /// ハンドラ関数を設定します。
    /// - Parameters:
    ///   - eventType: `Event`に指定されたクラスを基底クラスとするイベントクラス型。
    ///   - handler: `handlerType`型に準拠するハンドラ関数。
    public func setHandler<E: Event>(forEvent eventType: E.Type, handler: @escaping handlerType<E>){
        handlers[E.name] = handler
    }
    func handle<E: Event>(_ event: E) {
        if let handler = self.handlers[E.name] as? handlerType<E> {
            handler(event)
        } else if self.userDefaultHandler != nil {
            let handler = self.userDefaultHandler! as! ((Event) -> Void)
            handler(event)
        }
    }
    /// デフォルトハンドラ関数を設定します。デフォルトハンドラは、`setHandler(forEvent:handler:)`によりハンドラ関数が設定されていないイベントの発火を全て受け取ります。
    /// - Parameter handler: `handlerType`型に準拠するハンドラ関数。
    public func setDefaultHandler<E: Event>(_ handler: @escaping handlerType<E>) {
        self.userDefaultHandler = handler as Any?
    }
}

/// `DuctConnectionEvent`を受け取るためのマネージャークラスです。
public class DuctConnectionEventListener: DuctEventListener {
    public typealias Event = DuctConnectionEventListener
}

public class StarscreamEventListener: DuctEventListener {
    public typealias Event = StarscreamEvent
}
