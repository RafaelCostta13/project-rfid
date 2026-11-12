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
                ActionButton { objectName: "antennaSettingsButton"; text: "Antenas RFID"; variant: "secondary"; enabled: !!page.settingsBridge; onClicked: antennaPopup.open() }
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
        id: antennaPopup
        objectName: "antennaSettingsPopup"
        parent: Overlay.overlay
        modal: true
        focus: true
        anchors.centerIn: parent
        width: Math.min(700, parent.width - 48)
        height: Math.min(600, parent.height - 48)
        padding: 20
        property var drafts: []
        property var levels: []
        function reload() {
            drafts = page.settingsBridge.antennaSettings();
            levels = page.settingsBridge.antennaPowerLevels();
        }
        onOpened: reload()
        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: Theme.radius }
        ColumnLayout {
            anchors.fill: parent
            AppText { text: "Configuração de Antenas RFID"; textStyle: "section" }
            AppText { objectName: "antennaCount"; text: "Antenas configuradas: " + antennaPopup.drafts.length; color: Theme.secondaryText }
            AppText { text: "Disponibilidade física das antenas não confirmada pelo reader."; color: Theme.secondaryText; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            ScrollView {
                id: antennaLevelsScroll
                objectName: "antennaLevelsScroll"
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                clip: true
                contentWidth: availableWidth
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                AppText {
                    objectName: "antennaPowerLevels"
                    width: antennaLevelsScroll.availableWidth
                    text: antennaPopup.levels.length ? "Níveis suportados (dBm): " + antennaPopup.levels.join(", ") : "Reader indisponível ou níveis de potência não informados. Conecte o reader para salvar."
                    color: Theme.secondaryText
                    wrapMode: Text.Wrap
                    elide: Text.ElideNone
                }
            }
            AppText { text: "Potências salvas serão usadas na próxima leitura."; color: Theme.secondaryText; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: availableWidth
                ColumnLayout {
                    width: parent.availableWidth
                    Repeater {
                        id: antennaRepeater
                        model: antennaPopup.drafts
                        delegate: RowLayout {
                            required property var modelData
                            required property int index
                            property alias power: antennaPowerField.text
                            Layout.fillWidth: true
                            AppText { text: "Antena " + modelData.id + " · status não confirmado"; Layout.fillWidth: true }
                            FormField {
                                id: antennaPowerField
                                label: "Potência (dBm)"
                                fieldName: "antennaPower" + modelData.id
                                text: modelData.power
                                placeholderText: "Não configurada"
                                Layout.preferredWidth: 150
                            }
                        }
                    }
                }
            }
            FeedbackText { feedback: page.settingsBridge ? page.settingsBridge.feedback.antenna : null; Layout.fillWidth: true }
            RowLayout {
                ActionButton { objectName: "antennaMapOpenButton"; text: "Mapa de leitura"; variant: "secondary"; onClicked: mappingPopup.open() }
                ActionButton { objectName: "antennaReloadButton"; text: "Recarregar"; variant: "secondary"; enabled: !page.isBusy; onClicked: antennaPopup.reload() }
                ActionButton {
                    objectName: "antennaSaveButton"
                    text: "Salvar configurações"
                    enabled: !page.isBusy
                    onClicked: {
                        let values = [];
                        for (let i = 0; i < antennaRepeater.count; ++i)
                            values.push(antennaRepeater.itemAt(i).power);
                        page.settingsBridge.saveAntennaPower(values);
                    }
                }
                ActionButton { text: "Fechar"; variant: "secondary"; onClicked: antennaPopup.close() }
            }
        }
    }
    Popup {
        id: mappingPopup
        objectName: "antennaMappingPopup"
        parent: Overlay.overlay
        modal: true
        focus: true
        anchors.centerIn: parent
        width: Math.min(1100, parent.width - 32)
        height: Math.min(760, parent.height - 32)
        padding: 18
        closePolicy: Popup.NoAutoClose
        property var antennaList: []
        property var colors: ["#55aaff", "#ff7e89", "#58d59e", "#f4cc6b", "#bf99ff", "#ffad73", "#56d5df", "#ec8ed5", "#b1df6b", "#e0b0a0", "#899cff", "#d9df9c"]
        function antennaColor(id) {
            for (let i = 0; i < antennaList.length; ++i)
                if (antennaList[i].id === id) return colors[i % colors.length];
            return "#ffffff";
        }
        onOpened: { antennaList = page.settingsBridge.antennaSettings(); page.settingsBridge.setMappingAngle(angleInput.value); mapCanvas.requestPaint(); }
        onClosed: if (page.settingsBridge.mappingReserved) page.settingsBridge.stopMapping()
        Timer { interval: 250; repeat: true; running: mappingPopup.visible && !!page.settingsBridge && page.settingsBridge.mappingActive; onTriggered: page.settingsBridge.refreshMapping() }
        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: Theme.radius }
        ColumnLayout {
            anchors.fill: parent
            spacing: 8
            AppText { text: "Mapa de leitura assistido"; textStyle: "section" }
            AppText { text: "Informe o ângulo da etiqueta. O mapa mostra RSSI, não distância ou posição física."; color: Theme.secondaryText; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            RowLayout {
                AppText { text: "Ângulo (graus)" }
                SpinBox { id: angleInput; objectName: "mappingAngle"; from: -180; to: 180; stepSize: 30; value: 0; editable: true; onValueChanged: if (page.settingsBridge) page.settingsBridge.setMappingAngle(value) }
                ActionButton { objectName: "mappingStartButton"; text: "Iniciar mapeamento"; enabled: !!page.settingsBridge && page.settingsBridge.testsAvailable && !page.settingsBridge.mappingReserved && !page.settingsBridge.mappingPending; onClicked: page.settingsBridge.startMapping() }
                ActionButton { objectName: "mappingStopButton"; text: "Parar"; variant: "danger"; enabled: !!page.settingsBridge && page.settingsBridge.mappingReserved && !page.settingsBridge.mappingPending; onClicked: page.settingsBridge.stopMapping() }
                ActionButton { objectName: "mappingClearButton"; text: "Limpar mapa"; variant: "secondary"; onClicked: page.settingsBridge.clearMapping() }
                ActionButton { objectName: "mappingCloseButton"; text: "Fechar"; variant: "secondary"; onClicked: mappingPopup.close() }
            }
            AppText { objectName: "mappingStatus"; text: page.settingsBridge ? page.settingsBridge.mappingMessage : ""; color: Theme.secondaryText; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 16
                ColumnLayout {
                    Layout.preferredWidth: Math.min(mappingPopup.width * 0.48, 450)
                    Layout.fillHeight: true
                    Canvas {
                        id: mapCanvas
                        objectName: "mappingCanvas"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        onPaint: {
                            const ctx = getContext("2d");
                            ctx.reset();
                            const cx = width / 2, cy = height / 2;
                            const radius = Math.max(1, Math.min(width, height) / 2 - 32);
                            ctx.strokeStyle = "#546170"; ctx.lineWidth = 1;
                            for (let ring = 1; ring <= 3; ++ring) {
                                ctx.beginPath(); ctx.arc(cx, cy, radius * ring / 3, 0, Math.PI * 2); ctx.stroke();
                            }
                            ctx.beginPath(); ctx.moveTo(cx - radius, cy); ctx.lineTo(cx + radius, cy); ctx.moveTo(cx, cy - radius); ctx.lineTo(cx, cy + radius); ctx.stroke();
                            ctx.fillStyle = "#c0cbd8"; ctx.font = "12px sans-serif";
                            ctx.fillText("0°", cx - 8, cy - radius - 8);
                            ctx.fillText("90°", cx + radius + 4, cy + 4);
                            ctx.fillText("±180°", cx - 16, cy + radius + 18);
                            ctx.fillText("-90°", cx - radius - 30, cy + 4);
                            let points = page.settingsBridge ? page.settingsBridge.mappingPoints : [];
                            for (let a = 0; a < mappingPopup.antennaList.length; ++a) {
                                let antenna = mappingPopup.antennaList[a].id;
                                let series = points.filter(function(p) { return p.antenna === antenna; }).sort(function(x, y) { return x.angle - y.angle; });
                                ctx.strokeStyle = mappingPopup.antennaColor(antenna); ctx.fillStyle = ctx.strokeStyle; ctx.lineWidth = 2;
                                ctx.beginPath();
                                for (let i = 0; i < series.length; ++i) {
                                    let p = series[i], theta = p.angle * Math.PI / 180;
                                    let strength = Math.max(0, Math.min(1, (p.rssi + 90) / 60));
                                    let x = cx + Math.sin(theta) * radius * strength, y = cy - Math.cos(theta) * radius * strength;
                                    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
                                }
                                ctx.stroke();
                                for (let i = 0; i < series.length; ++i) {
                                    let p = series[i], theta = p.angle * Math.PI / 180;
                                    let strength = Math.max(0, Math.min(1, (p.rssi + 90) / 60));
                                    ctx.beginPath(); ctx.arc(cx + Math.sin(theta) * radius * strength, cy - Math.cos(theta) * radius * strength, 4, 0, Math.PI * 2); ctx.fill();
                                }
                            }
                        }
                        Connections { target: page.settingsBridge; function onChanged() { mapCanvas.requestPaint(); } }
                    }
                    AppText { text: "Escala visual: centro ≤ -90 dBm; borda ≥ -30 dBm."; color: Theme.secondaryText; textStyle: "caption"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Flow {
                        Layout.fillWidth: true
                        spacing: 12
                        Repeater { model: mappingPopup.antennaList; delegate: AppText { required property var modelData; text: "● Antena " + modelData.id; color: mappingPopup.antennaColor(modelData.id); textStyle: "caption" } }
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    AppText { text: "Leituras agregadas · maior RSSI"; textStyle: "card" }
                    AppText { text: "Horário UTC  ·  EPC  ·  Antena  ·  RSSI  ·  Ângulo"; color: Theme.secondaryText; textStyle: "caption" }
                    ScrollView {
                        objectName: "mappingReadings"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        contentWidth: availableWidth
                        clip: true
                        ColumnLayout {
                            width: parent.availableWidth
                            Repeater {
                                model: page.settingsBridge ? page.settingsBridge.mappingPoints : []
                                delegate: AppText {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    text: modelData.timestamp + "  ·  " + modelData.epc + "  ·  " + modelData.antenna + "  ·  " + modelData.rssi + " dBm  ·  " + modelData.angle + "°"
                                    color: mappingPopup.antennaColor(modelData.antenna)
                                    textStyle: "caption"
                                    wrapMode: Text.WrapAnywhere
                                }
                            }
                        }
                    }
                }
            }
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
