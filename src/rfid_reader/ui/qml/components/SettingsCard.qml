import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: card
    property string title: ""
    default property alias content: body.data
    implicitHeight: body.implicitHeight + 40
    color: Theme.surface
    radius: Theme.radius
    border.color: Theme.border
    ColumnLayout {
        id: body
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 20
        spacing: 12
        AppText { text: card.title; textStyle: "section"; Layout.fillWidth: true }
    }
}
