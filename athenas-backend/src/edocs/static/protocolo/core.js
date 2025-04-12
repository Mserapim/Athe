Ext.ns('edocs.protocolo');

Ext.applyIf(edocs.protocolo, {
    openReletad: function(protocol) {
        Ext._create('edocs.protocolo.ProtocolReferenceDetailWindow', {
            modal: true,
            values: {
                protocol: protocol
            }
        }).show();
    }
});
