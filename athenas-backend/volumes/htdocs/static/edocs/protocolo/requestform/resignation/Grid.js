Ext._define('edocs.protocolo.requestform.resignation.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.resignation.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.resignation.Restful',
    'edocs.protocolo.requestform.resignation.Grid'
);
