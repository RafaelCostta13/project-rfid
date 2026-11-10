import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: page
    objectName: "settingsPage"
    property var settingsBridge: null
    property var uiBridge: null
    property var diagnosticBridge: null
    property var epcPrefixDrafts: []
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
        if (section === "all" || section === "epc_filter") {
            epcFilterEnabled.checked = fields.epc_filter_enabled;
            epcPrefixDrafts = fields.epc_prefixes;
        }
        if (section === "all" || section === "audio") {
            audioEnabled.checked = fields.audio_enabled;
            audioInterval.value = fields.audio_interval_ms;
        }
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
            id: settingsGrid
            objectName: "settingsGrid"
            columns: page.availableWidth >= 850 ? 2 : 1
            Layout.fillWidth: true
            columnSpacing: Theme.spacing
            rowSpacing: Theme.spacing
            SettingsCard {
                objectName: "readerSettingsCard"
                title: "Configurações RFID"
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
            }
            SettingsCard {
                objectName: "waveshareSettingsCard"
                title: "Configurações da Waveshare"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                FormField { id: serialPort; fieldName: "serialPortField"; label: "Porta COM"; placeholderText: "Não configurada"; enabled: !page.isBusy; Layout.fillWidth: true }
                FormField { id: baud; fieldName: "baudField"; label: "Baud rate"; enabled: !page.isBusy; Layout.fillWidth: true }
                GridLayout {
                    columns: 2
                    Layout.fillWidth: true
                    columnSpacing: Theme.spacing
                    rowSpacing: Theme.spacing
                    FormField { id: bits; objectName: "bitsForm"; fieldName: "bitsField"; label: "Data bits"; enabled: !page.isBusy; Layout.fillWidth: true }
                    FormField { id: parity; objectName: "parityForm"; fieldName: "parityField"; label: "Paridade"; enabled: !page.isBusy; Layout.fillWidth: true }
                    FormField { id: stopBits; objectName: "stopBitsForm"; fieldName: "stopBitsField"; label: "Stop bits"; enabled: !page.isBusy; Layout.fillWidth: true }
                    FormField { id: device; objectName: "deviceForm"; fieldName: "deviceField"; label: "Device ID"; enabled: !page.isBusy; Layout.fillWidth: true }
                }
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
                objectName: "audioSettingsCard"
                title: "Configurações de Áudio"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                AppText { text: "Bip RFID"; textStyle: "card" }
                CheckBox { id: audioEnabled; objectName: "audioEnabled"; text: "Som de leitura"; enabled: !page.isBusy }
                RowLayout {
                    Layout.fillWidth: true
                    AppText { text: "Intervalo entre bips (ms)"; Layout.fillWidth: true }
                    SpinBox { id: audioInterval; objectName: "audioInterval"; from: 200; to: 1000; stepSize: 50; enabled: !page.isBusy && audioEnabled.checked }
                }
                ActionButton { objectName: "audioSaveButton"; text: "Salvar áudio"; enabled: !page.isBusy; onClicked: page.settingsBridge.saveAudio(audioEnabled.checked, audioInterval.value) }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.audio : null; Layout.fillWidth: true }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: Theme.border }
                AppText { text: "Notificação por voz"; textStyle: "card" }
                AppText { text: "Voz e idioma"; textStyle: "caption"; color: Theme.secondaryText }
                ActionButton { text: "Carregar vozes do Windows"; enabled: !!page.settingsBridge && !page.isBusy; onClicked: page.settingsBridge.loadVoices() }
                StyledComboBox {
                    id: voiceChoice
                    objectName: "voiceChoice"
                    Layout.fillWidth: true
                    model: page.settingsBridge ? page.settingsBridge.voices : []
                    textRole: "label"
                    valueRole: "name"
                    currentIndex: indexOfValue(page.settingsBridge ? page.settingsBridge.selectedVoice : "")
                    enabled: !page.isBusy && count > 0
                }
                ActionButton { text: "Salvar voz"; enabled: !page.isBusy && voiceChoice.currentIndex >= 0; onClicked: page.settingsBridge.saveVoice(voiceChoice.currentValue) }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.voice : null; Layout.fillWidth: true }
                AppText { text: "Quantidade de caixas"; textStyle: "caption"; color: Theme.secondaryText }
                SpinBox {
                    id: voiceQuantity
                    objectName: "voiceQuantity"
                    from: 0; to: 9999; value: 10
                    enabled: !!page.settingsBridge && !page.settingsBridge.voiceTesting
                    Layout.fillWidth: true
                }
                AppText {
                    objectName: "voiceMessagePreview"
                    text: page.settingsBridge ? "Mensagem: " + page.settingsBridge.voiceMessage(voiceQuantity.value) : ""
                    textStyle: "caption"; color: Theme.secondaryText
                }
                ActionButton {
                    objectName: "voiceTestButton"
                    text: page.settingsBridge && page.settingsBridge.voiceTesting ? "Reproduzindo..." : "Testar voz"
                    enabled: !!page.settingsBridge && !page.settingsBridge.voiceTesting
                    onClicked: page.settingsBridge.testVoice(voiceQuantity.value)
                }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.voiceFeedback : null; Layout.fillWidth: true }
            }
            SettingsCard {
                objectName: "epcFilterSettingsCard"
                title: "Filtro EPC"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                CheckBox {
                    id: epcFilterEnabled
                    objectName: "epcFilterEnabled"
                    text: "Habilitar filtro de EPC"
                    enabled: !page.isBusy
                }
                AppText {
                    text: "Prefixos autorizados (6 caracteres hexadecimais)"
                    textStyle: "caption"
                    color: Theme.secondaryText
                }
                ScrollView {
                    objectName: "epcPrefixList"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 220
                    Layout.maximumHeight: 220
                    clip: true
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.availableWidth
                        spacing: 4
                        Repeater {
                            model: page.epcPrefixDrafts
                            delegate: RowLayout {
                                required property string modelData
                                required property int index
                                Layout.fillWidth: true
                                AppText { text: modelData; textStyle: "caption"; Layout.fillWidth: true }
                                ActionButton {
                                    text: "Remover"
                                    variant: "secondary"
                                    implicitHeight: 32
                                    enabled: !page.isBusy
                                    onClicked: {
                                        let values = page.epcPrefixDrafts.slice();
                                        values.splice(index, 1);
                                        page.epcPrefixDrafts = values;
                                    }
                                }
                            }
                        }
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    FormField { id: newEpcPrefix; fieldName: "newEpcPrefixField"; label: "Novo prefixo"; enabled: !page.isBusy; Layout.fillWidth: true }
                    ActionButton {
                        objectName: "epcPrefixAddButton"
                        text: "Adicionar"
                        variant: "secondary"
                        enabled: !page.isBusy
                        onClicked: {
                            let value = newEpcPrefix.text.trim().toUpperCase();
                            if (value !== "") {
                                let values = page.epcPrefixDrafts.slice();
                                values.push(value);
                                page.epcPrefixDrafts = values;
                                newEpcPrefix.text = "";
                            }
                        }
                    }
                }
                ActionButton {
                    objectName: "epcFilterSaveButton"
                    text: "Salvar filtro"
                    enabled: !page.isBusy
                    onClicked: page.settingsBridge.saveEpcFilter(epcFilterEnabled.checked, page.epcPrefixDrafts)
                }
                FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.epc_filter : null; Layout.fillWidth: true }
            }
            SettingsCard {
                objectName: "dockSettingsCard"
                title: "Doca Estação"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                AppText { text: "Selecionar doca"; textStyle: "caption"; color: Theme.secondaryText }
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
                objectName: "backendSettingsCard"
                title: "Backend RFID"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
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
            SettingsCard {
                objectName: "testToolsSettingsCard"
                title: "Ferramentas de Teste"
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                AppText { text: "Simulador RFID"; textStyle: "caption"; color: Theme.secondaryText }
                ActionButton { objectName: "rfidSimulatorButton"; text: "Simulador RFID"; iconName: "flask-conical"; enabled: !!page.uiBridge; onClicked: simulator.open() }
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
    Popup {
        id: simulator
        objectName: "rfidSimulator"
        parent: Overlay.overlay
        modal: true
        focus: true
        anchors.centerIn: parent
        width: Math.min(900, parent.width - 48)
        height: Math.min(650, parent.height - 48)
        padding: 20
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: Theme.radius }
        onClosed: if (page.uiBridge) page.uiBridge.closeSimulation()
        ColumnLayout {
            anchors.fill: parent
            spacing: 12
            AppText { text: "Simulador RFID"; textStyle: "section" }
            AppText { objectName: "simulatorState"; text: page.uiBridge && page.uiBridge.simulationActive ? "Simulação ativa" : page.uiBridge && page.uiBridge.simulationPresenting ? "Simulação finalizada" : "Sessão: Inativa"; textStyle: "caption"; color: Theme.secondaryText }
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 96
                    count: page.uiBridge && page.uiBridge.simulationFoundCount !== undefined ? page.uiBridge.simulationFoundCount : 0
                    title: "EPCs encontrados"
                    accentColor: Theme.success
                    countObjectName: "simulationFoundCount"
                }
                MetricCard {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 96
                    count: page.uiBridge && page.uiBridge.simulationExtraBoxCount !== undefined ? page.uiBridge.simulationExtraBoxCount : 0
                    title: "Extra box"
                    accentColor: Theme.extraBoxAccent
                    countObjectName: "simulationExtraBoxCount"
                }
            }
            AppText { text: "Registros simulados"; textStyle: "caption"; color: Theme.secondaryText }
            StyledTable {
                objectName: "simulationTagTable"
                tableModel: page.uiBridge && page.uiBridge.simulationTagModel ? page.uiBridge.simulationTagModel : page.uiBridge.tagModel
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 180
            }
            ActionButton { objectName: "simulationStartButton"; text: "Iniciar sessão"; enabled: !!page.uiBridge && !page.uiBridge.simulationActive; onClicked: page.uiBridge.startSimulation() }
            RowLayout {
                Layout.fillWidth: true
                ActionButton { objectName: "simulationFoundButton"; text: "EPC encontrado"; enabled: !!page.uiBridge && !!page.uiBridge.simulationActive; Layout.fillWidth: true; onClicked: page.uiBridge.simulateFound() }
                ActionButton { objectName: "simulationExtraButton"; text: "Extra box"; variant: "secondary"; enabled: !!page.uiBridge && !!page.uiBridge.simulationActive; Layout.fillWidth: true; onClicked: page.uiBridge.simulateExtraBox() }
            }
            ActionButton { objectName: "simulationFinishButton"; text: "Finalizar sessão"; variant: "danger"; enabled: !!page.uiBridge && !!page.uiBridge.simulationActive; onClicked: page.uiBridge.finishSimulation() }
        }
    }
}
