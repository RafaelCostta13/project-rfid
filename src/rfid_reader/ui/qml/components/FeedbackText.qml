import QtQuick
import "../theme"

AppText {
    property var feedback: null
    text: feedback ? feedback.message : ""
    visible: text.length > 0
    color: feedback ? Theme.stateColor(feedback.state) : Theme.mutedText
    textStyle: "caption"
    wrapMode: Text.WordWrap
    elide: Text.ElideNone
}
