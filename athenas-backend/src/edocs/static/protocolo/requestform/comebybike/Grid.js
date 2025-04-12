Ext._define('edocs.protocolo.requestform.comebybike.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.comebybike.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.comebybike.Restful',
    'edocs.protocolo.requestform.comebybike.Grid'
);
