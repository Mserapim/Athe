Ext._define('edocs.protocolo.requestform.weddingdayoff.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.weddingdayoff.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.weddingdayoff.Restful',
    'edocs.protocolo.requestform.weddingdayoff.Grid'
);
