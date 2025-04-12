Ext._define('judicial.reminder.Restful', {
    extend: 'core.Restful',

    resource: 'EJudReminder',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.reminder.Restful.superclass.getFields.call(this, cfg).concat([
                { name: "created_by",type: "int",useNull: true },
                { name: "title",type: "string" },
                { name: "created_by_unicode",type: "string" },
                { name: "modified_by",type: "int",useNull: true },
                { name: "modified_by_unicode",type: "string" },
                { name: "created_at",type: "date",dateFormat: "d/m/Y H:i" },
                { name: "modified_at",type: "date",dateFormat: "d/m/Y H:i" },
                { name: "reminder_state",type: "int",useNull: true },
                { name: "reminder_state_display",type: "string" },
                { name: "reminder_type",type: "string" },
                { name: "content",type: "string" },
                { name: "deactived_by",type: "int",useNull: true },
                { name: "deactived_by_unicode",type: "string" },
                { name: "workplace",type: "int",useNull: true },
                { name: "workplace_unicode",type: "string" },
                { name: "is_active",type: "bool" }
            ]);

        return this._fields;
    },

    rendered: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute('render', pk,'GET', {
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

    deactivate: function(pkset, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute('deactivate', false,'PUT', {
                    params: {
                        pkset: pkset
                    },
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
});
