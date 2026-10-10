import QtQuick
import QtQuick.Layouts
import "../theme"

ColumnLayout {
    id: field
    property string label: ""
    property string fieldName: ""
    property alias text: editor.text
    property alias placeholderText: editor.placeholderText
    spacing: 6
    AppText { text: field.label; textStyle: "caption"; color: Theme.secondaryText }
    StyledTextField { id: editor; objectName: field.fieldName; Layout.fillWidth: true }
}
