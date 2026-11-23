import { AttendeeCalendarCalendarFilterSection } from "@calendar/views/attendee_calendar/filter_section/attendee_calendar_calendar_filter_section";
import { patch } from "@web/core/utils/patch";

patch(AttendeeCalendarCalendarFilterSection.prototype, {
    getDeleteCalendarDialogProps(filter) {
        const props = super.getDeleteCalendarDialogProps(filter);
        const body = String(props.body);
        return body.includes("Odoo")
            ? { ...props, body: body.replaceAll("Odoo", "Viindoo") }
            : props;
    },
});
