/** @odoo-module */
export var odooAuth = {
    status: 'Not Authorized',

    authenticate: async function(url, login, password, callback, dbName=undefined) {
        // Define the request body
        const requestBody = {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                db: dbName,
                login: login,
                password: password
            },
            id: null,
        };

        // Make the ajax request
        fetch(url + '/web/session/authenticate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            body: JSON.stringify(requestBody),
            credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.result && data.result.uid) {

                    // Authentication successful
                    console.log('Odoo authentication successful');
                    this.status = 'Authorized';
                    callback(true, data);
                } else {
                    // Authentication failed
                    console.log('Odoo authentication failed', data);
                    this.status = 'Not Authorized';
                    callback(false, data.error);
                }
            })
            .catch(error => {
                // Request failed
                this.status = 'Not Authorized';
                console.error('Odoo authentication request failed:', error);
                callback(false, error);
            });
    }
};
