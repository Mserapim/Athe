Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationPaymentRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationPayment',

    paymentSolicitation: function(solicitations, successCallback, failureCallback, commonCallback) {
        var values = {};
        values.solicitations = solicitations;
        this.doRequest(
            this.getRoute(
                'payment_solicitation',
                false,
                'POST',
                {
                    params: values,
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            core.invokeCallback(
                                successCallback || { fn: Ext.emptyFn },
                                rst
                            );
                        } else {
                            core.invokeCallback(
                                failureCallback || { fn: Ext.emptyFn },
                                rst.message
                            );
                        }
                    },
                    failure: function(xhr) {
                        core.invokeCallback(
                            failureCallback || { fn: Ext.emptyFn },
                            'Recurso indisponivel nomento.'
                        );
                    },
                    callback: function(xhr) {
                        core.invokeCallback(commonCallback || { fn: Ext.emptyFn });
                    }
                }
            )
        );
    },

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitation.MinuteSolicitationPaymentRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "date",
                    name: "start_reference_period",
                    dateFormat: "d/m/Y"
                },
                {
                    type: "int",
                    name: "status",
                    useNull: true
                },
                {
                    type: "string",
                    name: "status_display"
                },
                {
                    type: "date",
                    name: "end_reference_period",
                    dateFormat: "d/m/Y"
                },
                {
                    type: "string",
                    name: "observation"
                },
                {
                    type: "date",
                    name: "payment_date",
                    dateFormat: "d/m/Y"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "date",
                    name: "modified_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "string",
                    name: "bank_order"
                },
                {
                    type: "float",
                    name: "value",
                    useNull: true
                },
                {
                    type: "int",
                    name: "commitmentnote",
                    useNull: true
                },
                {
                    type: "string",
                    name: "commitmentnote_unicode"
                },
                {
                    type: "int",
                    name: "created_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "created_by_unicode"
                },
                {
                    type: "string",
                    name: "invoice"
                },
                {
                    type: "int",
                    name: "modified_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "modified_by_unicode"
                },
                {
                    type: "int",
                    name: "user",
                    useNull: true
                },
                {
                    type: "string",
                    name: "user_unicode"
                },
                {
                    type: "string",
                    name: "user_display"
                },
                {
                    type: "string",
                    name: "period_display"
                }
            ]);

        return this._fields;
    }
});
