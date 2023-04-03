/** @odoo-module **/

import * as colors from '@web/views/graph/colors';

var GRAPH_COLORS = ["#00bbce", "#7f4282", "#323232", "#00B365", "#0099E6",
    "#FFCC32", "#CC5252", "#ffa100", "#804080", "#343a40",
    "#66f0ff", "#c796ca", "#989898", "#59ffb6", "#73d0ff",
    "#ffe598", "#e5a8a8", "#ffd07f", "#ca95ca", "929ca6"];

colors.getColor = function (index, colorScheme) {
    const graph_colors = GRAPH_COLORS;
    return graph_colors[index % graph_colors.length];
}
