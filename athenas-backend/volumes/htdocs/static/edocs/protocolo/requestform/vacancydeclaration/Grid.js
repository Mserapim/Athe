Ext._define('edocs.protocolo.requestform.vacancydeclaration.Grid', {
    extend: 'edocs.protocolo.ProtocoloGrid',
    restWindow: 'edocs.protocolo.requestform.vacancydeclaration.Window',
});

core.RestfulGrid.register(
    'edocs.protocolo.requestform.vacancydeclaration.Restful',
    'edocs.protocolo.requestform.vacancydeclaration.Grid'
);
