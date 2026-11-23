import json

from odoo import http

from odoo.addons.website_event_track.controllers.webmanifest import TrackManifest


class BrandTrackManifest(TrackManifest):

    @http.route()
    def webmanifest(self):
        """Re-brand the colour of the events app manifest; core builds the body inline, so it is re-serialised."""
        response = super().webmanifest()
        manifest = json.loads(response.get_data(as_text=True))
        manifest['theme_color'] = self.env.website.get_events_app_theme_color()
        response.set_data(json.dumps(manifest))
        return response
