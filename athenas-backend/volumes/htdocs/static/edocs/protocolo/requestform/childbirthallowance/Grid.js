Ext._define('edocs.protocolo.requestform.childbirthallowance.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.childbirthallowance.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.childbirthallowance.Restful',
    'edocs.protocolo.requestform.childbirthallowance.Grid'
);
