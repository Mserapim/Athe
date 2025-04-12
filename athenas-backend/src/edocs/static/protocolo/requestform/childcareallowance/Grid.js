Ext._define('edocs.protocolo.requestform.childcareallowance.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.childcareallowance.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.childcareallowance.Restful',
    'edocs.protocolo.requestform.childcareallowance.Grid'
);
