Ext._define('edocs.protocolo.requestform.bereavementleave.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.bereavementleave.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.bereavementleave.Restful',
    'edocs.protocolo.requestform.bereavementleave.Grid'
);
