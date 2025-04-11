Ext._define('edocs.protocolo.requestform.functionalidentity.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.functionalidentity.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.functionalidentity.Restful',
    'edocs.protocolo.requestform.functionalidentity.Grid'
);
