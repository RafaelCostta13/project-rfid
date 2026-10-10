import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: page
    objectName: "settingsPage"
    property var settingsBridge: null
    property var diagnosticBridge: null
    signal diagnosticRequested()
    readonly property bool isBusy: settingsBridge ? settingsBridge.busy : true
    clip: true
    contentWidth: availableWidth

    function refresh(section) {
        if (!settingsBridge) return;
        const fields = settingsBridge.fields;
        if (section === "all" || section === "reader") {
            readerName.text = fields.reader_name;
            readerHost.text = fields.reader_host;
            readerPort.text = fields.reader_port;
        }
        if (section === "all" || section === "station") {
            dock.currentIndex = dock.find(fields.station_dock);
            dock.editText = fields.station_dock;
        }
        if (section === "all" || section === "waveshare") {
            serialPort.text = fields.serial_port;
            baud.text = fields.baud_rate;
            bits.text = fields.data_bits;
            parity.text = fields.parity;
            stopBits.text = fields.stop_bits;
            device.text = fields.device_id;
        }
        if (section === "all" || section === "backend") backendUrl.text = fields.backend_url;
    }
    Component.onCompleted: refresh("all")
    Connections {
        target: page.settingsBridge
        function onFinished(section, success) { if (success) page.refresh(section); }
    }

    ColumnLayout {
        width: page.availableWidth
        spacing: Theme.spacing
        AppText { text: "Configurações"; textStyle: "page" }
        AppText {
            text: "Configuração local da estação. Salvar não conecta ou altera equipamentos."
            color: Theme.mutedText
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        GridLayout {
            columns: page.availableWidth >= 850 ? 2 : 1
            Layout.fillWidth: true
            columnSpacing: Theme.spacing
            rowSpacing: Theme.spacing
            SettingsCard {
                title: "Configurações do RFID"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                FormField { id: readerName; fieldName: "readerNameField"; label: "Nome do reader"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: readerHost; fieldName: "readerHostField"; label: "Endereço IP"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: readerPort; fieldName: "readerPortField"; label: "Porta"; enabled: !page.isBusy; Layout.fillWidth: true }
                RowLayout {
                    Layout.fillWidth: true
                    ActionButton {
                        text: "Testar conexão"; variant: "secondary"; objectName: "readerTestButton"
                        enabled: !page.isBusy && page.settingsBridge.testsAvailable
                        onClicked: page.settingsBridge.testReader(readerName.text, readerHost.text, readerPort.text)
                    }
                    ActionButton {
                        objectName: "readerSaveButton"
                        text: "Salvar configurações"
                        enabled: !page.isBusy
                        onClicked: page.settingsBridge.saveReader(readerName.text, readerHost.text, readerPort.text)
                    }
                }
                FeedbackText { objectName: "readerFeedback"; feedback: page.settingsBridge ? page.settingsBridge.feedback.reader : null; Layout.fillWidth: true }
                AppText { text: "Doca da estação"; textStyle: "card" }
                StyledComboBox {
                    id: dock
                    objectName: "dockField"
                    editable: true
                    model: page.settingsBridge ? page.settingsBridge.dockSuggestions : []
                    enabled: !page.isBusy
                    Layout.fillWidth: true
                }
                ActionButton {
                    objectName: "dockSaveButton"
                    text: "Salvar Doca"
                    enabled: !page.isBusy
                    onClicked: page.settingsBridge.saveStation(dock.editText)
                }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.station : null; Layout.fillWidth: true }
            }
            SettingsCard {
                title: "Configurações da Waveshare"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                FormField { id: serialPort; fieldName: "serialPortField"; label: "Porta COM"; placeholderText: "Não configurada"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: baud; fieldName: "baudField"; label: "Baud rate"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: bits; fieldName: "bitsField"; label: "Data bits"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: parity; fieldName: "parityField"; label: "Paridade"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: stopBits; fieldName: "stopBitsField"; label: "Stop bits"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: device; fieldName: "deviceField"; label: "Device ID"; enabled: !page.isBusy; Layout.fillWidth: true }
                RowLayout {
                    Layout.fillWidth: true
                    ActionButton {
                        text: "Testar conexão"; variant: "secondary"; objectName: "waveshareTestButton"
                        enabled: !page.isBusy && page.settingsBridge.testsAvailable
                        onClicked: page.settingsBridge.testWaveshare(serialPort.text, baud.text, bits.text, parity.text, stopBits.text, device.text)
                    }
                    ActionButton {
                        objectName: "waveshareSaveButton"
                        text: "Salvar configurações"
                        enabled: !page.isBusy
                        onClicked: page.settingsBridge.saveWaveshare(serialPort.text, baud.text, bits.text, parity.text, stopBits.text, device.text)
                    }
                }
                ActionButton {
                    text: "Testar Waveshare"; variant: "secondary"; objectName: "diagnosticButton"
                    enabled: !!page.diagnosticBridge
                    onClicked: page.diagnosticRequested()
                }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.waveshare : null; Layout.fillWidth: true }
            }
            SettingsCard {
                title: "Backend RFID"
                Layout.columnSpan: parent.columns
                Layout.fillWidth: true
                FormField { id: backendUrl; fieldName: "backendUrlField"; label: "URL base"; enabled: !page.isBusy; Layout.fillWidth: true }
                RowLayout {
                    ActionButton {
                        text: "Testar conexão"; variant: "secondary"; objectName: "backendTestButton"
                        enabled: !page.isBusy && page.settingsBridge.testsAvailable
                        onClicked: page.settingsBridge.testBackend(backendUrl.text)
                    }
                    ActionButton {
                        objectName: "backendSaveButton"
                        text: "Salvar configurações"
                        enabled: !page.isBusy
                        onClicked: page.settingsBridge.saveBackend(backendUrl.text)
                    }
                }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.backend : null; Layout.fillWidth: true }
            }
        }
        AppText {
            visible: !page.diagnosticBridge
            text: "Testes de conexão e diagnóstico serão integrados nas próximas etapas."
            textStyle: "caption"
            color: Theme.mutedText
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }
}
