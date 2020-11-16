//
//  GeoLocation.swift
//  NDS
//
//  Created by Susumu Saito on 2020/07/08.
//  Copyright © 2020 Intelligent Framework Lab. All rights reserved.
//

import Foundation
import CoreLocation

/// `Geolocation`は、位置情報を管理するクラスです。
class Geolocation: NSObject, CLLocationManagerDelegate {
    var locationManager: CLLocationManager!
    var currentLocation: CLLocation? = nil
    
    var onUpdateLocationsHandler: (([CLLocation]) -> Void)? = nil
    var onChangeAuthorizationHandler: ((CLAuthorizationStatus) -> Void)? = nil
    
    /// 位置情報が更新された際のハンドラ関数を登録します。
    func setOnUpdateLocationsHandler(_ handler: @escaping ([CLLocation]) -> Void) { onUpdateLocationsHandler = handler }
    /// 位置情報の権限ステータスが変更された際のハンドラ関数を登録します。
    func setOnChangeAuthorizationHandler(_ handler: @escaping (CLAuthorizationStatus) -> Void) { onChangeAuthorizationHandler = handler }
    
    override init(){
        super.init()
        
        locationManager = CLLocationManager()
        locationManager.requestWhenInUseAuthorization()
        let status = getAuthorizationStatus()
        if status == .authorizedWhenInUse {
            locationManager.delegate = self
            locationManager.distanceFilter = 10
            locationManager.startUpdatingLocation()
        }
    }
    /// 現在の位置情報を取得します。
    /// - Returns: 位置情報
    func getCurrentLocation() -> CLLocation? {
        return currentLocation
    }
    
    /// 現在の位置情報の権限ステータスを取得します。
    /// - Returns: 権限ステータス
    func getAuthorizationStatus() -> CLAuthorizationStatus {
        return CLLocationManager.authorizationStatus()
    }
    
    /// 位置情報が更新された際に呼ばれる`CLLocationManagerDelegate`プロトコル準拠の関数です。
    /// これを直接呼び出すことは無く、`setOnUpdateLocationsHandler(_:)`においてハンドラ関数を登録することと等価となります。
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        currentLocation = locations.last
        if let handler = onUpdateLocationsHandler { handler(locations) }
    }

    /// 位置情報の権限ステータスが変更された際に呼ばれる`CLLocationManagerDelegate`プロトコル準拠の関数です。
    /// これを直接呼び出すことは無く、`setOnChangeAuthorizationHandler(_:)`においてハンドラ関数を登録することと等価となります。
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        if let handler = onChangeAuthorizationHandler { handler(status) }
    }
}
