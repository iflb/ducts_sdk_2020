import Foundation
import AVFoundation

/**
 `AudioRecorder`は、マイクからのユーザー発話音声入力のデータストリームを扱うクラスです。
​
 マイク入力音声はNDSサーバーが受け付ける音声データ仕様（16-bit Linear PCM, 16000kHz, Mono, 非圧縮）に内部的に変換されて扱われます。
 */

public class AudioRecorder {
    private let audioEngine = AVAudioEngine()
    private var downMixer = AVAudioMixerNode()

    var format: AVAudioFormat!
    var formatDownSample: AVAudioFormat!

    var bufferSize = AVAudioFrameCount(1600)
    var onDataBuffer = Data()
    let onDataEventBufferCount = 16000

    var onDataEventHandler: ((Data) -> Void)?

    var player: AVAudioPlayer?

    public init() {
    }

    /// マイク入力音声の取り込みを開始します。
    public func start() throws {
        format = audioEngine.inputNode.inputFormat(forBus: 0)
        // target format
        formatDownSample = AVAudioFormat.init(commonFormat: .pcmFormatInt16,
                                              sampleRate: 16000,
                                              channels: 1,
                                              interleaved: false)!

        audioEngine.prepare()

        if audioEngine.isRunning { return }
        
//        try! AVAudioSession.sharedInstance().setCategory(.playAndRecord, mode: .voicePrompt)
//        try! AVAudioSession.sharedInstance().setActive(true)

        // swiftlint:disable:next force_try
        try! audioEngine.start()

        audioEngine.inputNode.installTap(onBus: 0, bufferSize: bufferSize, format: format, block: { (buffer: AVAudioPCMBuffer!, _: AVAudioTime!) -> Void in
            // https://github.com/tad-iizuka/PCMDownSamplingSample/blob/master/PCMDownSamplingSample/ViewController.swift
            let converter = AVAudioConverter.init(from: self.format, to: self.formatDownSample)!
            let newbuffer = AVAudioPCMBuffer(pcmFormat: self.formatDownSample, frameCapacity: AVAudioFrameCount(self.bufferSize))!
            let inputBlock: AVAudioConverterInputBlock = { (inNumPackets, outStatus) -> AVAudioBuffer? in
                outStatus.pointee = AVAudioConverterInputStatus.haveData
                let audioBuffer: AVAudioBuffer = buffer
                return audioBuffer
            }
            var error: NSError?
            converter.convert(to: newbuffer, error: &error, withInputFrom: inputBlock)

            // swiftlint:disable:next shorthand_operator
            self.onDataBuffer = self.onDataBuffer + self.pcmBufferToData(PCMBuffer: newbuffer)
            if self.onDataBuffer.count >= self.onDataEventBufferCount {
                let myheader = self.createWaveHeader(data: self.onDataBuffer, sampleRate: Int(newbuffer.format.sampleRate))
                if let handler = self.onDataEventHandler {
                    handler(myheader + self.onDataBuffer)

                    //                        self.player = try! AVAudioPlayer(data: myheader + self.onDataBuffer)
                    //                        self.player?.prepareToPlay()
                    //                        self.player?.play()
                }
                self.onDataBuffer = Data()
            }
        }
        )
    }

    /// マイク入力音声の取り込みを終了します。（`audioRecorder.startRecording()`は以降呼ばれなくなります。）
    public func stop() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
    }

    /// `startRecording()`が呼ばれた時点から、約１秒おきにコールバック関数へマイク入力音声のチャンクを渡します。
    /// - Parameter callback: コールバック関数。第一引数に１秒間の入力音声のチャンクが渡されます（PCMヘッダ付き`Data`型）。
    public func setOnDataEventHandler(_ callback: @escaping (Data) -> Void) {
        onDataEventHandler = callback
    }

    private func pcmBufferToData(PCMBuffer: AVAudioPCMBuffer) -> Data {
        let channelCount = Int(PCMBuffer.format.channelCount)
        let channels = UnsafeBufferPointer(start: PCMBuffer.int16ChannelData, count: channelCount)
        let ch0Data = Data(NSData(bytes: channels[0], length: Int(PCMBuffer.frameCapacity * PCMBuffer.format.streamDescription.pointee.mBytesPerFrame)))
        return ch0Data
    }

    private func createWaveHeader(data: Data, sampleRate: Int) -> NSData {
        let sampleRate: Int32 = Int32(sampleRate)
        let chunkSize: Int32 = 36 + Int32(data.count)
        let subChunkSize: Int32 = 16
        let format: Int16 = 1
        let channels: Int16 = 1
        let bitsPerSample: Int16 = 16
        let blockAlign: Int16 = channels * bitsPerSample / 8
        let byteRate: Int32 = sampleRate * Int32(blockAlign)
        let dataSize: Int32 = Int32(data.count)
        let header = NSMutableData()
        //    print(sampleRate, chunkSize, subChunkSize, format, channels, bitsPerSample, byteRate, blockAlign, dataSize)
        header.append([UInt8]("RIFF".utf8), length: 4)
        header.append(intToByteArray(chunkSize), length: 4)
        //WAVE
        header.append([UInt8]("WAVE".utf8), length: 4)
        //FMT
        header.append([UInt8]("fmt ".utf8), length: 4)
        header.append(intToByteArray(subChunkSize), length: 4)
        header.append(shortToByteArray(format), length: 2)
        header.append(shortToByteArray(channels), length: 2)
        header.append(intToByteArray(sampleRate), length: 4)
        header.append(intToByteArray(byteRate), length: 4)
        header.append(shortToByteArray(blockAlign), length: 2)
        header.append(shortToByteArray(bitsPerSample), length: 2)
        header.append([UInt8]("data".utf8), length: 4)
        header.append(intToByteArray(dataSize), length: 4)
        //    dump(header)
        return header
    }
    // swiftlint:disable:next identifier_name
    private func intToByteArray(_ i: Int32) -> [UInt8] {
        //    return withUnsafeBytes(of: i.littleEndian, Array.init)
        return [
            //little endian
            UInt8(truncatingIfNeeded: (i ) & 0xff),
            UInt8(truncatingIfNeeded: (i >> 8) & 0xff),
            UInt8(truncatingIfNeeded: (i >> 16) & 0xff),
            UInt8(truncatingIfNeeded: (i >> 24) & 0xff)
        ]
    }
    // swiftlint:disable:next identifier_name
    private func shortToByteArray(_ i: Int16) -> [UInt8] {
        //    return withUnsafeBytes(of: i.littleEndian, Array.init)
        return [
            //little endian
            UInt8(truncatingIfNeeded: (i ) & 0xff),
            UInt8(truncatingIfNeeded: (i >> 8) & 0xff)
        ]
    }

}
