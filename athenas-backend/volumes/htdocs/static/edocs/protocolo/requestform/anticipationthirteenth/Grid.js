Ext._define('edocs.protocolo.requestform.anticipationthirteenth.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.anticipationthirteenth.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.anticipationthirteenth.Restful',
    'edocs.protocolo.requestform.anticipationthirteenth.Grid'
);
