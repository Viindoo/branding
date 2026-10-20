# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""This module restates a few core POS JS code paths with only the product name removed. Each guard
reads the core 19.0 source and fails when the restated fragment changes, so the copy is revisited."""
import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

ERROR_HANDLERS = "point_of_sale/static/src/app/utils/error_handlers.js"
CASH_MOVE_LIST_POPUP = (
    "point_of_sale/static/src/app/components/popups/cash_move_popup/cash_move_list_popup/"
    "cash_move_list_popup.js"
)
ORDER_PAYMENT_VALIDATION = "point_of_sale/static/src/app/utils/order_payment_validation.js"


def _squash(text):
    """Remove all whitespace: formatting changes of core must not trip the guards."""
    return re.sub(r"\s+", "", text)


@tagged("post_install", "-at_install")
class TestCoreDriftGuards(TransactionCase):

    def _assert_in_core(self, path, *fragments):
        with file_open(path) as f:
            source = _squash(f.read())
        for fragment in fragments:
            with self.subTest(path=path, fragment=fragment[:60]):
                self.assertIn(_squash(fragment), source, "core changed what viin_brand_pos restates")

    def test_rpc_error_handler_is_still_what_pos_rpc_error_handler_restates(self):
        self._assert_in_core(
            ERROR_HANDLERS,
            """export function handleRPCError(error, dialog) {
                const { data } = error;
                if (odooExceptionTitleMap.has(error.exceptionName)) {
                    const title = odooExceptionTitleMap.get(error.exceptionName).toString();
                    dialog.add(AlertDialog, { title, body: data.message });
                } else {
                    if (odoo.debug === "assets") {
                        dialog.add(ErrorDialog, {
                            traceback: data.message + "\\n" + data.debug + "\\n",
                        });
                    } else {
                        dialog.add(AlertDialog, {
                            title: _t("Odoo Server Error"),
                            body: data.message,
                        });
                    }
                }
            }""",
            """function rpcErrorHandler(env, error, originalError) {
                if (originalError instanceof RPCError) {
                    handleRPCError(originalError, env.services.dialog);
                    return true;
                }
            }
            registry.category("error_handlers").add("pos-rpcErrorHandler", rpcErrorHandler);""",
        )

    def test_offline_error_handler_is_still_what_pos_offline_error_handler_restates(self):
        self._assert_in_core(
            ERROR_HANDLERS,
            """export function offlineErrorHandler(env, error, originalError) {
                const candidateError = originalError || error;
                const isOfflineFetchTypeError =
                    candidateError instanceof TypeError &&
                    /NetworkError when attempting to fetch resource/i.test(candidateError.message || "");

                if (isOfflineFetchTypeError) {
                    return true;
                }

                if (originalError instanceof ConnectionLostError) {
                    const network = env.services.pos?.data?.network;
                    if (!network) {
                        return true;
                    }
                    if (!network.warningTriggered) {
                        env.services.dialog.add(AlertDialog, {
                            title: _t("Connection Lost"),""",
            """confirmLabel: _t("Continue with limited functionality"),
                        });
                        network.warningTriggered = true;
                    }

                    return true;
                }
            }
            registry.category("error_handlers").add("pos-offlineErrorHandler", offlineErrorHandler);""",
        )

    def test_cash_move_deletion_is_still_what_on_delete_cm_restates(self):
        self._assert_in_core(
            CASH_MOVE_LIST_POPUP,
            """async onDeleteCm(cm) {
                try {
                    await this.pos.data.call(
                        "pos.session",
                        "delete_cash_in_out",
                        [[this.pos.session.id], cm.id, this.props.partnerId],
                        {},
                        true
                    );
                    this.props.cashMoves = this.props.cashMoves.filter((cashMove) => cashMove.id !== cm.id);
                } catch (error) {
                    this.dialog.add(AlertDialog, {
                        title: _t("Odoo Server Error"),
                        body: error.data.message,
                    });
                    throw error;
                }
            }""",
        )

    def test_validation_error_handling_is_still_what_handle_validation_error_restates(self):
        self._assert_in_core(
            ORDER_PAYMENT_VALIDATION,
            """} else if (error instanceof RPCError) {
                this.order.state = "draft";
                handleRPCError(error, this.pos.dialog);
            } else {
                throw error;
            }
            return error;""",
        )
