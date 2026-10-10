import QtQuick
import QtQuick.Controls
import "../theme"

ComboBox {
    id: control
    implicitHeight: 38
    leftPadding: 12
    rightPadding: 28
    font.family: Theme.fontFamily
    font.pixelSize: Theme.fontSize("caption")
    contentItem: TextField {
        text: control.editable ? control.editText : control.displayText
        readOnly: !control.editable
        padding: 0
        font: control.font
        color: Theme.text
        selectionColor: Theme.primary
        selectedTextColor: Theme.text
        selectByMouse: control.editable
        background: null
        onTextEdited: { if (control.editable) control.editText = text; }
        verticalAlignment: Text.AlignVCenter
    }
    indicator: AppText {
        x: control.width - width - 12
        y: (control.height - height) / 2
        text: "⌄"
        color: Theme.secondaryText
    }
    background: Rectangle {
        color: Theme.alternate
        radius: Theme.smallRadius
        border.color: control.activeFocus ? Theme.primaryHover : Theme.border
    }
    delegate: ItemDelegate {
        required property int index
        required property var modelData
        width: control.width
        implicitHeight: 38
        highlighted: control.highlightedIndex === index
        contentItem: AppText { text: modelData; textStyle: "caption" }
        background: Rectangle { color: parent.highlighted ? Theme.primary : Theme.alternate }
    }
    popup: Popup {
        y: control.height + 4
        width: control.width
        padding: 6
        implicitHeight: contentItem.implicitHeight + 12
        background: Rectangle {
            color: Theme.alternate
            border.color: Theme.border
            radius: Theme.smallRadius
        }
        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
        }
    }
}
