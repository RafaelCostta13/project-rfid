import QtQuick
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: page
    objectName: "statusPage"
    required property var uiBridge

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacing
        AppText { objectName: "statusPageTitle"; text: "Status sistema"; textStyle: "page" }
        Rectangle {
            color: Theme.surface
            radius: Theme.radius
            border.color: Theme.border
            Layout.fillWidth: true
            Layout.preferredHeight: 248
            ColumnLayout {
                id: indicators
                objectName: "statusIndicators"
                anchors.fill: parent
                anchors.margins: 20
                spacing: Theme.spacing
                Repeater {
                    model: page.uiBridge.connections
                    StatusIndicator {
                        required property var modelData
                        label: modelData.label
                        state: modelData.state
                        description: modelData.description
                        Layout.fillWidth: true
                    }
                }
            }
        }
        Item { Layout.fillHeight: true }
    }
}
