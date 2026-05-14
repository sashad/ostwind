/** @odoo-module **/
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onWillUnmount } from "@odoo/owl";

patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        // const busService = useService("bus_service");
        this.busService = this.env.services.bus_service;
        this.isMounted = false;
        this.isSubcribed = false;
        onMounted(() => {
            if (!this.isSubcribed) {
                this.busService.addChannel("iot_mqtt_values_refresh");
                this.busService.subscribe("refresh_item", (payload) => {
                // if (!this.model.root) {
                //     // The object doesn't exist.
                //     return;
                // }
                // Find the specific record in the current list
                const record = this.model.root.records.find(
                    (r) => r.resId === payload.res_id
                );
                console.log("-----", payload, this.model.root.records, record);
                    if (this.isMounted && record) {
                        // Refresh ONLY this card
                        record.load();
                    }
                });
            }
            this.isMounted = true;
            this.isSubcribed = true;
        });

        onWillUnmount(() => {
            this.isMounted = false;
            console.log("-- unmount --")
            // this.busService.unsubscribe("refresh_item");
        });
    }
});
