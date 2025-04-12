Ext._define('edocs.protocolo.requestform.intimationwhatsappvictim.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.intimationwhatsappvictim.Window'
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.intimationwhatsappvictim.Restful',
    'edocs.protocolo.requestform.intimationwhatsappvictim.Grid'
);
