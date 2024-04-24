let temperature = 0;
let accX = 0;
let accY = 0;
let accZ = 0;
let temp = 0;
let steps = 0;

let isReady = false;
bluetooth.setTransmitPower(7)
bluetooth.startUartService()
let connected = false
let command = ""
let commandValue = ""
let commandKey = ""
let buffer = []


let _4digit = grove.createDisplay(DigitalPin.P2, DigitalPin.P16)
_4digit.set(7)

//we should store the data and then send it via bluetooth every minute
//this is to decrease power usage and maintain efficient usage.

// On gesture shake is too insensitive
// input.onGesture(Gesture.Shake, function () {
//     steps++;
// })

bluetooth.onBluetoothConnected(function () {
    connected = true
    basic.showIcon(IconNames.Happy)
})

bluetooth.onBluetoothDisconnected(function () {
    connected = false
    basic.showIcon(IconNames.No)
})

input.onButtonPressed(Button.A, function () {
    isReady = true
    basic.clearScreen()
})

input.onButtonPressed(Button.B, function () {
    basic.showNumber(steps)
})

control.inBackground(() => {
    while (!isReady || !connected) {
        basic.showIcon(IconNames.Sad)
    }

    while (isReady || connected) {
        // NOTE: step counter is slow to display once it is double digits
        // basic.showNumber(steps)
        basic.pause(100)
        if (input.acceleration(Dimension.Strength) >= 1500) {
            steps++;
        }
    }
})

bluetooth.onUartDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    basic.showString("R")

    command = bluetooth.uartReadUntil(serial.delimiters(Delimiters.NewLine))
    buffer = command.split("=")
    commandKey = buffer[0]
    commandValue = buffer[1]
    commandValue = commandValue.substr(0, commandValue.length - 1)

    if (commandKey == "sensor") {
        if (commandValue == "temp") {
            bluetooth.uartWriteString("" + 
            control.deviceName() + 
            "=temp=" + input.temperature() +
            "=steps=" + steps)
            basic.showString("T")
        }
    }
})

function calculateXYZ() {
    accX = input.acceleration(Dimension.X)
    accY = input.acceleration(Dimension.Y)
    accZ = input.acceleration(Dimension.Z)

    temp = input.temperature()
    let dataToSend = 'Temp: ${temperature}, AccX: ${accX}, AccY: ${accY}, AccZ: ${accZ}';
}