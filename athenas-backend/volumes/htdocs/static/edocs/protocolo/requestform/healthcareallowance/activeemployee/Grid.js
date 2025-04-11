Ext._define('edocs.protocolo.requestform.healthcareallowance.activeemployee.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.healthcareallowance.activeemployee.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.healthcareallowance.activeemployee.Restful',
    'edocs.protocolo.requestform.healthcareallowance.activeemployee.Grid'
);
