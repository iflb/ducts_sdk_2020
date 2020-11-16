//
//  EventListeners.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/21.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation

/// `DialogueEvent`を受け取るためのマネージャークラスです。
public class DialogueEventListener: DuctEventListener {
    public typealias Event = DialogueEvent
}
/// `SpeechRecognizerEvent`を受け取るためのマネージャークラスです。
public class SpeechRecognizerEventListener: DuctEventListener {
    public typealias Event = SpeechRecognizerEvent
}
/// `ResourceEvent`を受け取るためのマネージャークラスです。
public class ResourceEventListener: DuctEventListener {
    public typealias Event = ResourceEvent
}
