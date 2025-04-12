Ext._define('raf.conversation.Restful', {
    extend: 'core.Restful',

    resource: 'RAFConversation',

    conversation: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'create_conversation_content',
                false,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );
    },


    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.conversation.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "bool",
                    name: "finalized"
                },
                {
                    type: "integer",
                    name: "last_content"
                },
                {
                    type: "integer",
                    name: "last_content"
                }

            ]);

        return this._fields;
    }
});
