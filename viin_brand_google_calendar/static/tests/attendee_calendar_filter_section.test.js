import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { AttendeeCalendarCalendarFilterSection } from "@calendar/views/attendee_calendar/filter_section/attendee_calendar_calendar_filter_section";

describe.current.tags("headless");

beforeEach(() => allowTranslations());

const getDeleteDialogProps = (filter, syncStatus = {}) =>
    AttendeeCalendarCalendarFilterSection.prototype.getDeleteCalendarDialogProps.call(
        { props: { model: { syncStatus } } },
        filter
    );

test("deleting an owned calendar from the synchronised accounts names Viindoo", () => {
    const { body } = getDeleteDialogProps({ accessRole: "owner" });
    expect(body).not.toInclude("Odoo");
    expect(body).toInclude("Viindoo");
});

test("the other delete dialogs are left as core builds them", () => {
    const stopped = getDeleteDialogProps(
        { accessRole: "owner" },
        { google_calendar: "sync_stopped" }
    );
    expect(String(stopped.body)).not.toInclude("Viindoo");
    const subscriber = getDeleteDialogProps({ accessRole: "reader" });
    expect(String(subscriber.body)).not.toInclude("Viindoo");
});
