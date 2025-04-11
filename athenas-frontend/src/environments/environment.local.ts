export const environment = {
  production: false,
  environmentName: 'local',
  url_base: 'http://localhost:4200/',
  brokerNotificationURL: 'ws://localhost:8080/socket/websocket',
  api_endpoint: 'http://localhost:8080/athenas/api/v2',
  notificacoesURL: '',
  version_app: require('../../package.json').version,
  name_app: 'Suite Athenas (Local)',
  local: true,
  remote: undefined
};
