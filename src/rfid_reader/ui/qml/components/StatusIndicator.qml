import QtQuick
import QtQuick.Layouts
import "../theme"

RowLayout {
    id: indicator
    property string label: ""
    property string state: "unknown"
    property string description: "Desconhecido"
    spacing: 8
    Accessible.role: Accessible.StaticText
    Accessible.name: label + ": " + description

    Rectangle {
        implicitWidth: 7
        implicitHeight: 7
        radius: 4
        color: Theme.stateColor(indicator.state)
    }
    AppText {
        objectName: "statusLabel"
        text: indicator.label ? indicator.label + ": " + indicator.description : indicator.description
        color: Theme.stateColor(indicator.state)
        textStyle: "caption"
        Layout.fillWidth: true
    }
}
