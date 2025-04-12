Ext._define('edocs.protocolo.requestform.idbadge.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.idbadge.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.idbadge.Restful',
    'edocs.protocolo.requestform.idbadge.Grid'
);
