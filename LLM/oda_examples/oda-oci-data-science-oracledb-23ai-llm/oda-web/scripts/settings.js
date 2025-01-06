'use strict';

/**
 * Set client auth mode - true to enable client auth, false to disable it.
 *
 * Disabling authentication is preferred for initial integration of the SDK with the web app.
 *
 * When client authentication has been disabled, only connections made from unblocked lists (allowed domains) are
 * allowed at the server. This use case is recommended when the client application cannot generate a signed JWT (because
 * of a static website or no authentication mechanism for the web/mobile app) but requires ODA integration. It can also
 * be used when the chat widget is already secured and visible to only authenticated users in the client platforms (web
 * application with the protected page).
 *
 * For other cases, it is recommended that client auth enabled mode is used when using the SDK for production as it adds
 * another layer of security when connecting to a DA/skill.
 *
 * When client authentication has been enabled, client authentication is enforced by signed JWT tokens in addition to
 * the unblocked lists. When the SDK needs to establish a connection with the ODA server, it first requests a JWT token
 * from the client and then sends it along with the connection request. The ODA server validates the token signature and
 * obtains the claim set from the JWT payload to verify the token to establish the connection.
 *
 * The Web channel in ODA must also be enabled to accept client auth enabled connections.
 */
let isClientAuthEnabled = false;

/**
 * Initializes the SDK and sets a global field with passed name for it the can
 * be referred later
 *
 * @param {string} name Name by which the chat widget should be referred
 */
function initSdk(name) {
    // Retry initialization later if the web page hasn't finished loading or the WebSDK is not available yet
    if (!document || !document.body || !WebSDK) {
        setTimeout(function () {
            initSdk(name);
        }, 2000);
        return;
    }

    if (!name) {
        name = 'Bots';          // Set default reference name to 'Bots'
    }

    let Bots;

    /**
     * SDK configuration settings
     *
     * Other than URI, all fields are optional with two exceptions for auth modes:
     *
     * In client auth disabled mode, 'channelId' must be passed, 'userId' is optional
     * In client auth enabled mode, 'clientAuthEnabled: true' must be passed
     */
    const chatWidgetSettings = {
        URI: 'oda-6bd20d2d75414fc6893891714bc07f55-da2.data.digitalassistant.oci.oraclecloud.com',                               // ODA URI, only the hostname part should be passed, without the https://
        clientAuthEnabled: isClientAuthEnabled,     // Enables client auth enabled mode of connection if set true, no need to pass if set false
        channelId: '05957180-ceed-4dd7-9e6e-8c9b4c9514ae',  // Channel ID, available in channel settings in ODA UI, optional if client auth enabled
        // openChatOnLoad: true,
        userId: '<userId>',                         // User ID, optional field to personalize user experience
        // initUserHiddenMessage: 'Hi',
        openLinksInNewWindow: false,
        disablePastActions: 'none',
        enableAttachment: false,
        enableAutocomplete: true,                   // Enables autocomplete suggestions on user input
        enableBotAudioResponse: true,               // Enables audio utterance of skill responses
        enableClearMessage: true,                   // Enables display of button to clear conversation
        enableSpeech: true,                         // Enables voice recognition
        enableTimestamp: false,                     // Show timestamp with each message
        speechLocale: WebSDK.SPEECH_LOCALE.EN_US,
        showConnectionStatus: true,                 // Displays current connection status on the header
        speechLocale: WebSDK.SPEECH_LOCALE.EN_US,
        i18n: {                                     // Provide translations for the strings used in the widget
            en: {                                   // en locale, can be configured for any locale
                chatTitle: 'DataScience Oracle23AI ODA Bot'       // Set title at chat header
            }
        },
        timestampMode: 'relative',                  // Sets the timestamp mode, relative to current time or default (absolute)
        theme: WebSDK.THEME.REDWOOD_DARK,           // Redwood dark theme. The default is THEME.DEFAULT, while older theme is available as THEME.CLASSIC
        icons: {
            avatarBot: "./images/botIcon.png",
            avatarUser: './images/personIcon.png',
            launch:"./images/botButtonIcon.gif",
            logo:"./images/logoIcon.png",
        },
        height: '85vh', //layout modification property
        width: '45vw',  //layout modification property
    };

    // Initialize SDK
    if (isClientAuthEnabled) {
        Bots = new WebSDK(chatWidgetSettings, generateToken);
    } else {
        Bots = new WebSDK(chatWidgetSettings);
    }

    // Connect to skill when the widget is expanded for the first time
    let isFirstConnection = true;

    Bots.on(WebSDK.EVENT.WIDGET_OPENED, function () {
        if (isFirstConnection) {
            Bots.connect();

            isFirstConnection = false;
        }
    });

    function actionHandler(action) {
        Bots.sendMessage(action);
    }

    // Create global object to refer Bots
    window[name] = Bots;
}

/**
 * Function to generate JWT tokens. It returns a Promise to provide tokens.
 * The function is passed to SDK which uses it to fetch token whenever it needs
 * to establish connections to chat server
 *
 * @returns {Promise} Promise to provide a signed JWT token
 */
function generateToken() {
    return new Promise(function (resolve) {
        mockApiCall('https://mockurl').then(function (token) {
            resolve(token);
        });
    });
}

/**
 * A function mocking an endpoint call to backend to provide authentication token
 * The recommended behaviour is fetching the token from backend server
 *
 * @returns {Promise} Promise to provide a signed JWT token
 */
function mockApiCall() {
    return new Promise(function (resolve) {
        setTimeout(function () {
            const now = Math.floor(Date.now() / 1000);
            const payload = {
                iat: now,
                exp: now + 3600,
                channelId: '<channelID>',
                userId: '<userID>'
            };
            const SECRET = '<channel-secret>';

            // An unimplemented function generating signed JWT token with given header, payload, and signature
            const token = generateJWTToken({ alg: 'HS256', typ: 'JWT' }, payload, SECRET);
            resolve(token);
        }, Math.floor(Math.random() * 1000) + 1000);
    });
}

/**
 * Unimplemented function to generate signed JWT token. Should be replaced with
 * actual method to generate the token on the server.
 *
 * @param {object} header
 * @param {object} payload
 * @param {string} signature
 */
function generateJWTToken(header, payload, signature) {
    throw new Error('Method not implemented.');
}

function connectSkill() {
    const URI = document.getElementById('uri').value;
    const channelId = document.getElementById('channelId').value;
    if (URI && channelId) {
        Bots.connect({
            URI,
            channelId
        });
        Bots.openChat();
    }
}
