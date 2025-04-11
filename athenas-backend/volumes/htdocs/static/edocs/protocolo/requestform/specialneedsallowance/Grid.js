Ext._define('edocs.protocolo.requestform.specialneedsallowance.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.specialneedsallowance.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.specialneedsallowance.Restful',
    'edocs.protocolo.requestform.specialneedsallowance.Grid'
);
