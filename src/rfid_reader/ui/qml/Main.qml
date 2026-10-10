import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "theme"
import "components"
import "pages"

ApplicationWindow {
    id: window
    objectName: "prototypeWindow"
    required property var uiBridge
    property var settingsBridge: null
    property var diagnosticBridge: null
    property string initialPage: "start"
    property string currentPage: initialPage
    width: 1366
    height: 768
    minimumWidth: 850
    minimumHeight: 480
    title: diagnosticBridge ? "DSV RFID" : settingsBridge ? "DSV RFID · Configurações locais" : "DSV RFID · Protótipo simulado · Fase 1"
    color: Theme.background
    font.family: Theme.fontFamily

    Binding { target: Theme; property: "navy"; value: window.uiBridge.theme === "navy" }
    onClosing: {
        if (diagnosticBridge) diagnosticBridge.beginClose();
        if (settingsBridge) settingsBridge.beginClose();
    }

    function navigate(page) {
        if (page === "settings" && !settingsBridge) return;
        if (page === "settings" && currentPage !== page) settingsPage.refresh("all");
        currentPage = page;
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        AppHeader { bannerText: window.uiBridge.bannerText; Layout.fillWidth: true }
        Rectangle {
            color: Theme.alternate
            Layout.fillWidth: true
            implicitHeight: 48
            RowLayout {
                objectName: "connectionIndicators"
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 24
                spacing: 28
                Repeater {
                    model: window.uiBridge.connections
                    StatusIndicator {
                        required property var modelData
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        label: modelData.label
                        state: modelData.state
                        description: modelData.description
                    }
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            AppSidebar {
                uiBridge: window.uiBridge
                settingsAvailable: !!window.settingsBridge
                currentPage: window.currentPage
                onPageRequested: function(page) { window.navigate(page); }
                Layout.fillHeight: true
            }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: window.width < 1100 ? 16 : 28
                currentIndex: window.currentPage === "diagnostic" ? 2 : window.currentPage === "settings" ? 1 : 0
                StartPage { uiBridge: window.uiBridge }
                SettingsPage {
                    id: settingsPage
                    settingsBridge: window.settingsBridge
                    diagnosticBridge: window.diagnosticBridge
                    onDiagnosticRequested: window.navigate("diagnostic")
                }
                DiagnosticPage {
                    diagnosticBridge: window.diagnosticBridge
                    onBackRequested: window.navigate("settings")
                }
            }
        }
    }
}
