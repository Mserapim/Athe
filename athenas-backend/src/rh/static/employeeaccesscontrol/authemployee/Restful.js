Ext._define('rh.employeeaccesscontrol.authemployee.Restful', {
    extend: 'rh.employee.Restful',
  
    resource: 'AUTHEmployeeRestful',
  
    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.employeeaccesscontrol.authemployee.Restful.superclass.getFields.call(this, cfg).concat([
                { name: 'social_name', type: 'string' },
                { name: 'is_staff', type: 'string' },
                { name: 'is_active', type: 'string' },
                { name: 'is_superuser', type: 'string' },
                { name: 'username', type: 'string' },
                { name: 'user_pk', type: 'int' },
                { name: 'email_pessoal_verificado', type: 'bool' },
                { name: 'verificado_mastiff', type: 'bool' },
            ]);

        return this._fields
  
    },
  
    _process: function (params, cbSuccess, cbFailure, cbCallback) {
        var callbackMessage = {
            fn: function (message) {
                Ext.Msg.show({
                    title: 'Processando',
                    icon: Ext.Msg.WARNING,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        };
  
        this.doRequest(this.getRoute(
            params.customAction,
            null,
            'POST',
            {
                params: params,
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        core.invokeCallback((callbackMessage || { fn: Ext.emptyFn }), rst.message);
                    } else
                        core.invokeCallback((callbackMessage || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    core.invokeCallback((cbFailure || callbackMessage), 'Recurso indisponivel no momento.');
                },
                callback: function () {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },
  
});