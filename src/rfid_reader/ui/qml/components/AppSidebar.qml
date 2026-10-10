import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: sidebar
    required property var uiBridge
    property bool settingsAvailable: false
    property string currentPage: "start"
    signal pageRequested(string page)
    color: Theme.sidebar
    implicitWidth: 208

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        ActionButton {
            objectName: "startNavigation"
            text: "Start"
            iconName: "start"
            variant: sidebar.currentPage === "start" ? "primary" : "secondary"
            Layout.fillWidth: true
            onClicked: sidebar.pageRequested("start")
        }
        ActionButton {
            objectName: "settingsNavigation"
            text: "Configurações"
            iconName: "settings"
            variant: sidebar.currentPage === "settings" ? "primary" : "secondary"
            enabled: sidebar.settingsAvailable
            Layout.fillWidth: true
            ToolTip.visible: hovered
            ToolTip.text: "Configurações da estação."
            onClicked: sidebar.pageRequested("settings")
        }
        Item { Layout.fillHeight: true }
        AppText {
            text: sidebar.uiBridge.simulated ? "VALIDAÇÃO VISUAL" : sidebar.uiBridge.bannerText
            textStyle: "caption"; color: Theme.mutedText
        }
        AppText { text: "Tema"; textStyle: "caption"; color: Theme.secondaryText }
        StyledComboBox {
            objectName: "themeSelector"
            Layout.fillWidth: true
            model: ["Corporate Dark", "Navy Dark"]
            currentIndex: sidebar.uiBridge.theme === "navy" ? 1 : 0
            onActivated: function(index) {
                sidebar.uiBridge.selectTheme(index === 1 ? "navy" : "corporate");
            }
        }
        AppText {
            visible: sidebar.uiBridge.simulated
            text: "Cenário simulado"; textStyle: "caption"; color: Theme.secondaryText
        }
        StyledComboBox {
            objectName: "scenarioSelector"
            visible: sidebar.uiBridge.simulated
            readonly property var scenarioNames: ["ready", "reading", "failure", "checking", "empty"]
            Layout.fillWidth: true
            model: ["Sistema apto", "Leitura em andamento", "Falha", "Verificando", "Sem registros"]
            currentIndex: scenarioNames.indexOf(sidebar.uiBridge.scenario)
            onActivated: function(index) {
                sidebar.uiBridge.selectScenario(scenarioNames[index]);
            }
        }
        AppText {
            Layout.fillWidth: true
            text: sidebar.uiBridge.simulated ? "Fase 1 · sem hardware\nNenhuma chamada ao Backend."
                 : "DSV RFID · Estação de leitura"
            textStyle: "caption"
            color: Theme.mutedText
            wrapMode: Text.WordWrap
        }
    }
}
