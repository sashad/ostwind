/** @odoo-module */
import { Component, onMounted, useState } from '@odoo/owl';
import { CallInfo } from '@ostwind_personal_pbx/standalone_app/call_info';
import { SmsInfo } from '@ostwind_personal_pbx/standalone_app/sms_info';
import { longPoll } from './long-poll';

const ORIGIN_URLS = ['https://localhost', 'http://localhost:8000', 'http://localhost', 'file://'];

export class Root extends Component {
    static template = 'ostwind_personal_pbx.Root';
    static components = {
        CallInfo,
        SmsInfo
    };
    static props = {};

    setup() {
        super.setup(...arguments);
        this.state = useState({
            login: null,
            authorized: false,
        });
        try {
            this.appConfig = JSON.parse(localStorage.getItem('config'));
        } catch {
            this.appConfig = null;
        }
        console.log('appConfig:', this.appConfig);
        if (!!this.appConfig && !!this.appConfig.theme) {
            document.body.style.color = this.appConfig.theme.color;
            document.body.style.backgroundColor = this.appConfig.theme.backgroundColor;
        }

        onMounted(() => {
            window.addEventListener('message', this.handleMessage);
            // Save refs of child components.
            for (const key in this.__owl__.children) {
                this[this.__owl__.children[key].component.constructor.name] = this.__owl__.children[key].component;
            }
            ORIGIN_URLS.forEach((origin) => {
                window.parent.postMessage(
                    {
                        action: 'config'
                    },
                    origin
                );
            });
        });
    }

    handleMessage = async (event) => {
        console.log('window handle message:', event.data, event.origin);
        if (event.data.type === 'config') {
            document.body.style.color = event.data.theme.color;
            document.body.style.backgroundColor = event.data.theme.backgroundColor;
            localStorage.setItem('config', JSON.stringify(event.data));
            this.appConfig = event.data;
            longPoll.initialize(event.data, this);
            this.state.refresh = Date.now();
        } else if (event.data.type === 'send_data') {
            longPoll.sendData('data', event.data);
        } else if (event.data.type === 'status') {
            console.log('! status !');
            const result = longPoll.sendData(event.data.type, event.data);
            console.log('status:', result);
        } else if (event.data.type === 'response') {
            console.log('! response !', event.data);
            const result = longPoll.sendData(event.data.type, event.data);
            console.log('result:', result);
        }
    };

    async getResIdFromPhone(phone) {
        // Implement this function to get the res_id from the phone number
        // This is a placeholder implementation
        const partners = await this.env.services.rpc({
            model: 'res.partner',
            method: 'search_read',
            args: [[['phone', '=', phone]], ['id']],
        });
        return partners.length > 0 ? partners[0].id : null;
    }
}
