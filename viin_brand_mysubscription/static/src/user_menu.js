// Side-effect import: the entry is registered when this module loads, so the removal must run after it.
import "@mysubscription/user_menu";
import { registry } from "@web/core/registry";

registry.category("user_menuitems").remove("mysubscription_user_menu");
