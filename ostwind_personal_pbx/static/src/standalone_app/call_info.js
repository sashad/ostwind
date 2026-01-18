/** @odoo-module **/
import { Component, useState, onMounted, useRef } from '@odoo/owl';
import { longPoll } from './long-poll';

export class CallInfo extends Component {
    static template = 'ostwind_personal_pbx.CallInfo';
    static props = {};

    setup() {
        super.setup();
        this.state = useState({
            showCallInfo: false,
            phoneNumber: null,
            userName: null,
            reload: false,
        });
        this.div = useRef('call-info');

        onMounted(() => {
        });
    }

    reloadComponent() {
        this.state.reload = !this.state.reload;
    }

    async acceptCall() {
        this.state.showCallInfo = false;
        // Add logic to accept the call
        console.log('Call accepted', longPoll.rootCmp.appConfig);
        window.parent.postMessage(
            {
                action: 'call',
                phone: this.state.phoneNumber,
                name: this.state.userName,
                res_model: '',
                res_id: 0
            },
            longPoll.rootCmp.appConfig.origin
        );
        // longPoll.sendData('set_call_status', {status: 'process'});
    }

    async rejectCall() {
        this.state.showCallInfo = false;
        longPoll.sendData('set_call_status', {status: 'rejected'});
    }

    get isShow() {
        return this.state.showCallInfo;
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
    get callInfoClass() {
        if (this.isColorDark(window.getComputedStyle(document.body).backgroundColor)) {
            return 'call-info-content black';
        } else {
            return 'call-info-content white';
        }
    }
}
