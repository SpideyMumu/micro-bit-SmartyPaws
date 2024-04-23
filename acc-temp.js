let temperature = 0;
let accX = 0;
let accY = 0;
let accZ = 0;
let steps = 0;
let isReady = false;
let _4digit = grove.createDisplay(DigitalPin.P2, DigitalPin.P16)
_4digit.set(7)

//we should store the data and then send it via bluetooth every minute
//this is to decrease power usage and maintain efficient usage.

// On gesture shake is too insensitive
input.onGesture(Gesture.Shake, function() {
    steps++;
})

input.onButtonPressed(Button.A, function() {
    isReady = true
})

control.inBackground( () => {
    while (!isReady) {
        basic.showIcon(IconNames.Sad)
    }

    while (isReady) {
        basic.showNumber(steps);
        basic.pause(500)
    }
})

// basic.forever(function () {
//     basic.showIcon(IconNames.Heart)
//     temperature = input.temperature()
//     accX = input.acceleration(Dimension.X)
//     accY = input.acceleration(Dimension.Y)
//     accZ = input.acceleration(Dimension.Z)

//     _4digit.show(accX)
// })

// input.onButtonPressed(Button.A, function () {
//     let dataToSend = 'Temp: ${temperature}, AccX: ${accX}, AccY: ${accY}, AccZ: ${accZ}';
// })