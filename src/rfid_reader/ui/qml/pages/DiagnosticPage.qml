import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: page
    objectName: "diagnosticPage"
    property var diagnosticBridge: null
    signal backRequested()
    contentWidth: availableWidth
    clip: true

    ColumnLayout {
        width: page.availableWidth
        spacing: Theme.spacing
        RowLayout {
            Layout.fillWidth: true
            AppText { text: "Diagnóstico Waveshare"; textStyle: "page"; Layout.fillWidth: true }
            ActionButton { text: "Voltar"; variant: "secondary"; onClicked: page.backRequested() }
        }
        AppText {
            text: page.diagnosticBridge ? page.diagnosticBridge.diagnosticMessage : "Diagnóstico indisponível"
            color: Theme.mutedText
            Layout.fillWidth: true
        }
        RowLayout {
            ActionButton {
                objectName: "diagnosticConnectButton"
                text: "Conectar"; enabled: !!page.diagnosticBridge
                onClicked: page.diagnosticBridge.connectDiagnostic()
            }
            ActionButton {
                objectName: "diagnosticDisconnectButton"
                text: "Desconectar"; variant: "secondary"
                enabled: !!page.diagnosticBridge && !page.diagnosticBridge.automaticEnabled
                onClicked: page.diagnosticBridge.disconnectDiagnostic()
            }
        }
        SettingsCard {
            title: "Entradas digitais"
            Layout.fillWidth: true
            Repeater {
                model: 5
                RowLayout {
                    required property int index
                    readonly property var state: page.diagnosticBridge ? page.diagnosticBridge.diagnosticInputs[index] : null
                    AppText { text: "DI" + (parent.index + 1); Layout.preferredWidth: 60 }
                    StatusIndicator {
                        state: parent.state === true ? "ok" : parent.state === false ? "unknown" : "checking"
                        description: parent.state === true ? "ATIVA" + (parent.index < 2 ? " · feixe livre" : "")
                                     : parent.state === false ? "DESATIVADA" + (parent.index < 2 ? " · feixe interrompido" : "")
                                     : "Desconhecido"
                    }
                }
            }
        }
        SettingsCard {
            title: "Relés"
            Layout.fillWidth: true
            Repeater {
                model: 8
                RowLayout {
                    id: relayRow
                    required property int index
                    readonly property var state: page.diagnosticBridge ? page.diagnosticBridge.diagnosticRelays[index] : null
                    readonly property bool commandEnabled: !!page.diagnosticBridge && page.diagnosticBridge.diagnosticConnected && !(index < 3 && page.diagnosticBridge.automaticEnabled)
                    AppText { text: "CH" + (relayRow.index + 1); Layout.preferredWidth: 60 }
                    StatusIndicator {
                        state: relayRow.state === true ? "ok" : "unknown"
                        description: relayRow.state === true ? "ON" : relayRow.state === false ? "OFF" : "Desconhecido"
                        Layout.preferredWidth: 140
                    }
                    ActionButton {
                        objectName: "relayOn" + (relayRow.index + 1)
                        text: "Ligar"; variant: "success"; enabled: relayRow.commandEnabled
                        onClicked: page.diagnosticBridge.setRelay(relayRow.index + 1, true)
                    }
                    ActionButton {
                        objectName: "relayOff" + (relayRow.index + 1)
                        text: "Desligar"; variant: "secondary"; enabled: relayRow.commandEnabled
                        onClicked: page.diagnosticBridge.setRelay(relayRow.index + 1, false)
                    }
                }
            }
        }
    }
}
