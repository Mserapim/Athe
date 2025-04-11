Ext._define('edocs.protocolo.requestform.termocompromissosigilo.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.termocompromissosigilo.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.termocompromissosigilo.Restful',
    'edocs.protocolo.requestform.termocompromissosigilo.Grid'
);
