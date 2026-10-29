import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: sidebar
    objectName: "appSidebar"
    required property var uiBridge
    property bool settingsAvailable: false
    property string currentPage: "start"
    property bool collapsed: false
    signal pageRequested(string page)
    color: Theme.sidebar
    Layout.preferredWidth: collapsed ? 72 : 208
    Layout.minimumWidth: collapsed ? 72 : 208
    Layout.maximumWidth: collapsed ? 72 : 208
    Behavior on Layout.preferredWidth { NumberAnimation { duration: 180; easing.type: Easing.InOutQuad } }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        ActionButton {
            objectName: "sidebarToggle"
            text: sidebar.collapsed ? "Expandir menu" : "Recolher menu"
            iconName: sidebar.collapsed ? "chevron-right" : "chevron-left"
            tooltipText: text
            iconOnly: sidebar.collapsed
            variant: "secondary"
            Layout.alignment: sidebar.collapsed ? Qt.AlignHCenter : Qt.AlignRight
            onClicked: sidebar.collapsed = !sidebar.collapsed
        }
        ActionButton {
            objectName: "startNavigation"
            text: "Start"
            iconName: "start"
            iconOnly: sidebar.collapsed
            tooltipText: "Start"
            variant: sidebar.currentPage === "start" ? "primary" : "secondary"
            Layout.fillWidth: true
            onClicked: sidebar.pageRequested("start")
        }
        ActionButton {
            objectName: "settingsNavigation"
            text: "Configurações"
            iconName: "settings"
            iconOnly: sidebar.collapsed
            tooltipText: "Configurações"
            variant: sidebar.currentPage === "settings" ? "primary" : "secondary"
            enabled: sidebar.settingsAvailable
            Layout.fillWidth: true
            ToolTip.visible: hovered
            ToolTip.text: "Configurações da estação."
            onClicked: sidebar.pageRequested("settings")
        }
        Item { Layout.fillHeight: true }
        AppText { visible: !sidebar.collapsed; text: "Tema"; textStyle: "caption"; color: Theme.secondaryText }
        StyledComboBox {
            objectName: "themeSelector"
            visible: !sidebar.collapsed
            Layout.fillWidth: true
            model: ["Corporate Dark", "Navy Dark"]
            currentIndex: sidebar.uiBridge.theme === "navy" ? 1 : 0
            onActivated: function(index) {
                sidebar.uiBridge.selectTheme(index === 1 ? "navy" : "corporate");
            }
        }
        ActionButton {
            objectName: "themeButton"
            visible: sidebar.collapsed
            text: "Tema"
            iconName: "theme"
            iconOnly: true
            tooltipText: "Tema"
            variant: "secondary"
            Layout.alignment: Qt.AlignHCenter
            onClicked: themePopup.open()
        }
        AppText {
            visible: sidebar.uiBridge.simulated && !sidebar.collapsed
            text: "Cenário simulado"; textStyle: "caption"; color: Theme.secondaryText
        }
        StyledComboBox {
            objectName: "scenarioSelector"
            visible: sidebar.uiBridge.simulated && !sidebar.collapsed
            readonly property var scenarioNames: ["ready", "reading", "failure", "checking", "empty"]
            Layout.fillWidth: true
            model: ["Sistema apto", "Leitura em andamento", "Falha", "Verificando", "Sem registros"]
            currentIndex: scenarioNames.indexOf(sidebar.uiBridge.scenario)
            onActivated: function(index) {
                sidebar.uiBridge.selectScenario(scenarioNames[index]);
            }
        }
        AppText {
            visible: !sidebar.collapsed
            Layout.fillWidth: true
            text: sidebar.uiBridge.simulated ? "Fase 1 · sem hardware\nNenhuma chamada ao Backend."
                 : "DSV RFID · Estação de leitura"
            textStyle: "caption"
            color: Theme.mutedText
            wrapMode: Text.WordWrap
        }
    }

    Popup {
        id: themePopup
        x: sidebar.width + 8
        y: sidebar.height - height - 12
        padding: 12
        background: Rectangle { color: Theme.surface; border.color: Theme.border; radius: Theme.smallRadius }
        contentItem: ColumnLayout {
            AppText { text: "Tema"; textStyle: "caption"; color: Theme.secondaryText }
            StyledComboBox {
                objectName: "collapsedThemeSelector"
                Layout.preferredWidth: 170
                model: ["Corporate Dark", "Navy Dark"]
                currentIndex: sidebar.uiBridge.theme === "navy" ? 1 : 0
                onActivated: function(index) {
                    sidebar.uiBridge.selectTheme(index === 1 ? "navy" : "corporate");
                    themePopup.close();
                }
            }
        }
    }
}
