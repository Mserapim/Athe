// export const environment = {
//     production: false,
//     url_base: 'https://teste.mpmt.mp.br/',
//     api_endpoint: 'https://athenas-hom.mpmt.mp.br/athenas/api/v2',
//     versao: '@VERSAO',
//     nome_sistema: 'suite-athenas',
//     remote: undefined,
//     local: false,
// };

export const environment = {
    production: false,
    environmentName: 'Homologação',
    url_base: 'https://teste.mpmt.mp.br/',
    brokerNotificationURL: 'wss://teste.mpmt.mp.br/hermes-api/socket/websocket',
    api_endpoint: 'https://athenas-hom.mpmt.mp.br/athenas/api/v2',
    notificacoesURL: 'https://teste.mpmt.mp.br/hermes/#/notificacao',
    version_app: require('../../package.json').version,
    name_app: 'Suite Athenas',
    remote: undefined,
    local: false,
};
