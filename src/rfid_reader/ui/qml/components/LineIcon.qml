import QtQuick
import "../theme"

Item {
    id: icon
    property string name: "start"
    property color strokeColor: Theme.secondaryText
    implicitWidth: 20
    implicitHeight: 20
    onStrokeColorChanged: drawing.requestPaint()
    onNameChanged: drawing.requestPaint()

    Canvas {
        id: drawing
        anchors.fill: parent
        onPaint: {
            const ctx = getContext("2d");
            ctx.reset();
            ctx.strokeStyle = icon.strokeColor;
            ctx.lineWidth = 1.5;
            ctx.lineJoin = "round";
            if (icon.name === "play") {
                ctx.beginPath(); ctx.moveTo(6, 4); ctx.lineTo(16, 10);
                ctx.lineTo(6, 16); ctx.closePath(); ctx.stroke();
            } else if (icon.name === "stop") {
                ctx.strokeRect(5, 5, 10, 10);
            } else if (icon.name === "settings") {
                ctx.beginPath(); ctx.arc(10, 10, 5, 0, Math.PI * 2); ctx.stroke();
                ctx.beginPath(); ctx.arc(10, 10, 1.5, 0, Math.PI * 2); ctx.stroke();
                for (let i = 0; i < 8; i++) {
                    const angle = i * Math.PI / 4;
                    ctx.beginPath();
                    ctx.moveTo(10 + Math.cos(angle) * 5, 10 + Math.sin(angle) * 5);
                    ctx.lineTo(10 + Math.cos(angle) * 8, 10 + Math.sin(angle) * 8);
                    ctx.stroke();
                }
            } else {
                ctx.strokeRect(3, 3, 5, 5); ctx.strokeRect(12, 3, 5, 5);
                ctx.strokeRect(3, 12, 5, 5); ctx.strokeRect(12, 12, 5, 5);
            }
        }
    }
}
