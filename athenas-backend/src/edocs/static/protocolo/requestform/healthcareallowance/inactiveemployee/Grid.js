Ext._define('edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Restful',
    'edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Grid'
);
