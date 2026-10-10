import QtQuick
import QtQuick.Controls
import "../theme"

TextField {
    implicitHeight: 40
    leftPadding: 12
    rightPadding: 12
    font.family: Theme.fontFamily
    font.pixelSize: Theme.fontSize("body")
    color: Theme.text
    placeholderTextColor: Theme.mutedText
    selectionColor: Theme.primary
    selectedTextColor: Theme.text
    selectByMouse: true
    background: Rectangle {
        color: Theme.background
        radius: Theme.smallRadius
        border.color: parent.activeFocus ? Theme.primaryHover : Theme.border
        border.width: parent.activeFocus ? 2 : 1
    }
}
