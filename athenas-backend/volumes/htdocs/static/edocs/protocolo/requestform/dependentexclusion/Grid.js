Ext._define('edocs.protocolo.requestform.dependentexclusion.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.dependentexclusion.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.dependentexclusion.Restful',
    'edocs.protocolo.requestform.dependentexclusion.Grid'
);
