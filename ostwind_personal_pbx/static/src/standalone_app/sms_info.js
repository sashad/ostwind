/** @odoo-module **/
import { Component, useState, onMounted, useRef } from '@odoo/owl';
import { longPoll } from './long-poll';

export class SmsInfo extends Component {
    static template = 'ostwind_personal_pbx.SmsInfo';
    static props = {};

    setup() {
        super.setup();
        this.state = useState({
            showSmsInfo: false,
            phoneNumber: null,
            message: null,
            reload: false,
            smsId: null,
        });
        this.div = useRef('sms-info');

        onMounted(() => {
        });
    }

    reloadComponent() {
        this.state.reload = !this.state.reload;
    }

    async acceptSms() {
        this.state.showSmsInfo = false;
        // Add logic to accept the SMS
        console.log('Sms accepted', longPoll.rootCmp.appConfig);
        window.parent.postMessage(
            {
                action: 'sms',
                phone: this.state.phoneNumber,
                message: this.state.message,
                smsId: this.state.smsId,
            },
            longPoll.rootCmp.appConfig.origin
        );
        // longPoll.sendData('set_call_status', {status: 'process'});
    }

    async rejectSms() {
        this.state.showSmsInfo = false;
        longPoll.sendData('set_sms_state', {
            smsId: this.state.smsId,
            state: 'canceled',
            notification_status: 'exception',
            failure_type: 'sms_rejected',
        });
    }

    get isShow() {
        return this.state.showSmsInfo;
    }

    isColorDark(color) {
        // Convert the color to RGB format
        const rgb = color.match(/\d+/g);
        if (!rgb) {
            return false;
        }
        // Calculate the brightness of the color
        const brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
        // Compare the brightness with a threshold value
        return brightness < 128;
    }                                                                                                                                                 
    get smsInfoClass() {
        if (this.isColorDark(window.getComputedStyle(document.body).backgroundColor)) {
            return 'call-info-content black';
        } else {
            return 'call-info-content white';
        }
    }
}
