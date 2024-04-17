let temperature = 0;
let accX = 0;
let accY = 0;
let accZ = 0;

let _4digit = grove.createDisplay(DigitalPin.P2, DigitalPin.P16)
_4digit.set(7)

//we should store the data and then send it via bluetooth every minute
//this is to decrease power usage and maintain efficient usage.

basic.forever(function () {
 basic.showIcon(IconNames.Heart)
    temperature = input.temperature()
    accX = input.acceleration(Dimension.X)
    accY = input.acceleration(Dimension.Y)
    accZ = input.acceleration(Dimension.Z)

    _4digit.show(accX)
})

input.onButtonPressed(Button.A, function() {
    let dataToSend = 'Temp: ${temperature}, AccX: ${accX}, AccY: ${accY}, AccZ: ${accZ}';
})