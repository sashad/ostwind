/** @odoo-module */
import { odooAuth } from './auth';

export var longPoll = {
    odooServer: null,
    longPollUrl: '', // Long Poll URL
    SESSION_ID: '',
    DB: 'test',

    // Status:
    deviceStatus: null,

    // Root component.
    rootCmp: null,

    // Last sms_id from the backend.
    lastSmsId: 0,

    // Initialize Long Poll
    initialize: async function(odooServerData, rootCmp) {
        this.rootCmp = rootCmp;
        this.odooServer = odooServerData;
        console.log('!!!!-- odoo server --!!!!', this.odooServer);
        this.longPollUrl = this.odooServer.odooServerUrl;
        this.DB = this.odooServer.odooDbName;
        if (this.odooServer.odooDbName
            && this.odooServer.odooLoginName
            && this.odooServer.odooLoginPassword
            && this.odooServer.odooDbName
        ) {
            await odooAuth.authenticate(
                this.odooServer.odooServerUrl,
                this.odooServer.odooLoginName,
                this.odooServer.odooLoginPassword,
                (result, data) => {
                    this.rootCmp.state.authorized = result;
                    this.rootCmp.state.login = this.odooServer.odooLoginName;
                    console.log('!!!!----!!!!', result, data);
                    this.SESSION_ID = data.result.session_id;
                    this.startLongPoll();
                },
                this.odooServer.odooDbName
            );
        }
    },

    // Start Long Poll
    startLongPoll: function() {
        if (!this.longPollUrl) {
            console.error('Long Poll URL is not set');
            return;
        }

        // Make a request to the Long Poll URL
        this.makeLongPollRequest();
    },

    // Make a request to the Long Poll URL
    makeLongPollRequest: function() {
        console.log('cookie:', `${document.cookie}`, this.SESSION_ID);
        fetch(`/api/ostwind/personal_pbx/longpoll?db=${this.DB}&last_sms_id=${this.lastSmsId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'PBX-KEY': `${this.SESSION_ID}`,
            },
            body: ''
        })
            .then(async response => {
                // Handle the response data
                if (response.status === 200) {

                    return response.json();
                } else if (response.status === 403) {
                    await odooAuth.authenticate(
                        this.longPollUrl,
                        this.odooServer.odooLoginName,
                        this.odooServer.odooLoginPassword,
                        (result, data) => {
                            console.log('!!!!-- reauth --!!!!', result, data);
                            this.SESSION_ID = data.result.session_id;
                            this.startLongPoll();
                        },
                        this.odooServer.odooDbName
                    );
                } else {
                    setTimeout(() => {
                        this.makeLongPollRequest();
                    }, 3000);
                }
            })
            .then(async (data) => {
                if (!data) {
                    return;
                }
                await this.handleLongPollResponse(data);
                // Make the next request.
                setTimeout(() => {
                    this.makeLongPollRequest();
                }, 300);
            })
            .catch(error => {
                console.error('Long Poll request failed:', error);

                // Retry the request after a delay
                setTimeout(() => {
                    this.makeLongPollRequest();
                }, 3000); // Adjust the delay as needed
            });
    },

    // Handle the response data from the Long Poll URL
    handleLongPollResponse: async function(data) {
        // Process the response data as needed
        console.log('Long Poll response:', data, this);
        if (this.rootCmp && data.status === 'call') {
            const callInfo = this.rootCmp.CallInfo;
            const phoneNumber = Object.keys(data.data)[0];
            const userName = data.data[phoneNumber].name || '';
            callInfo.state.phoneNumber = phoneNumber;
            callInfo.state.userName = userName;
            if (this.odooServer.acceptOutgoingCalls === 'true') {
                callInfo.state.showCallInfo = true;
            } else {
                await callInfo.acceptCall();
            }
        } else if (this.rootCmp && data.status === 'sms') {
            if (this.lastSmsId === data.data.smsId) {
                // Wait for SMS accapting.
                return;
            }
            this.lastSmsId = data.data.smsId;

            const smsInfo = this.rootCmp.SmsInfo;
            smsInfo.state.phoneNumber = data.data.phone;
            smsInfo.state.message = data.data.message;
            smsInfo.state.smsId = data.data.smsId;
            if (this.odooServer.acceptSendingSms === 'true') {
                smsInfo.state.showSmsInfo = true;
            } else {
                await smsInfo.acceptSms();
            }
        }
    },

    // Send data to the Long Poll server
    sendData: function(action, data) {
        fetch(`/api/ostwind/personal_pbx/send_data?db=${this.DB}&action=${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'PBX-KEY': `${this.SESSION_ID}`,
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Data sent successfully:', data);
            })
            .catch(error => {
                console.error('Failed to send data:', error);
            });

        return true;
    }
};
