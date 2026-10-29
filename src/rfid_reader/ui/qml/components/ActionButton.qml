import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Button {
    id: control
    property string variant: "primary"
    property string iconName: ""
    property bool iconOnly: false
    property string tooltipText: ""
    implicitHeight: 42
    implicitWidth: iconOnly ? 42 : Math.max(146, contentItem.implicitWidth + 30)
    leftPadding: iconOnly ? 10 : 15
    rightPadding: iconOnly ? 10 : 15
    hoverEnabled: true
    opacity: enabled ? 1 : 0.45
    Accessible.name: text

    contentItem: RowLayout {
        spacing: 8
        LineIcon {
            visible: control.iconName !== ""
            name: control.iconName
            strokeColor: Theme.text
        }
        AppText {
            visible: !control.iconOnly
            text: control.text
            horizontalAlignment: Text.AlignHCenter
            Layout.fillWidth: true
        }
    }
    ToolTip.visible: control.iconOnly && control.hovered
    ToolTip.text: control.tooltipText !== "" ? control.tooltipText : control.text
    background: Rectangle {
        radius: Theme.smallRadius
        color: control.variant === "success" ? Theme.successButton
             : control.variant === "danger" ? Theme.dangerButton
             : control.variant === "secondary" ? Theme.alternate
             : control.hovered ? Theme.primaryHover : Theme.primary
        border.width: control.activeFocus ? 2 : 1
        border.color: control.activeFocus ? Theme.text : Theme.border
        opacity: control.down ? 0.8 : 1
    }
}
