Ext._define('planning.hiring.minutesolicitationrequisition.MinuteSolicitationRequisitionRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationRequisition',

    toRequisit: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(this.getRoute(
            'to_requisit',
            false,
            'POST', 
            {
                params: {
                    pk: pk,
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.document);
                    else
                        core.invokeCallback((cbFailure || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function(xhr) {
                    core.invokeCallback((cbFailure || cbFailure), 'Recurso indisponível no momento.');
                },
                callback: function() {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },

    rendererEdoc: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(this.getRoute(
            'renderer_edoc',
            false,
            'POST', 
            {
                params: {
                    pk: pk,
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.document);
                    else
                        core.invokeCallback((cbFailure || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function(xhr) {
                    core.invokeCallback((cbFailure || cbFailure), 'Recurso indisponível no momento.');
                },
                callback: function() {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.minutesolicitationrequisition.MinuteSolicitationRequisitionRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "solicitation",
                },
                {
                    type: "string",
                    name: "solicitation_display"
                },
                {
                    type: "string",
                    name: "solicitation_unicode"
                },
                {
                    type: "int",
                    name: "expense_approver",
                },
                {
                    type: "string",
                    name: "expense_approver_display"
                },
                {
                    type: "int",
                    name: "requester",
                },
                {
                    type: "string",
                    name: "requester_display"
                },
                {
                    type: "string",
                    name: "number",
                    useNull: true
                },
                {
                    type: "string",
                    name: "object_execution"
                },
                {
                    type: "string",
                    name: "signature_date"
                },
            ]);

        return this._fields;
    }
});
