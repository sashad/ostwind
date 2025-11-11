/** @odoo-module **/

import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { SendSMSButton } from '@sms/components/sms_button/sms_button';
import { onWillStart, useState, status } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { SendMailButton } from '../mail/mail';
import { patch } from "@web/core/utils/patch";

const RES_MODEL = "res.partner";
const NUMBER_FIELD_NAME = "phone";

class PartnerSendSMSButton extends SendSMSButton {
    setup() {
        super.setup(...arguments);
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

patch(Many2OneField.prototype, {
    template: "ostwind_partner_select_field.PartnerMany2OneField",
    components: {
        ...Many2OneField.components,
        PartnerSendSMSButton: PartnerSendSMSButton,
        SendMailButton: SendMailButton,
    },
    setup() {
        super.setup(...arguments);

        this.partner = useState({
            phone: null,
            email: null,
        });

        this.orm = useService("orm");
        onWillStart(this.fetchPartner.bind(this));
    },

    get isPartnerModel() {
        return this.relation === "res.partner";
    },

    get hasPhone() {
        return !!this.partner.phone;
    },

    get hasEmail() {
        return !!this.partner.email;
    },

    async updateRecord(value) {
        await this.fetchPartner();
        return super.updateRecord(value);
    },

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
});
