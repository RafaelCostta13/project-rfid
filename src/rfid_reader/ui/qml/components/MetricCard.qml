import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: card
    property int count: 0
    implicitHeight: 116
    color: Theme.surface
    radius: Theme.radius
    border.color: Theme.border
    AppText {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 18
        text: "EPCs encontrados"
        textStyle: "card"
        color: Theme.secondaryText
    }
    AppText {
        objectName: "foundCount"
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 10
        text: card.count.toString()
        textStyle: "kpi"
    }
}
