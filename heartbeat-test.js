// PROF's Code
control.onEvent(EventBusSource.MICROBIT_ID_IO_P0, EventBusValue.MICROBIT_PIN_EVT_RISE, function () {
    // Notes:
    // - Opening up the clip counts as 2 events when opening for prolonged period of time
    // - Opening up the clip counts as 1 event when opening momentarily
    // - Closing the clip counts as 1 event
    // - heart icon shows up indefinitely when clip is closed on finger/earlobe
    
    basic.showIcon(IconNames.Heart)
    basic.pause(100)
    basic.clearScreen()
})
basic.showIcon(IconNames.Yes)
pins.setEvents(DigitalPin.P0, PinEventType.Edge)

// Suggestions from Gemini
// To calculate your heart rate, you'd need to modify the code to:

// Detect both rising and falling edges of the signal from the heart rate sensor.
// Measure the time between consecutive rising or falling edges (intervals between heartbeats).
// Calculate the heart rate in beats per minute (BPM) by converting the time interval between beats.

// GPT code
let lastBeatTime = 0
let beatsPerMinute = 0
let sensorAttached = false
let sensorAttachedTime = 0
basic.showIcon(IconNames.Yes)

// Configure pin P0 to detect rising edges
pins.setEvents(DigitalPin.P0, PinEventType.Edge)

// Press A once sensor is attached/worn
input.onButtonPressed(Button.A, function () {
    sensorAttached = true
    sensorAttachedTime = input.runningTime()
})

control.onEvent(EventBusSource.MICROBIT_ID_IO_P0, EventBusValue.MICROBIT_PIN_EVT_RISE, function () {
    if(sensorAttached) {
        let currentTime =  input.runningTime() - sensorAttachedTime
        let timeSinceLastBeat = currentTime - lastBeatTime
        lastBeatTime = currentTime
        // Calculate beats per minute
        beatsPerMinute = 60000 / timeSinceLastBeat
        basic.showNumber(beatsPerMinute) 
        serial.writeNumber(beatsPerMinute)
    } else {
        basic.showIcon(IconNames.No)
    }
})

// claude code + src06 frm lecture6
let count = 0;
let doCounting = false;
let startTime = 0;
let currentTime = 0;

//on start
basic.showIcon(IconNames.Happy)
basic.pause(1000)
basic.clearScreen()

pins.setEvents(DigitalPin.P0, PinEventType.Edge);

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
                const heartRate = count * 4;
                basic.showNumber(heartRate);
            }
            startTime = input.runningTime();
            count = 0;
        }
    }
}