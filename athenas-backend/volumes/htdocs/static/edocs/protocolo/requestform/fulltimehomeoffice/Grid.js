Ext._define('edocs.protocolo.requestform.fulltimehomeoffice.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.fulltimehomeoffice.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.fulltimehomeoffice.Restful',
    'edocs.protocolo.requestform.fulltimehomeoffice.Grid'
);
