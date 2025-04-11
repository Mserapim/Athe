Ext._define('edocs.protocolo.requestform.nonanticipationthirteenth.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.nonanticipationthirteenth.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.nonanticipationthirteenth.Restful',
    'edocs.protocolo.requestform.nonanticipationthirteenth.Grid'
);
