let temp = 0;
let steps = 0;

let heartRate = 0;
let count = 0;
let doCounting = false;
let startTime = 0;
let currentTime = 0;

let simMode = false;
let isReady = false;

bluetooth.setTransmitPower(7)
bluetooth.startUartService()
let connected = false

let command = ""
let commandValue = ""
let commandKey = ""
let buffer = []

//we should store the data and then send it via bluetooth every half a minute
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

// Press button A once sensor is attached/worn
input.onButtonPressed(Button.A, function () {
    isReady = true
    basic.clearScreen()
})

input.onButtonPressed(Button.B, function () {
    basic.showNumber(steps)
})

input.onButtonPresed(Button.AB, function () {
    //adjust sim mode
    simMode = !simMode
})

// rising edge detection
control.onEvent(EventBusSource.MICROBIT_ID_IO_P0, EventBusValue.MICROBIT_PIN_EVT_RISE, function () {
    handleHeartRate();
});

function handleHeartRate() {
    count++;

    if (!doCounting) {
        if (count === 10) {
            basic.showIcon(IconNames.Heart);
            startTime = input.runningTime();
            count = 0;
            doCounting = true;
        }
    }

    if (doCounting) {
        currentTime = input.runningTime();
        if (currentTime - startTime > 15000) {
            if (count > 0) {
                heartRate = count * 4;
            }
            startTime = input.runningTime();
            count = 0;
        }
    }
}

control.inBackground(() => {
    // before setting up the sensor, we need to wait for the sensor to be attached
    while (!isReady || !connected) {
        basic.showIcon(IconNames.Sad)
    }

    // once the sensor is attached, we can start counting steps
    while (isReady || connected) {
        // NOTE: step counter is slow to display once it is double digits
        // basic.showNumber(steps)
        basic.pause(100)
        if (input.acceleration(Dimension.Strength) >= 1500) {
            steps++;
        }
    }

    // send data via serial for simulation purposes
    while(simMode) {
        temp = input.temperature()
        let dataToSend = 'temp: ${temp}, steps: ${steps}, heart_rate: ${heartRate}';
        serial.writeLine(dataToSend)
    }
})

// send data vie BLE
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
            "=steps=" + steps +
            "=temp=" + input.temperature() +
            "=heart_rate=" + heartRate)
            basic.showString("T")
        }
    }
})
