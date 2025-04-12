Ext._define('corregedoria.cirdir.ActionsMixin', {

    submit: function(cfg) {
        if(cfg) {
            Ext.Msg.show({
                title: cfg.alertTitle,
                msg: 'Tem certeza que deseja submeter?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    this._callAjaxRequest('CIRDIRControlInformation', 'submit', cfg);
                }
            });
        }
    },

    _callAjaxRequest: function(controller, method, cfg) {

        Ext.Ajax.request({
            scope: this,
            url: core.callAction(controller, method),
            params: cfg.params,
            callback: function() {
                this.getStore().reload();
                core.invokeCallback((this.callback || {}).success);
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                var type = rst.success == true ? 'INFO' : 'ERROR';
                Ext.Msg.show(this.alertCfg(cfg.alertTitle, rst.message, type));

            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show(this.alertCfg(cfg.alertTitle, rst.message, 'ERROR'));
            },
        });
    },

    alertCfg: function(title, message, type, fn) {
        var icon = {
            'INFO': Ext.Msg.INFO,
            'ERROR': Ext.Msg.ERROR,
        };

        return {
            title: title,
            msg: message,
            icon: icon[type],
            buttons: Ext.Msg.OK,
        };

    },

    columnActionAceptAndEdit: function() {
        return [
            {
                tooltip:'Confirmar informação',
                icon: '/'+ global.Context + '/static/corregedoria/images/decision.png',
                scope: this,
                handler:function(grid, row, col) {
                    grid.getSelectionModel().selectRow(row);
                    var rest = grid.factoryRestful();
                    var record = grid.getStore().getAt(row);

                    var cfg = {
                        alertTitle:  'Confirmar informação',
                        params: {
                            pk: record.get('pk')
                        }
                    }

                    this._callAjaxRequest(rest.resource, 'confirm_information', cfg);
                }
            },
        ]
    },

});
