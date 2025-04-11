Ext._define('edocs.protocolo.requestform.mobileliabilitystatement.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.mobileliabilitystatement.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.mobileliabilitystatement.Restful',
    'edocs.protocolo.requestform.mobileliabilitystatement.Grid'
);
