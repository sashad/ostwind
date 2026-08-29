/** @odoo-module **/
/* global $ */
import { onWillStart, useState } from '@odoo/owl';
import { useService } from '@web/core/utils/hooks';
// import { Chatter } from '@mail/core/web/chatter';
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from '@web/core/utils/patch';
// import { WebClient } from "@web/webclient/webclient";
import { PhoneField } from '@web/views/fields/phone/phone_field';
import { Many2OneField } from '@web/views/fields/many2one/many2one_field';
import { PartnerSendSMSButton } from '@ostwind_partner_select_field/js/partner_many2one_field';

const isAvailable = async function() {
    this.pbx.isAvailable = await this.orm.call(
        'ostwind.personalpbx',
        'is_available'
    );
};

patch(PhoneField.prototype, {
    template: 'ostwind_personal_pbx.FormPhoneField',
    setup() {
        super.setup(...arguments);
        this.pbx = useState({
            isAvailable: false,
            isDisabled: false,
            originalColor: '',
        });
        this.orm = useService('orm');
        this.notification = useService('notification');
        onWillStart(async () => {
            isAvailable.call(this);
        });
    },

    async onPhoneClick(e) {
        if (this.pbx.isAvailable && !this.pbx.isDisabled) {
            e.preventDefault();
            // const $el = $(this.__owl__.bdom.parentEl).find('.o_phone_form_link').find('small, .fa-phone');
            // console.log('onPhoneClick', $el, this);
            this.pbx.isDisabled = true;
            // this.pbx.originalColor = $el.css('color');
            // $el.css('color', getComputedStyle(document.body).backgroundColor);

            setTimeout(() => {
                this.pbx.isDisabled = false;
                // $el.css('color', this.pbx.originalColor);
            }, 2000);

            const { resModel, resId } = this.props.record.config;
            const result = await this.orm.call(
                'ostwind.personalpbx',
                'partner_call',
                [
                    this.props.record.data[this.props.name].replace(/\s+/g, ''),
                    resModel,
                    resId
                ],
            );
            if (result && !result.success) {
                this.notification.add(result.message, {
                    type: 'warning',
                    sticky: false,
                });
            }
            console.log('! On click !', this.props.record.data[this.props.name], result);
        } else if (this.pbx.isAvailable) {
            e.preventDefault();
        }
    }
});

patch(Many2OneField.prototype, {
    setup() {
        super.setup(...arguments);
        // to chack a pbx is active. A mobile app is connected.
        this.pbx = useState({
            isAvailable: false,
        });
        this.notification = useService('notification');
        onWillStart(async () => {
            if (this.isPartnerModel) {
                isAvailable.call(this);
            }
        });
    },

    async onPhoneClick(e) {
        if (this.pbx.isAvailable && !this.pbx.isDisabled) {
            e.preventDefault();
            // const $el = $(this.__owl__.bdom.parentEl).find('.o_phone_form_link').find('small, .fa-phone');
            // console.log('onPhoneClick', $el, this.busService);
            this.pbx.isDisabled = true;
            // this.pbx.originalColor = $el.css('color');
            // $el.css('color', getComputedStyle(document.body).backgroundColor);

            setTimeout(() => {
                this.pbx.isDisabled = false;
                // $el.css('color', this.pbx.originalColor);
            }, 2000);

            const { resModel, resId } = this.props.record.config;
            const result = await this.orm.call(
                'ostwind.personalpbx',
                'partner_call',
                [this.partner.phone, resModel, resId],
                this.partner
            );
            console.log('! On click !', this.partner.phone, result);
            if (result && !result.success) {
                this.notification.add(result.message, {
                    type: 'warning',
                    sticky: false,
                });
            }
        } else if (this.pbx.isAvailable) {
            e.preventDefault();
        }
    }
});

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        this.busService = this.env.services.bus_service;
        this.notification = useService('notification');

        this.lastNotifyId = 0;
        const busListener = ({ detail: notifications}) => {
            for (const { id, payload, type } of notifications) {
                if (
                    type === 'LOG_REFRESH' &&
                    this.lastNotifyId !== id
                ) {
                    this.lastNotifyId = id;
                    this.onPostCallback();
                    setTimeout(() => {
                        this.rootRef.el?.scrollTo({top: 0, behavior: 'smooth'});
                    }, 1000);
                } else if (type === 'PBX_NOTIFY') {
                    this.notification.add(payload.message, {
                        type: 'warning',
                        sticky: false,
                    });
                }
            }
        };
        this.busService.addEventListener('notification', busListener);
        this.busService.addChannel('pbx_res_pertner');
    },
});

patch(PartnerSendSMSButton.prototype, {
    async onClick() {
        await super.onClick();
    }
});
