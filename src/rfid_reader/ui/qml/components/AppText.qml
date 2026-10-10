import QtQuick
import "../theme"

Text {
    property string textStyle: "body"
    color: Theme.text
    font.family: Theme.fontFamily
    font.pixelSize: Theme.fontSize(textStyle)
    font.weight: Theme.fontWeight(textStyle)
    elide: Text.ElideRight
    renderType: Text.NativeRendering
}
