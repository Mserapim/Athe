Ext._define('edocs.protocolo.requestform.finalpaperdayoff.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.finalpaperdayoff.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.finalpaperdayoff.Restful',
    'edocs.protocolo.requestform.finalpaperdayoff.Grid'
);
