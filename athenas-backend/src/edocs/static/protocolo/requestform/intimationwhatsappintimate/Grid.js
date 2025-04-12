Ext._define('edocs.protocolo.requestform.intimationwhatsappintimate.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.intimationwhatsappintimate.Window'
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.intimationwhatsappintimate.Restful',
    'edocs.protocolo.requestform.intimationwhatsappintimate.Grid'
);
