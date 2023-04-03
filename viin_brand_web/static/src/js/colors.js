/** @odoo-module **/

import { COLORS } from "@web/views/graph/colors";

var GRAPH_COLORS = ["#00bbce", "#7f4282", "#dd3baf", "#00B365", "#0099E6",
    "#FFCC32", "#CC5252", "#ffa100", "#804080", "#343a40",
    "#66f0ff", "#c796ca", "#ee9dd6", "#59ffb6", "#73d0ff",
    "#ffe598", "#e5a8a8", "#ffd07f", "#ca95ca", "929ca6"];

for (let i=0;i<=GRAPH_COLORS.length;i++){
    COLORS[i] = GRAPH_COLORS[i]
}
