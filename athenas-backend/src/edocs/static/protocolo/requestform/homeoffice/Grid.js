Ext._define('edocs.protocolo.requestform.homeoffice.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.homeoffice.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.homeoffice.Restful',
    'edocs.protocolo.requestform.homeoffice.Grid'
);
