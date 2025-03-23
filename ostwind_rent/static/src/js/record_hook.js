/** @odoo-module **/
import { patch } from '@web/core/utils/patch';
import { RelationalModel } from '@web/model/relational_model/relational_model';
import { x2ManyCommands } from "@web/core/orm_service";
import { getFieldsSpec } from "@web/model/relational_model/utils";

patch(RelationalModel.prototype, {
    setup(params, options) {
        console.log('setup', params, options);

        super.setup(...arguments);
        this.hooks.onRecordChanged = async function(record, data) {
            const { fields, activeFields, resModel, resId } = record.config;
            const fieldSpec = getFieldsSpec(activeFields, fields, record.evalContext);
            const fieldNames = [];
            // if (cmp.data.name) {
            //     cmp.data.name = cmp.data.name + '!!';
            // }
            console.log('Record changed:', record.config, record);
            console.log('Record changed:', data);
            let response = await record.model.orm.call(
                resModel,
                "onchange",
                [[resId], data, fieldNames, fieldSpec],
                { context: { on_record_changed: 1, ...record.contex } }
            );
            console.log('Response:', response);
        }
    },
});

