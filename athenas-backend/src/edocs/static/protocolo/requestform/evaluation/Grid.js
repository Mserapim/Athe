Ext._define('edocs.protocolo.requestform.evaluation.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.evaluation.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.evaluation.Restful',
    'edocs.protocolo.requestform.evaluation.Grid'
);
