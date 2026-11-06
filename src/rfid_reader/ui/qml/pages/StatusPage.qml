import QtQuick
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: page
    required property var uiBridge

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacing
        AppText { objectName: "statusPageTitle"; text: "Status sistema"; textStyle: "page" }
        GridLayout {
            columns: page.width < 1000 ? 1 : 2
            columnSpacing: Theme.spacing
            rowSpacing: Theme.spacing
            Layout.fillWidth: true
            Repeater {
                model: page.uiBridge.connections
                delegate: Rectangle {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.preferredHeight: 104
                    color: Theme.surface
                    radius: Theme.radius
                    border.color: Theme.border
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        AppText { text: parent.parent.modelData.label; textStyle: "section" }
                        StatusIndicator {
                            label: parent.parent.modelData.label
                            state: parent.parent.modelData.state
                            description: parent.parent.modelData.description
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
        Item { Layout.fillHeight: true }
    }
}
