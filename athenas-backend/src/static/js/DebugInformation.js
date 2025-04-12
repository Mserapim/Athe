
/**
 *
 **/
Ext.define('core.DebugInformation', {
    extend: 'Object',

    statics: {
        start: function() {
            Ext.Ajax.request({
                url: core.callAction('DebugInformation', 'data'),
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    console.debug(rst);
                }
            });
        }
    }
});
