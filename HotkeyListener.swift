//
// HotkeyListener.swift
// Native macOS hotkey listener met proper entitlements
// Geen permission issues, altijd betrouwbaar
//

import Cocoa
import Carbon

class HotkeyListener {
    private var eventTap: CFMachPort?
    private var runLoopSource: CFRunLoopSource?
    private var daemonPID: Int32 = 0
    private var isPressed = false

    // PID file voor communicatie met Python daemon
    let pidFile = NSHomeDirectory() + "/.typtalk_pid"

    init() {
        print("🎧 TypTalk Native Hotkey Listener")
        print("==================================")
        loadDaemonPID()
    }

    func loadDaemonPID() {
        if let pidString = try? String(contentsOfFile: pidFile, encoding: .utf8),
           let pid = Int32(pidString.trimmingCharacters(in: .whitespacesAndNewlines)) {
            daemonPID = pid
            print("✓ Python daemon PID: \(pid)")
        } else {
            print("⚠️  Geen daemon PID gevonden")
            print("   Start eerst: ./venv/bin/python3 typtalk_daemon_v2.py &")
            exit(1)
        }
    }

    func start() {
        print("✓ Luisteren naar rechter Alt/Option toets...")
        print("✓ Druk Ctrl+C om te stoppen")
        print("==================================")
        print()

        // Create event tap
        let eventMask = (1 << CGEventType.keyDown.rawValue) | (1 << CGEventType.keyUp.rawValue) | (1 << CGEventType.flagsChanged.rawValue)

        guard let tap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: CGEventMask(eventMask),
            callback: { (proxy, type, event, refcon) -> Unmanaged<CGEvent>? in
                let listener = Unmanaged<HotkeyListener>.fromOpaque(refcon!).takeUnretainedValue()
                return listener.handleEvent(proxy: proxy, type: type, event: event)
            },
            userInfo: Unmanaged.passUnretained(self).toOpaque()
        ) else {
            print("❌ FOUT: Kan event tap niet aanmaken")
            print()
            print("Mogelijke oorzaken:")
            print("  1. Accessibility permissions niet gegeven")
            print("  2. App niet in Systeeminstellingen toegevoegd")
            print()
            print("FIX: Open Systeeminstellingen > Privacy & Beveiliging > Toegankelijkheid")
            print("     Voeg toe: Terminal.app (of deze applicatie)")
            exit(1)
        }

        eventTap = tap
        runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: tap, enable: true)

        // Run loop
        CFRunLoopRun()
    }

    func handleEvent(proxy: CGEventTapProxy, type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        // Check voor rechter Alt/Option (keyCode 61)
        let keyCode = event.getIntegerValueField(.keyboardEventKeycode)

        // Rechter Option/Alt key = code 61
        if keyCode == 61 {
            if type == .keyDown && !isPressed {
                isPressed = true
                print("🎤 START (rechter Alt ingedrukt)")
                sendSignalToDaemon(signal: SIGUSR1) // Start recording
            } else if type == .keyUp && isPressed {
                isPressed = false
                print("⏹️  STOP (rechter Alt losgelaten)")
                sendSignalToDaemon(signal: SIGUSR2) // Stop recording
            }
        }

        // Ook checken via flagsChanged (modifier keys)
        if type == .flagsChanged {
            let flags = event.flags
            let rightOptionPressed = flags.contains(.maskAlternate) && flags.contains(.maskSecondaryFn)

            if rightOptionPressed && !isPressed {
                isPressed = true
                print("🎤 START (via flags)")
                sendSignalToDaemon(signal: SIGUSR1)
            } else if !rightOptionPressed && isPressed {
                isPressed = false
                print("⏹️  STOP (via flags)")
                sendSignalToDaemon(signal: SIGUSR2)
            }
        }

        return Unmanaged.passRetained(event)
    }

    func sendSignalToDaemon(signal: Int32) {
        guard daemonPID > 0 else {
            print("⚠️  Geen daemon PID, signal niet verzonden")
            return
        }

        let result = kill(daemonPID, signal)
        if result != 0 {
            print("⚠️  Signal \(signal) naar PID \(daemonPID) gefaald")
            print("   Daemon mogelijk gestopt, herlaad PID...")
            loadDaemonPID()
        }
    }
}

// Main
let listener = HotkeyListener()
listener.start()
