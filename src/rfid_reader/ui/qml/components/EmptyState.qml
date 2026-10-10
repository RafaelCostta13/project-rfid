import QtQuick
import QtQuick.Layouts
import "../theme"

ColumnLayout {
    spacing: 8
    AppText {
        text: "Nenhum registro encontrado"
        textStyle: "card"
        Layout.alignment: Qt.AlignHCenter
    }
    AppText {
        text: "Os registros da sessão aparecerão aqui."
        textStyle: "caption"
        color: Theme.mutedText
        Layout.alignment: Qt.AlignHCenter
    }
}
