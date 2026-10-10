import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    property string bannerText: "PRÉVIA QML · DADOS SIMULADOS"
    color: Theme.header
    implicitHeight: 76
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 24
        anchors.rightMargin: 24
        spacing: 18
        Rectangle {
            implicitWidth: 144
            implicitHeight: 46
            radius: Theme.smallRadius
            color: Theme.logoSurface
            Image {
                objectName: "brandLogo"
                readonly property bool ready: status === Image.Ready
                anchors.centerIn: parent
                width: 116
                height: 36
                source: "../assets/branding/dsv_logo.svg"
                sourceSize.width: width * Screen.devicePixelRatio
                sourceSize.height: height * Screen.devicePixelRatio
                fillMode: Image.PreserveAspectFit
                Accessible.name: "DSV"
            }
        }
        AppText { text: "RFID SYSTEM"; textStyle: "section" }
        Item { Layout.fillWidth: true }
        AppText {
            text: bannerText
            textStyle: "caption"
            color: Theme.mutedText
        }
    }
}
