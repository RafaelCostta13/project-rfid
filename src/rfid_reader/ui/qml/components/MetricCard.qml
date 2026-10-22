import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: card
    property int count: 0
    property string title: "EPCs encontrados"
    property color accentColor: Theme.success
    property string countObjectName: "foundCount"
    implicitHeight: 116
    color: Theme.surface
    radius: Theme.radius
    border.color: Theme.border
    AppText {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 18
        text: card.title
        textStyle: "card"
        color: Theme.secondaryText
    }
    AppText {
        objectName: card.countObjectName
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 10
        text: card.count.toString()
        textStyle: "kpi"
        color: card.accentColor
    }
}
