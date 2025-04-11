export const environment = {
    production: true,
    environmentName: '',
    url_base: 'http://localhost:8000/',
    brokerNotificationURL:
        'wss://portal.mpmt.mp.br/hermes-api/socket/websocket',
    api_endpoint: 'https://athenas.mpmt.mp.br/athenas/api/v2',
    notificacoesURL: 'https://portal.mpmt.mp.br/hermes/#/notificacao',
    version_app: require('../../package.json').version,
    name_app: 'Suite Athenas',
    local: false,
    remote: undefined,
};
