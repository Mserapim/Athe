Ext._define('edocs.protocolo.requestform.electoralenlistment.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.electoralenlistment.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.electoralenlistment.Restful',
    'edocs.protocolo.requestform.electoralenlistment.Grid'
);
