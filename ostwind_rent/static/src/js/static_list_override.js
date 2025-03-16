/** @odoo-module */

import { StaticList } from "@web/model/relational_model/static_list";
import { patch } from "@web/core/utils/patch";
import { x2ManyCommands } from "@web/core/orm_service";
import { getFieldsSpec } from "@web/model/relational_model/utils";

patch(StaticList.prototype, {
    delete(record) {
        return this.model.mutex.exec(async () => {
            await this._applyCommands([[x2ManyCommands.DELETE, record.resId || record._virtualId]]);
            const { fields, activeFields, resModel, resId } = record.config;
            const fieldSpec = getFieldsSpec(activeFields, fields, record.evalContext);
            const fieldNames = [];
            let response = await this.model.orm.call(
                resModel,
                "onchange",
                [[resId], record.data, fieldNames, fieldSpec],
                { context: { del_object: 1, ...record.contex } }
            );
            console.log('!--- patched onDelete ---!', record, response);
            await this._onUpdate();
        });
    }
});
