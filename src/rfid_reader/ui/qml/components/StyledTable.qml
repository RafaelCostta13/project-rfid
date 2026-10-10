import QtQuick
import QtQuick.Controls
import "../theme"

Rectangle {
    id: container
    required property var tableModel
    property int selectedRow: -1
    readonly property var headings: tableModel.columnTitles
    color: Theme.surface
    border.color: Theme.border
    radius: Theme.smallRadius
    clip: true

    function columnWidth(column) {
        const widths = [120, Math.max(190, width - 540), 120, 80, 140, 80];
        return widths[column];
    }
    Rectangle {
        id: header
        height: 40
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 1
        color: Theme.alternate
        clip: true
        Row {
            x: -table.contentX
            Repeater {
                model: container.headings
                delegate: Item {
                    required property int index
                    required property string modelData
                    width: container.columnWidth(index)
                    height: header.height
                    AppText {
                        anchors.fill: parent
                        anchors.leftMargin: 14
                        anchors.rightMargin: 10
                        verticalAlignment: Text.AlignVCenter
                        text: modelData
                        textStyle: "tableHeader"
                        color: Theme.secondaryText
                    }
                }
            }
        }
    }
    TableView {
        id: table
        objectName: "tagTable"
        anchors.top: header.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 1
        clip: true
        model: container.tableModel
        columnWidthProvider: function(column) { return container.columnWidth(column); }
        rowHeightProvider: function(row) { return Theme.rowHeight; }
        onWidthChanged: forceLayout()
        onRowsChanged: container.selectedRow = -1
        delegate: Rectangle {
            required property int row
            required property int column
            required property string cellText
            required property string rowStatus
            implicitWidth: container.columnWidth(column)
            implicitHeight: Theme.rowHeight
            color: container.selectedRow === row ? Theme.primary
                 : row % 2 ? Theme.alternate : Theme.surface
            AppText {
                objectName: "tableCell"
                anchors.fill: parent
                anchors.leftMargin: 14
                anchors.rightMargin: 10
                text: cellText
                textStyle: "tableCell"
                verticalAlignment: Text.AlignVCenter
                color: column === 0 ? Theme.success : Theme.text
            }
            TapHandler { onTapped: container.selectedRow = row }
        }
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
    }
    EmptyState {
        objectName: "emptyState"
        anchors.centerIn: table
        visible: table.rows === 0
    }
}
