Ext._define('edocs.protocolo.requestform.transitpass.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.transitpass.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.transitpass.Restful',
    'edocs.protocolo.requestform.transitpass.Grid'
);
