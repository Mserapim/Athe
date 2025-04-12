Ext._define('edocs.protocolo.requestform.compensateexpense.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.compensateexpense.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.compensateexpense.Restful',
    'edocs.protocolo.requestform.compensateexpense.Grid'
);
