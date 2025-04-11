Ext._define('edocs.protocolo.requestform.debitauthorization.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.debitauthorization.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.debitauthorization.Restful',
    'edocs.protocolo.requestform.debitauthorization.Grid'
);
