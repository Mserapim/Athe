Ext._define('edocs.protocolo.requestform.funeralallowance.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.funeralallowance.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.funeralallowance.Restful',
    'edocs.protocolo.requestform.funeralallowance.Grid'
);
