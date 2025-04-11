// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.


export const environment = {
    production: false,
    environmentName: 'local',
    url_base: 'http://localhost:4200/',
    brokerNotificationURL: 'ws://localhost:8080/socket/websocket',
    api_endpoint: 'http://localhost:8080/athenas/api/v2',
    notificacoesURL: 'http://localhost:8080/hermes/#/notificacao',
    version_app: require('../../package.json').version,
    name_app: 'Suite Athenas (Local)',
    local: true,
    remote: undefined
  };




// export const environment = {
//     production: false,
//     environmentName: 'Desenvolvimento',
//     url_base: 'https://teste.mpmt.mp.br/',
//     brokerNotificationURL: 'wss://teste.mpmt.mp.br/hermes-api/socket/websocket',
//     api_endpoint: 'https://local.mpmt.mp.br:4200/athenas/api/v2',
//     version_app: '1.0',
//     notificacoesURL: 'https://teste.mpmt.mp.br/hermes/#/notificacao',
//     name_app: 'Suite Athenas',
//     remote: '172.16.20.91',
//     local: true,
// };






// export const environment = {
//     production: false,
//     url_base: 'https://teste.mpmt.mp.br/',
//     api_endpoint: 'https://local.mpmt.mp.br:4200/athenas/api/v2',
//     versao: '1.0',
//     nome_sistema: 'VDF',
//     remote: '172.16.20.91', //Somente para ambiente de desenvolvimento
//     local: true,
// };

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
