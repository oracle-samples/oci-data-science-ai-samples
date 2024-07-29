/**
 * Helper method to assist you migrate the older SDK settings object having icon
 * fields at the root level to 'icons' object field.
 * This method takes care of mapping the icons to their counterpart within the
 * 'icons' setting.
 * You can replace your existing settings with the returned object and use it
 * to initialize the SDK.
 * You may only need to use this method once to update your settings, and don't
 * need to use it again.
 * It is NOT REQUIRED to use this method, the SDK continues to support the
 * icons passed at the root of the settings.
 *
 * @param {object} config
 * @return {object} updated config
 */
function mapRootIconsToNested(config) {
    // Map older icons to new icons object fields
    var icons = {
        avatarAgent: config.agentAvatar,
        avatarBot: config.botIcon,
        avatarUser: config.personIcon,
        fileAudio: config.audioIcon,
        fileImage: config.imageIcon,
        fileGeneric: config.fileIcon,
        fileVideo: config.videoIcon,
        clearHistory: config.clearMessageIcon,
        collapse: config.closeIcon,
        download: config.downloadIcon,
        error: config.errorIcon,
        expandImage: config.expandImageIcon,
        keyboard: config.keyboardIcon,
        logo: config.logoIcon,
        launch: config.botButtonIcon,
        mic: config.micIcon,
        send: config.sendIcon,
        shareMenu: config.attachmentIcon,
        ttsOff: config.audioResponseOffIcon,
        ttsOn: config.audioResponseOnIcon,
        typingIndicator: config.chatBubbleIcon,
    };

    // Merge any existing icons properties in passed config with mapped ones
    if (config.icons) {
        var configIcons = config.icons;
        for (var configKey in configIcons) {
            if (configIcons.hasOwnProperty(configKey)) {
                icons[configKey] = configIcons[configKey];
            }
        }
    }

    // Remove undefined properties from the icons object
    for (var iconKey in icons) {
        if (!icons[iconKey]) {
            delete icons[iconKey];
        }
    }

    // Remove root icon properties from config
    var rootProps = [
        'agentAvatar',
        'botIcon',
        'personIcon',
        'audioIcon',
        'imageIcon',
        'fileIcon',
        'videoIcon',
        'clearMessageIcon',
        'closeIcon',
        'downloadIcon',
        'errorIcon',
        'expandImageIcon',
        'keyboardIcon',
        'logoIcon',
        'botButtonIcon',
        'micIcon',
        'sendIcon',
        'attachmentIcon',
        'audioResponseOffIcon',
        'audioResponseOnIcon',
        'chatBubbleIcon',
    ];
    for (var i = 0; i < rootProps.length; i++) {
        var rootProp = rootProps[i];
        if (config[rootProp]) {
            delete config[rootProp];
        }
    }

    config.icons = icons;
    return config;
}
