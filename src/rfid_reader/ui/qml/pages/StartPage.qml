import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: page
    required property var uiBridge
    ColumnLayout {
        anchors.fill: parent
        spacing: 12
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing
            MetricCard {
                Layout.fillWidth: true
                count: page.uiBridge.foundCount
                title: "EPCs encontrados"
                accentColor: Theme.success
            }
            MetricCard {
                Layout.fillWidth: true
                count: page.uiBridge.extraBoxCount
                title: "Extra box"
                accentColor: Theme.warning
                countObjectName: "extraBoxCount"
            }
        }
        Rectangle {
            color: Theme.surface
            radius: Theme.radius
            border.color: Theme.border
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 0
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 10
                RowLayout {
                    Layout.fillWidth: true
                    AppText {
                        text: "Inventário RFID automático"
                        textStyle: "section"
                        Layout.fillWidth: true
                    }
                    StatusIndicator {
                        objectName: "operationIndicator"
                        state: page.uiBridge.operationState
                        description: page.uiBridge.operationTitle
                    }
                }
                RowLayout {
                    spacing: 10
                    ActionButton {
                        objectName: "startButton"
                        text: "Iniciar leitura"
                        iconName: "play"
                        variant: "success"
                        enabled: page.uiBridge.startEnabled
                        onClicked: page.uiBridge.requestStart()
                    }
                    ActionButton {
                        objectName: "stopButton"
                        text: "Parar leitura"
                        iconName: "stop"
                        variant: "danger"
                        enabled: page.uiBridge.stopEnabled
                        onClicked: page.uiBridge.requestStop()
                    }
                    Item { Layout.fillWidth: true }
                }
                AppText { text: "Etiquetas lidas"; textStyle: "caption"; color: Theme.secondaryText }
                StyledTable {
                    tableModel: page.uiBridge.tagModel
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 150
                }
            }
        }
    }
}
