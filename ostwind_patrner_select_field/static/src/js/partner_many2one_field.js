/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { SendSMSButton } from '@sms/components/sms_button/sms_button';
import { Component, onWillStart, useState, status } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { SendMailButton } from '../mail/mail';

const RES_MODEL = "res.partner";
const NUMBER_FIELD_NAME = "phone";

class PartnerSendSMSButton extends SendSMSButton {
    setup() {
        super.setup();
    }

    async onClick() {
        let res_id = null;
        if (this.props.record.data[this.props.name].length) {
            res_id = this.props.record.data[this.props.name][0];
        }
        this.action.doAction(
            {
                type: "ir.actions.act_window",
                target: "new",
                name: this.title,
                res_model: "sms.composer",
                views: [[false, "form"]],
                context: {
                    ...this.user.context,
                    default_res_model: RES_MODEL,
                    default_number_field_name: NUMBER_FIELD_NAME,
                    default_res_id: res_id,
                    default_composition_mode: "comment",
                },
            },
            {
                onClose: () => {
                    if (status(this) === "destroyed") {
                        return;
                    }
                },
            }
        );
    }

    get phoneHref() {
        return "javascript: void();";
    }
}

class PartnerMany2OneField extends Many2OneField {
    setup() {
        super.setup();
        this.partner = useState({
            phone: null,
            email: null,
        });

        this.orm = useService("orm");
        onWillStart(this.fetchPartner.bind(this));
    }

    get isPartnerModel() {
        return this.relation === "res.partner";
    }

    get hasPhone() {
        return !!this.partner.phone;
    }

    get hasEmail() {
        return !!this.partner.email;
    }

    async updateRecord(value) {
        await this.fetchPartner();
        return super.updateRecord(value);
    }

    async fetchPartner() {
        const partnerId = this.props.record.data[this.props.name][0];
        if (this.isPartnerModel && partnerId) {
            const partnerData = await this.orm.read(
                RES_MODEL,
                [partnerId],
                ["email", "phone", "mobile"]
            );
            if (partnerData.length) {
                this.partner.phone = partnerData[0].mobile || partnerData[0].phone;
                this.partner.email = partnerData[0].email;
            }
        }
    }
}
PartnerMany2OneField.components = {
    Many2XAutocomplete,
    PartnerSendSMSButton,
    SendMailButton,
};
PartnerMany2OneField.template = "ostwind_personal_pbx.PartnerMany2OneField";

registry.category("fields").remove("many2one");
many2OneField.component = PartnerMany2OneField;
registry.category("fields").add("many2one", many2OneField);
