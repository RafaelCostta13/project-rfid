pragma Singleton
import QtQuick

QtObject {
    property bool navy: false
    readonly property color background: navy ? "#0b1526" : "#15191f"
    readonly property color header: navy ? "#0f1e35" : "#1c222b"
    readonly property color sidebar: navy ? "#102039" : "#1a2028"
    readonly property color surface: navy ? "#142640" : "#202730"
    readonly property color alternate: navy ? "#182d4a" : "#252e39"
    readonly property color border: navy ? "#29415e" : "#35404d"
    readonly property color primary: navy ? "#3265b2" : "#294e80"
    readonly property color primaryHover: navy ? "#3d77cb" : "#35639b"
    readonly property color text: "#f3f6fa"
    readonly property color secondaryText: "#c0cbd8"
    readonly property color mutedText: "#9daebf"
    readonly property color success: "#54d49a"
    readonly property color successButton: "#226548"
    readonly property color dangerButton: "#873b48"
    readonly property color error: "#ff8795"
    readonly property color warning: "#f4cc6b"
    readonly property color unknown: "#96a1ae"
    readonly property color logoSurface: "#ffffff"
    readonly property string fontFamily: "Segoe UI"
    readonly property int radius: 10
    readonly property int smallRadius: 6
    readonly property int spacing: 16
    readonly property int rowHeight: 48

    function stateColor(state) {
        if (state === "ok") return success;
        if (state === "error") return error;
        if (state === "warning" || state === "checking") return warning;
        return unknown;
    }
    function fontSize(style) {
        const sizes = { page: 27, section: 18, card: 14, body: 14, caption: 12,
                        kpi: 35, tableHeader: 12, tableCell: 14 };
        return sizes[style] || sizes.body;
    }
    function fontWeight(style) {
        return ["page", "section", "card", "kpi", "tableHeader"].includes(style)
            ? Font.DemiBold : Font.Normal;
    }
}
