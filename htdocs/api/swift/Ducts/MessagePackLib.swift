//
//  MessagePackLib.swift
//  NDS
//
//  Created by Susumu Saito on 2020/06/02.
//  Copyright © 2020 Susumu Saito. All rights reserved.
//

import Foundation
import MessagePack

func MPValueToJSON(_ MPValue : MessagePackValue) -> Any {
    if let val = MPValue.boolValue { return val }
    else if let val = MPValue.intValue { return val }
    else if let val = MPValue.uintValue { return val }
    else if let val = MPValue.floatValue { return val }
    else if let val = MPValue.doubleValue { return val }
    else if let val = MPValue.stringValue { return val }
    else if let val = MPValue.dataValue { return val }
    else if let ary = MPValue.arrayValue {
        var newAry = Array<Any?>(repeating: nil, count: ary.count)
        for (idx, elm) in ary.enumerated() {
            newAry[idx] = MPValueToJSON(elm)
        }
        // Arrayの要素を全てnon-Optionalにする：https://stackoverflow.com/questions/25589605/swift-shortcut-unwrapping-of-array-of-optionals
        let newAryNonOptional = newAry.compactMap{ $0 }
        return newAryNonOptional
    }
    else if let dict = MPValue.dictionaryValue {
        var newDict: [String: Any] = [:]
        for (key, val) in dict {
            newDict[MPValueToJSON(key) as! String] = MPValueToJSON(val)
        }
        return newDict
    }
    else {
        return [:]
    }
}

// https://github.com/a2/MessagePack.swift/issues/36
func anyToMPValue(_ anyVal : Any) -> MessagePackValue? {

    switch(anyVal) {

    case is Bool:
        return MessagePackValue(anyVal as! Bool)

    case is Int: // will not handle Int8, Int16, Int32, Int64
        return MessagePackValue(anyVal as! Int)

    case is UInt: // does not handle UInt8, UInt16, UInt32, UInt64
        return MessagePackValue(anyVal as! UInt)

    case is Float:
        return MessagePackValue(anyVal as! Float)

    case is Double:
        return MessagePackValue(anyVal as! Double)

    case is String:
        return MessagePackValue(anyVal as! String)

    case is Array<Any>:
        var mpArray = Array<MessagePackValue>()

        let arrayVal = anyVal as! Array<Any>
        for value in arrayVal {
            if let mpValue = anyToMPValue(value) {
                mpArray.append(mpValue)
            } else {
                print("failed to convert")
                print(value)
            }
        }
        return MessagePackValue(mpArray)

    case is Dictionary<String, Any>:
        var mpDict = [MessagePackValue : MessagePackValue]()

        let dictVal = anyVal as! Dictionary<String, Any>
        for (key,value) in dictVal {
            let mpKey = MessagePackValue(key)
            if let mpValue = anyToMPValue(value) {
                mpDict[mpKey] = mpValue
            } else {
                print("failed to convert")
                print(value)
            }
        }
        return MessagePackValue(mpDict)

    case is Data:
        return MessagePackValue(anyVal as! Data)

    default:
        return nil;
    }
}
